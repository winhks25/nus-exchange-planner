# Deployment and target verification

Date: 2026-10-23 (Asia/Singapore). Scope: T004 read-only verification of the
linked Supabase target and the currently deployed origins. No production mutation
was performed.

## Verified target

| Item | Observed value | Evidence |
| --- | --- | --- |
| Linked project ref | `wydziozsjibkvpgphpia` | `supabase/.temp/project-ref`; `supabase/.temp/linked-project.json` |
| Linked project name | `nus-exchange-planner` | `supabase/.temp/linked-project.json` |
| Supabase API URL | `https://wydziozsjibkvpgphpia.supabase.co` | Supabase MCP project URL |
| Database | `postgres` | Read-only SQL via MCP |
| Server version | PostgreSQL `17.11` | Read-only SQL via MCP |
| Reported deployment database region | `ap-southeast-2` | `plan/supabase-migration/deployment-results.md` |
| Runtime role recorded by deployment | `catalog_reader` | `plan/supabase-migration/deployment-results.md` |

The historical project reference `wydziozsjibkvpgphpia` matches the actual linked
project. No target mismatch was found.

## Migration history

Read-only verification returned exactly three applied versions, matching the
checked-in migration files:

| Version | Name |
| --- | --- |
| `20261022000100` | `create_exchange_catalog` |
| `20261022000200` | `prepare_catalog_import` |
| `20261022000300` | `catalog_reader` |

The local `supabase/migrations/` directory contains the same three versions and no
pending local migration. The new removal migration does not exist yet (T027).

## Current production data boundary

Read-only counts at verification time:

| Object | Count |
| --- | ---: |
| `public.catalog_import_batches` | 1 |
| Completed/current batches | 1 |
| `public.catalog_source_snapshots` | 8 |
| `public.catalog_source_rows` | 154 |
| `public.catalog_issues` | 34 |
| `public.catalog_repairs` | 44 |
| `public.degrees` | 6 |
| `public.partner_universities` | 5 |
| `public.module_mappings` | 151 |

All five metadata tables and the eight core tables are present in `public` with
RLS enabled. This is the state the later export and removal tasks must preserve
and compare against.

## Deployed origins

| Item | Value | Check |
| --- | --- | --- |
| Backend production origin | `https://nus-exchange-planner-api.vercel.app` | `/api/v1/catalog` returned 200 |
| Backend OpenAPI | `https://nus-exchange-planner-api.vercel.app/openapi.json` | Returned 200 |
| Frontend production origin | `https://nus-exchange-planner-web.vercel.app` | `/` returned 200 |
| Backend mode indicator | PostgreSQL | `Artificial Intelligence / University of Toronto` returned 10 mapping rows, matching the repaired PostgreSQL catalog rather than the frozen JSON count of 9 |
| CORS | Exact frontend origin allowed | `Origin: https://nus-exchange-planner-web.vercel.app` returned `access-control-allow-origin` with that exact value |

The existing deployment record also lists backend project
`nus-exchange-planner-api`, frontend project `nus-exchange-planner-web`, and the
deployment IDs `nus-exchange-planner-3hir2iioj-…` (backend) and
`nus-exchange-planner-b64ftt60i-…` (frontend). Those are references, not a fresh
deployment performed by this task.

## CLI and access notes

- Supabase CLI was run through `npx --yes supabase@latest` at version `2.121.0`.
- `supabase migration list --linked` failed with
  `AccessTokenRequiredError` because no access token or login session is
  available in this environment.
- Remote identity, migration history, and counts were therefore read through the
  configured Supabase MCP connection. The MCP query path executed read-only SQL
  and printed no credentials, connection strings, or passwords.

## Checks before destructive work

The following must still be confirmed at the T034/T036 boundary:

1. The active backend deployment contains the compatible core-readiness runtime
   from T014; the existing record does not tie a Vercel deployment to a source
   commit.
2. The linked project has no pending migration other than the reviewed removal
   migration and no schema dependency unexpected by `schema-inventory.md`.
3. The production reader role still resolves to `catalog_reader` and has only the
   intended read access.
4. The T008 baseline remains fresh, or a new versioned baseline is captured
   before deletion.

No blocker prevents local preparation work. Production deletion remains gated on
the later tasks and is not authorized by this record.


## T022 — Compatible core-readiness runtime verified end-to-end on localhost

Date: 2026-10-24 (Asia/Singapore). Source commit: `af4d30ef2fd95495f48973a6394cd6abc9a07667`
(`af4d30e`), on `master`. No deployment was performed; this is a localhost-only
verification, as the plan now specifies (no Vercel deploy from T22 onward).

Host memory was critically low, so the heavy Next.js dev server was not started.
The frontend's browser-level parity against this exact core-seeded runtime was
already proven in T021 (8 PostgreSQL browser flows passed against
`scripts.serve_catalog_api`). T022's remaining obligation — that the compatible
core-readiness runtime serves the real contract through the reader role — was
verified directly against the live API.

### Runtime under test

- Server: `python -m scripts.serve_catalog_api --host 127.0.0.1 --port 18765`.
- It starts a disposable `PostgresCluster`, seeds the eight core tables with
  `seed_preview(build_preview())` (the core-only seeder, T018/T019 — no importer,
  no metadata tables), and backs uvicorn with `database.reader_url`.
- Environment started with `LC_ALL=C LANG=C` (macOS/Homebrew PostgreSQL 16 locale
  workaround).

### Running code is the T014 core-readiness implementation

`backend/app/repositories/postgres_catalog.py` at `af4d30e` uses the parameterless
`CORE_READINESS_SQL` executed inside each read transaction (lines 27, 228) and a
defensive re-check (lines 132–133). `PUBLISHED_BATCH_SQL` and
`_require_published_batch` are gone, and no `catalog_import_batches` query remains.
This is the T014 implementation, not the old publication-marker path.

