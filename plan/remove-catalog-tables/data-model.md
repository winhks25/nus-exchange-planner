# Data model after catalog metadata removal

No replacement tables are introduced. Preserve the eight business tables and their current relationships.

| Table | Purpose | Required preservation |
| --- | --- | --- |
| `degrees` | Degree choices | IDs, unique names, faculty, full title, source order |
| `nus_modules` | NUS module facts | Codes, nullable names, offering faculty, verified units |
| `degree_modules` | Degree eligibility | Composite identity, module/degree foreign keys, requirement type |
| `specializations` | Specializations and focus areas | IDs, degree relation, name, kind, source order |
| `specialization_modules` | Specialization membership | Composite identity and both foreign keys |
| `partner_universities` | University choices | IDs, name, country, city, continent, source order |
| `pu_modules` | Partner module facts | IDs, university relation, code, nullable name, verified units |
| `module_mappings` | Mapping occurrences | IDs, both course relations, source order, row titles/units/faculty/page; remove only source_row_id |

## Existing constraints that must remain

These are quoted from the checked-in schema; inspect live DDL for additional constraints before implementation:

- `degrees.full_title`: `check (full_title is null or btrim(full_title) <> '')`. The schema permits null; runtime readiness rejects any degree with a null full title.
- `degrees.source_order`, `partner_universities.source_order`, and `specializations.source_order`: `check (source_order is null or source_order >= 0)`. Preserve their existing partial unique indexes and scopes.
- `nus_modules.verified_units` and `pu_modules.verified_units`: `check (verified_units is null or verified_units > 0)`.
- `specializations.kind`: `check (kind in ('specialization', 'focus_area'))`.
- `module_mappings.source_order`: `check (source_order is null or source_order >= 0)`.
- `module_mappings.source_nus_title`: `check (source_nus_title is null or btrim(source_nus_title) <> '')`.
- `module_mappings.source_partner_title`: `check (source_partner_title is null or btrim(source_partner_title) <> '')`.
- `module_mappings.source_nus_units`: `check (source_nus_units is null or source_nus_units > 0)`.
- `module_mappings.source_partner_units`: `check (source_partner_units is null or source_partner_units > 0)`.
- `module_mappings.source_faculty`: `check (source_faculty is null or btrim(source_faculty) <> '')`.
- `module_mappings.source_page`: `check (source_page is null or source_page > 0)`.
- NUS and partner codes retain `check (btrim(code) <> '' and code = upper(btrim(code)))`.

Keep original primary keys, unique keys, foreign keys between core tables, nonblank text checks, nullable unknown names, numeric precision, and identity sequences. Do not add a unique course-pair constraint: equal pairs at different mapping IDs are intentional independent occurrences. Do not make source_order globally unique on module_mappings; preserve current ordering semantics.

## Removed objects

`public.catalog_import_batches`, `public.catalog_source_snapshots`, `public.catalog_source_rows`, `public.catalog_issues`, `public.catalog_repairs`; their owned subordinate objects; `module_mappings_source_row_id_fkey`, `module_mappings_source_row_id_key`, `module_mappings.source_row_id`; and `public.reject_catalog_archive_mutation()` after checking it has no remaining users.

Runtime role names, API/type names, checked-in repair files, and migration history are not tables and are retained as needed.

## Snapshot semantics

For production before/after checks, compare all retained columns and row multiplicity, including IDs and sequence state, with deterministic serialization. Save removed source_row_id separately. For independently seeded local databases, resolve generated IDs through natural-key relationships before comparing; compare mappings as an ordered list or multiset with multiplicity, never a set of course pairs. SQL NULL and omitted API fields are different representations and must each be tested in the appropriate layer.
