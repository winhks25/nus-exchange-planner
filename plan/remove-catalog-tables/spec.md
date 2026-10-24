# Remove catalog metadata tables

Date: 2026-10-23 (Asia/Singapore). Status: specified; implementation has not started.

## Requested outcome and confirmed decisions

The application must operate without any `catalog_*` database tables. Remove its dependencies, delete the five metadata tables from the currently linked production Supabase project, verify behavior, clean up/refactor the code, and finish with a dedicated regression gate. This request produces planning documents only; it does not execute those changes.

The user confirmed:

- Retire the production JSON-to-database importer. Future data maintenance happens directly in Supabase.
- Keep the existing JSON backend as an explicit manual fallback. PostgreSQL failures must never trigger it automatically.
- Target the currently linked production project, after local rehearsal. An additional hosted staging project is not required.

“catalog_*” refers to database tables. The `/api/v1/catalog` route, `CATALOG_BACKEND`, `catalog_reader` role, Python classes/modules, source repair JSON, and ordinary use of the word catalog do not need renaming. Preserve the public API and current UI.

## User stories

### US1 — Serve the application from core tables (P1; first deployable increment)

As a student, I can use selectors, recommendations, and mappings with identical behavior when all `catalog_*` tables are absent or inaccessible to the runtime role.

Acceptance:

- `/api/v1/catalog`, `/api/v1/recommendations`, and `/api/v1/mappings` query only the six existing tables used by those operations: `degrees`, `partner_universities`, `degree_modules`, `nus_modules`, `pu_modules`, and `module_mappings`.
- Preserve `specializations` and `specialization_modules`, although the current endpoints do not query them.
- Replace the publication marker with a core-data readiness check shared by all three operations: at least one degree, at least one university, and a non-null full title for every degree. Blank titles remain prohibited by the existing constraint. An unready database returns the existing sanitized 503. Once ready, unknown selections return 404, missing required query parameters return 422, and known selections with no mappings return 200 with zero counts.
- Readiness does not demand any mapping rows, a nonempty membership for every degree, specialization rows, or hardcoded production counts. It establishes minimum usability, not proof that an operator finished all intended edits.
- Preserve source ordering, tie-breaking, mapping multiplicity, case-insensitive partner counts, title/unit fallback behavior, omitted optional mapping fields, verified repairs, and displayed NUS units of 4.
- Preserve bounded pool lifecycle, read-only transactions, timeouts, secret-safe errors, and explicit JSON fallback.
- A compatible backend deployment works with both the old schema and the schema after removal.

### US2 — Remove production metadata tables without changing core data (P1)

As the operator, I can remove the metadata tables with a tested migration, retain a restorable export, and show that the eight core tables retain their records and meaning.

Acceptance:

- Verify the linked project against the deployment and actual database before any mutation. The historical project reference is `wydziozsjibkvpgphpia`; it is a cross-check, not a substitute for current discovery.
- Export schema and data consistently to private storage; include all five removed tables and the pre-removal `module_mappings.source_row_id` values. Restore the export locally and prove it is usable before deletion.
- Deploy and verify US1 before applying destructive DDL. Rehearse both a populated upgrade and a clean migration chain locally.
- Remove `module_mappings.source_row_id` with its foreign key and unique constraint; preserve every other core field, identity, relationship, record, and required index.
- Explicitly drop `catalog_issues`, `catalog_repairs`, `catalog_source_rows`, `catalog_source_snapshots`, and `catalog_import_batches` in dependency order. Remove the now-unused archive trigger function after dependency inspection. Do not use broad `CASCADE`, wildcard deletion, or delete/truncate core tables.
- No `catalog_*` table remains in the application's `public` schema. Inventory other application-owned schemas and stop for review if unexpected matching tables or external dependencies exist; never delete Supabase-managed objects by prefix.
- Keep historical migrations unchanged. A new migration brings both existing and fresh databases to the desired final schema.
- Keep RLS, intended runtime SELECT policies, and write restrictions on the core tables. Remove obsolete grants/policies via the explicit drop and verify the resulting permissions.

### US3 — Verify production behavior immediately after deletion (P1)

As the operator, I can demonstrate that production responses, core data, and student journeys still match the recorded pre-change behavior.

Acceptance:

- Compare catalog options, every degree's recommendations, and every degree/university mapping response against a captured PostgreSQL baseline. Discover combinations from that baseline; historically there were six degrees and five universities, but actual captured data is authoritative.
- Compare exact ordering, values, optional field presence, counts, and repeated rows. The older JSON baseline is not the expected PostgreSQL result where reviewed repairs differ.
- Verify production SELECT access as the actual runtime role and exercise browser navigation, selectors, deep links, and a valid empty pair. Compare core-table fingerprints and constraints against the captured baseline.
- Rehearse connection failures, timeouts, JSON fallback, and recovery locally. Never deliberately disrupt the production database as a test.
- Record failures honestly and fix migration/runtime defects before beginning broad cleanup. Passing sampled browser checks is not a guarantee of perfection.

### US4 — Retire the importer and simplify maintenance (P2)

As a maintainer, I can run development, verification, and tests without a production importer or any query against the removed tables.

Acceptance:

- Delete the production importer command and its obsolete persistence code; remove imports, docs, scripts, and test assertions that require its batch/archive/issue/repair tables.
- Keep offline source parsing, reviewed repair inputs, and the JSON fallback. A disposable local test seeder may populate the eight core tables; it is not a supported production import or refresh command.
- The test seeder must reject external targets and use explicit writer access. Runtime and browser bundles never receive writer credentials.
- Keep a historical migration test fixture and historical planning evidence where needed. Explicit references to dropped names are allowed in history, migration/absence assertions, and recovery instructions, not in operational queries.
- Document direct Supabase maintenance with complete degree titles, foreign-key order, existing validation constraints, intentional duplicate mappings, explicit source order, null/units policy, and transactions for logically related edits. Explain that minimum readiness cannot detect every incomplete manual edit.
- Keep evidence in checked-in original source/repair files and the private pre-deletion export. Do not replace the deleted tables with renamed audit tables or a new runtime dependency.

### US5 — Complete a final regression gate (P2)

As a maintainer, I can run one reproducible regression gate after cleanup that proves the supported modes and migration paths still work.

Acceptance:

- The final schema contains the eight core tables and no `public.catalog_*` table. Prove this for both an upgraded populated database and a fresh migration replay.
- Run all backend tests and browser tests in both supported modes, plus frontend lint/typecheck/build and the applicable backend lint check. Required database tests fail if prerequisites are unavailable; they must not silently skip.
- Test baseline parity, readiness, empty/unknown selections, duplicate preservation, nullable fields, units, privileges, timeouts, recovery, pool cleanup, migration atomicity, and JSON fallback without database access.
- Preserve known JSON/PostgreSQL repair differences explicitly. Do not regenerate expected responses from the changed code merely to make tests pass.
- After cleanup is deployed, repeat production smoke and full read-only API comparison; tie evidence to the tested commit and deployed version. Record genuine limitations and blockers.

## Scope boundaries

No new curricula, data refresh, new admin UI, frontend redesign, automatic JSON fallback, role renaming, source-data corrections, or additional business tables. The source columns on core tables stay unless specifically identified above. Export retention, recovery, migration history, and test-only legacy fixtures are operational necessities, not active archive-table dependencies.

## Completion evidence

Implementation is complete only after all five stories and the final gate pass. Planning does not claim a database change, deployment, successful test run, or perfect behavior. Every implementation task in `tasks.md` begins unchecked.
