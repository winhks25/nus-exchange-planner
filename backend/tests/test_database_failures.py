"""Failure, timeout, cleanup and rollback coverage for the database runtime."""

import time

import psycopg
import pytest
from fastapi.testclient import TestClient

import app.main as main_module
from app.database import CatalogDatabase, DatabaseConfigurationError
from app.main import create_app
from app.settings import PoolSettings, Settings, SettingsError
from scripts.postgres_validation import (
    READER_ROLE,
    DatabaseTarget,
)

pytestmark = pytest.mark.regression

UNAVAILABLE = "Catalog data is unavailable. Please try again later."


def _settings(url: str, **pool: object) -> Settings:
    """Build postgres settings with test-friendly bounded defaults."""

    values = {"timeout": 1.0, "connect_timeout": 1, **pool}
    return Settings(
        catalog_backend="postgres",
        database_url=url,
        pool=PoolSettings(**values),
    )


def _wait_for_status(
    client: TestClient, path: str, status: int, timeout: float = 10.0
):
    """Poll until a recoverable outage clears, failing with the last response."""

    deadline = time.monotonic() + timeout
    last = None
    while time.monotonic() < deadline:
        last = client.get(path)
        if last.status_code == status:
            return last
        time.sleep(0.1)
    assert last is not None
    return last


def _reader_sessions(database: DatabaseTarget) -> int:
    """Count live server sessions owned by the runtime role for this database."""

    with psycopg.connect(database.owner_url) as connection:
        return int(
            connection.execute(
                """
                select count(*)
                from pg_stat_activity
                where datname = %s and usename = %s
                """,
                (database.name, READER_ROLE),
            ).fetchone()[0]
        )


def test_configuration_failures_are_explicit_and_never_echo_secrets() -> None:
    with pytest.raises(SettingsError, match="DATABASE_URL is required"):
        Settings.from_env({"CATALOG_BACKEND": "postgres"})

    with pytest.raises(SettingsError, match="unknown value"):
        Settings.from_env({"CATALOG_BACKEND": "sqlite"})

    with pytest.raises(SettingsError) as invalid_scheme:
        Settings.from_env(
            {
                "CATALOG_BACKEND": "postgres",
                "DATABASE_URL": "mysql://user:topsecret@example.com/catalog",
            }
        )
    assert "topsecret" not in str(invalid_scheme.value)

    with pytest.raises(SettingsError) as invalid_pool:
        Settings.from_env(
            {
                "DATABASE_URL": "postgresql://user:topsecret@example.com/catalog",
                "DB_POOL_MAX_SIZE": "many",
            }
        )
    assert "topsecret" not in str(invalid_pool.value)

    with pytest.raises(DatabaseConfigurationError):
        CatalogDatabase(Settings(catalog_backend="postgres"))


def test_unready_core_catalog_returns_503_without_json_fallback(
    database: DatabaseTarget, monkeypatch: pytest.MonkeyPatch
) -> None:
    def forbidden_json(*args, **kwargs):
        raise AssertionError("database failures must never construct the JSON adapter")

    monkeypatch.setattr(main_module, "JsonCatalogRepository", forbidden_json)
    settings = _settings(database.reader_url)

    with TestClient(create_app(settings=settings)) as client:
        for path, params in [
            ("/api/v1/catalog", None),
            ("/api/v1/recommendations", {"degree": "Computer Science"}),
            (
                "/api/v1/mappings",
                {"degree": "Computer Science", "uni": "University of Toronto"},
            ),
        ]:
            response = client.get(path, params=params)
            assert response.status_code == 503
            assert response.json() == {"detail": UNAVAILABLE}
            assert database.reader_url not in response.text
            assert "postgresql://" not in response.text


