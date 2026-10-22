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

Pending. The rehearsal will use the disposable PostgreSQL wrapper, stop and
restart the database, verify the sanitized 503 and recovery, then switch the API
to JSON mode and compare the frozen snapshot with the published batch.
