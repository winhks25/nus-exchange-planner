# Deployment results (T036-T038)

Generated: 2026-10-22

This file records the Phase 6 rollout evidence, including the completed
production configuration, deployment and smoke checks in T036/T037, and the
local outage rollback rehearsal in T038. The backend and frontend Vercel
projects were newly created with the operator's consent because no existing
NUS Exchange Planner project could be found in the Vercel account.

## Summary

| Task | Scope | Status |
| --- | --- | --- |
| T036 | Configure backend Vercel runtime variables | Complete: backend project created, runtime variables set, reader role provisioned |
| T037 | Deploy and smoke-check backend and frontend | Complete: production deploys verified against the published batch |
| T038 | Rehearse outage and JSON rollback locally | Complete: sanitized 503, recovery and JSON rollback verified |

## Target identifiers

| Item | Value |
| --- | --- |
| Supabase project ref | `wydziozsjibkvpgphpia` |
| Supabase API URL | `https://wydziozsjibkvpgphpia.supabase.co` |
| Supabase database region | `ap-southeast-2` (Sydney), from the pooler host |
| PostgreSQL version | 17.11 |
| Current import batch | `1`, `completed`, `is_current=true` |
| Source checksum | `b393cd0f6b34adb506a23ba810d65c083238339fab0b76a236167fdbef6901b9` |
| Repair checksum | `61268be6b39c1effc644d72c8cc4787287cdbcafc86d32fb3c48814d48064a3e` |
| Runtime role | `catalog_reader` |
| Vercel CLI | 65.1.0 |
| Vercel team | `win-htut-s-projects` |
| Backend project | `nus-exchange-planner-api` (Vercel root = repository root) |
| Frontend project | `nus-exchange-planner-web` (Vercel root = `frontend/`) |
| Backend production origin | `https://nus-exchange-planner-api.vercel.app` |
| Frontend production origin | `https://nus-exchange-planner-web.vercel.app` |

The Supabase project URL, project ref and Vercel origins are public
identifiers. No credential, connection string or password appears in this
file; the generated reader password and its URL exist only in the deployment
secret and were never printed or committed.

## T036 runtime configuration

The Vercel account had no existing NUS Exchange Planner project, so T036 created
`nus-exchange-planner-api` (linked at the repository root) and linked
`nus-exchange-planner-web` (linked in `frontend/`) after the operator consented.
The following server-only Production variables were applied to the backend
project, matching `backend/.env.example`:

| Variable | Value |
| --- | --- |
| `CATALOG_BACKEND` | `postgres` |
| `DATABASE_URL` | `catalog_reader.<project-ref>` URL, transaction pooler port 6543, `sslmode=require` |
| `DB_POOL_MIN_SIZE` | `0` |
| `DB_POOL_MAX_SIZE` | `1` (serverless default) |
| `DB_POOL_TIMEOUT` | `5` |
| `DB_POOL_MAX_WAITING` | `16` |
| `DB_POOL_CLOSE_TIMEOUT` | `5` |
| `DB_POOL_MAX_LIFETIME` | `1800` |
| `DB_POOL_MAX_IDLE` | `300` |
| `DB_CONNECT_TIMEOUT` | `5` |
| `DB_STATEMENT_TIMEOUT_MS` | `5000` |
| `DB_IDLE_IN_TRANSACTION_TIMEOUT_MS` | `5000` |
| `CORS_ORIGINS` | `https://nus-exchange-planner-web.vercel.app` |

`IMPORT_DATABASE_URL` is confirmed absent from the runtime project. One
misplaced `NEXT_PUBLIC_API_BASE_URL` was added to the backend project while the
shell was at the repository root; it was removed and the backend was redeployed
without it. The frontend project Production variable is:

| Variable | Value |
| --- | --- |
| `NEXT_PUBLIC_API_BASE_URL` | `https://nus-exchange-planner-api.vercel.app` |

The read-only role was provisioned with a generated login password outside any
migration or repository file:

| Check | Result |
| --- | --- |
| `catalog_reader` can log in | `true`, password provisioned with `alter role` |
| Live reader connection sees catalog | 6 degrees, 5 universities, 151 mappings, batch `1` completed/current |
| `select` from `catalog_source_snapshots` | denied (`42501`) |
| `insert` into catalog tables | denied (`25006` runtime read-only; `has_table_privilege ... 'insert'` is `false`) |

### Region

The database is in `ap-southeast-2`. The Vercel project is on the hobby plan,
which does not expose function region selection (`inspect --json` reports no
region). Observed warm p95 latency from `curl` including TLS setup was about
1.5-1.9 seconds per request. Record this distance as a known limitation; a
function region near Sydney should be chosen when the account plan allows.

## T037 deployment and smoke checks

Production deployments after the T036 configuration:

| Deployment | Description | Production URL | Timestamp (UTC) | Status |
| --- | --- | --- | --- | --- |
| `nus-exchange-planner-3hir2iioj-…` |Backend, final (CORS applied) | `https://nus-exchange-planner-api.vercel.app` | 2026-10-22T13:28:43Z | Ready |
| `nus-exchange-planner-b64ftt60i-…` | Frontend Next.js build | `https://nus-exchange-planner-web.vercel.app` | 2026-10-22T13:29:12Z | Ready |

