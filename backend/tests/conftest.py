import os
from collections.abc import Iterator

import psycopg
import pytest

# Keep legacy fixture tests on JSON even when the developer shell targets a real database.
os.environ["CATALOG_BACKEND"] = "json"
os.environ.pop("DATABASE_URL", None)

from scripts.catalog_preview import build_preview
from scripts.catalog_seed import seed_preview
from scripts.import_catalog import ImportPlan, apply_plan, build_import_plan
from scripts.postgres_validation import (
    LEGACY_MIGRATION_CEILING,
    DatabaseTarget,
    PostgresCluster,
    require_local_database_url,
)


def pytest_configure(config: pytest.Config) -> None:
    """Reject an external test target before any regression database is created."""

    configured_url = os.environ.get("TEST_DATABASE_URL")
    if configured_url:
        require_local_database_url(configured_url, "TEST_DATABASE_URL")


@pytest.fixture(scope="session")
def postgres_cluster() -> Iterator[PostgresCluster]:
    """One local PostgreSQL server shared by the database test session.

    A missing PostgreSQL installation raises an error so required regression
    suites fail instead of silently skipping database coverage.
    """

    server = PostgresCluster()
    server.start()
    yield server
    server.stop()


@pytest.fixture
def database(postgres_cluster: PostgresCluster) -> Iterator[DatabaseTarget]:
    """A migrated database that is dropped after each test."""

    test_database = postgres_cluster.create_database()
    yield test_database
    postgres_cluster.drop_database(test_database)


@pytest.fixture(scope="session")
def import_plan() -> ImportPlan:
    """Build the reviewed source plan once for every database regression test."""

    return build_import_plan()


@pytest.fixture(scope="session")
def published_catalog(
    postgres_cluster: PostgresCluster,
) -> Iterator[DatabaseTarget]:
    """A core-seeded catalog that read-only tests share without mutation.

    Readiness and API behavior depend only on the eight core tables, so ordinary
    fixtures seed them directly from the reviewed preview on the full (final)
    migration chain. The retired metadata tables are never written here.
    """

    test_database = postgres_cluster.create_database()
    seed_preview(test_database, build_preview())
    yield test_database
    postgres_cluster.drop_database(test_database)


@pytest.fixture(scope="session")
def legacy_published_catalog(
    postgres_cluster: PostgresCluster, import_plan: ImportPlan
) -> Iterator[DatabaseTarget]:
    """A real importer publication on the pre-removal migration ceiling.

    The retained import/provenance regression tests still exercise the metadata
    tables and source_row_id links, so they run against the legacy schema until
    those tables are removed in US2 and the tests are migrated in US4.
    """

    test_database = postgres_cluster.create_database(through=LEGACY_MIGRATION_CEILING)
    apply_plan(import_plan, test_database.importer_url)
    yield test_database
    postgres_cluster.drop_database(test_database)


@pytest.fixture
def repository(database: DatabaseTarget):
    """A started PostgreSQL repository bound to the read-only test role."""

    from app.repositories.postgres_catalog import PostgresCatalogRepository
    from app.settings import Settings

    settings = Settings(catalog_backend="postgres", database_url=database.reader_url)
    adapter = PostgresCatalogRepository(settings)
    adapter.startup()
    yield adapter
    adapter.close()


@pytest.fixture
def owner_connection(database: DatabaseTarget) -> Iterator[psycopg.Connection]:
    """Owner access for fixtures that must create catalog rows directly."""

    with psycopg.connect(database.owner_url) as connection:
        yield connection


@pytest.fixture
def importer_connection(database: DatabaseTarget) -> Iterator[psycopg.Connection]:
    """Privileged import access, separate from the runtime reader role."""

    with psycopg.connect(database.importer_url) as connection:
        yield connection


@pytest.fixture
def reader_connection(database: DatabaseTarget) -> Iterator[psycopg.Connection]:
    """Least-privilege runtime access used by the deployed API."""

    with psycopg.connect(database.reader_url) as connection:
        yield connection
