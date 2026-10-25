"""Read-only data audit for the exchange enhancement migration (dry-run).

Reports distinct legacy faculty labels, orphan relations, missing geography,
and university coverage for the core catalog tables, plus the state of the
new enhancement relations when they already exist. Writes a deterministic
markdown dry-run report; the database is only read and no credentials are
stored in the output.
"""

import argparse
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import psycopg
from psycopg.conninfo import conninfo_to_dict, make_conninfo

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ALIASES = REPO_ROOT / "data" / "exchange-enhancements" / "faculty-aliases.json"

# Core tables are fixed; enhancement tables/columns may predate the migration.
CORE_TABLES = (
    "degrees",
    "nus_modules",
    "degree_modules",
    "specializations",
    "specialization_modules",
    "partner_universities",
    "pu_modules",
    "module_mappings",
)
ENHANCEMENT_TABLES = ("faculties", "degree_faculties", "faculty_partner_universities")
NEW_COLUMNS = (
    ("nus_modules", "faculty_id"),
    ("partner_universities", "image"),
    ("partner_universities", "website"),
    ("partner_universities", "image_attribution"),
)


class AuditError(RuntimeError):
    """Raised when the audit cannot inspect the database safely."""


def main(argv: list[str] | None = None) -> int:
    """Run the audit and write the markdown dry-run report."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--database-url",
        help="PostgreSQL URL; defaults to DATABASE_URL or IMPORT_DATABASE_URL",
    )
    parser.add_argument(
        "--aliases",
        type=Path,
        default=None,
        help="optional reviewed faculty alias file used for candidate mappings",
    )
    parser.add_argument(
        "--target",
        help="confirmation label for the inspected target, recorded in the report",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="markdown report path; omit to print the report on stdout",
    )
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)

    database_url = (
        args.database_url or os.environ.get("DATABASE_URL") or os.environ.get("IMPORT_DATABASE_URL")
    )
    if not database_url:
        parser.error("requires --database-url, DATABASE_URL, or IMPORT_DATABASE_URL")

    aliases_path = args.aliases
    if aliases_path is None and DEFAULT_ALIASES.is_file():
        aliases_path = DEFAULT_ALIASES

    try:
        aliases = _load_aliases(aliases_path) if aliases_path else None
        audit = run_audit(database_url, aliases)
    except (AuditError, psycopg.Error, OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    report = render_report(audit, target_label=args.target)
    if args.output is not None:
        output = args.output.resolve()
        if output.exists() and not args.force:
            print(f"error: {output} already exists; pass --force to replace it", file=sys.stderr)
            return 1
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(report, encoding="utf-8")
        print(f"Wrote {output}")
    else:
        print(report)
    return 0 if audit["ok"] else 1


def run_audit(database_url: str, aliases: dict[str, str] | None = None) -> dict[str, Any]:
    """Collect every audit section in one read-only repeatable-read transaction."""

    with _connect(database_url) as connection:
        connection.read_only = True
        connection.isolation_level = psycopg.IsolationLevel.REPEATABLE_READ
        with connection.transaction():
            cur = connection.cursor()

            # Row counts for every core table.
            row_counts: dict[str, int] = {}
            for table in CORE_TABLES:
                cur.execute(f"select count(*) from public.{table}")
                row_counts[table] = int(cur.fetchone()[0])

            # New enhancement objects are optional: record presence and size.
            enhancement_tables: dict[str, dict[str, Any]] = {}
            for table in ENHANCEMENT_TABLES:
                cur.execute("select to_regclass(%s) is not null", (f"public.{table}",))
                present = bool(cur.fetchone()[0])
                rows = None
                if present:
                    cur.execute(f"select count(*) from public.{table}")
                    rows = int(cur.fetchone()[0])
                enhancement_tables[table] = {"present": present, "rows": rows}
            new_columns: dict[str, bool] = {}
            for table, column in NEW_COLUMNS:
                cur.execute(
                    """
                    select exists (
                      select 1 from information_schema.columns
                      where table_schema = 'public' and table_name = %s and column_name = %s
                    )
                    """,
                    (table, column),
                )
                new_columns[f"{table}.{column}"] = bool(cur.fetchone()[0])

            # Distinct legacy faculty labels from both legacy text columns.
            cur.execute(
                """
                select 'degrees' as source, faculty, count(*)
                from public.degrees group by faculty
                union all
                select 'nus_modules', faculty, count(*)
                from public.nus_modules group by faculty
                order by 2 nulls last, 1
                """
            )
            faculty_labels = [
                {"source": source, "label": label, "rows": int(rows)}
                for source, label, rows in cur.fetchall()
            ]

            # Orphan rows are impossible under the foreign keys; count them anyway.
            cur.execute(
                """
                select
                  (select count(*) from public.degree_modules dm
                     where not exists (select 1 from public.degrees d where d.id = dm.degree_id)
                        or not exists (
                          select 1 from public.nus_modules n where n.code = dm.module_code)),
                  (select count(*) from public.specializations s
                     where not exists (select 1 from public.degrees d where d.id = s.degree_id)),
                  (select count(*) from public.specialization_modules sm
                     where not exists (
                       select 1 from public.specializations p where p.id = sm.specialization_id)
                        or not exists (
                          select 1 from public.nus_modules n where n.code = sm.module_code)),
                  (select count(*) from public.pu_modules p
                     where not exists (
                       select 1 from public.partner_universities u where u.id = p.partner_university_id)),
                  (select count(*) from public.module_mappings mm
                     where not exists (
                       select 1 from public.nus_modules n where n.code = mm.nus_module_code)
                        or not exists (
                          select 1 from public.pu_modules p where p.id = mm.pu_module_id))
                """
            )
            orphans = {
                name: int(value)
                for name, value in zip(
                    (
                        "degree_modules",
                        "specializations",
                        "specialization_modules",
                        "pu_modules",
                        "module_mappings",
                    ),
                    cur.fetchone(),
                )
            }
            # Enhancement orphans only exist once their tables do.
            enhancement_orphans: dict[str, int] = {}
            if enhancement_tables["faculties"]["present"]:
                cur.execute(
                    """
                    select
                      (select count(*) from public.degree_faculties df
                         where not exists (select 1 from public.faculties f where f.id = df.faculty_id)
                            or not exists (select 1 from public.degrees d where d.id = df.degree_id)),
                      (select count(*) from public.faculty_partner_universities fpu
                         where not exists (
                           select 1 from public.faculties f where f.id = fpu.faculty_id)
                            or not exists (
                              select 1 from public.partner_universities u
                              where u.id = fpu.partner_university_id))
                    """
                )
                df_orphans, fpu_orphans = cur.fetchone()
                enhancement_orphans = {
                    "degree_faculties": int(df_orphans),
                    "faculty_partner_universities": int(fpu_orphans),
                }
                if new_columns["nus_modules.faculty_id"]:
                    cur.execute(
                        """
                        select count(*) from public.nus_modules n
                        where n.faculty_id is not null
                          and not exists (select 1 from public.faculties f where f.id = n.faculty_id)
                        """
                    )
                    enhancement_orphans["nus_modules.faculty_id"] = int(cur.fetchone()[0])

            # Universities whose geography is partially unknown.
            cur.execute(
                """
                select name, country, city, continent
                from public.partner_universities
                where city is null or continent is null
                order by id
                """
            )
            missing_geography = [
                {"name": name, "country": country, "city": city, "continent": continent}
                for name, country, city, continent in cur.fetchall()
            ]

            # Coverage per university: modules, mapping rows, and mapped degrees.
            cur.execute(
                """
                select u.name, u.country, u.city, u.continent,
                  (select count(*) from public.pu_modules p
                     where p.partner_university_id = u.id),
                  (select count(*) from public.module_mappings mm
                     join public.pu_modules p on p.id = mm.pu_module_id
                     where p.partner_university_id = u.id),
                  (select count(distinct dm.degree_id)
                     from public.degree_modules dm
                     join public.module_mappings mm on mm.nus_module_code = dm.module_code
                     join public.pu_modules p on p.id = mm.pu_module_id
                     where p.partner_university_id = u.id)
                from public.partner_universities u
                order by u.name collate "C"
                """
            )
            coverage = [
                {
                    "name": name,
                    "country": country,
                    "city": city,
                    "continent": continent,
                    "pu_modules": int(pu),
                    "mapping_rows": int(rows),
                    "mapped_degrees": int(degs),
                }
                for name, country, city, continent, pu, rows, degs in cur.fetchall()
            ]

            audit: dict[str, Any] = {
                "generated_at_utc": datetime.now(UTC).isoformat(timespec="seconds"),
                "target": _target_summary(database_url),
                "row_counts": row_counts,
                "enhancement_tables": enhancement_tables,
                "new_columns": new_columns,
                "faculty_labels": faculty_labels,
                "candidate_mappings": _candidate_mappings(faculty_labels, aliases),
                "orphans": orphans,
                "enhancement_orphans": enhancement_orphans,
                "missing_geography": missing_geography,
                "university_coverage": coverage,
            }
            # The audit passes when referential integrity holds and core data exists.
            audit["ok"] = (
                sum(orphans.values()) == 0
                and sum(enhancement_orphans.values()) == 0
                and row_counts["degrees"] > 0
                and row_counts["partner_universities"] > 0
            )
            return audit


def _candidate_mappings(
    faculty_labels: list[dict[str, Any]], aliases: dict[str, str] | None
) -> dict[str, Any]:
    """Deterministically map each distinct legacy label to a canonical faculty.

    Without a reviewed alias file the canonical name is the trimmed label
    itself. Variants (whitespace or case) are flagged instead of silently
    merged, and a label absent from the alias file is flagged unresolved.
    """

    labels = sorted(
        {row["label"] for row in faculty_labels if row["label"] is not None},
        key=str.casefold,
    )
    null_counts = sum(row["rows"] for row in faculty_labels if row["label"] is None)
    folded = {label.casefold() for label in labels}
    mappings: list[dict[str, Any]] = []
    for label in labels:
        flags: list[str] = []
        if label != label.strip():
            flags.append("whitespace variant")
        if any(other != label and other.casefold() == label.casefold() for other in labels):
            flags.append("case variant")
        canonical = label.strip()
        if aliases is not None:
            canonical = aliases.get(label.casefold(), canonical)
            if label.casefold() not in aliases:
                flags.append("missing from alias file")
        mappings.append(
            {"label": label, "canonical": canonical, "flags": sorted(flags)}
        )
    return {
        "mappings": mappings,
        "null_label_rows": null_counts,
        "casefold_collisions": len(labels) - len(folded),
    }


def _connect(database_url: str) -> psycopg.Connection:
    """Open a secret-safe read-only connection with local-friendly TLS defaults."""

    try:
        params = conninfo_to_dict(database_url)
        host = str(params.get("host") or "").lower()
        local = host in {"localhost", "127.0.0.1", "::1"} or host.startswith("/")
        if not local and params.get("sslmode") not in {"require", "verify-ca", "verify-full"}:
            params["sslmode"] = "require"
        params.setdefault("application_name", "nus-exchange-planner-audit")
        params.setdefault("connect_timeout", "15")
        return psycopg.connect(
            make_conninfo(**params),
            autocommit=False,
            prepare_threshold=None,
        )
    except (psycopg.Error, ValueError) as exc:
        diagnostic = getattr(exc, "diag", None)
        detail = getattr(diagnostic, "message_primary", None) if diagnostic else None
        message = str(detail or exc).splitlines()[0]
        raise AuditError(f"database operation failed: {message}") from None


def _load_aliases(path: Path) -> dict[str, str]:
    """Map each reviewed label (casefolded) to its canonical faculty name."""

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AuditError(f"cannot read alias file {path}: {exc}") from None
    if not isinstance(raw, dict) or raw.get("schema_version") != 1:
        raise AuditError(f"alias file {path} has an unsupported schema version")
    faculties = raw.get("faculties")
    if not isinstance(faculties, list):
        raise AuditError("alias file must contain a faculties list")
    mapping: dict[str, str] = {}
    for entry in faculties:
        name = entry.get("name")
        if not isinstance(name, str) or not name.strip():
            raise AuditError("alias entries need a nonblank canonical name")
        aliases = entry.get("aliases", [])
        if not isinstance(aliases, list) or not all(isinstance(a, str) for a in aliases):
            raise AuditError(f"aliases for {name!r} must be a list of strings")
        for label in (name, *aliases):
            key = label.casefold()
            if key in mapping and mapping[key] != name:
                raise AuditError(f"label {label!r} maps to two different faculties")
            mapping[key] = name
    return mapping


def _target_summary(database_url: str) -> dict[str, str]:
    """Record only the host and database name, never credentials."""

    parts = urlsplit(database_url)
    return {
        "host": parts.hostname or "local",
        "database": (parts.path or "/").lstrip("/") or "postgres",
    }


def render_report(audit: dict[str, Any], target_label: str | None = None) -> str:
    """Render the audit as deterministic markdown (no timestamps beyond the header)."""

    target = audit["target"]
    lines = [
        "# Exchange enhancement data audit (dry-run)",
        "",
        f"Generated: {audit['generated_at_utc']} UTC",
        f"Target: `{target['host']}/{target['database']}`"
        + (f" ({target_label})" if target_label else ""),
        f"Result: **{'PASS' if audit['ok'] else 'FAIL'}**",
        "",
        "The audit is read-only: it counts rows, verifies referential integrity,",
        "and lists legacy faculty labels and university coverage. It writes",
        "nothing to the inspected database and stores no credentials.",
        "",
        "## Row counts (core tables)",
        "",
        "| Table | Rows |",
        "| --- | ---: |",
    ]
    for table in CORE_TABLES:
        lines.append(f"| `{table}` | {audit['row_counts'][table]} |")

    lines += [
        "",
        "## Enhancement objects (post-migration state)",
        "",
        "| Object | Present | Rows |",
        "| --- | --- | ---: |",
    ]
    for table in ENHANCEMENT_TABLES:
        state = audit["enhancement_tables"][table]
        rows = "n/a" if state["rows"] is None else state["rows"]
        lines.append(f"| `{table}` | {'yes' if state['present'] else 'no'} | {rows} |")
    for column, present in audit["new_columns"].items():
        lines.append(f"| column `{column}` | {'yes' if present else 'no'} | n/a |")

    lines += [
        "",
        "## Distinct legacy faculty labels",
        "",
        "| Source | Label | Rows |",
        "| --- | --- | ---: |",
    ]
    for row in audit["faculty_labels"]:
        label = row["label"] if row["label"] is not None else "NULL"
        lines.append(f"| `{row['source']}.faculty` | {label} | {row['rows']} |")

    candidates = audit["candidate_mappings"]
    lines += [
        "",
        "## Candidate faculty mappings",
        "",
        "Candidate mappings are deterministic: without a reviewed alias file the",
        "canonical faculty is the trimmed label itself. Variants are flagged,",
        "never silently merged.",
        "",
        "| Legacy label | Canonical faculty | Flags |",
        "| --- | --- | --- |",
    ]
    for row in candidates["mappings"]:
        flags = ", ".join(row["flags"]) if row["flags"] else "—"
        lines.append(f"| {row['label']} | {row['canonical']} | {flags} |")
    lines.append(
        f"\nNull-label rows: {candidates['null_label_rows']}. "
        f"Casefold collisions: {candidates['casefold_collisions']}."
    )

    lines += [
        "",
        "## Orphan relations",
        "",
        "| Relation | Orphan rows |",
        "| --- | ---: |",
    ]
    for relation, count in audit["orphans"].items():
        lines.append(f"| `{relation}` | {count} |")
    if audit["enhancement_orphans"]:
        for relation, count in audit["enhancement_orphans"].items():
            lines.append(f"| `{relation}` | {count} |")

    lines += [
        "",
        "## Missing geography",
        "",
        f"Universities with a null city or continent: {len(audit['missing_geography'])}.",
        "",
    ]
    if audit["missing_geography"]:
        lines += [
            "| University | Country | City | Continent |",
            "| --- | --- | --- | --- |",
        ]
        for row in audit["missing_geography"]:
            lines.append(
                f"| {row['name']} | {row['country']} "
                f"| {row['city'] or 'null'} | {row['continent'] or 'null'} |"
            )
    else:
        lines.append("All universities have both city and continent.")

    lines += [
        "",
        "## University coverage",
        "",
        "| University | Country | City | Continent | Partner modules | Mapping rows | Mapped degrees |",
        "| --- | --- | --- | --- | ---: | ---: | ---: |",
    ]
    for row in audit["university_coverage"]:
        lines.append(
            f"| {row['name']} | {row['country']} | {row['city'] or 'null'} "
            f"| {row['continent'] or 'null'} | {row['pu_modules']} "
            f"| {row['mapping_rows']} | {row['mapped_degrees']} |"
        )

    lines += [
        "",
        "## Dry-run conclusion",
        "",
    ]
    if audit["ok"]:
        lines.append(
            "Referential integrity holds and the core catalog is present. The additive"
        )
        lines.append(
            "migration and alias backfill can proceed; no legacy row requires special"
        )
        lines.append(
            "handling beyond the candidate mappings above."
        )
    else:
        lines.append(
            "The audit found orphan rows or an empty core catalog. Fix the data before"
        )
        lines.append("running the migration and backfill.")
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    sys.exit(main())
