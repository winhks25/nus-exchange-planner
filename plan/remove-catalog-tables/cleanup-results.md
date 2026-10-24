# Cleanup and Retirement Inventory for Catalog Tables (US4)

Date: 2026-10-24. Scope: T049 audit and mapping of every remaining `scripts.import_catalog` symbol,
dependency, and caller to its retained purpose, establishing the keep/move/delete plan for Phase 6 (US4).

## 1. Symbol-by-Symbol Mapping (`backend/scripts/import_catalog.py`)

| Symbol | Category | Description / Callers | Action | Destination / Retained Mechanism |
| --- | --- | --- | --- | --- |
| `CatalogImportError`, `ImportDataError`, `ImportRefused`, `SimulatedImportFailure` | Exceptions | Error classes for import failure simulation and data issues. | **Delete** | Retired with the importer. Tests use standard assertions or repository/snapshot errors. |
| `DegreeRecord`, `NusModuleRecord`, `DegreeModuleRecord`, `UniversityRecord`, `PartnerModuleRecord`, `SourceRowRecord`, `MappingRecord`, `IssueRecord`, `RepairRecord`, `SpecializationRecord`, `SpecializationModuleRecord` | Dataclasses | Entity representations extracted from preview data. | **Delete** | Core seeding and preview validation already use dicts directly via `scripts.catalog_preview` and `scripts.catalog_seed`. |
| `CatalogEntities`, `ImportPlan`, `PublicationState` | Dataclasses | Containers for the import plan and database publication state. | **Delete** | Retired. `verify_catalog.py` will use `build_preview()` directly for core checks. |
| `build_import_plan()` | Plan builder | Wraps `build_preview()` to produce `ImportPlan`. | **Delete** | Direct consumers switch to `scripts.catalog_preview.build_preview()`. |
| `_build_entities()`, `_validate_degree_eligibility()`, `_degree_record()`, `_nus_module_record()`, `_degree_module_record()`, `_university_record()`, `_partner_module_record()`, `_specialization_record()` | Entity helpers | Transformation of preview entities into records. | **Delete** | Already implemented in `scripts.catalog_preview` and `scripts.catalog_seed`. |
| `_validate_archives()`, `_build_source_rows()`, `_raw_course()`, `_build_mappings()`, `_build_issues()`, `_build_repairs()`, `_lookup_path()`, `_validate_provenance()`, `_validate_entities()` | Validation helpers | Validated raw archives against preview and checked provenance. | **Move/Retain in tests** | Offline source and preview integrity tests move to `tests/test_catalog_preview.py` and `tests/test_core_seed.py`. |
| `_unique_values()`, `_required_text()`, `_optional_text()`, `_required_int()`, `_optional_positive_int()`, `_required_code()`, `_optional_positive()` | Formatting / Normalization | Type and format validation helpers. | **Delete** | Handled natively by preview builders and psycopg type casting. |
| `_project_ref_from_url()`, `_expected_target_label()`, `_validate_target()`, `_target_summary()`, `_database_error_message()`, `_connect()` | Connection / Target Validation | Safe target validation and connection handling without credentials. | **Move / Already in Snapshot** | Already available in `scripts.snapshot_core_data`. Shared target helpers in `verify_catalog.py` will import from `scripts.snapshot_core_data`. |
| `_require_schema()`, `_catalog_counts()`, `_publication_state()`, `_plan_counts()`, `_result_base()`, `dry_run()` | Operational State | Checks existing batches/counts and generates publication reports. | **Delete** | Retired. Core tables are validated via `snapshot_core_data.py` and `verify_catalog.py`. |
| `_insert_batch()`, `_insert_snapshots()`, `_insert_source_rows()`, `_insert_degrees()`, `_insert_nus_modules()`, `_insert_degree_modules()`, `_insert_universities()`, `_insert_partner_modules()`, `_insert_mappings()`, `_insert_specializations()`, `_insert_issues()`, `_insert_repairs()`, `_complete_batch()` | Persistence | Writes to the 5 metadata tables and 8 core tables. | **Delete** | Production importing is retired. Local test seeding for core tables is handled by `scripts.catalog_seed.seed_preview()`. |
| `apply_plan()`, `_print_summary()`, `_emit()`, `_exit_code()`, `_parser()`, `main()` | CLI Runner | Importer entry point and execution runner. | **Delete** | Command line `import_catalog.py` is permanently retired. |

---

## 2. Caller-by-Caller Mapping and Rewiring Plan

