# Baseline and starting state

Date: 2026-10-23 (Asia/Singapore). Scope: Phase 1 setup and scope verification.

## Starting repository state (T001)

| Item | Value |
| --- | --- |
| Branch | `master` |
| Starting commit | `32833566669e88b89062b1c27e265d5657681a60` (`docs: record final migration validation (T040)`) |
| Tracked working tree | Clean; no staged or unstaged tracked changes |
| Unrelated untracked files | `.agents/`, `skills-lock.json` |
| Feature planning files | `plan/remove-catalog-tables/` (untracked at start) |
| Ignored local files present | `.env.local`, `backend/.env`, `.vercel/`, caches |

The untracked skill assets are user-owned inputs from the Supabase skill install and
are preserved unchanged. No tracked or staged user work was present, so Phase 1
does not need to stash or selectively stage around unrelated edits.

## Inputs read

- `plan/remove-catalog-tables/spec.md`, `plan.md`, `data-model.md`, and `tasks.md`
- `frontend/AGENTS.md` and the repository Supabase skill at `.agents/skills/supabase/SKILL.md`
- `plan/contracts/openapi.yaml`, current runtime repository, settings, and related tests
- Historical planning and deployment evidence under `plan/supabase-migration/`

No repository-level `AGENTS.md` exists outside `frontend/AGENTS.md`. The
`.specify/` directory, setup script, constitution, and hook registry are absent,
matching the planning note in `tasks.md`. No pre- or post-implementation hooks
are registered.

## Supabase guidance and CLI

Current guidance consulted on 2026-10-23:

- <https://supabase.com/docs/guides/platform/backups>
- <https://supabase.com/docs/guides/local-development/restoring-downloaded-backup>
- <https://supabase.com/docs/guides/platform/migrating-within-supabase/backup-restore>
- <https://supabase.com/docs/reference/cli/supabase-db-dump>

The `supabase` binary is not installed on `PATH`. CLI help was inspected through
`npx --yes supabase@latest` (version `2.121.0`):

- `supabase migration --help` exposes `list`, `new`, `repair`, and `up`.
- `supabase db dump --help` supports `--linked`, `--schema`, `--data-only`, and
  `--file`; the default dump includes schema and data.
- `supabase db push --help` supports `--dry-run`, `--linked`, and
  `--include-all`; `--dry-run` is the supported pending-migration preview.
- `supabase migration list --help` supports `--linked` and `--project-ref`.

The linked CLI call could not authenticate because no access token or login
session is available. Remote verification therefore used the configured Supabase
MCP connection and read-only SQL instead; no secret value was printed.

## Execution constraints carried into later tasks

- Production must not be mutated in Phase 1. All database inspection was read-only.
- The linked project must be re-checked at the change boundary because the current
  deployment record does not tie its Vercel deployment to a source commit.
- Local disposable PostgreSQL and Playwright dependencies are present; see the
  baseline checks section appended by T005.
- No operational command may depend on the five metadata tables after the removal
  migration is applied.

## Baseline checks before editing (T005)

All checks ran on 2026-10-23 before any implementation edit. The repository had
no tracked modifications at the time.

### Toolchain availability

| Tool | Version / availability |
| --- | --- |
| macOS | 26.5.1 (build 25F80) |
| git | 2.56.0 |
| uv | 0.13.0 |
| Python used by `uv` | 3.12.14 |
| Host `python3` | 3.14.2 |
| Node.js | 22.23.3 |
| npm | 10.9.9 |
| Playwright (local package) | 1.56.1 |
| Installed Playwright browsers | Chromium 1194 and 1243, headless shells, FFmpeg |
| PostgreSQL binaries | `initdb`, `pg_ctl`, and `psql` 15.15 (Homebrew) |
| OpenSSL | 4.0.3 |
| Supabase CLI | 2.121.0 through `npx --yes supabase@latest` |
| psycopg | 3.3.6 |

`uv`, Node, npm, Playwright, PostgreSQL, and OpenSSL are available. The Supabase
CLI is available only through `npx` and has no authenticated linked session, as
recorded in the target verification section above.

### Commands and results

| Command | Exit | Result |
| --- | ---: | --- |
| `bash scripts/check-migration-regressions.sh` | 1 | Backend and JSON browser suites passed; PostgreSQL browser suite had one failure |
| `npm --prefix frontend run lint` | 0 | ESLint completed with no reported problems |
| `npm --prefix frontend run typecheck` | 0 | `tsc --noEmit` completed |
| `npm --prefix frontend run build` | 0 | Next.js production build completed; routes `/`, `/mappings`, and `/_not-found` generated |
| `cd frontend && TEST_CATALOG_BACKEND=postgres npx playwright test tests/database-regression.spec.ts --reporter=line` | 0 | Isolated rerun: 8 passed in 1.5m |

The regression script unsets inherited `CATALOG_BACKEND`, `DATABASE_URL`,
`IMPORT_DATABASE_URL`, `TEST_DATABASE_URL`, and `TEST_CATALOG_BACKEND`, so it did
not contact a developer or production database.

### Regression script details

| Stage | Exit | Counts | Notes |
| --- | ---: | --- | --- |
| Backend pytest | 0 | 60 passed, 1 warning | Warning: Starlette deprecation recommending `httpx2` |
| JSON Playwright | 0 | 65 passed in 44.9s | `database-regression.spec.ts` is excluded by `playwright.config.ts` in JSON mode |
| PostgreSQL Playwright | 1 | 72 passed, 1 failed in 1.3m | Failure described below; all 73 tests were attempted |

Failure:

