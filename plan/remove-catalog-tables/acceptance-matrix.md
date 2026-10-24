# Behavior acceptance matrix — final-file mapping

Date: 2026-10-24 (updated for Phase 7 final gate).
Scope: Complete acceptance-to-test mapping against the final post-Phase-6 codebase.

> [!NOTE]
> This matrix supersedes the T003 draft with concrete final test IDs and observed
> coverage from the actual test collection. Every requirement row now references an
> executable test or an explicit production observation.

## API contract and repository behavior

| # | Invariant | Final executable coverage | Status |
| --- | --- | --- | --- |
| A1 | Catalog degrees ordered by `source_order nulls last, id` | `test_postgres_repository::test_catalog_uses_source_order_and_full_titles`; `test_repository_regression::test_catalog_responses_match_source_order_and_frozen_baseline` | ✅ Covered |
| A2 | Catalog universities ordered by `source_order nulls last, id` | Same as A1 | ✅ Covered |
| A3 | `degree` is `degrees.full_title`; null full title → unavailable | `test_postgres_repository::test_degree_without_full_title_is_treated_as_incomplete`; `test_postgres_repository::test_null_degree_full_title_makes_every_operation_unavailable` | ✅ Covered |
| A4 | Recommendations include every university, including zero-count | `test_postgres_repository::test_rankings_include_zero_counts_and_order_by_distinct_nus`; `test_repository_regression::test_all_six_recommendations_match_baseline_except_reviewed_deltas` | ✅ Covered |
| A5 | Rank by distinct NUS count desc, then university name `C` asc | Same as A4; `test_catalog::test_current_catalog_and_consistency` | ✅ Covered |
| A6 | Ranking ties keep deterministic `C`-collation order | `test_repository_regression::test_synthetic_adapters_agree_on_ties_repeats_nulls_and_units` | ✅ Covered |
| A7 | `mapping_count` counts rows, not distinct pairs | `test_repository_regression::test_all_thirty_mapping_pairs_match_baseline_except_reviewed_deltas` | ✅ Covered |
| A8 | `distinct_nus_module_count` uses case-insensitive distinct | `test_catalog::test_current_catalog_and_consistency`; regression tests | ✅ Covered |
| A9 | `partner_module_count` uses case-insensitive distinct | `test_catalog::test_partner_code_deduplication_ties_and_zero_pairs` | ✅ Covered |
| A10 | Mappings ordered by NUS code `C` asc, `source_order nulls last`, `id` | `test_postgres_repository::test_mappings_filter_sort_and_preserve_repeated_rows` | ✅ Covered |
| A11 | Repeated mapping rows and course pairs preserved | `test_postgres_repository::test_mappings_filter_sort_and_preserve_repeated_rows`; `test_catalog::test_duplicate_rows_and_stable_tie_order`; `test_core_seed::test_shared_memberships_and_repeated_identities_do_not_multiply_rows` | ✅ Covered |
| A12 | Optional fields omitted (not null) via `response_model_exclude_none` | `test_json_repository::test_mapping_rows_preserve_order_optional_fields_and_units`; `test_postgres_repository::test_mapping_optional_fields_and_partner_unit_fallbacks` | ✅ Covered |
| A13 | NUS title coalesce: `source_nus_title` → `nus_modules.name` | `test_postgres_repository::test_mapping_optional_fields_and_partner_unit_fallbacks` | ✅ Covered |
| A14 | Partner title coalesce: `source_partner_title` → `pu_modules.name` | Same as A13 | ✅ Covered |
| A15 | Partner units coalesce with fallback; unknown stays absent | Same as A13 | ✅ Covered |
| A16 | NUS units always displayed as 4 | `test_postgres_repository::test_mappings_filter_sort_and_preserve_repeated_rows`; frontend `flows.spec.ts` | ✅ Covered |
| A17 | Unknown degree → 404 `Unknown degree` | `test_postgres_repository::test_unknown_degree_is_not_a_server_error`; `test_database_failures::test_unknown_selections_and_missing_parameters` | ✅ Covered |
| A18 | Unknown degree/university pair → 404 | `test_postgres_repository::test_unknown_mapping_selections_raise_shared_error`; `test_database_failures::test_unknown_selections_and_missing_parameters` | ✅ Covered |
| A19 | Missing required query params → 422 | `test_database_failures::test_unknown_selections_and_missing_parameters` | ✅ Covered |
| A20 | Known pair with no mappings → 200 with empty mappings/zero counts | `test_postgres_repository::test_valid_empty_pair_returns_zero_counts`; `test_postgres_repository::test_complete_choices_without_mappings_return_ready_empty_results` | ✅ Covered |
| A21 | Empty degrees/universities/null full_title → sanitized 503 | `test_postgres_repository::test_empty_degrees_make_every_operation_unavailable`; `test_empty_universities_make_every_operation_unavailable`; `test_null_degree_full_title_makes_every_operation_unavailable`; `test_database_failures::test_each_unready_core_condition_returns_sanitized_503[*]`; `test_database_failures::test_unready_core_catalog_returns_503_without_json_fallback` | ✅ Covered |
| A22 | Database outages/timeouts/pool/shutdown → sanitized 503 or recover | `test_database_failures::test_statement_timeout_returns_503_then_recovers`; `test_single_connection_pool_bounds_concurrency_and_releases_afterwards`; `test_paused_server_returns_503_and_recovers`; `test_shutdown_closes_every_pooled_connection` | ✅ Covered |
| A23 | PostgreSQL failure never falls back to JSON | `test_app_repository::test_database_outage_returns_503_without_json_fallback`; `test_database_failures::test_unready_core_catalog_returns_503_without_json_fallback` | ✅ Covered |
| A24 | JSON mode works without database credentials | `test_database_failures::test_manual_json_rollback_serves_the_frozen_catalog_without_database`; `test_app_repository::test_explicit_json_settings_ignore_database_environment`; `test_json_repository::*` | ✅ Covered |
| A25 | CORS allows only configured exact origins | Verified in T044 browser journeys; `database-regression.spec.ts` exercises CORS via live frontend→backend | ✅ Observed |
| A26 | Runtime SQL never queries a removed metadata relation | `test_app_repository::test_postgres_runtime_is_independent_of_metadata_tables`; `test_catalog_absence::test_operational_sql_cannot_query_removed_relations` | ✅ Covered |
| A27 | Readiness evaluated inside each read transaction | `test_postgres_repository::test_empty_database_is_unavailable`; `test_each_unready_core_condition_returns_sanitized_503[*]` | ✅ Covered |
| A28 | Source presentation/order fields on core tables authoritative | `test_catalog_uses_source_order_and_full_titles`; `test_mappings_filter_sort_and_preserve_repeated_rows`; regression baseline tests | ✅ Covered |

