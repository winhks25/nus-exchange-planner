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
    data = {
        "CS2102": "CS9999",
        "prose": "CS8888",
        "nested": ["BT2102 or cs2102", {"deep": ["CS1231S", "badXCS2102", "BT2102"]}],
    }
    assert extract_course_codes(data) == {"BT2102", "CS2102", "CS1231S"}


def test_current_catalog_and_consistency():
    catalog = load_catalog()
    client = TestClient(create_app())
    assert len(catalog.degrees) == 6
    assert len(catalog.universities) == 5
    partner_order_differs = False
    for degree in catalog.degrees:
        rankings = rank_universities(catalog, degree.name)
        assert len(rankings) == 5
        assert rankings == sorted(
            rankings, key=lambda item: (-item.distinct_nus_module_count, item.university)
        )
        partner_order = sorted(
            rankings, key=lambda item: (-item.partner_module_count, item.university)
        )
        if [item.university for item in rankings] != [item.university for item in partner_order]:
            partner_order_differs = True
        recommendations_response = client.get(
            "/api/v1/recommendations", params={"degree": degree.name}
        )
        assert recommendations_response.status_code == 200
        assert recommendations_response.json()["recommendations"] == [
            item.model_dump() for item in rankings
        ]
        for item in rankings:
            pair = pair_mappings(catalog, degree.name, item.university)
            rows = compare_rows(catalog, degree.name, item.university)
            expected_partner = len({row.partner_course.code.upper() for row in pair})
            expected_nus = len({row.nus_course.code.upper() for row in pair})
            assert item.partner_module_count == expected_partner
            assert item.distinct_nus_module_count == expected_nus
            assert item.mapping_count == len(pair)
            assert set(item.model_dump()) == {
                "university",
                "country",
                "partner_module_count",
                "distinct_nus_module_count",
                "mapping_count",
            }
            response = client.get(
                "/api/v1/mappings", params={"degree": degree.name, "uni": item.university}
            )
            assert response.status_code == 200
            body = response.json()
            assert body["partner_module_count"] == expected_partner
            assert body["distinct_nus_module_count"] == expected_nus
            assert len(body["mappings"]) == len(pair)
            assert len(pair) == len(rows)
            assert [row.nus_course.code.upper() for row in rows] == sorted(
                row.nus_course.code.upper() for row in rows
            )
            assert all(row.nus_course.units == 4 for row in rows)
    assert any(
        (item.partner_module_count, item.distinct_nus_module_count, item.mapping_count) == (0, 0, 0)
        for item in rank_universities(catalog, "Computer Science")
    )
    assert partner_order_differs, "expected a degree whose NUS and partner rank orders differ"

    toronto = client.get(
        "/api/v1/mappings",
        params={"degree": "Artificial Intelligence", "uni": "University of Toronto"},
    ).json()
    assert (
        toronto["partner_module_count"],
        toronto["distinct_nus_module_count"],
        len(toronto["mappings"]),
    ) == (9, 6, 9)
    western = client.get(
        "/api/v1/mappings",
        params={"degree": "Business Analytics", "uni": "University of Western Australia, The"},
    ).json()
    assert western["partner_module_count"] == 19
    assert len(western["mappings"]) == 22
    assert len({row["partner_course"]["code"].upper() for row in western["mappings"]}) == 19


def test_api_status_and_optional_units():
    client = TestClient(create_app())
    assert client.get("/api/v1/catalog").status_code == 200
    assert client.get("/api/v1/recommendations", params={"degree": "missing"}).status_code == 404
    assert (
        client.get(
            "/api/v1/mappings", params={"degree": "Computer Science", "uni": "missing"}
        ).status_code
        == 404
    )
    rows = client.get(
        "/api/v1/mappings", params={"degree": "Computer Science", "uni": "University of Toronto"}
    ).json()["mappings"]
    assert rows and all(row["nus_course"]["units"] == 4 for row in rows)
    assert all(row["partner_course"]["units"] is not None for row in rows)


