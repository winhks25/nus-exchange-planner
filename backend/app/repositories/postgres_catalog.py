"""Read-only repository adapter backed by the core PostgreSQL catalog tables."""

import logging

import psycopg

from ..database import CatalogDatabase, DatabaseError
from ..models import (
    CatalogResponse,
    Course,
    DegreeOption,
    FacultyOption,
    Mapping,
    MappingResponse,
    Recommendation,
    RecommendationsResponse,
    UniversityOption,
)
from ..settings import Settings
from .base import CATALOG_UNAVAILABLE_MESSAGE, CatalogUnavailable, UnknownSelection

LOG = logging.getLogger(__name__)

# Parameterless core-readiness check: a catalog is ready when it has at least one
# degree, at least one university, and no degree with a null full_title. It reads
# only core tables (no metadata relation) and takes no parameters, so it can run
# inside every read transaction without per-request schema introspection.
CORE_READINESS_SQL = """
select
  exists (select 1 from public.degrees) as has_degrees,
  exists (select 1 from public.partner_universities) as has_universities,
  exists (select 1 from public.degrees where full_title is null) as has_null_full_title
"""

# JSON field access supports both the archived fixture schema and the cleaned live schema.
# Missing legacy keys become NULL instead of producing UndefinedColumn errors.
CATALOG_DEGREES_SQL = """
select d.id, d.name, d.full_title
from public.degrees d
order by (to_jsonb(d)->>'source_order')::integer nulls last, d.id
"""

CATALOG_UNIVERSITIES_SQL = """
select u.id, u.name, u.country, u.city, u.continent, u.image, u.website, u.image_attribution
from public.partner_universities u
order by (to_jsonb(u)->>'source_order')::integer nulls last, u.id
"""

# Faculties have no source order; the contract fixes name then id.
CATALOG_FACULTIES_SQL = """
select id, name
from public.faculties
order by name collate "C", id
"""

# Membership queries fetch parent-ordered rows so Python grouping preserves the
# faculty name/id sort within each parent; no per-row round trips.
DEGREE_FACULTY_IDS_SQL = """
select df.degree_id, f.id
from public.degree_faculties df
join public.faculties f on f.id = df.faculty_id
order by df.degree_id, f.name collate "C", f.id
"""

UNIVERSITY_FACULTY_IDS_SQL = """
select fpu.partner_university_id, f.id
from public.faculty_partner_universities fpu
join public.faculties f on f.id = fpu.faculty_id
order by fpu.partner_university_id, f.name collate "C", f.id
"""

DEGREE_ID_SQL = """
select id
from public.degrees
where name = %s
"""

RANKINGS_SQL = """
select
  u.name,
  u.country,
  coalesce(ranked.mapping_count, 0),
  coalesce(ranked.distinct_nus_count, 0),
  coalesce(ranked.partner_count, 0)
from public.partner_universities u
left join (
  select
    pm.partner_university_id as university_id,
    count(*) as mapping_count,
    count(distinct mm.nus_module_code) as distinct_nus_count,
    count(distinct upper(pm.code)) as partner_count
  from public.module_mappings mm
  join public.pu_modules pm on pm.id = mm.pu_module_id
  join public.degree_modules dm on dm.module_code = mm.nus_module_code
  where dm.degree_id = %s
  group by pm.partner_university_id
) ranked on ranked.university_id = u.id
order by coalesce(ranked.distinct_nus_count, 0) desc, u.name collate "C" asc
"""

DEGREE_UNIVERSITY_IDS_SQL = """
select d.id, u.id
from public.degrees d
cross join public.partner_universities u
where d.name = %s and u.name = %s
"""

MAPPINGS_SQL = """
select
  mm.nus_module_code,
  coalesce(to_jsonb(mm)->>'source_nus_title', nm.name),
  pm.code,
  coalesce(to_jsonb(mm)->>'source_partner_title', pm.name),
  coalesce(
    (to_jsonb(mm)->>'source_partner_units')::numeric,
    (to_jsonb(pm)->>'pu_units')::numeric,
    (to_jsonb(pm)->>'verified_units')::numeric
  ),
  case when to_jsonb(nm) ? 'units' then (to_jsonb(nm)->>'units')::numeric
       else 4 end
from public.module_mappings mm
join public.nus_modules nm on nm.code = mm.nus_module_code
join public.pu_modules pm on pm.id = mm.pu_module_id
where pm.partner_university_id = %s
  and mm.nus_module_code in (
    select dm.module_code
    from public.degree_modules dm
    where dm.degree_id = %s
  )
order by mm.nus_module_code collate "C" asc, (to_jsonb(mm)->>'source_order')::integer nulls last, mm.id asc
"""