| Caller File | Current Usage | Retained Purpose | Planned Action |
| --- | --- | --- | --- |
| `backend/scripts/verify_catalog.py` | Imports `ImportPlan`, `build_import_plan`, `_connect`, `_database_error_message`, `_target_summary`, `_validate_target`. Runs `Reconciler` checking 5 metadata tables. | Validation of core database entities and API responses against source preview and JSON baseline. | **T050**: Refactor `verify_catalog.py` to compare the 8 core tables directly against `scripts.catalog_preview.build_preview()`. Import target/connection helpers from `scripts.snapshot_core_data`. Eliminate all metadata table queries (`catalog_import_batches`, `catalog_source_*`, `catalog_issues`, `catalog_repairs`, and `source_row_id`). |
| `backend/tests/conftest.py` | Defines `import_plan`, `legacy_published_catalog`, and `importer_connection`. Ordinary `published_catalog` already uses `seed_preview`. | Provide clean fixtures for backend tests. | **T051**: Remove `import_plan`, `legacy_published_catalog`, and `importer_connection` fixtures. All database tests run on the final migration chain using `published_catalog` (core-seeded). |
| `backend/scripts/serve_catalog_api.py` | Already rewired in T019 to `seed_preview(database, build_preview())`. | Serve API on disposable core-seeded database for browser/Playwright tests. | **T051**: Verify no residual import credentials or unneeded env vars. |
| `backend/scripts/serve_catalog_database.py` | Already uses `seed_preview(database, build_preview())`. | Provide disposable database for local development. | **T051**: Verify cleanup and local target verification. |
| `backend/scripts/measure_catalog_performance.py` | Already uses `seed_preview(database, build_preview())`. | Measure query performance on core tables with synthetic enlargement. | **T051**: Verify no residual importer calls. |
| `backend/scripts/catalog_seed.py` | Seeds 8 core tables from `preview`. | Local disposable database seeder for test environments. | **T052**: Final cleanup: remove obsolete unused helpers, ensure clean one-transaction insertion, enforce local target check. |
| `backend/tests/test_import_regression.py` | 400 lines testing batch publication, provenance joins across 5 metadata tables, concurrency locks, and idempotency. | Provenance persistence testing is retired. Core data preservation, duplicate mappings, and rollback tests must be preserved. | **T053**: Replace with `tests/test_core_seed.py` and `tests/test_catalog_table_removal.py` to cover core data invariants (repeated mappings, overlapping degree memberships, rollback on seed error, unchanged source files). Retire concurrency and publication-specific tests with explicit documented reasons. |
| `backend/tests/test_import_catalog.py` | Tests plan building, entity counts, repair application, dry run, and publication. | Source parsing and repair normalization must remain verified. | **T054**: Move offline parsing and repair validation to `tests/test_catalog_preview.py` and remove publication/batch tests. |
| `backend/scripts/generate_catalog_fixtures.py` | Generated pre-removal fixtures in T010. | Tooling completed in Phase 2. | **T055**: Update comments noting the tool has finished its lifecycle. |
| `backend/tests/test_database_failures.py` | Contains access-control checks against `catalog_import_batches` and metadata tables. | Verify database error handling and least-privilege runtime security. | **T056**: Refactor access checks to target core tables and assert absence of metadata tables under reader role. |
| `frontend/playwright.config.ts` | Configures web server for tests. | Runs browser tests against API and JSON mode. | **T057**: Confirm commands and core-seeded final schema compatibility. |
| `scripts/check-migration-regressions.sh` | Top-level regression test runner. | Single command regression suite. | **T058**: Replace with `scripts/check-regressions.sh` covering final schema, core seeder, unit tests, lint, and browser journeys. |
| `README.md`, `supabase/README.md`, `backend/.env.example` | Operator documentation and example env configs. | Clear maintenance and operation instructions. | **T059, T061**: Remove `import_catalog` commands, batch concepts, and `IMPORT_DATABASE_URL`. Document direct Supabase maintenance and local verification tooling. |
| `plan/remove-catalog-tables/quickstart.md` | Operator guide for Supabase maintenance. | Safe direct maintenance instructions. | **T060**: Write comprehensive guide. |

---

## 3. Concrete Keep / Move / Delete List

