import pytest

from app.repositories.base import CatalogUnavailable
from app.repositories.postgres_catalog import PostgresCatalogRepository
from app.settings import Settings
from tests.postgres_support import DatabaseTarget, PostgresCluster

PUBLISHED_BATCH = """
insert into public.catalog_import_batches (
  source_checksum, repair_checksum, status, is_current, completed_at
) values (repeat('a', 64), repeat('b', 64), 'completed', true, now());
"""


@pytest.fixture(scope="module")
def cluster():
    server = PostgresCluster()
    server.start()
    yield server
    server.stop()


@pytest.fixture
def database(cluster: PostgresCluster):
    test_database = cluster.create_database()
    yield test_database
    cluster.drop_database(test_database)


@pytest.fixture
def repository(database: DatabaseTarget):
    settings = Settings(catalog_backend="postgres", database_url=database.url)
    adapter = PostgresCatalogRepository(settings)
    adapter.startup()
    yield adapter
    adapter.close()


def test_unpublished_database_is_unavailable(repository: PostgresCatalogRepository):
    with pytest.raises(CatalogUnavailable):
        repository.catalog()


def test_catalog_uses_source_order_and_full_titles(
    repository: PostgresCatalogRepository, database: DatabaseTarget
):
    database.execute(
        PUBLISHED_BATCH
        + """
        insert into public.degrees (name, faculty, full_title, source_order) values
          ('Second', 'School of Computing', 'Bachelor of Second', 1),
          ('First', 'School of Computing', 'Bachelor of First', 0);
        insert into public.partner_universities (name, country, source_order) values
          ('Later University', 'Japan', 1),
          ('Earlier University', 'Canada', 0);
        """
    )

    catalog = repository.catalog()
    assert [item.model_dump() for item in catalog.degrees] == [
        {"name": "First", "degree": "Bachelor of First"},
        {"name": "Second", "degree": "Bachelor of Second"},
    ]
    assert [item.model_dump() for item in catalog.universities] == [
        {"name": "Earlier University", "country": "Canada"},
        {"name": "Later University", "country": "Japan"},
    ]


def test_completed_batch_without_degrees_is_unavailable(
    repository: PostgresCatalogRepository, database: DatabaseTarget
):
    database.execute(PUBLISHED_BATCH)
    with pytest.raises(CatalogUnavailable):
        repository.catalog()


def test_degree_without_full_title_is_treated_as_incomplete(
    repository: PostgresCatalogRepository, database: DatabaseTarget
):
    database.execute(
        PUBLISHED_BATCH
        + """
        insert into public.degrees (name, faculty, full_title, source_order)
        values ('Test', 'School of Computing', null, 0);
        insert into public.partner_universities (name, country, source_order)
        values ('One University', 'Japan', 0);
        """
    )
    with pytest.raises(CatalogUnavailable):
        repository.catalog()
