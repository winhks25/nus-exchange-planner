from fastapi.testclient import TestClient

from app.main import create_app
from app.repositories.base import CATALOG_UNAVAILABLE_MESSAGE
from app.settings import PoolSettings, Settings
from scripts.postgres_validation import DatabaseTarget

APP_FIXTURE = """
insert into public.catalog_import_batches (
  source_checksum, repair_checksum, status, is_current, completed_at
) values (repeat('a', 64), repeat('b', 64), 'completed', true, now());
insert into public.nus_modules (code) values ('CS2102');
insert into public.degrees (name, faculty, full_title, source_order)
values ('Test', 'School of Computing', 'Bachelor of Test', 0);
insert into public.degree_modules (degree_id, module_code, requirement_type)
select d.id, 'CS2102', null from public.degrees d where d.name = 'Test';
insert into public.partner_universities (name, country, source_order)
values ('One University', 'Japan', 0);
insert into public.pu_modules (code, partner_university_id)
select 'P1', u.id from public.partner_universities u where u.name = 'One University';
insert into public.module_mappings (nus_module_code, pu_module_id)
select 'CS2102', pm.id from public.pu_modules pm
where pm.code = 'P1' and pm.partner_university_id = (
  select id from public.partner_universities where name = 'One University'
);
"""


def test_postgres_mode_serves_routes_from_the_repository(database: DatabaseTarget):
    database.execute(APP_FIXTURE)
    settings = Settings(catalog_backend="postgres", database_url=database.url)
    app = create_app(settings=settings)

    with TestClient(app) as client:
        assert client.get("/api/v1/catalog").json() == {
            "degrees": [{"name": "Test", "degree": "Bachelor of Test"}],
            "universities": [{"name": "One University", "country": "Japan"}],
        }
        recommendations = client.get(
            "/api/v1/recommendations", params={"degree": "Test"}
        )
        assert recommendations.status_code == 200
        assert recommendations.json()["recommendations"] == [
            {
                "university": "One University",
                "country": "Japan",
                "partner_module_count": 1,
                "distinct_nus_module_count": 1,
                "mapping_count": 1,
            }
        ]
        mappings = client.get(
            "/api/v1/mappings", params={"degree": "Test", "uni": "One University"}
        )
        assert mappings.status_code == 200
        assert mappings.json() == {
            "degree": "Test",
            "university": "One University",
            "partner_module_count": 1,
            "distinct_nus_module_count": 1,
            "mappings": [
                {
                    "nus_course": {"code": "CS2102", "units": 4},
                    "partner_course": {"code": "P1"},
                }
            ],
        }
        assert (
            client.get(
                "/api/v1/mappings", params={"degree": "Test", "uni": "Missing"}
            ).status_code
            == 404
        )


def test_database_outage_returns_503_without_json_fallback():
    settings = Settings(
        catalog_backend="postgres",
        database_url="postgresql://postgres@127.0.0.1:1/postgres",
        pool=PoolSettings(timeout=0.1, connect_timeout=1),
    )
    app = create_app(settings=settings)

    with TestClient(app) as client:
        for path in (
            "/api/v1/catalog",
            "/api/v1/recommendations?degree=Computer%20Science",
            "/api/v1/mappings?degree=Computer%20Science&uni=Kyoto%20University",
        ):
            response = client.get(path)
            assert response.status_code == 503
            assert response.json() == {"detail": CATALOG_UNAVAILABLE_MESSAGE}


def test_explicit_json_settings_ignore_database_environment(monkeypatch):
    monkeypatch.setenv("CATALOG_BACKEND", "postgres")
    monkeypatch.setenv("DATABASE_URL", "postgresql://postgres@127.0.0.1:1/postgres")

    with TestClient(create_app(settings=Settings(catalog_backend="json"))) as client:
        assert client.get("/api/v1/catalog").status_code == 200
