# Live schema inventory before catalog-table removal

Date: 2026-10-23 (Asia/Singapore). Scope: T006 read-only inventory of the
verified production database before any destructive change.

## Verification method

| Item | Value |
| --- | --- |
| Target project | `wydziozsjibkvpgphpia` (`nus-exchange-planner`) |
| Database | `postgres` on PostgreSQL `17.11` |
| Inspection path | Supabase MCP read-only SQL; no CLI session |
| Session user | `postgres` (server-side inspection only) |
| Mutation performed | None |
| Migration history | `20261022000100`, `20261022000200`, `20261022000300` |

This inventory is the authoritative live-schema reference for T026-T038. It is
not a substitute for the stored export or for the pre-migration dependency
recheck at the production change boundary.

## Application schema summary

All thirteen application relations are ordinary tables in `public`. No view,
materialized view, partitioned table, foreign table, or matching application
table exists in another schema. The only relations matching `catalog%` in any
schema are the five removal targets in `public`.

| Table | Kind | Owner | RLS | Forced RLS | Rows | Total size | Removal target |
| --- | --- | --- | --- | --- | ---: | ---: | --- |
| `catalog_import_batches` | table | `postgres` | enabled | no | 1 | 64 kB | yes |
| `catalog_source_snapshots` | table | `postgres` | enabled | no | 8 | 136 kB | yes |
| `catalog_source_rows` | table | `postgres` | enabled | no | 154 | 168 kB | yes |
| `catalog_issues` | table | `postgres` | enabled | no | 34 | 80 kB | yes |
| `catalog_repairs` | table | `postgres` | enabled | no | 44 | 112 kB | yes |
| `degrees` | table | `postgres` | enabled | no | 6 | 64 kB | no |
| `nus_modules` | table | `postgres` | enabled | no | 152 | 32 kB | no |
| `degree_modules` | table | `postgres` | enabled | no | 226 | 96 kB | no |
| `specializations` | table | `postgres` | enabled | no | 19 | 64 kB | no |
| `specialization_modules` | table | `postgres` | enabled | no | 30 | 48 kB | no |
| `partner_universities` | table | `postgres` | enabled | no | 5 | 64 kB | no |
| `pu_modules` | table | `postgres` | enabled | no | 142 | 80 kB | no |
| `module_mappings` | table | `postgres` | enabled | no | 151 | 136 kB | no |

All thirteen tables are permanent (`p`), use the default replica identity, and
live in `pg_default`. All identities are `bigint generated always as identity`
with start/current values recorded below.

## Removed metadata tables

### `public.catalog_import_batches`

| Column | Type | Null | Default / identity |
| --- | --- | --- | --- |
| `id` | `bigint` | no | identity always, start 1, increment 1 |
| `source_checksum` | `char(64)` | no | none |
| `repair_checksum` | `char(64)` | no | none |
| `status` | `text` | no | `'running'::text` |
| `is_current` | `boolean` | no | `false` |
| `source_manifest` | `jsonb` | no | `'{}'::jsonb` |
| `source_file_count` | `integer` | no | `0` |
| `raw_row_count` | `integer` | no | `0` |
| `accepted_row_count` | `integer` | no | `0` |
| `repaired_row_count` | `integer` | no | `0` |
| `quarantined_row_count` | `integer` | no | `0` |
| `started_at` | `timestamptz` | no | `now()` |
| `completed_at` | `timestamptz` | yes | none |
| `note` | `text` | yes | none |

Constraints:

- `catalog_import_batches_pkey` primary key (`id`).
- `catalog_import_batches_source_checksum_check` check (`source_checksum ~ '^[0-9a-f]{64}$'`).
- `catalog_import_batches_repair_checksum_check` check (`repair_checksum ~ '^[0-9a-f]{64}$'`).
- `catalog_import_batches_status_check` check (`status in ('running', 'completed', 'failed')`).
- `catalog_import_batches_source_manifest_check` check (`jsonb_typeof(source_manifest) = 'object'`).
- `catalog_import_batches_source_file_count_check` check (`source_file_count >= 0`).
- `catalog_import_batches_raw_row_count_check` check (`raw_row_count >= 0`).
- `catalog_import_batches_accepted_row_count_check` check (`accepted_row_count >= 0`).
- `catalog_import_batches_repaired_row_count_check` check (`repaired_row_count >= 0`).
- `catalog_import_batches_quarantined_row_count_check` check (`quarantined_row_count >= 0`).
- `catalog_import_batches_current_completed_check` check (`not is_current or status = 'completed'`).
- `catalog_import_batches_completed_at_check` check (`(status = 'completed') = (completed_at is not null)`).
- `catalog_import_batches_note_check` check (`note is null or btrim(note) <> ''`).

