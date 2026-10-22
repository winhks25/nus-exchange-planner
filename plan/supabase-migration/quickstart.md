# Migration Regression Quickstart

This gate proves the catalog still serves the reviewed JSON snapshot and the
imported PostgreSQL catalog correctly. It never connects to Supabase or any
developer database: every PostgreSQL run creates a temporary local cluster,
applies the migrations, publishes the reviewed source with the real importer and
drops the database when the process stops.

## Prerequisites

- Python 3.12 or newer, plus `uv`
- Node.js 22 and npm
- PostgreSQL 15, 16 or 17 with `initdb`, `pg_ctl`, `psql` and `openssl`
- Playwright Chromium

macOS (Homebrew):

```bash
brew install postgresql@15
cd backend && uv sync
cd ../frontend && npm ci && npx playwright install chromium
```

Linux (Debian/Ubuntu packages vary by release):

```bash
sudo apt install postgresql postgresql-client openssl
cd backend && uv sync
cd ../frontend && npm ci && npx playwright install chromium
```

PostgreSQL binaries do not need to be on `PATH` on macOS; the test helper checks
the Homebrew versioned kegs. If the toolchain is missing, the gate exits nonzero
instead of skipping database coverage.

## Run the gate

From the repository root:

```bash
./scripts/check-migration-regressions.sh
```

The script unsets `CATALOG_BACKEND`, `DATABASE_URL`, `IMPORT_DATABASE_URL`,
`TEST_DATABASE_URL` and `TEST_CATALOG_BACKEND` before starting, then runs:

1. All backend tests with `CATALOG_BACKEND=json`. This includes the import,
   repository-parity and failure regression suites, which create their own
   throwaway databases.
2. The full Playwright suite in JSON mode. `database-regression.spec.ts` is
   ignored in this mode.
3. The full Playwright suite in PostgreSQL mode. The backend web server is
   `backend/scripts/serve_catalog_api.py`, which seeds a temporary database with
   the reviewed importer and exposes it through the read-only runtime role.

Expected baseline on the reviewed source: 60 backend tests, 65 JSON browser
tests and 73 PostgreSQL browser tests, with zero failures and zero skips. The
exact run is recorded in `plan/supabase-migration/regression-results.md`.

## Run individual checks

Backend, including the database regression suites:

```bash
CATALOG_BACKEND=json uv run --directory backend pytest -q
```

Only the database-backed backend suites:

```bash
uv run --directory backend pytest -q \
  tests/test_import_regression.py \
  tests/test_repository_regression.py \
  tests/test_database_failures.py
```

JSON browser suite:

```bash
cd frontend
TEST_CATALOG_BACKEND=json npx playwright test
```

PostgreSQL browser suite with an automatically seeded local database:

```bash
cd frontend
TEST_CATALOG_BACKEND=postgres npx playwright test
```

Run only the PostgreSQL browser regression spec:

```bash
cd frontend
TEST_CATALOG_BACKEND=postgres npx playwright test tests/database-regression.spec.ts
```

The wrapper can also be started by hand while inspecting the API:

```bash
uv run --directory backend python -m scripts.serve_catalog_api --port 18765
```

## Guardrails

- `backend/tests/conftest.py` refuses a `TEST_DATABASE_URL` whose host is not
  `127.0.0.1`, `localhost` or `::1`.
- `frontend/playwright.config.ts` refuses the same non-local hosts and rejects
  unknown `TEST_CATALOG_BACKEND` values before any web server starts.
- JSON mode never reads the database, even when a database URL is present.
- PostgreSQL mode never falls back to JSON. An unpublished, paused or unreachable
  database produces a sanitized 503.
- `reuseExistingServer` is disabled, so Playwright fails if ports 18765, 18766 or
  18767 are already in use rather than testing an unknown process.

To use an already prepared disposable local database instead of the wrapper,
migrate and import it first, then set `TEST_DATABASE_URL` to a localhost URL
before running Playwright. The gate script intentionally ignores this variable
and always creates its own database.

## Troubleshooting

- **Missing PostgreSQL errors:** install the server package and confirm
  `initdb`, `pg_ctl` and `psql` exist. The tests do not skip when binaries are
  missing.
- **Port already in use:** stop the process using 18765, 18766 or 18767. The
  config never reuses an existing server.
- **Stale temporary cluster:** the gate removes its database and data directory
  on normal exit. If a run was killed with `SIGKILL`, remove leftover
  `${TMPDIR:-/tmp}/nus-catalog-pg-*` directories after confirming no PostgreSQL
  process is using them.
- **Browser missing:** run `npx playwright install chromium` in `frontend`.
- **Unexplained count change:** compare the response with
  `plan/supabase-migration/baseline-responses.json` and
  `plan/supabase-migration/data-deltas.md`. Only the four documented Toronto
  pair changes may differ in PostgreSQL mode.
