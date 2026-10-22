# Exchange catalog database

Target Supabase project: `wydziozsjibkvpgphpia`.

## Deployment status

Applied the initial migration through the project's SQL Editor on 2026-10-22.
The public schema was empty before application. The SQL Editor reported success;
a subsequent catalog query verified all eight tables, RLS enabled on each,
eight foreign keys, and sixteen indexes (including primary/unique indexes).
No application data was imported. The manual application did not register CLI
history, so version `20261022000100` was later recorded with
`supabase migration repair` after a full schema comparison found no drift.
Local and remote migration history now agree; see
`plan/supabase-migration/schema-audit.md`.

The initial migration is `migrations/20261022000100_create_exchange_catalog.sql`.
Inspect the remote schema before applying it. It creates eight tables in one
transaction and deliberately fails if any already exist rather than silently
accepting an incompatible schema. Apply once through Supabase migrations or the
dashboard SQL Editor. A manual SQL Editor run does not register CLI migration
history; reconcile migration history before subsequently using `supabase db push`.

Degrees and NUS modules have a many-to-many relationship through `degree_modules`.
A module's offering faculty does not restrict which degrees can include it.
Specializations belong to a degree and have their own module membership; those
memberships do not automatically insert rows into `degree_modules`. Queries for
a degree including specialization options must explicitly combine both sets.

Partner course codes are unique within each university, not globally. Mappings
represent individual NUS/partner course pairs. Repeated mapping pairs remain
allowed to preserve the current application's source-row semantics. Bundled
equivalencies and curriculum-year versioning are outside this initial schema.

City, continent, offering faculty, and requirement type may be unknown rather
than inferred during a future import. Module names are required; an import must
resolve missing names explicitly. This migration contains no seed data and does
not switch the application away from JSON. It also does not add course units,
which must be addressed before migrating the existing API's unit fields.

All tables enable row level security without public policies. Anonymous and
ordinary authenticated Data API clients cannot read or write rows. Configure
backend database access separately; never expose privileged credentials in the
frontend. Foreign keys use PostgreSQL's default NO ACTION behavior to prevent
accidental deletion of referenced catalog records.

After applying, verify all eight tables, foreign keys, indexes, and RLS flags in
the remote database. Do not treat the existence of this file as proof of deployment.

## Catalog import and reader migrations

Apply migrations in order after the initial catalog schema:

1. `migrations/20261022000200_prepare_catalog_import.sql` adds source snapshots,
   import batches, source-addressed issues/repairs, and row-level presentation.
2. `migrations/20261022000300_catalog_reader.sql` creates the least-privilege
   runtime role and its SELECT policies.

Do not replay the initial `CREATE TABLE` migration. Use normal migration history
once the earlier repair is recorded.

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
