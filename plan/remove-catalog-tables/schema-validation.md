# Schema validation — catalog-metadata removal

Migration: `supabase/migrations/20261024034234_remove_catalog_metadata.sql`.
Evidence captured locally on a disposable PostgreSQL cluster built to the legacy
ceiling (`20261022000300`) and advanced by exactly the removal migration via
`PostgresCluster.apply_next_migration`. Owner-role read-only inspection,
`LC_ALL=C LANG=C`.

## T028 — explicit core unlink (module_mappings)

The migration drops `module_mappings_source_row_id_fkey`, then
`module_mappings_source_row_id_key`, then the `source_row_id` column. Every other
mapping column, constraint, index, and row is preserved. No data is cleared and
no unique constraint is added on `(nus_module_code, pu_module_id)`.

### Columns

| State | Columns (ordinal order) |
| --- | --- |
| Pre | id, nus_module_code, pu_module_id, **source_row_id**, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page |
| Post | id, nus_module_code, pu_module_id, source_order, source_nus_title, source_nus_units, source_partner_title, source_partner_units, source_faculty, source_page |

Columns removed: `source_row_id` (and only that column).

### Constraints

Retained **10 of 12**. Removed exactly:

- `module_mappings_source_row_id_fkey` (foreign key → `public.catalog_source_rows`)
- `module_mappings_source_row_id_key` (unique on `source_row_id`)

All retained constraints are intact, including the primary key, the
`(nus_module_code, pu_module_id)` relationships, and the `source_*` check
constraints. No new constraint was added.

### Indexes

| State | Indexes |
| --- | --- |
| Pre | module_mappings_pkey, module_mappings_nus_module_code_idx, module_mappings_pu_module_id_idx, module_mappings_nus_code_source_order_idx, **module_mappings_source_row_id_key** |
| Post | module_mappings_pkey, module_mappings_nus_module_code_idx, module_mappings_pu_module_id_idx, module_mappings_nus_code_source_order_idx |

Indexes removed: only `module_mappings_source_row_id_key` — the implicit index
backing the dropped unique constraint. The `source_order` index
(`module_mappings_nus_code_source_order_idx`) and every other index are retained.

### Data preservation (populated-upgrade path)

Verified against `backend/tests/fixtures/pre_catalog_removal.sql`, which populates
real provenance links (152 mappings, all 152 with non-null `source_row_id` before
the migration). After the migration:

- All eight core table counts unchanged:
  degrees 6, nus_modules 152, degree_modules 226, specializations 19,
  specialization_modules 30, partner_universities 5, pu_modules 142,
  module_mappings 152.
- `module_mappings_id_seq.last_value` unchanged (152).
- A full ordered row-by-row snapshot of all eight core tables (IDs included,
  `source_row_id` excluded from the comparison) is byte-for-byte identical
  before and after.

Automated by
`backend/tests/test_catalog_table_removal.py::test_removal_migration_preserves_core_data_and_only_drops_source_row_id`.

## T029 — metadata tables and archive guard

The migration drops the five metadata tables in foreign-key dependency order,
then the archive-guard function, inside the same transaction as T028:

```
drop table public.catalog_issues;
drop table public.catalog_repairs;
drop table public.catalog_source_rows;
drop table public.catalog_source_snapshots;
drop table public.catalog_import_batches;
drop function public.reject_catalog_archive_mutation();
```

Order rationale (verified against the live dependency graph):

- `catalog_issues` and `catalog_repairs` are leaf children (each FKs into
  `source_rows`, `snapshots`, and `import_batches`) — dropped first.
- `catalog_source_rows` FKs into `snapshots`; `catalog_source_snapshots` FKs into
  `import_batches`; `import_batches` is the root — dropped parents-last.
- `reject_catalog_archive_mutation()` is used only by immutability triggers on
  `catalog_source_snapshots` and `catalog_source_rows`. Those triggers drop with
  their tables, so the function has no remaining dependents and is removed last.

Each `drop table` removes that table's own triggers, RLS policies, indexes, and
owned sequences by ownership — no separate drops, no `CASCADE`, no wildcard.

### Final-schema fingerprint (removal migration applied, core-seeded)

