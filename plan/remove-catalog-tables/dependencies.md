# Dependency inventory for catalog table removal

Date: 2026-10-23. Scope: T002 inventory of executable references in
`backend/app/`, `backend/scripts/`, `backend/tests/`, `scripts/`,
`frontend/playwright.config.ts`, and `frontend/tests/`.

Removal targets are the SQL relations `public.catalog_import_batches`,
`public.catalog_source_snapshots`, `public.catalog_source_rows`,
`public.catalog_issues`, `public.catalog_repairs`, and the
`public.module_mappings.source_row_id` column with its foreign key and unique key.
This inventory excludes historical planning files and migrations, which stay
unchanged.

## Reference summary

| Area | Metadata-table SQL | `source_row_id` | Indirect importer use | Planned action |
| --- | --- | --- | --- | --- |
| Runtime adapter | Yes | No | No | Replace publication marker with core readiness (T014) |
| Importer | Yes | Yes | Yes | Retire publication path after moving retained parsing (T049-T055) |
| Seeder | Yes (batch only) | No | Yes | Seed only eight core tables (T018, T052) |
| Verifier | Yes | Yes | Yes | Remove archive/batch reconciliation (T050) |
| Browser servers | No | No | Yes | Use core seeder (T019, T051) |
| Performance helper | No | No | Yes (via seeder) | Remove importer caller (T051) |
| Backend tests | Yes | Yes | Yes | Replace fixtures and provenance assertions (T016, T017, T024, T053-T056) |
| Frontend config/tests | No | No | Yes (server command) | Adjust only if the PostgreSQL server command changes (T057) |
| Regression script | No | No | Yes (runs affected suites) | Replace with `scripts/check-regressions.sh` (T058) |

## Runtime

`backend/app/repositories/postgres_catalog.py` is the only application runtime
file that queries a removal target:

- `PUBLISHED_BATCH_SQL` reads `public.catalog_import_batches` at line 25.
- `_require_published_batch()` runs that query at the start of `catalog()`,
  `recommendations()`, and `mappings()`.
- No runtime SQL selects `catalog_source_*`, `catalog_issues`,
  `catalog_repairs`, or `source_row_id`.

Impact: after removal, all three endpoints would fail with a missing-relation
error surfaced as a sanitized 503. T014 replaces this marker with the core
readiness query; T012/T013/T017 prove the readiness and independence behavior.

## Operational scripts

| File | Direct dependency | Detail and follow-up |
| --- | --- | --- |
| `backend/scripts/import_catalog.py` | All five tables and `source_row_id` | Defines `REQUIRED_TABLES`, `_catalog_counts`, `_publication_state`, `_insert_batch`, `_insert_snapshots`, `_insert_source_rows`, `_insert_mappings`, `_insert_issues`, `_insert_repairs`, `_complete_batch`, and `apply_plan`. This is the production importer to retire. Retain offline plan building/validation only if still needed by tests or the simplified verifier. |
| `backend/scripts/catalog_seed.py` | `catalog_import_batches` | `seed_preview()` calls `_insert_batch()` before inserting core rows. Remove the batch write and keep the remaining eight-table seeding path (T018). |
| `backend/scripts/verify_catalog.py` | All five tables and `source_row_id` | Reconciliation queries at lines 787, 856, 904-905, 1100-1101, 1156-1158, 1204-1206, 1257-1295 and the `EDGE_CASE_SQL` batch insert at line 493. It also imports `_connect`, `_validate_target`, `_target_summary`, `_database_error_message`, `ImportPlan`, and `build_import_plan` from the importer. T050 replaces archive reconciliation with core/source-derived checks and moves or reuses target validation deliberately. |
| `backend/scripts/serve_catalog_api.py` | None directly | Imports `apply_plan` and `build_import_plan`, so the disposable browser database currently requires the importer. T019 switches it to the core-only seeder. |
| `backend/scripts/serve_catalog_database.py` | None directly | Calls `catalog_seed.seed_preview()`, which currently inserts a batch marker. It becomes core-only when the seeder is fixed. |
| `backend/scripts/measure_catalog_performance.py` | None directly | Imports `seed_preview`, so it inherits the seeder dependency. T051 removes the importer-dependent setup path. |
| `scripts/check-migration-regressions.sh` | None directly | Runs backend tests and both browser modes that currently build fixtures through the importer. T058 replaces it with the ongoing core-table gate. |

