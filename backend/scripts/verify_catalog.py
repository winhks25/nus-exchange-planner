"""Verify catalog API responses or reconcile a published database.

API mode seeds a disposable local database from the deterministic import
preview, exercises both repositories through the real API, and writes a
human-readable report. Reconcile mode is a read-only comparison between a
published catalog and the checked-in import plan, with a JSON report.
"""

import argparse
import hashlib
import json
import logging
import os
import platform
import sys
import time
from collections import Counter
from collections.abc import Iterable
from copy import deepcopy
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import psycopg
from fastapi.testclient import TestClient

from app.main import create_app
from app.repositories.base import CATALOG_UNAVAILABLE_MESSAGE
from app.settings import PoolSettings, Settings
from scripts.catalog_preview import build_preview
from scripts.catalog_seed import seed_preview
from scripts.import_catalog import (
    CatalogImportError,
    ImportPlan,
    _connect,
    _database_error_message,
    _expected_target_label,
    _target_summary,
    _validate_target,
    build_import_plan,
)
from scripts.measure_catalog_performance import (
    collect_evidence,
    enlarge,
)
from scripts.measure_catalog_performance import (
    write_report as write_performance_report,
)
from scripts.postgres_validation import PostgresCluster

REPO_ROOT = Path(__file__).resolve().parents[2]
BASELINE_PATH = REPO_ROOT / "plan" / "supabase-migration" / "baseline-responses.json"
DEFAULT_OUTPUT = REPO_ROOT / "plan" / "supabase-migration" / "api-validation.md"
DEFAULT_PERFORMANCE_OUTPUT = REPO_ROOT / "plan" / "supabase-migration" / "performance.md"

LOG = logging.getLogger("verify_catalog")


class VerificationFailure(AssertionError):
    """Raised when an API response diverges from the expected result."""


@dataclass
class Check:
    """One named verification result."""

    name: str
    passed: bool
    evidence: str


class ExpectedCatalog:
    """Build API responses directly from the import preview, independent of SQL."""

    def __init__(self, preview: dict[str, Any]) -> None:
        self.preview = preview
        self.degrees = sorted(preview["degrees"], key=lambda item: item["source_order"])
        self.universities = sorted(preview["universities"], key=lambda item: item["source_order"])
        self.nus_names = {item["code"]: item["name"] for item in preview["nus_modules"]}
        self.partner_names = {
            (item["university"], item["code"]): item["name"] for item in preview["partner_modules"]
        }

    def catalog(self) -> dict[str, Any]:
        return {
            "degrees": [
                {"name": item["name"], "degree": item["full_title"]} for item in self.degrees
            ],
            "universities": [
                {"name": item["name"], "country": item["country"]} for item in self.universities
            ],
        }

    def recommendations(self, degree: str) -> dict[str, Any]:
        ranked = []
        for university in self.universities:
            rows = self.pair(degree, university["name"])
            ranked.append(
                {
                    "university": university["name"],
                    "country": university["country"],
                    "partner_module_count": _partner_count(rows),
                    "distinct_nus_module_count": _nus_count(rows),
                    "mapping_count": len(rows),
                }
            )
        ranked.sort(key=lambda item: (-item["distinct_nus_module_count"], item["university"]))
        return {"degree": degree, "recommendations": ranked}

    def mappings(self, degree: str, university: str) -> dict[str, Any]:
        rows = [body for _, body in self.pair_rows(degree, university)]
        return {
            "degree": degree,
            "university": university,
            "partner_module_count": _partner_count(rows),
            "distinct_nus_module_count": _nus_count(rows),
            "mappings": rows,
        }

    def pair(self, degree: str, university: str) -> list[dict[str, Any]]:
        return [body for _, body in self.pair_rows(degree, university)]

    def pair_rows(self, degree: str, university: str) -> list[tuple[dict, dict]]:
        sources = [
            row
            for row in self.preview["mappings"]
            if row["university"] == university and degree in row["degree_names"]
        ]
        sources.sort(key=lambda row: (row["nus_module_code"], row["source_order"]))
        return [(source, self._serialize(source)) for source in sources]

    def _serialize(self, source: dict[str, Any]) -> dict[str, Any]:
        nus_code = source["nus_module_code"]
        nus_title = source["mapping_nus_title"] or self.nus_names.get(nus_code)
        nus_course: dict[str, Any] = {"code": nus_code, "units": 4}
        if nus_title is not None:
            nus_course["title"] = nus_title

        partner_code = source["partner_module_code"]
        partner_title = source["mapping_partner_title"] or self.partner_names.get(
            (source["university"], partner_code)
        )
        partner_course: dict[str, Any] = {"code": partner_code}
        if partner_title is not None:
            partner_course["title"] = partner_title
        if source["mapping_partner_units"] is not None:
            partner_course["units"] = source["mapping_partner_units"]

        return {"nus_course": nus_course, "partner_course": partner_course}


def _partner_count(rows: list[dict[str, Any]]) -> int:
    return len({row["partner_course"]["code"].upper() for row in rows})


def _nus_count(rows: list[dict[str, Any]]) -> int:
    return len({row["nus_course"]["code"].upper() for row in rows})


def _legacy_rows(pair_rows: list[tuple[dict, dict]]) -> list[dict[str, Any]]:
    """Reverse only the verified repairs so the result can match the baseline."""

    legacy = []
    for source, body in pair_rows:
        repair_fields = {repair["field"] for repair in source["applied_repairs"]}
        if "nus_course.code" in repair_fields:
            continue
        restored = deepcopy(body)
        if "partner_course.units" in repair_fields:
            units = source["source_partner_units"]
            if units is None:
                restored["partner_course"].pop("units", None)
            else:
                restored["partner_course"]["units"] = units
        legacy.append(restored)
    return legacy