def test_missing_and_malformed_expected_file_fail_entire_catalog(tmp_path: Path):
    data = tmp_path / "data"
    (data / "majors").mkdir(parents=True)
    (data / "mapping" / "japan").mkdir(parents=True)
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({"files": ["majors/one.json", "mapping/japan/one.json"]}))
    (data / "majors" / "one.json").write_text(
        '{"majors":[{"name":"Test","degree":"Full title","required":["CS2102"]}]}'
    )
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
    (data / "majors" / "one.json").write_text(
        '{"majors":[{"name":"Test","degree":"Full title","required":["CS2102"]}]}'
    )
    rows = [
        {"nus_course": {"code": "CS2102"}, "partner_course": {"code": "SECOND"}},
        {"nus_course": {"code": "CS2102"}, "partner_course": {"code": "FIRST"}},
        {"nus_course": {"code": "Invalid"}, "partner_course": {"code": "BAD"}},
    ]
    (data / "mapping" / "japan" / "one.json").write_text(
        json.dumps({"partner_university": {"name": "One"}, "mapping_count": 99, "mappings": rows})
    )
    catalog = load_catalog(data, manifest)
    recommendation = rank_universities(catalog, "Test")[0]
    assert (
        recommendation.partner_module_count,
        recommendation.distinct_nus_module_count,
        recommendation.mapping_count,
    ) == (2, 1, 2)
    assert [row.partner_course.code for row in compare_rows(catalog, "Test", "One")] == [
        "SECOND",
        "FIRST",
    ]
    response = TestClient(create_app(data, manifest)).get(
        "/api/v1/mappings", params={"degree": "Test", "uni": "One"}
    )
    assert "units" not in response.json()["mappings"][0]["partner_course"]


def test_partner_code_deduplication_ties_and_zero_pairs(tmp_path: Path):
    data = tmp_path / "data"
    (data / "majors").mkdir(parents=True)
    (data / "mapping" / "japan").mkdir(parents=True)
    manifest = tmp_path / "manifest.json"
    files = ["majors/one.json"] + [f"mapping/japan/{name}.json" for name in ("a", "b", "c", "z")]
    manifest.write_text(json.dumps({"files": files}))
    (data / "majors" / "one.json").write_text(
        json.dumps({"majors": [{"name": "Test", "degree": "Full title", "required": ["CS2102"]}]})
    )
    for name, partner_codes in (
        ("A", ["same", "SAME"]),
        ("B", ["OTHER"]),
        ("C", ["ONE", "TWO"]),
        ("Z", []),
    ):
        rows = [
            {"nus_course": {"code": "CS2102"}, "partner_course": {"code": code}}
            for code in partner_codes
        ]
        (data / "mapping" / "japan" / f"{name.lower()}.json").write_text(
            json.dumps(
                {"partner_university": {"name": name}, "mapping_count": 999, "mappings": rows}
            )
        )
    catalog = load_catalog(data, manifest)
    ranked = rank_universities(catalog, "Test")
    assert [item.university for item in ranked] == ["A", "B", "C", "Z"]
    assert [
        (item.partner_module_count, item.distinct_nus_module_count, item.mapping_count)
        for item in ranked
    ] == [(1, 1, 2), (1, 1, 1), (2, 1, 2), (0, 0, 0)]
    client = TestClient(create_app(data, manifest))
    assert client.get("/api/v1/mappings", params={"degree": "Test", "uni": "Z"}).json() == {
        "degree": "Test",
        "university": "Z",
        "partner_module_count": 0,
        "distinct_nus_module_count": 0,
        "mappings": [],
    }


def test_nus_ranking_opposes_partner_count_and_dedupes_duplicate_rows(tmp_path: Path):
    data = tmp_path / "data"
    (data / "majors").mkdir(parents=True)
    (data / "mapping" / "japan").mkdir(parents=True)
    manifest = tmp_path / "manifest.json"
    files = ["majors/one.json"] + [f"mapping/japan/{name}.json" for name in ("a", "b", "c", "z")]
    manifest.write_text(json.dumps({"files": files}))
    (data / "majors" / "one.json").write_text(
        json.dumps(
            {
                "majors": [
                    {
                        "name": "Test",
                        "degree": "Full title",
                        "required": ["CS2102", "CS2103", "CS2104", "CS2105"],
                    }
                ]
            }
        )
    )
    rows_by_partner = {
        "A": [("CS2102", "P1"), ("CS2102", "P2"), ("CS2102", "P3")],
        "B": [("CS2103", "Q1"), ("CS2103", "Q2"), ("CS2104", "Q3")],
        "C": [("CS2103", "R1"), ("CS2105", "R2")],
        "Z": [],
    }
    for name, pairs in rows_by_partner.items():
        rows = [
            {"nus_course": {"code": nus}, "partner_course": {"code": partner}}
            for nus, partner in pairs
        ]
        (data / "mapping" / "japan" / f"{name.lower()}.json").write_text(
            json.dumps(
                {"partner_university": {"name": name}, "mapping_count": 999, "mappings": rows}
            )
        )
    catalog = load_catalog(data, manifest)
    ranked = rank_universities(catalog, "Test")
    assert [item.university for item in ranked] == ["B", "C", "A", "Z"]
    assert [
        (item.partner_module_count, item.distinct_nus_module_count, item.mapping_count)
        for item in ranked
    ] == [(3, 2, 3), (2, 2, 2), (3, 1, 3), (0, 0, 0)]
    partner_order = sorted(ranked, key=lambda item: (-item.partner_module_count, item.university))
    assert [item.university for item in partner_order] == ["A", "B", "C", "Z"]
