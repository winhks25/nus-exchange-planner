# Baseline and starting state

Date: 2026-10-25 (Asia/Singapore). Scope: Phase 1 setup (T001) for the exchange
planner enhancements. All inspection was read-only; no credentials were printed.

## Starting repository state

| Item | Value |
| --- | --- |
| Branch | `master` |
| Starting commit | `0a2adb524a6592d7cb44b9b07b2b22650dbebbb6` (`Write featureSpecs for recommend and mappings page`) |
| Tracked working tree | Clean; nothing staged or unstaged |
| Feature planning files | `plan/exchange-enhancements/` (tracked at the starting commit) |
| Supabase project | `wydziozsjibkvpgphpia` (region `ap-southeast-2`) |

## Inputs read

- `plan/exchange-enhancements/spec.md`, `plan.md`, `source-requirements.md`, `tasks.md`
- `README.md`, `supabase/README.md`, `frontend/AGENTS.md`
- `backend/app/models.py`, `backend/app/catalog.py`, `backend/app/repositories/postgres_catalog.py`,
  `backend/app/repositories/json_catalog.py`, `frontend/lib/types.ts`, `frontend/lib/api.ts`
- All four committed migrations in `supabase/migrations/`
- Historical evidence: `plan/remove-catalog-tables/baseline.md` and
  `baseline-responses.json`, `plan/supabase-cleanup/results.md`

## Toolchain

| Tool | Version |
| --- | --- |
| macOS host | Darwin (arm64) |
| git | 2.56.0 |
| uv | 0.13.0 |
| Node.js / npm | 22.23.3 / 10.9.9 |
| Host `python3` | 3.14.2 (backend uses uv-managed 3.12) |
| Supabase CLI | 2.122.0 through `npx --yes supabase@latest` |
| PostgreSQL binaries | available (Homebrew), used by backend test suites |

## Production endpoint state at capture

The deployed API `https://nus-exchange-planner-api.vercel.app` returned **503**
with the sanitized body `{"detail": "Catalog data is unavailable. Please try
again later."}` for both `/api/v1/catalog` and
`/api/v1/recommendations?degree=Computer%20Science`, checked three times
between `2026-10-25T11:40Z` and `2026-10-25T11:46Z`. At the same time the Supabase MCP
read channel served the project database normally. A direct pooler connection
from this machine (`<pooler-host>:5432`, role-qualified `postgres` user) timed
out after 10 seconds, and the Supabase CLI `migration list --project-ref` call
failed with the same pooler connection timeout. The most consistent explanation
is that the database instance or the client network path to the pooler is
degraded; the application code itself is unchanged. This must be re-checked at
deployment time. Consequences:

- The 2026-10-23 production capture in
  `plan/remove-catalog-tables/baseline-responses.json` is the last known good
  API-level baseline; it is superseded below only where the October 25 data
  cleanup changed counts (it did not change degree/university sets).
- The canonical pre-change payload, ranking orders, and counts below were
  derived directly from the deployed database using the repository's own
  query shapes, so T013 can compare against exact numbers.

## Current catalog payload (deployed database)

`degrees.source_order` and `partner_universities.source_order` do not exist in
the deployed schema, so the repository's `to_jsonb(...)->>'source_order'`
ordering degrades to stable `id` order. The catalog response therefore lists:

| # | `degrees[]` name | `degrees[]` degree (full_title) |
| ---: | --- | --- |
| 1 | Artificial Intelligence | Bachelor of Computing (Artificial Intelligence) |
| 2 | Business Analytics | Bachelor of Science (Business Analytics) |
| 3 | Business Artificial Intelligence Systems | Bachelor of Computing (Business Artificial Intelligence Systems) |
| 4 | Computer Science | Bachelor of Computing (Computer Science) |
| 5 | Information Systems | Bachelor of Computing (Information Systems) |
| 6 | Information Security | Bachelor of Computing (Information Security) |

| # | `universities[]` name | country | city | continent |
| ---: | --- | --- | --- | --- |
| 1 | University of Western Australia | Australia | Perth | Oceania |
| 2 | University of Toronto | Canada | Toronto | North America |
| 3 | Kyoto University | Japan | Kyoto | Asia |
| 4 | Korea University | South Korea | Seoul | Asia |
| 5 | Yonsei University | South Korea | Seoul | Asia |