Indexes:

- `catalog_import_batches_pkey` unique (`id`).
- `catalog_import_batches_completed_key` unique (`source_checksum`, `repair_checksum`) where `status = 'completed'`.
- `catalog_import_batches_current_key` unique (`is_current`) where `is_current`.

Policies: `catalog_reader_select_import_batches`, SELECT to `catalog_reader`, `using (true)`.
Sequence: `catalog_import_batches_id_seq`, owned by `id`, last value 1.

### `public.catalog_source_snapshots`

| Column | Type | Null | Default / identity |
| --- | --- | --- | --- |
| `id` | `bigint` | no | identity always, start 1, increment 1 |
| `batch_id` | `bigint` | no | none |
| `file_path` | `text` | no | none |
| `source_kind` | `text` | no | none |
| `raw_text` | `text` | no | none |
| `parsed_json` | `jsonb` | no | none |
| `sha256` | `char(64)` | no | none |
| `byte_size` | `bigint` | no | none |
| `archived_at` | `timestamptz` | no | `now()` |

Constraints:

- `catalog_source_snapshots_pkey` primary key (`id`).
- `catalog_source_snapshots_batch_id_file_path_key` unique (`batch_id`, `file_path`).
- `catalog_source_snapshots_batch_id_fkey` foreign key (`batch_id`) references `catalog_import_batches(id)`.
- `catalog_source_snapshots_file_path_check` check (`btrim(file_path) <> ''`).
- `catalog_source_snapshots_source_kind_check` check (`source_kind in ('majors', 'mapping', 'repairs', 'manifest')`).
- `catalog_source_snapshots_raw_text_check` check (`length(raw_text) > 0`).
- `catalog_source_snapshots_sha256_check` check (`sha256 ~ '^[0-9a-f]{64}$'`).
- `catalog_source_snapshots_byte_size_check` check (`byte_size >= 0`).

Indexes:

- `catalog_source_snapshots_pkey` unique (`id`).
- `catalog_source_snapshots_batch_id_file_path_key` unique (`batch_id`, `file_path`).
- `catalog_source_snapshots_batch_idx` (`batch_id`).

Policies: none. Triggers: `catalog_source_snapshots_immutable` (BEFORE UPDATE OR DELETE, row) and `catalog_source_snapshots_no_truncate` (BEFORE TRUNCATE, statement), both `reject_catalog_archive_mutation()`.
Sequence: `catalog_source_snapshots_id_seq`, owned by `id`, last value 8.

### `public.catalog_source_rows`

| Column | Type | Null | Default / identity |
| --- | --- | --- | --- |
| `id` | `bigint` | no | identity always, start 1, increment 1 |
| `snapshot_id` | `bigint` | no | none |
| `mapping_index` | `integer` | no | none |
| `raw_json` | `jsonb` | no | none |
| `source_nus_code` | `text` | no | none |
| `source_partner_code` | `text` | no | none |
| `source_nus_title` | `text` | yes | none |
| `source_partner_title` | `text` | yes | none |
| `source_nus_units` | `numeric(8,2)` | yes | none |
| `source_partner_units` | `numeric(8,2)` | yes | none |
| `source_faculty` | `text` | yes | none |
| `source_page` | `integer` | yes | none |
| `outcome` | `text` | no | `'accepted'::text` |
| `created_at` | `timestamptz` | no | `now()` |

Constraints:

