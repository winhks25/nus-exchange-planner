-- Least-privilege runtime access for the catalog API.
-- The role is created without login; provision its password outside migrations.
-- Browser roles receive no policies and therefore no readable catalog rows.

begin;

-- Create the dedicated runtime role with safe attributes in one statement.
-- Hosted projects run migrations as a CREATEROLE owner, not a superuser, so we
-- must not ALTER superuser/BYPASSRLS attributes after creation.
do $$
declare
  existing_role record;
begin
  select rolsuper, rolbypassrls into existing_role
  from pg_roles
  where rolname = 'catalog_reader';

  if not found then
    create role catalog_reader
      nologin
      nosuperuser
      nocreatedb
      nocreaterole
      noreplication
      nobypassrls;
  elsif existing_role.rolsuper or existing_role.rolbypassrls then
    raise exception 'catalog_reader must not have SUPERUSER or BYPASSRLS';
  end if;
end
$$;

-- Bound runtime sessions even if a caller forgets the pool-level settings.
alter role catalog_reader set statement_timeout = '5s';
alter role catalog_reader set idle_in_transaction_session_timeout = '5s';
alter role catalog_reader set default_transaction_read_only = on;

-- Remove any previous grants before granting only the required read surface.
revoke all on schema public from catalog_reader;
grant usage on schema public to catalog_reader;

revoke all on all tables in schema public from catalog_reader;
revoke all on all sequences in schema public from catalog_reader;
revoke all on all functions in schema public from catalog_reader;

grant select on table
  public.degrees,
  public.nus_modules,
  public.degree_modules,
  public.specializations,
  public.specialization_modules,
  public.partner_universities,
  public.pu_modules,
  public.module_mappings,
  public.catalog_import_batches
to catalog_reader;

-- SELECT policies are required because the reader is not a table owner or BYPASSRLS.
drop policy if exists catalog_reader_select_degrees on public.degrees;
create policy catalog_reader_select_degrees on public.degrees
  for select to catalog_reader using (true);

drop policy if exists catalog_reader_select_nus_modules on public.nus_modules;
create policy catalog_reader_select_nus_modules on public.nus_modules
  for select to catalog_reader using (true);

drop policy if exists catalog_reader_select_degree_modules on public.degree_modules;
create policy catalog_reader_select_degree_modules on public.degree_modules
  for select to catalog_reader using (true);

drop policy if exists catalog_reader_select_specializations on public.specializations;
create policy catalog_reader_select_specializations on public.specializations
  for select to catalog_reader using (true);

drop policy if exists catalog_reader_select_specialization_modules
  on public.specialization_modules;
create policy catalog_reader_select_specialization_modules
  on public.specialization_modules
  for select to catalog_reader using (true);

drop policy if exists catalog_reader_select_partner_universities
  on public.partner_universities;
create policy catalog_reader_select_partner_universities
  on public.partner_universities
  for select to catalog_reader using (true);

drop policy if exists catalog_reader_select_pu_modules on public.pu_modules;
create policy catalog_reader_select_pu_modules on public.pu_modules
  for select to catalog_reader using (true);

drop policy if exists catalog_reader_select_module_mappings on public.module_mappings;
create policy catalog_reader_select_module_mappings on public.module_mappings
  for select to catalog_reader using (true);

drop policy if exists catalog_reader_select_import_batches
  on public.catalog_import_batches;
create policy catalog_reader_select_import_batches
  on public.catalog_import_batches
  for select to catalog_reader using (true);

comment on role catalog_reader is
  'Read-only runtime role for the catalog API; no raw archive or issue access.';

commit;