## Recommendation order and counts (deployed database)

Exact `RANKINGS_SQL` output per degree: rank order is descending
`distinct_nus_module_count`, then university name in the "C" collation.

| Degree | 1st | 2nd | 3rd | 4th | 5th |
| --- | --- | --- | --- | --- | --- |
| Artificial Intelligence | Toronto 10/6/10 | Yonsei 4/3/4 | Korea 2/2/2 | Kyoto 1/1/1 | W. Australia 0/0/0 |
| Business Analytics | Korea 18/11/17 | W. Australia 22/11/19 | Toronto 19/9/19 | Yonsei 10/5/10 | Kyoto 2/2/2 |
| Business AI Systems | Korea 11/8/11 | W. Australia 8/6/8 | Yonsei 6/4/6 | Toronto 4/3/4 | Kyoto 1/1/1 |
| Computer Science | Toronto 7/3/7 | Korea 2/2/2 | Kyoto 1/1/1 | W. Australia 0/0/0 | Yonsei 0/0/0 |
| Information Systems | Korea 12/9/12 | W. Australia 12/9/9 | Toronto 9/5/9 | Yonsei 7/5/7 | Kyoto 3/3/3 |
| Information Security | W. Australia 6/6/6 | Toronto 8/5/8 | Korea 5/4/5 | Yonsei 3/2/3 | Kyoto 1/1/1 |

Cells are `mapping_count / distinct_nus_module_count / partner_module_count`.
For Business Analytics the equal distinct-NUS tie (Korea 11, W. Australia 11)
resolves by name, so Korea ranks above W. Australia. These exact orders and
counts are the T013 preservation reference.

## Mappings deep links and pair counts

Frontend deep link format: `/mappings?degree=<degree name>&uni=<university
name>` with URL-encoded names; the page hydrates both selectors and fetches
`GET /api/v1/mappings?degree=...&uni=...` automatically when both are valid.
Absent or unknown parameters clear the selection (unknown names render a
warning note). Example:
`/mappings?degree=Computer%20Science&uni=University%20of%20Toronto`.

Per-pair `mapping_rows / distinct NUS / partner modules` for all 30 pairs
(degree order above, universities in name "C" order):

| Degree | W. Australia | Toronto | Kyoto | Korea | Yonsei |
| --- | --- | --- | --- | --- | --- |
| Artificial Intelligence | 0/0/0 | 10/6/10 | 1/1/1 | 2/2/2 | 4/3/4 |
| Business Analytics | 22/11/19 | 19/9/19 | 2/2/2 | 18/11/17 | 10/5/10 |
| Business AI Systems | 8/6/8 | 4/3/4 | 1/1/1 | 11/8/11 | 6/4/6 |
| Computer Science | 0/0/0 | 7/3/7 | 1/1/1 | 2/2/2 | 0/0/0 |
| Information Systems | 12/9/9 | 9/5/9 | 3/3/3 | 12/9/12 | 7/5/7 |
| Information Security | 6/6/6 | 8/5/8 | 1/1/1 | 5/4/5 | 3/2/3 |

Known empty pairs (valid selections with zero mappings): Computer Science with
University of Western Australia and Yonsei University; Artificial Intelligence
with University of Western Australia.

## Deployed schema inventory

Eight core tables, all with row level security enabled and no browser-facing
policies. Row counts at capture: degrees 6, nus_modules 152, degree_modules
226, specializations 19, specialization_modules 30, partner_universities 5,
pu_modules 142, module_mappings 151.

| Table | Columns (constraints) |
| --- | --- |
| `degrees` | `id bigint identity PK`, `name text unique not null (btrim<>'')`, `faculty text not null (btrim<>'')`, `full_title text null (btrim<>'')` |
| `nus_modules` | `code text PK (upper, btrim<>'')`, `name text null (btrim<>'')`, `faculty text null`, `units numeric null (>0)` |
| `degree_modules` | `degree_id bigint FK→degrees`, `module_code text FK→nus_modules`, `requirement_type text null`, `module_type text null`; PK (degree_id, module_code) |
| `specializations` | `id bigint identity PK`, `degree_id bigint FK→degrees`, `name text not null`; unique (degree_id, name) |
| `specialization_modules` | `specialization_id bigint FK`, `module_code text FK`; PK pair |
| `partner_universities` | `id bigint identity PK`, `name text unique not null`, `country text not null`, `city text null`, `continent text null` |
| `pu_modules` | `id bigint identity PK`, `code text not null (upper)`, `name text null`, `partner_university_id bigint FK`, `pu_units numeric null (>0)`; unique (partner_university_id, code) |
| `module_mappings` | `id bigint identity PK`, `nus_module_code text FK→nus_modules`, `pu_module_id bigint FK→pu_modules` |