- `catalog_source_rows_pkey` primary key (`id`).
- `catalog_source_rows_snapshot_id_mapping_index_key` unique (`snapshot_id`, `mapping_index`).
- `catalog_source_rows_snapshot_id_fkey` foreign key (`snapshot_id`) references `catalog_source_snapshots(id)`.
- `catalog_source_rows_mapping_index_check` check (`mapping_index >= 0`).
- `catalog_source_rows_raw_json_check` check (`jsonb_typeof(raw_json) = 'object'`).
- `catalog_source_rows_source_nus_code_check` check (`btrim(source_nus_code) <> ''`).
- `catalog_source_rows_source_partner_code_check` check (`btrim(source_partner_code) <> ''`).
- `catalog_source_rows_source_nus_title_check` check (`source_nus_title is null or btrim(source_nus_title) <> ''`).
- `catalog_source_rows_source_partner_title_check` check (`source_partner_title is null or btrim(source_partner_title) <> ''`).
- `catalog_source_rows_source_nus_units_check` check (`source_nus_units is null or source_nus_units > 0`).
- `catalog_source_rows_source_partner_units_check` check (`source_partner_units is null or source_partner_units > 0`).
- `catalog_source_rows_source_faculty_check` check (`source_faculty is null or btrim(source_faculty) <> ''`).
- `catalog_source_rows_source_page_check` check (`source_page is null or source_page > 0`).
- `catalog_source_rows_outcome_check` check (`outcome in ('accepted', 'repaired', 'quarantined')`).

Indexes:

- `catalog_source_rows_pkey` unique (`id`).
- `catalog_source_rows_snapshot_id_mapping_index_key` unique (`snapshot_id`, `mapping_index`).
- `catalog_source_rows_snapshot_idx` (`snapshot_id`).
- `catalog_source_rows_outcome_idx` (`outcome`).

Policies: none. Triggers: `catalog_source_rows_immutable` (BEFORE UPDATE OR DELETE, row) and `catalog_source_rows_no_truncate` (BEFORE TRUNCATE, statement), both `reject_catalog_archive_mutation()`.
Sequence: `catalog_source_rows_id_seq`, owned by `id`, last value 154.

### `public.catalog_issues`

| Column | Type | Null | Default / identity |
| --- | --- | --- | --- |
| `id` | `bigint` | no | identity always, start 1, increment 1 |
| `batch_id` | `bigint` | no | none |
| `snapshot_id` | `bigint` | no | none |
| `source_row_id` | `bigint` | yes | none |
| `json_pointer` | `text` | no | none |
| `issue_code` | `text` | no | none |
| `severity` | `text` | no | `'error'::text` |
| `message` | `text` | no | none |
| `status` | `text` | no | `'open'::text` |
| `created_at` | `timestamptz` | no | `now()` |

Constraints:

- `catalog_issues_pkey` primary key (`id`).
- `catalog_issues_batch_id_fkey` foreign key (`batch_id`) references `catalog_import_batches(id)`.
- `catalog_issues_snapshot_id_fkey` foreign key (`snapshot_id`) references `catalog_source_snapshots(id)`.
- `catalog_issues_source_row_id_fkey` foreign key (`source_row_id`) references `catalog_source_rows(id)`.
- `catalog_issues_json_pointer_check` check (`json_pointer = '' or json_pointer like '/%'`).
- `catalog_issues_issue_code_check` check (`btrim(issue_code) <> ''`).
- `catalog_issues_severity_check` check (`severity in ('warning', 'error')`).
- `catalog_issues_message_check` check (`btrim(message) <> ''`).
- `catalog_issues_status_check` check (`status in ('open', 'resolved', 'quarantined')`).

Indexes:

- `catalog_issues_pkey` unique (`id`).
- `catalog_issues_source_key` unique (`batch_id`, `snapshot_id`, `coalesce(source_row_id, 0)`, `json_pointer`, `issue_code`).
- `catalog_issues_snapshot_idx` (`snapshot_id`).
- `catalog_issues_status_idx` (`status`).

Policies: none. Triggers: none.
Sequence: `catalog_issues_id_seq`, owned by `id`, last value 34.

### `public.catalog_repairs`

