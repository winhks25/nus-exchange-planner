# Schema audit

Audited: 2026-10-22
Target project: `wydziozsjibkvpgphpia`
Local migration: `supabase/migrations/20261022000100_create_exchange_catalog.sql`
Local migration SHA-256: `30f3721a16a6e39bc0199a26f7477e5bb762494dbe6f99b4acda92cfe0ab4daf`

## Outcome

**Blocked: the remote schema and migration history could not be inspected.**
No Supabase access token or database credentials are available in this
environment, and the repository is not linked to the project.

This audit does not claim that the remote schema matches the local migration.
Drift remains **unknown** until the checks below are run with access.

## Evidence collected

| Check | Result |
|---|---|
| `supabase` CLI on PATH | Not installed; `npx supabase@latest` resolves CLI 2.121.0 |
| `supabase/config.toml` | Absent, so the repository is not initialized or linked |
| `supabase/.temp/project-ref` | Absent |
| `SUPABASE_ACCESS_TOKEN` | Not set |
| `~/.config/supabase`, `~/.supabase` | Absent |
| `npx supabase projects list` | `AccessTokenRequiredError: Access token not provided` |
| `npx supabase migration list` | `ProjectRefNotLinkedError: Cannot find project ref` |
| Project REST root | HTTPS 401 without an API key; the project host resolves |
| Database credentials | No `DATABASE_URL` or password in tracked files or environment |

The REST 401 confirms the project host is reachable but does not expose schema
information. No anonymous or guessed credentials were used.

## Expected local schema

The initial migration creates eight tables in the `public` schema inside one
transaction and enables row level security on every table.

| Table | Primary key | Foreign keys |
|---|---|---|
| `degrees` | `id` | None |
| `nus_modules` | `code` | None |
| `degree_modules` | `(degree_id, module_code)` | `degree_id -> degrees.id`, `module_code -> nus_modules.code` |
| `specializations` | `id` | `degree_id -> degrees.id` |
| `specialization_modules` | `(specialization_id, module_code)` | `specialization_id -> specializations.id`, `module_code -> nus_modules.code` |
| `partner_universities` | `id` | None |
| `pu_modules` | `id` | `partner_university_id -> partner_universities.id` |
| `module_mappings` | `id` | `nus_module_code -> nus_modules.code`, `pu_module_id -> pu_modules.id` |

Expected indexes: eight primary-key indexes, four unique indexes (`degrees.name`,
`partner_universities.name`, `specializations (degree_id, name)`, `pu_modules
(partner_university_id, code)`), and four explicit lookup indexes on
`degree_modules.module_code`, `specialization_modules.module_code`,
`module_mappings.nus_module_code`, and `module_mappings.pu_module_id`.

Expected constraints include nonblank checks on names and codes, uppercase course
codes, and no browser-facing RLS policies. The migration is intentionally
non-idempotent: replaying its `CREATE TABLE` statements against an existing
schema must fail.

## Drift status

The remote DDL has not been read, so no table, column, constraint, index, or RLS
comparison can be reported as matching. The statements in `supabase/README.md`
about eight tables, eight foreign keys, sixteen indexes, and RLS enabled are
prior manual evidence, not verification from this audit.

## Migration-history status

| Item | Status |
|---|---|
| Local file `20261022000100` | Present and unchanged |
| Remote `supabase_migrations.schema_migrations` | Not queried |
| Likely history state | Missing `20261022000100`; the README says it was applied through the SQL Editor |
| CLI-linked project | No |
| `supabase db push` safe to run | No; it would treat the migration as pending and may replay DDL |

The manual SQL Editor run did not register CLI history. Do not run `db push`
until the remote schema is compared and the history row is repaired.

## Safe reconciliation sequence

Run these steps only with a real access token and the project database password.
Do not put either value in a tracked file.

```sql
-- Compare the remote catalog with the expected objects. Read-only.
select table_name, column_name, data_type, is_nullable
from information_schema.columns
where table_schema = 'public'
  and table_name in (
    'degrees', 'nus_modules', 'degree_modules', 'specializations',
    'specialization_modules', 'partner_universities', 'pu_modules', 'module_mappings'
  )
order by table_name, ordinal_position;

-- Check primary keys, unique constraints, foreign keys, and check constraints.
select conrelid::regclass as table_name, conname, contype, pg_get_constraintdef(oid)
from pg_constraint
where connamespace = 'public'::regnamespace
order by conrelid::regclass::text, conname;

-- Check indexes.
select tablename, indexname, indexdef
from pg_indexes
where schemaname = 'public'
order by tablename, indexname;

-- Check RLS flags and policies.
select relname, relrowsecurity, relforcerowsecurity
from pg_class
where relnamespace = 'public'::regnamespace and relkind = 'r'
order by relname;

select tablename, policyname, cmd, roles, qual, withcheck
from pg_policies
where schemaname = 'public'
order by tablename, policyname;

-- Check registered migration versions.
select version, name, inserted_at
from supabase_migrations.schema_migrations
order by version;
```

Then reconcile history only if the comparison shows the expected tables,
constraints, indexes, and RLS state:

```bash
# Link and inspect first. These commands do not modify the schema.
npx supabase link --project-ref wydziozsjibkvpgphpia
npx supabase migration list

# Mark the manually applied migration as applied ONLY after equivalence is
# confirmed. This writes a history row; it does not run the SQL file.
npx supabase migration repair 20261022000100 --status applied

# Re-list to confirm local and remote history agree.
npx supabase migration list
```

Never run `db push`, `db reset`, or the migration file itself to "fix" history
while the tables already exist.

## Required follow-up

Provide one of the following, then repeat this audit and record the observed
schema and history:

1. A Supabase access token plus the linked project and database password, or
2. A read-only `DATABASE_URL` for introspection plus a separate way to repair
   history after equivalence is confirmed.

Until then, T002 remains blocked and no reconciliation command has been run.
