# Recovery capture and validation

Date: 2026-10-24 (Asia/Singapore). Scope: T035 (partial, by operator decision) and
T039 (post-removal recovery choices).

## T035 — export status: skipped, partial capture taken

The operator selected the Supabase MCP apply path, which skips the full `pg_dump`
export and its local restore rehearsal (the recoverable-backup prerequisite). As a
minimal safety net, the irrecoverable recovery data was captured read-only through
the MCP immediately before the apply.

### Capture location

`PRIVATE_BACKUP_DIR` = `/Users/winhtutkhaungsoe/Backups/nus-exchange-planner/catalog-removal-20261023`
(mode `0700`, outside Git).

### Captured files

| File | SHA-256 | Purpose |
| --- | --- | --- |
| `mapping-source-row-ids.csv` | `3300771eb2ff93e288dc29522e5b65aa38f3b73f95257d58178d810a28cdf7be` | `module_mappings.id → source_row_id` for all 151 mappings |
| `sequence-state.csv` | `c65e00ce9379e9614e3b362021197be8fda255b7ebd7a2e214838cf60a108595` | `last_value` for all 10 public sequences |
| `partial-manifest.json` | `a24d4edf5e3607edef580d3a893a98d9205aed73a6d87b485988c29c2a98aacd` | timestamp, project ref, row count, skipped-row note |

The mapping has 151 rows; `source_row_id` values skip 81, 82, and 86 (three
quarantined source rows), so the mapping is not a simple offset and is stored
explicitly. This is the recovery key required to re-link mappings if the metadata
were ever restored.

### What was NOT captured

This is a data-only capture. It does **not** include a restorable schema dump
(constraints, indexes, RLS policies, triggers, grants, functions) or the full
contents of the five dropped metadata tables. A local restore rehearsal and
core/archive fingerprint comparison were therefore not possible. The full
`application.dump` + `roles.sql` + restore procedure in `recovery.md` remains the
reference for any future controlled export; it was not executed for this change.

## T039 — post-removal recovery choices

The three recovery choices are documented in `recovery.md`. The required path
after removal is **choice 1 (redeploy the compatible core-readiness runtime)**:
the production Vercel backend is still running the pre-T014 code that queries
`catalog_import_batches`, so after the deletion it returns
`503 Catalog data is unavailable`. The compatible runtime was verified only on
localhost (T022/T023) and was never deployed — the plan's "no app redeploy"
assumption does not hold for the live backend. A redeploy of the compatible
runtime (or an explicit JSON-fallback switch) is required to restore service.

### Verification of the recovery paths

- **Compatible runtime:** verified on localhost in T022/T023 — the core-readiness
  runtime serves the full public contract through the reader role with no
  metadata tables. This is the target deployment; it is not yet live in
  production.
- **Explicit JSON fallback:** exercised locally during the earlier
  `plan/supabase-migration` outage rehearsal; the frozen snapshot starts without
  database credentials and serves the documented repaired-vs-frozen differences.
  A dedicated post-cleanup re-test is scheduled in T046/T072.
- **Restore deleted metadata (old runtime):** requires the full `application.dump`
  export, which was skipped. This path is documented in `recovery.md` but was not
  testable for this change. The `source_row_id` mapping captured above is the key
  that would backfill restored mappings by ID; it cannot recreate the schema.

### Production state after the apply

The production API (`https://nus-exchange-planner-api.vercel.app`) returns
`503 Catalog data is unavailable` immediately after the removal, confirming the
live backend still queries the deleted `catalog_import_batches`. The fix is to
redeploy the backend with the compatible core-readiness runtime (commit `af4d30e`
or later) or switch to `CATALOG_BACKEND=json`. This is operator-run (Vercel CLI +
credentials are not available in this session).

### Limitation

Because the full export was skipped, the "verify the export can restore
`source_row_id` links by mapping ID" check in T039 was reduced to capturing the
mapping (done) rather than a full restore rehearsal (not done). Any future
production restore must first capture a new full export at a controlled boundary,
per `recovery.md`, and reconcile post-export edits.
