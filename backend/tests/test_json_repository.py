import json
from pathlib import Path

import pytest

from app.repositories.base import CatalogUnavailable, UnknownSelection
from app.repositories.json_catalog import JsonCatalogRepository


@pytest.fixture
def repository(tmp_path: Path) -> JsonCatalogRepository:
    data = tmp_path / "data"
    (data / "majors").mkdir(parents=True)
    (data / "mapping" / "japan").mkdir(parents=True)
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps({"files": ["majors/one.json", "mapping/japan/one.json"]})
    )
    (data / "majors" / "one.json").write_text(
        json.dumps(
            {
                "majors": [
                    {"name": "Test", "degree": "Full title", "required": ["CS2102"]}
                ]
            }
        )
    )
    rows = [
        {"nus_course": {"code": "CS2102", "title": "Data"}, "partner_course": {"code": "SECOND"}},
        {"nus_course": {"code": "CS2102"}, "partner_course": {"code": "FIRST", "units": 3}},
        {"nus_course": {"code": "Invalid"}, "partner_course": {"code": "BAD"}},
    ]
    (data / "mapping" / "japan" / "one.json").write_text(
        json.dumps({"partner_university": {"name": "One"}, "mappings": rows})
    )
    return JsonCatalogRepository(data, manifest)


def test_catalog_and_rankings_preserve_legacy_semantics(repository: JsonCatalogRepository):
    assert repository.catalog().model_dump() == {
        "faculties": [],
        "degrees": [{"name": "Test", "degree": "Full title", "faculty_ids": []}],
        "universities": [
            {
                "id": None,
                "name": "One",
                "country": "Japan",
                "city": None,
                "continent": None,
                "faculty_ids": [],
                "image": None,
                "website": None,
                "image_attribution": None,
            }
        ],
    }

    ranked = repository.recommendations("Test").recommendations
    assert [
        (item.university, item.partner_module_count, item.distinct_nus_module_count, item.mapping_count)
        for item in ranked
    ] == [("One", 2, 1, 2)]


def test_mapping_rows_preserve_order_optional_fields_and_units(
    repository: JsonCatalogRepository,
):
    response = repository.mappings("Test", "One")
    assert response.partner_module_count == 2
    assert response.distinct_nus_module_count == 1
    assert [row.partner_course.code for row in response.mappings] == ["SECOND", "FIRST"]
    assert response.mappings[0].partner_course.units is None
    assert response.mappings[1].partner_course.units == 3
    assert all(row.nus_course.units == 4 for row in response.mappings)


def test_unknown_selections_and_unavailable_sources_raise_shared_errors(
    repository: JsonCatalogRepository, tmp_path: Path
):
    with pytest.raises(UnknownSelection, match="Unknown degree$"):
        repository.recommendations("Missing")
    with pytest.raises(UnknownSelection, match="Unknown degree or university$"):
        repository.mappings("Test", "Missing")

    empty_root = tmp_path / "empty"
    empty_root.mkdir()
    with pytest.raises(CatalogUnavailable):
        JsonCatalogRepository(empty_root, tmp_path / "missing-manifest.json")
