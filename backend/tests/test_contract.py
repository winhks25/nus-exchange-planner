from pathlib import Path

import yaml

from app.main import app


def resolve(schema: dict, document: dict) -> dict:
    if "$ref" not in schema:
        return schema
    target = document
    for part in schema["$ref"].lstrip("#/").split("/"):
        target = target[part]
    return target


def test_generated_openapi_matches_contract():
    contract = yaml.safe_load((Path(__file__).resolve().parents[2] / "plan/contracts/openapi.yaml").read_text())
    generated = app.openapi()
    prefix = contract["servers"][0]["url"]
    for path, item in contract["paths"].items():
        actual = generated["paths"][prefix + path]["get"]
        specified = item["get"]
        assert set(actual["responses"]) == set(specified["responses"])
        assert {p["name"] for p in actual.get("parameters", [])} == {
            p["name"] for p in specified.get("parameters", [])
        }
        for parameter in specified.get("parameters", []):
            assert any(
                p["name"] == parameter["name"]
                and p["in"] == "query"
                and p["required"]
                for p in actual["parameters"]
            )
        for status, response in specified["responses"].items():
            assert status in actual["responses"]
            if status == "200":
                expected = response["content"]["application/json"]["schema"]
                got = resolve(actual["responses"][status]["content"]["application/json"]["schema"], generated)
                assert set(got["required"]) == set(expected["required"])
                assert set(got["properties"]) == set(expected["properties"])
            elif status in {"404", "503"}:
                got = resolve(actual["responses"][status]["content"]["application/json"]["schema"], generated)
                assert "detail" in got["required"]
            elif status == "422":
                got = resolve(actual["responses"][status]["content"]["application/json"]["schema"], generated)
                assert "detail" in got["properties"]

    for model, expected in {
        "DegreeOption": {"name", "degree"},
        "UniversityOption": {"name", "country"},
        "Recommendation": {"university", "country", "module_count"},
        "Mapping": {"nus_course", "partner_course"},
        "Course": {"code", "title", "units"},
    }.items():
        actual = generated["components"]["schemas"][model]
        assert set(actual["properties"]) == expected
    assert generated["components"]["schemas"]["Course"]["required"] == ["code"]
