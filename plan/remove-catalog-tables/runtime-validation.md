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

## Not run here (deferred)

- `test_json_repository.py` and the contract suite: unaffected by US1 runtime
  changes; covered by the final gate (T065).
- Full backend suite, lint/typecheck/build, and Playwright browser flows: the
  host is memory-critical. T021 (browser) and T065/T070 (full gate) must run when
  memory frees.