```text
tests/database-regression.spec.ts:48:5
degree selection navigates to imported Toronto recommendations

Locator: locator('.mapping-row')
Expected: 10
Received: 0
Timeout: 5000ms
at frontend/tests/database-regression.spec.ts:66
```

The URL assertion immediately before the row count passed, so the click and route
update occurred, but the mapping rows had not rendered within five seconds. The
same test passed when the PostgreSQL database-regression file was rerun alone
with one worker (8/8 passed). Because no source code changed between runs, this is
classified as a pre-existing timing flake under four-worker parallel load, not a
regression introduced by Phase 1.

### Skips and warnings

- Backend: no skipped tests.
- JSON browser mode: the PostgreSQL-only `database-regression.spec.ts` file is
  intentionally excluded by configuration.
- PostgreSQL browser mode: no skipped tests.
- Next.js reported that `@next/swc-darwin-arm64` was not installed and fell back
  to the available compiler path; the build still succeeded.
- Next.js warned that a `package-lock.json` exists above the repository root.
  This does not affect the build and is not a Phase 1 blocker.
- Starlette warned that `httpx` with `TestClient` is deprecated. This is existing
  dependency debt.

### Baseline conclusion

The backend, JSON browser behavior, lint, typecheck, and production build are
green. The current PostgreSQL browser gate is red only for one
`database-regression.spec.ts` case that passed in isolation. This failure must
not be hidden or weakened; T021 and T057/T069 should rerun the PostgreSQL flows
and investigate the timing before the final gate.

## Pre-change PostgreSQL API baseline (T008)

The dedicated pre-change baseline is
`plan/remove-catalog-tables/baseline-responses.json`. It is a new snapshot from
the verified PostgreSQL-backed production API, not a copy of the historical
JSON-only baseline in `plan/supabase-migration/baseline-responses.json`.

| Item | Value |
| --- | --- |
| Endpoint origin | `https://nus-exchange-planner-api.vercel.app` |
| Capture command | `uv run --directory backend python -m scripts.compare_api_baseline capture --base-url https://nus-exchange-planner-api.vercel.app --expected-origin https://nus-exchange-planner-api.vercel.app --timeout 10 --max-requests 200` |
| Baseline captured | `2026-10-23T14:42:17.452174+00:00` (Asia/Singapore: 22:42) |
| Request window | `2026-10-23T14:42:15.829126+00:00` to `2026-10-23T14:43:19.121088+00:00` |
| Requests captured | 41 read-only `GET` requests |
| Request bounds | 10-second timeout per request, 200-request ceiling, 2 MB response ceiling |
| Baseline bytes / SHA-256 | `102059` / `0f31a6e417ff4614464a95da578339a8c8c51b638f252a03d5f86a89b4ef7ee0` |
| Capture Git revision | `4d3442d189a0baddb03e80b60d040d4475a94d5c` |
| Mutation performed | None; the utility issues only bounded `GET` requests |

### Captured request set

| Case | Count | Parameters |
| --- | ---: | --- |
| Catalog | 1 | none |
| Recommendations | 6 | one request per discovered degree name |
| Mappings | 30 | every discovered degree/university pair |
| Error responses | 4 | two missing-parameter `422` cases and two unknown-selection `404` cases |

The six degrees and five universities were discovered from the production
catalog response, not hardcoded. Each case records its exact method, path,
parameters, URL, request timestamp, status, and parsed body. Arrays retain their
server order, and optional `title`/`units` fields retain their presence or
absence.

Representative error cases captured:

| Case | Status | Body detail |
| --- | ---: | --- |
| `missing_recommendation_degree` | 422 | `loc: ["query", "degree"]` |
| `missing_mapping_university` | 422 | `loc: ["query", "uni"]` |
| `unknown_degree` | 404 | `Unknown degree` |
| `unknown_university` | 404 | `Unknown degree or university` |

Valid empty pairs are part of the 30 mapping requests:
`Artificial Intelligence / University of Western Australia`,
`Computer Science / University of Western Australia`, and
`Computer Science / Yonsei University` all returned `200` with zero mappings.

### Endpoint mode and data boundary

The endpoint is PostgreSQL-backed. `Artificial Intelligence / University of
Toronto` returned `mapping_count=10`, `distinct_nus_module_count=6`, and
`partner_module_count=10`, matching the repaired PostgreSQL catalog rather than
the frozen JSON count of 9.

The read-only database boundary was checked immediately before and after the
capture through the configured Supabase MCP connection. The final boundary check
at `2026-10-23T14:49:34.660857+00:00` returned:

| Table | Rows | Table | Rows |
| --- | ---: | --- | ---: |
| `catalog_import_batches` | 1 | `degrees` | 6 |
| `catalog_source_snapshots` | 8 | `nus_modules` | 152 |
| `catalog_source_rows` | 154 | `degree_modules` | 226 |
| `catalog_issues` | 34 | `specializations` | 19 |
| `catalog_repairs` | 44 | `specialization_modules` | 30 |
| `partner_universities` | 5 | `pu_modules` | 142 |
| `module_mappings` | 151 | | |

Migration history remained `20261022000100`, `20261022000200`, and
`20261022000300`. The counts match the T006 inventory and the earlier T004
boundary, so the captured responses correspond to the recorded 151 mapping rows
and six degrees/five universities.

### Utility validation

Immediately after capture, comparison mode replayed all 41 requests against the
same endpoint and reported zero differences and zero request failures. A
deliberately altered temporary copy of the baseline produced one reported
difference and exit status 1 without modifying the baseline. Formal local-fixture
and post-deletion comparison remain T040-T042.
