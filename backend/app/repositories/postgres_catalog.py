"""Read-only repository adapter backed by the published PostgreSQL catalog."""

import logging

import psycopg

from ..database import CatalogDatabase, DatabaseError
from ..models import (
    CatalogResponse,
    DegreeOption,
    Recommendation,
    RecommendationsResponse,
    UniversityOption,
)
from ..settings import Settings
from .base import CATALOG_UNAVAILABLE_MESSAGE, CatalogUnavailable, UnknownSelection

LOG = logging.getLogger(__name__)

PUBLISHED_BATCH_SQL = """
select 1
from public.catalog_import_batches
where status = 'completed' and is_current
limit 1
"""

CATALOG_DEGREES_SQL = """
select name, full_title
from public.degrees
order by source_order nulls last, id
"""

CATALOG_UNIVERSITIES_SQL = """
select name, country
from public.partner_universities
order by source_order nulls last, id
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


class PostgresCatalogRepository:
    """Serve catalog responses from a completed, current import batch."""

    def __init__(self, settings: Settings) -> None:
        self._database = CatalogDatabase(settings)

    def startup(self) -> None:
        """Start the bounded connection pool without opening a network connection."""

        self._database.open()

    def close(self) -> None:
        """Close the connection pool during application shutdown."""

        self._database.close()

    def catalog(self) -> CatalogResponse:
        """Return degree and university options in their persisted source order."""

        try:
            with self._database.read_transaction("catalog") as conn:
                _require_published_batch(conn)
                degrees = conn.execute(CATALOG_DEGREES_SQL).fetchall()
                universities = conn.execute(CATALOG_UNIVERSITIES_SQL).fetchall()
        except DatabaseError:
            raise CatalogUnavailable(CATALOG_UNAVAILABLE_MESSAGE) from None

        # A completed batch with no options is an incomplete import, not an empty catalog.
        if not degrees or not universities:
            LOG.error("Published catalog has no degrees or universities")
            raise CatalogUnavailable(CATALOG_UNAVAILABLE_MESSAGE)

        # Full titles are persisted by the importer; a null title means the import is incomplete.
        if any(full_title is None for _, full_title in degrees):
            LOG.error("Published catalog has a degree without a full title")
            raise CatalogUnavailable(CATALOG_UNAVAILABLE_MESSAGE)

        return CatalogResponse(
            degrees=[
                DegreeOption(name=name, degree=full_title) for name, full_title in degrees
            ],
            universities=[
                UniversityOption(name=name, country=country)
                for name, country in universities
            ],
        )

    def recommendations(self, degree: str) -> RecommendationsResponse:
        """Rank all universities by distinct NUS modules in one set-based query."""

        try:
            with self._database.read_transaction("recommendations") as conn:
                _require_published_batch(conn)
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


def _require_published_batch(conn: psycopg.Connection) -> None:
    """Reject an unpopulated or unpublished database with a sanitized error."""

    if conn.execute(PUBLISHED_BATCH_SQL).fetchone() is None:
        LOG.error("Catalog database has no completed current import batch")
        raise CatalogUnavailable(CATALOG_UNAVAILABLE_MESSAGE)


def _require_degree(conn: psycopg.Connection, degree: str) -> int:
    """Return the degree id or raise the shared unknown-selection error."""

    row = conn.execute(DEGREE_ID_SQL, (degree,)).fetchone()
    if row is None:
        raise UnknownSelection("Unknown degree")
    return int(row[0])
