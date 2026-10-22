"""Seed a disposable database from the deterministic import preview.

This is validation tooling only. It must never run against the production
Supabase project; the importer in Phase 3 owns real publication.
"""

from typing import Any

import psycopg
from psycopg.types.json import Jsonb

from scripts.postgres_validation import DatabaseTarget


def seed_preview(database: DatabaseTarget, preview: dict[str, Any]) -> None:
    """Publish the preview's active catalog rows into an empty migrated database."""

    with psycopg.connect(database.url) as conn, conn.transaction():
        _insert_batch(conn, preview)
        degree_ids = _insert_degrees(conn, preview["degrees"])
        _insert_nus_modules(conn, preview["nus_modules"])
        _insert_degree_modules(conn, preview["degrees"], degree_ids)
        university_ids = _insert_universities(conn, preview["universities"])
        partner_ids = _insert_partner_modules(
            conn, preview["partner_modules"], university_ids
        )
        _insert_mappings(conn, preview["mappings"], partner_ids)
        _insert_specializations(conn, preview["specializations"], degree_ids)


def _insert_batch(conn: psycopg.Connection, preview: dict[str, Any]) -> None:
    snapshot = preview["source_snapshot"]
    summary = preview["summary"]
    conn.execute(
        """
        insert into public.catalog_import_batches (
          source_checksum, repair_checksum, status, is_current,
          source_manifest, source_file_count, raw_row_count,
          accepted_row_count, repaired_row_count, quarantined_row_count,
          completed_at, note
        ) values (%s, %s, 'completed', true, %s, %s, %s, %s, %s, %s, now(), %s)
        """,
        (
            snapshot["source_checksum_sha256"],
            snapshot["repair_checksum_sha256"],
            Jsonb({"files": [item["path"] for item in snapshot["files"]]}),
            len(snapshot["files"]),
            summary["raw_rows"],
            summary["accepted_rows"],
            summary["repaired_rows"],
            summary["quarantined_rows"],
            "Disposable validation seed from the import preview.",
        ),
    )


def _insert_degrees(
    conn: psycopg.Connection, degrees: list[dict[str, Any]]
) -> dict[str, int]:
    ids: dict[str, int] = {}
    for degree in degrees:
        row = conn.execute(
            """
            insert into public.degrees (name, faculty, full_title, source_order)
            values (%s, %s, %s, %s)
            returning id
            """,
            (
                degree["name"],
                degree["faculty"],
                degree["full_title"],
                degree["source_order"],
            ),
        ).fetchone()
        ids[degree["name"]] = int(row[0])
    return ids


def _insert_nus_modules(
    conn: psycopg.Connection, modules: list[dict[str, Any]]
) -> None:
    conn.cursor().executemany(
        """
        insert into public.nus_modules (code, name, offering_faculty, verified_units)
        values (%s, %s, %s, %s)
        """,
        [
            (module["code"], module["name"], module["offering_faculty"], module["verified_units"])
            for module in modules
        ],
    )


def _insert_degree_modules(
    conn: psycopg.Connection,
    degrees: list[dict[str, Any]],
    degree_ids: dict[str, int],
) -> None:
    rows = []
    for degree in degrees:
        for module in degree["degree_modules"]:
            rows.append(
                (degree_ids[degree["name"]], module["code"], module["requirement_type"])
            )
    conn.cursor().executemany(
        """
        insert into public.degree_modules (degree_id, module_code, requirement_type)
        values (%s, %s, %s)
        on conflict (degree_id, module_code) do nothing
        """,
        rows,
    )


def _insert_universities(
    conn: psycopg.Connection, universities: list[dict[str, Any]]
) -> dict[str, int]:
    ids: dict[str, int] = {}
    for university in universities:
        row = conn.execute(
            """
            insert into public.partner_universities (
              name, country, city, continent, source_order
            ) values (%s, %s, %s, %s, %s)
            returning id
            """,
            (
                university["name"],
                university["country"],
                university["city"],
                university["continent"],
                university["source_order"],
            ),
        ).fetchone()
        ids[university["name"]] = int(row[0])
    return ids


def _insert_partner_modules(
    conn: psycopg.Connection,
    modules: list[dict[str, Any]],
    university_ids: dict[str, int],
) -> dict[tuple[str, str], int]:
    ids: dict[tuple[str, str], int] = {}
    for module in modules:
        row = conn.execute(
            """
            insert into public.pu_modules (
              code, name, partner_university_id, verified_units
            ) values (%s, %s, %s, %s)
            returning id
            """,
            (
                module["code"],
                module["name"],
                university_ids[module["university"]],
                module["verified_units"],
            ),
        ).fetchone()
        ids[(module["university"], module["code"])] = int(row[0])
    return ids


def _insert_mappings(
    conn: psycopg.Connection,
    mappings: list[dict[str, Any]],
    partner_ids: dict[tuple[str, str], int],
) -> None:
    rows = []
    for row in mappings:
        # Active mappings always have normalized codes after verified repairs.
        if row["nus_module_code"] is None or row["partner_module_code"] is None:
            raise ValueError(f"Active mapping {row['mapping_index']} has no normalized code")
        rows.append(
            (
                row["nus_module_code"],
                partner_ids[(row["university"], row["partner_module_code"])],
                row["source_order"],
                row["mapping_nus_title"],
                row["mapping_nus_units"],
                row["mapping_partner_title"],
                row["mapping_partner_units"],
                row["mapping_faculty"],
                row["mapping_page"],
            )
        )
    conn.cursor().executemany(
        """
        insert into public.module_mappings (
          nus_module_code, pu_module_id, source_order,
          source_nus_title, source_nus_units,
          source_partner_title, source_partner_units,
          source_faculty, source_page
        ) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        rows,
    )


def _insert_specializations(
    conn: psycopg.Connection,
    specializations: list[dict[str, Any]],
    degree_ids: dict[str, int],
) -> None:
    for specialization in specializations:
        row = conn.execute(
            """
            insert into public.specializations (degree_id, name, kind, source_order)
            values (%s, %s, %s, %s)
            returning id
            """,
            (
                degree_ids[specialization["degree"]],
                specialization["name"],
                specialization["kind"],
                specialization["source_order"],
            ),
        ).fetchone()
        specialization_id = int(row[0])
        conn.cursor().executemany(
            """
            insert into public.specialization_modules (specialization_id, module_code)
            values (%s, %s)
            on conflict (specialization_id, module_code) do nothing
            """,
            [
                (specialization_id, code)
                for code in specialization["memberships"]
            ],
        )
