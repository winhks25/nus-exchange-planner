"""End-to-end regression coverage for the transactional catalog importer."""

import copy
import hashlib
import json
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from pathlib import Path
from typing import Any

import psycopg
import pytest

from scripts.import_catalog import (
    ImportPlan,
    ImportRefused,
    SimulatedImportFailure,
    _catalog_counts,
    apply_plan,
)
from scripts.postgres_validation import REPO_ROOT, DatabaseTarget

pytestmark = pytest.mark.regression


def _connect(url: str) -> psycopg.Connection:
    """Open a plain owner connection for assertions."""

    return psycopg.connect(url)


def _json(value: Any) -> Any:
    """Normalize JSONB values to their serialized JSON representation."""

    return json.loads(json.dumps(value, ensure_ascii=False, default=str))


def _catalog_counts_from(database: DatabaseTarget) -> dict[str, int]:
    """Read persisted table counts without relying on the importer's report."""

    with _connect(database.owner_url) as connection:
        connection.read_only = True
        with connection.transaction():
            return _catalog_counts(connection)


def test_import_accounts_for_every_raw_source_byte_and_row(
    legacy_published_catalog: DatabaseTarget, import_plan: ImportPlan
) -> None:
    expected_files = {
        item["path"]: item for item in import_plan.preview["source_snapshot"]["files"]
    }

    # Every archive keeps exact source text, checksum and parsed content.
    with _connect(legacy_published_catalog.owner_url) as connection:
        connection.read_only = True
        with connection.transaction():
            snapshots = connection.execute(
                """
                select file_path, source_kind, raw_text, parsed_json, sha256, byte_size
                from public.catalog_source_snapshots
                order by file_path
                """
            ).fetchall()
            source_rows = connection.execute(
                """
                select
                  s.file_path,
                  r.mapping_index,
                  r.source_nus_code,
                  r.source_partner_code,
                  r.outcome,
                  r.raw_json
                from public.catalog_source_rows r
                join public.catalog_source_snapshots s on s.id = r.snapshot_id
                order by s.file_path, r.mapping_index
                """
            ).fetchall()
            batch = connection.execute(
                """
                select source_checksum, repair_checksum, status, is_current,
                       source_file_count, raw_row_count, accepted_row_count,
                       repaired_row_count, quarantined_row_count
                from public.catalog_import_batches
                """
            ).fetchall()

    assert sorted(item[0] for item in snapshots) == sorted(expected_files)
    for path, kind, raw_text, parsed_json, sha256, byte_size in snapshots:
        expected = expected_files[path]
        assert kind == expected["kind"]
        assert sha256 == expected["sha256"]
        assert byte_size == expected["byte_size"]
        assert raw_text == (REPO_ROOT / path).read_text(encoding="utf-8")
        assert hashlib.sha256(raw_text.encode("utf-8")).hexdigest() == sha256
        assert _json(parsed_json) == json.loads(raw_text)

    # Every source row keeps its file, array index, raw JSON and outcome.
    expected_rows = {
        (row.source_file, row.mapping_index): row for row in import_plan.source_rows
    }
    actual_rows = {
        (path, index): (nus_code, partner_code, outcome, raw_json)
        for path, index, nus_code, partner_code, outcome, raw_json in source_rows
    }
    assert set(actual_rows) == set(expected_rows)
    for key, expected in expected_rows.items():
        assert actual_rows[key] == (
            expected.source_nus_code,
            expected.source_partner_code,
            expected.outcome,
            _json(expected.raw_row),
        )

    # The completed batch marker records the same checksums and accounting.
    assert batch == [
        (
            import_plan.source_checksum,
            import_plan.repair_checksum,
            "completed",
            True,
            len(import_plan.archives),
            import_plan.summary["raw_rows"],
            import_plan.summary["accepted_rows"],
            import_plan.summary["repaired_rows"],
            import_plan.summary["quarantined_rows"],
        )
    ]