| Item | Value |
| --- | --- |
| Applied migration versions | 20261022000100, 20261022000200, 20261022000300, **20261024034234** |
| `catalog_`-prefixed tables in public | 0 |
| `reject_catalog_archive_mutation()` present | no |
| `module_mappings.source_row_id` present | no |
| Core counts (degrees, nus_modules, degree_modules, specializations, specialization_modules, partner_universities, pu_modules, module_mappings) | 6, 152, 226, 19, 30, 5, 142, 151 |

(The 151 mapping count is the reviewed core-seed preview; the populated-upgrade
fixture carries 152 because it includes one intentional duplicate pair.)

Absence automated by `backend/tests/test_catalog_absence.py`
(`test_no_catalog_prefixed_tables_remain`, `test_named_metadata_tables_are_absent`,
`test_archive_guard_function_is_absent`,
`test_operational_sql_cannot_query_removed_relations`).

## T030 / T031 — retained constraints, RLS, and reader permissions

On the final schema (core-seeded):

- **Check constraints retained** (semantically compared, PG-normalized): the four
  core checks `verified_units > 0`, `kind in ('specialization','focus_area')`,
  `source_order >= 0`, `code = upper(btrim(code))`, and the six retained
  `module_mappings.source_*` checks.
- **RLS**: enabled on all eight core tables, each with its single
  `catalog_reader_select_*` SELECT policy for role `catalog_reader`.
- **Reader privileges**: SELECT on exactly the eight core tables and nothing
  else — the metadata-table grants vanished with the tables. No INSERT/UPDATE/
  DELETE and no new browser or write privilege was introduced.
- **Nullable unknowns and duplicates**: a mapping row with all `source_*` columns
  NULL and two rows for the same `(nus_module_code, pu_module_id)` pair both
  insert without violating any retained check or a (nonexistent) unique
  constraint.

Automated by `test_retained_core_check_constraints_present`,
`test_retained_keys_and_rls_policies`,
`test_reader_role_has_only_select_on_core_tables`,
`test_retained_mapping_check_constraints_present`, and
`test_mapping_nullable_unknowns_and_duplicates_remain_valid`.

## T032 — both migration paths + API response comparison

- **Populated-upgrade path**: legacy ceiling + populated provenance fixture +
  removal migration → only `source_row_id` removed, all eight core tables and the
  `module_mappings` sequence byte-for-byte identical (T024 test).
- **Fresh-replay path**: full migration chain from empty, then core seed → final
  schema with zero metadata tables (fingerprint above).
- **API response comparison**: a core-seeded API server on the final schema
  (reader role) compared against `baseline-responses.json`:

  ```bash
  LC_ALL=C LANG=C uv run python -m scripts.serve_catalog_api --host 127.0.0.1 --port 18767
  LC_ALL=C LANG=C uv run python -m scripts.compare_api_baseline compare \
    --base-url http://127.0.0.1:18767 \
    --baseline ../plan/remove-catalog-tables/baseline-responses.json \
    --report <scratch>/compare-final.md
  # -> Compared 41 requests ...: 0 differences, 0 failures   (PASS)
  ```

  All 41 requests (catalog, every degree's recommendations, every degree/
  university pair, four error cases) matched exactly. Successful DDL alone is not
  the evidence — the full response comparison on the final schema is.

## T033 — migration abort behavior (tested locally)

The runner applies the migration file with `psql -v ON_ERROR_STOP=1`; the
migration's own `begin … commit` means any statement failure rolls the whole
transaction back.

| Condition | Observed | Assertion |
| --- | --- | --- |
| Unexpected dependent object (a view on `catalog_import_batches`) | `DROP` fails under RESTRICT: "cannot drop table … because other objects depend on it"; rc≠0 | all five tables and `source_row_id` still present; migration not recorded as applied |
| Conflicting `ACCESS EXCLUSIVE` lock held on `module_mappings` in a second connection | migration aborts in **5.0s** with "canceling statement due to lock timeout"; rc≠0 | bounded wait (< 20s); all five tables and `source_row_id` still present |
| Normal path after releasing the lock | rc=0 | zero `catalog_` tables, `source_row_id` absent |

Transaction semantics confirmed: the single `begin/commit` plus RESTRICT and
`lock_timeout = '5s'` make the migration all-or-nothing and self-aborting on an
unexpected dependency or lock contention — no partial state, no forced retry.

Automated by `test_migration_aborts_on_unexpected_dependency` and
`test_migration_aborts_on_conflicting_lock_then_normal_path`.
