-- Initial catalog schema. Apply once to the intended Supabase project.
-- Transactional: conflicting existing tables abort instead of being overwritten.
begin;

create table public.degrees (
  id bigint generated always as identity primary key,
  name text not null unique check (btrim(name) <> ''),
  faculty text not null check (btrim(faculty) <> '')
);

create table public.nus_modules (
  code text primary key check (btrim(code) <> '' and code = upper(btrim(code))),
  name text not null check (btrim(name) <> ''),
  offering_faculty text
);

create table public.degree_modules (
  degree_id bigint not null references public.degrees(id),
  module_code text not null references public.nus_modules(code),
  requirement_type text check (requirement_type is null or btrim(requirement_type) <> ''),
  primary key (degree_id, module_code)
);

create table public.specializations (
  id bigint generated always as identity primary key,
  degree_id bigint not null references public.degrees(id),
  name text not null check (btrim(name) <> ''),
  unique (degree_id, name)
);

create table public.specialization_modules (
  specialization_id bigint not null references public.specializations(id),
  module_code text not null references public.nus_modules(code),
  primary key (specialization_id, module_code)
);

create table public.partner_universities (
  id bigint generated always as identity primary key,
  name text not null unique check (btrim(name) <> ''),
  country text not null check (btrim(country) <> ''),
  city text,
  continent text
);

create table public.pu_modules (
  id bigint generated always as identity primary key,
  code text not null check (btrim(code) <> '' and code = upper(btrim(code))),
  name text not null check (btrim(name) <> ''),
  partner_university_id bigint not null references public.partner_universities(id),
  unique (partner_university_id, code)
);

create table public.module_mappings (
  id bigint generated always as identity primary key,
  nus_module_code text not null references public.nus_modules(code),
  pu_module_id bigint not null references public.pu_modules(id)
);

-- Composite primary/unique keys already index their leading columns.
create index degree_modules_module_code_idx on public.degree_modules (module_code);
create index specialization_modules_module_code_idx on public.specialization_modules (module_code);
create index module_mappings_nus_module_code_idx on public.module_mappings (nus_module_code);
create index module_mappings_pu_module_id_idx on public.module_mappings (pu_module_id);

-- Backend-only access for now; no browser Data API policies are granted.
alter table public.degrees enable row level security;
alter table public.nus_modules enable row level security;
alter table public.degree_modules enable row level security;
alter table public.specializations enable row level security;
alter table public.specialization_modules enable row level security;
alter table public.partner_universities enable row level security;
alter table public.pu_modules enable row level security;
alter table public.module_mappings enable row level security;

commit;
