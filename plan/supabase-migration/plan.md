# Implementation plan: Supabase catalog migration

## Approach

Keep Next.js and FastAPI. Use synchronous Psycopg 3 with a bounded psycopg_pool
pool, matching current synchronous API handlers. Pin compatible versions through
backend/pyproject.toml, backend/uv.lock and root requirements.txt at implementation.
Use parameterized SQL and short read-only transactions; do not materialize the whole
database into the existing in-memory Catalog per instance or request. Create and
close the pool with FastAPI lifespan, not import-time network operations.

Use Supabase's transaction pooler for runtime traffic; verify current official
Psycopg/Supabase guidance, disable incompatible prepared statements, configure TLS,
and bound pool wait, connection and statement timeouts. Use a migration-compatible
connection for DDL/imports. Keep credentials outside Git and browser bundles.

## Repository structure

- backend/app/settings.py: explicit mode and connection configuration.
- backend/app/database.py: pool/lifecycle and safe database error translation.
- backend/app/repositories/base.py: catalog/recommendations/mappings interface.
- backend/app/repositories/json_catalog.py: current behavior adapter.
- backend/app/repositories/postgres_catalog.py: SQL-backed adapter.
- backend/app/main.py: injected repository and lifespan selection.
- backend/scripts/audit_catalog.py: source inventory and import preparation.
- backend/scripts/import_catalog.py: transactional, repeatable publication.
- backend/scripts/verify_catalog.py: source/DB reconciliation and API comparison.
- data/repairs/catalog_repairs.json: source-addressed corrections and citations.
- supabase/migrations/20261022000200_prepare_catalog_import.sql: additive schema changes.
- supabase/migrations/20261022000300_catalog_reader.sql: least-privilege read access.
- plan/supabase-migration/: research, evidence, rollout instructions and task list.

## Schema evolution

Do not rerun or rewrite the already-applied initial migration. Compare remote DDL
with it, then reconcile CLI migration history before subsequent db push operations.
Keep original tables and relations; add degree full title and deterministic source
order, nullable module names (unknown must not become invented names), nullable
verified units, and a specialization kind distinguishing specialization/focus_area.
Archive exact source text plus parsed JSON, path, checksum, and source snapshot ID.
Track import batches, source-row identity and issues/correction provenance. Preserve
mapping-specific source presentation where a normalized course entity cannot
represent different titles/units across source rows.

Source mapping identity is snapshot/file path/array index; equal course pairs at
different indexes remain distinct records. Reimporting the same snapshot+repair
checksum is a no-op. A new dataset refresh is a separate future operation; the
initial importer must refuse to overwrite an already-published different snapshot
unless a separately reviewed refresh implementation exists. Use one transaction
and an advisory transaction lock for initial publication, with a completed-import
marker committed alongside catalog data. No partial import is visible.

Degree membership must preserve extract_course_codes semantics across all list
strings, including specialization lists. Store specialization-specific links too,
without multiplying mappings in joins. Archive choice-group expressions and avoid
inventing academic eligibility rules. University/course titles, ordering, repeated
rows and units must be reconstructible for API parity.

RLS stays enabled on new and existing tables. No anonymous/authenticated browser
policies. Give a dedicated runtime role SELECT only on needed catalog relations,
with explicit SELECT policies if it does not bypass RLS; deny raw archives/issues
and mutation access. Provision its password separately without putting secrets in
migrations. Import role remains separate. Verify access as the actual runtime role.

## Delivery and risks

US1 imports and verifies data while the app stays on JSON. US2 adds PostgreSQL mode
and compares every degree/university combination. US3 enables it after verification,
then demonstrates manual rollback. A dedicated automated regression phase between
US2 and US3 gates deployment on import integrity, API parity, failure recovery,
role restrictions and browser flows in isolated environments. Rollback initially uses the frozen original JSON
snapshot and therefore may reverse documented repairs; record that limitation.

Official-source research is scoped to existing records and names, not expansion of
the course catalog. Keep unresolved names null and invalid-code rows quarantined;
do not guess. Present unresolved issues and repair-induced result changes explicitly.

Production runtime credentials and deployment access are implementation prerequisites,
not reasons to store secrets in planning files. Record a concrete access blocker if
they are unavailable; do not claim a deployed connection from local verification.
