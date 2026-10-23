"""Capture and compare read-only snapshots of the eight retained core tables.

Capture mode reads a fixed allowlist of tables and their retained columns in one
repeatable-read transaction. Compare mode checks exact rows, identifiers, and
sequence state for the same database, or normalized natural keys for databases
that were seeded independently. The utility never writes to the inspected
database and never stores connection credentials in its output.
"""

import argparse
import csv
import hashlib
import json
import os
import sys
from collections import Counter
from collections.abc import Iterable, Sequence
from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import psycopg
from psycopg import sql
from psycopg.conninfo import conninfo_to_dict, make_conninfo

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_VERSION = 1
TOOL_NAME = "snapshot_core_data"
TOOL_VERSION = "1.0"
REPORT_LIMIT = 5

# The allowlist is also the dependency order used by fixture generation.
CORE_TABLES: dict[str, tuple[str, ...]] = {
    "degrees": ("id", "name", "faculty", "full_title", "source_order"),
    "nus_modules": ("code", "name", "offering_faculty", "verified_units"),
    "degree_modules": ("degree_id", "module_code", "requirement_type"),
    "partner_universities": ("id", "name", "country", "city", "continent", "source_order"),
    "pu_modules": ("id", "code", "name", "partner_university_id", "verified_units"),
    "specializations": ("id", "degree_id", "name", "kind", "source_order"),
    "specialization_modules": ("specialization_id", "module_code"),
    "module_mappings": (
        "id",
        "nus_module_code",
        "pu_module_id",
        "source_order",
        "source_nus_title",
        "source_nus_units",
        "source_partner_title",
        "source_partner_units",
        "source_faculty",
        "source_page",
    ),
}

CORE_SEQUENCES = (
    "degrees_id_seq",
    "module_mappings_id_seq",
    "partner_universities_id_seq",
    "pu_modules_id_seq",
    "specializations_id_seq",
)


class SnapshotError(RuntimeError):
    """Raised when a snapshot cannot be captured or compared safely."""


def main(argv: list[str] | None = None) -> int:
    """Dispatch capture or comparison and return a process exit status."""

    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "capture":
            capture(args)
        else:
            return compare(args)
    except SnapshotError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


def _build_parser() -> argparse.ArgumentParser:
    """Create the capture and compare command-line interfaces."""

    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Capture reads one database and writes a snapshot plus optional source links.
    capture_parser = subparsers.add_parser("capture", help="capture a database snapshot")
    capture_parser.add_argument("--database-url")
    capture_parser.add_argument(
        "--target",
        help="confirmation label: 'local' for localhost, otherwise the project ref or host",
    )
    capture_parser.add_argument("--output", type=Path, required=True)
    capture_parser.add_argument(
        "--source-row-ids",
        type=Path,
        help="optional CSV export of module_mappings.id and source_row_id",
    )
    capture_parser.add_argument("--force", action="store_true")

    # Compare checks snapshots without opening a database or changing either file.
    compare_parser = subparsers.add_parser("compare", help="compare two snapshots")
    compare_parser.add_argument("--baseline", type=Path, required=True)
    compare_parser.add_argument("--candidate", type=Path, required=True)
    compare_parser.add_argument(
        "--mode",
        choices=("ids", "natural"),
        default="ids",
        help="ids compares identifiers and sequence state; natural ignores generated IDs",
    )
    compare_parser.add_argument("--report", type=Path)
    compare_parser.add_argument("--json", action="store_true")
    return parser


