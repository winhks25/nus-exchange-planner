# Catalog Migration Quickstart

This page is the operator guide for the JSON-to-PostgreSQL catalog migration. It
covers local JSON and PostgreSQL runs, Supabase migrations and imports, runtime
configuration, checksum gates, failure diagnostics and manual rollback. The
automated regression gate is at the end.

The application has exactly two catalog modes. JSON mode reads the checked-in
snapshot in `data/`; PostgreSQL mode reads one completed, current import batch
through the read-only `catalog_reader` role. The mode is explicit. A database
failure returns 503 and never falls back to JSON.

## Prerequisites

- Python 3.12 or newer and `uv`
- Node.js 22 and npm
- PostgreSQL 15, 16 or 17 with `initdb`, `pg_ctl`, `psql` and `openssl` for
  local database runs and the regression gate
- Playwright Chromium for the browser gate
- Access to the Supabase project and the backend Vercel project for deployment

Install the local toolchain:

```bash
# macOS
brew install postgresql@15

# Ubuntu / Debian
sudo apt install postgresql postgresql-client openssl

cd backend && uv sync
cd ../frontend && npm ci && npx playwright install chromium
```

PostgreSQL binaries do not need to be on `PATH` on macOS; the test helper checks
the Homebrew versioned kegs. A missing toolchain makes the regression gate exit
nonzero instead of skipping database coverage.

## Environment files

Create local settings once:

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local
```

`./dev` sources both files, starts the API with reload on `API_PORT`, and then
starts Next.js on `FRONTEND_PORT`. Neither file is committed.

| Variable | Where | Purpose |
| --- | --- | --- |
| `CATALOG_BACKEND` | Backend | `json` or `postgres`; defaults to `json` |
| `DATABASE_URL` | Backend, server-only | Read-only runtime connection; required only in PostgreSQL mode |
| `IMPORT_DATABASE_URL` | Import shell only | Writer connection for migrations and imports |
| `DB_POOL_*`, `DB_CONNECT_TIMEOUT`, `DB_*_TIMEOUT_MS` | Backend | Bounded pool and query timeouts |
| `CORS_ORIGINS` | Backend | Comma-separated exact frontend origins |
| `NEXT_PUBLIC_API_BASE_URL` | Frontend | Public backend origin, without `/api/v1` |

Never put `DATABASE_URL`, `IMPORT_DATABASE_URL` or a role password in a
`NEXT_PUBLIC_*` variable. Only `NEXT_PUBLIC_API_BASE_URL` is browser-visible.

## Local JSON mode

JSON mode is the default and needs no database credentials. In `backend/.env`:

```dotenv
CATALOG_BACKEND=json
DATABASE_URL=
IMPORT_DATABASE_URL=
CORS_ORIGINS=http://localhost:3000
```

Run both servers:

```bash
./dev
```

Open `http://localhost:3000` and `http://localhost:3000/mappings`, or call the
API directly:

```bash
# All three routes must return 200 from the frozen snapshot.
curl -s http://localhost:8001/api/v1/catalog
curl -s 'http://localhost:8001/api/v1/recommendations?degree=Computer%20Science'
curl -s 'http://localhost:8001/api/v1/mappings?degree=Computer%20Science&uni=University%20of%20Toronto'
```

The snapshot has 6 degrees, 5 universities and 147 accepted mapping rows. Seven
raw Toronto rows are skipped by the legacy loader because their NUS code field
contains a course title instead of a code.

## Local PostgreSQL mode

### Disposable seeded database (recommended)

This wrapper creates a temporary TLS-enabled PostgreSQL cluster, applies every
migration, creates the separate importer and reader roles, publishes the reviewed
snapshot with the real importer, and serves the API through the read-only role.
Nothing in this path can reach Supabase.

```bash
# Terminal 1: API on 18765; CORS allows the frontend on 18766.
uv run --directory backend python -m scripts.serve_catalog_api --port 18765

# Terminal 2: frontend.
cd frontend
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:18765 npm run dev -- --port 18766
```

Open `http://127.0.0.1:18766`. The wrapper removes its database when stopped.

### An existing local database

Apply the reviewed migrations in order:

