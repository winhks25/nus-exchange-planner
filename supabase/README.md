# Exchange catalog database

Target Supabase project: `wydziozsjibkvpgphpia` (region `ap-southeast-2`).

## Deployment status

The database is deployed and current. All three reviewed migrations are applied,
the reviewed catalog is published as import batch `1` (`completed`,
`is_current=true`), and the production backend reads it through the read-only
`catalog_reader` role. The deployed frontend is unchanged apart from its API
origin. Deployment evidence and URLs are in
`plan/supabase-migration/deployment-results.md`.

| Version | Migration | Purpose |
| --- | --- | --- |
| `20261022000100` | `create_exchange_catalog` | Initial eight-table catalog schema |
| `20261022000200` | `prepare_catalog_import` | Source provenance, issues, repairs and presentation |
| `20261022000300` | `catalog_reader` | Least-privilege runtime role and SELECT policies |

The initial migration was applied manually through the SQL Editor on 2026-10-22.
It did not register CLI history, so version `20261022000100` was later recorded
with `supabase migration repair` after a full schema comparison found no drift.
Local and remote migration history now agree; see
`plan/supabase-migration/schema-audit.md`. Never replay the initial `CREATE TABLE`
statements against the existing schema; apply future migrations with
`npx supabase@latest db push` and confirm with `migration list`.

## Schema layout

Degrees and NUS modules have a many-to-many relationship through `degree_modules`.
A module's offering faculty does not restrict which degrees can include it.
Specializations belong to a degree and have their own module membership; those
memberships do not automatically insert rows into `degree_modules`. Queries for a
degree including specialization options must explicitly combine both sets.

Partner course codes are unique within each university, not globally. Mappings
represent individual NUS/partner course pairs. Repeated mapping pairs remain
allowed to preserve the current application's source-row semantics. Bundled
equivalencies and curriculum-year versioning are outside this schema.

City, continent, offering faculty, and requirement type may be unknown rather
than inferred. Module names may be null in the source and are not invented during
import. The import also stores verified units, degree full titles and source
order, specialization kind, raw source snapshots, import batches, source-addressed
issues and repairs, source-row identity, and row-specific presentation.

All tables enable row level security without browser policies. Anonymous and
ordinary authenticated Data API clients cannot read or write rows. Foreign keys
use PostgreSQL's default NO ACTION behavior to prevent accidental deletion of
referenced catalog records.

## Catalog data lifecycle

The checked-in JSON in `data/` plus reviewed repairs in
`data/repairs/catalog_repairs.json` are imported with the separate writer
credential `IMPORT_DATABASE_URL`. The operator runbook is
`plan/supabase-migration/quickstart.md`.

```bash
# Inspect without writing; the default mode is a dry run.
uv run --directory backend python -m scripts.import_catalog \
  --dry-run --target-project-ref wydziozsjibkvpgphpia

# Publish explicitly; remote targets require an exact confirmation value.
uv run --directory backend python -m scripts.import_catalog \
  --apply --target-project-ref wydziozsjibkvpgphpia \
  --confirm-project-ref wydziozsjibkvpgphpia

# Reconcile the completed batch read-only.
uv run --directory backend python -m scripts.verify_catalog \
  --reconcile --target-project-ref wydziozsjibkvpgphpia
```

The importer takes an advisory transaction lock, writes the batch marker,
archives, source rows, entities, mappings, issues and repairs in one transaction,
and commits the completed marker with them. A matching source and repair checksum
is a no-op. A different published snapshot is refused rather than overwritten;
refreshing the data requires a separately reviewed workflow. No table is truncated.

The current batch archives 8 files and 154 raw mapping rows: 146 accepted, 5
repaired, and 3 quarantined. It publishes 6 degrees, 5 universities, 151 active
mappings, 152 NUS modules, 142 partner modules and 19 specializations. The
reconciliation passes 19/19 checks; see `plan/supabase-migration/import-results.md`
and `plan/supabase-migration/data-deltas.md`.

## Unresolved data

Unresolved source rows are retained and reported, not silently dropped. The
current batch has 16 open, 9 resolved and 9 quarantined issues, plus 44 repair
records (24 verified and 20 unresolved). Three Toronto rows (source indexes 48,
49 and 53) remain quarantined because their NUS code field contains a course
title that cannot be resolved to one official code without inference. Missing NUS
titles remain null. These rows stay in `catalog_source_rows` and are excluded from
`module_mappings`. Canonical details are `plan/supabase-migration/repair-report.md`,
`data-deltas.md` and `import-results.md`.

## Runtime source and mode switches

The production backend uses `CATALOG_BACKEND=postgres` with a server-only
`DATABASE_URL` for `catalog_reader`. A database failure returns a sanitized 503;
it never loads JSON. To roll back, set `CATALOG_BACKEND=json`, remove
`DATABASE_URL`, and redeploy the backend. JSON mode serves the frozen snapshot and
does not undo database changes, so PostgreSQL mode can be restored later without
re-importing. Detailed rollback and roll-forward steps are in
`plan/supabase-migration/quickstart.md`.

## Runtime role credentials

The reader migration creates `catalog_reader` with `NOLOGIN`, `NOSUPERUSER`,
and `NOBYPASSRLS`, plus fixed statement and idle-transaction timeouts. It grants
`USAGE` on `public` and `SELECT` only on the catalog and import-batch tables. The
role cannot mutate data, read raw source snapshots, source rows, issues, or
repairs, and it has no browser-facing policies.

Provision a login password outside the repository and outside migrations:

```sql
-- Run once as the project owner with a password generated in a secret manager.
alter role catalog_reader with login password '<generated-password>';
```

Use the transaction pooler host from the project's Connect dialog and the
role-qualified pooler username:

```text
postgresql://catalog_reader.<project-ref>:<password>@<pooler-host>:6543/postgres?sslmode=require
```

Store that URL only in the backend deployment's server-side `DATABASE_URL`.
The application pool also forces `sslmode=require` and disables prepared
statements for transaction-pooler compatibility.

## Import credentials

Imports and migrations must not use `catalog_reader` or its password. Set a
separate `IMPORT_DATABASE_URL` for the project owner or a dedicated writer role,
prefer a direct connection (port `5432`) or session pooler, and keep it out of
the runtime deployment. The importer needs write access to the catalog, batch,
archive, issue, and repair tables; the reader intentionally does not.

Passwords are never committed to migrations or planning files. After
provisioning, verify the split with queries such as:

```sql
select has_table_privilege('catalog_reader', 'public.module_mappings', 'select');
select has_table_privilege('catalog_reader', 'public.catalog_source_snapshots', 'select');
select has_table_privilege('catalog_reader', 'public.module_mappings', 'insert');
```

The expected results are `true`, `false`, and `false`.