def capture(args: argparse.Namespace) -> None:
    """Capture a read-only snapshot and the optional mapping recovery export."""

    database_url = args.database_url or os.environ.get("SNAPSHOT_DATABASE_URL")
    if not database_url:
        raise SnapshotError("--database-url or SNAPSHOT_DATABASE_URL is required")
    target_label = _validate_target(database_url, args.target)
    output = args.output.resolve()
    if output.exists() and not args.force:
        raise SnapshotError(f"{output} already exists; pass --force to replace it")
    _protect_remote_output(output, target_label, "--output")
    if args.source_row_ids is not None:
        source_path = args.source_row_ids.resolve()
        if source_path == output:
            raise SnapshotError("--output and --source-row-ids must be different files")
        _protect_remote_output(source_path, target_label, "--source-row-ids")
        if source_path.exists() and not args.force:
            raise SnapshotError(f"{source_path} already exists; pass --force to replace it")

    # Read every table and sequence from one consistent transaction.
    snapshot, source_rows = read_snapshot(
        database_url, include_source_row_ids=args.source_row_ids is not None
    )
    _write_json_atomic(output, snapshot)
    digest = _file_sha256(output)

    # Keep the source-row recovery mapping in a separate, ordered file.
    if source_rows is not None:
        _write_csv_atomic(
            args.source_row_ids.resolve(),
            ("id", "source_row_id"),
            source_rows,
        )
        print(f"Wrote {args.source_row_ids.resolve()} ({len(source_rows)} mapping links)")
    table_rows = sum(table["row_count"] for table in snapshot["tables"].values())
    print(
        f"Wrote {output} ({table_rows} rows across {len(CORE_TABLES)} tables from "
        f"{snapshot['target']['host']}/{snapshot['target']['database']}, sha256 {digest})"
    )


def compare(args: argparse.Namespace) -> int:
    """Compare two snapshots and optionally write a markdown report."""

    baseline_path = args.baseline.resolve()
    candidate_path = args.candidate.resolve()
    if args.report is not None:
        report_path = args.report.resolve()
        if report_path in {baseline_path, candidate_path}:
            raise SnapshotError("--report must not overwrite either snapshot")
    else:
        report_path = None

    baseline = _load_snapshot(baseline_path)
    candidate = _load_snapshot(candidate_path)
    result = _compare_snapshots(baseline, candidate, args.mode)
    result["baseline"] = str(baseline_path)
    result["candidate"] = str(candidate_path)

    if report_path is not None:
        _write_report(report_path, result)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        _print_comparison(result)
    return 0 if result["equal"] else 1


def read_snapshot(
    database_url: str, *, include_source_row_ids: bool = False
) -> tuple[dict[str, Any], list[tuple[int, int | None]] | None]:
    """Read the fixed core allowlist in one repeatable-read transaction."""

    try:
        with _connect(database_url) as connection:
            connection.read_only = True
            connection.isolation_level = psycopg.IsolationLevel.REPEATABLE_READ
            with connection.transaction():
                server_version = str(
                    connection.execute("show server_version").fetchone()[0]
                )
                tables = _read_tables(connection)
                sequences = _read_sequences(connection)
                migrations = _read_migrations(connection)
                source_rows = (
                    _read_source_row_ids(connection)
                    if include_source_row_ids
                    else None
                )
    except psycopg.Error as exc:
        raise SnapshotError(_database_error_message(exc)) from None

    snapshot = {
        "schema_version": SCHEMA_VERSION,
        "captured_at_utc": datetime.now(UTC).isoformat(),
        "tool": {"name": TOOL_NAME, "version": TOOL_VERSION},
        "target": {
            **_target_summary(database_url),
            "server_version": server_version,
        },
        "migration_versions": migrations,
        "tables": tables,
        "sequences": sequences,
        "mapping_multiplicity": _mapping_multiplicity(tables),
    }
    return snapshot, source_rows


def _read_tables(connection: psycopg.Connection) -> dict[str, Any]:
    """Read every allowlisted table using explicit columns and stable row order."""

    tables: dict[str, Any] = {}
    for table, columns in CORE_TABLES.items():
        # Column and table names come only from the local allowlist.
        query = sql.SQL("select {} from public.{}").format(
            sql.SQL(", ").join(sql.Identifier(column) for column in columns),
            sql.Identifier(table),
        )
        rows = [
            {
                column: _normalize_value(value)
                for column, value in zip(columns, row, strict=True)
            }
            for row in connection.execute(query)
        ]
        rows.sort(key=_canonical_json)
        tables[table] = {
            "columns": list(columns),
            "row_count": len(rows),
            "fingerprint": _fingerprint(table, rows),
            "rows": rows,
        }
    return tables