The importer is imported by:

- `backend/tests/conftest.py` (`ImportPlan`, `apply_plan`, `build_import_plan`)
- `backend/tests/test_import_catalog.py` and `test_import_regression.py`
- `backend/scripts/serve_catalog_api.py`
- `backend/scripts/verify_catalog.py` (shared helpers and plan type)

Deleting importer symbols before those callers are rewired would break test
collection, the PostgreSQL browser server, and reconciliation mode. T049-T051
and T062 cover that ordering.

## Backend tests

| File | Dependency | Planned change |
| --- | --- | --- |
| `backend/tests/conftest.py` | Imports importer plan/apply; `published_catalog` publishes a batch | Replace with core-only seeder for ordinary fixtures; keep a legacy ceiling fixture only for upgrade tests (T019, T051) |
| `backend/tests/test_postgres_repository.py` | `PUBLISHED_BATCH` fixture inserts `catalog_import_batches` | Delete the marker; build readiness from core rows (T016) |
| `backend/tests/test_app_repository.py` | `APP_FIXTURE` inserts a batch | Replace with core readiness rows (T016) |
| `backend/tests/test_repository_regression.py` | `SYNTHETIC_FIXTURE` inserts a batch | Replace with core readiness rows (T016) |
| `backend/tests/test_database_failures.py` | Inserts a batch, counts `catalog_source_snapshots` and `catalog_source_rows`, asserts reader denial on archives | Replace with unready-core readiness cases; move access-control checks to retained core tables and final-schema absence (T017, T056) |
| `backend/tests/test_import_catalog.py` | Importer plan/apply and deletes a `catalog_repairs` row | Keep offline parsing coverage; retire database-publication assertions (T053, T054) |
| `backend/tests/test_import_regression.py` | Deep joins over all archive tables and `module_mappings.source_row_id` | Replace with core fixture/data-preservation cases (T053) |
| `backend/tests/test_catalog_preview.py` | Only the file path `data/repairs/catalog_repairs.json` | Harmless checked-in repair input; no table SQL |

The new migration tests will intentionally name the removed relations:
`test_catalog_table_removal.py` (upgrade/constraint/abort) and
`test_catalog_absence.py` (absence and final-schema runtime). These are permitted
negative/historical references, not operational dependencies.

## Frontend

`frontend/playwright.config.ts` contains no metadata-table SQL. It selects the
PostgreSQL backend by running `scripts.serve_catalog_api`, which indirectly uses
the importer; T057 only needs to adjust that command if T019 changes its
interface. `frontend/tests/database-regression.spec.ts` has no table references
and asserts repaired counts (7/10/19 mappings, Toronto). Those data expectations
must stay.

## Harmless names to keep

These are not database relations and are outside the removal scope:

- `/api/v1/catalog` route and catalog API response/type names
- `CATALOG_BACKEND=json|postgres` and `CatalogRepository`/`CatalogDatabase`
- `catalog_reader` database role
- `backend/scripts/catalog_source.py`, `catalog_preview.py`, `catalog_seed.py`
- `data/repairs/catalog_repairs.json` (source input, not the dropped table)
- `source_row_id` as a Python field name only in retired importer code; any
  surviving use must be documented as a historical/negative-test reference

## Documentation callers

Current operator docs and examples that still assume the importer or batch model:

- `README.md` (dry-run/apply/reconcile commands, import lifecycle)
- `supabase/README.md` (importer workflow and archive references)
- `backend/.env.example` (`IMPORT_DATABASE_URL` and import comments)
- `plan/supabase-migration/quickstart.md` and historical evidence files

T059/T060 update current operator documentation; historical
`plan/supabase-migration/` evidence stays as a record with links to the new
quickstart where needed.

## Removal-order implications

1. Replace runtime readiness and core-only test/browser fixtures first so the
   application no longer needs metadata permissions.
2. Capture the upgrade fixture and migration rehearsal data while the importer
   still exists.
3. Drop the production metadata tables only after the compatible runtime is
   deployed and the export is restorable.
4. Retire importer and provenance tooling after production verification.
5. Replace the regression entry point and re-run the complete gate.

No executable metadata-table reference should remain in runtime, current
operational scripts, or current documentation after T061/T062.