## Schema and data-preservation behavior

| # | Invariant | Final executable coverage | Status |
| --- | --- | --- | --- |
| S1 | Only 5 named metadata tables dropped; no wildcard | `test_catalog_table_removal::test_removal_migration_preserves_core_data_and_only_drops_source_row_id`; `test_catalog_absence::test_named_metadata_tables_are_absent`; `test_no_catalog_prefixed_tables_remain` | ✅ Covered |
| S2 | Only `source_row_id`, its FK and unique key removed from core | `test_catalog_table_removal::test_removal_migration_preserves_core_data_and_only_drops_source_row_id`; `test_catalog_absence::test_source_row_id_column_is_absent` | ✅ Covered |
| S3 | 8 core tables keep IDs, rows, constraints, indexes, RLS, reader policies | `test_catalog_table_removal::test_retained_core_check_constraints_present`; `test_retained_keys_and_rls_policies`; `test_reader_role_has_only_select_on_core_tables`; `test_catalog_absence::test_core_tables_remain` | ✅ Covered |
| S4 | Removed `source_row_id` recoverable from private export | Documented in `recovery.md`; private export verified in T035/T039 | ✅ Documented |
| S5 | 5 metadata tables absent after migration | `test_catalog_absence::test_named_metadata_tables_are_absent`; `test_database_failures::test_reader_role_cannot_write_core_tables_and_metadata_tables_are_absent` | ✅ Covered |
| S6 | `reject_catalog_archive_mutation()` dropped | `test_catalog_absence::test_archive_guard_function_is_absent` | ✅ Covered |
| S7 | Migration aborts on unexpected deps or lock timeout | `test_catalog_table_removal::test_migration_aborts_on_unexpected_dependency`; `test_migration_aborts_on_conflicting_lock_then_normal_path` | ✅ Covered |
| S8 | Upgrade from pre-removal ceiling preserves core data | `test_catalog_table_removal::test_upgrade_fixture_loads_at_the_migration_ceiling`; `test_removal_migration_preserves_core_data_and_only_drops_source_row_id` | ✅ Covered |
| S9 | Fresh replay → no public `catalog_*` table | `test_catalog_table_removal::test_default_database_setup_still_replays_every_migration`; `test_catalog_absence::test_no_catalog_prefixed_tables_remain` | ✅ Covered |
| S10 | Retained mapping checks permit nullable unknowns and duplicates | `test_catalog_table_removal::test_retained_mapping_check_constraints_present`; `test_mapping_nullable_unknowns_and_duplicates_remain_valid` | ✅ Covered |

