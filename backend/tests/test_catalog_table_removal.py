"""Migration-harness checks for the catalog-table removal fixture workflow."""

import subprocess
from pathlib import Path

import psycopg
import pytest

from scripts.postgres_validation import (
    LEGACY_MIGRATION_CEILING,
    MIGRATIONS,
    PostgresCluster,
    migration_version,
    require_local_database_url,
)

pytestmark = pytest.mark.regression

FIXTURE_DIR = Path(__file__).parent / "fixtures"
UPGRADE_FIXTURE = FIXTURE_DIR / "pre_catalog_removal.sql"


def _write_migration(tmp_path: Path, version: str, sql: str) -> Path:
    """Create one temporary migration in an isolated directory."""

    path = tmp_path / f"{version}_test_migration.sql"
    path.write_text(sql, encoding="utf-8")
    return path


def test_database_ceiling_stops_at_pre_removal_version(postgres_cluster: PostgresCluster) -> None:
    database = postgres_cluster.create_database(through=LEGACY_MIGRATION_CEILING)
    try:
        versions = [migration_version(path) for path in database.applied_migrations]
        assert versions[-1] == LEGACY_MIGRATION_CEILING
        assert versions == [migration_version(path) for path in MIGRATIONS[: len(versions)]]

        # The metadata tables exist at the ceiling and are ready for fixture data.
        with psycopg.connect(database.owner_url) as connection:
            connection.read_only = True
            for table in (
                "catalog_import_batches",
                "catalog_source_snapshots",
                "catalog_source_rows",
                "catalog_issues",
                "catalog_repairs",
            ):
                assert connection.execute(
                    "select to_regclass(%s)", (f"public.{table}",)
                ).fetchone()[0] is not None
    finally:
        postgres_cluster.drop_database(database)

    # An unknown ceiling is rejected before a database is created.
    with pytest.raises(ValueError, match="unknown migration ceiling"):
        postgres_cluster.create_database(through="99999999999999")


def test_default_database_setup_still_replays_every_migration(
    postgres_cluster: PostgresCluster,
) -> None:
    database = postgres_cluster.create_database()
    try:
        assert tuple(database.applied_migrations) == MIGRATIONS
    finally:
        postgres_cluster.drop_database(database)


def test_upgrade_fixture_loads_at_the_migration_ceiling(
    postgres_cluster: PostgresCluster,
) -> None:
    database = postgres_cluster.create_database(through=LEGACY_MIGRATION_CEILING)
    try:
        database.execute_file(UPGRADE_FIXTURE)
        with psycopg.connect(database.owner_url) as connection:
            connection.read_only = True
            counts = connection.execute(
                """
                select
                  (select count(*) from public.catalog_import_batches),
                  (select count(*) from public.catalog_source_snapshots),
                  (select count(*) from public.catalog_source_rows),
                  (select count(*) from public.catalog_issues),
                  (select count(*) from public.catalog_repairs),
                  (select count(*) from public.degrees),
                  (select count(*) from public.nus_modules),
                  (select count(*) from public.degree_modules),
                  (select count(*) from public.specializations),
                  (select count(*) from public.specialization_modules),
                  (select count(*) from public.partner_universities),
                  (select count(*) from public.pu_modules),
                  (select count(*) from public.module_mappings),
                  (select count(*) from public.module_mappings
                   where source_row_id is not null)
                """
            ).fetchone()
            duplicate = connection.execute(
                """
                select nus_module_code, pu_module_id, count(*)
                from public.module_mappings
                group by nus_module_code, pu_module_id
                having count(*) > 1
                """
            ).fetchall()
            sequence_value = connection.execute(
                "select last_value from public.module_mappings_id_seq"
            ).fetchone()[0]

        assert counts == (1, 8, 155, 34, 44, 6, 152, 226, 19, 30, 5, 142, 152, 152)
        assert duplicate == [("CS3213", 100, 2)]
        assert sequence_value == 152
    finally:
        postgres_cluster.drop_database(database)


def test_apply_next_migration_applies_exactly_one_pending_migration(
    tmp_path: Path,
) -> None:
    next_migration = _write_migration(
        tmp_path,
        "20261023000400",
        "create table public.test_next_migration_marker (id integer primary key);",
    )
    cluster = PostgresCluster(migrations=(*MIGRATIONS, next_migration))
    cluster.start()
    try:
        database = cluster.create_database(through=LEGACY_MIGRATION_CEILING)
        assert migration_version(database.applied_migrations[-1]) == LEGACY_MIGRATION_CEILING

        advanced = cluster.apply_next_migration(database)

        assert migration_version(advanced.applied_migrations[-1]) == "20261023000400"
        assert len(advanced.applied_migrations) == len(database.applied_migrations) + 1
        with psycopg.connect(advanced.owner_url) as connection:
            assert connection.execute(
                "select to_regclass('public.test_next_migration_marker')"
            ).fetchone()[0] is not None

        # A second call refuses to apply anything once the chain is exhausted.
        with pytest.raises(RuntimeError, match="no pending migrations"):
            cluster.apply_next_migration(advanced)
    finally:
        cluster.stop()


def test_apply_next_migration_propagates_sql_errors(tmp_path: Path) -> None:
    bad_migration = _write_migration(
        tmp_path,
        "20261023000400",
        "select * from public.table_that_does_not_exist;",
    )
    cluster = PostgresCluster(migrations=(*MIGRATIONS, bad_migration))
    cluster.start()
    try:
        database = cluster.create_database(through=LEGACY_MIGRATION_CEILING)

        with pytest.raises(subprocess.CalledProcessError):
            cluster.apply_next_migration(database)

        # The failed migration was not recorded as applied.
        assert migration_version(database.applied_migrations[-1]) == LEGACY_MIGRATION_CEILING
    finally:
        cluster.stop()


def test_database_setup_rejects_external_targets() -> None:
    with pytest.raises(RuntimeError, match="local disposable PostgreSQL server"):
        require_local_database_url(
            "postgresql://db.example.com:5432/catalog", "TEST_DATABASE_URL"
        )
    require_local_database_url(
        "postgresql://127.0.0.1:5432/catalog", "TEST_DATABASE_URL"
    )
