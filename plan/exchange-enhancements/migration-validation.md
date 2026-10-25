# Migration rehearsal — exchange planner enhancements

Date: 2026-10-25 (T013). This record documents the local rehearsal of the
additive enhancement migration (`supabase/migrations/
20261025121412_exchange_enhancements.sql`) and the faculty backfill
(`backend/scripts/seed_exchange_enhancements.py`), including the rollback
drill. **Result: PASS** — every step below completed and every check held.

## Why a local rehearsal, not the live database

- The pooler host of Supabase project `wydziozsjibkvpgphpia` is unreachable
  from this machine (connection timeout, confirmed 2026-10-25), so neither
  the Supabase CLI nor a direct connection could reach the live database.
  The deployed API returned 503 in the same window (baseline.md).
- The live core rows were therefore captured read-only through the Supabase
  MCP channel on 2026-10-25 and loaded into a disposable local PostgreSQL
  database built with this repository's `PostgresCluster` test
  infrastructure. The replica reproduces the deployed cleaned schema
  (renamed `faculty`/`units` columns, no `source_order`, no metadata tables)
  exactly.
- A Supabase dev branch ("staging") was not used: `supabase create branch`
  is blocked by the same CLI authentication path that the pooler outage
  affects, and it would incur hourly compute charges. The local rehearsal
  is the full rehearsal; the live application path is recorded at the end.

## Rehearsal environment

- One disposable local PostgreSQL server (`scripts.postgres_validation.
  PostgresCluster`), one empty database per run.
- Deployed cleaned schema (`replica.SCHEMA_SQL` equivalent of the eight core
  tables) plus the `catalog_reader` role with its deployed SELECT grants on
  the eight core tables, mirroring `20261022000300_catalog_reader.sql`.
- Live core rows captured 2026-10-25 (degrees 6, nus_modules 152,
  degree_modules 226, specializations 19, specialization_modules 30,
  partner_universities 5, pu_modules 142, module_mappings 151).

## Steps and results

### 1. Snapshot before any change

The captured live rows were loaded into the replica, then the pre-change
state was recorded:

- Row counts for all eight core tables — **match the live baseline**
  (baseline.md / data-audit.md).
- Foreign-key integrity — **0 orphan rows** in `degree_modules`,
  `module_mappings`, and `pu_modules`.
- All six per-degree recommendation rankings — **byte-identical** to the
  live baseline recorded in baseline.md.

### 2. Apply the enhancement migration

`20261025121412_exchange_enhancements.sql` was applied to the replica in its
single transaction:

- New objects present: `faculties`, `degree_faculties`,
  `faculty_partner_universities`, `nus_modules.faculty_id`,
  `partner_universities.image` / `website` / `image_attribution`, and the
  three reverse-lookup indexes.
- Row level security enabled on the three new tables.
- `catalog_reader` holds **SELECT only** on the three new tables, with one
  matching SELECT policy each; a probe role granted INSERT but holding no
  RLS policy (the live position of `anon` under Supabase default privileges)
  was **blocked by RLS** on write.
- Core data untouched: row counts and all six rankings identical to the
  snapshot from step 1; orphan count still 0.

### 3. Backfill: dry-run, then apply

`scripts/seed_exchange_enhancements.py` against the replica with the reviewed
`data/exchange-enhancements/faculty-aliases.json`:

- Dry run: 1 faculty to create (`School of Computing`), 6 degree
  memberships to add, 152 module `faculty_id` updates, 0 unresolved labels,
  0 conflicts — no writes.
- Apply (one transaction): 1 `faculties` row, 6 `degree_faculties` rows, all
  152 `nus_modules.faculty_id` values set.
- Preservation: every legacy `nus_modules.faculty` text value retained
  (152 rows still `School of Computing`), all 151 `module_mappings` rows
  intact, `faculty_partner_universities` left empty (availability is seeded
  later by T027, never derived), core row counts and rankings unchanged.
- Unique pairs: no duplicate `(degree_id, faculty_id)` or
  `(faculty_id, partner_university_id)` pair exists after the upserts.

