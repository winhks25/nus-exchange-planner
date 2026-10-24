"""Parity regression tests for the JSON and PostgreSQL catalog adapters."""

import json
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.repositories.json_catalog import JsonCatalogRepository
from app.repositories.postgres_catalog import PostgresCatalogRepository
from app.settings import PoolSettings, Settings
from scripts.catalog_preview import build_preview
from scripts.postgres_validation import DatabaseTarget
from scripts.verify_catalog import ExpectedCatalog

pytestmark = pytest.mark.regression

BASELINE_PATH = (
    Path(__file__).resolve().parents[2]
    / "plan"
    / "supabase-migration"
    / "baseline-responses.json"
)

# These four degree/university pairs change only because of reviewed repairs.
# Values are (mapping_count, distinct_nus_module_count, partner_module_count).
REVIEWED_PAIR_COUNTS = {
    ("Artificial Intelligence", "University of Toronto"): (10, 6, 10),
    ("Business Analytics", "University of Toronto"): (19, 9, 19),
    ("Computer Science", "University of Toronto"): (7, 3, 7),
    ("Information Security", "University of Toronto"): (8, 5, 8),
}

EMPTY_PAIRS = {
    ("Artificial Intelligence", "University of Western Australia"),
    ("Computer Science", "University of Western Australia"),
    ("Computer Science", "Yonsei University"),
}


