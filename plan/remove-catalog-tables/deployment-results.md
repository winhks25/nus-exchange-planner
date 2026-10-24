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


## T034–T038 — production deletion boundary

Date: 2026-10-24 (Asia/Singapore). The local US2 rehearsal (T029–T033) is
complete and green. T034 (read-only change-boundary recheck), T037 (the single
apply), and T038 (post-apply verification) are complete; T035 (full `pg_dump`
export) was skipped by operator decision in favour of a partial recovery capture.

### Execution path (operator decision)

The operator selected the Supabase MCP path over the CLI (`supabase db push`) and
the full `pg_dump` export:

1. **T035 export skipped.** The full `pg_dump` export + local restore rehearsal
   was skipped by operator decision. A minimal recovery capture (the
   `module_mappings.id → source_row_id` mapping, sequence state, and a manifest)
   was written to `PRIVATE_BACKUP_DIR` instead — see `recovery-validation.md`.
2. **T037 applied via MCP.** The reviewed DDL was applied through the Supabase
   MCP `apply_migration` tool (the CLI `db push --linked` path was not used). The
   MCP records migration history with its own generated version, which differs
   from the local file's `20261024034234` (recorded in T037 below).

### T034 — change-boundary recheck (read-only, completed)

Date: 2026-10-24 (Asia/Singapore). Recheck performed read-only through the
Supabase MCP connection. No production mutation was performed.

| Check | Expected | Observed | Result |
| --- | --- | --- | --- |
| Linked target | `wydziozsjibkvpgphpia` | `wydziozsjibkvpgphpia` | PASS |
| Applied migrations | `20261022000100`, `20261022000200`, `20261022000300` | exactly those three, in order | PASS |
| Pending migration | only `20261024034234_remove_catalog_metadata` | file present locally, not applied remotely | PASS |
| FKs into removal targets | 9 named constraints (per `schema-inventory.md`) | exactly those 9, none outside `public` | PASS |
| Archive-guard dependents | 4 triggers on `catalog_source_rows` / `catalog_source_snapshots` | exactly those 4, enabled | PASS |
| Public relations | 13 tables + 10 owned sequences; no view / MV / foreign / partitioned table | matches exactly | PASS |
| `module_mappings.source_row_id` | present, nullable `bigint`, FK + unique key | present | PASS |
| Baseline freshness (T008) | 13 table counts unchanged | all 13 match exactly | PASS |
| Active writers at boundary | none | none | PASS |
| T022/T023 localhost verification | PASS at `af4d30e` | recorded above | PASS |

All thirteen table counts match the T008 capture boundary exactly:
`catalog_import_batches`=1, `catalog_source_snapshots`=8,
`catalog_source_rows`=154, `catalog_issues`=34, `catalog_repairs`=44, `degrees`=6,
`nus_modules`=152, `degree_modules`=226, `specializations`=19,
`specialization_modules`=30, `partner_universities`=5, `pu_modules`=142,
`module_mappings`=151. No data changed since T008, so no new baseline version is
required.

**Go/no-go: GO.** The target, pending migration set, schema dependencies, and
baseline freshness all match the runbook's expectations, and the compatible
core-readiness runtime passed localhost verification (T022/T023). The operator
may proceed to T035 (consistent export) and T037 (apply). The operator must still
pause direct data edits / import jobs before the export and keep them paused
through T038. The export and apply remain operator-run under the
no-autonomous-prod-deploy rule and are not authorized by this record.

### T035 — consistent export (skipped by operator decision)

The full `pg_dump` export and local restore rehearsal were **skipped**. The
operator chose to apply via the Supabase MCP without the recoverable-backup
prerequisite. As a minimal safety net, the irrecoverable recovery data was
captured read-only before the apply and written to `PRIVATE_BACKUP_DIR`
(`/Users/winhtutkhaungsoe/Backups/nus-exchange-planner/catalog-removal-20261023`):

| File | Contents |
| --- | --- |
| `mapping-source-row-ids.csv` | `module_mappings.id → source_row_id` for all 151 mappings (skipped source rows 81, 82, 86) |
| `sequence-state.csv` | `last_value` for all 10 public sequences at the boundary |
| `partial-manifest.json` | capture timestamp, project ref, row counts, skipped-row note |

This is a data-only capture, not a restorable schema dump. The schema
(constraints, policies, triggers) and the five metadata tables' full contents are
not recoverable from it, so a restore rehearsal was not possible. This limitation
is recorded in `recovery-validation.md`.

### T036 — reviewed migration artifact

Reviewed SQL: `supabase/migrations/20261024034234_remove_catalog_metadata.sql`.
The reviewed DDL is byte-identical to the statements applied via MCP (only the
recorded history version differs — see T037).

| Property | Value |
| --- | --- |
| Reviewed against | `schema-inventory.md` (object list) + live dependency graph |
| Drop order | source_row_id unlink; issues, repairs; source_rows; snapshots; import_batches; reject function |
| Transaction | single transaction, `lock_timeout = '5s'`, RESTRICT (no CASCADE) |
| Historical migrations | three applied files byte-for-byte unchanged |
| Localhost runtime verified | T022/T023 PASS at `af4d30e` |

