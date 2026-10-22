# Tasks: Supabase catalog migration

Date: 2026-10-22. Status: implementation in progress; Phase 1, Phase 2 and Phase 4
complete; Phase 3 importer and target publication pending.

Sources: [spec.md](spec.md), [plan.md](plan.md), the applied migration in
supabase/migrations/20261022000100_create_exchange_catalog.sql, and
plan/contracts/openapi.yaml. All checklist paths are repository-relative.

Confirmed decisions: preserve current UI/API behavior; research official sources
to repair data; explicitly select database mode with manual JSON rollback.
The current baseline has 6 degrees, 5 universities, 154 source mapping rows,
147 accepted mappings and 7 missing course-title occurrences. Recompute these
before implementation. Repairs may legitimately change the accepted-row count.

Workflow adaptation: `.specify/` is absent; its setup command was attempted and
failed because the script does not exist. No setup template, constitution, or
extension-hook registry is available. This file follows the skill's phase and
checklist format in the repository's established plan directory. No unrelated
feature's spec/plan is treated as the migration specification. The user explicitly requested automated regression coverage; Phase 5 adds new
test suites alongside existing checks and import/reconciliation utilities.

## Phase 1: Setup

- [X] T001 Inspect working changes, existing schema evidence and API behavior; capture Git revision, source checksums, existing check outcomes, and current endpoint responses for all six degrees and thirty degree/university pairs in plan/supabase-migration/baseline.md and plan/supabase-migration/baseline-responses.json, without overwriting user work or exposing credentials.
- [X] T002 Inspect project wydziozsjibkvpgphpia through available Supabase tooling, compare table/constraint/index/RLS definitions against supabase/migrations/20261022000100_create_exchange_catalog.sql, and record drift plus migration-history status in plan/supabase-migration/schema-audit.md; reconcile the manually applied migration using the supported CLI history-repair command only after verifying equivalence, never replay its CREATE TABLE statements against the existing schema.
  - Status: complete. The remote schema matches with no drift; local and remote history both report `20261022000100` after the CLI repair. Evidence is in schema-audit.md.
- [X] T003 Consult current official Supabase connection, Psycopg 3 pool/TLS, and migration-history documentation; record linked implementation decisions, timeout values and supported package versions in plan/supabase-migration/research.md, including transaction-pooler prepared-statement restrictions and the separate runtime/import credentials.

## Phase 2: Foundation

Goal: establish configuration and schema support before data publication or API changes.

- [X] T004 Add compatible pinned Psycopg 3 binary/pool dependencies through backend/pyproject.toml, regenerate backend/uv.lock, and synchronize deployment dependencies in requirements.txt; verify both installation paths can import the selected driver and pool.
- [X] T005 Implement explicit CATALOG_BACKEND=json|postgres configuration in backend/app/settings.py and document placeholders in backend/.env.example: default json during transition, reject unknown mode, require DATABASE_URL only for postgres, separate import credentials, validate bounded pool/timeouts, and redact secrets in all errors; retain existing local environment loading via dev.
- [X] T006 Implement bounded synchronous connection pooling in backend/app/database.py with TLS and prepared-statement settings from research.md, short read-only transactions, connection/pool/statement timeouts, shutdown cleanup and sanitized operational errors; keep all network access out of module import.
- [X] T007 Create supabase/migrations/20261022000200_prepare_catalog_import.sql as an additive follow-up: degree full title/source order, nullable module names and verified units, specialization kind, immutable raw source snapshots, import batches, source-addressed issues/repairs, source-row mapping identity/order and row-specific presentation; enforce foreign keys, repeat-import uniqueness and nonblank known values, preserve repeated equivalent pairs at different source indexes, and enable RLS on every new table.
- [X] T008 Create supabase/migrations/20261022000300_catalog_reader.sql and credential-provisioning instructions in supabase/README.md for a dedicated non-owner, non-BYPASSRLS runtime role with only required schema usage/table SELECT privileges and corresponding SELECT policies; deny writes, raw archives and issue tables, retain no browser policies, and keep passwords out of migrations; give imports separate credentials.
- [X] T009 Apply the new migrations to an isolated PostgreSQL validation database before Supabase, inspect resulting constraints/policies, then apply them to the verified Supabase project and record execution/history evidence in plan/supabase-migration/schema-audit.md; confirm the actual runtime role can read intended tables and cannot mutate them or read archives.

Gate: original deployed schema remains intact, new schema is verified, roles are separated,
and settings support JSON mode without database credentials. US1 and US2 construction
can now progress independently, but US2 parity verification requires US1 publication.

## Phase 3: US1 — Traceable, repeatable data migration (P1; MVP)

Goal: migrate all source information, repair what official evidence supports, and
publish usable normalized data without silently losing unresolved records.