```bash
createdb nus_catalog_dev
for file in supabase/migrations/*.sql; do
  psql -X -v ON_ERROR_STOP=1 -d nus_catalog_dev -f "$file"
done
```

Provision a local reader login and a separate importer. The reader migration
creates `catalog_reader` without login on purpose; passwords are provisioned
outside migrations.

```bash
psql -X -v ON_ERROR_STOP=1 -d nus_catalog_dev <<'SQL'
alter role catalog_reader with login password 'local-reader-only';

do $$
begin
  if not exists (select 1 from pg_roles where rolname = 'catalog_importer') then
    create role catalog_importer
      login password 'local-import-only' bypassrls;
  end if;
end
$$;
grant usage on schema public to catalog_importer;
grant select, insert, update, delete on all tables in schema public to catalog_importer;
grant usage, select on all sequences in schema public to catalog_importer;
SQL
```

Import and reconcile as described in the next section, using the local importer
URL and `--target-project-ref local`:

```bash
export IMPORT_DATABASE_URL='postgresql://catalog_importer:local-import-only@127.0.0.1:5432/nus_catalog_dev'

uv run --directory backend python -m scripts.import_catalog \
  --dry-run --target-project-ref local

uv run --directory backend python -m scripts.import_catalog \
  --apply --target-project-ref local --confirm-project-ref local

uv run --directory backend python -m scripts.verify_catalog \
  --reconcile --target-project-ref local
```

Serve the imported database through the reader role:

```bash
export CATALOG_BACKEND=postgres
export DATABASE_URL='postgresql://catalog_reader:local-reader-only@127.0.0.1:5432/nus_catalog_dev?sslmode=require'
export CORS_ORIGINS=http://localhost:3000
uv run --directory backend uvicorn app.main:app --port 8001
```

The API forces `sslmode=require` for every connection. A local server used by the
API must therefore offer TLS; the disposable wrapper configures it
automatically. If your server has no TLS, use the wrapper rather than weakening
the runtime connection settings.

## Supabase migrations and roles

Use the Supabase CLI through `npx` so no global install is required:

```bash
npx supabase@latest login
npx supabase@latest link --project-ref wydziozsjibkvpgphpia
npx supabase@latest migration list
```

All three local versions must appear as applied remotely:

```text
20261022000100  create_exchange_catalog
20261022000200  prepare_catalog_import
20261022000300  catalog_reader
```

The initial migration was applied through the SQL Editor and was later recorded
with `npx supabase@latest migration repair 20261022000100 --status applied`
after a full schema comparison. Do not replay its `CREATE TABLE` statements.
Apply future migrations with `npx supabase@latest db push`.

Provision the runtime password once, as the project owner, from a password
manager or secret store:

```sql
alter role catalog_reader with login password '<generated-password>';
```

Store the resulting URL only in the backend deployment's server-side
`DATABASE_URL`. The username on the shared transaction pooler is role-qualified:

```text
postgresql://catalog_reader.<project-ref>:<password>@<pooler-host>:6543/postgres?sslmode=require
```

Use the host shown in the project's Connect dialog. The runtime must not use the
project owner or the importer credentials. Imports and migrations use a separate
`IMPORT_DATABASE_URL`, preferably a direct connection on port 5432 or the session
pooler.

Verify the split before deploying:

```sql
select has_table_privilege('catalog_reader', 'public.module_mappings', 'select');
select has_table_privilege('catalog_reader', 'public.catalog_source_snapshots', 'select');
select has_table_privilege('catalog_reader', 'public.module_mappings', 'insert');
```

The expected results are `true`, `false` and `false`.

## Import and checksum gates

Run every import from the repository root with the writer URL exported. The
command never prints the connection string.

```bash
export IMPORT_DATABASE_URL='<owner-or-importer-connection>'

# Inspect the target and checksums without writing.
uv run --directory backend python -m scripts.import_catalog \
  --dry-run --target-project-ref wydziozsjibkvpgphpia
```

Before applying, confirm the reviewed values:

| Gate | Expected |
| --- | --- |
| Source checksum | `b393cd0f6b34adb506a23ba810d65c083238339fab0b76a236167fdbef6901b9` |
| Repair checksum | `61268be6b39c1effc644d72c8cc4787287cdbcafc86d32fb3c48814d48064a3e` |
| Raw source rows | 154 |
| Active mappings | 151 (146 accepted, 5 repaired) |
| Quarantined rows | 3 |
| Degrees / universities | 6 / 5 |

