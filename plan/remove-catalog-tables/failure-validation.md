# Failure and recovery validation (T045)

Date: 2026-10-24 (Asia/Singapore). Scope: isolated failure and recovery checks
on the final core-only schema. All checks ran locally against disposable
PostgreSQL clusters; production was not disrupted and no production write was
attempted.

## Command and result

```bash
LC_ALL=C LANG=C uv run --directory backend pytest -q tests/test_database_failures.py
# -> 13 passed, 1 warning (StarletteDeprecationWarning, pre-existing)
uv run --directory backend ruff check tests/test_database_failures.py
# -> All checks passed!
```

The `LC_ALL=C LANG=C` prefix is the known macOS/Homebrew locale workaround for
starting the disposable cluster; it is unrelated to the code under test.

## Coverage

| Required check | Test | Result |
| --- | --- | --- |
| Bounded pool timeout / concurrency | `test_single_connection_pool_bounds_concurrency_and_releases_afterwards` | PASS |
| Bounded statement timeout and recovery | `test_statement_timeout_returns_503_then_recovers` | PASS |
| Connection loss / paused server and recovery | `test_paused_server_returns_503_and_recovers` | PASS |
| Pool shutdown closes connections | `test_shutdown_closes_every_pooled_connection` | PASS |
| Unready core catalog returns sanitized 503 | `test_unready_core_catalog_returns_503_without_json_fallback` | PASS |
| Each unready condition (empty degrees, empty universities, null full title) | `test_each_unready_core_condition_returns_sanitized_503` | PASS |
| Denied required-table read returns sanitized 503 | `test_denied_required_table_read_returns_sanitized_503` (added) | PASS |
| No silent JSON fallback | `JsonCatalogRepository` monkeypatched to fail if constructed | PASS |
| Missing/unknown selections | `test_unknown_selections_and_missing_parameters` | PASS |
| Configuration failures without secret echo | `test_configuration_failures_are_explicit_and_never_echo_secrets` | PASS |
| Explicit JSON rollback path | `test_manual_json_rollback_serves_the_frozen_catalog_without_database` | PASS |
| Reader write denial / protected archives | `test_reader_role_cannot_write_or_read_protected_archives` | PASS (legacy pre-removal fixture; refactored in T056) |

### Added denied-read regression

`test_denied_required_table_read_returns_sanitized_503` creates a disposable
login role with no core-table `SELECT`, points the runtime at it, and asserts:

- `/api/v1/catalog` returns `503` with the fixed sanitized detail;
- no connection string, SQL, or `permission denied` text leaks in the body;
- `JsonCatalogRepository` is never constructed.

The role is dropped in a `finally` block, so the check leaves no cluster state.
The pool logs only the operation and exception class
(`Database catalog failed: InsufficientPrivilege`).

## No removed-table dependency

`grep -rn "catalog_import_batches\|catalog_source_rows\|catalog_source_snapshots\|catalog_issues\|catalog_repairs\|source_row_id" backend/app/`
returns no matches: the runtime never queries a removed relation and has no
`source_row_id` path.

Remaining references in `backend/scripts/verify_catalog.py` and
`backend/scripts/snapshot_core_data.py` belong to maintenance tooling, not the
runtime. `verify_catalog.py` is simplified under T050, and
`snapshot_core_data.py` keeps the optional recovery export only for a
pre-removal database (it refuses when the column is absent).

## Notes

- Write denial and privilege checks use local disposable roles, as required; no
  write was attempted against Supabase.
- `test_reader_role_cannot_write_or_read_protected_archives` still targets the
  legacy pre-removal fixture by design (T019). T056 repoints access-control
  coverage at the retained core tables and final-schema absence.
- The pre-existing Starlette/httpx deprecation warning is dependency debt and is
  not caused by this change.
