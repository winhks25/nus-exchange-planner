"""Generate the frozen pre-removal core and upgrade fixtures.

This is a one-time, local-only tool that runs before the production importer is
retired. It imports the reviewed snapshot into a disposable PostgreSQL cluster,
cross-checks it against an independent preview seed and the read-only API
baseline, adds one fixture-only duplicate mapping, and writes the two fixture
files plus their digests for documentation.
"""

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import psycopg
from psycopg.types.json import Jsonb

from scripts.catalog_preview import build_preview
from scripts.catalog_seed import seed_preview
from scripts.import_catalog import apply_plan, build_import_plan
from scripts.postgres_validation import (
    LEGACY_MIGRATION_CEILING,
    REPO_ROOT,
    DatabaseTarget,
    PostgresCluster,
)
from scripts.snapshot_core_data import _compare_snapshots, read_snapshot

DEFAULT_OUTPUT_DIR = REPO_ROOT / "backend" / "tests" / "fixtures"
CORE_FILENAME = "core_dataset.json"
UPGRADE_FILENAME = "pre_catalog_removal.sql"
BASELINE_PATH = (
    REPO_ROOT / "plan" / "remove-catalog-tables" / "baseline-responses.json"
)


class FixtureGenerationError(RuntimeError):
    """Raised when generation cannot produce trustworthy fixtures."""