Independent acceptance: reconcile every input file and all 154 original mapping rows;
every row is active or has an explicit issue. Verify relationships, source checksums,
names/units, specializations, duplicates, and raw metadata. Repeat the exact import:
no additional rows or modified identities. Inject a local import failure: no partial
publication. JSON API remains usable throughout this story.

- [X] T010 [US1] Implement a read-only inventory in backend/scripts/audit_catalog.py over data/majors/nus_soc_majors.json and every data/mapping/**/*.json file, using backend/app/course_codes.py semantics; list missing titles, invalid codes, repeated pairs, missing metadata, and code/title/unit conflicts with exact file and JSON pointer, and output plan/supabase-migration/data-audit.json plus SHA-256 checksums.
- [X] T011 [US1] Research each inventoried issue using official NUS curriculum/course sources and the relevant partner's official course/mapping sources; record before/after values, exact source URL, accessed date, applicable academic year, evidence, and unresolved status in data/repairs/catalog_repairs.json and plan/supabase-migration/repair-report.md; do not infer exchange equivalence from a course-name match or overwrite original JSON.
- [X] T012 [US1] Extend backend/scripts/audit_catalog.py to produce a deterministic corrected import preview, retaining raw source content; leave unknown names/units/faculty/city null, quarantine invalid codes not verified by research, reject unexplained conflicting metadata, and report every repair-induced change to counts or rankings in plan/supabase-migration/data-deltas.md.
- [X] T013 [US1] Implement entity/member transformation in backend/scripts/import_catalog.py: six degree names/full titles/faculty, all codes discovered by the legacy extractor, shared degree memberships, five partners, partner-scoped course identities, and known names/units; preserve course-code display independently of case-insensitive identity when needed, and do not label every course in an OR/choose-one group as compulsory.
- [X] T014 [US1] Add source-listed specialization and CS focus-area import to backend/scripts/import_catalog.py, using specialization kind and degree-specific identity; import only explicit memberships, preserve degree eligibility exactly as the legacy extractor computes it, retain unknown membership notes, and ensure specialization joins never multiply mapping counts.
- [X] T015 [US1] Add raw snapshots, mapping rows, repair/issue provenance and row-specific presentation to backend/scripts/import_catalog.py; archive exact file text plus parsed JSON/checksum, retain all curriculum notes and metadata, preserve each duplicate pair by source position, and reconcile original rows as accepted/repaired/quarantined rather than silently discarding them.
- [X] T016 [US1] Add --dry-run and explicit --apply to backend/scripts/import_catalog.py, require target-project confirmation through CLI parameters, use an advisory transaction lock and one transaction, commit the completed-import marker with all rows, and make matching source+repair checksums a no-op; refuse a different published snapshot without an explicit future refresh workflow and never truncate existing tables.
- [X] T017 [P] [US1] Implement reconciliation in backend/scripts/verify_catalog.py using the finalized import schema: compare source checksums, entity/link counts, per-source mapping outcomes, duplicate multiplicity, optional metadata, and published-batch status; print a sanitized machine-readable report and fail on unexplained loss, orphans or missing publication markers.
- [X] T018 [US1] Exercise dry-run, initial import, identical rerun, and forced failure against isolated PostgreSQL using backend/scripts/import_catalog.py and backend/scripts/verify_catalog.py; then import into the target Supabase project and record final counts, unresolved issues, reconciliation results and batch/checksum identifiers in plan/supabase-migration/import-results.md.

Checkpoint: data is available and verified in Supabase; the application still runs JSON.
This is the smallest useful deliverable, not completion of backend integration.

## Phase 4: US2 — PostgreSQL-backed API (P1)

Goal: serve existing routes from PostgreSQL while preserving the agreed behavior.

Independent acceptance: compare catalog, six recommendation responses and all thirty
mapping responses to baseline plus documented repairs; exercise 404, 422, valid-empty,
503 and database recovery. Verify no complete catalog is loaded into Python and no
query-per-university pattern is used for ranking. Existing frontend flows pass.

