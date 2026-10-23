# Behavior acceptance matrix

Date: 2026-10-23. Scope: T003 invariants extracted from
`plan/contracts/openapi.yaml`, `backend/app/repositories/postgres_catalog.py`,
`backend/app/models.py`, `backend/app/main.py`, `backend/app/database.py`, and
`frontend/tests/`.

The matrix separates behavior that already has executable coverage from behavior
that will be covered by the tasks in `tasks.md`. Planned test IDs are the source
of truth for new coverage; existing test names are evidence that the behavior is
currently exercised.

## API contract and repository behavior

| # | Invariant | Contract/runtime evidence | Existing coverage | Planned coverage |
| --- | --- | --- | --- | --- |
| A1 | Catalog degrees are ordered by `source_order nulls last, id` | `CATALOG_DEGREES_SQL`; `/catalog` schema requires `name` and `degree` | `test_postgres_repository.py::test_catalog_uses_source_order_and_full_titles` | T015 review; T066 parity |
| A2 | Catalog universities are ordered by `source_order nulls last, id` | `CATALOG_UNIVERSITIES_SQL` | Same catalog test | T015, T066 |
| A3 | `degree` is the persisted `degrees.full_title`; a null full title makes the catalog unavailable | Runtime catalog validation; data-model constraint | `test_degree_without_full_title_is_treated_as_incomplete` | T012 readiness case |
| A4 | Recommendations include every university, including zero-count partners | `RANKINGS_SQL` left join; OpenAPI says zero counts included | `test_rankings_include_zero_counts_and_order_by_distinct_nus` | T015, T066 |
| A5 | Recommendations rank by distinct NUS module count descending, then university name using `C` collation ascending | `RANKINGS_SQL` `order by ... u.name collate "C" asc` | `test_rankings_include_zero_counts_and_order_by_distinct_nus`; `test_catalog.py::test_current_catalog_and_consistency` | T015, T066 |
| A6 | Ranking ties keep deterministic university-name order, including case-sensitive `C` ordering | Same SQL ordering | `test_repository_regression.py::test_synthetic_adapters_agree_on_ties_repeats_nulls_and_units` | T066 |
| A7 | `mapping_count` counts mapping rows, not distinct pairs | `count(*)` in `RANKINGS_SQL`; response model integer | Ranking and mapping fixtures | T015, T066 |
| A8 | `distinct_nus_module_count` counts distinct NUS codes case-insensitively | `count(distinct mm.nus_module_code)` with normalized codes | `test_catalog.py::test_current_catalog_and_consistency` | T015, T066 |
| A9 | `partner_module_count` counts distinct partner codes case-insensitively | `count(distinct upper(pm.code))`; response construction uses `.upper()` | `test_partner_code_deduplication_ties_and_zero_pairs` | T015, T066 |
| A10 | Mappings are ordered by NUS code `C` ascending, then `source_order nulls last`, then mapping `id` | `MAPPINGS_SQL` ordering | `test_mappings_filter_sort_and_preserve_repeated_rows` | T015, T066 |
| A11 | Repeated mapping rows and repeated course pairs are preserved as independent occurrences | No unique course-pair constraint; mappings query returns all rows | `test_mappings_filter_sort_and_preserve_repeated_rows`; `test_catalog.py::test_duplicate_rows_and_stable_tie_order` | T024, T030/T031, T064 |
| A12 | Mapping optional fields are omitted, not serialized as `null` | `response_model_exclude_none=True` in `main.py`; `Course` defaults | `test_json_repository.py::test_mapping_rows_preserve_order_optional_fields_and_units`; frontend flow for absent units | T015, T066 |
| A13 | NUS titles fall back from `module_mappings.source_nus_title` to `nus_modules.name` | `coalesce(mm.source_nus_title, nm.name)` | `test_mapping_optional_fields_and_partner_unit_fallbacks` | T015, T066 |
| A14 | Partner titles fall back from `module_mappings.source_partner_title` to `pu_modules.name` | `coalesce(mm.source_partner_title, pm.name)` | Same mapping test | T015, T066 |
| A15 | Partner units fall back from `module_mappings.source_partner_units` to `pu_modules.verified_units`; unknown units stay absent | `coalesce(...)` and `_optional_float` | `test_mapping_optional_fields_and_partner_unit_fallbacks` | T015, T031, T066 |
| A16 | NUS units are always displayed as `4` | Runtime constructs `units=4` | `test_mappings_filter_sort_and_preserve_repeated_rows`; frontend `flows.spec.ts` | T015, T066, T069 |
| A17 | Unknown degree returns 404 with `Unknown degree` | `_require_degree` and `main.py` error mapping | `test_unknown_degree_is_not_a_server_error`; `test_unknown_selections_and_missing_parameters` | T016, T067 |
| A18 | Unknown degree/university pair returns 404 with `Unknown degree or university` | `DEGREE_UNIVERSITY_IDS_SQL` and `UnknownSelection` | `test_unknown_mapping_selections_raise_shared_error`; frontend invalid-link flow | T016, T067 |
| A19 | Missing required query parameters return 422 | FastAPI parameter declarations in `main.py` | `test_unknown_selections_and_missing_parameters` | T067 |
| A20 | A known pair with no mappings returns 200 with empty `mappings` and zero counts | No mapping-count readiness requirement | `test_valid_empty_pair_returns_zero_counts`; frontend empty-state flows | T012, T067 |
| A21 | Empty degrees, empty universities, or a null degree full title make all three operations return the sanitized 503 | New core-readiness contract in `plan.md`; historical batch check currently returns 503 | `test_unpublished_database_is_unavailable`; `test_completed_batch_without_degrees_is_unavailable` | T012, T013, T014, T017, T067 |
| A22 | Database outages, statement timeouts, pool exhaustion, and shutdown return sanitized 503s or recover without leaking connection details | `database.py` error translation; OpenAPI 503 response | `test_database_failures.py` timeout, pool, pause, shutdown, and secret checks | T017, T067 |
| A23 | A PostgreSQL failure never falls back to JSON automatically | `build_repository` selects one adapter from explicit settings | `test_database_outage_returns_503_without_json_fallback`; `test_unpublished_catalog_returns_503_without_json_fallback` | T017, T045, T067 |
| A24 | JSON mode remains an explicit manual fallback and works without database credentials | `CATALOG_BACKEND=json`; `JsonCatalogRepository` | `test_manual_json_rollback_serves_the_frozen_catalog_without_database`; JSON browser suite | T046, T072 |
| A25 | CORS allows only configured exact origins and `GET` | `CORS_ORIGINS` parsing and `CORSMiddleware` | No automated assertion found in backend tests | T069 (browser/CORS), plus production check in T044 |
| A26 | Runtime SQL never queries a removed metadata relation | Current `PUBLISHED_BATCH_SQL` is the only metadata runtime query | None after removal | T013, T025, T045, T067 |
| A27 | Runtime readiness is parameterless and evaluated inside each read transaction, without per-request catalog introspection | Design decision in `plan.md` | None | T013, T014, T015 |
| A28 | Source presentation/order fields on core tables remain authoritative | Schema/data-model; runtime uses `source_order` and row titles/units | Mapping and ranking fixtures | T015, T024, T030/T031, T064 |