def _read_sequences(connection: psycopg.Connection) -> dict[str, dict[str, Any]]:
    """Read state for sequences owned by the retained core tables."""

    rows = connection.execute(
        """
        select sequencename, last_value, start_value, increment_by,
               min_value, max_value, cycle
        from pg_sequences
        where schemaname = 'public' and sequencename = any(%s)
        order by sequencename
        """,
        (list(CORE_SEQUENCES),),
    ).fetchall()
    return {
        str(name): {
            "last_value": _normalize_value(last_value),
            "start_value": _normalize_value(start_value),
            "increment_by": _normalize_value(increment_by),
            "min_value": _normalize_value(min_value),
            "max_value": _normalize_value(max_value),
            "cycle": _normalize_value(cycle),
        }
        for name, last_value, start_value, increment_by, min_value, max_value, cycle in rows
    }


def _read_migrations(connection: psycopg.Connection) -> list[dict[str, str]]:
    """Read Supabase migration versions when the target records them."""

    exists = connection.execute(
        "select to_regclass('supabase_migrations.schema_migrations')"
    ).fetchone()[0]
    if exists is None:
        return []
    rows = connection.execute(
        """
        select version, name
        from supabase_migrations.schema_migrations
        order by version
        """
    ).fetchall()
    return [{"version": str(version), "name": str(name)} for version, name in rows]


def _read_source_row_ids(connection: psycopg.Connection) -> list[tuple[int, int | None]]:
    """Read mapping IDs and their optional pre-removal provenance links."""

    present = connection.execute(
        """
        select 1
        from information_schema.columns
        where table_schema = 'public'
          and table_name = 'module_mappings'
          and column_name = 'source_row_id'
        """
    ).fetchone()
    if present is None:
        raise SnapshotError(
            "module_mappings.source_row_id is absent; cannot export recovery links"
        )
    rows = connection.execute(
        "select id, source_row_id from public.module_mappings order by id"
    ).fetchall()
    return [
        (int(mapping_id), int(source_row_id) if source_row_id is not None else None)
        for mapping_id, source_row_id in rows
    ]


def _compare_snapshots(
    baseline: dict[str, Any], candidate: dict[str, Any], mode: str
) -> dict[str, Any]:
    """Compare all allowlisted table rows and, for IDs mode, sequence state."""

    baseline_tables = baseline["tables"]
    candidate_tables = candidate["tables"]
    result: dict[str, Any] = {
        "mode": mode,
        "equal": True,
        "tables": {},
        "sequences": {},
        "mapping_multiplicity": {
            "baseline": baseline["mapping_multiplicity"],
            "candidate": candidate["mapping_multiplicity"],
        },
    }

    # Compare every table as a multiset so repeated mapping rows stay significant.
    for table in CORE_TABLES:
        baseline_rows = _comparison_rows(table, baseline_tables, mode)
        candidate_rows = _comparison_rows(table, candidate_tables, mode)
        missing, extra = _multiset_difference(baseline_rows, candidate_rows)
        fingerprint = _fingerprint(table, baseline_rows)
        candidate_fingerprint = _fingerprint(table, candidate_rows)
        table_equal = not missing["count"] and not extra["count"]
        result["equal"] = result["equal"] and table_equal
        result["tables"][table] = {
            "equal": table_equal,
            "baseline_count": len(baseline_rows),
            "candidate_count": len(candidate_rows),
            "baseline_fingerprint": fingerprint,
            "candidate_fingerprint": candidate_fingerprint,
            "missing": missing,
            "extra": extra,
        }

    # Sequence state is meaningful only for snapshots of the same database.
    if mode == "ids":
        sequence_result = _compare_sequences(
            baseline.get("sequences", {}), candidate.get("sequences", {})
        )
        result["sequences"] = sequence_result
        result["equal"] = result["equal"] and sequence_result["equal"]
    else:
        result["sequences"] = {
            "compared": False,
            "reason": "natural-key mode ignores generated IDs and sequence state",
        }
    return result