### Files to Keep
- `backend/scripts/catalog_source.py` (Source file reading and raw JSON parsing)
- `backend/scripts/catalog_preview.py` (Offline repair application, entity resolution, and summary statistics)
- `backend/scripts/catalog_seed.py` (Disposable local PostgreSQL seeder for the 8 core tables)
- `backend/scripts/snapshot_core_data.py` (Core table data snapshot and natural key comparison)
- `backend/scripts/compare_api_baseline.py` (Read-only API comparator against captured baseline)
- `backend/scripts/verify_catalog.py` (Simplified to core entity and API verification)
- `backend/tests/fixtures/core_dataset.json` (Frozen baseline data fixture)
- `backend/tests/fixtures/pre_catalog_removal.sql` (Legacy upgrade test fixture for migration testing)

### Files to Move / Refactor
- `backend/tests/test_import_catalog.py` -> Move offline parsing/repair assertions to `backend/tests/test_catalog_preview.py`; remove publication tests.
- `backend/tests/test_import_regression.py` -> Replace with `backend/tests/test_core_seed.py` (for core seed integrity) and retain migration assertions in `backend/tests/test_catalog_table_removal.py`.
- `scripts/check-migration-regressions.sh` -> Replace with `scripts/check-regressions.sh`.

### Files to Delete
- `backend/scripts/import_catalog.py` (Deleted in T055 once all callers are rewired)
- Obsolete test files or test fixtures once superseded in T053-T055.

---

## 4. Retired Import Regression Assertions and Replacement Mapping (T053)

`backend/tests/test_import_regression.py` has been replaced by `backend/tests/test_core_seed.py` and `backend/tests/test_catalog_table_removal.py`. Below is the audit of each test and the reason for removal/relocation:

| Test in `test_import_regression.py` | Disposition | Reason / Retained Coverage |
| --- | --- | --- |
| `test_import_accounts_for_every_raw_source_byte_and_row` | **Retired** | Verified storage in `catalog_source_snapshots` and `catalog_source_rows`. Both tables were deleted in migration `20261024034234_remove_catalog_metadata`. File integrity checks retained in `test_source_files_remain_unchanged`. |
| `test_persisted_repairs_issues_and_unknown_values_match_reviewed_sources` | **Retired** | Verified storage in `catalog_repairs` and `catalog_issues` linked via `source_row_id`. Both tables and column were dropped in the migration. Offline repair validation is tested in `test_catalog_preview.py`. |
| `test_shared_memberships_and_repeated_identities_do_not_multiply_rows` | **Moved to `test_core_seed.py`** | Preserves core invariant: repeated mappings, degree-module links, specialization memberships, and BT4240 requirements must not multiply rows. |
| `test_identical_import_is_noop_and_changed_snapshot_is_refused` | **Retired** | Production importing with batch tracking and hash locking is retired. Database maintenance is performed directly on Supabase. |
| `test_concurrent_importers_serialize_on_the_advisory_lock` | **Retired** | Importer CLI concurrency locking is obsolete since the importer is retired. |
| `test_injected_failure_rolls_back_every_table` | **Moved to `test_core_seed.py`** | Verifies transactional atomicity: a seed failure in `seed_preview` rolls back all 8 core tables completely. |
| `test_source_files_remain_unchanged_by_the_import` | **Moved to `test_core_seed.py`** | Verifies that source files on disk in `data/` and `data/repairs/` match expected sha256 digests. |

---

## 5. Verification Checkpoint for T049 & T053
- All symbols in `backend/scripts/import_catalog.py` accounted for.
- Every dependent caller identified and mapped to a specific Phase 6 task (T050-T062).
- Zero broken imports planned; rewiring precedes deletion.
- Retired assertions documented with justification.

---

## 6. Credential Audit and Stale Reference Cleanup (T061)

### A. Credential Audit and Redacted Changes
- **`IMPORT_DATABASE_URL`**:
  - Removed from `backend/.env.example`.
  - Removed from `backend/app/settings.py` (`Settings.import_database_url` and env parsing removed).
  - Explicitly popped from runtime subprocess environments in `backend/scripts/serve_catalog_api.py`.
  - Unset in `scripts/check-regressions.sh` along with testing credentials to guarantee sandbox isolation.
- **Runtime Credentials (`DATABASE_URL`)**:
  - Unchanged: Bound to the least-privilege `catalog_reader` role. Requires core readiness (1 degree, 1 uni, non-null degree full_title).
- **Administrative / Writer Credentials**:
  - Kept strictly out of repository configurations and runtime deployments.
  - Direct SQL maintenance uses owner credentials via direct connection (5432) or session pooler as documented in `quickstart.md`.

