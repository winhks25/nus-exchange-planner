# Exchange catalog database

Target Supabase project: `wydziozsjibkvpgphpia` (region `ap-southeast-2`).

## Deployment status

The database is deployed and current. All four reviewed migrations are applied,
the catalog operates directly on the eight core tables, and the production
backend reads it through the read-only `catalog_reader` role. The deployed
frontend is unchanged apart from its API origin. Deployment evidence and URLs
are in `plan/supabase-migration/deployment-results.md` and `plan/remove-catalog-tables/cleanup-results.md`.

| Version | Migration | Purpose |
| --- | --- | --- |
| `20261022000100` | `create_exchange_catalog` | Initial eight-table catalog schema |
| `20261022000200` | `prepare_catalog_import` | Source provenance, issues, repairs and presentation |
| `20261022000300` | `catalog_reader` | Least-privilege runtime role and SELECT policies |
| `20261024034234` | `remove_catalog_metadata` | Drop metadata/archive/provenance tables and source_row_id column |
| `20261026000000` | `create_university_images_bucket` | Public university photograph bucket with service-role-only upload policies |

The initial migration was applied manually through the SQL Editor on 2026-10-22.
It did not register CLI history, so version `20261022000100` was later recorded
with `supabase migration repair` after a full schema comparison found no drift.
Local and remote migration history now agree; see
`plan/supabase-migration/schema-audit.md`. Never replay the initial `CREATE TABLE`
statements against the existing schema; apply future migrations with
`npx supabase@latest db push` and confirm with `migration list`.

## Schema layout

The catalog consists exclusively of eight core application tables:
`degrees`, `degree_modules`, `nus_modules`, `partner_universities`, `pu_modules`,
`module_mappings`, `specializations`, and `specialization_modules`.

Degrees and NUS modules have a many-to-many relationship through `degree_modules`.
A module's offering faculty does not restrict which degrees can include it.
Specializations belong to a degree and have their own module membership; those
memberships do not automatically insert rows into `degree_modules`. Queries for a
degree including specialization options must explicitly combine both sets.

Partner course codes are unique within each university, not globally. Mappings
represent individual NUS/partner course pairs. Repeated mapping pairs remain
allowed to preserve the application's source-row semantics. Bundled
equivalencies and curriculum-year versioning are outside this schema.

City, continent, offering faculty, and requirement type may be unknown rather
than inferred. Module names may be null in the source and are not invented.
The operational importer and its metadata tables (`catalog_import_batches`,
`catalog_source_snapshots`, `catalog_source_rows`, `catalog_issues`,
`catalog_repairs`) and the `source_row_id` column have been permanently removed.

All tables enable row level security without browser policies. Anonymous and
ordinary authenticated Data API clients cannot read or write rows. Foreign keys
use PostgreSQL's default NO ACTION behavior to prevent accidental deletion of
referenced catalog records.

## Catalog data maintenance

Production catalog maintenance is performed directly against the eight core tables
using standard SQL transactions. The operator runbook is
[maintenance guide](../plan/remove-catalog-tables/quickstart.md).

For local test databases, disposable targets can be seeded from the reviewed
preview using:

```bash
# Seed a local test database from the reviewed preview:
uv run --directory backend python -m scripts.catalog_seed \
  --database-url postgresql://postgres:postgres@localhost:54322/postgres

# Reconcile a database read-only against the reviewed preview:
uv run --directory backend python -m scripts.verify_catalog \
  --reconcile --target-project-ref wydziozsjibkvpgphpia
```

`scripts.catalog_seed` is restricted to local development targets and will reject
remote database URLs.

The current published core catalog contains 6 degrees, 5 universities, 151 active
mappings, 152 NUS modules, 142 partner modules, and 19 specializations. Missing
NUS titles remain null and are never invented.

## University image storage

Partner card photographs live in the public `university-images` bucket
(migration `20261026000000_create_university_images_bucket`). Objects are
addressed as `universities/<partner_university_id>.<ext>`.