| Column | Type | Null | Default / identity |
| --- | --- | --- | --- |
| `id` | `bigint` | no | identity always, start 1, increment 1 |
| `batch_id` | `bigint` | no | none |
| `snapshot_id` | `bigint` | no | none |
| `source_row_id` | `bigint` | yes | none |
| `json_pointer` | `text` | no | none |
| `before_value` | `jsonb` | yes | none |
| `after_value` | `jsonb` | yes | none |
| `source_url` | `text` | no | none |
| `source_title` | `text` | yes | none |
| `accessed_on` | `date` | no | none |
| `academic_year` | `text` | yes | none |
| `evidence` | `text` | no | none |
| `status` | `text` | no | `'verified'::text` |
| `created_at` | `timestamptz` | no | `now()` |

Constraints:

- `catalog_repairs_pkey` primary key (`id`).
- `catalog_repairs_batch_id_fkey` foreign key (`batch_id`) references `catalog_import_batches(id)`.
- `catalog_repairs_snapshot_id_fkey` foreign key (`snapshot_id`) references `catalog_source_snapshots(id)`.
- `catalog_repairs_source_row_id_fkey` foreign key (`source_row_id`) references `catalog_source_rows(id)`.
- `catalog_repairs_json_pointer_check` check (`json_pointer = '' or json_pointer like '/%'`).
- `catalog_repairs_source_url_check` check (`source_url ~ '^https?://\S+$'`).
- `catalog_repairs_source_title_check` check (`source_title is null or btrim(source_title) <> ''`).
- `catalog_repairs_academic_year_check` check (`academic_year is null or btrim(academic_year) <> ''`).
- `catalog_repairs_evidence_check` check (`btrim(evidence) <> ''`).
- `catalog_repairs_status_check` check (`status in ('verified', 'unresolved')`).

Indexes:

- `catalog_repairs_pkey` unique (`id`).
- `catalog_repairs_source_key` unique (`batch_id`, `snapshot_id`, `coalesce(source_row_id, 0)`, `json_pointer`, `source_url`).
- `catalog_repairs_snapshot_idx` (`snapshot_id`).
- `catalog_repairs_source_row_idx` (`source_row_id`).

Policies: none. Triggers: none.
Sequence: `catalog_repairs_id_seq`, owned by `id`, last value 44.

## Retained core tables

### `public.degrees`

| Column | Type | Null | Default / identity |
| --- | --- | --- | --- |
| `id` | `bigint` | no | identity always, start 1, increment 1 |
| `name` | `text` | no | none |
| `faculty` | `text` | no | none |
| `full_title` | `text` | yes | none |
| `source_order` | `integer` | yes | none |

Constraints:

- `degrees_pkey` primary key (`id`).
- `degrees_name_key` unique (`name`).
- `degrees_name_check` check (`btrim(name) <> ''`).
- `degrees_faculty_check` check (`btrim(faculty) <> ''`).
- `degrees_full_title_check` check (`full_title is null or btrim(full_title) <> ''`).
- `degrees_source_order_check` check (`source_order is null or source_order >= 0`).

Indexes:

- `degrees_pkey` unique (`id`).
- `degrees_name_key` unique (`name`).
- `degrees_source_order_key` unique (`source_order`) where `source_order is not null`.

Policy: `catalog_reader_select_degrees`, SELECT to `catalog_reader`, `using (true)`.
Sequence: `degrees_id_seq`, owned by `id`, last value 6.

### `public.nus_modules`

| Column | Type | Null | Default / identity |
| --- | --- | --- | --- |
| `code` | `text` | no | none |
| `name` | `text` | yes | none |
| `offering_faculty` | `text` | yes | none |
| `verified_units` | `numeric(8,2)` | yes | none |

Constraints:

- `nus_modules_pkey` primary key (`code`).
- `nus_modules_code_check` check (`btrim(code) <> '' and code = upper(btrim(code))`).
- `nus_modules_name_check` check (`btrim(name) <> ''`).
- `nus_modules_verified_units_check` check (`verified_units is null or verified_units > 0`).

Indexes: `nus_modules_pkey` unique (`code`).
Policy: `catalog_reader_select_nus_modules`, SELECT to `catalog_reader`, `using (true)`.
Sequence: none (text primary key).