def _comparison_rows(
    table: str, tables: dict[str, Any], mode: str
) -> list[dict[str, Any]]:
    """Return exact rows for ID mode or natural-key rows for independent databases."""

    if table not in tables:
        raise SnapshotError(f"snapshot has no {table} table")
    rows = tables[table]["rows"]
    if mode == "ids":
        return rows
    return _natural_rows(table, tables, _natural_context(tables))


def _natural_context(tables: dict[str, Any]) -> dict[str, dict[Any, Any]]:
    """Build ID-to-natural-key lookups from one snapshot."""

    try:
        degrees = {row["id"]: row["name"] for row in tables["degrees"]["rows"]}
        universities = {
            row["id"]: row["name"] for row in tables["partner_universities"]["rows"]
        }
        partner_modules = {
            row["id"]: {
                "university": universities[row["partner_university_id"]],
                "code": row["code"],
            }
            for row in tables["pu_modules"]["rows"]
        }
        specializations = {
            row["id"]: {
                "degree": degrees[row["degree_id"]],
                "name": row["name"],
            }
            for row in tables["specializations"]["rows"]
        }
    except (KeyError, TypeError) as exc:
        raise SnapshotError("snapshot contains an unresolved foreign key") from exc
    return {
        "degrees": degrees,
        "universities": universities,
        "partner_modules": partner_modules,
        "specializations": specializations,
    }


def _natural_rows(
    table: str, tables: dict[str, Any], context: dict[str, dict[Any, Any]]
) -> list[dict[str, Any]]:
    """Replace generated IDs with stable natural keys for one table."""

    try:
        if table == "degrees":
            return [_without(row, "id") for row in tables[table]["rows"]]
        if table == "nus_modules":
            return [dict(row) for row in tables[table]["rows"]]
        if table == "degree_modules":
            return [
                {
                    "degree": context["degrees"][row["degree_id"]],
                    "module_code": row["module_code"],
                    "requirement_type": row["requirement_type"],
                }
                for row in tables[table]["rows"]
            ]
        if table == "partner_universities":
            return [_without(row, "id") for row in tables[table]["rows"]]
        if table == "pu_modules":
            return [
                {
                    "university": context["universities"][row["partner_university_id"]],
                    "code": row["code"],
                    "name": row["name"],
                    "verified_units": row["verified_units"],
                }
                for row in tables[table]["rows"]
            ]
        if table == "specializations":
            return [
                {
                    "degree": context["degrees"][row["degree_id"]],
                    "name": row["name"],
                    "kind": row["kind"],
                    "source_order": row["source_order"],
                }
                for row in tables[table]["rows"]
            ]
        if table == "specialization_modules":
            return [
                {
                    "degree": context["specializations"][row["specialization_id"]][
                        "degree"
                    ],
                    "specialization": context["specializations"][
                        row["specialization_id"]
                    ]["name"],
                    "module_code": row["module_code"],
                }
                for row in tables[table]["rows"]
            ]
        if table == "module_mappings":
            return [
                {
                    **_without(row, "id", "pu_module_id"),
                    "university": context["partner_modules"][row["pu_module_id"]][
                        "university"
                    ],
                    "partner_module_code": context["partner_modules"][
                        row["pu_module_id"]
                    ]["code"],
                }
                for row in tables[table]["rows"]
            ]
    except (KeyError, TypeError) as exc:
        raise SnapshotError(f"snapshot {table} contains an unresolved foreign key") from exc
    raise SnapshotError(f"no natural-key rule for {table}")


def _without(row: dict[str, Any], *keys: str) -> dict[str, Any]:
    """Copy a row without the generated key columns."""

    return {key: value for key, value in row.items() if key not in keys}