## Schema and data-preservation behavior

| # | Invariant | Evidence | Planned coverage |
| --- | --- | --- | --- |
| S1 | Only the five named metadata tables are dropped; no wildcard/prefix deletion | `spec.md`, `plan.md` | T026, T029, T037, T038, T064 |
| S2 | Only `module_mappings.source_row_id`, its foreign key, and its unique key are removed from core tables | `data-model.md` | T024, T028, T030, T031 |
| S3 | Eight core tables keep IDs, rows, sequence state, constraints, indexes, RLS, and reader policies | `data-model.md` | T024, T030, T031, T032, T064 |
| S4 | Removed `source_row_id` values are recoverable by mapping ID from the private export | `plan.md`, `recovery.md` plan | T007, T035, T039, T078 |
| S5 | `catalog_import_batches`, `catalog_source_snapshots`, `catalog_source_rows`, `catalog_issues`, and `catalog_repairs` are absent after migration | `spec.md`, `plan.md` | T025, T029, T032, T038, T064 |
| S6 | `reject_catalog_archive_mutation()` is dropped only after dependency inspection | `plan.md` | T029, T032, T038 |
| S7 | Migration aborts on unexpected dependencies or lock timeout without partial changes | `plan.md` | T026, T033 |
| S8 | Upgrade from the pre-removal migration ceiling preserves core data and provenance-linked mappings | `plan.md` | T010, T011, T024, T032 |
| S9 | Fresh replay ends with no public `catalog_*` table | `spec.md` | T025, T032, T064 |
| S10 | Retained mapping checks permit nullable unknowns and repeated course pairs | `data-model.md` | T030, T031 |

