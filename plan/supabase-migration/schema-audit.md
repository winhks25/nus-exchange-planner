# Schema audit

Audited: 2026-10-22
Target project: `wydziozsjibkvpgphpia`
Local migration: `supabase/migrations/20261022000100_create_exchange_catalog.sql`
Local migration SHA-256: `30f3721a16a6e39bc0199a26f7477e5bb762494dbe6f99b4acda92cfe0ab4daf`

## Outcome

**The remote public schema matches the local migration. No schema drift was found.**
All eight expected tables, 26 columns, identity columns, 30 constraints, 16 indexes,
and RLS flags are present with the expected definitions. No RLS policies exist.

**Migration history is now reconciled.** The manually applied migration was
registered with the supported CLI `migration repair` command after schema
equivalence was verified. Both local and remote history now report version
`20261022000100`; no DDL was replayed.

## Method

- Used the project-scoped access token from the untracked `backend/.env`. The
  token was never printed, committed, or written to this report.
- Ran read-only SQL through the Supabase Management API database query endpoint.
- Ran `npx supabase link --project-ref wydziozsjibkvpgphpia --yes`; it succeeded
  and wrote only CLI state under `supabase/.temp/`.
- Loaded the database password from the untracked `backend/.env` and connected
  through the transaction pooler on port `6543`; the session pooler on `5432`
  timed out from this network despite resolving correctly.
- Ran `npx supabase migration repair 20261022000100 --status applied --db-url ...`
  with the pooler URL. The CLI reported the version as applied, then
  `migration list` reported local and remote both as `20261022000100`.
- Did not run `db push`, `db reset`, `migration up`, or the migration SQL.

## Remote inventory

### Tables

Exactly eight base tables exist in `public`, matching the migration:

`degree_modules`, `degrees`, `module_mappings`, `nus_modules`,
`partner_universities`, `pu_modules`, `specialization_modules`, `specializations`.

### Columns and identity

- 26 columns match the expected names, order, types, nullability, and defaults.
- Five identity columns use `GENERATED ALWAYS AS IDENTITY` starting at 1 with
  increment 1: `degrees.id`, `specializations.id`, `partner_universities.id`,
  `pu_modules.id`, and `module_mappings.id`.

### Constraints

30 constraints: 8 primary keys, 8 foreign keys, 4 unique constraints, and 10 check
constraints.

Foreign keys, all with the default `NO ACTION` behavior:

- `degree_modules_degree_id_fkey` -> `degrees(id)`
- `degree_modules_module_code_fkey` -> `nus_modules(code)`
- `module_mappings_nus_module_code_fkey` -> `nus_modules(code)`
- `module_mappings_pu_module_id_fkey` -> `pu_modules(id)`
- `pu_modules_partner_university_id_fkey` -> `partner_universities(id)`
- `specialization_modules_module_code_fkey` -> `nus_modules(code)`
- `specialization_modules_specialization_id_fkey` -> `specializations(id)`
- `specializations_degree_id_fkey` -> `degrees(id)`

Unique constraints:

- `degrees_name_key` on `(name)`
- `partner_universities_name_key` on `(name)`
- `specializations_degree_id_name_key` on `(degree_id, name)`
- `pu_modules_partner_university_id_code_key` on `(partner_university_id, code)`

Check constraints enforce nonblank names, nonblank degree faculty, nonblank
country, nonblank codes, uppercase NUS and partner codes, and null-or-nonblank
`degree_modules.requirement_type`.

### Indexes

16 indexes: eight primary-key indexes, four unique indexes, and the four explicit
lookup indexes from the migration:

- `degree_modules_module_code_idx` on `degree_modules (module_code)`
- `specialization_modules_module_code_idx` on `specialization_modules (module_code)`
- `module_mappings_nus_module_code_idx` on `module_mappings (nus_module_code)`
- `module_mappings_pu_module_id_idx` on `module_mappings (pu_module_id)`

### RLS and policies

- RLS is enabled on all eight tables.
- No table forces RLS.
- `pg_policies` returns zero rows for `public`, matching the migration's
  backend-only access model.

### Data

All eight tables are empty. The remote database contains schema only; no catalog
data has been imported.

## Drift summary

| Area | Expected | Remote | Drift |
|---|---|---|---|
| Tables | 8 | 8 | None |
| Columns | 26 | 26 | None |
| Identity columns | 5 | 5 | None |
| Primary keys | 8 | 8 | None |
| Foreign keys | 8 | 8 | None |
| Unique constraints | 4 | 4 | None |
| Check constraints | 10 | 10 | None |
| Indexes | 16 | 16 | None |
| RLS enabled tables | 8 | 8 | None |
| RLS policies | 0 | 0 | None |
| Rows | 0 | 0 | None |

## Migration-history status

| Item | Status |
|---|---|
| Local file `20261022000100` | Present and unchanged |
| Local SHA-256 | `30f3721a16a6e39bc0199a26f7477e5bb762494dbe6f99b4acda92cfe0ab4daf` |
| `supabase_migrations` schema | Created by the CLI repair |
| `supabase_migrations.schema_migrations` | Present |
| Remote version `20261022000100` | Registered as `create_exchange_catalog` |
| CLI project link | Linked to `wydziozsjibkvpgphpia` |
| `migration list` | Local and remote both report `20261022000100` |
| History repair run | Yes, via transaction pooler `6543` |
| `db push` safe to run | Yes; no pending local migration remains |

The manual SQL Editor application did not create the CLI history schema, so the
repair created it and recorded the version without executing the migration SQL.

## Reconciliation executed

Equivalence was verified before the supported CLI repair:

```bash
npx supabase migration repair 20261022000100 --status applied --db-url "$DB_URL"
npx supabase migration list --db-url "$DB_URL"
```

Observed result:

```text
Repaired migration history: [20261022000100] => applied
local: 20261022000100, remote: 20261022000100
```

The Management API then confirmed one row in
`supabase_migrations.schema_migrations`: version `20261022000100`, name
`create_exchange_catalog`. The public schema still contains exactly eight tables
and no data.

Do not use `db push`, `db reset`, or the migration SQL to recreate this history;
future migrations may use normal CLI history once reviewed.

## Status

`T002` is complete: schema drift is absent and migration history is reconciled.