def test_persisted_repairs_issues_and_unknown_values_match_reviewed_sources(
    legacy_published_catalog: DatabaseTarget, import_plan: ImportPlan
) -> None:
    with _connect(legacy_published_catalog.owner_url) as connection:
        connection.read_only = True
        with connection.transaction():
            repairs = connection.execute(
                """
                select
                  s.file_path, rows.mapping_index, r.json_pointer,
                  r.before_value, r.after_value, r.source_url, r.status
                from public.catalog_repairs r
                join public.catalog_source_snapshots s on s.id = r.snapshot_id
                join public.catalog_source_rows rows on rows.id = r.source_row_id
                order by s.file_path, rows.mapping_index, r.json_pointer, r.source_url
                """
            ).fetchall()
            issues = connection.execute(
                """
                select
                  s.file_path, rows.mapping_index, i.json_pointer,
                  i.issue_code, i.severity, i.message, i.status
                from public.catalog_issues i
                join public.catalog_source_snapshots s on s.id = i.snapshot_id
                left join public.catalog_source_rows rows on rows.id = i.source_row_id
                order by s.file_path, i.json_pointer, i.issue_code
                """
            ).fetchall()
            nus_modules = connection.execute(
                """
                select code, name, offering_faculty, verified_units
                from public.nus_modules
                """
            ).fetchall()
            partner_modules = connection.execute(
                """
                select code, name, verified_units
                from public.pu_modules
                """
            ).fetchall()
            repaired_mapping = connection.execute(
                """
                select mm.nus_module_code, mm.source_nus_title,
                       mm.source_nus_units, mm.source_partner_units
                from public.module_mappings mm
                join public.catalog_source_rows rows on rows.id = mm.source_row_id
                where rows.mapping_index = 50
                  and rows.snapshot_id = (
                    select id from public.catalog_source_snapshots
                    where file_path = 'data/mapping/canada/toronto.json'
                  )
                """
            ).fetchone()

    # Verified and unresolved repairs remain source-addressed with evidence.
    expected_repairs = {
        (
            item.source_file,
            item.mapping_index,
            item.json_pointer,
            _json(item.before_value),
            _json(item.after_value),
            item.source_url,
            item.status,
        )
        for item in import_plan.repairs
    }
    actual_repairs = {
        (path, index, pointer, _json(before), _json(after), url, status)
        for path, index, pointer, before, after, url, status in repairs
    }
    assert actual_repairs == expected_repairs
    assert Counter(row[6] for row in repairs) == Counter(
        item.status for item in import_plan.repairs
    )

    # Issue rows carry the reviewed status and message, including retained notes.
    expected_issues = {
        (
            item.source_file,
            item.mapping_index,
            item.json_pointer,
            item.code,
            item.severity,
            item.message,
            item.status,
        )
        for item in import_plan.issues
    }
    actual_issues = {
        (path, index, pointer, code, severity, message, status)
        for path, index, pointer, code, severity, message, status in issues
    }
    assert actual_issues == expected_issues
    assert Counter(row[6] for row in issues) == Counter(
        item.status for item in import_plan.issues
    )

    # Unknown names and units stay null instead of being invented.
    assert {
        (code, name, faculty, float(units) if units is not None else None)
        for code, name, faculty, units in nus_modules
    } == {
        (item.code, item.name, item.offering_faculty, item.verified_units)
        for item in import_plan.entities.nus_modules
    }
    assert {
        (code, name, float(units) if units is not None else None)
        for code, name, units in partner_modules
    } == {
        (item.code, item.name, item.verified_units)
        for item in import_plan.entities.partner_modules
    }
    assert any(row[1] is None for row in nus_modules)
    assert all(row[1] is not None for row in partner_modules)

    # A repaired identity keeps the normalized code and the corrected presentation.
    assert repaired_mapping is not None
    assert repaired_mapping[:3] == (
        "CS3264",
        "Foundations of Machine Learning",
        None,
    )
    assert float(repaired_mapping[3]) == 0.5