### `public.degree_modules`

| Column | Type | Null | Default / identity |
| --- | --- | --- | --- |
| `degree_id` | `bigint` | no | none |
| `module_code` | `text` | no | none |
| `requirement_type` | `text` | yes | none |

Constraints:

- `degree_modules_pkey` primary key (`degree_id`, `module_code`).
- `degree_modules_degree_id_fkey` foreign key (`degree_id`) references `degrees(id)`.
- `degree_modules_module_code_fkey` foreign key (`module_code`) references `nus_modules(code)`.
- `degree_modules_requirement_type_check` check (`requirement_type is null or btrim(requirement_type) <> ''`).

Indexes:

- `degree_modules_pkey` unique (`degree_id`, `module_code`).
- `degree_modules_module_code_idx` (`module_code`).

Policy: `catalog_reader_select_degree_modules`, SELECT to `catalog_reader`, `using (true)`.
Sequence: none.

### `public.specializations`

| Column | Type | Null | Default / identity |
| --- | --- | --- | --- |
| `id` | `bigint` | no | identity always, start 1, increment 1 |
| `degree_id` | `bigint` | no | none |
| `name` | `text` | no | none |
| `kind` | `text` | no | `'specialization'::text` |
| `source_order` | `integer` | yes | none |

Constraints:

- `specializations_pkey` primary key (`id`).
- `specializations_degree_id_name_key` unique (`degree_id`, `name`).
- `specializations_degree_id_fkey` foreign key (`degree_id`) references `degrees(id)`.
- `specializations_name_check` check (`btrim(name) <> ''`).
- `specializations_kind_check` check (`kind in ('specialization', 'focus_area')`).
- `specializations_source_order_check` check (`source_order is null or source_order >= 0`).

Indexes:

- `specializations_pkey` unique (`id`).
- `specializations_degree_id_name_key` unique (`degree_id`, `name`).
- `specializations_degree_source_order_key` unique (`degree_id`, `source_order`) where `source_order is not null`.

Policy: `catalog_reader_select_specializations`, SELECT to `catalog_reader`, `using (true)`.
Sequence: `specializations_id_seq`, owned by `id`, last value 19.

### `public.specialization_modules`

| Column | Type | Null | Default / identity |
| --- | --- | --- | --- |
| `specialization_id` | `bigint` | no | none |
| `module_code` | `text` | no | none |

Constraints:

- `specialization_modules_pkey` primary key (`specialization_id`, `module_code`).
- `specialization_modules_specialization_id_fkey` foreign key (`specialization_id`) references `specializations(id)`.
- `specialization_modules_module_code_fkey` foreign key (`module_code`) references `nus_modules(code)`.

Indexes:

- `specialization_modules_pkey` unique (`specialization_id`, `module_code`).
- `specialization_modules_module_code_idx` (`module_code`).

Policy: `catalog_reader_select_specialization_modules`, SELECT to `catalog_reader`, `using (true)`.
Sequence: none.

### `public.partner_universities`

| Column | Type | Null | Default / identity |
| --- | --- | --- | --- |
| `id` | `bigint` | no | identity always, start 1, increment 1 |
| `name` | `text` | no | none |
| `country` | `text` | no | none |
| `city` | `text` | yes | none |
| `continent` | `text` | yes | none |
| `source_order` | `integer` | yes | none |

Constraints:

- `partner_universities_pkey` primary key (`id`).
- `partner_universities_name_key` unique (`name`).
- `partner_universities_name_check` check (`btrim(name) <> ''`).
- `partner_universities_country_check` check (`btrim(country) <> ''`).
- `partner_universities_source_order_check` check (`source_order is null or source_order >= 0`).

Indexes:

- `partner_universities_pkey` unique (`id`).
- `partner_universities_name_key` unique (`name`).
- `partner_universities_source_order_key` unique (`source_order`) where `source_order is not null`.

Policy: `catalog_reader_select_partner_universities`, SELECT to `catalog_reader`, `using (true)`.
Sequence: `partner_universities_id_seq`, owned by `id`, last value 5.

