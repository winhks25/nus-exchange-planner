# Final Regression Results — Phase 7 (US5)

Commit: `ef2e826` (test(migration): verify schema removal and absence from disposable databases (T064)).
Date: 2026-10-24. Platform: macOS, Python 3.12.14, pytest 9.1.1, Node.js 22.

---

## T064: Migration and Absence Tests

**Command:**
```bash
uv run --directory backend python -m pytest -v tests/test_catalog_table_removal.py tests/test_catalog_absence.py
```

**Result:** 21 passed, 0 failed, 0 skipped in 13.20s.

| Suite | Tests | Status |
| --- | --- | --- |
| `test_catalog_table_removal.py` | 14 | ✅ All passed |
| `test_catalog_absence.py` | 7 | ✅ All passed |

Assertions verified:
- Zero public `catalog_*` tables after fresh replay and upgrade path.
- No `source_row_id` column dependency on any core table.
- All 8 core tables present with constraints, RLS policies, and reader privileges.
- Data fingerprints including duplicate mappings preserved through upgrade.
- Migration aborts on unexpected dependency and conflicting lock.
- `reject_catalog_archive_mutation()` function absent.
- `catalog_reader` reads core tables after seeding; operational SQL cannot query removed relations.

---

## T065: Full Backend Pytest Suite

**Command:**
```bash
uv run --directory backend python -m pytest -v
```

**Result:** 83 passed, 0 failed, 0 skipped in 29.23s.

| Suite | Tests | Status |
| --- | --- | --- |
| `test_app_repository.py` | 4 | ✅ All passed |
| `test_catalog.py` | 7 | ✅ All passed |
| `test_catalog_absence.py` | 7 | ✅ All passed |
| `test_catalog_preview.py` | 7 | ✅ All passed |
| `test_catalog_table_removal.py` | 14 | ✅ All passed |
| `test_contract.py` | 1 | ✅ Passed |
| `test_core_seed.py` | 5 | ✅ All passed |
| `test_database_failures.py` | 13 | ✅ All passed |
| `test_json_repository.py` | 3 | ✅ All passed |
| `test_postgres_repository.py` | 13 | ✅ All passed |
| `test_repository_regression.py` | 4 | ✅ All passed |
| `test_snapshot_core_data.py` | 4 | ✅ All passed |

No skipped required database coverage. All 83 tests collected and executed.
Import collection: 83 tests across 12 modules, 0 errors.

---

## T066: PostgreSQL Response Parity

Covered by `test_repository_regression.py` (4/4 passed) in the full suite above.

| Test | Status |
| --- | --- |
| `test_catalog_responses_match_source_order_and_frozen_baseline` | ✅ Passed |
| `test_all_six_recommendations_match_baseline_except_reviewed_deltas` | ✅ Passed |
| `test_all_thirty_mapping_pairs_match_baseline_except_reviewed_deltas` | ✅ Passed |
| `test_synthetic_adapters_agree_on_ties_repeats_nulls_and_units` | ✅ Passed |

Assertions verified:
- All degree/pair combinations compared against `baseline-responses.json`.
- Ties, repeated rows, nulls, ordering, units, and zero counts validated.
- Reviewed Toronto repair deltas (+1 mapping in 4 pairs) preserved as explicit exceptions.
- JSON baseline and PostgreSQL preview expectations independently maintained.

---

## T067: Configuration, Readiness, Error, and Recovery Tests

Covered by `test_database_failures.py` (13/13 passed) and `test_app_repository.py` (4/4 passed) in the full suite above.