SQL digest (sha256 of the migration file):

```
sha256: d917d39c52fc28641253c131c6bde674a470f6bfeae053eb3fb61dbafec1c32d
```

### T037 — apply (completed via Supabase MCP)

| Item | Value |
| --- | --- |
| Applied | 2026-10-24 (Asia/Singapore), ~13:45 SGT (05:45 UTC) |
| Path | Supabase MCP `apply_migration` (not CLI `db push`) |
| Result | success — single transaction, no lock or dependency error |
| Recorded migration version | `20261024054553` (name `remove_catalog_metadata`) |

The MCP records migration history with its own generated version `20261024054553`,
which differs from the local file's `20261024034234`. The applied DDL is identical
to the reviewed migration file; only the bookkeeping version differs.

**Implication and remediation:** the local file
`20261024034234_remove_catalog_metadata.sql` no longer matches the remote
`supabase_migrations.schema_migrations` history, so a future
`supabase db push --linked` would treat `20261024034234` as pending and attempt to
re-apply it. Before any future CLI push, either mark it applied
(`supabase migration repair --status applied 20261024034234 --linked`) or rename
the local file to `20261024054553_remove_catalog_metadata.sql` to match the remote
history. Do not re-apply the DDL.

### T038 — immediate post-apply verification (completed)

Verified read-only immediately after the apply; the full record is in
`schema-validation.md`:

| Check | Result |
| --- | --- |
| Migration history | 4 versions; new version `20261024054553` recorded once |
| Five named tables absent | PASS |
| Unexpected `catalog_` tables | none (only the 8 retained `catalog_reader_select_*` policies remain) |
| `module_mappings.source_row_id` + FK + unique key | absent |
| `reject_catalog_archive_mutation()` | absent |
| 8 core tables present, RLS + one reader policy each | PASS |
| Core counts (6/152/226/19/30/5/142/151) | unchanged |
| Core sequences (degrees 6, module_mappings 151, partner_universities 5, pu_modules 142, specializations 19) | unchanged |
| Retained check constraints | all present (semantic) |

## Production outage after the apply (critical)

Immediately after the removal, the production backend
(`https://nus-exchange-planner-api.vercel.app`) returns
`503 {"detail":"Catalog data is unavailable. Please try again later."}` for
`/api/v1/catalog` and `/api/v1/recommendations`. The live Vercel backend is still
running the **pre-T014** code whose `_require_published_batch` query reads
`catalog_import_batches`, which is now dropped. The compatible core-readiness
runtime (T014) was verified only on localhost (T022/T023) and was never deployed,
so the "no app redeploy" assumption in the plan revision does not hold for the
live backend.

**Required fix (operator-run):** redeploy the backend with the compatible
core-readiness runtime (commit `af4d30e` or later), or switch the backend to
`CATALOG_BACKEND=json` with `DATABASE_URL` removed. Vercel CLI and credentials are
not available in this session. The frontend shell still serves (HTTP 200) but
cannot load catalog data until the backend is redeployed. See
`recovery-validation.md`.


---

## T073 — Localhost Runtime Verification (PostgreSQL and JSON Modes)

Date: 2026-10-24. Scope: Localhost execution of the tested cleanup version (commit `bf1b465`) across both supported backend modes. Per the 2026-10-24 revision, production redeployment to Vercel is out of scope.

### 1. PostgreSQL Mode Execution
- **Tested Commit:** `bf1b465`
- **Command:**
  ```bash
  CATALOG_BACKEND=postgres \
  DATABASE_URL="postgresql://catalog_reader:...@127.0.0.1:.../postgres" \
  CORS_ORIGINS="http://localhost:3000" \
  uv run --directory backend uvicorn app.main:app --host 127.0.0.1 --port 18880
  ```
- **Observations:**
  - Status: HTTP 200 on `/api/v1/catalog`.
  - Content: All 6 degrees and 5 partner universities returned.
  - CORS Header: `access-control-allow-origin: http://localhost:3000` (exact origin match).
  - Reader Role: Runtime operates under `catalog_reader` permissions without write access.
  - Target: Fresh final-schema core-seeded disposable database.
  - Absence of Importer: `IMPORT_DATABASE_URL` absent; zero metadata table queries made.

### 2. JSON Fallback Mode Execution
- **Command:**
  ```bash
  CATALOG_BACKEND=json \
  CORS_ORIGINS="http://localhost:3000" \
  uv run --directory backend uvicorn app.main:app --host 127.0.0.1 --port 18880
  ```
- **Observations:**
  - Status: HTTP 200 on `/api/v1/catalog`.
  - Content: Frozen catalog returned from `data/` snapshot.
  - Database Credentials: None provided or needed (`DATABASE_URL` absent).
  - CORS Header: `access-control-allow-origin: http://localhost:3000`.

### 3. Verification Conclusion
Both PostgreSQL and JSON runtime modes operate correctly on localhost with proper CORS handling, reader role least privilege, and zero dependency on the retired operational importer or dropped metadata tables.