def _assert_equal(name: str, actual: Any, expected: Any, evidence: str) -> Check:
    if actual != expected:
        raise VerificationFailure(
            f"{name} failed: {evidence}\nactual={json.dumps(actual, sort_keys=True)}"
            f"\nexpected={json.dumps(expected, sort_keys=True)}"
        )
    return Check(name=name, passed=True, evidence=evidence)


def _assert_status(name: str, response, status: int, detail: str | None = None) -> Check:
    if response.status_code != status:
        raise VerificationFailure(f"{name} failed: expected {status}, got {response.status_code}")
    if detail is not None and response.json().get("detail") != detail:
        raise VerificationFailure(
            f"{name} failed: unexpected detail {response.json().get('detail')!r}"
        )
    return Check(name=name, passed=True, evidence=f"status {status}")


def verify_catalog_and_recommendations(
    preview: dict[str, Any],
    expected: ExpectedCatalog,
    baseline: dict[str, Any],
    json_client: TestClient,
    postgres_client: TestClient,
) -> list[Check]:
    checks = [
        _assert_equal(
            "JSON catalog matches baseline",
            json_client.get("/api/v1/catalog").json(),
            baseline["catalog"]["body"],
            "GET /api/v1/catalog",
        ),
        _assert_equal(
            "PostgreSQL catalog matches preview",
            postgres_client.get("/api/v1/catalog").json(),
            expected.catalog(),
            "source-ordered degrees and universities",
        ),
    ]

    changed_pairs = {
        (item["degree"], item["university"]): item for item in preview["deltas"]["changed_pairs"]
    }
    actual_changed: set[tuple[str, str]] = set()

    for degree in [item["name"] for item in expected.degrees]:
        baseline_body = baseline["recommendations"][degree]["body"]
        json_body = json_client.get("/api/v1/recommendations", params={"degree": degree}).json()
        postgres_body = postgres_client.get(
            "/api/v1/recommendations", params={"degree": degree}
        ).json()
        checks.append(
            _assert_equal(
                f"JSON recommendations match baseline: {degree}",
                json_body,
                baseline_body,
                f"GET /api/v1/recommendations?degree={degree}",
            )
        )
        checks.append(
            _assert_equal(
                f"PostgreSQL recommendations match preview: {degree}",
                postgres_body,
                expected.recommendations(degree),
                f"GET /api/v1/recommendations?degree={degree}",
            )
        )

        legacy = deepcopy(postgres_body)
        for item in legacy["recommendations"]:
            key = (degree, item["university"])
            if key in changed_pairs:
                baseline_item = next(
                    row
                    for row in baseline_body["recommendations"]
                    if row["university"] == item["university"]
                )
                for field in (
                    "partner_module_count",
                    "distinct_nus_module_count",
                    "mapping_count",
                ):
                    if item[field] != baseline_item[field]:
                        actual_changed.add(key)
                    item[field] = baseline_item[field]
        checks.append(
            _assert_equal(
                f"Recommendation deltas are enumerated: {degree}",
                legacy,
                baseline_body,
                "only documented repairs change ranking counts",
            )
        )

    if actual_changed != set(changed_pairs):
        raise VerificationFailure(
            "Recommendation deltas do not match data-deltas.md: "
            f"reported={sorted(actual_changed)}, expected={sorted(changed_pairs)}"
        )
    checks.append(
        Check(
            "Documented ranking deltas",
            True,
            f"{len(changed_pairs)} changed degree/university pairs",
        )
    )

    return checks


def verify_mappings(
    preview: dict[str, Any],
    expected: ExpectedCatalog,
    baseline: dict[str, Any],
    json_client: TestClient,
    postgres_client: TestClient,
) -> list[Check]:
    checks: list[Check] = []
    changed_pairs = {
        (item["degree"], item["university"]): item for item in preview["deltas"]["changed_pairs"]
    }
    actual_changed: set[tuple[str, str]] = set()
    empty_pairs: list[tuple[str, str]] = []
    repeated_pairs: list[tuple[str, str]] = []

    for degree in [item["name"] for item in expected.degrees]:
        for university in [item["name"] for item in expected.universities]:
            key = f"{degree} || {university}"
            baseline_body = baseline["mappings"][key]["body"]
            pair_rows = expected.pair_rows(degree, university)
            expected_body = expected.mappings(degree, university)
            json_body = json_client.get(
                "/api/v1/mappings", params={"degree": degree, "uni": university}
            ).json()
            postgres_body = postgres_client.get(
                "/api/v1/mappings", params={"degree": degree, "uni": university}
            ).json()

            checks.append(
                _assert_equal(
                    f"JSON mappings match baseline: {key}",
                    json_body,
                    baseline_body,
                    f"GET /api/v1/mappings?degree={degree}&uni={university}",
                )
            )
            checks.append(
                _assert_equal(
                    f"PostgreSQL mappings match preview: {key}",
                    postgres_body,
                    expected_body,
                    "all qualifying rows, order and optional fields",
                )
            )

            legacy_rows = _legacy_rows(pair_rows)
            legacy_body = {
                "degree": degree,
                "university": university,
                "partner_module_count": _partner_count(legacy_rows),
                "distinct_nus_module_count": _nus_count(legacy_rows),
                "mappings": legacy_rows,
            }
            if legacy_body != baseline_body:
                raise VerificationFailure(
                    f"Unexplained mapping delta for {key}:\n"
                    f"legacy={json.dumps(legacy_body, sort_keys=True)}\n"
                    f"baseline={json.dumps(baseline_body, sort_keys=True)}"
                )
            if postgres_body != baseline_body:
                actual_changed.add((degree, university))
            if not pair_rows:
                empty_pairs.append((degree, university))
            if len(pair_rows) != len({body["nus_course"]["code"] for _, body in pair_rows}):
                repeated_pairs.append((degree, university))

    if actual_changed != set(changed_pairs):
        raise VerificationFailure(
            "Mapping deltas do not match data-deltas.md: "
            f"reported={sorted(actual_changed)}, expected={sorted(changed_pairs)}"
        )
    if not empty_pairs:
        raise VerificationFailure("Expected at least one valid-empty degree/university pair")
    if not repeated_pairs:
        raise VerificationFailure("Expected at least one pair with repeated NUS codes")

    checks.extend(
        [
            Check(
                "Documented mapping deltas",
                True,
                f"{len(changed_pairs)} changed pairs; "
                f"{len(repeated_pairs)} pairs preserve repeated NUS codes",
            ),
            Check(
                "Valid-empty pairs",
                True,
                ", ".join(f"{degree} / {university}" for degree, university in empty_pairs),
            ),
        ]
    )
    return checks