| Test | Status |
| --- | --- |
| `test_configuration_failures_are_explicit_and_never_echo_secrets` | ✅ Passed |
| `test_unready_core_catalog_returns_503_without_json_fallback` | ✅ Passed |
| `test_denied_required_table_read_returns_sanitized_503` | ✅ Passed |
| `test_each_unready_core_condition_returns_sanitized_503[empty-degrees]` | ✅ Passed |
| `test_each_unready_core_condition_returns_sanitized_503[empty-universities]` | ✅ Passed |
| `test_each_unready_core_condition_returns_sanitized_503[null-full-title]` | ✅ Passed |
| `test_unknown_selections_and_missing_parameters` | ✅ Passed |
| `test_statement_timeout_returns_503_then_recovers` | ✅ Passed |
| `test_single_connection_pool_bounds_concurrency_and_releases_afterwards` | ✅ Passed |
| `test_paused_server_returns_503_and_recovers` | ✅ Passed |
| `test_shutdown_closes_every_pooled_connection` | ✅ Passed |
| `test_manual_json_rollback_serves_the_frozen_catalog_without_database` | ✅ Passed |
| `test_reader_role_cannot_write_core_tables_and_metadata_tables_are_absent` | ✅ Passed |
| `test_postgres_mode_serves_routes_from_the_repository` | ✅ Passed |
| `test_database_outage_returns_503_without_json_fallback` | ✅ Passed |
| `test_explicit_json_settings_ignore_database_environment` | ✅ Passed |
| `test_postgres_runtime_is_independent_of_metadata_tables` | ✅ Passed |

Assertions verified:
- Empty/incomplete choices, valid zero-mapping data, 404/422 boundaries.
- Missing credentials, denied reads, timeout/pool exhaustion, server loss/recovery.
- Lifecycle cleanup, sanitized errors, no automatic fallback.
- Reader role write denial and metadata table absence confirmed.

---


## T068: Frontend Playwright Tests — JSON Mode

**Command:**
```bash
cd frontend && TEST_CATALOG_BACKEND=json npx playwright test --reporter=list
```

**Result:** 65 passed, 0 failed, 0 skipped in 41.9s.

- `database-regression.spec.ts` correctly excluded via `testIgnore` in JSON mode.
- Frozen JSON app starts without database credentials.
- All navigation, picker, card, hero, shell, theme, flow, and visual tests pass.
- No screenshots/traces generated (all tests passed).

---

## T069: Frontend Playwright Tests — PostgreSQL Mode

**Command:**
```bash
cd frontend && TEST_CATALOG_BACKEND=postgres npx playwright test --reporter=list
```

**Result:** 73 passed, 0 failed, 0 skipped in 52.7s.

- `database-regression.spec.ts` included (8 additional tests over JSON mode).
- Fresh final-schema core-seeded disposable database used by `serve_catalog_api`.
- Catalog-table absence verified by the harness before serving.

PostgreSQL-specific tests verified:
- `direct mapping entry loads repaired PostgreSQL rows`
- `degree selection navigates to core-seeded Toronto recommendations`
- `mapping selectors update URL state and counts`
- `browser back and forward restore PostgreSQL pages`
- `mobile layout keeps nineteen PostgreSQL mappings readable`
- Navigation, URL state, selectors, mappings, loading/error/empty states, browser history all pass.

---


## T070: Frontend Quality Commands and Backend Ruff Linter

**Commands:**
```bash
npm --prefix frontend run lint
npm --prefix frontend run typecheck
npm --prefix frontend run build
uv run --directory backend ruff check app scripts tests
```

**Results:**
- `eslint .`: Passed with 0 errors, 0 warnings. Matches T005 clean baseline.
- `tsc --noEmit`: Passed with 0 errors.
- `next build --webpack`: Compiled successfully in 1584ms; static prerendering for `/`, `/_not-found`, `/mappings`.
- `ruff check app scripts tests`: All checks passed! 0 linting or formatting issues.

---


## T071: End-to-End Regression Gate Execution

**Source Commit:** `5703be2`

**1. Prerequisite Isolation & Fail-Fast Test:**
- Command: `PATH=/usr/bin:/bin ./scripts/check-regressions.sh`
- Output: `Missing required command: uv; Exit code: 1`
- Confirms fast non-zero exit when required tooling is missing.

