"""Compare JSON and PostgreSQL catalog responses with the recorded baseline.

The script seeds a disposable local database from the deterministic import
preview, exercises both repositories through the real API, and writes a
human-readable report. It refuses non-local database targets.
"""

import argparse
import json
import logging
import platform
import sys
import time
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
DEFAULT_PERFORMANCE_OUTPUT = (
    REPO_ROOT / "plan" / "supabase-migration" / "performance.md"
)

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
        self.universities = sorted(
            preview["universities"], key=lambda item: item["source_order"]
        )
        self.nus_names = {
            item["code"]: item["name"] for item in preview["nus_modules"]
        }
        self.partner_names = {
            (item["university"], item["code"]): item["name"]
            for item in preview["partner_modules"]
        }

    def catalog(self) -> dict[str, Any]:
        return {
            "degrees": [
                {"name": item["name"], "degree": item["full_title"]}
                for item in self.degrees
            ],
            "universities": [
                {"name": item["name"], "country": item["country"]}
                for item in self.universities
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
        ranked.sort(
            key=lambda item: (-item["distinct_nus_module_count"], item["university"])
        )
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


def _assert_status(
    name: str, response, status: int, detail: str | None = None
) -> Check:
    if response.status_code != status:
        raise VerificationFailure(
            f"{name} failed: expected {status}, got {response.status_code}"
        )
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
        (item["degree"], item["university"]): item
        for item in preview["deltas"]["changed_pairs"]
    }
    actual_changed: set[tuple[str, str]] = set()

    for degree in [item["name"] for item in expected.degrees]:
        baseline_body = baseline["recommendations"][degree]["body"]
        json_body = json_client.get(
            "/api/v1/recommendations", params={"degree": degree}
        ).json()
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
        (item["degree"], item["university"]): item
        for item in preview["deltas"]["changed_pairs"]
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
    checks.append(
        _assert_status("Database available before outage", before, 200)
    )

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
    checks.append(
        _assert_status("Database recovers after restart", recovered, 200)
    )
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
        lines.append(
            f"| {check.name} | {'PASS' if check.passed else 'FAIL'} | {evidence} |"
        )
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


def _validate_target(url: str) -> None:
    host = urlsplit(url).hostname
    if host not in {"127.0.0.1", "localhost", "::1"}:
        raise SystemExit("Refusing to verify against a non-local database target")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--database-url",
        help="Existing local PostgreSQL URL; by default a disposable cluster is started.",
    )
    parser.add_argument(
        "--seed",
        action="store_true",
        help="Seed the supplied local database from the import preview before verifying.",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--enlarge",
        action="store_true",
        help="Add synthetic rows and record T027 performance evidence.",
    )
    parser.add_argument(
        "--performance-output", type=Path, default=DEFAULT_PERFORMANCE_OUTPUT
    )
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    preview = build_preview()
    expected = ExpectedCatalog(preview)
    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))

    cluster: PostgresCluster | None = None
    database: Any = None
    try:
        if args.database_url:
            _validate_target(args.database_url)
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
            checks.extend(
                verify_request_contract(expected, json_client, postgres_client)
            )
            checks.extend(verify_outage_and_recovery(cluster, postgres_client))

        if cluster is not None:
            checks.extend(verify_null_serialization(cluster))

        write_report(
            args.output,
            preview,
            checks,
            _postgres_version(database.url),
            "uv run --directory backend python -m scripts.verify_catalog",
        )
        LOG.info("Wrote %s (%d checks passed)", args.output, len(checks))

        if args.enlarge:
            if cluster is None:
                raise SystemExit("--enlarge requires a disposable cluster, not --database-url")
            enlarge(database)
            database.execute("analyze")
            evidence = collect_evidence(database)
            performance_command = (
                "uv run --directory backend python -m scripts.verify_catalog --enlarge "
                f"--output {args.output} --performance-output {args.performance_output}"
            )
            write_performance_report(
                args.performance_output, evidence, performance_command
            )
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