def main(argv: list[str] | None = None) -> int:
    """Generate both fixtures and print their digests and counts."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    output_dir = args.output_dir.resolve()
    core_path = output_dir / CORE_FILENAME
    upgrade_path = output_dir / UPGRADE_FILENAME
    if not args.force:
        existing = [path for path in (core_path, upgrade_path) if path.exists()]
        if existing:
            raise SystemExit(
                f"{', '.join(str(path) for path in existing)} exists; pass --force"
            )
    output_dir.mkdir(parents=True, exist_ok=True)

    cluster = PostgresCluster()
    cluster.start()
    try:
        imported = cluster.create_database()
        preview_database = cluster.create_database()
        plan = build_import_plan()

        # Publish the reviewed importer output and an independent preview seed.
        apply_plan(plan, imported.importer_url)
        seed_preview(preview_database, build_preview())

        # Prove both seeds describe the same retained core facts.
        imported_before, _ = read_snapshot(imported.owner_url)
        preview_snapshot, _ = read_snapshot(preview_database.owner_url)
        cross_check = _compare_snapshots(imported_before, preview_snapshot, "natural")
        if not cross_check["equal"]:
            raise FixtureGenerationError(
                "importer core data does not match the independent preview seed"
            )

        # Prove the importer data still matches the captured PostgreSQL API baseline.
        baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
        expected_counts = _expected_api_counts(baseline)
        visible_counts = _api_visible_counts(imported.owner_url)
        if visible_counts != expected_counts:
            raise FixtureGenerationError(
                "API-visible mapping counts do not match the captured baseline"
            )

        # Add one duplicate course pair that cannot affect any public endpoint.
        duplicate = _add_fixture_duplicate(imported)
        snapshot, _ = read_snapshot(imported.owner_url)
        multiplicity = snapshot["mapping_multiplicity"]
        if multiplicity["duplicate_course_pair_rows"] != 1:
            raise FixtureGenerationError("intentional duplicate mapping was not preserved")
        if _api_visible_counts(imported.owner_url) != visible_counts:
            raise FixtureGenerationError(
                "fixture-only duplicate unexpectedly changed API-visible counts"
            )

        # Keep the repaired presentation that underpins the source repair evidence.
        if not any(
            row["nus_module_code"] == "CS3264"
            and row["source_nus_title"] == "Foundations of Machine Learning"
            and row["source_partner_units"] == "0.50"
            for row in snapshot["tables"]["module_mappings"]["rows"]
        ):
            raise FixtureGenerationError("repaired mapping presentation is missing")

        # Attach fixture provenance without changing the snapshot tables.
        snapshot["fixture"] = {
            "kind": "core_dataset",
            "migration_ceiling": LEGACY_MIGRATION_CEILING,
            "source_checksum_sha256": plan.source_checksum,
            "repair_checksum_sha256": plan.repair_checksum,
            "production_mapping_rows": 151,
            "fixture_mapping_rows": multiplicity["rows"],
            "api_visible_pair_counts_match_baseline": True,
            "api_visible_duplicate": False,
            "intentional_duplicate": duplicate,
            "notes": [
                "Generated from a disposable pre-removal database populated by the importer.",
                "The extra duplicate mapping intentionally has no degree membership.",
                "The SQL fixture includes all eight core and five metadata tables.",
            ],
        }
        core_path.write_text(
            json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

        # Dump the same database, including provenance tables and source links.
        pg_dump = shutil.which("pg_dump")
        if pg_dump is None:
            raise FixtureGenerationError(
                "pg_dump is required to generate the upgrade fixture"
            )
        subprocess.run(
            [
                pg_dump,
                "--format=plain",
                "--data-only",
                "--schema=public",
                "--column-inserts",
                "--no-owner",
                "--no-privileges",
                "--file",
                str(upgrade_path),
                imported.owner_url,
            ],
            check=True,
        )
        header = (
            "-- Generated from a disposable local database populated by the reviewed importer.\n"
            "-- Includes one fixture-only duplicate mapping outside every degree membership.\n"
        )
        upgrade_path.write_text(
            header + upgrade_path.read_text(encoding="utf-8"), encoding="utf-8"
        )

        # Print secret-free evidence for the fixture README.
        summary = {
            "cross_check": "pass",
            "duplicate": duplicate,
            "core_counts": {
                table: detail["row_count"] for table, detail in snapshot["tables"].items()
            },
            "mapping_multiplicity": multiplicity,
            "core_fixture": _file_evidence(core_path),
            "upgrade_fixture": _file_evidence(upgrade_path),
        }
        print(json.dumps(summary, indent=2))
    finally:
        cluster.stop()
    return 0


def _expected_api_counts(baseline: dict) -> dict[tuple[str, str], int]:
    """Read nonzero mapping counts from the captured PostgreSQL baseline."""

    counts: dict[tuple[str, str], int] = {}
    for degree, case in baseline["recommendations"].items():
        for item in case["body"]["recommendations"]:
            if item["mapping_count"] > 0:
                counts[(degree, item["university"])] = item["mapping_count"]
    return counts


def _api_visible_counts(database_url: str) -> dict[tuple[str, str], int]:
    """Count mapping rows per degree and university as the public endpoints do."""

    with psycopg.connect(database_url) as connection:
        connection.read_only = True
        rows = connection.execute(
            """
            select d.name, u.name, count(mm.id)
            from public.degrees d
            join public.degree_modules dm on dm.degree_id = d.id
            join public.module_mappings mm on mm.nus_module_code = dm.module_code
            join public.pu_modules pm on pm.id = mm.pu_module_id
            join public.partner_universities u on u.id = pm.partner_university_id
            group by d.name, u.name
            """
        ).fetchall()
    return {(degree, university): int(count) for degree, university, count in rows}


def _add_fixture_duplicate(database: DatabaseTarget) -> dict[str, object]:
    """Duplicate one API-invisible mapping with a new source row and mapping ID."""

    with psycopg.connect(database.owner_url) as connection, connection.transaction():
        original = connection.execute(
            """
            select mm.id, mm.nus_module_code, mm.pu_module_id, mm.source_order,
                   r.snapshot_id, r.mapping_index, r.raw_json,
                   r.source_nus_code, r.source_partner_code,
                   r.source_nus_title, r.source_partner_title,
                   r.source_nus_units, r.source_partner_units,
                   r.source_faculty, r.source_page,
                   mm.source_nus_title, mm.source_nus_units,
                   mm.source_partner_title, mm.source_partner_units,
                   mm.source_faculty, mm.source_page
            from public.module_mappings mm
            join public.catalog_source_rows r on r.id = mm.source_row_id
            where not exists (
              select 1 from public.degree_modules dm
              where dm.module_code = mm.nus_module_code
            )
            order by mm.id
            limit 1
            """
        ).fetchone()
        if original is None:
            raise FixtureGenerationError(
                "no API-invisible mapping is available for the duplicate fixture"
            )

        # Insert a new source position with the same source facts.
        (
            original_id,
            nus_code,
            pu_module_id,
            source_order,
            snapshot_id,
            _mapping_index,
            raw_json,
            source_nus_code,
            source_partner_code,
            source_nus_title,
            source_partner_title,
            source_nus_units,
            source_partner_units,
            source_faculty,
            source_page,
            mapping_nus_title,
            mapping_nus_units,
            mapping_partner_title,
            mapping_partner_units,
            mapping_faculty,
            mapping_page,
        ) = original
        next_index = connection.execute(
            """
            select coalesce(max(mapping_index), -1) + 1
            from public.catalog_source_rows
            where snapshot_id = %s
            """,
            (snapshot_id,),
        ).fetchone()[0]
        new_source_id = connection.execute(
            """
            insert into public.catalog_source_rows (
              snapshot_id, mapping_index, raw_json, source_nus_code,
              source_partner_code, source_nus_title, source_partner_title,
              source_nus_units, source_partner_units, source_faculty,
              source_page, outcome
            ) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'accepted')
            returning id
            """,
            (
                snapshot_id,
                next_index,
                Jsonb(raw_json),
                source_nus_code,
                source_partner_code,
                source_nus_title,
                source_partner_title,
                source_nus_units,
                source_partner_units,
                source_faculty,
                source_page,
            ),
        ).fetchone()[0]

        # Insert the exact duplicate course pair against the new source row.
        new_mapping_id = connection.execute(
            """
            insert into public.module_mappings (
              nus_module_code, pu_module_id, source_row_id, source_order,
              source_nus_title, source_nus_units, source_partner_title,
              source_partner_units, source_faculty, source_page
            ) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            returning id
            """,
            (
                nus_code,
                pu_module_id,
                new_source_id,
                source_order,
                mapping_nus_title,
                mapping_nus_units,
                mapping_partner_title,
                mapping_partner_units,
                mapping_faculty,
                mapping_page,
            ),
        ).fetchone()[0]

        # Keep the batch counters aligned with the two fixture-only rows.
        connection.execute(
            """
            update public.catalog_import_batches
            set raw_row_count = raw_row_count + 1,
                accepted_row_count = accepted_row_count + 1
            """
        )

    return {
        "original_mapping_id": int(original_id),
        "new_mapping_id": int(new_mapping_id),
        "new_source_row_id": int(new_source_id),
        "nus_module_code": str(nus_code),
        "mapping_index": int(next_index),
    }


def _file_evidence(path: Path) -> dict[str, object]:
    """Return a file's size and SHA-256 digest without reading it twice."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return {"path": str(path), "bytes": path.stat().st_size, "sha256": digest.hexdigest()}


if __name__ == "__main__":
    sys.exit(main())