### `public.pu_modules`

| Column | Type | Null | Default / identity |
| --- | --- | --- | --- |
| `id` | `bigint` | no | identity always, start 1, increment 1 |
| `code` | `text` | no | none |
| `name` | `text` | yes | none |
| `partner_university_id` | `bigint` | no | none |
| `verified_units` | `numeric(8,2)` | yes | none |

Constraints:

- `pu_modules_pkey` primary key (`id`).
- `pu_modules_partner_university_id_code_key` unique (`partner_university_id`, `code`).
- `pu_modules_partner_university_id_fkey` foreign key (`partner_university_id`) references `partner_universities(id)`.
- `pu_modules_code_check` check (`btrim(code) <> '' and code = upper(btrim(code))`).
- `pu_modules_name_check` check (`btrim(name) <> ''`).
- `pu_modules_verified_units_check` check (`verified_units is null or verified_units > 0`).

Indexes:

- `pu_modules_pkey` unique (`id`).
- `pu_modules_partner_university_id_code_key` unique (`partner_university_id`, `code`).

Policy: `catalog_reader_select_pu_modules`, SELECT to `catalog_reader`, `using (true)`.
Sequence: `pu_modules_id_seq`, owned by `id`, last value 142.

### `public.module_mappings`

| Column | Type | Null | Default / identity |
| --- | --- | --- | --- |
| `id` | `bigint` | no | identity always, start 1, increment 1 |
| `nus_module_code` | `text` | no | none |
| `pu_module_id` | `bigint` | no | none |
| `source_row_id` | `bigint` | yes | removal target |
| `source_order` | `integer` | yes | none |
| `source_nus_title` | `text` | yes | none |
| `source_nus_units` | `numeric(8,2)` | yes | none |
| `source_partner_title` | `text` | yes | none |
| `source_partner_units` | `numeric(8,2)` | yes | none |
| `source_faculty` | `text` | yes | none |
| `source_page` | `integer` | yes | none |

Constraints:

- `module_mappings_pkey` primary key (`id`).
- `module_mappings_source_row_id_key` unique (`source_row_id`) — removal target.
- `module_mappings_nus_module_code_fkey` foreign key (`nus_module_code`) references `nus_modules(code)`.
- `module_mappings_pu_module_id_fkey` foreign key (`pu_module_id`) references `pu_modules(id)`.
- `module_mappings_source_row_id_fkey` foreign key (`source_row_id`) references `catalog_source_rows(id)` — removal target.
- `module_mappings_source_order_check` check (`source_order is null or source_order >= 0`).
- `module_mappings_source_nus_title_check` check (`source_nus_title is null or btrim(source_nus_title) <> ''`).
- `module_mappings_source_nus_units_check` check (`source_nus_units is null or source_nus_units > 0`).
- `module_mappings_source_partner_title_check` check (`source_partner_title is null or btrim(source_partner_title) <> ''`).
- `module_mappings_source_partner_units_check` check (`source_partner_units is null or source_partner_units > 0`).
- `module_mappings_source_faculty_check` check (`source_faculty is null or btrim(source_faculty) <> ''`).
- `module_mappings_source_page_check` check (`source_page is null or source_page > 0`).

Indexes:

- `module_mappings_pkey` unique (`id`).
- `module_mappings_source_row_id_key` unique (`source_row_id`) — removal target.
- `module_mappings_nus_module_code_idx` (`nus_module_code`).
- `module_mappings_pu_module_id_idx` (`pu_module_id`).
- `module_mappings_nus_code_source_order_idx` (`nus_module_code`, `source_order`).

Policy: `catalog_reader_select_module_mappings`, SELECT to `catalog_reader`, `using (true)`.
Sequence: `module_mappings_id_seq`, owned by `id`, last value 151.

## Roles and privileges

### Runtime role

| Attribute | `catalog_reader` |
| --- | --- |
| Login | yes |
| Superuser | no |
| Create role / database | no / no |
| Replication | no |
| Bypass RLS | no |
| Connection limit | -1 |
| Role settings | `statement_timeout=5s`, `idle_in_transaction_session_timeout=5s`, `default_transaction_read_only=on` |

