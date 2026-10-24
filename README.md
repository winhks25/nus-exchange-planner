# NUS Exchange Planner

A read-only tool for NUS School of Computing students to find exchange partners with module mappings. **Recommend** (`/`) ranks every partner by the number of distinct degree modules with a mapping. **Mappings** (`/mappings`) shows every qualifying mapping row for a degree and partner, including repeated NUS codes.

Production serves the catalog from Supabase PostgreSQL through the read-only `catalog_reader` role. Local development defaults to the checked-in JSON snapshot in `data/`, which is also the frozen manual-rollback release. The source is selected explicitly with `CATALOG_BACKEND=json|postgres`; a database failure returns a sanitized 503 and never falls back to JSON automatically. In PostgreSQL mode, the backend checks core readiness (at least one degree, one university, and no null degree full_title) before serving requests.

The reviewed PostgreSQL batch contains 154 raw source rows: 146 accepted, 5 repaired and 3 quarantined because their NUS code field contains a course title. It publishes 151 active mappings, including one verified unit repair. The frozen JSON snapshot still contains the original 147 accepted mappings and missing titles. Both are documented in [data deltas](plan/supabase-migration/data-deltas.md); unresolved names remain null and are never invented.

## Run locally

Install Python 3.12+, [uv](https://docs.astral.sh/uv/), Node.js 20.9+, and npm. From the repository root:

```sh
uv sync --directory backend
npm ci --prefix frontend
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local
./dev
```

After the first install, run only `./dev`. It starts both servers and stops the API when the frontend exits. Open `http://localhost:3000` and `http://localhost:3000/mappings`; the backend schema is at `http://localhost:8001/openapi.json`. Local settings are saved in ignored `backend/.env` and `frontend/.env.local`. Port 8001 avoids the other local server using port 8000. `CORS_ORIGINS` is a comma-separated list of exact frontend origins without trailing slashes. `NEXT_PUBLIC_API_BASE_URL` is the backend origin, without `/api/v1`.

`backend/.env.example` defaults to `CATALOG_BACKEND=json`, so local development needs no database credentials. To run PostgreSQL mode locally, use the disposable seeded database described in the [migration quickstart](plan/supabase-migration/quickstart.md) rather than pointing a developer shell at Supabase.

## Checks

```sh
uv run --directory backend pytest -q
uv run --directory backend ruff check .
npm run lint --prefix frontend
npm run typecheck --prefix frontend
npm run build --prefix frontend
npm run test:e2e --prefix frontend
```

Backend tests include import, repository-parity and failure suites that create disposable local PostgreSQL databases; install PostgreSQL 15-17 and `openssl`. Playwright starts isolated local servers on ports 18765, 18766 and 18767 and needs Chromium (`cd frontend && npx playwright install chromium`). Its frontend uses `.next-e2e/` so test bundles containing the temporary API address cannot overwrite the normal dev server's `.next/` output. You can keep `./dev` running during tests.

Run the complete release gate, which covers backend tests plus the browser suites in both JSON and imported PostgreSQL modes:

```sh
./scripts/check-regressions.sh
```

It never contacts Supabase or a developer database. Expected baseline and the latest evidence are in [regression results](plan/supabase-migration/regression-results.md).

## Catalog data and direct maintenance

Production catalog data resides in eight core tables in Supabase (`degrees`, `degree_modules`, `nus_modules`, `partner_universities`, `pu_modules`, `module_mappings`, `specializations`, `specialization_modules`). The previous operational importer and its metadata tables (`catalog_import_batches`, `catalog_source_snapshots`, `catalog_source_rows`, `catalog_issues`, `catalog_repairs`) have been permanently retired.

Updates are applied directly via SQL transactions against Supabase adhering to foreign-key constraints and core invariants (see [maintenance guide](plan/remove-catalog-tables/quickstart.md)). For local testing, disposable databases are seeded using `scripts.catalog_seed.seed_preview` from the reviewed preview.

```sh
# Reconcile a database against the reviewed preview (read-only):
uv run --directory backend python -m scripts.verify_catalog \
  --reconcile --target-project-ref wydziozsjibkvpgphpia
```

For disaster recovery, data snapshots, or manual rollback to the frozen JSON mode, refer to the [recovery runbook](plan/remove-catalog-tables/recovery.md).

Supabase migration history is maintained with the CLI:

```sh
npx supabase@latest migration list
```

The applied versions are `20261022000100` (initial catalog), `20261022000200` (import provenance), `20261022000300` (read-only runtime role), and `20261024034234` (`remove_catalog_metadata`). The initial migration was applied manually through the SQL Editor and later recorded with `migration repair` after a full schema comparison; never replay its `CREATE TABLE` statements. See [schema audit](plan/supabase-migration/schema-audit.md).

## Deploy on Vercel

Production is deployed as two Vercel projects: backend `nus-exchange-planner-api` (project root = repository root) and frontend `nus-exchange-planner-web` (project root = `frontend/`). The frontend uses `https://nus-exchange-planner-api.vercel.app` as its public API origin.

Deploy the backend first. The recognized FastAPI entry point is root `index.py` (with `api/index.py` also exporting the app); root `requirements.txt` supplies production dependencies and `.python-version` selects Python 3.12. Set the server-only `CATALOG_BACKEND=postgres`, `DATABASE_URL` for the `catalog_reader` transaction-pooler role and `CORS_ORIGINS` to the exact frontend origin. SQL migrations and direct administrative maintenance use separate admin credentials, never shared with the runtime. See [Vercel's FastAPI deployment guide](https://vercel.com/docs/frameworks/backend/fastapi) for project setup and [deployment results](plan/supabase-migration/deployment-results.md) for the recorded rollout.

Create the frontend project with root directory **`frontend/`** and the Next.js framework preset. Set `NEXT_PUBLIC_API_BASE_URL` to the stable backend production origin, then deploy. For previews, use a stable staging backend and set the frontend preview origin in that backend's `CORS_ORIGINS`; the backend does not use a wildcard CORS rule. Environment changes require redeployment.

## Mode changes and rollback

Production runs PostgreSQL. To roll back, set `CATALOG_BACKEND=json` in the backend project, remove `DATABASE_URL`, and redeploy the backend; no frontend change is needed. This serves the frozen JSON snapshot, not later database repairs, and the database remains intact for roll-forward. There is no automatic fallback in either direction. The exact steps, including the four Toronto pairs whose mapping counts revert, are in the [migration quickstart](plan/supabase-migration/quickstart.md#manual-rollback-to-json).

## Scope and limitations

See the [migration specification](plan/supabase-migration/spec.md), [implementation plan](plan/supabase-migration/plan.md), and [API contract](plan/contracts/openapi.yaml). The catalog has six SoC majors and five partners. The UI does not invent missing text: unresolved PostgreSQL titles stay null and three Toronto rows remain quarantined in the raw source archive rather than becoming mappings. Partner units are displayed only when present; NUS units display as 4 for compatibility. The hobby-plan deployment cannot select a function region near `ap-southeast-2`, and live cold-start/load behavior was not stress-tested.
