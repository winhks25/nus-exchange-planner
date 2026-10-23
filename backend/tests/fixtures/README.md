# Pre-removal catalog fixtures

Date: 2026-10-23 (Asia/Singapore). Scope: T010 frozen fixtures for local
migration and seeding tests. Both files were generated from one disposable
PostgreSQL database populated by the reviewed importer before any metadata table
was removed.

## Files

| File | Purpose | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| `core_dataset.json` | All retained facts from the eight core tables in the snapshot format used by `backend/scripts/snapshot_core_data.py` | 167890 | `78a78b0f4ac6e0c5966601cbb9b81cd322eec8a4c447c8695f578fddee70659f` |
| `pre_catalog_removal.sql` | Data-only upgrade fixture for all thirteen tables at migration ceiling `20261022000300`, including provenance links and sequence state | 438764 | `bbb54a616065e388415bb3e3a063e2dbdf707e746f831d9922c0eefde22ff919` |

Neither file contains a production dump, connection string, password, or private
export. The database was a temporary local cluster created by
`scripts.postgres_validation.PostgresCluster`.

## Core fixture contents

| Table | Rows |
| --- | ---: |
| `degrees` | 6 |
| `nus_modules` | 152 |
| `degree_modules` | 226 |
| `partner_universities` | 5 |
| `pu_modules` | 142 |
| `specializations` | 19 |
| `specialization_modules` | 30 |
| `module_mappings` | 152 |

The core fixture excludes `module_mappings.source_row_id`, because that column is
removed by the migration. It records the retained columns, exact rows, per-table
fingerprints and counts, mapping multiplicity, core sequence values, capture
metadata, and a `fixture` provenance block.

The upgrade fixture contains all thirteen tables: the eight core tables plus
`catalog_import_batches`, `catalog_source_snapshots`, `catalog_source_rows`,
`catalog_issues`, and `catalog_repairs`. It has:

| Object | Rows / value |
| --- | ---: |
| `catalog_import_batches` | 1 completed current batch |
| `catalog_source_snapshots` | 8 |
| `catalog_source_rows` | 155 |
| `catalog_issues` | 34 |
| `catalog_repairs` | 44 |
| `module_mappings` | 152, all with non-null `source_row_id` |
| `catalog_import_batches.raw_row_count` | 155 |
| `catalog_import_batches.accepted_row_count` | 147 |
| `module_mappings_id_seq` last value | 152 |

## Intentional duplicate

The importer publication has 151 mapping rows. The fixture adds one more mapping
row and source row so the upgrade path exercises an exact repeated course pair:

| Field | Value |
| --- | --- |
| Original mapping ID | 10 |
| New mapping ID | 152 |
| New source row ID | 155 |
| NUS module | `CS3213` |
| Partner module | University of Western Australia / `CITS3301` |
| Source mapping index | 32 |
| Multiplicity | 2 rows for the same natural course pair |

`CS3213` is not part of any `degree_modules` membership, so the duplicate cannot
appear in catalog options, recommendations, or mappings responses. The core
fixture therefore retains production API behavior while providing a real
repeated pair for migration-preservation and constraint tests.

## Generation

The generator is a one-time, local-only tool:

```bash
uv run --directory backend python -m scripts.generate_catalog_fixtures --force
```

It performs these checks and aborts instead of writing fixtures on failure:

1. Creates two disposable local databases and applies the checked-in migrations.
2. Populates one database with `scripts.import_catalog.apply_plan` and the other
   with the independent `scripts.catalog_preview` seed.
3. Compares the eight core tables in natural-key mode; generated IDs and
   sequence state are ignored for this independent-seed check.
4. Compares every API-visible degree/university mapping count with
   `plan/remove-catalog-tables/baseline-responses.json`.
5. Confirms the repaired `CS3264` mapping keeps the reviewed title and partner
   units of `0.50`.
6. Adds the intentional duplicate mapping and source row, updates the batch
   counters, and verifies that API-visible counts are unchanged.
7. Writes the core snapshot and dumps `public` data with `pg_dump`
   (`--data-only --column-inserts --no-owner --no-privileges`).

The command requires the checked-in pre-removal importer and `pg_dump` on
`PATH`. It never accepts a remote database URL. Regeneration produces a new
snapshot timestamp and therefore new file digests; update this README when
regenerating. The generator must be retired together with the importer once these
frozen fixtures and the final-schema seeder are in use.

## Loading the upgrade fixture

Load the SQL only into a disposable local database that has migrations applied
through `20261022000300` and has the roles required by the migration chain. The
T011 harness adds the `create_database(through=...)` and
`apply_next_migration(...)` helpers used by the tests:

```bash
psql -X -v ON_ERROR_STOP=1 -d "<local-disposable-database>" \
  -f backend/tests/fixtures/pre_catalog_removal.sql
```

The fixture uses `OVERRIDING SYSTEM VALUE` for identity columns and restores
sequence values with `setval`, so it is intended for an empty schema at the
ceiling, not for an already-populated database. Archive triggers are
BEFORE UPDATE/DELETE or TRUNCATE triggers, so the data load itself is allowed.

## Cross-check evidence

- Natural-key comparison of the importer publication against the independent
  preview seed passed for all eight core tables.
- Every nonzero degree/university mapping count matched the captured PostgreSQL
  baseline (151 production mapping rows).
- The fixture duplicate is the only repeated exact course pair and is outside
  every degree membership.
- The repaired `CS3264` row retains `Foundations of Machine Learning` and
  `source_partner_units = 0.50`.
- The generated SQL loaded successfully into a disposable database at the
  migration ceiling with all thirteen tables, 152 non-null `source_row_id`
  links, the repeated `CS3213`/`CITS3301` pair, and sequence value 152.
- After loading that SQL, the eight core tables matched `core_dataset.json` in
  both ID and natural-key comparison modes, including sequence state.
