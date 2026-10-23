"""Capture or compare read-only catalog API responses against a JSON baseline.

Capture mode discovers degrees and universities from the live catalog, records
every public read-only response, and writes a baseline without seeding or
mutating data. Compare mode replays the baseline requests and writes a report
with exact status and body differences. Both modes only issue bounded GET
requests and never overwrite the expected baseline during comparison.
"""

import argparse
import json
import platform
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BASELINE = (
    REPO_ROOT / "plan" / "remove-catalog-tables" / "baseline-responses.json"
)
DEFAULT_REPORT = (
    REPO_ROOT / "plan" / "remove-catalog-tables" / "post-delete-validation.md"
)
API_ROOT = "/api/v1"
SCHEMA_VERSION = 1
TOOL_NAME = "compare_api_baseline"
TOOL_VERSION = "1.0"
MAX_RESPONSE_BYTES = 2_000_000
UNKNOWN_DEGREE = "Unknown Degree (baseline)"
UNKNOWN_UNIVERSITY = "Unknown University (baseline)"


class BaselineError(RuntimeError):
    """Raised when capture or comparison cannot produce trustworthy evidence."""


class _NoRedirectHandler(HTTPRedirectHandler):
    """Refuse redirects so a read-only run cannot leave the verified origin."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class ReadOnlyClient:
    """Bounded GET client that records the request metadata used by a baseline."""

    def __init__(
        self,
        origin: str,
        timeout: float = 10.0,
        max_requests: int = 200,
    ) -> None:
        if not 0.1 <= timeout <= 30.0:
            raise BaselineError("--timeout must be between 0.1 and 30 seconds")
        if not 1 <= max_requests <= 500:
            raise BaselineError("--max-requests must be between 1 and 500")
        self.origin = origin
        self.timeout = timeout
        self.max_requests = max_requests
        self.request_count = 0
        self._opener = build_opener(_NoRedirectHandler())

    def get(self, path: str, params: dict[str, str] | None = None) -> dict[str, Any]:
        """Issue one GET request and return its status and parsed JSON body."""

        # Bound the run before issuing any network request.
        self.request_count += 1
        if self.request_count > self.max_requests:
            raise BaselineError(
                f"request limit of {self.max_requests} exceeded before GET {path}"
            )

        # Build the exact URL that will be recorded in the baseline.
        safe_params = params or {}
        query = f"?{urlencode(safe_params)}" if safe_params else ""
        url = f"{self.origin}{path}{query}"
        request = Request(
            url,
            method="GET",
            headers={
                "Accept": "application/json",
                "User-Agent": f"{TOOL_NAME}/{TOOL_VERSION}",
            },
        )
        requested_at = datetime.now(UTC).isoformat()

        # Read bounded response bytes, including expected 404/422 responses.
        try:
            with self._opener.open(request, timeout=self.timeout) as response:
                status = response.status
                raw_body = _read_bounded(response)
        except HTTPError as exc:
            status = exc.code
            raw_body = _read_bounded(exc)
        except (URLError, TimeoutError, OSError) as exc:
            reason = getattr(exc, "reason", exc)
            raise BaselineError(f"GET {path} failed: {reason}") from None

        # Preserve the exact JSON structure, including array order and optional fields.
        try:
            body = json.loads(raw_body)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise BaselineError(f"GET {path} did not return valid JSON: {exc}") from None

        return {
            "request": {
                "method": "GET",
                "path": path,
                "params": safe_params,
                "url": url,
            },
            "requested_at_utc": requested_at,
            "status": status,
            "body": body,
        }


def main(argv: list[str] | None = None) -> int:
    """Dispatch capture or comparison and return a process exit status."""

    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "capture":
            capture(args)
        else:
            return compare(args)
    except BaselineError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


def _build_parser() -> argparse.ArgumentParser:
    """Create the capture and compare command-line interfaces."""

    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Capture records a new baseline from a verified read-only endpoint.
    capture_parser = subparsers.add_parser("capture", help="capture a new baseline")
    capture_parser.add_argument("--base-url", required=True)
    capture_parser.add_argument("--expected-origin")
    capture_parser.add_argument("--output", type=Path, default=DEFAULT_BASELINE)
    capture_parser.add_argument("--force", action="store_true")
    _add_limit_arguments(capture_parser)

    # Compare replays a baseline and writes differences without changing it.
    compare_parser = subparsers.add_parser("compare", help="compare against a baseline")
    compare_parser.add_argument(
        "--base-url", help="defaults to the baseline endpoint origin"
    )
    compare_parser.add_argument("--expected-origin")
    compare_parser.add_argument("--baseline", type=Path, default=DEFAULT_BASELINE)
    compare_parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    _add_limit_arguments(compare_parser)
    return parser


def _add_limit_arguments(parser: argparse.ArgumentParser) -> None:
    """Add the shared timeout and request-count bounds."""

    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--max-requests", type=int, default=200)


def capture(args: argparse.Namespace) -> None:
    """Capture catalog, recommendation, mapping, and error-case responses."""

    origin = _normalize_origin(args.base_url)
    if args.expected_origin and _normalize_origin(args.expected_origin) != origin:
        raise BaselineError("--base-url does not match --expected-origin")
    output = args.output.resolve()
    if output.exists() and not args.force:
        raise BaselineError(f"{output} already exists; pass --force to replace it")

    # Discover the authoritative degree and university names from the live catalog.
    client = ReadOnlyClient(origin, args.timeout, args.max_requests)
    catalog = _require_status("catalog", client.get(f"{API_ROOT}/catalog"), 200)
    degrees, universities = _discover(catalog["body"])

    baseline: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "captured_at_utc": datetime.now(UTC).isoformat(),
        "endpoint_origin": origin,
        "tool": {
            "name": TOOL_NAME,
            "version": TOOL_VERSION,
            "limits": {
                "timeout_seconds": args.timeout,
                "max_requests": args.max_requests,
                "max_response_bytes": MAX_RESPONSE_BYTES,
            },
        },
        "capture_environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "git": _git_state(),
        },
        "catalog": catalog,
        "recommendations": {},
        "mappings": {},
        "error_cases": {},
    }

    # Capture one ranking response per discovered degree.
    for degree in degrees:
        case = client.get(f"{API_ROOT}/recommendations", {"degree": degree})
        baseline["recommendations"][degree] = _require_status(degree, case, 200)

    # Capture every discovered degree/university pair, including empty pairs.
    for degree in degrees:
        for university in universities:
            case = client.get(
                f"{API_ROOT}/mappings", {"degree": degree, "uni": university}
            )
            key = _pair_key(degree, university)
            baseline["mappings"][key] = _require_status(key, case, 200)

    # Capture representative validation and unknown-selection responses.
    for name, path, params, expected_status in _error_requests(degrees[0]):
        case = client.get(f"{API_ROOT}{path}", params)
        baseline["error_cases"][name] = _require_status(name, case, expected_status)

    baseline["request_count"] = client.request_count
    output.parent.mkdir(parents=True, exist_ok=True)
    _write_json_atomic(output, baseline)
    print(f"Wrote {output} ({client.request_count} read-only responses from {origin})")


def compare(args: argparse.Namespace) -> int:
    """Replay a baseline and report exact response differences."""

    baseline_path = args.baseline.resolve()
    report = args.report.resolve()
    if report == baseline_path:
        raise BaselineError("--report must not overwrite the expected baseline")
    baseline = _load_baseline(baseline_path)
    origin = _normalize_origin(args.base_url or baseline["endpoint_origin"])
    if args.expected_origin and _normalize_origin(args.expected_origin) != origin:
        raise BaselineError("--base-url does not match --expected-origin")

    # Derive the expected request set from the original catalog, not current data.
    degrees, universities = _discover(baseline["catalog"]["body"])
    client = ReadOnlyClient(origin, args.timeout, args.max_requests)
    differences: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []

    # Compare catalog, recommendations, mappings, and error cases in baseline order.
    _compare_case(client, "catalog", baseline["catalog"], differences, failures)
    for degree in degrees:
        expected = baseline["recommendations"].get(degree)
        if expected is None:
            failures.append(
                {"name": degree, "message": "baseline has no recommendation case"}
            )
            continue
        _compare_case(
            client, f"recommendations: {degree}", expected, differences, failures
        )
    for degree in degrees:
        for university in universities:
            key = _pair_key(degree, university)
            expected = baseline["mappings"].get(key)
            if expected is None:
                failures.append({"name": key, "message": "baseline has no mapping case"})
                continue
            _compare_case(client, f"mappings: {key}", expected, differences, failures)
    for name, expected in baseline["error_cases"].items():
        _compare_case(client, f"error: {name}", expected, differences, failures)

    _write_report(
        report,
        baseline_path=baseline_path,
        origin=origin,
        baseline=baseline,
        request_count=client.request_count,
        differences=differences,
        failures=failures,
    )
    print(
        f"Compared {client.request_count} requests against {baseline_path}: "
        f"{len(differences)} differences, {len(failures)} failures"
    )
    print(f"Wrote {report}")
    return 0 if not differences and not failures else 1


def _compare_case(
    client: ReadOnlyClient,
    name: str,
    expected: dict[str, Any],
    differences: list[dict[str, Any]],
    failures: list[dict[str, str]],
) -> None:
    """Replay one expected case and record any status or body difference."""

    request = expected.get("request")
    if not isinstance(request, dict) or request.get("method") != "GET":
        failures.append({"name": name, "message": "baseline request is not a GET"})
        return
    try:
        actual = client.get(request["path"], request.get("params"))
    except BaselineError as exc:
        failures.append({"name": name, "message": str(exc)})
        return

    # Compare status and the full JSON body so array order and optional fields count.
    if actual["status"] != expected["status"] or actual["body"] != expected["body"]:
        differences.append(
            {
                "name": name,
                "request": actual["request"],
                "expected_status": expected["status"],
                "actual_status": actual["status"],
                "expected_body": expected["body"],
                "actual_body": actual["body"],
            }
        )


def _error_requests(first_degree: str) -> tuple[tuple[str, str, dict[str, str], int], ...]:
    """Build the representative 404 and 422 cases for the first known degree."""

    return (
        ("missing_recommendation_degree", "/recommendations", {}, 422),
        ("missing_mapping_university", "/mappings", {"degree": first_degree}, 422),
        ("unknown_degree", "/recommendations", {"degree": UNKNOWN_DEGREE}, 404),
        (
            "unknown_university",
            "/mappings",
            {"degree": first_degree, "uni": UNKNOWN_UNIVERSITY},
            404,
        ),
    )


def _discover(body: Any) -> tuple[list[str], list[str]]:
    """Extract validated degree and university names from a catalog response."""

    if not isinstance(body, dict):
        raise BaselineError("catalog body must be a JSON object")
    degrees = _option_names(body.get("degrees"), "degrees")
    universities = _option_names(body.get("universities"), "universities")
    if not degrees or not universities:
        raise BaselineError("catalog must contain at least one degree and university")
    return degrees, universities


def _option_names(value: Any, label: str) -> list[str]:
    """Read unique non-empty option names and reject malformed catalog data."""

    if not isinstance(value, list):
        raise BaselineError(f"catalog {label} must be an array")
    names: list[str] = []
    for item in value:
        if not isinstance(item, dict) or not isinstance(item.get("name"), str):
            raise BaselineError(f"catalog {label} contains a malformed option")
        name = item["name"]
        if not name.strip() or name in names:
            raise BaselineError(f"catalog {label} contains a blank or duplicate name")
        names.append(name)
    return names


def _require_status(name: str, case: dict[str, Any], expected: int) -> dict[str, Any]:
    """Fail capture when the live endpoint does not return the contract status."""

    if case["status"] != expected:
        raise BaselineError(
            f"{name} returned status {case['status']}, expected {expected}"
        )
    return case


def _pair_key(degree: str, university: str) -> str:
    """Match the historical mapping key format for readable baselines."""

    return f"{degree} || {university}"


def _read_bounded(response: Any) -> bytes:
    """Read at most the configured response limit and reject oversized bodies."""

    raw = response.read(MAX_RESPONSE_BYTES + 1)
    if len(raw) > MAX_RESPONSE_BYTES:
        raise BaselineError(
            f"response body exceeds {MAX_RESPONSE_BYTES} bytes"
        )
    return raw


def _normalize_origin(value: str) -> str:
    """Validate an HTTP(S) origin without path, query, fragment, or credentials."""

    try:
        parsed = urlsplit(value.strip())
    except ValueError:
        raise BaselineError("endpoint URL is invalid") from None
    if parsed.scheme not in {"http", "https"}:
        raise BaselineError("endpoint URL must use http or https")
    if not parsed.hostname:
        raise BaselineError("endpoint URL must include a host")
    if parsed.username or parsed.password:
        raise BaselineError("endpoint URL must not contain credentials")
    if parsed.path not in {"", "/"} or parsed.query or parsed.fragment:
        raise BaselineError("endpoint URL must be a bare origin without a path")
    return f"{parsed.scheme}://{parsed.netloc}"


def _git_state() -> dict[str, Any]:
    """Record the local revision and worktree state without failing outside Git."""

    def run(*args: str) -> str | None:
        try:
            result = subprocess.run(
                ["git", "-C", str(REPO_ROOT), *args],
                check=False,
                capture_output=True,
                text=True,
            )
        except OSError:
            return None
        return result.stdout.strip() if result.returncode == 0 else None

    status = run("status", "--short")
    return {
        "revision": run("rev-parse", "HEAD"),
        "status_short": status.splitlines() if status else [],
    }


def _write_json_atomic(path: Path, value: dict[str, Any]) -> None:
    """Replace the baseline only after the complete JSON document is written."""

    temporary = path.with_name(f".{path.name}.tmp")
    try:
        temporary.write_text(
            json.dumps(value, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def _load_baseline(path: Path) -> dict[str, Any]:
    """Load and validate a versioned baseline document."""

    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise BaselineError(f"cannot read baseline {path}: {exc}") from None
    except json.JSONDecodeError as exc:
        raise BaselineError(f"baseline {path} is not valid JSON: {exc}") from None
    if not isinstance(value, dict) or value.get("schema_version") != SCHEMA_VERSION:
        raise BaselineError(f"baseline {path} has an unsupported schema version")
    if not isinstance(value.get("endpoint_origin"), str):
        raise BaselineError(f"baseline {path} has no endpoint origin")
    if not isinstance(value.get("catalog"), dict):
        raise BaselineError(f"baseline {path} has no catalog case")
    for key in ("recommendations", "mappings", "error_cases"):
        if not isinstance(value.get(key), dict):
            raise BaselineError(f"baseline {path} has no {key} object")
    return value


def _write_report(
    path: Path,
    baseline_path: Path,
    origin: str,
    baseline: dict[str, Any],
    request_count: int,
    differences: list[dict[str, Any]],
    failures: list[dict[str, str]],
) -> None:
    """Write a markdown comparison report without touching the baseline."""

    passed = not differences and not failures
    lines = [
        "# Post-deletion API baseline comparison",
        "",
        f"Generated: {datetime.now(UTC).isoformat(timespec='seconds')}",
        f"Endpoint: `{origin}`",
        f"Baseline: `{baseline_path}`",
        f"Baseline captured: {baseline.get('captured_at_utc', 'unknown')}",
        f"Requests: {request_count}",
        f"Result: {'PASS' if passed else 'FAIL'}",
        "",
        "## Summary",
        "",
        f"- Differences: {len(differences)}",
        f"- Request failures: {len(failures)}",
        "",
    ]

    # List concrete body or status differences with both versions.
    if differences:
        lines.extend(["## Differences", ""])
        for difference in differences:
            lines.extend(
                [
                    f"### {difference['name']}",
                    "",
                    f"Request: `{difference['request']['url']}`",
                    "",
                    f"Expected status: {difference['expected_status']}",
                    f"Actual status: {difference['actual_status']}",
                    "",
                    "Expected body:",
                    "",
                    "```json",
                    json.dumps(
                        difference["expected_body"], indent=2, ensure_ascii=False
                    ),
                    "```",
                    "",
                    "Actual body:",
                    "",
                    "```json",
                    json.dumps(difference["actual_body"], indent=2, ensure_ascii=False),
                    "```",
                    "",
                ]
            )
    else:
        lines.extend(["## Differences", "", "No response differences.", ""])

    # List requests that could not complete, which also fail the comparison.
    if failures:
        lines.extend(["## Request failures", ""])
        for failure in failures:
            lines.append(f"- **{failure['name']}**: {failure['message']}")
        lines.append("")
    else:
        lines.extend(["## Request failures", "", "None.", ""])

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
