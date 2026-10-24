"""Fresh-schema absence checks after the catalog-metadata removal migration.

These tests apply the removal migration on top of the legacy ceiling, core-seed
the eight retained tables, and assert the end state: no `catalog_`-prefixed
table in `public`, no `module_mappings.source_row_id` column, no archive-guard
function, the eight core tables intact, and the reader role still able to SELECT
core data while removed relations cannot be resolved by operational SQL.
"""

import psycopg
import pytest

from scripts.catalog_preview import build_preview
from scripts.catalog_seed import seed_preview
from scripts.postgres_validation import (
    LEGACY_MIGRATION_CEILING,
    DatabaseTarget,
    PostgresCluster,
    migration_version,
)

pytestmark = pytest.mark.regression

REMOVAL_VERSION = "20261024034234"

METADATA_TABLES = (
    "catalog_import_batches",
    "catalog_source_snapshots",
    "catalog_source_rows",
    "catalog_issues",
    "catalog_repairs",
)

CORE_TABLES = (
    "degrees",
    "nus_modules",
    "degree_modules",
    "specializations",
    "specialization_modules",
    "partner_universities",
    "pu_modules",
    "module_mappings",
)


@pytest.fixture(scope="module")
def removed_catalog(postgres_cluster: PostgresCluster):
    """A core-seeded database with the removal migration applied once.

    Built on the legacy ceiling, advanced by exactly the removal migration, then
    seeded with the eight core tables from the reviewed preview — the same path
    the runtime uses, with no importer and no metadata writes.
    """

    database = postgres_cluster.create_database(through=LEGACY_MIGRATION_CEILING)
    advanced = postgres_cluster.apply_next_migration(database)
    assert migration_version(advanced.applied_migrations[-1]) == REMOVAL_VERSION
    seed_preview(advanced, build_preview())
    yield advanced
    postgres_cluster.drop_database(advanced)


def test_source_row_id_column_is_absent(removed_catalog: DatabaseTarget) -> None:
    """T028: module_mappings.source_row_id and its constraints are gone."""

    with psycopg.connect(removed_catalog.owner_url) as connection:
        connection.read_only = True
        assert connection.execute(
            """
            select 1 from information_schema.columns
            where table_schema = 'public'
              and table_name = 'module_mappings'
              and column_name = 'source_row_id'
            """
        ).fetchone() is None
        remaining = connection.execute(
            """
            select conname from pg_constraint
            where conrelid = 'public.module_mappings'::regclass
              and conname in (
                'module_mappings_source_row_id_fkey',
                'module_mappings_source_row_id_key'
              )
            """
        ).fetchall()
        assert remaining == []


def test_core_tables_remain(removed_catalog: DatabaseTarget) -> None:
    """All eight retained core tables still exist in public."""

    with psycopg.connect(removed_catalog.owner_url) as connection:
        connection.read_only = True
        present = connection.execute(
            """
            select table_name from information_schema.tables
            where table_schema = 'public' and table_name = any(%s)
            order by table_name
            """,
            (list(CORE_TABLES),),
        ).fetchall()
    assert sorted(name for (name,) in present) == sorted(CORE_TABLES)


def test_no_catalog_prefixed_tables_remain(removed_catalog: DatabaseTarget) -> None:
    """T029: no literal `catalog_`-prefixed relation remains in public."""

    with psycopg.connect(removed_catalog.owner_url) as connection:
        connection.read_only = True
        remaining = connection.execute(
            r"""
            select tablename from pg_tables
            where schemaname = 'public' and tablename like 'catalog\_%'
            order by tablename
            """
        ).fetchall()
    assert remaining == []


def test_named_metadata_tables_are_absent(removed_catalog: DatabaseTarget) -> None:
    """T029: each of the five named metadata tables cannot be resolved."""

    with psycopg.connect(removed_catalog.owner_url) as connection:
        connection.read_only = True
        for table in METADATA_TABLES:
            assert connection.execute(
                "select to_regclass(%s)", (f"public.{table}",)
            ).fetchone()[0] is None


def test_archive_guard_function_is_absent(removed_catalog: DatabaseTarget) -> None:
    """T029: the unused archive-guard trigger function is removed."""

    with psycopg.connect(removed_catalog.owner_url) as connection:
        connection.read_only = True
        assert connection.execute(
            """
            select 1 from pg_proc p
            join pg_namespace n on n.oid = p.pronamespace
            where n.nspname = 'public'
              and p.proname = 'reject_catalog_archive_mutation'
            """
        ).fetchone() is None


def test_reader_role_reads_core_after_seeding(removed_catalog: DatabaseTarget) -> None:
    """The reader role can SELECT core data on the final core-only schema."""

    with psycopg.connect(removed_catalog.reader_url) as connection:
        assert connection.execute("select count(*) from public.degrees").fetchone()[0] > 0
        assert (
            connection.execute("select count(*) from public.module_mappings").fetchone()[0]
            > 0
        )


def test_operational_sql_cannot_query_removed_relations(
    removed_catalog: DatabaseTarget,
) -> None:
    """T029: querying a removed relation raises UndefinedTable, not silent data."""

    with (
        psycopg.connect(removed_catalog.reader_url) as connection,
        pytest.raises(psycopg.errors.UndefinedTable),
    ):
        connection.execute("select 1 from public.catalog_import_batches")