Two earlier backend deployments, `2mch9o1z4` and `6qk4vgxul`, are superseded by
`3hir2iioj`.

### Backend smoke evidence

All checks were made against the live production URL with the full import batch
published in Supabase.

| Check | Expected | Result |
| --- | --- | --- |
| `GET /api/v1/catalog` | 200, source order | 200; 6 degrees, 5 universities; full titles present as the `degree` field, matching the baseline shape |
| `GET /api/v1/recommendations?degree=Computer Science` | 200 | 200; Toronto first with 7/3/7 |
| `GET /api/v1/mappings?degree=Computer Science&uni=University of Toronto` | 200, 7 rows | 200; 7 mapping rows, 7 partner modules, 3 distinct NUS modules, including the verified `0.5` unit repair |
| Unknown degree mappings | 404 | 404 |
| Missing `degree` parameter | 422 | 422 |
| Valid-empty pair, Computer Science / Yonsei | 200 | 200 |

### Frontend smoke evidence

| Check | Expected | Result |
| --- | --- | --- |
| `GET /` | 200 | 200 |
| `GET /mappings` | 200 | 200 |
| Origin allowed by backend CORS | exact origin | `Origin: https://nus-exchange-planner-web.vercel.app` on `/api/v1/catalog` returns 200 |
| Browser bundle API base | production origin | The deployed Next.js chunks contain `nus-exchange-planner-api.vercel.app` and no `localhost:8001` fallback |

The production responses match the reviewed PostgreSQL batch: the four repaired
Toronto pairs appear in PostgreSQL mode (Artificial Intelligence 10, Business
Analytics 19, Computer Science 7, Information Security 8) and were exercised on
the deployed instance via the mappings smoke checks.

### Remaining issues

- Function-to-database latency is limited by the non-selectable hobby-plan
  function region and the `ap-southeast-2` database.
- Quota/limits and cold-start behavior were not stress-tested on the live
  deployment; measurements in `performance.md` cover contention locally.

## T038 local outage and rollback rehearsal

Completed on 2026-10-22 at approximately 12:57 UTC against a disposable local
PostgreSQL 15 cluster. The rehearsal used the same migrations, importer and
read-only runtime role as `quickstart.md`; no Supabase project was contacted.

### Procedure

1. Create a temporary TLS-enabled cluster, apply all three migrations, and
   publish the reviewed snapshot through `catalog_importer`.
2. Start uvicorn with `CATALOG_BACKEND=postgres`, `DATABASE_URL` set to the
   `catalog_reader` URL, and no `IMPORT_DATABASE_URL` in the process.
3. Confirm `GET /api/v1/catalog` returns 200 with 6 degrees and 5 universities.
4. Pause the PostgreSQL server and request the catalog again.
5. Resume the same server and retry on the unchanged uvicorn process.
6. Stop the API, remove `DATABASE_URL`, and start it with
   `CATALOG_BACKEND=json`.
7. Confirm the JSON catalog is served and compare the four repaired Toronto
   pairs with the PostgreSQL responses.
8. Stop the API and delete the temporary cluster.

### Results

| Step | Status | Evidence |
| --- | --- | --- |
| PostgreSQL catalog before outage | 200 | 6 degrees, 5 universities |
| Database paused | 503 | `{"detail":"Catalog data is unavailable. Please try again later."}` |
| Recovery after resume | 200 | Same uvicorn process, no restart |
| JSON rollback | 200 | 6 degrees, 5 universities |
| Cleanup | complete | Port 18801 free; no temporary cluster left |

The outage log contained only `Database catalog failed: PoolTimeout`. It did not
contain a connection string, role name or password. The API returned no JSON
catalog while the database was unavailable, so no automatic fallback occurred.

### Data-version differences

| Degree / University | JSON mapping rows | PostgreSQL mapping rows |
| --- | ---: | ---: |
| Artificial Intelligence / Toronto | 9 | 10 |
| Business Analytics / Toronto | 18 | 19 |
| Computer Science / Toronto | 6 | 7 |
| Information Security / Toronto | 7 | 8 |

Partner-module counts follow the mapping rows. Distinct NUS counts are unchanged
at 6, 9, 3 and 5 respectively. Rollback therefore restores the frozen 147-row
snapshot and removes the four repaired rows; it does not undo later database
changes, because it does not use the database at all.

### Rollback and roll-forward steps

Local:

```text
stop the PostgreSQL API
set CATALOG_BACKEND=json and unset DATABASE_URL
start uvicorn again
confirm /api/v1/catalog is 200 with the frozen snapshot
```

Production, once T036 unblocks access:

```text
set CATALOG_BACKEND=json in the backend Vercel project
remove DATABASE_URL from the runtime project
redeploy the backend; no frontend change is needed
confirm the backend catalog and both frontend pages
```

Roll forward by setting `CATALOG_BACKEND=postgres`, restoring the server-only
`DATABASE_URL`, and redeploying. The database remains intact throughout, and an
identical import is a no-op, so no re-import is required.

The frozen JSON snapshot remains deployable: it started successfully during the
rehearsal without any database credentials and served the expected catalog.
