import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.catalog import CatalogUnavailable, load_catalog
from app.course_codes import extract_course_codes
from app.main import create_app
from app.matching import compare_rows, pair_mappings
from app.recommendations import rank_universities


def test_code_extraction_only_list_strings():
    data = {"CS2102": "CS9999", "prose": "CS8888", "nested": ["BT2102 or cs2102", {"deep": ["CS1231S", "badXCS2102", "BT2102"]}]}
    assert extract_course_codes(data) == {"BT2102", "CS2102", "CS1231S"}


def test_current_catalog_and_consistency():
    catalog = load_catalog()
    assert len(catalog.degrees) == 6
    assert len(catalog.universities) == 5
    for degree in catalog.degrees:
        rankings = rank_universities(catalog, degree.name)
        assert len(rankings) == 5
        assert rankings == sorted(rankings, key=lambda item: (-item.module_count, item.university))
        for item in rankings:
            pair = pair_mappings(catalog, degree.name, item.university)
            rows = compare_rows(catalog, degree.name, item.university)
            assert item.module_count == len({row.nus_course.code.upper() for row in rows})
            assert len(pair) == len(rows)
            assert [row.nus_course.code.upper() for row in rows] == sorted(row.nus_course.code.upper() for row in rows)
            assert all(row.nus_course.units == 4 for row in rows)
    assert any(item.module_count == 0 for item in rank_universities(catalog, "Computer Science"))


def test_api_status_and_optional_units():
    client = TestClient(create_app())
    assert client.get("/api/v1/catalog").status_code == 200
    assert client.get("/api/v1/recommendations", params={"degree": "missing"}).status_code == 404
    assert client.get("/api/v1/mappings", params={"degree": "Computer Science", "uni": "missing"}).status_code == 404
    rows = client.get("/api/v1/mappings", params={"degree": "Computer Science", "uni": "University of Toronto"}).json()["mappings"]
    assert rows and all(row["nus_course"]["units"] == 4 for row in rows)
    assert all(row["partner_course"]["units"] is not None for row in rows)


def test_missing_and_malformed_expected_file_fail_entire_catalog(tmp_path: Path):
    data = tmp_path / "data"
    (data / "majors").mkdir(parents=True)
    (data / "mapping" / "japan").mkdir(parents=True)
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({"files": ["majors/one.json", "mapping/japan/one.json"]}))
    (data / "majors" / "one.json").write_text('{"majors":[{"name":"Test","degree":"Full title","required":["CS2102"]}]}')
    with pytest.raises(CatalogUnavailable):
        load_catalog(data, manifest)
    (data / "mapping" / "japan" / "one.json").write_text("not json")
    with pytest.raises(CatalogUnavailable):
        load_catalog(data, manifest)
    assert TestClient(create_app(data, manifest)).get("/api/v1/catalog").status_code == 503


def test_duplicate_rows_and_stable_tie_order(tmp_path: Path):
    data = tmp_path / "data"
    (data / "majors").mkdir(parents=True)
    (data / "mapping" / "japan").mkdir(parents=True)
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({"files": ["majors/one.json", "mapping/japan/one.json"]}))
    (data / "majors" / "one.json").write_text('{"majors":[{"name":"Test","degree":"Full title","required":["CS2102"]}]}')
    rows = [
        {"nus_course": {"code": "CS2102"}, "partner_course": {"code": "SECOND"}},
        {"nus_course": {"code": "CS2102"}, "partner_course": {"code": "FIRST"}},
        {"nus_course": {"code": "Invalid"}, "partner_course": {"code": "BAD"}},
    ]
    (data / "mapping" / "japan" / "one.json").write_text(json.dumps({"partner_university": {"name": "One"}, "mapping_count": 99, "mappings": rows}))
    catalog = load_catalog(data, manifest)
    assert rank_universities(catalog, "Test")[0].module_count == 1
    assert [row.partner_course.code for row in compare_rows(catalog, "Test", "One")] == ["SECOND", "FIRST"]
    response = TestClient(create_app(data, manifest)).get("/api/v1/mappings", params={"degree": "Test", "uni": "One"})
    assert "units" not in response.json()["mappings"][0]["partner_course"]