### B. Stale Removed-Table Audit
- **Application Runtime (`backend/app/`)**:
  - Zero executable references to the 5 deleted metadata tables (`catalog_import_batches`, `catalog_source_snapshots`, `catalog_source_rows`, `catalog_issues`, `catalog_repairs`) or `source_row_id`.
  - `backend/tests/test_app_repository.py`: Removed obsolete `REVOKE_METADATA_ACCESS` fixture referencing dropped `catalog_import_batches`.
- **Validation and Test Tooling (`backend/scripts/`, `backend/tests/`)**:
  - `verify_catalog.py` reconciled directly against `build_preview()` on core entities without batch/archive joins.
  - `test_database_failures.py` updated to verify `UndefinedTable` on dropped metadata tables under `catalog_reader`.
- **Historical Runbooks and Planning Docs**:
  - Historical `plan/supabase-migration/quickstart.md` annotated with an alert pointing to `plan/remove-catalog-tables/quickstart.md`.
  - Historical migration SQL files and planning logs preserved as immutable audit history.

---

## 7. Targeted Verification and Tooling Validation (T062)

### A. Test Execution Summary
- **Backend Pytest Suite**: 83/83 passed in 30.93s (`uv run --directory backend pytest -q`).
- **Python Import Collection**: 83 tests successfully collected across 12 test modules with 0 errors (`python -m pytest --collect-only`).
- **Command CLI Interface (`--help`)**:
  - `scripts.catalog_seed --help`: Pass.
  - `scripts.verify_catalog --help`: Pass.
  - `scripts.snapshot_core_data --help`: Pass.
  - `scripts.catalog_preview --help`: Pass.
  - `scripts.compare_api_baseline --help`: Pass.
- **Frontend Quality Gates**:
  - ESLint: 0 errors (`npm --prefix frontend run lint`).
  - TypeScript Compiler: 0 errors (`npm --prefix frontend run typecheck`).
- **Backend Linter**:
  - Ruff: All checks passed (`uv run --directory backend ruff check app scripts tests`).

### B. Core Invariant & Regression Checks
- **Source Data Digests**: `test_source_files_remain_unchanged` confirmed that source files in `data/` and `data/repairs/` match expected sha256 digests.
- **Core Entity Seed & Persistence**: `test_seed_preview_populates_core_tables`, `test_shared_memberships_and_repeated_identities_do_not_multiply_rows`, and `test_seed_failure_rolls_back_every_core_table` confirmed single-transaction insertion, duplicate handling, and rollback integrity.
- **JSON Fallback & Baseline Agreement**: Contract tests (`test_contract.py`), JSON repository tests (`test_json_repository.py`), and baseline comparison tests confirmed that explicit JSON fallback and expected baseline responses remain unaltered.
- **Absence Assertions**: `test_catalog_absence.py` confirmed `source_row_id` is absent, core tables remain, no `catalog_`-prefixed metadata tables remain, and the archive guard trigger function is absent.





---

## 8. Security, Secret Sanitization, and Artifact Cleanup Audit (T078)

### A. Private Backup and Recovery Verification
- **Backup Location:** `/Users/winhtutkhaungsoe/Backups/nus-exchange-planner/catalog-removal-20261023`
  - Located strictly outside the repository worktree (`Desktop/nus-exchange-planner`).
  - Directory permissions: `0700` (`drwx------`).
  - Files present: `mapping-source-row-ids.csv`, `sequence-state.csv`, `partial-manifest.json`.
  - Content contains the 151 `source_row_id` mapping links and sequence values captured prior to deletion.
- **Restore Procedures:** Retained and reachable in `plan/remove-catalog-tables/recovery.md` and `plan/remove-catalog-tables/quickstart.md`.

### B. Secret and Credential Sanitization Audit
- Verified git status and full commit history across all Phase 6 and Phase 7 changes:
  - **Zero** production passwords, connection strings, or service tokens committed.
  - Runtime credentials (`DATABASE_URL`) references use redacted placeholders (`...`).
  - Importer credentials (`IMPORT_DATABASE_URL`) completely removed from environment examples and application settings.
  - Zero database dump files (`.dump`, `.sql` data dumps) tracked in git.

### C. Process and Disposable Cluster Cleanup
- Checked running processes for orphaned testing servers or clusters (`uvicorn`, test `postgres`).
- Confirmed only system and user services remain running; all task-owned disposable test clusters created during pytest and Playwright runs were terminated and unlinked cleanly.
- Intentional evidence files in `plan/remove-catalog-tables/` remain intact for auditable verification.
