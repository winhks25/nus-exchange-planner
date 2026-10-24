"""Seed a disposable local database from the deterministic import preview.

This is disposable validation tooling only. It must never run against the
production Supabase project; it seeds only the eight core catalog tables
and writes nothing to metadata tables.
"""

from typing import Any

import psycopg

from scripts.postgres_validation import DatabaseTarget, require_local_database_url


def seed_preview(database: DatabaseTarget, preview: dict[str, Any]) -> None:
    """Insert preview core rows into an empty migrated local database."""

    # Reject any non-local target before connecting
    require_local_database_url(database.url, "catalog seed target")

    # Run in a single transaction in dependency order (parents before children)
    with psycopg.connect(database.url) as conn, conn.transaction():
        # Insert degree records and resolve primary keys
        degree_ids = _insert_degrees(conn, preview["degrees"])

        # Insert NUS modules
        _insert_nus_modules(conn, preview["nus_modules"])

        # Insert degree-module memberships linking degrees to NUS modules
        _insert_degree_modules(conn, preview["degrees"], degree_ids)

        # Insert partner universities and resolve primary keys
        university_ids = _insert_universities(conn, preview["universities"])

        # Insert partner university modules linking to partner universities
        partner_ids = _insert_partner_modules(
            conn, preview["partner_modules"], university_ids
        )

        # Insert active course mappings preserving multiplicity and source order
        _insert_mappings(conn, preview["mappings"], partner_ids)

        # Insert specializations and their module memberships
        _insert_specializations(conn, preview["specializations"], degree_ids)


def _insert_degrees(
    conn: psycopg.Connection, degrees: list[dict[str, Any]]
) -> dict[str, int]:
    """Insert degrees and return a mapping from degree name to generated ID."""
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
    """Insert NUS modules with offering faculty and verified units."""
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
    """Insert degree requirements linking degrees to NUS module codes."""
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
    """Insert partner universities and return a mapping from name to generated ID."""
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
    """Insert partner university modules and map (university, code) to generated ID."""
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
    """Insert module mappings preserving duplicate course pairs and presentation details."""
    rows = []
    for row in mappings:
        # Check normalized codes
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
    """Insert degree specializations/focus areas and their module memberships."""
    for specialization in specializations:
        # Insert specialization header
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

        # Insert specialization module memberships
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