@pytest.fixture(scope="session")
def baseline() -> dict[str, Any]:
    """Load the frozen response snapshot captured before the migration."""

    return json.loads(BASELINE_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def expected_catalog() -> ExpectedCatalog:
    """Build expected responses from source data and reviewed repairs, not SQL."""

    return ExpectedCatalog(build_preview())


@pytest.fixture(scope="session")
def json_client() -> TestClient:
    """Serve the frozen JSON catalog through the public API."""

    with TestClient(create_app(settings=Settings(catalog_backend="json"))) as client:
        yield client


@pytest.fixture(scope="session")
def postgres_client(published_catalog: DatabaseTarget) -> TestClient:
    """Serve a real importer publication through the read-only runtime role."""

    settings = Settings(
        catalog_backend="postgres",
        database_url=published_catalog.reader_url,
        pool=PoolSettings(timeout=2),
    )
    with TestClient(create_app(settings=settings)) as client:
        yield client


def _pair_key(degree: str, university: str) -> str:
    """Match the frozen baseline's mapping key format."""

    return f"{degree} || {university}"


def _counts(body: dict[str, Any]) -> tuple[int, int, int]:
    """Return mapping, distinct NUS, and partner counts from one response."""

    return (
        len(body["mappings"]),
        body["distinct_nus_module_count"],
        body["partner_module_count"],
    )


def test_catalog_responses_match_source_order_and_frozen_baseline(
    baseline: dict[str, Any],
    expected_catalog: ExpectedCatalog,
    json_client: TestClient,
    postgres_client: TestClient,
) -> None:
    json_catalog = json_client.get("/api/v1/catalog").json()
    postgres_catalog = postgres_client.get("/api/v1/catalog").json()

    assert json_catalog == baseline["catalog"]["body"]
    assert postgres_catalog == expected_catalog.catalog()
    assert postgres_catalog == json_catalog


def test_all_six_recommendations_match_baseline_except_reviewed_deltas(
    baseline: dict[str, Any],
    expected_catalog: ExpectedCatalog,
    json_client: TestClient,
    postgres_client: TestClient,
) -> None:
    actual_changed: set[tuple[str, str]] = set()

    for degree in [item["name"] for item in expected_catalog.degrees]:
        baseline_body = baseline["recommendations"][degree]["body"]
        json_body = json_client.get(
            "/api/v1/recommendations", params={"degree": degree}
        ).json()
        postgres_body = postgres_client.get(
            "/api/v1/recommendations", params={"degree": degree}
        ).json()

        assert json_body == baseline_body
        assert postgres_body == expected_catalog.recommendations(degree)
        assert [item["university"] for item in postgres_body["recommendations"]] == [
            item["university"] for item in baseline_body["recommendations"]
        ]

        # Compare every ranking row; only the reviewed pairs may differ.
        baseline_rows = {
            item["university"]: item for item in baseline_body["recommendations"]
        }
        for item in postgres_body["recommendations"]:
            key = (degree, item["university"])
            if key in REVIEWED_PAIR_COUNTS:
                actual_changed.add(key)
                assert (
                    item["mapping_count"],
                    item["distinct_nus_module_count"],
                    item["partner_module_count"],
                ) == REVIEWED_PAIR_COUNTS[key]
            else:
                assert item == baseline_rows[item["university"]]

    assert actual_changed == set(REVIEWED_PAIR_COUNTS)


def test_all_thirty_mapping_pairs_match_baseline_except_reviewed_deltas(
    baseline: dict[str, Any],
    expected_catalog: ExpectedCatalog,
    json_client: TestClient,
    postgres_client: TestClient,
) -> None:
    actual_changed: set[tuple[str, str]] = set()
    repeated_pairs: set[tuple[str, str]] = set()
    empty_pairs: set[tuple[str, str]] = set()

    for degree in [item["name"] for item in expected_catalog.degrees]:
        for university in [item["name"] for item in expected_catalog.universities]:
            key = (degree, university)
            baseline_body = baseline["mappings"][_pair_key(degree, university)]["body"]
            json_body = json_client.get(
                "/api/v1/mappings", params={"degree": degree, "uni": university}
            ).json()
            postgres_body = postgres_client.get(
                "/api/v1/mappings", params={"degree": degree, "uni": university}
            ).json()

            assert json_body == baseline_body
            assert postgres_body["degree"] == degree
            assert postgres_body["university"] == university

            rows = postgres_body["mappings"]
            assert postgres_body["distinct_nus_module_count"] == len(
                {row["nus_course"]["code"].upper() for row in rows}
            )
            assert postgres_body["partner_module_count"] == len(
                {row["partner_course"]["code"].upper() for row in rows}
            )
            assert all(row["nus_course"]["units"] == 4 for row in rows)

            if not rows:
                empty_pairs.add(key)
                assert postgres_body["distinct_nus_module_count"] == 0
                assert postgres_body["partner_module_count"] == 0
                assert postgres_body == baseline_body
            if len(rows) != len({row["nus_course"]["code"] for row in rows}):
                repeated_pairs.add(key)

            if key in REVIEWED_PAIR_COUNTS:
                actual_changed.add(key)
                assert _counts(postgres_body) == (
                    REVIEWED_PAIR_COUNTS[key][0],
                    REVIEWED_PAIR_COUNTS[key][1],
                    REVIEWED_PAIR_COUNTS[key][2],
                )
                assert postgres_body == expected_catalog.mappings(degree, university)
            else:
                assert postgres_body == baseline_body

    assert actual_changed == set(REVIEWED_PAIR_COUNTS)
    assert empty_pairs == EMPTY_PAIRS
    assert repeated_pairs
    assert sum(
        1
        for degree in [item["name"] for item in expected_catalog.degrees]
        for university in [item["name"] for item in expected_catalog.universities]
    ) == 30


def _write_synthetic_json(root: Path) -> Path:
    """Write one small catalog that exercises ties, repeats, nulls and empties."""

    (root / "majors").mkdir(parents=True)
    (root / "mapping" / "japan").mkdir(parents=True)
    manifest = root / "manifest.json"
    files = [
        "majors/one.json",
        "mapping/japan/alpha University.json",
        "mapping/japan/Zeta University.json",
        "mapping/japan/beta University.json",
        "mapping/japan/gamma University.json",
    ]
    manifest.write_text(json.dumps({"files": files}), encoding="utf-8")
    (root / "majors" / "one.json").write_text(
        json.dumps(
            {
                "majors": [
                    {
                        "name": "Test",
                        "degree": "Bachelor of Test",
                        "required": ["CS2102", "CS2103", "CS2104", "CS2105"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    def write_mapping(name: str, rows: list[dict[str, Any]]) -> None:
        (root / "mapping" / "japan" / f"{name}.json").write_text(
            json.dumps({"partner_university": {"name": name}, "mappings": rows}),
            encoding="utf-8",
        )

    write_mapping(
        "alpha University",
        [
            {
                "nus_course": {"code": "CS2102", "title": "Alpha Data"},
                "partner_course": {"code": "P3", "title": "Partner Three"},
            },
            {
                "nus_course": {"code": "CS2102"},
                "partner_course": {"code": "P1", "units": 3.0},
            },
            {
                "nus_course": {"code": "CS2103"},
                "partner_course": {"code": "P2", "title": "Partner Two"},
            },
            {"nus_course": {"code": "CS2105"}, "partner_course": {"code": "P2"}},
        ],
    )
    write_mapping(
        "Zeta University",
        [{"nus_course": {"code": "CS2104"}, "partner_course": {"code": "Z1"}}],
    )
    write_mapping(
        "beta University",
        [{"nus_course": {"code": "CS2104"}, "partner_course": {"code": "B1"}}],
    )
    write_mapping("gamma University", [])
    return manifest


SYNTHETIC_FIXTURE = """
insert into public.nus_modules (code) values
  ('CS2102'), ('CS2103'), ('CS2104'), ('CS2105');
insert into public.degrees (name, faculty, full_title, source_order)
values ('Test', 'School of Computing', 'Bachelor of Test', 0);
insert into public.degree_modules (degree_id, module_code, requirement_type)
select d.id, modules.code, null
from public.degrees d
cross join (values ('CS2102'), ('CS2103'), ('CS2104'), ('CS2105')) modules(code)
where d.name = 'Test';
insert into public.partner_universities (name, country, source_order) values
  ('alpha University', 'Japan', 0),
  ('Zeta University', 'Japan', 1),
  ('beta University', 'Japan', 2),
  ('gamma University', 'Japan', 3);
insert into public.pu_modules (code, partner_university_id)
select pairs.code, u.id
from (
  values
    ('alpha University', 'P1'),
    ('alpha University', 'P2'),
    ('alpha University', 'P3'),
    ('Zeta University', 'Z1'),
    ('beta University', 'B1')
) pairs(university, code)
join public.partner_universities u on u.name = pairs.university;
insert into public.module_mappings (
  nus_module_code, pu_module_id, source_order,
  source_nus_title, source_partner_title, source_partner_units
)
select
  pairs.nus_code, pm.id, pairs.source_order,
  pairs.nus_title, pairs.partner_title, pairs.partner_units
from (
  values
    ('alpha University', 'P3', 'CS2102', 0, 'Alpha Data', 'Partner Three', null),
    ('alpha University', 'P1', 'CS2102', 1, null, null, 3.0),
    ('alpha University', 'P2', 'CS2103', 2, null, 'Partner Two', null),
    ('alpha University', 'P2', 'CS2105', 3, null, null, null),
    ('Zeta University', 'Z1', 'CS2104', 0, null, null, null),
    ('beta University', 'B1', 'CS2104', 0, null, null, null)
) pairs(university, partner_code, nus_code, source_order, nus_title, partner_title, partner_units)
join public.partner_universities u on u.name = pairs.university
join public.pu_modules pm
  on pm.partner_university_id = u.id and pm.code = pairs.partner_code;
"""


def test_synthetic_adapters_agree_on_ties_repeats_nulls_and_units(
    tmp_path: Path, database: DatabaseTarget, repository: PostgresCatalogRepository
) -> None:
    manifest = _write_synthetic_json(tmp_path)
    database.execute(SYNTHETIC_FIXTURE)
    json_repository = JsonCatalogRepository(tmp_path, manifest)

    expected_catalog = {
        "degrees": [{"name": "Test", "degree": "Bachelor of Test"}],
        "universities": [
            {"name": "alpha University", "country": "Japan"},
            {"name": "Zeta University", "country": "Japan"},
            {"name": "beta University", "country": "Japan"},
            {"name": "gamma University", "country": "Japan"},
        ],
    }
    expected_recommendations = [
        {
            "university": "alpha University",
            "country": "Japan",
            "partner_module_count": 3,
            "distinct_nus_module_count": 3,
            "mapping_count": 4,
        },
        {
            "university": "Zeta University",
            "country": "Japan",
            "partner_module_count": 1,
            "distinct_nus_module_count": 1,
            "mapping_count": 1,
        },
        {
            "university": "beta University",
            "country": "Japan",
            "partner_module_count": 1,
            "distinct_nus_module_count": 1,
            "mapping_count": 1,
        },
        {
            "university": "gamma University",
            "country": "Japan",
            "partner_module_count": 0,
            "distinct_nus_module_count": 0,
            "mapping_count": 0,
        },
    ]
    expected_rows = [
        {
            "nus_course": {"code": "CS2102", "title": "Alpha Data", "units": 4.0},
            "partner_course": {
                "code": "P3",
                "title": "Partner Three",
                "units": None,
            },
        },
        {
            "nus_course": {"code": "CS2102", "title": None, "units": 4.0},
            "partner_course": {"code": "P1", "title": None, "units": 3.0},
        },
        {
            "nus_course": {"code": "CS2103", "title": None, "units": 4.0},
            "partner_course": {"code": "P2", "title": "Partner Two", "units": None},
        },
        {
            "nus_course": {"code": "CS2105", "title": None, "units": 4.0},
            "partner_course": {"code": "P2", "title": None, "units": None},
        },
    ]

    assert json_repository.catalog().model_dump() == expected_catalog
    assert repository.catalog().model_dump() == expected_catalog
    assert json_repository.recommendations("Test").model_dump()["recommendations"] == (
        expected_recommendations
    )
    assert repository.recommendations("Test").model_dump()["recommendations"] == (
        expected_recommendations
    )

    json_mappings = json_repository.mappings("Test", "alpha University").model_dump()
    postgres_mappings = repository.mappings("Test", "alpha University").model_dump()
    assert json_mappings == postgres_mappings
    assert json_mappings["mappings"] == expected_rows
    assert json_mappings["partner_module_count"] == 3
    assert json_mappings["distinct_nus_module_count"] == 3

    # Valid empty pairs return zero counts rather than an error.
    for adapter in (json_repository, repository):
        empty = adapter.mappings("Test", "gamma University").model_dump()
        assert empty["mappings"] == []
        assert empty["partner_module_count"] == 0
        assert empty["distinct_nus_module_count"] == 0