Stop if a checksum or count differs from the reviewed evidence in
`data-deltas.md` and `import-results.md`. Publishing requires explicit apply and
an exact target confirmation:

```bash
uv run --directory backend python -m scripts.import_catalog \
  --apply \
  --target-project-ref wydziozsjibkvpgphpia \
  --confirm-project-ref wydziozsjibkvpgphpia
```

The importer takes an advisory transaction lock and writes the batch marker,
archives, source rows, entities, mappings, issues and repairs in one transaction.
It refuses a different published snapshot and never truncates existing tables. A
matching source and repair checksum returns `noop`.

Reconcile the published result read-only:

```bash
uv run --directory backend python -m scripts.verify_catalog \
  --reconcile --target-project-ref wydziozsjibkvpgphpia
```

The command prints a sanitized JSON report, including the current batch, row
outcomes, duplicate multiplicity and referential integrity. A successful target
run reports 19/19 checks and batch `1` with status `completed` and
`is_current=true`. Treat any other result as a deployment blocker.

## Runtime deployment configuration

The backend Vercel project uses the repository root. Set these server-only
variables in Production before deploying:

```dotenv
CATALOG_BACKEND=postgres
DATABASE_URL=postgresql://catalog_reader.<project-ref>:<password>@<pooler-host>:6543/postgres?sslmode=require
CORS_ORIGINS=https://<frontend-production-origin>
DB_POOL_MIN_SIZE=0
DB_POOL_MAX_SIZE=1
DB_POOL_TIMEOUT=5
DB_POOL_MAX_WAITING=16
DB_POOL_CLOSE_TIMEOUT=5
DB_POOL_MAX_LIFETIME=1800
DB_POOL_MAX_IDLE=300
DB_CONNECT_TIMEOUT=5
DB_STATEMENT_TIMEOUT_MS=5000
DB_IDLE_IN_TRANSACTION_TIMEOUT_MS=5000
```

Keep `IMPORT_DATABASE_URL` out of the runtime project. The defaults match this
list; the values are shown because deployment variables should be explicit.
`DB_POOL_MAX_SIZE=1` is the serverless default. Raise it only for a runtime that
keeps persistent workers, using the contention evidence in `performance.md`.

Place the backend in a region close to the Supabase database. The target project
is in `ap-southeast-2`; a Singapore (`sin1`) function region is the closest
Vercel option. Record the selected region in `deployment-results.md`.

The frontend keeps its existing public setting:

```dotenv
NEXT_PUBLIC_API_BASE_URL=https://<backend-production-origin>
```

Deploy in this order: import and reconcile, backend environment change, backend
deployment, backend smoke check, frontend check. Environment changes require a
redeployment in Vercel.

## Startup and failure diagnostics

Configuration is validated before the server serves traffic:

```text
CATALOG_BACKEND must be one of json, postgres; got an unknown value
DATABASE_URL is required when CATALOG_BACKEND=postgres
DATABASE_URL must use the postgres:// or postgresql:// scheme
DB_POOL_MAX_SIZE must be between 1 and 10
```

These messages never include a connection string or password. In PostgreSQL
mode, database failures are logged by operation and exception class only, for
example `Database query failed: OperationalError`. The API returns:

```json
{"detail": "Catalog data is unavailable. Please try again later."}
```

with status 503. An unpopulated or unpublished database, a paused project, an
expired pooler host, a missing reader login or a timeout all follow this path.
There is no automatic JSON fallback.

Smoke-check the deployed backend:

```bash
BASE=https://<backend-production-origin>

# Catalog options: 6 degrees, 5 universities.
curl -sS -w '\n%{http_code}\n' "$BASE/api/v1/catalog"

# One recommendation set.
curl -sS -w '\n%{http_code}\n' \
  "$BASE/api/v1/recommendations?degree=Computer%20Science"

# One mapping pair with repaired rows.
curl -sS -w '\n%{http_code}\n' \
  "$BASE/api/v1/mappings?degree=Computer%20Science&uni=University%20of%20Toronto"
```