def _compare_sequences(
    baseline: dict[str, Any], candidate: dict[str, Any]
) -> dict[str, Any]:
    """Compare sequence names and values for two snapshots of one database."""

    names = sorted(set(baseline) | set(candidate))
    changed = [
        name
        for name in names
        if baseline.get(name) != candidate.get(name)
    ]
    return {
        "equal": not changed,
        "baseline": baseline,
        "candidate": candidate,
        "changed": changed,
        "missing": sorted(set(baseline) - set(candidate)),
        "extra": sorted(set(candidate) - set(baseline)),
    }


def _mapping_multiplicity(tables: dict[str, Any]) -> dict[str, Any]:
    """Summarize repeated course pairs without collapsing duplicate rows."""

    context = _natural_context(tables)
    pairs: Counter[tuple[str, str, str]] = Counter()
    for row in tables["module_mappings"]["rows"]:
        partner = context["partner_modules"].get(row["pu_module_id"])
        if partner is None:
            raise SnapshotError("module_mappings contains an unresolved partner module")
        pairs[
            (str(partner["university"]), str(row["nus_module_code"]), str(partner["code"]))
        ] += 1
    duplicates = [
        {
            "university": university,
            "nus_module_code": nus_code,
            "partner_module_code": partner_code,
            "count": count,
        }
        for (university, nus_code, partner_code), count in sorted(
            pairs.items(), key=lambda item: (-item[1], item[0])
        )
        if count > 1
    ]
    return {
        "rows": len(tables["module_mappings"]["rows"]),
        "distinct_course_pairs": len(pairs),
        "duplicate_course_pair_rows": sum(count - 1 for count in pairs.values()),
        "max_rows_per_course_pair": max(pairs.values(), default=0),
        "duplicate_samples": duplicates[:REPORT_LIMIT],
    }


