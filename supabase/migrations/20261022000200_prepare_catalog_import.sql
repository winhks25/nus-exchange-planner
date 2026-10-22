-- Additive schema support for a traceable, repeatable catalog import.
-- The initial catalog tables keep their existing meaning; this migration only
-- adds source metadata, import bookkeeping, and row-specific presentation.

begin;

-- Degrees gain the full published title and their order in the source file.
alter table public.degrees
  add column full_title text,
  add column source_order integer;

alter table public.degrees
  add constraint degrees_full_title_check
    check (full_title is null or btrim(full_title) <> ''),
  add constraint degrees_source_order_check
    check (source_order is null or source_order >= 0);

create unique index degrees_source_order_key
  on public.degrees (source_order)
  where source_order is not null;

-- Module names may be unknown, so a missing title stays null instead of being invented.
alter table public.nus_modules
  alter column name drop not null,
  add column verified_units numeric(8, 2);

alter table public.nus_modules
  add constraint nus_modules_verified_units_check
    check (verified_units is null or verified_units > 0);

alter table public.pu_modules
  alter column name drop not null,
  add column verified_units numeric(8, 2);

alter table public.pu_modules
  add constraint pu_modules_verified_units_check
    check (verified_units is null or verified_units > 0);

-- Specializations and CS focus areas share a table but keep their source kind.
alter table public.specializations
  add column kind text not null default 'specialization',
  add column source_order integer;

alter table public.specializations
  add constraint specializations_kind_check
    check (kind in ('specialization', 'focus_area')),
  add constraint specializations_source_order_check
    check (source_order is null or source_order >= 0);

create unique index specializations_degree_source_order_key
  on public.specializations (degree_id, source_order)
  where source_order is not null;

-- Partner ordering preserves the source catalog's university sequence.
alter table public.partner_universities
  add column source_order integer;

alter table public.partner_universities
  add constraint partner_universities_source_order_check
    check (source_order is null or source_order >= 0);

create unique index partner_universities_source_order_key
  on public.partner_universities (source_order)
  where source_order is not null;

-- Import batches identify one published source+repair snapshot.
create table public.catalog_import_batches (
  id bigint generated always as identity primary key,
  source_checksum char(64) not null
    check (source_checksum ~ '^[0-9a-f]{64}$'),
  repair_checksum char(64) not null
    check (repair_checksum ~ '^[0-9a-f]{64}$'),
  status text not null default 'running'
    check (status in ('running', 'completed', 'failed')),
  is_current boolean not null default false,
  source_manifest jsonb not null default '{}'::jsonb
    check (jsonb_typeof(source_manifest) = 'object'),
  source_file_count integer not null default 0 check (source_file_count >= 0),
  raw_row_count integer not null default 0 check (raw_row_count >= 0),
  accepted_row_count integer not null default 0 check (accepted_row_count >= 0),
  repaired_row_count integer not null default 0 check (repaired_row_count >= 0),
  quarantined_row_count integer not null default 0 check (quarantined_row_count >= 0),
  started_at timestamptz not null default now(),
  completed_at timestamptz,
  note text check (note is null or btrim(note) <> ''),
  constraint catalog_import_batches_current_completed_check
    check (not is_current or status = 'completed'),
  constraint catalog_import_batches_completed_at_check
    check ((status = 'completed') = (completed_at is not null))
);

-- A matching source+repair snapshot can only publish once; only one batch is current.
create unique index catalog_import_batches_completed_key
  on public.catalog_import_batches (source_checksum, repair_checksum)
  where status = 'completed';

create unique index catalog_import_batches_current_key
  on public.catalog_import_batches (is_current)
  where is_current;