Expected statuses are 200. Missing parameters return 422; unknown selections
return 404; a database outage returns 503. Afterwards open the frontend `/` and
`/mappings` pages and confirm the same counts.

Check the published batch directly when diagnosing a 503:

```sql
select id, status, is_current, source_checksum, repair_checksum
from public.catalog_import_batches
order by id;
```

## Manual rollback to JSON

Rollback is an explicit configuration change, not an automatic fallback.

1. In the backend Vercel project, set `CATALOG_BACKEND=json`.
2. Remove `DATABASE_URL` from the runtime project, or leave it in place knowing
   that JSON mode ignores it. Removing it prevents accidental reuse.
3. Redeploy the backend. No frontend change or redeployment is required.
4. Confirm `GET /api/v1/catalog` returns 200 with the frozen snapshot, and confirm
   the frontend `/` and `/mappings` pages load.
5. Leave the Supabase database untouched so PostgreSQL mode can be restored
   without another import.

JSON mode restores the checked-in snapshot, not the later database repairs. The
snapshot contains 147 accepted mappings and the original missing titles. The
published PostgreSQL batch contains 151 active mappings, five repaired rows and
three quarantined rows. In particular, the four Toronto pairs documented in
`data-deltas.md` return their pre-repair counts after rollback:

| Degree | University | JSON | PostgreSQL |
| --- | --- | ---: | ---: |
| Artificial Intelligence | University of Toronto | 9 | 10 |
| Business Analytics | University of Toronto | 18 | 19 |
| Computer Science | University of Toronto | 6 | 7 |
| Information Security | University of Toronto | 7 | 8 |

To roll forward, set `CATALOG_BACKEND=postgres`, restore the server-only
`DATABASE_URL`, redeploy the backend, and repeat the smoke checks. An identical
import is a no-op, so restoring PostgreSQL mode does not require re-importing.

For a local rehearsal, stop the disposable database behind the PostgreSQL API and
confirm the 503, restart it and confirm recovery, then stop the API and restart it
with `CATALOG_BACKEND=json` and no `DATABASE_URL`. The failure and recovery paths
are also covered automatically by `backend/tests/test_database_failures.py`.

## Regression gate

This gate proves the catalog still serves the reviewed JSON snapshot and the
imported PostgreSQL catalog correctly. It never connects to Supabase or any
developer database: every PostgreSQL run creates a temporary local cluster,
applies the migrations, publishes the reviewed source with the real importer and
drops the database when the process stops.

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

### Run individual checks

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

### Guardrails

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

- **503 in PostgreSQL mode:** confirm the batch is `completed` and `is_current`,
  the reader role can log in, the pooler host matches the current Connect dialog,
  and the runtime can reach `ap-southeast-2`. Do not switch to JSON automatically.
- **Configuration failure at startup:** fix the named variable. The error never
  echoes the value.
- **Count differs from JSON:** compare with `data-deltas.md`. Only the four
  documented Toronto pairs may change.
- **Missing PostgreSQL errors:** install the server package and confirm
  `initdb`, `pg_ctl` and `psql` exist. The tests do not skip when binaries are
  missing.
- **Port already in use:** stop the process using 18765, 18766 or 18767. The
  Playwright config never reuses an existing server.
- **Stale temporary cluster:** the gate removes its database and data directory
  on normal exit. If a run was killed with `SIGKILL`, remove leftover
  `${TMPDIR:-/tmp}/nus-catalog-pg-*` directories after confirming no PostgreSQL
  process is using them.
- **Browser missing:** run `npx playwright install chromium` in `frontend`.
- **Unexplained count change:** compare the response with
  `baseline-responses.json` and `data-deltas.md`. Only the four documented
  Toronto pair changes may differ in PostgreSQL mode.

## Evidence

- `baseline.md` and `baseline-responses.json`: frozen JSON behavior
- `schema-audit.md`: applied schema, migration history and role checks
- `import-results.md`: published batch, counts and reconciliation
- `api-validation.md`: JSON/PostgreSQL endpoint comparison
- `performance.md`: query plans and pool measurements
- `regression-results.md`: release-gate results
- `deployment-results.md`: deployment, smoke and rollback evidence
