-- Exchange enhancements: additive faculty and university metadata layer.
--
-- Scope: adds the public.faculties table and the public.degree_faculties and
-- public.faculty_partner_universities link tables, the nullable
-- public.nus_modules.faculty_id foreign key, and the nullable
-- public.partner_universities.image, website, and image_attribution columns.
-- No academic year or semester fields are modeled. Enables row level
-- security on the three new tables and grants the existing catalog_reader
-- role SELECT access through matching policies. Every existing column,
-- row, constraint, index, policy, and grant is preserved unchanged.
--
-- Safety: one explicit transaction and a bounded lock_timeout so a blocked
-- ALTER on a core table fails fast instead of waiting indefinitely. All new
-- objects are additive; the legacy text faculty columns stay in place until
-- their readers migrate (decisions.md, decisions 1 and 4).

begin;

-- Fail fast on a conflicting lock instead of waiting on production sessions.
set local lock_timeout = '5s';

-- Canonical faculty list. Names are trimmed, nonblank, and unique; the id is
-- the stable identity used by the catalog contract.
create table public.faculties (
  id bigint generated always as identity primary key,
  name text not null unique check (btrim(name) <> '')
);

-- Explicit degree membership. Membership is never derived from module
-- offerings; the pair is unique and both sides are foreign-key bound.
create table public.degree_faculties (
  degree_id bigint not null references public.degrees(id),
  faculty_id bigint not null references public.faculties(id),
  primary key (degree_id, faculty_id)
);

-- Explicit faculty-to-partner availability. A missing pair means unknown,
-- not unavailable; availability is never inferred from mapping existence.
create table public.faculty_partner_universities (
  faculty_id bigint not null references public.faculties(id),
  partner_university_id bigint not null references public.partner_universities(id),
  primary key (faculty_id, partner_university_id)
);

-- Additive faculty link on NUS modules. Nullable so unresolved legacy labels
-- stay null (decisions.md, decision 7); the legacy faculty text is retained.
alter table public.nus_modules
  add column faculty_id bigint references public.faculties(id);

-- Additive, reviewed-only university metadata. Null means unknown and blank
-- strings are rejected (decisions.md, decisions 5 and 10).
alter table public.partner_universities
  add column image text check (image is null or btrim(image) <> '');
alter table public.partner_universities
  add column website text check (website is null or btrim(website) <> '');
alter table public.partner_universities
  add column image_attribution text
  check (image_attribution is null or btrim(image_attribution) <> '');

-- Composite primary keys already index their leading columns; these cover the
-- reverse lookups (faculty -> degrees, partner -> faculties, faculty -> modules).
create index degree_faculties_faculty_id_idx on public.degree_faculties (faculty_id);
create index faculty_partner_universities_partner_university_id_idx
  on public.faculty_partner_universities (partner_university_id);
create index nus_modules_faculty_id_idx on public.nus_modules (faculty_id);

-- Backend-only access for the new tables, mirroring the core tables. Row
-- level security is enabled with no policy for the browser roles, so the
-- default-privilege grants held by anon and authenticated resolve to zero
-- rows and no writable surface (convention of
-- 20261022000100_create_exchange_catalog.sql and 20261022000300_catalog_reader.sql).
alter table public.faculties enable row level security;
alter table public.degree_faculties enable row level security;
alter table public.faculty_partner_universities enable row level security;

-- The runtime reader is least-privilege and not BYPASSRLS, so it needs an
-- explicit SELECT grant plus a matching SELECT policy on each new table.
grant select on table
  public.faculties,
  public.degree_faculties,
  public.faculty_partner_universities
to catalog_reader;

create policy catalog_reader_select_faculties on public.faculties
  for select to catalog_reader using (true);
create policy catalog_reader_select_degree_faculties on public.degree_faculties
  for select to catalog_reader using (true);
create policy catalog_reader_select_faculty_partner_universities
  on public.faculty_partner_universities
  for select to catalog_reader using (true);

commit;