-- Immutable snapshots keep the exact source text and its parsed form.
create table public.catalog_source_snapshots (
  id bigint generated always as identity primary key,
  batch_id bigint not null
    references public.catalog_import_batches (id),
  file_path text not null check (btrim(file_path) <> ''),
  source_kind text not null
    check (source_kind in ('majors', 'mapping', 'repairs', 'manifest')),
  raw_text text not null check (length(raw_text) > 0),
  parsed_json jsonb not null,
  sha256 char(64) not null check (sha256 ~ '^[0-9a-f]{64}$'),
  byte_size bigint not null check (byte_size >= 0),
  archived_at timestamptz not null default now(),
  unique (batch_id, file_path)
);

create index catalog_source_snapshots_batch_idx
  on public.catalog_source_snapshots (batch_id);

-- Every raw mapping row keeps its source position and flattened presentation.
create table public.catalog_source_rows (
  id bigint generated always as identity primary key,
  snapshot_id bigint not null
    references public.catalog_source_snapshots (id),
  mapping_index integer not null check (mapping_index >= 0),
  raw_json jsonb not null check (jsonb_typeof(raw_json) = 'object'),
  source_nus_code text not null check (btrim(source_nus_code) <> ''),
  source_partner_code text not null check (btrim(source_partner_code) <> ''),
  source_nus_title text
    check (source_nus_title is null or btrim(source_nus_title) <> ''),
  source_partner_title text
    check (source_partner_title is null or btrim(source_partner_title) <> ''),
  source_nus_units numeric(8, 2)
    check (source_nus_units is null or source_nus_units > 0),
  source_partner_units numeric(8, 2)
    check (source_partner_units is null or source_partner_units > 0),
  source_faculty text
    check (source_faculty is null or btrim(source_faculty) <> ''),
  source_page integer check (source_page is null or source_page > 0),
  outcome text not null default 'accepted'
    check (outcome in ('accepted', 'repaired', 'quarantined')),
  created_at timestamptz not null default now(),
  unique (snapshot_id, mapping_index)
);

create index catalog_source_rows_snapshot_idx
  on public.catalog_source_rows (snapshot_id);

create index catalog_source_rows_outcome_idx
  on public.catalog_source_rows (outcome);

-- Source-addressed issues explain every raw row that is not a normal mapping.
create table public.catalog_issues (
  id bigint generated always as identity primary key,
  batch_id bigint not null
    references public.catalog_import_batches (id),
  snapshot_id bigint not null
    references public.catalog_source_snapshots (id),
  source_row_id bigint
    references public.catalog_source_rows (id),
  json_pointer text not null
    check (json_pointer = '' or json_pointer like '/%'),
  issue_code text not null check (btrim(issue_code) <> ''),
  severity text not null default 'error'
    check (severity in ('warning', 'error')),
  message text not null check (btrim(message) <> ''),
  status text not null default 'open'
    check (status in ('open', 'resolved', 'quarantined')),
  created_at timestamptz not null default now()
);

create unique index catalog_issues_source_key
  on public.catalog_issues (
    batch_id,
    snapshot_id,
    coalesce(source_row_id, 0),
    json_pointer,
    issue_code
  );

create index catalog_issues_snapshot_idx
  on public.catalog_issues (snapshot_id);

create index catalog_issues_status_idx
  on public.catalog_issues (status);

-- Repairs cite official evidence and retain their before/after values.
create table public.catalog_repairs (
  id bigint generated always as identity primary key,
  batch_id bigint not null
    references public.catalog_import_batches (id),
  snapshot_id bigint not null
    references public.catalog_source_snapshots (id),
  source_row_id bigint
    references public.catalog_source_rows (id),
  json_pointer text not null
    check (json_pointer = '' or json_pointer like '/%'),
  before_value jsonb,
  after_value jsonb,
  source_url text not null check (source_url ~ '^https?://\S+$'),
  source_title text
    check (source_title is null or btrim(source_title) <> ''),
  accessed_on date not null,
  academic_year text
    check (academic_year is null or btrim(academic_year) <> ''),
  evidence text not null check (btrim(evidence) <> ''),
  status text not null default 'verified'
    check (status in ('verified', 'unresolved')),
  created_at timestamptz not null default now()
);

