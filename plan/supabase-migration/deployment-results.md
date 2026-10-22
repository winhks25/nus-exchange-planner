# Deployment results (T036-T038)

Generated: 2026-10-22

This file records the Phase 6 rollout evidence. Local checks are complete, but
the production configuration and deployment are blocked by missing Vercel
access. No deployment, production environment change or Supabase mutation is
claimed.

## Status

| Task | Scope | Status |
| --- | --- | --- |
| T036 | Configure backend Vercel runtime variables | Blocked: Vercel CLI is logged out and no project link or token exists |
| T037 | Deploy and smoke-check backend and frontend | Blocked: depends on T036 |
| T038 | Rehearse outage and JSON rollback locally | Complete; see below |

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
| Vercel authentication | Logged out |
| Vercel project link | None in the repository |
| Backend production origin | Not available |
| Frontend production origin | Not available |

The Supabase project URL and project ref are public identifiers. No credential,
connection string or password appears in this file.

## T036 configuration preflight

The runtime variables were prepared from `backend/.env.example`, but they cannot
be written to Vercel without an authenticated project link. The required target
configuration is:

| Variable | Required value | Current state |
| --- | --- | --- |
| `CATALOG_BACKEND` | `postgres` | Not set; Vercel project inaccessible |
| `DATABASE_URL` | `catalog_reader` URL on the transaction pooler | Not set; reader has no login |
| `DB_POOL_MIN_SIZE` | `0` | Documented, not set |
| `DB_POOL_MAX_SIZE` | `1` for serverless | Documented, not set |
| `DB_POOL_TIMEOUT` | `5` | Documented, not set |
| `DB_POOL_MAX_WAITING` | `16` | Documented, not set |
| `DB_CONNECT_TIMEOUT` | `5` | Documented, not set |
| `DB_STATEMENT_TIMEOUT_MS` | `5000` | Documented, not set |
| `DB_IDLE_IN_TRANSACTION_TIMEOUT_MS` | `5000` | Documented, not set |
| `CORS_ORIGINS` | Exact frontend production origin | Unchanged; origin unknown |
| `IMPORT_DATABASE_URL` | Must be absent from runtime | Confirmed absent from runtime config |

The read-only role currently has no login, so a deployed backend could not
connect even if the URL were configured:

| Check | Result |
| --- | --- |
| `catalog_reader` can select `public.module_mappings` | `true` |
| `catalog_reader` can select `public.catalog_source_snapshots` | `false` |
| `catalog_reader` can insert into `public.module_mappings` | `false` |
| `catalog_reader` can log in | `false` |

The frontend setting `NEXT_PUBLIC_API_BASE_URL` was not changed. It still points
at `http://localhost:8001`, and no frontend production deployment is known.
`CORS_ORIGINS` was not changed either.

### Region

The database is in `ap-southeast-2`. A Vercel backend in `sin1` (Singapore) is
the closest documented option. The existing project region could not be
inspected, so proximity is not verified.

### Blockers

1. `npx vercel@latest whoami` reports `Logged out`.
2. There is no `.vercel/` project link in the repository and no `VERCEL_TOKEN` in
   the environment.
3. No backend or frontend production URL is recorded anywhere in the repository.
4. The `catalog_reader` role still has `rolcanlogin=false`; its password must be
   provisioned outside the repository and stored only in the deployment secret.

No Vercel or Supabase production state was modified while establishing these
blockers. Completing T036 requires an operator to authenticate the CLI or link
the existing project, provision the reader password, and set the variables in the
project dashboard or through `vercel env add` with values supplied interactively.
Secrets must not be passed on the command line or committed.

## T037 deployment and smoke check

Not executed. Deployment cannot start until T036 supplies an authenticated Vercel
project with the runtime variables.

No production smoke result is claimed. The local release gate and target import
evidence remain the only completed verification:

| Check | Evidence |
| --- | --- |
| Phase 5 regression gate | `regression-results.md`: 198 checks passed |
| Target publication | `import-results.md`: batch `1`, 151 active mappings |
| Target reconciliation | `import-results.md`: 19/19 checks passed |
| API parity | `api-validation.md`: all degrees and 30 pairs compared |

The deployment smoke commands remain those in `quickstart.md`: check
`/api/v1/catalog`, `/api/v1/recommendations` and `/api/v1/mappings` on the
backend origin, then open `/` and `/mappings` on the frontend origin. Those URLs
do not exist yet.

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