- [X] T019 [US2] Define an injectable repository interface and shared not-found/unavailable errors in backend/app/repositories/base.py for catalog options, rankings and mapping results, preserving backend/app/models.py response types and leaving SQL details outside route handlers.
- [X] T020 [P] [US2] Implement backend/app/repositories/json_catalog.py around backend/app/catalog.py, backend/app/matching.py and backend/app/recommendations.py; preserve fixture injection through create_app(data_root, manifest), startup validation and original JSON semantics without requiring DATABASE_URL.
- [X] T021 [P] [US2] Implement backend/app/repositories/postgres_catalog.py with parameterized catalog queries, persisted source order/full degree titles and completed-import checks; an unpopulated/unpublished database is unavailable, not a misleading empty catalog; do not select raw archives or load all mappings.
- [X] T022 [US2] Add a set-based ranking query in backend/app/repositories/postgres_catalog.py that validates degree existence, includes zero-count partners, counts distinct NUS/partner codes separately from mapping rows, prevents membership-join duplication, and reproduces Python's descending-count/name ordering including collation-sensitive ties.
- [X] T023 [US2] Add filtered mapping queries in backend/app/repositories/postgres_catalog.py that validate both selections, return all qualifying rows without pagination, preserve repeats, use uppercase NUS code plus source position for stable sorting, maintain optional title/unit serialization and NUS displayed units=4, and retain valid-empty results with correct distinct counts.
- [X] T024 [US2] Wire repository selection and pool lifecycle into backend/app/main.py; preserve query names/routes/status codes/CORS, adapt missing-data errors to existing 503 responses, keep configuration failures distinguishable from transient outages, and ensure postgres failures never activate the JSON adapter.
- [X] T025 [US2] Extend backend/scripts/verify_catalog.py to compare actual API responses across both modes and against plan/supabase-migration/baseline-responses.json, allowing only enumerated verified repairs from data-deltas.md; cover catalog order, all pairs, ties, repeated rows, null fields, missing/unknown parameters, unavailable database and recovery, and record results in plan/supabase-migration/api-validation.md.
- [X] T026 [US2] Run existing backend/tests/test_catalog.py and backend/tests/test_contract.py plus Ruff; explicitly select JSON for legacy fixture tests so shell settings cannot redirect them to production, update only evidence-backed assertions, and run existing frontend/tests/flows.spec.ts against a disposable PostgreSQL-backed local setup; record commands/results in plan/supabase-migration/api-validation.md.
- [X] T027 [US2] Inspect representative EXPLAIN plans and measure request latency/pool contention using backend/scripts/verify_catalog.py against a disposable enlarged dataset; document query plans, dataset size, concurrency, timings and limitations in plan/supabase-migration/performance.md, adding a forward SQL migration only if evidence shows a missing index; do not run synthetic data generation in production.

Checkpoint: both modes work locally and repaired-data differences are fully explained.

## Phase 5: Regression tests — release gate

Goal: catch migration regressions before production deployment. These are new
executable tests, not just another manual run of existing checks. They use isolated
PostgreSQL and deterministic fixtures; never mutate the live Supabase project.

- [X] T028 Add isolated PostgreSQL fixtures and explicit test database configuration in backend/tests/conftest.py and backend/pyproject.toml; apply migrations to a disposable database, provide owner/importer/read-only connections, refuse production targets, and ensure cleanup and deterministic state. The required regression run must fail rather than silently skip if PostgreSQL is unavailable.
- [X] T029 [P] Add backend/tests/test_import_regression.py covering complete raw-source accounting, verified repairs and unresolved issues, nullable names/units, shared degree/specialization memberships, duplicate-pair preservation, identical-import no-op, changed-snapshot refusal, concurrent importer serialization and transaction rollback on an injected mid-import failure; compare persisted results and checksums, not just function calls.
- [X] T030 [P] Add backend/tests/test_repository_regression.py comparing JSON and PostgreSQL adapters against independently specified fixtures for all three API responses, including all thirty real-source pairs; verify ordering/ties, zero-count partners, repeated rows, case-insensitive distinct counts, empty results, optional fields and displayed NUS units. Account for real-data repairs through explicit reviewed deltas rather than regenerating expected output from the implementation.
- [ ] T031 [P] Add backend/tests/test_database_failures.py covering missing/invalid configuration, unpublished catalog, unknown selections, missing parameters, pool exhaustion/timeouts, connection loss and recovery, sanitized 503s, lifecycle cleanup, and explicit manual JSON rollback; prove database failures never invoke JSON fallback and the runtime role cannot write or read protected archives.
- [ ] T032 Extend frontend/playwright.config.ts and add frontend/tests/database-regression.spec.ts to run against an isolated, seeded PostgreSQL-backed API; exercise direct entry, degree selection, recommendation navigation, mapping selectors/URL state, browser back/forward, empty/error/loading states, rapid selection changes and mobile layout. Retain the JSON-mode suite and ensure fixture/environment settings cannot target production.
- [ ] T033 Add scripts/check-migration-regressions.sh to run the required database import/repository/failure suites, existing backend contract/catalog tests and browser suites in both modes with explicit environment settings; ensure any required failure or missing dependency returns nonzero and document reproducible setup/commands in plan/supabase-migration/quickstart.md.
- [ ] T034 Run the regression command and record database/package versions, fixture/source/repair checksums, exact commands, pass/fail/skip totals and failure fixes in plan/supabase-migration/regression-results.md; rerun affected suites after fixes and block production deployment until every required scenario passes with no unexplained result changes.

Acceptance: all required suites pass against real isolated PostgreSQL and JSON;
rollback and error behavior are proven; every repaired-data difference is documented.
Existing smoke checks after deployment remain necessary.

