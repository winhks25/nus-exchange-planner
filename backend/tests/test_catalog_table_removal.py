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

# The catalog-metadata removal migration (T027): the single pending migration
# after the legacy ceiling.
REMOVAL_VERSION = "20261024034234"

# Migrations up to and including the legacy ceiling. The harness-only tests
# below build a cluster from this slice plus a synthetic marker so the next
# pending migration is that marker, independent of the real removal migration
# that now follows the ceiling in the full MIGRATIONS tuple.
MIGRATIONS_THROUGH_CEILING = tuple(
    migration
    for migration in MIGRATIONS
    if migration_version(migration) <= LEGACY_MIGRATION_CEILING
)


def _write_migration(tmp_path: Path, version: str, sql: str) -> Path:
    """Create one temporary migration in an isolated directory."""

    path = tmp_path / f"{version}_test_migration.sql"
    path.write_text(sql, encoding="utf-8")
    return path


def _ceiling_chain_with_marker(tmp_path: Path, version: str, sql: str) -> tuple[Path, ...]:
    """Stage the ceiling migrations plus one marker in a single directory.

    `PostgresCluster` sorts its migrations by full path, so a marker written to
    a different directory than the real migrations would sort out of version
    order. Copying the ceiling migrations alongside the marker keeps path order
    identical to version order, which is what `apply_next_migration` relies on.
    """

    for migration in MIGRATIONS_THROUGH_CEILING:
        (tmp_path / migration.name).write_text(
            migration.read_text(encoding="utf-8"), encoding="utf-8"
        )
    marker = _write_migration(tmp_path, version, sql)
    return (*sorted(tmp_path / m.name for m in MIGRATIONS_THROUGH_CEILING), marker)


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
    migrations = _ceiling_chain_with_marker(
        tmp_path,
        "20261023000400",
        "create table public.test_next_migration_marker (id integer primary key);",
    )
    cluster = PostgresCluster(migrations=migrations)
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
    migrations = _ceiling_chain_with_marker(
        tmp_path,
        "20261023000400",
        "select * from public.table_that_does_not_exist;",
    )
    cluster = PostgresCluster(migrations=migrations)
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


# --- T024: upgrade preservation --------------------------------------------

# The eight retained core tables. Each snapshot row set is ordered by its full
# selected column list (by ordinal position) so the ordering is deterministic
# for every table, including the two junction tables that have no id column.
_CORE_TABLES: tuple[str, ...] = (
    "degrees",
    "nus_modules",
    "degree_modules",
    "specializations",
    "specialization_modules",
    "partner_universities",
    "pu_modules",
    "module_mappings",
)

# Sequences owned by core identity columns; their last_value must survive the
# migration unchanged. The two junction tables and the text-keyed nus_modules
# have no sequence.
_CORE_SEQUENCES: tuple[str, ...] = (
    "degrees_id_seq",
    "specializations_id_seq",
    "partner_universities_id_seq",
    "pu_modules_id_seq",
    "module_mappings_id_seq",
)


def _core_columns(
    connection: psycopg.Connection, table: str, *, exclude: frozenset[str] = frozenset()
) -> list[str]:
    """Return a table's column names in ordinal order, minus excluded ones."""

    rows = connection.execute(
        """
        select column_name
        from information_schema.columns
        where table_schema = 'public' and table_name = %s
        order by ordinal_position
        """,
        (table,),
    ).fetchall()
    return [name for (name,) in rows if name not in exclude]


def _core_snapshot(
    connection: psycopg.Connection, *, exclude: dict[str, frozenset[str]] | None = None
) -> dict[str, object]:
    """Snapshot full ordered rows of the eight core tables and sequence state.

    IDs are included so the snapshot proves identity, not just row counts. The
    caller excludes `source_row_id` from `module_mappings` so the ONLY expected
    difference across the migration is that column's removal.
    """

    exclude = exclude or {}
    tables: dict[str, object] = {}
    for table in _CORE_TABLES:
        columns = _core_columns(connection, table, exclude=exclude.get(table, frozenset()))
        column_sql = ", ".join(f'"{name}"' for name in columns)
        order_sql = ", ".join(str(index) for index in range(1, len(columns) + 1))
        rows = connection.execute(
            f"select {column_sql} from public.{table} order by {order_sql}"
        ).fetchall()
        tables[table] = {"columns": columns, "rows": rows}
    sequences = {
        name: connection.execute(f"select last_value from public.{name}").fetchone()[0]
        for name in _CORE_SEQUENCES
    }
    return {"tables": tables, "sequences": sequences}


def test_removal_migration_preserves_core_data_and_only_drops_source_row_id(
    postgres_cluster: PostgresCluster,
) -> None:
    """Upgrade a populated database and assert only source_row_id is removed.

    The fixture populates real provenance links (non-null source_row_id). The
    before-snapshot excludes that column so the comparison fails if the
    migration changed any retained row, title, unit, order, membership, or
    mapping occurrence — it cannot pass by ignoring the foreign-key removal.
    """

    database = postgres_cluster.create_database(through=LEGACY_MIGRATION_CEILING)
    try:
        database.execute_file(UPGRADE_FIXTURE)

        with psycopg.connect(database.owner_url) as connection:
            connection.read_only = True
            # The migration must have real work to do: the column exists and is
            # actually linked, so a no-op drop cannot masquerade as success.
            assert connection.execute(
                """
                select 1 from information_schema.columns
                where table_schema = 'public'
                  and table_name = 'module_mappings'
                  and column_name = 'source_row_id'
                """
            ).fetchone() is not None
            linked = connection.execute(
                "select count(*) from public.module_mappings where source_row_id is not null"
            ).fetchone()[0]
            assert linked > 0
            before = _core_snapshot(
                connection,
                exclude={"module_mappings": frozenset({"source_row_id"})},
            )

        advanced = postgres_cluster.apply_next_migration(database)
        assert migration_version(advanced.applied_migrations[-1]) == REMOVAL_VERSION

        with psycopg.connect(database.owner_url) as connection:
            connection.read_only = True
            # source_row_id and its two constraints are gone.
            assert connection.execute(
                """
                select 1 from information_schema.columns
                where table_schema = 'public'
                  and table_name = 'module_mappings'
                  and column_name = 'source_row_id'
                """
            ).fetchone() is None
            for constraint in (
                "module_mappings_source_row_id_fkey",
                "module_mappings_source_row_id_key",
            ):
                assert connection.execute(
                    "select 1 from pg_constraint where conname = %s", (constraint,)
                ).fetchone() is None
            # The unrelated source_order index is preserved.
            assert connection.execute(
                """
                select 1 from pg_indexes
                where schemaname = 'public'
                  and indexname = 'module_mappings_nus_code_source_order_idx'
                """
            ).fetchone() is not None
            after = _core_snapshot(
                connection,
                exclude={"module_mappings": frozenset({"source_row_id"})},
            )

        # Every retained column, row, ID, and sequence is byte-for-byte identical.
        assert after == before
    finally:
        postgres_cluster.drop_database(database)