def test_denied_required_table_read_returns_sanitized_503(
    database: DatabaseTarget, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A role without core-table SELECT must fail closed, never fall back."""

    role = "catalog_denied_reader"
    password = "catalog-denied-local"

    # Create a disposable login role with no core-table SELECT privilege.
    with psycopg.connect(database.owner_url, autocommit=True) as connection:
        connection.execute(f"drop role if exists {role}")
        connection.execute(f"create role {role} login password '{password}'")

    try:
        url = (
            f"postgresql://{role}:{password}"
            f"@127.0.0.1:{database.cluster.port}/{database.name}"
        )

        # Any attempt to build the JSON adapter fails the test.
        def forbidden_json(*args, **kwargs):
            raise AssertionError("denied reads must never construct the JSON adapter")

        monkeypatch.setattr(main_module, "JsonCatalogRepository", forbidden_json)

        with TestClient(create_app(settings=_settings(url))) as client:
            response = client.get("/api/v1/catalog")
            assert response.status_code == 503
            assert response.json() == {"detail": UNAVAILABLE}
            assert "postgresql://" not in response.text
            assert "permission denied" not in response.text.lower()
    finally:
        with psycopg.connect(database.owner_url, autocommit=True) as connection:
            connection.execute(f"drop role if exists {role}")


# Each fragment seeds a core catalog that fails exactly one readiness condition.
UNREADY_CORE_FRAGMENTS = {
    "empty-degrees": """
        insert into public.partner_universities (name, country, source_order)
        values ('One University', 'Japan', 0);
    """,
    "empty-universities": """
        insert into public.degrees (name, faculty, full_title, source_order)
        values ('Test', 'School of Computing', 'Bachelor of Test', 0);
    """,
    "null-full-title": """
        insert into public.degrees (name, faculty, full_title, source_order)
        values ('Test', 'School of Computing', null, 0);
        insert into public.partner_universities (name, country, source_order)
        values ('One University', 'Japan', 0);
    """,
}


@pytest.mark.parametrize("fragment", sorted(UNREADY_CORE_FRAGMENTS))
def test_each_unready_core_condition_returns_sanitized_503(
    database: DatabaseTarget, monkeypatch: pytest.MonkeyPatch, fragment: str
) -> None:
    def forbidden_json(*args, **kwargs):
        raise AssertionError("an unready core catalog must never build the JSON adapter")

    monkeypatch.setattr(main_module, "JsonCatalogRepository", forbidden_json)
    database.execute(UNREADY_CORE_FRAGMENTS[fragment])

    with TestClient(create_app(settings=_settings(database.reader_url))) as client:
        response = client.get("/api/v1/catalog")
        assert response.status_code == 503
        assert response.json() == {"detail": UNAVAILABLE}
        # The sanitized error must not leak the connection string or SQL.
        assert database.reader_url not in response.text
        assert "postgresql://" not in response.text
        assert "select" not in response.text.lower()


def test_unknown_selections_and_missing_parameters(
    published_catalog: DatabaseTarget,
) -> None:
    with TestClient(create_app(settings=_settings(published_catalog.reader_url))) as client:
        assert client.get("/api/v1/recommendations").status_code == 422
        assert client.get("/api/v1/mappings", params={"degree": "Computer Science"}).status_code == 422

        unknown_degree = client.get(
            "/api/v1/recommendations", params={"degree": "Missing Degree"}
        )
        assert unknown_degree.status_code == 404
        assert unknown_degree.json() == {"detail": "Unknown degree"}

        unknown_university = client.get(
            "/api/v1/mappings",
            params={"degree": "Computer Science", "uni": "Missing University"},
        )
        assert unknown_university.status_code == 404
        assert unknown_university.json() == {"detail": "Unknown degree or university"}

        empty = client.get(
            "/api/v1/mappings",
            params={
                "degree": "Computer Science",
                "uni": "University of Western Australia",
            },
        )
        assert empty.status_code == 200
        assert empty.json()["mappings"] == []
        assert empty.json()["distinct_nus_module_count"] == 0
        assert empty.json()["partner_module_count"] == 0


def test_statement_timeout_returns_503_then_recovers(
    published_catalog: DatabaseTarget,
) -> None:
    settings = _settings(published_catalog.reader_url, statement_timeout_ms=100)

    with TestClient(create_app(settings=settings)) as client:
        assert client.get("/api/v1/catalog").status_code == 200

        # Block catalog tables so the next request hits the statement timeout.
        with psycopg.connect(published_catalog.owner_url) as blocker, blocker.transaction():
            blocker.execute(
                "lock table public.degrees, public.partner_universities "
                "in access exclusive mode"
            )
            started = time.monotonic()
            response = client.get("/api/v1/catalog")
            elapsed = time.monotonic() - started

        assert response.status_code == 503
        assert response.json() == {"detail": UNAVAILABLE}
        assert elapsed < 5

        recovered = _wait_for_status(client, "/api/v1/catalog", 200)
        assert recovered.status_code == 200


def test_single_connection_pool_bounds_concurrency_and_releases_afterwards(
    published_catalog: DatabaseTarget,
) -> None:
    settings = _settings(
        published_catalog.reader_url,
        max_size=1,
        max_waiting=1,
        timeout=0.2,
    )

    with TestClient(create_app(settings=settings)) as client:
        repository = client.app.state.repository
        assert client.get("/api/v1/catalog").status_code == 200

        # Hold the only pooled connection; a second request must fail fast with 503.
        with repository._database.read_transaction("hold"):
            response = client.get("/api/v1/catalog")

        assert response.status_code == 503
        assert response.json() == {"detail": UNAVAILABLE}

        # The timed-out request must not poison the pool.
        assert client.get("/api/v1/catalog").status_code == 200

    assert _reader_sessions(published_catalog) == 0


def test_paused_server_returns_503_and_recovers(
    published_catalog: DatabaseTarget,
) -> None:
    settings = _settings(published_catalog.reader_url)
    cluster = published_catalog.cluster

    with TestClient(create_app(settings=settings)) as client:
        assert client.get("/api/v1/catalog").status_code == 200

        try:
            cluster.pause()
            unavailable = client.get("/api/v1/catalog")
            assert unavailable.status_code == 503
            assert unavailable.json() == {"detail": UNAVAILABLE}
            assert "postgresql://" not in unavailable.text
        finally:
            cluster.resume()

        recovered = _wait_for_status(client, "/api/v1/catalog", 200)
        assert recovered.status_code == 200


def test_shutdown_closes_every_pooled_connection(
    published_catalog: DatabaseTarget,
) -> None:
    settings = _settings(published_catalog.reader_url)

    with TestClient(create_app(settings=settings)) as client:
        assert client.get("/api/v1/catalog").status_code == 200
        assert _reader_sessions(published_catalog) == 1

    deadline = time.monotonic() + 5
    while _reader_sessions(published_catalog) and time.monotonic() < deadline:
        time.sleep(0.05)
    assert _reader_sessions(published_catalog) == 0


def test_manual_json_rollback_serves_the_frozen_catalog_without_database() -> None:
    settings = Settings.from_env(
        {
            "CATALOG_BACKEND": "json",
            "DATABASE_URL": "postgresql://unused.invalid/catalog",
        }
    )
    with TestClient(create_app(settings=settings)) as client:
        assert client.get("/api/v1/catalog").status_code == 200
        assert (
            client.get(
                "/api/v1/recommendations", params={"degree": "Computer Science"}
            ).status_code
            == 200
        )
        assert (
            client.get(
                "/api/v1/mappings",
                params={"degree": "Computer Science", "uni": "University of Toronto"},
            ).status_code
            == 200
        )


def test_reader_role_cannot_write_or_read_protected_archives(
    published_catalog: DatabaseTarget,
) -> None:
    with psycopg.connect(published_catalog.reader_url) as connection:
        with pytest.raises(psycopg.errors.ReadOnlySqlTransaction):
            connection.execute(
                "insert into public.degrees (name, faculty, full_title, source_order) "
                "values ('Test', 'Faculty', 'Title', 99)"
            )
        connection.rollback()

        for table in (
            "catalog_import_batches",
            "catalog_source_snapshots",
            "catalog_source_rows",
            "catalog_issues",
            "catalog_repairs",
        ):
            with pytest.raises(psycopg.errors.UndefinedTable):
                connection.execute(f"select count(*) from public.{table}")
            connection.rollback()
