"""Tests for core database seeding and data preservation (US4).

Verifies that the local disposable seeder correctly populates the eight
core catalog tables from the reviewed preview, preserves mapping multiplicity
and degree memberships, rolls back completely on seed failure, and refuses
non-local targets.
"""

import copy
import hashlib
from collections import Counter
from pathlib import Path

import psycopg
import pytest

from scripts.catalog_preview import build_preview
from scripts.catalog_seed import seed_preview
from scripts.postgres_validation import REPO_ROOT, DatabaseTarget


def _core_table_counts(connection: psycopg.Connection) -> dict[str, int]:
    """Return row counts for all eight core catalog tables."""
    tables = [
        "degrees",
        "nus_modules",
        "degree_modules",
        "partner_universities",
        "pu_modules",
        "specializations",
        "specialization_modules",
        "module_mappings",
    ]
    counts = {}
    for table in tables:
        count = connection.execute(f"select count(*) from public.{table}").fetchone()[0]
        counts[table] = int(count)
    return counts


def test_seed_preview_populates_core_tables(database: DatabaseTarget) -> None:
    """Core seeder should populate all eight core tables matching preview entities."""
    preview = build_preview()
    seed_preview(database, preview)

    # Verify row counts match the deterministic preview
    with psycopg.connect(database.reader_url) as conn:
        counts = _core_table_counts(conn)

    assert counts == {
        "degrees": len(preview["degrees"]),
        "nus_modules": len(preview["nus_modules"]),
        "degree_modules": sum(len(d["degree_modules"]) for d in preview["degrees"]),
        "partner_universities": len(preview["universities"]),
        "pu_modules": len(preview["partner_modules"]),
        "specializations": len(preview["specializations"]),
        "specialization_modules": sum(
            len(s["memberships"]) for s in preview["specializations"]
        ),
        "module_mappings": len(preview["mappings"]),
    }
    assert counts["degrees"] == 6
    assert counts["nus_modules"] == 152
    assert counts["partner_universities"] == 5
    assert counts["module_mappings"] == 151


def test_shared_memberships_and_repeated_identities_do_not_multiply_rows(
    published_catalog: DatabaseTarget,
) -> None:
    """Core mappings and degree links should preserve multiplicities without multiplying rows."""
    preview = build_preview()

    with psycopg.connect(published_catalog.reader_url) as conn:
        # Degree module mapping counts
        degree_counts = conn.execute(
            """
            select d.name, count(mm.id)
            from public.degrees d
            join public.degree_modules dm on dm.degree_id = d.id
            join public.module_mappings mm on mm.nus_module_code = dm.module_code
            group by d.name
            """
        ).fetchall()

        # Repeated NUS modules across mappings
        repeated_nus = conn.execute(
            """
            select nus_module_code, count(*)
            from public.module_mappings
            group by nus_module_code
            having count(*) > 1
            """
        ).fetchall()

        # Repeated partner courses
        repeated_partner = conn.execute(
            """
            select pm.partner_university_id, pm.code, count(*)
            from public.module_mappings mm
            join public.pu_modules pm on pm.id = mm.pu_module_id
            group by pm.partner_university_id, pm.code
            having count(*) > 1
            """
        ).fetchall()

        # Exact course pairs
        exact_pairs = conn.execute(
            """
            select nus_module_code, pu_module_id, count(*)
            from public.module_mappings
            group by nus_module_code, pu_module_id
            """
        ).fetchall()

        # Specializations and requirements
        specialization_modules_count = conn.execute(
            "select count(*) from public.specialization_modules"
        ).fetchone()[0]

        specializations_count = conn.execute(
            "select count(*) from public.specializations"
        ).fetchone()[0]

        bt4240_requirement = conn.execute(
            """
            select dm.requirement_type
            from public.degree_modules dm
            join public.degrees d on d.id = dm.degree_id
            where d.name = 'Business Analytics' and dm.module_code = 'BT4240'
            """
        ).fetchone()

    # Compare degree mapping counts with expectations
    expected_degree_counts: Counter[str] = Counter()
    for mapping in preview["mappings"]:
        for degree in mapping["degree_names"]:
            expected_degree_counts[degree] += 1
    assert dict(degree_counts) == dict(expected_degree_counts)

    # Repeated course codes remain separate mapping rows
    planned_nus = Counter(row["nus_module_code"] for row in preview["mappings"])
    planned_partner = Counter(
        (row["university"], row["partner_module_code"]) for row in preview["mappings"]
    )
    assert {
        code: count for code, count in planned_nus.items() if count > 1
    } == {code: count for code, count in repeated_nus}
    assert len(repeated_partner) == sum(
        1 for count in planned_partner.values() if count > 1
    )
    assert len(exact_pairs) == len(preview["mappings"])

    # Specialization memberships remain separate
    expected_spec_modules = sum(len(s["memberships"]) for s in preview["specializations"])
    assert specialization_modules_count == expected_spec_modules
    assert specializations_count == len(preview["specializations"])
    assert bt4240_requirement is not None
    assert "specialization:Machine Learning-based Analytics" in bt4240_requirement[0]


def test_seed_failure_rolls_back_every_core_table(database: DatabaseTarget) -> None:
    """An unhandled error midway through seeding should roll back all tables."""
    preview = copy.deepcopy(build_preview())

    # Introduce an error by breaking a foreign key reference in mappings
    preview["mappings"][0]["partner_module_code"] = "NONEXISTENT_CODE_XYZ"

    with pytest.raises(KeyError):
        seed_preview(database, preview)

    # Confirm all tables remain completely empty after rollback
    with psycopg.connect(database.owner_url) as conn:
        counts = _core_table_counts(conn)
    assert all(value == 0 for value in counts.values())


def test_source_files_remain_unchanged() -> None:
    """Source files on disk must remain unchanged with matching digests."""
    preview = build_preview()
    for file_info in preview["source_snapshot"]["files"]:
        path = Path(REPO_ROOT) / file_info["path"]
        assert path.exists()
        assert hashlib.sha256(path.read_bytes()).hexdigest() == file_info["sha256"]


def test_seed_preview_rejects_remote_targets() -> None:
    """Seeder must refuse execution against non-local database URLs."""
    class FakeRemoteTarget:
        url = "postgresql://user:pass@db.example.com:5432/prod"

    preview = build_preview()

    with pytest.raises(RuntimeError, match="must point at a local disposable PostgreSQL server"):
        seed_preview(FakeRemoteTarget(), preview)  # type: ignore[arg-type]