def verify_request_contract(
    expected: ExpectedCatalog, json_client: TestClient, postgres_client: TestClient
) -> list[Check]:
    checks: list[Check] = []
    for label, client in (("JSON", json_client), ("PostgreSQL", postgres_client)):
        checks.append(
            _assert_status(
                f"{label} missing degree is 422",
                client.get("/api/v1/recommendations"),
                422,
            )
        )
        degree = expected.degrees[0]["name"]
        checks.append(
            _assert_status(
                f"{label} missing university is 422",
                client.get("/api/v1/mappings", params={"degree": degree}),
                422,
            )
        )
        checks.append(
            _assert_status(
                f"{label} unknown degree is 404",
                client.get("/api/v1/recommendations", params={"degree": "Missing"}),
                404,
                "Unknown degree",
            )
        )
        checks.append(
            _assert_status(
                f"{label} unknown university is 404",
                client.get(
                    "/api/v1/mappings",
                    params={"degree": degree, "uni": "Missing University"},
                ),
                404,
                "Unknown degree or university",
            )
        )

    empty_degree, empty_university = next(
        (degree["name"], university["name"])
        for degree in expected.degrees
        for university in expected.universities
        if not expected.pair(degree["name"], university["name"])
    )
    for label, client in (("JSON", json_client), ("PostgreSQL", postgres_client)):
        response = client.get(
            "/api/v1/mappings",
            params={"degree": empty_degree, "uni": empty_university},
        )
        checks.append(
            _assert_equal(
                f"{label} valid-empty pair is 200",
                response.json(),
                {
                    "degree": empty_degree,
                    "university": empty_university,
                    "partner_module_count": 0,
                    "distinct_nus_module_count": 0,
                    "mappings": [],
                },
                f"{empty_degree} / {empty_university}",
            )
        )
    return checks


def verify_outage_and_recovery(
    cluster: PostgresCluster | None, postgres_client: TestClient
) -> list[Check]:
    if cluster is None:
        return [
            Check(
                "Database outage and recovery",
                True,
                "skipped: external database target was not paused",
            )
        ]

    checks = []
    before = postgres_client.get("/api/v1/catalog")
    checks.append(_assert_status("Database available before outage", before, 200))

    cluster.pause()
    outage = postgres_client.get("/api/v1/catalog")
    checks.append(
        _assert_status(
            "Database outage returns 503 without JSON fallback",
            outage,
            503,
            CATALOG_UNAVAILABLE_MESSAGE,
        )
    )

    cluster.resume()
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        recovered = postgres_client.get("/api/v1/catalog")
        if recovered.status_code == 200:
            break
        time.sleep(0.2)
    checks.append(_assert_status("Database recovers after restart", recovered, 200))
    return checks


EDGE_CASE_SQL = """
insert into public.catalog_import_batches (
  source_checksum, repair_checksum, status, is_current, completed_at
) values (repeat('c', 64), repeat('d', 64), 'completed', true, now());
insert into public.nus_modules (code, name) values
  ('CS2102', null),
  ('CS2103', 'Verified Module');
insert into public.degrees (name, faculty, full_title, source_order)
values ('Test', 'School of Computing', 'Bachelor of Test', 0);
insert into public.degree_modules (degree_id, module_code, requirement_type)
select d.id, pairs.code, null
from public.degrees d
cross join (values ('CS2102'), ('CS2103')) pairs(code)
where d.name = 'Test';
insert into public.partner_universities (name, country, source_order)
values ('One University', 'Japan', 0);
insert into public.pu_modules (code, name, partner_university_id)
select pairs.code, pairs.name, u.id
from (values ('P1', null), ('P2', 'Verified Partner')) pairs(code, name)
join public.partner_universities u on u.name = 'One University';
insert into public.module_mappings (nus_module_code, pu_module_id, source_order)
select pairs.nus_code, pm.id, pairs.source_order
from (
  values
    ('P1', 'CS2102', 0),
    ('P2', 'CS2103', 1)
) pairs(partner_code, nus_code, source_order)
join public.partner_universities u on u.name = 'One University'
join public.pu_modules pm
  on pm.partner_university_id = u.id and pm.code = pairs.partner_code;
"""