create unique index catalog_repairs_source_key
  on public.catalog_repairs (
    batch_id,
    snapshot_id,
    coalesce(source_row_id, 0),
    json_pointer,
    source_url
  );

create index catalog_repairs_snapshot_idx
  on public.catalog_repairs (snapshot_id);

create index catalog_repairs_source_row_idx
  on public.catalog_repairs (source_row_id);

-- Accepted mappings link to their source row and keep row-level presentation.
alter table public.module_mappings
  add column source_row_id bigint,
  add column source_order integer,
  add column source_nus_title text,
  add column source_nus_units numeric(8, 2),
  add column source_partner_title text,
  add column source_partner_units numeric(8, 2),
  add column source_faculty text,
  add column source_page integer;

alter table public.module_mappings
  add constraint module_mappings_source_row_id_key unique (source_row_id),
  add constraint module_mappings_source_row_id_fkey
    foreign key (source_row_id) references public.catalog_source_rows (id),
  add constraint module_mappings_source_order_check
    check (source_order is null or source_order >= 0),
  add constraint module_mappings_source_nus_title_check
    check (source_nus_title is null or btrim(source_nus_title) <> ''),
  add constraint module_mappings_source_nus_units_check
    check (source_nus_units is null or source_nus_units > 0),
  add constraint module_mappings_source_partner_title_check
    check (source_partner_title is null or btrim(source_partner_title) <> ''),
  add constraint module_mappings_source_partner_units_check
    check (source_partner_units is null or source_partner_units > 0),
  add constraint module_mappings_source_faculty_check
    check (source_faculty is null or btrim(source_faculty) <> ''),
  add constraint module_mappings_source_page_check
    check (source_page is null or source_page > 0);

create index module_mappings_nus_code_source_order_idx
  on public.module_mappings (nus_module_code, source_order);

-- Archive rows are append-only so source evidence cannot be rewritten.
create function public.reject_catalog_archive_mutation()
returns trigger
language plpgsql
as $$
begin
  raise exception 'catalog archive rows are immutable';
end;
$$;

create trigger catalog_source_snapshots_immutable
  before update or delete on public.catalog_source_snapshots
  for each row execute function public.reject_catalog_archive_mutation();

create trigger catalog_source_snapshots_no_truncate
  before truncate on public.catalog_source_snapshots
  for each statement execute function public.reject_catalog_archive_mutation();

create trigger catalog_source_rows_immutable
  before update or delete on public.catalog_source_rows
  for each row execute function public.reject_catalog_archive_mutation();

create trigger catalog_source_rows_no_truncate
  before truncate on public.catalog_source_rows
  for each statement execute function public.reject_catalog_archive_mutation();

-- New tables stay backend-only; T008 grants the runtime role explicit SELECT access.
alter table public.catalog_import_batches enable row level security;
alter table public.catalog_source_snapshots enable row level security;
alter table public.catalog_source_rows enable row level security;
alter table public.catalog_issues enable row level security;
alter table public.catalog_repairs enable row level security;

comment on table public.catalog_import_batches is
  'One attempted publication of a source snapshot and its repair set.';
comment on table public.catalog_source_snapshots is
  'Immutable exact text and parsed form of every archived source file.';
comment on table public.catalog_source_rows is
  'Immutable mapping rows addressed by snapshot and array index.';
comment on table public.catalog_issues is
  'Source-addressed data problems and their resolution state.';
comment on table public.catalog_repairs is
  'Source-addressed corrections with official evidence and before/after values.';
comment on column public.module_mappings.source_row_id is
  'Source row identity; unique so repeated course pairs at different indexes remain distinct.';
comment on column public.module_mappings.source_order is
  'Stable presentation order assigned from the source snapshot.';
comment on column public.specializations.kind is
  'Either a degree specialization or a CS focus area.';

commit;