### Runtime uses the reader role, not the owner

`serve_catalog_api.py` passes `DATABASE_URL = database.reader_url` to the uvicorn
child; the owner URL never leaves the parent process. The API therefore serves
every request through the read-only runtime role.

### Endpoint behaviour (against `http://127.0.0.1:18765/api/v1`)

| Request | Status | Observed |
| --- | ---: | --- |
| `GET /catalog` | 200 | 6 degrees, 5 universities |
| `GET /recommendations?degree=Artificial Intelligence` | 200 | #1 Toronto (10 partner / 6 distinct NUS / 10 mappings); Yonsei 4; Korea 2; Kyoto 1; UWA zero-count present |
| `GET /mappings?degree=Artificial Intelligence&uni=University of Toronto` | 200 | mapping rows returned with counts |
| `GET /recommendations` (no degree) | 422 | validation error |
| `GET /mappings?degree=Artificial Intelligence` (no uni) | 422 | validation error |
| `GET /recommendations?degree=<unknown>` | 404 | unknown selection |
| `GET /mappings?degree=Artificial Intelligence&uni=<unknown>` | 404 | unknown selection |

All catalog/recommendations/mappings and 404/422 behaviour match the captured
contract. The exact T023 baseline comparison (0 differences across 41 requests)
is recorded in `plan/remove-catalog-tables/runtime-validation.md`.

### Conclusion

The compatible core-readiness runtime (commit `af4d30e`) serves the full public
contract end-to-end on localhost through the reader role against a core-seeded
disposable PostgreSQL database, with no metadata tables and no importer. This
satisfies the T034 precondition that no active caller depends on the metadata
tables before their later deletion. There is no deployed artifact to recheck.


## T034–T038 — production deletion boundary (BLOCKED on operator)

Date: 2026-10-24 (Asia/Singapore). Source commit after US2 local work:
`949e506`. The local US2 rehearsal (T029–T033) is complete and green; the
production steps below are prepared but NOT executed from this session.

### Why not executed here

1. **No authenticated path.** `supabase migration list --linked` returns
   `Access token not provided` and `SUPABASE_ACCESS_TOKEN` is unset. The real
   export (T035) and the apply (T037) require an operator login this environment
   does not have.
2. **No-autonomous-prod-deploy rule.** Production DDL and the consistent export
   are user-run by standing policy. This session prepares and reviews; it does
   not apply.

### T034 — change-boundary recheck (to be run by operator)

Preconditions already satisfied locally:

- Compatible core-readiness runtime (commit `af4d30e`) passed localhost
  verification in T022/T023 — no active caller depends on the metadata tables.
  There is no deployed artifact to recheck.

Still to confirm against the live target at the boundary, per the runbook:

- Pause direct data edits / import jobs.
- Re-verify the linked target is `wydziozsjibkvpgphpia` and the pending-migration
  list contains exactly `20261024034234_remove_catalog_metadata`.
- Re-check schema dependencies against `schema-inventory.md` (no object outside
  the expected set depends on the five tables / the archive function).
- Confirm the T008 baseline is still fresh, or capture a new versioned baseline
  before deletion if data changed since.

### T035 — consistent export (operator)

Execute the export defined in `recovery.md` into `PRIVATE_BACKUP_DIR`: full
application schema/data, the `source_row_id` recovery mapping, sequence state, and
a redacted manifest (timestamps, counts, digests). Verify by restoring into an
isolated local database and comparing core/archive fingerprints. A file that
merely exists does not pass — the restore comparison is the gate.

### T036 — reviewed migration artifact

Reviewed SQL: `supabase/migrations/20261024034234_remove_catalog_metadata.sql`.

| Property | Value |
| --- | --- |
| Reviewed against | `schema-inventory.md` (object list) + live dependency graph |
| Drop order | source_row_id unlink; issues, repairs; source_rows; snapshots; import_batches; reject function |
| Transaction | single `begin/commit`, `lock_timeout = '5s'`, RESTRICT (no CASCADE) |
| Historical migrations | three applied files byte-for-byte unchanged |
| Pending set | exactly one migration (confirm with `db push --linked --dry-run`) |
| Localhost runtime verified | T022/T023 PASS at `af4d30e` |

SQL digest (sha256 of the migration file), for the operator to match before
apply:

```
sha256: d917d39c52fc28641253c131c6bde674a470f6bfeae053eb3fb61dbafec1c32d
```

(Recompute before apply: `shasum -a 256 supabase/migrations/20261024034234_remove_catalog_metadata.sql`.)

Execution prerequisite: operator authenticated (`supabase login` or
`SUPABASE_ACCESS_TOKEN`). If an approval mechanism blocks execution, report its
exact reason and preserve this reviewed artifact; do not bypass it or substitute
ad hoc destructive SQL.

### T037 — apply (operator runs)

```bash
npx --yes supabase@latest db push --linked --dry-run   # expect exactly 1 pending
npx --yes supabase@latest db push --linked             # apply once
npx --yes supabase@latest migration list --linked      # confirm recorded
```

Capture migration version, transaction result, timestamp, and redacted output
here. On a lock/dependency error, confirm rollback and investigate — do not retry
with CASCADE or overwrite migration history.

### T038 — immediate post-apply verification (operator)

Verify: migration history shows the one new version; the five named tables and
all unexpected `catalog_` tables are absent; `source_row_id` and the archive
function are gone; RLS/policies retained; core fingerprints/counts/IDs/sequence
state unchanged (compare to the T035 export). Record in `schema-validation.md`.
Keep writes paused until the data comparison and initial endpoint checks confirm
no retained data changed.