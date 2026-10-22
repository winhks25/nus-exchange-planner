"""Repository adapter for the frozen JSON catalog used during migration."""

from pathlib import Path

from ..catalog import DATA_ROOT, MANIFEST, Catalog, load_catalog
from ..catalog import CatalogUnavailable as SourceUnavailable
from ..matching import compare_rows, count_distinct_nus_modules, count_partner_modules
from ..models import (
    CatalogResponse,
    DegreeOption,
    MappingResponse,
    RecommendationsResponse,
    UniversityOption,
)
from ..recommendations import rank_universities
from .base import CATALOG_UNAVAILABLE_MESSAGE, CatalogUnavailable, UnknownSelection


class JsonCatalogRepository:
    """Serve all three API responses from the checked-in JSON snapshot."""

    def __init__(self, data_root: Path = DATA_ROOT, manifest: Path = MANIFEST) -> None:
        # Validate the manifest and every source file before the app starts serving.
        try:
            self._catalog = load_catalog(data_root, manifest)
        except SourceUnavailable:
            raise CatalogUnavailable(CATALOG_UNAVAILABLE_MESSAGE) from None

    def startup(self) -> None:
        """The JSON snapshot needs no external resources or network access."""

    def close(self) -> None:
        """The JSON snapshot has no resources to release."""

    def catalog(self) -> CatalogResponse:
        return _catalog_response(self._catalog)

    def recommendations(self, degree: str) -> RecommendationsResponse:
        # Match the legacy route's error text and ranking order exactly.
        if self._catalog.degree(degree) is None:
            raise UnknownSelection("Unknown degree")
        return RecommendationsResponse(
            degree=degree, recommendations=rank_universities(self._catalog, degree)
        )

    def mappings(self, degree: str, university: str) -> MappingResponse:
        # compare_rows validates both selections and applies the displayed NUS units policy.
        try:
            rows = compare_rows(self._catalog, degree, university)
        except KeyError as exc:
            raise UnknownSelection("Unknown degree or university") from exc
        return MappingResponse(
            degree=degree,
            university=university,
            partner_module_count=count_partner_modules(rows),
            distinct_nus_module_count=count_distinct_nus_modules(rows),
            mappings=rows,
        )


def _catalog_response(catalog: Catalog) -> CatalogResponse:
    """Map the in-memory catalog to the public response model."""

    return CatalogResponse(
        degrees=[
            DegreeOption(name=item.name, degree=item.degree) for item in catalog.degrees
        ],
        universities=[
            UniversityOption(name=item.name, country=item.country)
            for item in catalog.universities
        ],
    )
