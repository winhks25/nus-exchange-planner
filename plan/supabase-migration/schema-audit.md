# Schema audit

Audited: 2026-10-22
Target project: `wydziozsjibkvpgphpia`
Local migration: `supabase/migrations/20261022000100_create_exchange_catalog.sql`
Local migration SHA-256: `30f3721a16a6e39bc0199a26f7477e5bb762494dbe6f99b4acda92cfe0ab4daf`

## Outcome

**The remote public schema matches the local migration. No schema drift was found.**
All eight expected tables, 26 columns, identity columns, 30 constraints, 16 indexes,
and RLS flags are present with the expected definitions. No RLS policies exist.

**Migration history is missing.** The remote database has no
`supabase_migrations` schema, so the manually applied migration is not registered.
The CLI project link now succeeds, but `migration list` and `migration repair`
still require the database password, which is not available. No history row has
been written and no DDL has been replayed.

## Method

- Used the project-scoped access token from the untracked `backend/.env`. The
  token was never printed, committed, or written to this report.
- Ran read-only SQL through the Supabase Management API database query endpoint.
- Ran `npx supabase link --project-ref wydziozsjibkvpgphpia --yes`; it succeeded
  and wrote only CLI state under `supabase/.temp/`.
- Attempted `npx supabase migration list --linked`; it blocked waiting for the
  database password and was terminated by the command timeout. It made no
  schema or history changes.
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
| `supabase_migrations` schema | Absent |
| `supabase_migrations.schema_migrations` | Absent |
| Remote version `20261022000100` | Not registered |
| CLI project link | Linked to `wydziozsjibkvpgphpia` |
| `migration list` | Blocked on database password |
| History repair run | No |
| `db push` safe to run | No; it would treat the migration as pending |

The manual SQL Editor application did not create the CLI history schema. Until a
history row exists, `db push` must not be used.

## Safe reconciliation sequence

Equivalence is verified. Complete the history repair with the supported CLI
command once the database password is available. Provide it through a local
environment variable or CLI prompt; do not commit it.

```bash
# The project is already linked.
npx supabase migration repair 20261022000100 --status applied --linked

# Confirm local and remote history agree.
npx supabase migration list --linked
```

Never run `db push`, `db reset`, or the migration SQL to repair history while the
tables already exist.

## Remaining blocker

`T002` schema comparison is complete with no drift. The task's final step, CLI
history repair, needs the project database password (or a direct database URL).
Without it the CLI cannot connect to `supabase_migrations` and the migration
remains unregistered.