Indexes beyond primary/unique keys: `degree_modules_module_code_idx`,
`specialization_modules_module_code_idx`, `module_mappings_nus_module_code_idx`,
`module_mappings_pu_module_id_idx`. The deployed schema is the cleaned
post-October-25 shape: `nus_modules.faculty` (renamed from `offering_faculty`),
`nus_modules.units` and `pu_modules.pu_units` (renamed from `verified_units`),
no `source_order` columns, and no mapping provenance columns.

### Runtime reader access

`catalog_reader` (NOLOGIN, NOSUPERUSER, NOBYPASSRLS, read-only transactions,
5s statement/idle timeouts) has `SELECT` only, with matching `FOR SELECT`
policies, on exactly the eight core tables; insert/update/delete are all
denied (verified via `has_table_privilege`). No other policies exist.

### Deployed faculty label data

- `degrees.faculty`: all 6 rows are `School of Computing`.
- `nus_modules.faculty`: all 152 rows are `School of Computing` (no nulls).
- `partner_universities.city`/`continent`: all 5 rows populated.
- Frozen JSON sources (`data/`) carry only `School of Computing` in mapping
  rows and the majors file; no alternative faculty labels exist anywhere.

### Consumers of `degrees.faculty` and `nus_modules.offering_faculty` (deployed name: `faculty`)

No runtime API query reads either column: `postgres_catalog.py` and
`json_catalog.py` expose no faculty field, so the additive faculty work cannot
change existing API behavior. Current readers are tooling and fixtures only:

- `backend/scripts/catalog_seed.py` — inserts `degrees.faculty` and (old-schema)
  `nus_modules.offering_faculty` into disposable local databases.
- `backend/scripts/catalog_preview.py` — reads source JSON `faculty` with a
  `FACULTY_FALLBACK = "School of Computing"` constant.
- `backend/scripts/cleanup_catalog.py` — performed the `offering_faculty →
  faculty` rename in the October 25 cleanup.
- `backend/scripts/snapshot_core_data.py` — snapshots both old and cleaned
  column sets; `backend/scripts/verify_catalog.py` and
  `backend/scripts/measure_catalog_performance.py` target the archived schema.
- `backend/tests/` fixtures and `backend/tests/fixtures/pre_catalog_removal.sql`
  use the column names for disposable test databases.
- `frontend/` has no faculty consumer.

## Migration history

| Version | Name | In repo | In live history |
| --- | --- | --- | --- |
| `20261022000100` | `create_exchange_catalog` | yes | yes |
| `20261022000200` | `prepare_catalog_import` | yes | yes |
| `20261022000300` | `catalog_reader` | yes | yes |
| `20261024054553` | `remove_catalog_metadata` | no | yes |
| `20261024034234` | `remove_catalog_metadata` | yes | no |

**Drift finding:** the live history records `remove_catalog_metadata` at
`20261024054553`, but the committed file is
`supabase/migrations/20261024034234_remove_catalog_metadata.sql`. The schema
itself matches the removal (no metadata tables, no `source_row_id`), so the
content is applied — only the recorded version differs. Until this is repaired
(`supabase migration repair`, which needs an authenticated CLI session that the
pooler network block currently prevents), `supabase db push` will treat the
repo file as pending and fail on the first `DROP TABLE`. T006 must therefore
generate and apply the new migration through the MCP channel and T013 must
record the drift and its repair plan.

## Constraints carried into later tasks

- No production mutation before the T013 rehearsal passes on a local replica.
- The pooler is unreachable from this machine, so all live database reads used
  the Supabase MCP read channel; DDL/DML will be applied through the same
  channel and re-verified read-only afterwards.
- All new schema fields are nullable and all new tables are additive; existing
  row counts, ranking orders, and mapping outputs above must be unchanged.
- `catalog_reader` must gain SELECT (and only SELECT) on the new tables.
