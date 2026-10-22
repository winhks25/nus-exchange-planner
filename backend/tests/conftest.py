import pytest

from scripts.postgres_validation import DatabaseTarget, PostgresCluster


@pytest.fixture(scope="session")
def postgres_cluster():
    """One local PostgreSQL server shared by the database test session."""

    server = PostgresCluster()
    server.start()
    yield server
    server.stop()


@pytest.fixture
def database(postgres_cluster: PostgresCluster):
    """A migrated database that is dropped after each test."""

    test_database = postgres_cluster.create_database()
    yield test_database
    postgres_cluster.drop_database(test_database)


@pytest.fixture
def repository(database: DatabaseTarget):
    """A started PostgreSQL repository bound to the test database."""

    from app.repositories.postgres_catalog import PostgresCatalogRepository
    from app.settings import Settings

    settings = Settings(catalog_backend="postgres", database_url=database.url)
    adapter = PostgresCatalogRepository(settings)
    adapter.startup()
    yield adapter
    adapter.close()
