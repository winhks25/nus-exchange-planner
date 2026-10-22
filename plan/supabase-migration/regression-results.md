# Migration Regression Results

Final Phase 5 release-gate record for the JSON-to-PostgreSQL catalog migration.
No Supabase project or remote database was contacted.

## Run

- Tested commit: `2962e50` (`test: add one-command migration regression gate (T033)`)
- Run window: 2026-10-22T12:37:45Z to 2026-10-22T12:39:44Z
- Command: `./scripts/check-migration-regressions.sh`
- Exit status: 0
- Environment: macOS 26.5.1 on arm64

| Component | Version |
| --- | --- |
| PostgreSQL (disposable cluster) | 15.15 (Homebrew) |
| Python | 3.12.14 |
| uv | 0.13.0 |
| pytest | 9.1.1 |
| Ruff | 0.17.1 |
| psycopg / psycopg-pool | 3.3.6 / 3.3.3 |
| Node.js | 22.23.3 |
| npm | 10.9.9 |
| Playwright | 1.56.1 |
| Chromium | 141.0.7390.37 |

## Fixture and data

The gate creates a new local cluster, applies every migration, provisions the
separate importer and reader roles, publishes the reviewed source through the
real importer, and drops the database on exit.

| Item | Value |
| --- | --- |
| Source checksum | `b393cd0f6b34adb506a23ba810d65c083238339fab0b76a236167fdbef6901b9` |
| Repair checksum | `61268be6b39c1effc644d72c8cc4787287cdbcafc86d32fb3c48814d48064a3e` |
| Source files (including manifest) | 8 |
| Raw rows | 154 |
| Active mappings | 151 |
| Accepted rows | 146 |
| Repaired rows | 5 |
| Quarantined rows | 3 |
| Degrees / universities | 6 / 5 |
| NUS / partner modules | 152 / 142 |
| Specializations / memberships | 19 / 30 |
| Catalog repairs | 44 (24 verified, 20 unresolved) |
| Catalog issues | 34 (16 open, 9 resolved, 9 quarantined) |
| Changed degree/university pairs | 4 (rank changes: 0) |

## Results

| Stage | Command | Passed | Failed | Skipped |
| --- | --- | ---: | ---: | ---: |
| Backend (JSON plus database regression) | `CATALOG_BACKEND=json uv run --directory backend pytest -q` | 60 | 0 | 0 |
| Browser, JSON rollback | `TEST_CATALOG_BACKEND=json npx playwright test` | 65 | 0 | 0 |
| Browser, imported PostgreSQL | `TEST_CATALOG_BACKEND=postgres npx playwright test` | 73 | 0 | 0 |

Total: 198 checks passed, 0 failed, 0 skipped. The PostgreSQL browser run is the
65-test JSON suite plus the 8-test `database-regression.spec.ts`; JSON mode
ignores that spec.

Additional static checks passed:

- `uv run --directory backend ruff check app scripts tests`
- `cd frontend && npm run lint`
- `cd frontend && npm run typecheck`

### PostgreSQL behavior covered

- Complete raw-source byte/row accounting, import no-op, changed-snapshot
  refusal, concurrent importer serialization and injected-failure rollback.
- JSON/PostgreSQL parity for catalog, all six recommendation sets and all thirty
  mapping pairs. The only PostgreSQL differences are the four reviewed Toronto
  pairs: AI (10 mappings), Business Analytics (19), Computer Science (7) and
  Information Security (8). No ordering or rank changes.
- Unknown selections return 404, missing parameters 422, valid empty pairs 200
  with zero counts, and unpublished/unreachable databases 503 without JSON
  fallback.
- Statement timeout, pool exhaustion, paused-server recovery, pool shutdown
  cleanup, and reader-role write/archive denial.
- Browser direct entry, selection, URL state, back/forward, empty/error/loading
  states, rapid selection changes and a 390px mobile layout.

## Failures found and fixed

| Task | Failure | Fix |
| --- | --- | --- |
| T029 | Test importer role hit row-level security on insert, and the source-row assertion selected a nonexistent `source_order` column. | Test-only importer credentials now use `BYPASSRLS`; source rows assert the persisted `mapping_index` and values. |
| T030 | Synthetic JSON manifest used lowercase filenames while the files used university names, so startup rejected the fixture. | Manifest now lists the exact fixture paths. |
| T031 | Failure tests expected the database-specific 503 text instead of the shared catalog message; an invalid `sslmode` value only fails at connect time. | Assertions use the shared sanitized 503 detail; removed the non-failing conninfo assertion. |
| T032 | App router encodes spaces as `+`, and the original back/forward test assumed recommend-page state survives a return. | URL assertions parse `searchParams`; history coverage compares direct mapping URLs. |
| T032 | Playwright killed the database wrapper before its cleanup ran, leaving temporary clusters. | Added a 15-second `SIGTERM` graceful shutdown; subsequent runs left no processes or data directories. |

One early mobile browser run timed out while the Next dev server was warming.
The spec passed standalone, and all later full runs passed; no product change was
needed. Final gate runs had no retries and no skipped checks.

## Warnings

- Starlette reports that the current `TestClient` import path is deprecated in
  favor of `httpx2`. This does not affect the migration behavior.
- Next.js reports that the optional native SWC package is unavailable and uses
  its fallback. This is a local toolchain warning only.

## Deployment decision

The Phase 5 gate passes with no unexplained response changes. Production
deployment and the manual Supabase switch remain blocked until Phase 6 (T035-
T038) performs the reviewed deployment and rollback rehearsal.