def test_shared_memberships_and_repeated_identities_do_not_multiply_rows(
    legacy_published_catalog: DatabaseTarget, import_plan: ImportPlan
) -> None:
    with _connect(legacy_published_catalog.owner_url) as connection:
        connection.read_only = True
        with connection.transaction():
            degree_counts = connection.execute(
                """
                select d.name, count(mm.id)
                from public.degrees d
                join public.degree_modules dm on dm.degree_id = d.id
                join public.module_mappings mm on mm.nus_module_code = dm.module_code
                group by d.name
                """
            ).fetchall()
            repeated_nus = connection.execute(
                """
                select nus_module_code, count(*)
                from public.module_mappings
                group by nus_module_code
                having count(*) > 1
                """
            ).fetchall()
            repeated_partner = connection.execute(
                """
                select pm.partner_university_id, pm.code, count(*)
                from public.module_mappings mm
                join public.pu_modules pm on pm.id = mm.pu_module_id
                group by pm.partner_university_id, pm.code
                having count(*) > 1
                """
            ).fetchall()
            exact_pairs = connection.execute(
                """
                select nus_module_code, pu_module_id, count(*)
                from public.module_mappings
                group by nus_module_code, pu_module_id
                """
            ).fetchall()
            specialization_memberships = connection.execute(
                """
                select count(*)
                from public.specialization_modules
                """
            ).fetchone()[0]
            bt4240_requirement = connection.execute(
                """
                select dm.requirement_type
                from public.degree_modules dm
                join public.degrees d on d.id = dm.degree_id
                where d.name = 'Business Analytics' and dm.module_code = 'BT4240'
                """
            ).fetchone()
            specialization_rows = connection.execute(
                """
                select count(*)
                from public.specializations
                """
            ).fetchone()[0]

    expected_degree_counts: Counter[str] = Counter()
    for mapping in import_plan.preview["mappings"]:
        for degree in mapping["degree_names"]:
            expected_degree_counts[degree] += 1
    assert dict(degree_counts) == dict(expected_degree_counts)

    # Repeated course codes remain separate mapping rows and source positions.
    planned_nus = Counter(row.nus_module_code for row in import_plan.mappings)
    planned_partner = Counter(
        (row.university, row.partner_module_code) for row in import_plan.mappings
    )
    assert {
        code: count for code, count in planned_nus.items() if count > 1
    } == {code: count for code, count in repeated_nus}
    assert len(repeated_partner) == sum(
        1 for count in planned_partner.values() if count > 1
    )
    assert sum(row[2] for row in repeated_partner) == sum(
        count for count in planned_partner.values() if count > 1
    )
    assert len(exact_pairs) == len(import_plan.mappings)

    # Specialization memberships stay separate from degree requirements.
    assert specialization_memberships == len(import_plan.entities.specialization_modules)
    assert specialization_rows == len(import_plan.entities.specializations)
    assert bt4240_requirement is not None
    assert "specialization:Machine Learning-based Analytics" in bt4240_requirement[0]


def test_identical_import_is_noop_and_changed_snapshot_is_refused(
    database: DatabaseTarget, import_plan: ImportPlan
) -> None:
    first = apply_plan(import_plan, database.importer_url)
    second = apply_plan(import_plan, database.importer_url)

    assert first["action"] == "imported"
    assert second["action"] == "noop"
    assert second["batch_id"] == first["batch_id"]
    assert _catalog_counts_from(database)["batches"] == 1

    changed_preview = copy.deepcopy(import_plan.preview)
    changed_preview["source_snapshot"]["source_checksum_sha256"] = "0" * 64
    changed_plan = replace(import_plan, preview=changed_preview)
    with pytest.raises(ImportRefused, match="different or partial catalog"):
        apply_plan(changed_plan, database.importer_url)

    counts = _catalog_counts_from(database)
    assert counts["batches"] == 1
    assert counts["source_rows"] == import_plan.summary["raw_rows"]


def test_concurrent_importers_serialize_on_the_advisory_lock(
    database: DatabaseTarget, import_plan: ImportPlan
) -> None:
    def run_import() -> dict[str, Any]:
        return apply_plan(import_plan, database.importer_url)

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(run_import), executor.submit(run_import)]
        results = [future.result() for future in futures]

    assert sorted(result["action"] for result in results) == ["imported", "noop"]
    assert len({result["batch_id"] for result in results}) == 1
    counts = _catalog_counts_from(database)
    assert counts["batches"] == 1
    assert counts["source_rows"] == import_plan.summary["raw_rows"]
    assert counts["module_mappings"] == len(import_plan.mappings)


def test_injected_failure_rolls_back_every_table(
    database: DatabaseTarget, import_plan: ImportPlan
) -> None:
    with pytest.raises(SimulatedImportFailure):
        apply_plan(import_plan, database.importer_url, simulate_failure=True)

    counts = _catalog_counts_from(database)
    assert all(value == 0 for value in counts.values())


def test_source_files_remain_unchanged_by_the_import(
    import_plan: ImportPlan,
) -> None:
    for archive in import_plan.archives:
        path = Path(REPO_ROOT) / archive.path
        assert hashlib.sha256(path.read_bytes()).hexdigest() == archive.sha256
