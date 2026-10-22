"""Read-only repository adapter backed by the published PostgreSQL catalog."""

import logging

import psycopg

from ..database import CatalogDatabase, DatabaseError
from ..models import CatalogResponse, DegreeOption, UniversityOption
from ..settings import Settings
from .base import CATALOG_UNAVAILABLE_MESSAGE, CatalogUnavailable

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


def _require_published_batch(conn: psycopg.Connection) -> None:
    """Reject an unpopulated or unpublished database with a sanitized error."""

    if conn.execute(PUBLISHED_BATCH_SQL).fetchone() is None:
        LOG.error("Catalog database has no completed current import batch")
        raise CatalogUnavailable(CATALOG_UNAVAILABLE_MESSAGE)
