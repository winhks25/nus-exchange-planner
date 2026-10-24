-- Remove the catalog metadata (provenance/import) layer.
--
-- Scope: this migration unlinks module_mappings from the source archive
-- (T028) and then drops the five metadata tables and the archive-guard
-- function (T029). It MUST NOT touch any retained core column, index, row,
-- constraint, RLS policy, or grant on the eight core tables.
--
-- Safety: one explicit transaction, a bounded lock_timeout so a blocked drop
-- fails fast instead of waiting indefinitely, and plain DROP (RESTRICT is the
-- PostgreSQL default) so an unexpected dependency ABORTS the whole migration
-- rather than silently cascading. No wildcard drops, no CASCADE, no core-table
-- data rewrite, no migration-history repair.

begin;

-- Fail fast on a conflicting lock instead of blocking production writers.
set local lock_timeout = '5s';

-- T028 — explicit core unlink: drop the source_row_id foreign key, then its
-- unique key, then the column itself. Every other module_mappings column,
-- index (including module_mappings_nus_code_source_order_idx on source_order),
-- constraint, and row is preserved. No data is cleared and no new unique
-- constraint is added on (nus_module_code, pu_module_id).
alter table public.module_mappings
  drop constraint module_mappings_source_row_id_fkey;

alter table public.module_mappings
  drop constraint module_mappings_source_row_id_key;

alter table public.module_mappings
  drop column source_row_id;

-- T029 — metadata-table and archive-guard removal. Drop order follows the
-- foreign-key dependency graph so plain DROP (RESTRICT) succeeds without CASCADE:
-- the two leaf child tables first, then source_rows, then snapshots, then the
-- import_batches root. Each DROP TABLE removes that table's own triggers, RLS
-- policies, indexes, and owned sequences by ownership. The archive-guard
-- function is used only by triggers on catalog_source_snapshots and
-- catalog_source_rows, so it has no remaining dependents once those two tables
-- are dropped and is removed last.
drop table public.catalog_issues;
drop table public.catalog_repairs;
drop table public.catalog_source_rows;
drop table public.catalog_source_snapshots;
drop table public.catalog_import_batches;

drop function public.reject_catalog_archive_mutation();

commit;