class PostgresCatalogRepository:
    """Serve catalog responses from the core tables when the catalog is ready."""

    def __init__(self, settings: Settings) -> None:
        self._database = CatalogDatabase(settings)

    def startup(self) -> None:
        """Start the bounded connection pool without opening a network connection."""

        try:
            self._database.open()
        except DatabaseError:
            raise CatalogUnavailable(CATALOG_UNAVAILABLE_MESSAGE) from None

    def close(self) -> None:
        """Close the connection pool during application shutdown."""

        self._database.close()

    def catalog(self) -> CatalogResponse:
        """Return faculties, degree and university options in persisted source order."""

        try:
            with self._database.read_transaction("catalog") as conn:
                _require_ready_catalog(conn)
                degrees = conn.execute(CATALOG_DEGREES_SQL).fetchall()
                universities = conn.execute(CATALOG_UNIVERSITIES_SQL).fetchall()
                faculties = conn.execute(CATALOG_FACULTIES_SQL).fetchall()
                degree_memberships = conn.execute(DEGREE_FACULTY_IDS_SQL).fetchall()
                university_memberships = conn.execute(UNIVERSITY_FACULTY_IDS_SQL).fetchall()
        except DatabaseError:
            raise CatalogUnavailable(CATALOG_UNAVAILABLE_MESSAGE) from None

        # Defensive re-check of the readiness invariant against the fetched rows,
        # guarding the gap between the readiness query and these reads: a catalog
        # with no degrees or universities is not ready to serve.
        if not degrees or not universities:
            LOG.error("Catalog core tables have no degrees or universities")
            raise CatalogUnavailable(CATALOG_UNAVAILABLE_MESSAGE)

        # A null full_title means the core catalog is incomplete and not ready.
        if any(full_title is None for _, _, full_title in degrees):
            LOG.error("Catalog core tables have a degree without a full title")
            raise CatalogUnavailable(CATALOG_UNAVAILABLE_MESSAGE)

        # Group ordered membership rows by parent id; the ordered fetch keeps
        # the faculty name/id sort within each parent list.
        degree_faculty_ids: dict[int, list[int]] = {}
        for degree_id, faculty_id in degree_memberships:
            degree_faculty_ids.setdefault(int(degree_id), []).append(int(faculty_id))
        university_faculty_ids: dict[int, list[int]] = {}
        for university_id, faculty_id in university_memberships:
            university_faculty_ids.setdefault(int(university_id), []).append(int(faculty_id))

        return CatalogResponse(
            faculties=[
                FacultyOption(id=int(faculty_id), name=name) for faculty_id, name in faculties
            ],
            degrees=[
                DegreeOption(
                    name=name,
                    degree=full_title,
                    faculty_ids=degree_faculty_ids.get(int(degree_id), []),
                )
                for degree_id, name, full_title in degrees
            ],
            universities=[
                _university_option(row, university_faculty_ids) for row in universities
            ],
        )

    def recommendations(self, degree: str) -> RecommendationsResponse:
        """Rank all universities by distinct NUS modules in one set-based query."""

        try:
            with self._database.read_transaction("recommendations") as conn:
                _require_ready_catalog(conn)
                degree_id = _require_degree(conn, degree)
                rows = conn.execute(RANKINGS_SQL, (degree_id,)).fetchall()
        except DatabaseError:
            raise CatalogUnavailable(CATALOG_UNAVAILABLE_MESSAGE) from None

        return RecommendationsResponse(
            degree=degree,
            recommendations=[
                Recommendation(
                    university=university,
                    country=country,
                    partner_module_count=partner_count,
                    distinct_nus_module_count=distinct_nus_count,
                    mapping_count=mapping_count,
                )
                for university, country, mapping_count, distinct_nus_count, partner_count in rows
            ],
        )

    def mappings(self, degree: str, university: str) -> MappingResponse:
        """Return every qualifying source row for one degree/university pair."""

        try:
            with self._database.read_transaction("mappings") as conn:
                _require_ready_catalog(conn)
                selected = conn.execute(DEGREE_UNIVERSITY_IDS_SQL, (degree, university)).fetchone()
                if selected is None:
                    raise UnknownSelection("Unknown degree or university")
                degree_id, university_id = selected
                rows = conn.execute(MAPPINGS_SQL, (university_id, degree_id)).fetchall()
        except DatabaseError:
            raise CatalogUnavailable(CATALOG_UNAVAILABLE_MESSAGE) from None

        # Read canonical module values after cleanup; preserve the archived schema during rollout.
        mappings = [
            Mapping(
                nus_course=Course(code=nus_code, title=nus_title, units=_optional_float(nus_units)),
                partner_course=Course(
                    code=partner_code,
                    title=partner_title,
                    units=_optional_float(partner_units),
                ),
            )
            for nus_code, nus_title, partner_code, partner_title, partner_units, nus_units in rows
        ]
        return MappingResponse(
            degree=degree,
            university=university,
            partner_module_count=len({row.partner_course.code.upper() for row in mappings}),
            distinct_nus_module_count=len({row.nus_course.code.upper() for row in mappings}),
            mappings=mappings,
        )


def _require_ready_catalog(conn: psycopg.Connection) -> None:
    """Reject an unready core catalog with a sanitized error.

    The catalog is ready only when it holds at least one degree, at least one
    university, and no degree with a null full_title. The check reads only core
    tables and runs inside the caller's read transaction.
    """

    row = conn.execute(CORE_READINESS_SQL).fetchone()
    has_degrees, has_universities, has_null_full_title = row
    if not has_degrees or not has_universities or has_null_full_title:
        LOG.error("Catalog core tables are not ready to serve")
        raise CatalogUnavailable(CATALOG_UNAVAILABLE_MESSAGE)


def _require_degree(conn: psycopg.Connection, degree: str) -> int:
    """Return the degree id or raise the shared unknown-selection error."""

    row = conn.execute(DEGREE_ID_SQL, (degree,)).fetchone()
    if row is None:
        raise UnknownSelection("Unknown degree")
    return int(row[0])


def _optional_float(value) -> float | None:
    """Convert a numeric database value while preserving unknown units as null."""

    return float(value) if value is not None else None


def _university_option(row, memberships: dict[int, list[int]]) -> UniversityOption:
    """Build one university option with its explicit faculty availability links."""

    university_id, name, country, city, continent, image, website, attribution = row
    return UniversityOption(
        id=int(university_id),
        name=name,
        country=country,
        city=city,
        continent=continent,
        faculty_ids=memberships.get(int(university_id), []),
        image=image,
        website=website,
        image_attribution=attribution,
    )