## Frontend behavior

| # | Invariant | Existing coverage | Planned coverage |
| --- | --- | --- | --- |
| F1 | Initial catalog load exposes both selectors and no fabricated results | `app-shell.spec.ts`, `recommend-picker.spec.ts`, `flows.spec.ts` | T021, T044, T057, T069 |
| F2 | Degree search/filter and keyboard behavior are unchanged | `recommend-picker.spec.ts` | T021, T044, T069 |
| F3 | Recommendation cards show rank, full university name/country, distinct NUS count, and partner-module count; `mapping_count` is not rendered | `recommend-card.spec.ts`, `flows.spec.ts` | T021, T044, T069 |
| F4 | Zero-count universities remain visible and rank deterministically | `flows.spec.ts`, `recommend-card.spec.ts` | T021, T044, T069 |
| F5 | "View Mappings" deep links preserve degree/university query state | `flows.spec.ts`, `database-regression.spec.ts` | T021, T044, T057, T069 |
| F6 | Mapping rows preserve repeated rows, row titles, optional units, and counts | `database-regression.spec.ts`, `flows.spec.ts` | T021, T044, T057, T069 |
| F7 | Browser back/forward restore both selectors and result state | `app-shell.spec.ts`, `database-regression.spec.ts` | T021, T044, T069 |
| F8 | Loading, service-error, unknown-selection, and valid-empty states stay explicit | `flows.spec.ts`, `recommend-picker.spec.ts`, `database-regression.spec.ts` | T021, T044, T069 |
| F9 | Late responses for superseded selections never replace current results | `flows.spec.ts`, `recommend-picker.spec.ts`, `database-regression.spec.ts` | T021, T044, T069 |
| F10 | Old `/compare` links redirect to `/mappings` and preserve selections | `flows.spec.ts` | T021, T044, T069 |
| F11 | Desktop and mobile layouts avoid horizontal overflow and keep mapping rows readable | `database-regression.spec.ts`, `recommend-visual.spec.ts` | T021, T044, T069 |

## Explicit differences between JSON and PostgreSQL modes

The frozen JSON snapshot and the repaired PostgreSQL catalog intentionally differ
for four Toronto pairs. These differences are documented in
`plan/supabase-migration/data-deltas.md` and must not be normalized away:

| Degree / University | JSON mapping rows | PostgreSQL mapping rows |
| --- | ---: | ---: |
| Artificial Intelligence / University of Toronto | 9 | 10 |
| Business Analytics / University of Toronto | 18 | 19 |
| Computer Science / University of Toronto | 6 | 7 |
| Information Security / University of Toronto | 7 | 8 |

`test_repository_regression.py` already encodes these deltas and the valid-empty
pairs. T066 must keep them as reviewed exceptions rather than regenerating
expectations from the implementation under test.

## Coverage gaps to close before the final gate

- Core-readiness cases for empty degrees, empty universities, null full titles,
  and complete choices with no mappings (T012).
- Runtime independence from metadata-table permissions (T013).
- Unready-core 503s and no-fallback behavior for the new readiness contract (T017).
- Physical absence, removed-function dependencies, and final-schema runtime (T025).
- Upgrade preservation including populated `source_row_id` links (T024).
- Retained constraints, RLS, and reader privileges after removal (T030, T031, T056).
- CORS assertion in automated browser/backend coverage (T044, T069).
- Explicit JSON fallback after removal and return to PostgreSQL (T046, T072).
