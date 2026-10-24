"""Migration-harness checks for the catalog-table removal fixture workflow."""

import subprocess
import time
from pathlib import Path

import psycopg
import pytest

from scripts.catalog_preview import build_preview
from scripts.catalog_seed import seed_preview
from scripts.postgres_validation import (
    LEGACY_MIGRATION_CEILING,
    MIGRATIONS,
    DatabaseTarget,
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


# --- T030 / T031: retained constraints, RLS, and reader permissions --------

CORE_RLS_TABLES: tuple[str, ...] = (
    "degrees",
    "nus_modules",
    "degree_modules",
    "specializations",
    "specialization_modules",
    "partner_universities",
    "pu_modules",
    "module_mappings",
)


def _normalize_check(definition: str) -> str:
    """Collapse PostgreSQL's rendered CHECK text for semantic comparison.

    PostgreSQL re-renders a CHECK clause with its own spacing, casts, and
    parentheses, so a literal string match is brittle. Lowercasing and removing
    spaces/parentheses/`::type` casts compares the predicate's meaning, not its
    exact printed form.
    """

    import re

    text = definition.lower()
    text = re.sub(r"::[a-z0-9_ ]+", "", text)  # drop type casts e.g. ::numeric, ::text
    text = re.sub(r"[()\[\]\s]", "", text)  # drop parentheses, brackets, and whitespace
    return text


def _check_defs(connection: psycopg.Connection) -> dict[str, str]:
    """Return {constraint_name: normalized CHECK definition} for public checks."""

    rows = connection.execute(
        """
        select conname, pg_get_constraintdef(oid)
        from pg_constraint
        where contype = 'c' and connamespace = 'public'::regnamespace
        """
    ).fetchall()
    return {name: _normalize_check(defn) for name, defn in rows}


@pytest.fixture(scope="module")
def _final_schema(postgres_cluster: PostgresCluster):
    """A core-seeded database with the removal migration applied (module-scoped)."""

    database = postgres_cluster.create_database(through=LEGACY_MIGRATION_CEILING)
    advanced = postgres_cluster.apply_next_migration(database)
    assert migration_version(advanced.applied_migrations[-1]) == REMOVAL_VERSION
    seed_preview(advanced, build_preview())
    yield advanced
    postgres_cluster.drop_database(advanced)


def test_retained_core_check_constraints_present(_final_schema) -> None:
    """T030: the four named core check constraints survive with their meaning."""

    expected = {
        "nus_modules_verified_units_check": "check verified_units is null or verified_units > 0",
        "specializations_kind_check": "check kind = any array'specialization','focus_area'",
        "degrees_source_order_check": "check source_order is null or source_order >= 0",
        "nus_modules_code_check": "check btrim(code) <> '' and code = upper(btrim(code))",
    }
    with psycopg.connect(_final_schema.owner_url) as connection:
        connection.read_only = True
        defs = _check_defs(connection)
    for name, raw in expected.items():
        assert name in defs, f"missing check constraint {name}"
        assert defs[name] == _normalize_check(raw), (name, defs[name])


def test_retained_keys_and_rls_policies(_final_schema) -> None:
    """T030: RLS stays enabled on every core table with its reader SELECT policy."""

    with psycopg.connect(_final_schema.owner_url) as connection:
        connection.read_only = True
        rls = dict(
            connection.execute(
                """
                select relname, relrowsecurity from pg_class
                where relnamespace = 'public'::regnamespace and relkind = 'r'
                  and relname = any(%s)
                """,
                (list(CORE_RLS_TABLES),),
            ).fetchall()
        )
        policies = connection.execute(
            """
            select tablename, policyname, cmd, roles::text
            from pg_policies where schemaname = 'public'
            order by tablename
            """
        ).fetchall()
        primary_keys = connection.execute(
            """
            select conrelid::regclass::text
            from pg_constraint
            where contype = 'p' and connamespace = 'public'::regnamespace
            """
        ).fetchall()
    for table in CORE_RLS_TABLES:
        assert rls.get(table) is True, f"RLS not enabled on {table}"
    reader_tables = {
        table for table, _name, cmd, roles in policies
        if cmd == "SELECT" and "catalog_reader" in roles
    }
    assert reader_tables == set(CORE_RLS_TABLES)
    # Every core table that has a primary key kept it (the removal touched none).
    pk_tables = {name for (name,) in primary_keys}
    for table in ("degrees", "nus_modules", "module_mappings"):
        assert f"public.{table}" in pk_tables or table in {
            name.split(".")[-1] for name in pk_tables
        }


def test_reader_role_has_only_select_on_core_tables(_final_schema) -> None:
    """T030: no browser/write privilege was introduced; reader is SELECT-only."""

    with psycopg.connect(_final_schema.owner_url) as connection:
        connection.read_only = True
        grants = connection.execute(
            """
            select table_name, privilege_type
            from information_schema.role_table_grants
            where grantee = 'catalog_reader'
            order by table_name, privilege_type
            """
        ).fetchall()
    tables = {table for table, _priv in grants}
    privileges = {priv for _table, priv in grants}
    # Reader can SELECT exactly the eight core tables and nothing else remains
    # grantable (the metadata-table grants vanished with the tables).
    assert tables == set(CORE_RLS_TABLES)
    assert privileges == {"SELECT"}


def test_retained_mapping_check_constraints_present(_final_schema) -> None:
    """T031: the six retained module_mappings source_* checks survive."""

    expected = {
        "module_mappings_source_nus_title_check": "check source_nus_title is null or btrim(source_nus_title) <> ''",
        "module_mappings_source_partner_title_check": "check source_partner_title is null or btrim(source_partner_title) <> ''",
        "module_mappings_source_nus_units_check": "check source_nus_units is null or source_nus_units > 0",
        "module_mappings_source_partner_units_check": "check source_partner_units is null or source_partner_units > 0",
        "module_mappings_source_faculty_check": "check source_faculty is null or btrim(source_faculty) <> ''",
        "module_mappings_source_page_check": "check source_page is null or source_page > 0",
    }
    with psycopg.connect(_final_schema.owner_url) as connection:
        connection.read_only = True
        defs = _check_defs(connection)
    for name, raw in expected.items():
        assert name in defs, f"missing check constraint {name}"
        assert defs[name] == _normalize_check(raw), (name, defs[name])


def test_mapping_nullable_unknowns_and_duplicates_remain_valid(_final_schema) -> None:
    """T031: nullable source_* unknowns and intentional repeated pairs insert fine.

    Writes go through the owner connection into a disposable database; the core
    seeder left the table populated, so this proves the retained checks admit
    nulls and that no unique constraint blocks a repeated (nus, pu) pair.
    """

    with psycopg.connect(_final_schema.owner_url) as connection:
        nus = connection.execute(
            "select code from public.nus_modules limit 1"
        ).fetchone()[0]
        pu = connection.execute(
            "select id from public.pu_modules limit 1"
        ).fetchone()[0]
        # Two rows for the SAME (nus, pu) pair, all source_* columns NULL.
        connection.execute(
            """
            insert into public.module_mappings (nus_module_code, pu_module_id)
            values (%s, %s), (%s, %s)
            """,
            (nus, pu, nus, pu),
        )
        count = connection.execute(
            """
            select count(*) from public.module_mappings
            where nus_module_code = %s and pu_module_id = %s
            """,
            (nus, pu),
        ).fetchone()[0]
        connection.rollback()
    assert count >= 2


# --- T033: migration abort behavior ----------------------------------------

REMOVAL_MIGRATION_PATH = (
    Path(__file__).resolve().parents[1].parent
    / "supabase"
    / "migrations"
    / f"{REMOVAL_VERSION}_remove_catalog_metadata.sql"
)


def _apply_migration_file(database: DatabaseTarget) -> subprocess.CompletedProcess:
    """Apply the real removal migration as owner, returning the psql result.

    Uses ON_ERROR_STOP so any statement error returns a nonzero exit code; the
    migration's own BEGIN/COMMIT means a failure rolls the whole thing back.
    """

    return subprocess.run(
        [
            database.cluster.psql,
            "-X",
            "-v",
            "ON_ERROR_STOP=1",
            "-d",
            database.owner_url,
            "-f",
            str(REMOVAL_MIGRATION_PATH),
        ],
        check=False,
        capture_output=True,
        text=True,
    )


def _metadata_state(database: DatabaseTarget) -> tuple[int, bool]:
    """Return (count of catalog_ tables, whether source_row_id still exists)."""

    with psycopg.connect(database.owner_url) as connection:
        connection.read_only = True
        present = connection.execute(
            r"""
            select count(*) from pg_tables
            where schemaname = 'public' and tablename like 'catalog\_%'
            """
        ).fetchone()[0]
        has_column = connection.execute(
            """
            select 1 from information_schema.columns
            where table_schema = 'public'
              and table_name = 'module_mappings'
              and column_name = 'source_row_id'
            """
        ).fetchone() is not None
    return present, has_column


def test_migration_aborts_on_unexpected_dependency(
    postgres_cluster: PostgresCluster,
) -> None:
    """An unexpected dependent object makes a RESTRICT drop fail and roll back."""

    database = postgres_cluster.create_database(through=LEGACY_MIGRATION_CEILING)
    try:
        # An unexpected view on a metadata table — not part of schema-inventory.
        database.execute(
            "create view public.unexpected_dep as "
            "select id from public.catalog_import_batches;"
        )
        result = _apply_migration_file(database)

        assert result.returncode != 0
        assert "depend" in result.stderr.lower()
        # Nothing was applied: all five tables and source_row_id remain.
        present, has_column = _metadata_state(database)
        assert present == 5
        assert has_column is True
        # The migration is not recorded as applied in the harness state.
        assert migration_version(database.applied_migrations[-1]) == LEGACY_MIGRATION_CEILING
    finally:
        postgres_cluster.drop_database(database)


def test_migration_aborts_on_conflicting_lock_then_normal_path(
    postgres_cluster: PostgresCluster,
) -> None:
    """A held conflicting lock aborts the migration within lock_timeout; the
    normal path then succeeds once the lock is released."""

    database = postgres_cluster.create_database(through=LEGACY_MIGRATION_CEILING)
    try:
        holder = psycopg.connect(database.owner_url)
        holder.autocommit = False
        try:
            holder.execute("begin")
            holder.execute(
                "lock table public.module_mappings in access exclusive mode"
            )

            started = time.monotonic()
            result = _apply_migration_file(database)
            waited = time.monotonic() - started

            assert result.returncode != 0
            assert "lock timeout" in result.stderr.lower()
            # Bounded waiting: the 5s lock_timeout fired, not an unbounded block.
            assert waited < 20
            present, has_column = _metadata_state(database)
            assert present == 5
            assert has_column is True
        finally:
            holder.rollback()
            holder.close()

        # With the lock released, the migration applies cleanly end to end.
        normal = _apply_migration_file(database)
        assert normal.returncode == 0
        present, has_column = _metadata_state(database)
        assert present == 0
        assert has_column is False
    finally:
        postgres_cluster.drop_database(database)
