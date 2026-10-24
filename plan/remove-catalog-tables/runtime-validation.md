# Runtime validation (US1)

Date: 2026-10-24 (Asia/Singapore). Source commit: `4bbec54` (T19), on `master`.

Scope: T020 targeted repository, application, failure, and regression suites plus
the core seeder and migration-harness checks, after T012–T019. Host memory was
critically low, so only the targeted suites below were run (not the full gate,
which is T065/T071). The disposable PostgreSQL cluster requires `LC_ALL=C LANG=C`
to start on this macOS/Homebrew PostgreSQL 16 host (a locale bug, unrelated to the
code under test).

## Commands and outcomes

Environment: `LC_ALL=C LANG=C`, run from the repository root.

```bash
uv run --directory backend pytest -q \
  tests/test_postgres_repository.py \
  tests/test_app_repository.py \
  tests/test_database_failures.py \
  tests/test_repository_regression.py \
  tests/test_snapshot_core_data.py \
  tests/test_import_regression.py
# -> 45 passed, 1 warning (StarletteDeprecationWarning, pre-existing)

uv run --directory backend pytest -q tests/test_catalog_table_removal.py
# -> 4 passed, 2 failed (both PRE-EXISTING; see below)

uv run --directory backend ruff check \
  scripts/catalog_seed.py scripts/serve_catalog_api.py \
  tests/conftest.py tests/test_database_failures.py
# -> All checks passed!
```

| Suite | Result | Notes |
| --- | --- | --- |
| `test_postgres_repository.py` | pass | Core-readiness cases (T012) and existing behavior, now core-seeded (T016). |
| `test_app_repository.py` | pass | Runtime independence (T013) and core-only `APP_FIXTURE` (T016). |
| `test_database_failures.py` | pass | Unready-core 503s (T017); protected-archive test repointed to the legacy fixture (T019). |
| `test_repository_regression.py` | pass | Synthetic fixture core-seeded (T016); JSON/PostgreSQL parity against the frozen baseline and reviewed Toronto deltas unchanged. |
| `test_snapshot_core_data.py` | pass | Repointed to the legacy importer fixture (provenance/`source_row_id` is importer-only). |
| `test_import_regression.py` | pass | Repointed to `legacy_published_catalog` on the pre-removal ceiling (T019). |

## Baseline comparison

`test_repository_regression.py` compares every degree and all 30 degree/university
pairs to `plan/supabase-migration/baseline-responses.json` and to
`ExpectedCatalog(build_preview())`. All pass: source order, `C`-collation ties,
repeated rows, null omission, partner-unit fallback, NUS units=4, and zero-count
universities are unchanged. The four reviewed Toronto deltas and the three
valid-empty pairs remain reviewed exceptions, not regenerated expectations.

The core seeder reproduces the reviewed preview exactly, so switching the shared
`published_catalog` fixture from the importer to `seed_preview` changed no expected
API output — the parity suite is the evidence.

## Explicitly resolved assertion changes (not weakened)

- `test_completed_batch_without_degrees_is_unavailable` was removed: readiness no
  longer depends on an import batch, and the empty-database and empty-degree cases
  are covered by `test_empty_database_is_unavailable` and the T012 cases.
- `test_reader_role_cannot_write_or_read_protected_archives`,
  `test_import_regression.py`, and `test_snapshot_core_data.py` were repointed to
  `legacy_published_catalog` (real importer, legacy migration ceiling) rather than
  relaxing their metadata-table/provenance assertions. Those assertions are
  retired in US2 (table removal) and US4 (T053/T056), not here.

## Pre-existing failures (not caused by US1 runtime work)

- `test_catalog_table_removal.py::test_apply_next_migration_applies_exactly_one_pending_migration`
- `test_catalog_table_removal.py::test_apply_next_migration_propagates_sql_errors`

Both fail at `HEAD` before the T015–T019 edits (verified by `git stash`), because
the final removal migration (`REMOVAL_MIGRATION`, T027) does not exist yet, so
`apply_next_migration` has no pending migration to apply. This is expected US2
work, not a US1 runtime regression.

## T021 — PostgreSQL browser flows

Date: 2026-10-24 (Asia/Singapore). Host memory was TIGHT (~2.2 GB free), so only
the PostgreSQL DB-regression spec was run (single worker, line reporter), not the
full JSON+PostgreSQL matrix (that is T068/T069 in US5).

Command (run from `frontend/`):