## Phase 6: US3 — Deployment and manual rollback (P2)

Goal: deliberately switch production to verified Supabase data and retain a documented
manual route back to the frozen JSON release.

Independent acceptance: backend deployment reads Supabase with its runtime role,
frontend works unchanged, outage returns 503 without secret leakage or JSON fallback,
and reverting the mode restores the documented JSON snapshot. Record actual deployment
evidence; local success alone is insufficient.

- [ ] T035 [US3] Write plan/supabase-migration/quickstart.md with local JSON/postgres commands, separate import/migration commands, role provisioning, environment loading, checksum gates and startup diagnostics; document manual-mode rollback and that it restores the original snapshot rather than later database repairs.
- [ ] T036 [US3] Configure the existing backend Vercel project's server-only runtime DATABASE_URL, CATALOG_BACKEND=postgres and bounded pool settings using backend/.env.example as the variable reference; keep frontend NEXT_PUBLIC_API_BASE_URL and CORS behavior intact, exclude importer credentials from runtime, verify region proximity, and record redacted configuration/deployment identifiers in plan/supabase-migration/deployment-results.md.
- [ ] T037 [US3] Deploy the backend after import and API gates pass; smoke-check /api/v1/catalog, /api/v1/recommendations and /api/v1/mappings plus frontend / and /mappings, comparing against the verified import batch; record URLs, timestamps, status/count evidence and remaining issues in plan/supabase-migration/deployment-results.md without credentials.
- [ ] T038 [US3] Rehearse loss/recovery of database access and explicit CATALOG_BACKEND=json rollback in a local/staging environment using plan/supabase-migration/quickstart.md; verify 503 with no automatic fallback, restore postgres mode, confirm the frozen JSON snapshot remains deployable, and record precise rollback/redeployment steps and data-version differences in plan/supabase-migration/deployment-results.md.

## Phase 7: Documentation and final verification

- [ ] T039 Update README.md, supabase/README.md and backend/.env.example to explain the new runtime source, import lifecycle, migration history, supported mode switches, unresolved-data reporting and deployed status; update plan/contracts/openapi.yaml's unavailable-service description to cover database failures without changing response shapes.
- [ ] T040 Run final applicable backend checks and frontend lint/typecheck/build plus relevant existing browser checks via frontend/package.json, inspect git diff --check and tracked files for accidental credentials, and summarize requirements-to-evidence coverage and any genuine blockers in plan/supabase-migration/validation-results.md; mark tasks complete only where implementation or deployment evidence exists.

## Dependencies

```text
T001 → T002 → T003 → T004 → T005 → T006 → T007 → T008 → T009
Foundation → US1: T010 → T011 → T012 → T013 → T014 → T015 → T016 → T018
                                                     T017 ──────────┘
Foundation → US2: T019 → [T020 || T021] → T022 → T023 → T024
US1 publication + T024 → T025 → T026 → T027
US1 + US2 → T028 → [T029 || T030 || T031] → T032 → T033 → T034
Regression gate → US3: T035 → T036 → T037 → T038 → T039 → T040
```

T017 can run alongside importer implementation once the schema and transformation
rules are finalized in T012. T020 and T021 touch different files after T019. US1 data
work and US2 repository work can overlap after foundation, but integration checks
wait for the completed import. Keep edits to shared evidence files sequential.

## Parallel execution examples

- US1: one workstream implements importer transformations (T013–T016); another
  implements the independent reconciliation utility (T017) against the agreed schema.
- US2: after the repository interface, implement the JSON adapter (T020) and initial
  PostgreSQL adapter (T021) separately, then integrate them sequentially.
- Regression: after T028, T029–T031 use different test files and isolated database state; run independently, then complete browser/runner/evidence tasks sequentially.
- US3: no parallel task markers; configuration, deployment verification and rollback
  rehearsal depend on each other's evidence and must proceed in order.

These are scheduling examples, not instructions to spawn agents.

## Implementation strategy

Deliver US1 first while leaving JSON runtime intact. Add US2 behind explicit mode
selection, then perform US3 only after data reconciliation, API comparison and the Phase 5 regression gate pass.
Research existing-record defects without expanding this task into a new curriculum
scrape. Missing official evidence becomes a reported unresolved issue, not fabricated
data. Preserve original raw files for traceability and manual rollback. Do not remove
JSON support, introduce pagination, or add specialization filtering in this feature.

## Checklist audit

40 tasks: setup 3, foundation 6, US1 9, US2 9, regression 7, US3 4, final 2.
Six parallel-marked tasks: T017, T020, T021, T029, T030, T031. IDs T001–T040 are sequential.
Every task has a checkbox, ID and concrete file path; story tasks have a US label.
Pre/post extension hooks: registry absent, so none available to execute.