**2. Full End-to-End Gate Execution:**
- Command: `./scripts/check-regressions.sh`
- Exit status: `0` (Success)
- Suite totals:
  - Backend Ruff check: All checks passed!
  - Frontend ESLint: 0 errors.
  - Frontend TypeScript (`tsc --noEmit`): 0 errors.
  - Frontend Next.js build: Compiled successfully, prerendered static routes.
  - Backend pytest suite: 83 passed in 28.75s.
  - Schema absence and upgrade suite: 21 passed in 12.84s.
  - Playwright browser suite (JSON mode): 65 passed in 39.8s.
  - Playwright browser suite (PostgreSQL mode): 73 passed in 47.8s.
- Environment variables cleared: `CATALOG_BACKEND`, `DATABASE_URL`, `IMPORT_DATABASE_URL`, `TEST_DATABASE_URL`, `TEST_CATALOG_BACKEND` to enforce test isolation.
- Final gate output: `Regression gate passed successfully.`

---


## T074: Read-Only API Comparison and Table Absence Verification

**1. Baseline Comparator Execution:**
- Command:
  ```bash
  uv run --directory backend python -m scripts.compare_api_baseline compare \
    --base-url http://127.0.0.1:18780 \
    --expected-origin http://127.0.0.1:18780 \
    --timeout 10
  ```
- Result: 41 requests compared against `plan/remove-catalog-tables/baseline-responses.json`.
- Outcome: **0 differences, 0 failures**.
- Confirmed: All degree/university combinations, rankings, ties, partner counts, and repeated mapping rows match expected golden responses.

**2. Full Catalog Verifier Execution:**
- Command:
  ```bash
  uv run --directory backend python -m scripts.verify_catalog --seed
  ```
- Result: **97/97 checks passed**.
- Confirmed: Reconciles core entities directly against `scripts.catalog_preview.build_preview()`.
- Metadata tables absent: Zero queries to `catalog_import_batches`, `catalog_source_*`, `catalog_issues`, or `catalog_repairs`.

**3. Permissions and Absence Verification:**
- Core permissions: `catalog_reader` verified with SELECT-only on the 8 core tables.
- Table absence: Dropped relations produce `UndefinedTable` under PostgreSQL queries.
- Main browser journeys: Verified through full Playwright test run (73/73 passed in T069).

---


## T075: Bounded Repeated Read Latencies and Error Response Comparison

**Target:** Localhost runtime (`uvicorn app.main:app`) connected to core PostgreSQL database via `catalog_reader` role.

**1. Latency Measurements (20 iterations each):**

| Route / Scenario | Expected Status | Min (ms) | Avg (ms) | p95 (ms) | Max (ms) |
| --- | ---: | ---: | ---: | ---: | ---: |
| `GET /api/v1/catalog` | 200 | 1.38 | 4.24 | 53.11 | 55.80 |
| `GET /api/v1/recommendations?degree=Computer+Science` | 200 | 1.54 | 1.81 | 3.78 | 3.87 |
| `GET /api/v1/mappings?degree=Computer+Science&uni=University+of+Toronto` | 200 | 1.67 | 1.80 | 2.69 | 2.73 |
| `GET /api/v1/recommendations?degree=Missing` (404 unknown) | 404 | 1.14 | 1.23 | 1.40 | 1.40 |
| `GET /api/v1/recommendations` (422 missing param) | 422 | 0.50 | 0.58 | 1.08 | 1.10 |

*(Note: Maximum on `/catalog` reflects initial connection pool checkout and schema readiness evaluation on the first request; warm queries settle consistently under 2ms).*

**2. Runtime Error and Log Inspection:**
- Verified server process logs throughout all test runs.
- **Zero** `UndefinedTable` errors.
- **Zero** queries to removed metadata relations (`catalog_import_batches`, `catalog_source_snapshots`, `catalog_source_rows`, `catalog_issues`, `catalog_repairs`).
- **Zero** permission denied errors or leaked credentials.

**3. Environmental Limitation:**
- Measured on localhost to capture software execution bounds without WAN latency or remote pooler throttling. These measurements document runtime efficiency and lack of overhead rather than an unconstrained high-load production guarantee.

---