`catalog_importer` does not exist in the production database.

### Schema privilege

`catalog_reader` has `USAGE` on `public` and no `CREATE`.

### Table privileges for `catalog_reader`

`SELECT` only on the eight core tables and `catalog_import_batches`. It has no
table privilege on `catalog_source_snapshots`, `catalog_source_rows`,
`catalog_issues`, or `catalog_repairs`. These table-level grants surface as 55
column-level SELECT grants (5 + 4 + 3 + 5 + 2 + 6 + 5 + 11 + 14 columns).

### Other role grants

Supabase default grants give `anon`, `authenticated`, and `service_role` broad
table privileges (`DELETE`, `INSERT`, `REFERENCES`, `SELECT`, `TRIGGER`,
`TRUNCATE`, `UPDATE`) on all thirteen tables and `USAGE` on all ten sequences.
`anon` and `authenticated` have no SELECT policies, so row-level security
returns no application rows to browser roles. `service_role` bypasses RLS.
These broad grants are pre-existing platform defaults, not part of this change.

## Functions, triggers, and sequences

### Functions

| Function | Owner | Security definer | Arguments | Returns | ACL |
| --- | --- | --- | --- | --- | --- |
| `public.reject_catalog_archive_mutation()` | `postgres` | no | none | trigger | `EXECUTE` to PUBLIC, `anon`, `authenticated`, `postgres`, `service_role` |

Function body:

```sql
begin
  raise exception 'catalog archive rows are immutable';
end;
```

The function has four dependent triggers (`pg_trigger` OIDs 17963-17966), all
listed above. It has no table, view, or routine dependency of its own.

`public.rls_auto_enable()` is a Supabase-managed event-trigger function used by
the `ensure_rls` event trigger. It is not application-owned and is outside the
removal scope.

### Triggers

| Table | Trigger | Timing / event | Function | Enabled |
| --- | --- | --- | --- | --- |
| `catalog_source_snapshots` | `catalog_source_snapshots_immutable` | BEFORE UPDATE OR DELETE, row | `reject_catalog_archive_mutation` | yes |
| `catalog_source_snapshots` | `catalog_source_snapshots_no_truncate` | BEFORE TRUNCATE, statement | `reject_catalog_archive_mutation` | yes |
| `catalog_source_rows` | `catalog_source_rows_immutable` | BEFORE UPDATE OR DELETE, row | `reject_catalog_archive_mutation` | yes |
| `catalog_source_rows` | `catalog_source_rows_no_truncate` | BEFORE TRUNCATE, statement | `reject_catalog_archive_mutation` | yes |

No core table has a user-defined trigger.

### Sequences

| Sequence | Owned by | Last value | Start | Increment | Min / max | Cycle |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `catalog_import_batches_id_seq` | `catalog_import_batches.id` | 1 | 1 | 1 | 1 / 9223372036854775807 | no |
| `catalog_source_snapshots_id_seq` | `catalog_source_snapshots.id` | 8 | 1 | 1 | 1 / 9223372036854775807 | no |
| `catalog_source_rows_id_seq` | `catalog_source_rows.id` | 154 | 1 | 1 | 1 / 9223372036854775807 | no |
| `catalog_issues_id_seq` | `catalog_issues.id` | 34 | 1 | 1 | 1 / 9223372036854775807 | no |
| `catalog_repairs_id_seq` | `catalog_repairs.id` | 44 | 1 | 1 | 1 / 9223372036854775807 | no |
| `degrees_id_seq` | `degrees.id` | 6 | 1 | 1 | 1 / 9223372036854775807 | no |
| `module_mappings_id_seq` | `module_mappings.id` | 151 | 1 | 1 | 1 / 9223372036854775807 | no |
| `partner_universities_id_seq` | `partner_universities.id` | 5 | 1 | 1 | 1 / 9223372036854775807 | no |
| `pu_modules_id_seq` | `pu_modules.id` | 142 | 1 | 1 | 1 / 9223372036854775807 | no |
| `specializations_id_seq` | `specializations.id` | 19 | 1 | 1 | 1 / 9223372036854775807 | no |

