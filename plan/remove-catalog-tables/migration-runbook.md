# Migration runbook — remove catalog metadata tables

Migration: `supabase/migrations/20261024034234_remove_catalog_metadata.sql`
(REMOVAL_MIGRATION). Linked project: `wydziozsjibkvpgphpia`
(`nus-exchange-planner`). Supabase CLI inspected at version `2.122.0` via
`npx --yes supabase@latest`.

Production execution is **user-run** (the stored no-autonomous-prod-deploy rule).
This runbook is the reviewed procedure; T037 is the single apply. There is no app
redeploy — the compatible core-readiness runtime (T014) already serves without the
metadata tables, verified on localhost in T022/T023.

## Exact object changes

The migration removes, in this order, inside one transaction:

1. **T028 — core unlink (module_mappings):**
   - drop constraint `module_mappings_source_row_id_fkey` (FK → `catalog_source_rows`)
   - drop constraint `module_mappings_source_row_id_key` (unique on `source_row_id`)
   - drop column `public.module_mappings.source_row_id`
2. **T029 — metadata tables and archive guard (appended by T029):**
   - drop `public.catalog_issues`, `public.catalog_repairs` (children)
   - drop `public.catalog_source_rows`
   - drop `public.catalog_source_snapshots`
   - drop `public.catalog_import_batches`
   - drop function `public.reject_catalog_archive_mutation()` once its remaining
     dependencies are verified absent

Dropping each table removes its attached triggers, RLS policies, indexes, and
owned sequences by ownership — no separate drops, no wildcard, no `CASCADE`.

## Dependency order and transaction behavior

- **Order:** unlink `module_mappings` first (so no FK points into the archive),
  then drop archive children before parents, then the guard function last.
- **One transaction:** `begin; … commit;`. Any statement error aborts the whole
  migration; nothing is left half-applied.
- **RESTRICT semantics:** plain `DROP` uses PostgreSQL's default `RESTRICT`. An
  unexpected dependent object makes the drop fail rather than cascade. This is
  intentional — an unexpected dependency is a stop condition, not something to
  force through.
- **No `CASCADE`, no wildcard drops, no core-table data rewrite, no automatic
  repair of unrelated migration history.**

## Lock timeout

`set local lock_timeout = '5s';` at the top of the transaction. A drop blocked by
a conflicting lock fails fast instead of queueing behind long-running writers.
Direct data edits and import jobs are paused at the T034 change boundary, so no
legitimate writer should contend.

## Stop conditions (abort, investigate, do not retry blindly)

- A drop fails on an unexpected dependent object (RESTRICT fired).
- `lock_timeout` is exceeded (a writer still holds a conflicting lock).
- The pending-migration list contains anything other than this one migration.
- The linked target is not `wydziozsjibkvpgphpia`.
- Post-apply verification (T038) finds any core table/column/row changed, or any
  of the five named tables still present.

On any abort: confirm the transaction rolled back (no partial change, migration
not recorded as applied), investigate the cause, and **do not** retry with
`CASCADE` or overwrite migration history.

## Previewing pending migrations

```bash
# Requires a Supabase access token / login session in the operator's shell.
npx --yes supabase@latest migration list --linked      # local vs remote history
npx --yes supabase@latest db push --linked --dry-run    # prints what WOULD apply
```

The dry-run must show exactly one pending migration:
`20261024034234_remove_catalog_metadata`. If it shows more, stop (T027 requires
the three historical files unchanged and no stray local migration).

## Production command sequence (T037 — user runs)

```bash
# 0. Operator is authenticated: `supabase login` (or SUPABASE_ACCESS_TOKEN set).
# 1. Confirm target and pending set.
npx --yes supabase@latest migration list --linked
npx --yes supabase@latest db push --linked --dry-run

# 2. Apply the single reviewed migration.
npx --yes supabase@latest db push --linked

# 3. Confirm it is recorded exactly once.
npx --yes supabase@latest migration list --linked
```

`db push --linked` applies pending migrations to the linked project and records
them in the remote `supabase_migrations.schema_migrations` history. Do not pass
`--include-all`; only the single pending removal migration should apply.

## How migration history is updated

The CLI records the applied version in the remote migration history table after a
successful transaction. A failed/rolled-back apply records nothing, so a retry
after fixing the cause starts from the same clean state. Never hand-edit the
history table to force a version in or out.

## What this runbook must NOT do

- No production run from an agent session — the operator runs step 2.
- No `CASCADE`, no wildcard `drop table catalog_*`, no `drop … if exists` guard
  that would hide an unexpected missing object.
- No change to the three applied historical migrations.
- No core-table data rewrite, reseed, or readiness-marker insert.
