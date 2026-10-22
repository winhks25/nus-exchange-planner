"""Shared repository contract and errors for catalog-backed API routes."""

from typing import Protocol

from ..models import CatalogResponse, MappingResponse, RecommendationsResponse

CATALOG_UNAVAILABLE_MESSAGE = "Catalog data is unavailable. Please try again later."


class RepositoryError(Exception):
    """Base class for failures raised by a catalog repository."""


class UnknownSelection(RepositoryError):
    """Raised when a degree or partner university is not published."""


class CatalogUnavailable(RepositoryError):
    """Raised when catalog data cannot be served without partial results."""


class CatalogRepository(Protocol):
    """Read-only catalog operations used by the HTTP routes.

    Adapters own their storage details so route handlers only translate domain
    errors into the response contract.
    """

    def startup(self) -> None:
        """Prepare external resources such as a connection pool."""

    def close(self) -> None:
        """Release external resources during application shutdown."""

    def catalog(self) -> CatalogResponse:
        """Return degree and university options in source order."""

    def recommendations(self, degree: str) -> RecommendationsResponse:
        """Rank every university for one degree, including zero-count partners."""

    def mappings(self, degree: str, university: str) -> MappingResponse:
        """Return every mapping row for one degree/university pair."""