All sequences are `public`, owned by their table identity column, and removed
automatically with their owning table.

## Inbound dependencies

### Foreign keys into removal targets

| Referencing table | Constraint | References |
| --- | --- | --- |
| `catalog_source_snapshots` | `catalog_source_snapshots_batch_id_fkey` | `catalog_import_batches(id)` |
| `catalog_source_rows` | `catalog_source_rows_snapshot_id_fkey` | `catalog_source_snapshots(id)` |
| `catalog_issues` | `catalog_issues_batch_id_fkey` | `catalog_import_batches(id)` |
| `catalog_issues` | `catalog_issues_snapshot_id_fkey` | `catalog_source_snapshots(id)` |
| `catalog_issues` | `catalog_issues_source_row_id_fkey` | `catalog_source_rows(id)` |
| `catalog_repairs` | `catalog_repairs_batch_id_fkey` | `catalog_import_batches(id)` |
| `catalog_repairs` | `catalog_repairs_snapshot_id_fkey` | `catalog_source_snapshots(id)` |
| `catalog_repairs` | `catalog_repairs_source_row_id_fkey` | `catalog_source_rows(id)` |
| `module_mappings` | `module_mappings_source_row_id_fkey` | `catalog_source_rows(id)` |

All foreign keys are in `public` with default (immediate, not deferrable)
semantics. No foreign key from another schema references a target table.

### Removed core column: `module_mappings.source_row_id`

| Fact | Value |
| --- | --- |
| Type / nullability | `bigint`, nullable |
| Foreign key | `module_mappings_source_row_id_fkey` → `catalog_source_rows(id)` |
| Unique key | `module_mappings_source_row_id_key` |
| Rows with a value | 151 of 151 |
| Null values | 0 |
| Duplicate values | 0 |

The unique key is required because each source row maps to at most one accepted
mapping occurrence while repeated course pairs remain independent. Dropping the
column removes both dependent constraints and no mapping row.

### Other dependency classes

`pg_depend` reports 82 normal dependencies from `pg_constraint` on the thirteen
tables. They comprise the primary, unique, foreign-key, and check constraints
listed above. There are:

- No views, materialized views, or rules depending on a target table.
- No functions (other than the four archive triggers) depending on a target table.
- No defaults, generated columns, or publications depending on a target table.
- No partition or inheritance relationships.
- No triggers on the eight core tables.
- No foreign keys outside `public`.
- No application-owned objects matching `catalog%` outside `public`.

## Objects outside `public`

| Schema | Relations | Relevance |
| --- | --- | --- |
| `auth` | 27 | Supabase-managed; no target references |
| `extensions` | 2 | Supabase-managed; no target references |
| `realtime` | 3 | Supabase-managed; no target references |
| `storage` | 8 | Supabase-managed; no target references |
| `supabase_migrations` | 1 | Migration history only |
| `vault` | 2 | Supabase-managed; no target references |

No unexpected application-owned table, view, or foreign key references the
thirteen tables. Dropping only the five named tables and
`module_mappings.source_row_id` will not remove a Supabase-managed object.

## Comparison with checked-in migrations

The live schema matches the three applied migration files for all application
objects and constraints. Two live details come from deployment/platform activity
rather than the checked-in DDL and are retained:

- `catalog_reader` has `LOGIN` enabled and the documented role timeouts. Migration
  `20261022000300` created it `NOLOGIN` and provisioned accesses; credentials and
  login were applied outside migrations.
- `anon`, `authenticated`, and `service_role` hold Supabase default broad grants.
  They are not used by the backend and grant no browser row access while RLS
  policies remain absent.

No unexpected object was found, so T006 does not stop destructive work. The
production boundary recheck (T034/T036) must repeat the dependency and target
comparison because this document describes the state at capture time only.

## Evidence provenance

- Read-only queries were executed through the configured Supabase MCP connection
  on 2026-10-23 (Asia/Singapore).
- Row counts, sizes, and sequence values are point-in-time observations.
- No connection string, password, API key, or full database URL is recorded here.
- The private export created in T035 must supersede these counts for recovery.