- **Reads** are open through the public URL
  (`https://wydziozsjibkvpgphpia.supabase.co/storage/v1/object/public/university-images/...`).
  No storage policy grants `anon` or `authenticated` Data API access, so the
  bucket contents cannot be listed or fetched through the API without the public URL.
- **Writes** are restricted to the service role. The insert/update/select
  policies on `storage.objects` are scoped to `bucket_id = 'university-images'`
  and name `service_role` explicitly; the service key bypasses RLS by design, so
  only the administrative uploader (which holds that key server-side) can write.
- **Bucket-level upload restrictions** cap objects at 4 MiB and allow only
  `image/jpeg`, `image/png`, and `image/webp`.

The uploader is `backend/scripts/upload_university_assets.py`. It reads the
reviewed manifest at `data/exchange-enhancements/university-assets.json`,
downloads only the manifest-approved Wikimedia URLs, validates magic bytes and
size, uploads to the deterministic object path, and reuses an existing object
when its checksum matches (resume). Successful uploads produce per-university
outcomes in the manifest and a SQL artifact that updates
`partner_universities.image`, `website`, and `image_attribution`.

```bash
# Preview without any storage or database writes:
SUPABASE_ACCESS_TOKEN=<owner-token> \
  uv run --directory backend python -m scripts.upload_university_assets --dry-run

# Apply uploads and database updates in one reachable environment:
SUPABASE_ACCESS_TOKEN=<owner-token> \
  uv run --directory backend python -m scripts.upload_university_assets \
  --database-url '<server-only-url>'
```

`SUPABASE_ACCESS_TOKEN` is the owner's management token; the service role key is
retrieved from the Supabase Management API at runtime, kept in memory, and never
committed or shipped to the frontend. The live bucket was created on 2026-10-26
through the MCP channel because the pooler was unreachable from the development
machine at the time; `supabase db reset` applies the migration in local
environments.

## Unresolved data and historical provenance

The 3 quarantined Toronto rows that lacked official NUS codes remain excluded from
`module_mappings`. Historical provenance and audit trails are preserved in
repository planning documentation (`plan/supabase-migration/repair-report.md`
and `data-deltas.md`). The database itself stores only clean, normalized core entities.

## Runtime source and mode switches

The production backend uses `CATALOG_BACKEND=postgres` with a server-only
`DATABASE_URL` for `catalog_reader`. On startup or first query, the backend
verifies core readiness: at least one degree, at least one university, and no
null `full_title` in degrees.

A database failure or readiness failure returns a sanitized 503; it never falls
back to JSON automatically. To roll back, set `CATALOG_BACKEND=json`, remove
`DATABASE_URL`, and redeploy the backend. JSON mode serves the frozen snapshot
in `data/`. Detailed rollback and recovery procedures are in
[recovery guide](../plan/remove-catalog-tables/recovery.md).

## Runtime role credentials

The reader migration creates `catalog_reader` with `NOLOGIN`, `NOSUPERUSER`,
and `NOBYPASSRLS`, plus fixed statement and idle-transaction timeouts. It grants
`USAGE` on `public` and `SELECT` only on the eight core catalog tables. The
role cannot mutate data and has no browser-facing policies.

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

## Administrative and maintenance credentials

Direct maintenance, schema changes, and migrations must not use `catalog_reader`.
Use project owner or admin credentials via a direct connection (port `5432`)
or session pooler (port `5432`), and keep them out of runtime deployments.

Passwords are never committed to migrations or planning files. After
provisioning, verify the privileges with queries such as:

```sql
select has_table_privilege('catalog_reader', 'public.module_mappings', 'select');
select has_table_privilege('catalog_reader', 'public.degrees', 'select');
select has_table_privilege('catalog_reader', 'public.module_mappings', 'insert');
```

The expected results are `true`, `true`, and `false`. All dropped metadata tables
(`catalog_import_batches`, etc.) no longer exist.
