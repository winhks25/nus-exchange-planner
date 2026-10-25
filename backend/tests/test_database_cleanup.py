"""Exercise actual tasks 1–7 schema changes through the read-only public API."""

import json
from pathlib import Path

import psycopg
import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.settings import Settings
from scripts.catalog_preview import build_preview
from scripts.catalog_seed import seed_preview
from scripts.cleanup_catalog import cleanup_sql
from scripts.snapshot_core_data import read_snapshot

EVIDENCE = Path(__file__).resolve().parents[2] / "plan/supabase-cleanup"

# Reproduce the completed changes, rather than mocking SQL query results.
COMPLETED_SQL = """
alter table degree_modules add column module_type text;
update degree_modules set module_type = 'Computing Foundations';
alter table degrees drop column source_order;
alter table pu_modules rename column verified_units to pu_units;
update pu_modules set name = initcap(name);
update pu_modules p set pu_units = m.source_partner_units
from module_mappings m where m.pu_module_id=p.id and m.source_partner_units is not null;
alter table module_mappings drop column source_order, drop column source_nus_title,
 drop column source_nus_units, drop column source_partner_title,
 drop column source_partner_units, drop column source_faculty, drop column source_page;
alter table specializations drop column source_order, drop column kind;
"""


def evidence():
    return (
        json.loads((EVIDENCE / "nusmods.json").read_text())["modules"],
        json.loads((EVIDENCE / "locations.json").read_text()),
    )


def test_completed_cleanup_and_enrichment_through_api(database):
    seed_preview(database, build_preview())
    database.execute(COMPLETED_SQL)
    settings = Settings(catalog_backend="postgres", database_url=database.reader_url)
    with TestClient(create_app(settings=settings)) as client:
        catalog = client.get("/api/v1/catalog")
        assert catalog.status_code == 200
        assert len(catalog.json()["degrees"]) == 6
        before = {}
        for degree in catalog.json()["degrees"]:
            response = client.get("/api/v1/recommendations", params={"degree": degree["name"]})
            assert response.status_code == 200
            before[degree["name"]] = response.json()
        modules, locations = evidence()
        database.execute(cleanup_sql(modules, locations))
        # Replay is safe and does not require the old column names.
        database.execute(cleanup_sql(modules, locations))
        snapshot, _ = read_snapshot(database.owner_url)
        assert "units" in snapshot["tables"]["nus_modules"]["columns"]
        assert "verified_units" not in snapshot["tables"]["nus_modules"]["columns"]
        assert "module_type" in snapshot["tables"]["degree_modules"]["columns"]
        assert "source_order" not in snapshot["tables"]["degrees"]["columns"]
        with psycopg.connect(database.owner_url) as conn:
            # Non-four and unknown units must not be silently replaced with 4.
            conn.execute("update nus_modules set units=6 where code='CS2103'")
            conn.execute("update nus_modules set units=null where code='CS2105'")
            expected = conn.execute("""select m.nus_module_code, n.name, n.units,
                p.code, p.name, p.pu_units, u.name, m.id
                from module_mappings m join nus_modules n on n.code=m.nus_module_code
                join pu_modules p on p.id=m.pu_module_id
                join partner_universities u on u.id=p.partner_university_id""").fetchall()
            memberships = conn.execute("""select d.name, dm.module_code from degree_modules dm
                join degrees d on d.id=dm.degree_id""").fetchall()
            actual_locations = conn.execute(
                "select name,city,country,continent from partner_universities order by name"
            ).fetchall()
        assert actual_locations == sorted(
            (r["name"], r["city"], r["country"], r["continent"]) for r in locations
        )
        for degree in catalog.json()["degrees"]:
            name = degree["name"]
            assert (
                client.get("/api/v1/recommendations", params={"degree": name}).json()
                == before[name]
            )
            codes = {code for d, code in memberships if d == name}
            for university in catalog.json()["universities"]:
                uni = university["name"]
                response = client.get("/api/v1/mappings", params={"degree": name, "uni": uni})
                assert response.status_code == 200
                rows = response.json()["mappings"]
                # The API intentionally omits null optional fields.
                for row in rows:
                    for course in row.values():
                        course.setdefault("units", None)
                        course.setdefault("title", None)
                selected = sorted(
                    (r for r in expected if r[0] in codes and r[6] == uni),
                    key=lambda r: (r[0], r[7]),
                )
                assert rows == [
                    {
                        "nus_course": {
                            "code": r[0],
                            "title": r[1],
                            "units": float(r[2]) if r[2] is not None else None,
                        },
                        "partner_course": {
                            "code": r[3],
                            "title": r[4],
                            "units": float(r[5]) if r[5] is not None else None,
                        },
                    }
                    for r in selected
                ]
                assert response.json()["distinct_nus_module_count"] == len({r[0] for r in selected})
                assert response.json()["partner_module_count"] == len(
                    {r[3].upper() for r in selected}
                )


@pytest.mark.parametrize("value", ["NaN", "Infinity", "-1", "0", "bad"])
def test_rejects_invalid_api_credits(value):
    modules, locations = evidence()
    modules[0]["units"] = value
    with pytest.raises(ValueError, match="Invalid credits"):
        cleanup_sql(modules, locations)


def test_incomplete_evidence_rolls_back_renames(database):
    seed_preview(database, build_preview())
    modules, locations = evidence()
    with pytest.raises(RuntimeError, match="evidence incomplete"):
        database.execute(cleanup_sql(modules[:-1], locations))
    with psycopg.connect(database.owner_url) as conn:
        assert conn.execute("select count(*) from nus_modules").fetchone()[0] == 152
        conn.execute("select offering_faculty, verified_units from nus_modules limit 1")


def test_unoffered_modules_still_have_official_titles():
    modules, _ = evidence()
    unoffered = [m for m in modules if not m["listed"]]
    assert len(unoffered) == 23
    assert all(m["title"] and float(m["units"]) > 0 for m in unoffered)