def _multiset_difference(
    baseline: Sequence[dict[str, Any]], candidate: Sequence[dict[str, Any]]
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Return missing and extra rows while preserving duplicate row counts."""

    baseline_rows = Counter(_canonical_json(row) for row in baseline)
    candidate_rows = Counter(_canonical_json(row) for row in candidate)
    missing_counter = baseline_rows - candidate_rows
    extra_counter = candidate_rows - baseline_rows
    return (
        _difference_summary(missing_counter),
        _difference_summary(extra_counter),
    )


def _difference_summary(difference: Counter[str]) -> dict[str, Any]:
    """Convert a multiset difference to a bounded, report-friendly summary."""

    samples = [json.loads(value) for value in list(difference)[:REPORT_LIMIT]]
    return {"count": sum(difference.values()), "samples": samples}


def _normalize_value(value: Any) -> Any:
    """Convert database values into stable JSON-compatible values."""

    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float):
        return value
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, dict):
        return {
            str(key): _normalize_value(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    if isinstance(value, (list, tuple)):
        return [_normalize_value(item) for item in value]
    if isinstance(value, (bytes, bytearray, memoryview)):
        return bytes(value).hex()
    return str(value)


def _canonical_json(value: Any) -> str:
    """Serialize a value with stable key order and no insignificant whitespace."""

    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _fingerprint(table: str, rows: Iterable[dict[str, Any]]) -> str:
    """Fingerprint a table's ordered canonical row multiset."""

    digest = hashlib.sha256()
    digest.update(f"{table}\n".encode())
    for row in sorted(rows, key=_canonical_json):
        digest.update(_canonical_json(row).encode("utf-8"))
        digest.update(b"\n")
    return f"sha256:{digest.hexdigest()}"


def _connect(database_url: str) -> psycopg.Connection:
    """Open a secret-safe read-only connection with local-friendly TLS defaults."""

    try:
        params = conninfo_to_dict(database_url)
        host = str(params.get("host") or "").lower()
        local = host in {"localhost", "127.0.0.1", "::1"} or host.startswith("/")
        if not local and params.get("sslmode") not in {
            "require",
            "verify-ca",
            "verify-full",
        }:
            params["sslmode"] = "require"
        params.setdefault("application_name", "nus-exchange-planner-snapshot")
        params.setdefault("connect_timeout", "15")
        return psycopg.connect(
            make_conninfo(**params),
            autocommit=False,
            prepare_threshold=None,
        )
    except (psycopg.Error, ValueError) as exc:
        raise SnapshotError(_database_error_message(exc)) from None


def _database_error_message(exc: Exception) -> str:
    """Keep driver failures actionable without echoing connection strings."""

    diagnostic = getattr(exc, "diag", None)
    detail = getattr(diagnostic, "message_primary", None) if diagnostic else None
    sqlstate = getattr(exc, "sqlstate", None)
    parts = [type(exc).__name__]
    if sqlstate:
        parts.append(str(sqlstate))
    if detail:
        parts.append(detail)
    return "Database operation failed: " + " - ".join(parts)


def _project_ref_from_url(database_url: str) -> str | None:
    """Read a Supabase project ref from the host without exposing credentials."""

    parts = urlsplit(database_url)
    host = (parts.hostname or "").lower()
    username = parts.username or ""
    if host.endswith(".pooler.supabase.com") and "." in username:
        return username.split(".", 1)[1]
    if host.startswith("db.") and host.endswith(".supabase.co"):
        return host.split(".")[1]
    return None


def _expected_target_label(database_url: str) -> str:
    """Return the confirmation label a database URL requires."""

    project_ref = _project_ref_from_url(database_url)
    if project_ref:
        return project_ref
    host = (urlsplit(database_url).hostname or "").lower()
    if host in {"localhost", "127.0.0.1", "::1"} or host.startswith("/"):
        return "local"
    return host


def _validate_target(database_url: str, target: str | None) -> str:
    """Require explicit confirmation for every non-local target."""

    expected = _expected_target_label(database_url)
    if target is None:
        if expected != "local":
            raise SnapshotError(
                f"remote target requires --target {expected!r}"
            )
        return expected
    if target != expected:
        raise SnapshotError(f"Target confirmation mismatch: expected {expected!r}, got {target!r}")
    return expected


def _target_summary(database_url: str) -> dict[str, str | None]:
    """Describe a target without exposing usernames, passwords, or query strings."""

    parts = urlsplit(database_url)
    return {
        "host": parts.hostname,
        "database": parts.path.lstrip("/") or None,
        "project_ref": _project_ref_from_url(database_url),
    }


def _protect_remote_output(path: Path, target_label: str, option: str) -> None:
    """Keep live remote snapshots outside the repository by default."""

    if target_label == "local":
        return
    try:
        path.relative_to(REPO_ROOT)
    except ValueError:
        return
    raise SnapshotError(f"{option} must be outside the repository for a remote target")


def _write_json_atomic(path: Path, value: dict[str, Any]) -> None:
    """Replace a snapshot only after the full JSON document is written."""

    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    try:
        temporary.write_text(
            json.dumps(value, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def _write_csv_atomic(
    path: Path, header: tuple[str, ...], rows: Sequence[tuple[Any, ...]]
) -> None:
    """Write a small ordered CSV without leaving a partial recovery file."""

    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    try:
        with temporary.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(header)
            writer.writerows(rows)
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def _load_snapshot(path: Path) -> dict[str, Any]:
    """Load a versioned snapshot and verify every required table is present."""

    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise SnapshotError(f"cannot read snapshot {path}: {exc}") from None
    except json.JSONDecodeError as exc:
        raise SnapshotError(f"snapshot {path} is not valid JSON: {exc}") from None
    if not isinstance(value, dict) or value.get("schema_version") != SCHEMA_VERSION:
        raise SnapshotError(f"snapshot {path} has an unsupported schema version")
    tables = value.get("tables")
    if not isinstance(tables, dict):
        raise SnapshotError(f"snapshot {path} has no tables object")
    missing = [table for table in CORE_TABLES if table not in tables]
    if missing:
        raise SnapshotError(f"snapshot {path} is missing tables: {', '.join(missing)}")
    return value


def _print_comparison(result: dict[str, Any]) -> None:
    """Print a concise comparison summary suitable for terminal evidence."""

    print(
        f"Compared {result['baseline']} to {result['candidate']} "
        f"in {result['mode']} mode: {'PASS' if result['equal'] else 'FAIL'}"
    )
    for table, detail in result["tables"].items():
        print(
            f"  {table}: {detail['baseline_count']} -> {detail['candidate_count']} rows, "
            f"missing {detail['missing']['count']}, extra {detail['extra']['count']}"
        )
    if result["mode"] == "ids":
        sequences = result["sequences"]
        print(
            f"  sequences: {'match' if sequences['equal'] else 'changed'}"
            + (f" ({', '.join(sequences['changed'])})" if sequences["changed"] else "")
        )


def _write_report(path: Path, result: dict[str, Any]) -> None:
    """Write a markdown comparison report with bounded difference samples."""

    lines = [
        "# Core data snapshot comparison",
        "",
        f"Generated: {datetime.now(UTC).isoformat(timespec='seconds')}",
        f"Baseline: `{result['baseline']}`",
        f"Candidate: `{result['candidate']}`",
        f"Mode: `{result['mode']}`",
        f"Result: {'PASS' if result['equal'] else 'FAIL'}",
        "",
        "## Tables",
        "",
        "| Table | Baseline | Candidate | Missing | Extra | Result |",
        "| --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for table, detail in result["tables"].items():
        lines.append(
            f"| `{table}` | {detail['baseline_count']} | {detail['candidate_count']} | "
            f"{detail['missing']['count']} | {detail['extra']['count']} | "
            f"{'PASS' if detail['equal'] else 'FAIL'} |"
        )

    # Record sequence state only when IDs and sequence values are comparable.
    lines.extend(["", "## Sequences", ""])
    if result["mode"] == "ids":
        sequences = result["sequences"]
        lines.append(f"Result: {'PASS' if sequences['equal'] else 'FAIL'}")
        if sequences["changed"]:
            lines.append("")
            lines.append(f"Changed: {', '.join(sequences['changed'])}")
    else:
        lines.append(result["sequences"]["reason"])

    # Show duplicate course-pair counts so repeated mappings are not overlooked.
    baseline_multiplicity = result["mapping_multiplicity"]["baseline"]
    candidate_multiplicity = result["mapping_multiplicity"]["candidate"]
    baseline_duplicates = baseline_multiplicity["duplicate_course_pair_rows"]
    candidate_duplicates = candidate_multiplicity["duplicate_course_pair_rows"]
    baseline_maximum = baseline_multiplicity["max_rows_per_course_pair"]
    candidate_maximum = candidate_multiplicity["max_rows_per_course_pair"]
    lines.extend(
        [
            "",
            "## Mapping multiplicity",
            "",
            f"- Baseline rows: {baseline_multiplicity['rows']}",
            f"- Candidate rows: {candidate_multiplicity['rows']}",
            f"- Baseline duplicate pair rows: {baseline_duplicates}",
            f"- Candidate duplicate pair rows: {candidate_duplicates}",
            f"- Baseline maximum rows per pair: {baseline_maximum}",
            f"- Candidate maximum rows per pair: {candidate_maximum}",
            "",
        ]
    )

    # Include a bounded sample of missing and extra rows for each failed table.
    lines.extend(["## Differences", ""])
    failed_tables = [
        (table, detail)
        for table, detail in result["tables"].items()
        if not detail["equal"]
    ]
    if not failed_tables:
        lines.append("No table differences.")
    for table, detail in failed_tables:
        lines.extend([f"### `{table}`", ""])
        for label in ("missing", "extra"):
            sample = detail[label]["samples"]
            if not sample:
                continue
            lines.extend(
                [
                    f"{label.capitalize()} rows ({detail[label]['count']} total):",
                    "",
                    "```json",
                    json.dumps(sample, indent=2, ensure_ascii=False),
                    "```",
                    "",
                ]
            )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _file_sha256(path: Path) -> str:
    """Return the SHA-256 digest of a completed file."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


if __name__ == "__main__":
    sys.exit(main())
