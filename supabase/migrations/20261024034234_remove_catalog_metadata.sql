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

-- T029 — metadata-table and archive-guard removal is appended here before
-- commit (child archive tables first, then parents, then the trigger
-- function once its dependencies are gone).

commit;