def verify_null_serialization(cluster: PostgresCluster) -> list[Check]:
    database = cluster.create_database()
    try:
        database.execute(EDGE_CASE_SQL)
        settings = Settings(
            catalog_backend="postgres",
            database_url=database.url,
            pool=PoolSettings(timeout=2),
        )
        with TestClient(create_app(settings=settings)) as client:
            response = client.get(
                "/api/v1/mappings",
                params={"degree": "Test", "uni": "One University"},
            )
            return [
                _assert_equal(
                    "Null titles and units are omitted",
                    response.json(),
                    {
                        "degree": "Test",
                        "university": "One University",
                        "partner_module_count": 2,
                        "distinct_nus_module_count": 2,
                        "mappings": [
                            {
                                "nus_course": {"code": "CS2102", "units": 4.0},
                                "partner_course": {"code": "P1"},
                            },
                            {
                                "nus_course": {
                                    "code": "CS2103",
                                    "title": "Verified Module",
                                    "units": 4.0,
                                },
                                "partner_course": {
                                    "code": "P2",
                                    "title": "Verified Partner",
                                },
                            },
                        ],
                    },
                    "optional title/unit fields stay absent when unknown",
                )
            ]
    finally:
        cluster.drop_database(database)


def _postgres_version(url: str) -> str:
    with psycopg.connect(url) as conn:
        return str(conn.execute("show server_version").fetchone()[0])