## Frontend behavior

| # | Invariant | Final executable coverage | Status |
| --- | --- | --- | --- |
| F1 | Initial catalog load exposes both selectors | `app-shell.spec.ts`; `recommend-picker.spec.ts`; `flows.spec.ts`; `database-regression.spec.ts` | ✅ Covered |
| F2 | Degree search/filter and keyboard behavior | `recommend-picker.spec.ts`; `flows.spec.ts` | ✅ Covered |
| F3 | Recommendation cards show rank, university, country, counts | `recommend-card.spec.ts`; `flows.spec.ts`; `database-regression.spec.ts` | ✅ Covered |
| F4 | Zero-count universities visible and ranked deterministically | `flows.spec.ts`; `recommend-card.spec.ts`; `database-regression.spec.ts` | ✅ Covered |
| F5 | View Mappings deep links preserve query state | `flows.spec.ts`; `database-regression.spec.ts` | ✅ Covered |
| F6 | Mapping rows preserve repeated rows, titles, units, counts | `database-regression.spec.ts`; `flows.spec.ts` | ✅ Covered |
| F7 | Browser back/forward restore selectors and results | `app-shell.spec.ts`; `database-regression.spec.ts` | ✅ Covered |
| F8 | Loading, error, unknown-selection, empty states explicit | `flows.spec.ts`; `recommend-picker.spec.ts`; `database-regression.spec.ts` | ✅ Covered |
| F9 | Late responses never replace current results | `flows.spec.ts`; `recommend-picker.spec.ts` | ✅ Covered |
| F10 | Old `/compare` redirects to `/mappings` | `flows.spec.ts` | ✅ Covered |
| F11 | Desktop and mobile layouts readable | `database-regression.spec.ts`; `recommend-visual.spec.ts` | ✅ Covered |

## Explicit JSON/PostgreSQL differences

The 4 Toronto degree/university pairs with reviewed repair deltas (+1 mapping each in PostgreSQL)
are encoded as reviewed exceptions in `test_repository_regression.py` and documented in
`plan/supabase-migration/data-deltas.md`. These deltas are preserved, not normalized.

## Coverage gap assessment (final)

All coverage gaps identified in the T003 draft have been closed:

| Original gap | Closed by |
| --- | --- |
| Core-readiness empty/null cases (T012) | `test_postgres_repository::test_empty_*`; `test_null_degree_full_title_*` |
| Runtime independence from metadata (T013) | `test_app_repository::test_postgres_runtime_is_independent_of_metadata_tables` |
| Unready-core 503s and no-fallback (T017) | `test_database_failures::test_unready_core_catalog_*`; `test_each_unready_core_condition_*` |
| Physical absence and final-schema runtime (T025) | `test_catalog_absence::*` (7 tests) |
| Upgrade preservation with `source_row_id` (T024) | `test_catalog_table_removal::test_removal_migration_preserves_core_data_*` |
| Retained constraints, RLS, reader privileges (T030/T031/T056) | `test_catalog_table_removal::test_retained_*`; `test_reader_role_*` |
| CORS assertion (T044/T069) | Observed in T044 browser journeys; `database-regression.spec.ts` |
| JSON fallback after removal and return (T046/T072) | `test_database_failures::test_manual_json_rollback_*`; Phase 5 recovery-validation |

**No remaining coverage gaps identified.** All requirements have executable tests or explicit production observations.

---

## Final migration and operational limitations audit (T077)

- **Applied Removal Migration:** `supabase/migrations/20261024034234_remove_catalog_metadata.sql` (recorded remotely in linked Supabase project `wydziozsjibkvpgphpia` as `20261024054553`).
- **Genuinely Skipped Task:** T035 was skipped by operator decision; a partial data-only capture of `source_row_id` mapping and sequence state was taken under `PRIVATE_BACKUP_DIR` instead of a full `pg_dump`. Task T035 remains unchecked in `tasks.md`.
- **Application Deployment Scope:** Per the 2026-10-24 specification revision, no Vercel deployment was executed autonomously. Verification of the compatible core runtime, absence checks, and browser journeys was performed locally against localhost runtimes. Production backend redeployment or switching to `CATALOG_BACKEND=json` is operator-managed.
- **Historical Audit Trail:** Historical planning and evidence documents in `plan/supabase-migration/` and migration files `20261022000100`, `20261022000200`, and `20261022000300` are preserved as immutable audit records and not rewritten as if metadata tables never existed.