### 4. Repeatable re-run

A second dry run after the apply produced a pure no-op plan: 0 faculties to
create, 0 memberships to add (6 already present), 0 module updates (152
already set), 0 unresolved, 0 conflicts. Re-running the apply is therefore
safe at any time with the same alias file.

A conflict probe (a module whose `faculty_id` was hand-set to a different
faculty) makes the dry run report the conflict and the apply **abort with a
nonzero exit and zero writes** until the conflict is reviewed. An unknown
label probe (faculty_id null, label not in the alias file) leaves the row
null and reports the label, per decisions.md decision 7.

### 5. Rollback drill (no existing data deleted)

The rollback removes only objects the migration added, in dependency order,
inside one transaction:

```sql
-- 1. New RLS policies first.
drop policy if exists catalog_reader_select_faculties on public.faculties;
drop policy if exists catalog_reader_select_degree_faculties on public.degree_faculties;
drop policy if exists catalog_reader_select_faculty_partner_universities
  on public.faculty_partner_universities;

-- 2. Reader grants on the new tables.
revoke select on table
  public.faculties,
  public.degree_faculties,
  public.faculty_partner_universities
from catalog_reader;

-- 3. New link tables before the faculties parent (RESTRICT drops).
drop table public.degree_faculties;
drop table public.faculty_partner_universities;

-- 4. New columns; their indexes and the nus_modules foreign key drop with them.
alter table public.nus_modules drop column faculty_id;
alter table public.partner_universities drop column image;
alter table public.partner_universities drop column website;
alter table public.partner_universities drop column image_attribution;

-- 5. The now-isolated faculties table.
drop table public.faculties;
```

After the rollback on the rehearsal replica:

- All eight core tables **byte-identical** to the step-1 snapshot (row
  counts and all six rankings).
- No leftover enhancement tables, columns, or reader grants.
- The reader's original eight core-table SELECT grants intact.

The rollback deletes **no existing data**: the only rows removed are the
backfill rows the migration itself created. Core rows, mappings, and legacy
text columns are never touched by either direction.

## Re-running the rehearsal

```sh
# Local snapshot capture (needs a reachable database; otherwise capture
# read-only through the Supabase MCP channel as done on 2026-10-25):
uv run --directory backend python -m scripts.snapshot_core_data \
  --database-url '<url>' --output snapshot.csv

# Rehearsal steps (each on a fresh local cluster database):
#   1. Load the snapshot into the deployed cleaned schema.
#   2. psql -f supabase/migrations/20261025121412_exchange_enhancements.sql
#   3. uv run --directory backend python -m scripts.seed_exchange_enhancements \
#        --database-url '<url>' --dry-run
#      uv run --directory backend python -m scripts.seed_exchange_enhancements \
#        --database-url '<url>'
#   4. Re-run step 3's dry run and confirm a no-op plan.
#   5. Run the rollback SQL above and compare against the step-1 snapshot.
#   6. Re-verify with the audit:
#      uv run --directory backend python -m scripts.audit_exchange_enhancements \
#        --database-url '<url>' --output /dev/null
```

## Remaining live-execution steps (blocked on pooler reachability)

1. Apply `20261025121412_exchange_enhancements.sql` to the live project
   through the Supabase MCP channel (`apply_migration`), inside its
   transaction.
2. Run the backfill: if the pooler is reachable, use
   `scripts/seed_exchange_enhancements.py` (dry run first, then apply);
   otherwise execute the equivalent statements through the MCP channel.
3. Re-run `scripts/audit_exchange_enhancements.py` against the live
   database and confirm the report matches data-audit.md plus the new
   enhancement rows (1 faculty, 6 degree memberships, 152 linked modules).
4. Re-verify the deployed API's catalog, recommendation order, and mapping
   outputs against baseline.md; confirm `catalog_reader` serves the new
   fields.
5. Repair the pre-existing `remove_catalog_metadata` migration-version
   drift with `supabase migration repair` once the CLI can authenticate
   (recorded in decisions.md, decision 6).