def write_report(
    path: Path,
    preview: dict[str, Any],
    checks: list[Check],
    server_version: str,
    command: str,
) -> None:
    snapshot = preview["source_snapshot"]
    lines = [
        "# PostgreSQL API validation (T025)",
        "",
        f"Generated: {datetime.now(UTC).isoformat(timespec='seconds')}",
        "",
        "## Environment",
        "",
        f"- Python: {platform.python_version()}",
        f"- PostgreSQL: {server_version}",
        f"- psycopg: {psycopg.__version__}",
        f"- Source checksum: `{snapshot['source_checksum_sha256']}`",
        f"- Repair checksum: `{snapshot['repair_checksum_sha256']}`",
        "",
        "## Command",
        "",
        "```bash",
        command,
        "```",
        "",
        "## Checks",
        "",
        "| Check | Result | Evidence |",
        "| --- | --- | --- |",
    ]
    for check in checks:
        evidence = check.evidence.replace("|", "\\|")
        lines.append(f"| {check.name} | {'PASS' if check.passed else 'FAIL'} | {evidence} |")
    lines.extend(
        [
            "",
            "## Scope and limitations",
            "",
            "- The PostgreSQL side is seeded from the deterministic import preview into a",
            "  disposable TLS-enabled local database created from the checked-in migrations.",
            "- The real Phase 3 importer publication has not run against Supabase yet, so this",
            "  records API behavior and repair deltas rather than target-project import evidence.",
            "- Catches, counts and ordering are compared exactly for all six degrees and all",
            "  thirty degree/university pairs; only the documented repairs are allowed to differ.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _number(value: Any) -> float | None:
    """Normalize PostgreSQL numerics to JSON numbers for exact comparison."""

    return None if value is None else float(value)


def _json_value(value: Any) -> Any:
    """Round-trip JSONB values so Decimal and scalar types compare stably."""

    if value is None:
        return None
    return json.loads(json.dumps(value, ensure_ascii=False, default=str))


def _digest(records: Iterable[dict[str, Any]]) -> str:
    """Hash canonical records so the report carries a compact fingerprint."""

    payload = json.dumps(list(records), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _count_summary(counts: Counter[Any]) -> dict[str, int]:
    """Describe multiplicity without dumping every duplicate group."""

    return {
        "groups": len(counts),
        "rows": sum(counts.values()),
        "duplicate_groups": sum(1 for value in counts.values() if value > 1),
        "duplicate_rows": sum(value for value in counts.values() if value > 1),
    }


class Reconciler:
    """Read-only comparison between the published catalog and the import plan."""

    def __init__(self, connection: psycopg.Connection, plan: ImportPlan) -> None:
        self.connection = connection
        self.plan = plan
        self.checks: list[dict[str, Any]] = []
        self.batch_id: int | None = None

    def _record(
        self,
        name: str,
        ok: bool,
        expected: Any = None,
        actual: Any = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        check: dict[str, Any] = {"name": name, "ok": bool(ok)}
        if expected is not None:
            check["expected"] = expected
        if actual is not None:
            check["actual"] = actual
        if details:
            check["details"] = details
        self.checks.append(check)

    def _compare_map(
        self,
        name: str,
        expected: list[dict[str, Any]],
        actual: list[dict[str, Any]],
        key_fields: tuple[str, ...],
    ) -> None:
        """Compare complete records and report missing, extra and changed keys."""

        def key(record: dict[str, Any]) -> tuple[Any, ...]:
            return tuple(record.get(field) for field in key_fields)

        def sort_key(record: dict[str, Any]) -> tuple[str, ...]:
            return tuple(str(record.get(field)) for field in key_fields)

        expected_map = {key(record): record for record in expected}
        actual_map = {key(record): record for record in actual}
        missing = sorted(set(expected_map) - set(actual_map), key=str)
        unexpected = sorted(set(actual_map) - set(expected_map), key=str)
        changed = sorted(
            (
                item
                for item in set(expected_map) & set(actual_map)
                if expected_map[item] != actual_map[item]
            ),
            key=str,
        )
        changed_details = []
        for item in changed[:20]:
            fields = sorted(
                field
                for field in expected_map[item]
                if expected_map[item].get(field) != actual_map[item].get(field)
            )
            changed_details.append({"key": list(item), "fields": fields})
        expected_summary = {
            "records": len(expected),
            "digest": _digest(sorted(expected, key=sort_key)),
        }
        actual_summary = {
            "records": len(actual),
            "digest": _digest(sorted(actual, key=sort_key)),
        }
        self._record(
            name,
            not missing and not unexpected and not changed,
            expected_summary,
            actual_summary,
            {
                "missing": [list(item) for item in missing[:20]],
                "unexpected": [list(item) for item in unexpected[:20]],
                "changed": changed_details,
            },
        )

    def _compare_counts(
        self,
        name: str,
        expected: Counter[Any],
        actual: Counter[Any],
    ) -> None:
        """Compare duplicate-group multiplicities without hiding repeated rows."""

        mismatches = [
            {
                "key": list(item),
                "expected": expected.get(item, 0),
                "actual": actual.get(item, 0),
            }
            for item in sorted(set(expected) | set(actual), key=str)
            if expected.get(item, 0) != actual.get(item, 0)
        ]
        self._record(
            name,
            not mismatches,
            _count_summary(expected),
            _count_summary(actual),
            {"mismatches": mismatches[:50]},
        )

    def _check_batch(self) -> None:
        """Verify the completed publication marker and its source accounting."""

        rows = self.connection.execute(
            """
            select
              id,
              source_checksum,
              repair_checksum,
              status,
              is_current,
              source_file_count,
              raw_row_count,
              accepted_row_count,
              repaired_row_count,
              quarantined_row_count,
              source_manifest,
              completed_at
            from public.catalog_import_batches
            order by id
            """
        ).fetchall()
        self.batch_id = int(rows[0][0]) if len(rows) == 1 else None
        self._record("published batch count", len(rows) == 1, 1, len(rows))
        if len(rows) != 1:
            return
        row = rows[0]
        expected_manifest = {
            "files": [
                {
                    "path": archive.path,
                    "kind": archive.kind,
                    "sha256": archive.sha256,
                    "byte_size": archive.byte_size,
                }
                for archive in self.plan.archives
            ],
            "source_checksum_sha256": self.plan.source_checksum,
            "repair_checksum_sha256": self.plan.repair_checksum,
            "academic_year": self.plan.academic_year,
            "prepared_on": self.plan.prepared_on,
            "repair_file": self.plan.repair_file,
        }
        actual = {
            "source_checksum": row[1],
            "repair_checksum": row[2],
            "status": row[3],
            "is_current": row[4],
            "source_file_count": row[5],
            "raw_row_count": row[6],
            "accepted_row_count": row[7],
            "repaired_row_count": row[8],
            "quarantined_row_count": row[9],
            "source_manifest": row[10],
            "completed_at_present": row[11] is not None,
        }
        expected = {
            "source_checksum": self.plan.source_checksum,
            "repair_checksum": self.plan.repair_checksum,
            "status": "completed",
            "is_current": True,
            "source_file_count": len(self.plan.archives),
            "raw_row_count": self.plan.summary["raw_rows"],
            "accepted_row_count": self.plan.summary["accepted_rows"],
            "repaired_row_count": self.plan.summary["repaired_rows"],
            "quarantined_row_count": self.plan.summary["quarantined_rows"],
            "source_manifest": expected_manifest,
            "completed_at_present": True,
        }
        self._record(
            "published batch fields",
            actual == expected,
            expected,
            actual,
            {
                "changed_fields": sorted(
                    field for field in expected if expected[field] != actual[field]
                )
            },
        )

    def _check_snapshots(self) -> None:
        """Compare archived text, parsed JSON, checksums and source kinds."""

        rows = self.connection.execute(
            """
            select file_path, source_kind, raw_text, parsed_json, sha256, byte_size, batch_id
            from public.catalog_source_snapshots
            order by file_path
            """
        ).fetchall()
        actual = [
            {
                "path": row[0],
                "kind": row[1],
                "raw_text": row[2],
                "parsed": row[3],
                "sha256": row[4],
                "byte_size": row[5],
                "batch_id": row[6],
            }
            for row in rows
        ]
        expected = [
            {
                "path": archive.path,
                "kind": archive.kind,
                "raw_text": archive.raw_text,
                "parsed": archive.parsed,
                "sha256": archive.sha256,
                "byte_size": archive.byte_size,
                "batch_id": self.batch_id,
            }
            for archive in self.plan.archives
        ]
        self._compare_map("archived source snapshots", expected, actual, ("path",))

    def _check_source_rows(self) -> None:
        """Compare every raw row, including quarantined and repaired outcomes."""

        rows = self.connection.execute(
            """
            select
              s.file_path,
              r.mapping_index,
              r.raw_json,
              r.source_nus_code,
              r.source_partner_code,
              r.source_nus_title,
              r.source_partner_title,
              r.source_nus_units,
              r.source_partner_units,
              r.source_faculty,
              r.source_page,
              r.outcome
            from public.catalog_source_rows r
            join public.catalog_source_snapshots s on s.id = r.snapshot_id
            order by s.file_path, r.mapping_index
            """
        ).fetchall()
        actual = [
            {
                "file": row[0],
                "index": row[1],
                "raw_json": row[2],
                "nus_code": row[3],
                "partner_code": row[4],
                "nus_title": row[5],
                "partner_title": row[6],
                "nus_units": _number(row[7]),
                "partner_units": _number(row[8]),
                "faculty": row[9],
                "page": row[10],
                "outcome": row[11],
            }
            for row in rows
        ]
        expected = [
            {
                "file": item.source_file,
                "index": item.mapping_index,
                "raw_json": item.raw_row,
                "nus_code": item.source_nus_code,
                "partner_code": item.source_partner_code,
                "nus_title": item.source_nus_title,
                "partner_title": item.source_partner_title,
                "nus_units": item.source_nus_units,
                "partner_units": item.source_partner_units,
                "faculty": item.source_faculty,
                "page": item.source_page,
                "outcome": item.outcome,
            }
            for item in self.plan.source_rows
        ]
        self._compare_map("catalog source rows", expected, actual, ("file", "index"))
        self._compare_counts(
            "source row outcome counts",
            Counter(item["outcome"] for item in expected),
            Counter(item["outcome"] for item in actual),
        )

    def _check_entities(self) -> None:
        """Compare normalized entities and links, independent of row presentation."""

        queries = {
            "degrees": (
                "select name, faculty, full_title, source_order from public.degrees",
                ("name",),
                [
                    {
                        "name": item.name,
                        "faculty": item.faculty,
                        "full_title": item.full_title,
                        "source_order": item.source_order,
                    }
                    for item in self.plan.entities.degrees
                ],
            ),
            "NUS modules": (
                "select code, name, offering_faculty, verified_units from public.nus_modules",
                ("code",),
                [
                    {
                        "code": item.code,
                        "name": item.name,
                        "offering_faculty": item.offering_faculty,
                        "verified_units": item.verified_units,
                    }
                    for item in self.plan.entities.nus_modules
                ],
            ),
            "degree memberships": (
                """
                select d.name as degree, dm.module_code, dm.requirement_type
                from public.degree_modules dm
                join public.degrees d on d.id = dm.degree_id
                """,
                ("degree", "module_code"),
                [
                    {
                        "degree": item.degree,
                        "module_code": item.module_code,
                        "requirement_type": item.requirement_type,
                    }
                    for item in self.plan.entities.degree_modules
                ],
            ),
            "partner universities": (
                (
                    "select name, country, city, continent, source_order "
                    "from public.partner_universities"
                ),
                ("name",),
                [
                    {
                        "name": item.name,
                        "country": item.country,
                        "city": item.city,
                        "continent": item.continent,
                        "source_order": item.source_order,
                    }
                    for item in self.plan.entities.universities
                ],
            ),
            "partner modules": (
                """
                select u.name as university, pm.code, pm.name, pm.verified_units
                from public.pu_modules pm
                join public.partner_universities u on u.id = pm.partner_university_id
                """,
                ("university", "code"),
                [
                    {
                        "university": item.university,
                        "code": item.code,
                        "name": item.name,
                        "verified_units": item.verified_units,
                    }
                    for item in self.plan.entities.partner_modules
                ],
            ),
            "specializations": (
                """
                select d.name as degree, s.name as specialization, s.kind, s.source_order
                from public.specializations s
                join public.degrees d on d.id = s.degree_id
                """,
                ("degree", "specialization"),
                [
                    {
                        "degree": item.degree,
                        "specialization": item.name,
                        "kind": item.kind,
                        "source_order": item.source_order,
                    }
                    for item in self.plan.entities.specializations
                ],
            ),
            "specialization memberships": (
                """
                select d.name as degree, s.name as specialization, sm.module_code
                from public.specialization_modules sm
                join public.specializations s on s.id = sm.specialization_id
                join public.degrees d on d.id = s.degree_id
                """,
                ("degree", "specialization", "module_code"),
                [
                    {
                        "degree": item.degree,
                        "specialization": item.specialization,
                        "module_code": item.module_code,
                    }
                    for item in self.plan.entities.specialization_modules
                ],
            ),
        }
        for label, (query, key_fields, expected) in queries.items():
            cursor = self.connection.execute(query)
            rows = cursor.fetchall()
            columns = [column.name for column in cursor.description]
            actual = [
                {
                    column: (_number(value) if column == "verified_units" else value)
                    for column, value in zip(columns, row, strict=True)
                }
                for row in rows
            ]
            self._compare_map(label, expected, actual, key_fields)

    def _check_mappings(self) -> None:
        """Compare each active mapping with its source row and presentation fields."""

        rows = self.connection.execute(
            """
            select
              s.file_path,
              r.mapping_index,
              u.name,
              m.nus_module_code,
              pm.code,
              m.source_order,
              m.source_nus_title,
              m.source_nus_units,
              m.source_partner_title,
              m.source_partner_units,
              m.source_faculty,
              m.source_page
            from public.module_mappings m
            join public.catalog_source_rows r on r.id = m.source_row_id
            join public.catalog_source_snapshots s on s.id = r.snapshot_id
            join public.pu_modules pm on pm.id = m.pu_module_id
            join public.partner_universities u on u.id = pm.partner_university_id
            order by s.file_path, r.mapping_index
            """
        ).fetchall()
        actual = [
            {
                "file": row[0],
                "index": row[1],
                "university": row[2],
                "nus_module_code": row[3],
                "partner_module_code": row[4],
                "source_order": row[5],
                "source_nus_title": row[6],
                "source_nus_units": _number(row[7]),
                "source_partner_title": row[8],
                "source_partner_units": _number(row[9]),
                "source_faculty": row[10],
                "source_page": row[11],
            }
            for row in rows
        ]
        expected = [
            {
                "file": item.source_file,
                "index": item.mapping_index,
                "university": item.university,
                "nus_module_code": item.nus_module_code,
                "partner_module_code": item.partner_module_code,
                "source_order": item.source_order,
                "source_nus_title": item.source_nus_title,
                "source_nus_units": item.source_nus_units,
                "source_partner_title": item.source_partner_title,
                "source_partner_units": item.source_partner_units,
                "source_faculty": item.source_faculty,
                "source_page": item.source_page,
            }
            for item in self.plan.mappings
        ]
        self._compare_map("module mappings", expected, actual, ("file", "index"))

    def _check_issues(self) -> None:
        """Compare every issue with its source address, severity and status."""

        rows = self.connection.execute(
            """
            select
              s.file_path,
              r.mapping_index,
              i.json_pointer,
              i.issue_code,
              i.severity,
              i.message,
              i.status
            from public.catalog_issues i
            join public.catalog_source_snapshots s on s.id = i.snapshot_id
            left join public.catalog_source_rows r on r.id = i.source_row_id
            """
        ).fetchall()
        actual = [
            {
                "file": row[0],
                "index": row[1],
                "pointer": row[2],
                "code": row[3],
                "severity": row[4],
                "message": row[5],
                "status": row[6],
            }
            for row in rows
        ]
        expected = [
            {
                "file": item.source_file,
                "index": item.mapping_index,
                "pointer": item.json_pointer,
                "code": item.code,
                "severity": item.severity,
                "message": item.message,
                "status": item.status,
            }
            for item in self.plan.issues
        ]
        self._compare_map("catalog issues", expected, actual, ("file", "index", "pointer", "code"))

    def _check_repairs(self) -> None:
        """Compare repair values, citations, dates and resolved status."""

        rows = self.connection.execute(
            """
            select
              s.file_path,
              r.mapping_index,
              p.json_pointer,
              p.before_value,
              p.after_value,
              p.source_url,
              p.source_title,
              to_char(p.accessed_on, 'YYYY-MM-DD'),
              p.academic_year,
              p.evidence,
              p.status
            from public.catalog_repairs p
            join public.catalog_source_snapshots s on s.id = p.snapshot_id
            left join public.catalog_source_rows r on r.id = p.source_row_id
            """
        ).fetchall()
        actual = [
            {
                "file": row[0],
                "index": row[1],
                "pointer": row[2],
                "before": _json_value(row[3]),
                "after": _json_value(row[4]),
                "source_url": row[5],
                "source_title": row[6],
                "accessed_on": row[7],
                "academic_year": row[8],
                "evidence": row[9],
                "status": row[10],
            }
            for row in rows
        ]
        expected = [
            {
                "file": item.source_file,
                "index": item.mapping_index,
                "pointer": item.json_pointer,
                "before": _json_value(item.before_value),
                "after": _json_value(item.after_value),
                "source_url": item.source_url,
                "source_title": item.source_title,
                "accessed_on": item.accessed_on.isoformat(),
                "academic_year": item.academic_year,
                "evidence": item.evidence,
                "status": item.status,
            }
            for item in self.plan.repairs
        ]
        self._compare_map(
            "catalog repairs",
            expected,
            actual,
            ("file", "index", "pointer", "source_url"),
        )

    def _scalar(self, query: str, params: tuple[Any, ...] = ()) -> int:
        return int(self.connection.execute(query, params).fetchone()[0])

    def _check_orphans(self) -> None:
        """Prove that every active row, issue and repair is linked to its source."""

        batch_id = self.batch_id if self.batch_id is not None else -1
        checks = {
            "mappings without a source row": self._scalar(
                "select count(*) from public.module_mappings where source_row_id is null"
            ),
            "active source rows without a mapping": self._scalar(
                """
                select count(*)
                from public.catalog_source_rows r
                left join public.module_mappings m on m.source_row_id = r.id
                where r.outcome <> 'quarantined' and m.id is null
                """
            ),
            "quarantined source rows with a mapping": self._scalar(
                """
                select count(*)
                from public.catalog_source_rows r
                join public.module_mappings m on m.source_row_id = r.id
                where r.outcome = 'quarantined'
                """
            ),
            "row issues without a source row": self._scalar(
                """
                select count(*)
                from public.catalog_issues
                where json_pointer like '/mappings/%%' and source_row_id is null
                """
            ),
            "repairs without a source row": self._scalar(
                "select count(*) from public.catalog_repairs where source_row_id is null"
            ),
            "source rows outside the current batch": self._scalar(
                """
                select count(*)
                from public.catalog_source_rows r
                join public.catalog_source_snapshots s on s.id = r.snapshot_id
                where s.batch_id <> %s
                """,
                (batch_id,),
            ),
            "snapshots outside the current batch": self._scalar(
                "select count(*) from public.catalog_source_snapshots where batch_id <> %s",
                (batch_id,),
            ),
        }
        expected = {name: 0 for name in checks}
        self._record(
            "referential integrity",
            all(value == 0 for value in checks.values()),
            expected,
            checks,
        )

    def _check_duplicates(self) -> None:
        """Preserve every repeated source row with the same multiplicity."""

        partner_rows = self.connection.execute(
            """
            select u.name, pm.code, count(*)::int
            from public.module_mappings m
            join public.pu_modules pm on pm.id = m.pu_module_id
            join public.partner_universities u on u.id = pm.partner_university_id
            group by u.name, pm.code
            """
        ).fetchall()
        nus_rows = self.connection.execute(
            """
            select u.name, m.nus_module_code, count(*)::int
            from public.module_mappings m
            join public.pu_modules pm on pm.id = m.pu_module_id
            join public.partner_universities u on u.id = pm.partner_university_id
            group by u.name, m.nus_module_code
            """
        ).fetchall()
        pair_rows = self.connection.execute(
            """
            select u.name, m.nus_module_code, pm.code, count(*)::int
            from public.module_mappings m
            join public.pu_modules pm on pm.id = m.pu_module_id
            join public.partner_universities u on u.id = pm.partner_university_id
            group by u.name, m.nus_module_code, pm.code
            """
        ).fetchall()
        self._compare_counts(
            "partner-code multiplicity",
            Counter((item.university, item.partner_module_code) for item in self.plan.mappings),
            Counter((row[0], row[1]) for row in partner_rows) | Counter()
            if False
            else Counter({(row[0], row[1]): row[2] for row in partner_rows}),
        )
        self._compare_counts(
            "NUS-code multiplicity",
            Counter((item.university, item.nus_module_code) for item in self.plan.mappings),
            Counter({(row[0], row[1]): row[2] for row in nus_rows}),
        )
        self._compare_counts(
            "exact-pair multiplicity",
            Counter(
                (item.university, item.nus_module_code, item.partner_module_code)
                for item in self.plan.mappings
            ),
            Counter({(row[0], row[1], row[2]): row[3] for row in pair_rows}),
        )

    def run(self) -> dict[str, Any]:
        """Run every reconciliation check and return a sanitized report."""

        self._check_batch()
        self._check_snapshots()
        self._check_source_rows()
        self._check_entities()
        self._check_mappings()
        self._check_issues()
        self._check_repairs()
        self._check_orphans()
        self._check_duplicates()
        failed = [check for check in self.checks if not check["ok"]]
        return {
            "generated_at": datetime.now(UTC).isoformat(),
            "mode": "reconcile",
            "ok": not failed,
            "source_checksum": self.plan.source_checksum,
            "repair_checksum": self.plan.repair_checksum,
            "batch_id": self.batch_id,
            "summary": {
                "checks": len(self.checks),
                "passed": len(self.checks) - len(failed),
                "failed": len(failed),
            },
            "checks": self.checks,
        }


def _run_reconcile(args: argparse.Namespace, parser: argparse.ArgumentParser) -> int:
    """Reconcile a published database without seeding or writing catalog data."""

    database_url = args.database_url or os.environ.get("IMPORT_DATABASE_URL")
    if not database_url:
        parser.error("--reconcile requires --database-url or IMPORT_DATABASE_URL")
    target = args.target_project_ref
    if not target:
        target = _expected_target_label(database_url)
        if target != "local":
            parser.error("remote reconciliation requires --target-project-ref")
    try:
        _validate_target(database_url, target)
        plan = build_import_plan()
        with _connect(database_url) as connection:
            connection.read_only = True
            with connection.transaction():
                report = Reconciler(connection, plan).run()
    except CatalogImportError as exc:
        LOG.error("%s", exc)
        return 2
    except psycopg.Error as exc:
        LOG.error("%s", _database_error_message(exc))
        return 1
    report["target"] = _target_summary(database_url)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
    return 0 if report["ok"] else 1


def _validate_local_target(url: str) -> None:
    host = urlsplit(url).hostname
    if host not in {"127.0.0.1", "localhost", "::1"}:
        raise SystemExit("Refusing to verify against a non-local database target")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--database-url",
        help="Existing PostgreSQL URL; by default a disposable local cluster is started.",
    )
    parser.add_argument(
        "--reconcile",
        action="store_true",
        help="Compare a published database with the checked-in import plan; read-only.",
    )
    parser.add_argument(
        "--target-project-ref",
        help="expected Supabase project ref for --reconcile, or 'local'",
    )
    parser.add_argument(
        "--seed",
        action="store_true",
        help="Seed the supplied local database from the import preview before verifying.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="report path; defaults to api-validation.md for API mode",
    )
    parser.add_argument(
        "--enlarge",
        action="store_true",
        help="Add synthetic rows and record T027 performance evidence.",
    )
    parser.add_argument("--performance-output", type=Path, default=DEFAULT_PERFORMANCE_OUTPUT)
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    if args.reconcile:
        if args.seed or args.enlarge:
            parser.error("--reconcile cannot be combined with --seed or --enlarge")
        return _run_reconcile(args, parser)

    output = args.output or DEFAULT_OUTPUT
    preview = build_preview()
    expected = ExpectedCatalog(preview)
    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))

    cluster: PostgresCluster | None = None
    database: Any = None
    try:
        if args.database_url:
            _validate_local_target(args.database_url)
            if not args.seed:
                raise SystemExit(
                    "Pass --seed to publish the preview into the supplied local database"
                )
            database = _ExternalDatabase(args.database_url)
        else:
            cluster = PostgresCluster()
            cluster.start()
            database = cluster.create_database()

        if args.seed or cluster is not None:
            seed_preview(database, preview)

        json_app = create_app(settings=Settings(catalog_backend="json"))
        postgres_settings = Settings(
            catalog_backend="postgres",
            database_url=database.url,
            pool=PoolSettings(timeout=2),
        )
        postgres_app = create_app(settings=postgres_settings)

        checks: list[Check] = []
        with TestClient(json_app) as json_client, TestClient(postgres_app) as postgres_client:
            checks.extend(
                verify_catalog_and_recommendations(
                    preview, expected, baseline, json_client, postgres_client
                )
            )
            checks.extend(
                verify_mappings(preview, expected, baseline, json_client, postgres_client)
            )
            checks.extend(verify_request_contract(expected, json_client, postgres_client))
            checks.extend(verify_outage_and_recovery(cluster, postgres_client))

        if cluster is not None:
            checks.extend(verify_null_serialization(cluster))

        write_report(
            output,
            preview,
            checks,
            _postgres_version(database.url),
            "uv run --directory backend python -m scripts.verify_catalog",
        )
        LOG.info("Wrote %s (%d checks passed)", output, len(checks))

        if args.enlarge:
            if cluster is None:
                raise SystemExit("--enlarge requires a disposable cluster, not --database-url")
            enlarge(database)
            database.execute("analyze")
            evidence = collect_evidence(database)
            performance_command = (
                "uv run --directory backend python -m scripts.verify_catalog --enlarge "
                f"--output {output} --performance-output {args.performance_output}"
            )
            write_performance_report(args.performance_output, evidence, performance_command)
            LOG.info("Wrote %s", args.performance_output)
        return 0
    except VerificationFailure as exc:
        LOG.error("%s", exc)
        return 1
    finally:
        if cluster is not None:
            cluster.stop()


class _ExternalDatabase:
    """Adapter for an already-running local database URL."""

    def __init__(self, url: str) -> None:
        self.url = url

    def execute(self, sql: str) -> None:
        with psycopg.connect(self.url) as conn, conn.transaction():
            conn.execute(sql)


if __name__ == "__main__":
    sys.exit(main())
