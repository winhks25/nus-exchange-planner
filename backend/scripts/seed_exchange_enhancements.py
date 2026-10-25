"""Repeatable, transactional backfill for the exchange enhancement tables.

Resolves legacy faculty text through the reviewed faculty-aliases.json file:
upserts the canonical faculties, records explicit degree membership in
degree_faculties, and sets nus_modules.faculty_id where the module label
resolves. A label without a reviewed alias keeps faculty_id null and retains
its legacy text until an alias is added (decisions.md, decisions 4 and 7).
The backfill never deletes rows and never changes an already-set faculty_id,
so re-running the same input is a no-op. Use --dry-run to preview the plan
without writing.
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Any

import psycopg
from psycopg.conninfo import conninfo_to_dict, make_conninfo

from scripts.audit_exchange_enhancements import AuditError, _load_aliases

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ALIASES = REPO_ROOT / "data" / "exchange-enhancements" / "faculty-aliases.json"


class SeedError(RuntimeError):
    """Raised when the backfill cannot be applied safely."""


def main(argv: list[str] | None = None) -> int:
    """Parse arguments, build the seed plan, and apply it unless dry-run."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--database-url",
        help="PostgreSQL URL; defaults to DATABASE_URL or IMPORT_DATABASE_URL",
    )
    parser.add_argument(
        "--aliases",
        type=Path,
        default=None,
        help="reviewed faculty alias file; defaults to data/exchange-enhancements/faculty-aliases.json",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print the seed plan without writing to the database",
    )
    args = parser.parse_args(argv)

    database_url = (
        args.database_url or os.environ.get("DATABASE_URL") or os.environ.get("IMPORT_DATABASE_URL")
    )
    if not database_url:
        parser.error("requires --database-url, DATABASE_URL, or IMPORT_DATABASE_URL")

    aliases_path = args.aliases
    if aliases_path is None and DEFAULT_ALIASES.is_file():
        aliases_path = DEFAULT_ALIASES
    if aliases_path is None:
        parser.error("no alias file found; pass --aliases")

    try:
        aliases = _load_aliases(aliases_path)
        with _connect(database_url) as conn, conn.transaction():
            # The plan reads and the writes share one transaction snapshot;
            # any failure rolls the whole backfill back.
            plan = build_seed_plan(conn, aliases)
            _print_plan(plan, dry_run=args.dry_run)
            if args.dry_run:
                return 0
            # Conflicting rows mean a faculty_id was set by hand; review
            # before the backfill touches anything on this target.
            if plan["module_conflicts"]:
                print(
                    "aborted: conflicting faculty links need manual review",
                    file=sys.stderr,
                )
                return 1
            apply_seed_plan(conn, plan)
    except (SeedError, AuditError, psycopg.Error, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


def build_seed_plan(conn: psycopg.Connection, aliases: dict[str, str]) -> dict[str, Any]:
    """Compute everything the backfill would change, without writing.

    The plan is derived from the current database state, so re-running it
    after a successful apply reports zero changes.
    """

    # Existing faculty names and ids so a re-run reuses the stable identities.
    faculty_rows = conn.execute("select name, id from public.faculties").fetchall()
    existing = {name: int(faculty_id) for name, faculty_id in faculty_rows}
    id_names = {int(faculty_id): name for name, faculty_id in faculty_rows}

    # Canonical faculties from the reviewed alias file, deterministically sorted.
    canonical_names = sorted(set(aliases.values()), key=lambda name: (name.casefold(), name))
    faculties = [
        {"name": name, "id": existing.get(name)} for name in canonical_names
    ]

    # Degree membership comes only from the degree's own legacy label; it is
    # never derived from module offerings (decisions.md, decision 2).
    degree_rows = conn.execute(
        "select id, name, faculty from public.degrees order by id"
    ).fetchall()
    existing_pairs = {
        (int(row[0]), int(row[1]))
        for row in conn.execute(
            "select degree_id, faculty_id from public.degree_faculties order by 1, 2"
        )
    }
    degree_memberships: list[tuple[int, str, str, bool]] = []
    unresolved_degrees: list[tuple[str, str | None]] = []
    for degree_id, degree_name, label in degree_rows:
        faculty_name = _resolve(label, aliases)
        if faculty_name is None:
            unresolved_degrees.append((degree_name, label))
            continue
        faculty_id = existing.get(faculty_name)
        # Only a pair whose faculty already exists can already be recorded.
        already = faculty_id is not None and (int(degree_id), faculty_id) in existing_pairs
        degree_memberships.append((int(degree_id), degree_name, faculty_name, already))

    # Modules: null faculty_id plus a resolving label is the only case updated.
    module_rows = conn.execute(
        "select code, faculty, faculty_id from public.nus_modules order by code"
    ).fetchall()
    module_updates: list[tuple[str, str]] = []
    conflicts: list[tuple[str, str | None, str]] = []
    unresolved_modules: dict[str | None, int] = {}
    already_set = 0
    for code, label, faculty_id in module_rows:
        faculty_name = _resolve(label, aliases)
        if faculty_name is None:
            key = label.strip() if label is not None else None
            unresolved_modules[key] = unresolved_modules.get(key, 0) + 1
            continue
        if faculty_id is not None:
            current = id_names.get(int(faculty_id))
            if current == faculty_name:
                already_set += 1
            else:
                conflicts.append((code, current, faculty_name))
            continue
        module_updates.append((code, faculty_name))

    return {
        "faculties": faculties,
        "degree_memberships": degree_memberships,
        "unresolved_degrees": unresolved_degrees,
        "module_updates": module_updates,
        "modules_already_set": already_set,
        "module_conflicts": conflicts,
        "unresolved_modules": unresolved_modules,
        "degrees_total": len(degree_rows),
        "modules_total": len(module_rows),
    }


def apply_seed_plan(conn: psycopg.Connection, plan: dict[str, Any]) -> None:
    """Apply the plan in dependency order; the caller owns the transaction."""

    # Faculties first so the link rows can reference stable ids. The upsert
    # returns the id whether the row existed or was created.
    faculty_ids: dict[str, int] = {}
    for faculty in plan["faculties"]:
        row = conn.execute(
            """
            insert into public.faculties (name) values (%s)
            on conflict (name) do update set name = excluded.name
            returning id
            """,
            (faculty["name"],),
        ).fetchone()
        faculty_ids[faculty["name"]] = int(row[0])

    # Explicit degree membership; a duplicate pair is a no-op on re-run.
    if plan["degree_memberships"]:
        conn.cursor().executemany(
            """
            insert into public.degree_faculties (degree_id, faculty_id)
            values (%s, %s)
            on conflict (degree_id, faculty_id) do nothing
            """,
            [(degree_id, faculty_ids[name])
             for degree_id, _, name, _ in plan["degree_memberships"]],
        )

    # Only modules whose faculty_id is still null; every existing link is kept.
    if plan["module_updates"]:
        values = ", ".join("(%s::text, %s::bigint)" for _ in plan["module_updates"])
        params = [
            value for code, name in plan["module_updates"] for value in (code, faculty_ids[name])
        ]
        conn.execute(
            f"""
            update public.nus_modules n
            set faculty_id = v.faculty_id
            from (values {values}) as v(code, faculty_id)
            where n.code = v.code and n.faculty_id is null
            """,
            params,
        )


def _resolve(label: str | None, aliases: dict[str, str]) -> str | None:
    """Map a legacy label to its canonical faculty, or None when unresolved."""

    if label is None:
        return None
    return aliases.get(label.strip().casefold())


def _print_plan(plan: dict[str, Any], dry_run: bool) -> None:
    """Print the deterministic seed plan for review and the run log."""

    mode = "dry run - no writes" if dry_run else "will apply in one transaction"
    print(f"Seed plan ({mode})")

    print("Faculties:")
    for faculty in plan["faculties"]:
        state = f"existing id {faculty['id']}" if faculty["id"] is not None else "to create"
        print(f"  {faculty['name']} ({state})")

    to_add = [row for row in plan["degree_memberships"] if not row[3]]
    already = len(plan["degree_memberships"]) - len(to_add)
    print(f"Degree memberships to add: {len(to_add)}")
    for degree_id, degree_name, faculty_name, _ in to_add:
        print(f"  {degree_name} -> {faculty_name}")
    print(f"Degree memberships already present (left untouched): {already}")
    print(f"Degrees with unresolved labels (no membership added): {len(plan['unresolved_degrees'])}")
    for degree_name, label in plan["unresolved_degrees"]:
        print(f"  {degree_name}: {label!r}")

    print(f"Module faculty_id updates: {len(plan['module_updates'])}")
    print(f"Modules already set (left untouched): {plan['modules_already_set']}")
    print(f"Modules with unresolved labels (faculty_id stays null): "
          f"{sum(plan['unresolved_modules'].values())}")
    for label, count in sorted(
        plan["unresolved_modules"].items(), key=lambda item: (str(item[0]), item[0] is None)
    ):
        print(f"  {label!r}: {count}")

    print(f"Conflicting faculty links (existing id differs from resolved): "
          f"{len(plan['module_conflicts'])}")
    for code, current, resolved in plan["module_conflicts"]:
        print(f"  {code}: {current!r} -> resolved {resolved!r}")


def _connect(database_url: str) -> psycopg.Connection:
    """Open a secret-safe connection with local-friendly TLS defaults."""

    try:
        params = conninfo_to_dict(database_url)
        host = str(params.get("host") or "").lower()
        local = host in {"localhost", "127.0.0.1", "::1"} or host.startswith("/")
        if not local and params.get("sslmode") not in {"require", "verify-ca", "verify-full"}:
            params["sslmode"] = "require"
        params.setdefault("application_name", "nus-exchange-planner-seed")
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
        raise SeedError(f"database operation failed: {message}") from None


if __name__ == "__main__":
    sys.exit(main())