```bash
LC_ALL=C LANG=C TEST_CATALOG_BACKEND=postgres \
  npx playwright test tests/database-regression.spec.ts --workers=1 --reporter=line
# -> 8 passed (24.9s)
```

The backend server was `scripts.serve_catalog_api` (the Playwright `webServer`
command for postgres mode), which starts a disposable `PostgresCluster`, seeds it
with `seed_preview(build_preview())` — the **core-only seeder** (T018/T019) — and
backs uvicorn with the read-only `reader_url`. No importer, no metadata tables.

| Flow | Result | Asserted |
| --- | --- | --- |
| direct mapping entry loads repaired rows | pass | Toronto 7 mappings / 3 distinct NUS / 7 mappable partner. |
| degree selection → Toronto recommendations | pass | AI degree: 5 cards, #1 Toronto, 6 NUS / 10 partner, deep link → 10 mapping rows. |
| mapping selectors update URL state and counts | pass | Business Analytics × Toronto = 19; × Kyoto = 2 distinct. |
| browser back/forward restore pages | pass | Toronto 7 ↔ Kyoto 1 via history. |
| valid empty pair and unavailable service | pass | UWA valid-empty (0 mappable, "No qualifying mappings"); mocked 503 → alert. |
| loading state stays visible | pass | Loading spinner during delayed response → 7 rows. |
| rapid selection ignores late response | pass | Superseded Toronto request discarded; Kyoto 1 distinct holds. |
| mobile layout keeps 19 mappings readable | pass | 390×844 viewport, no horizontal overflow, 19 rows. |

Key finding: every exact count the spec asserts (Toronto=7, AI=10, Business
Analytics=19, Kyoto, zero-count UWA) reproduced from the **core seeder**, so the
core-seeded server is behaviorally identical to the importer-backed server for the
browser suite — the parity goal of US1. No selector, loading/error/empty-state, or
count regression. The SWC `next-swc-darwin-arm64` warnings are pre-existing
environment noise (a `package-lock.json` outside the repo), not test failures.

## Not run here (deferred)

- `test_json_repository.py` and the contract suite: unaffected by US1 runtime
  changes; covered by the final gate (T065).
- JSON-mode Playwright flows and the full backend suite / lint / typecheck /
  build: covered by the US5 final gate (T065/T068/T069/T070) and not required by
  T021, which scopes only the PostgreSQL browser flows.


## T023 — Compatible localhost runtime vs captured API baseline

Date: 2026-10-24 (Asia/Singapore). Source commit: `af4d30e`, on `master`. Host
memory critically low; this is a backend-only comparison (no frontend dev server).

The core-seeded disposable database stands in for production locally while the
metadata tables still exist remotely. The separate read-only check that the *real*
Supabase data is unchanged happens at the deletion boundary (T034/T038), not here.

### Command

```bash
# backend server (separate process): core-seeded disposable PostgreSQL, reader role
LC_ALL=C LANG=C uv run python -m scripts.serve_catalog_api --host 127.0.0.1 --port 18765

# comparison (run from backend/)
LC_ALL=C LANG=C uv run python -m scripts.compare_api_baseline compare \
  --base-url http://127.0.0.1:18765 \
  --baseline ../plan/remove-catalog-tables/baseline-responses.json \
  --report <scratch>/t023-compare-report.md
# -> Compared 41 requests ...: 0 differences, 0 failures   (exit 0)
```

`--base-url` overrides the baseline's recorded `endpoint_origin`
(`https://nus-exchange-planner-api.vercel.app`) so the T008 production baseline is
replayed against the local compatible runtime.

### Result: PASS — 0 differences, 0 failures across 41 requests

The comparator derives its request set from the original captured catalog (6
degrees × 5 universities) and replays, in baseline order:

- `catalog` (1)
- `recommendations` for every discovered degree (6)
- `mappings` for every degree/university pair (30)
- representative error cases: missing degree 422, missing uni 422, unknown degree
  404, unknown uni 404 (4)

Every response matched the production baseline on **exact status and full JSON
body**, so array order, repeated mapping rows, null omission, partner-unit
fallback, NUS units=4, tie order, full degree titles, university order, and
zero-count universities are all unchanged. Authenticated database access was
through the reader role (the server backs uvicorn with `reader_url`).

### Conclusion

The compatible core-readiness runtime (commit `af4d30e`) produces byte-identical
public API responses to the pre-change production baseline for all 41 captured
requests, confirming unchanged public behaviour. US1 localhost verification
(T022 + T023) is complete.
