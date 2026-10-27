"""Repository adapter for the frozen JSON catalog used during migration."""

from pathlib import Path

from pydantic import BaseModel, Field, ValidationError

from ..catalog import DATA_ROOT, MANIFEST, Catalog, load_catalog
from ..catalog import CatalogUnavailable as SourceUnavailable
from ..matching import compare_rows, count_distinct_nus_modules, count_partner_modules
from ..models import (
    CatalogResponse,
    DegreeOption,
    FacultyOption,
    MappingResponse,
    RecommendationsResponse,
    UniversityOption,
)
from ..recommendations import rank_universities
from .base import CATALOG_UNAVAILABLE_MESSAGE, CatalogUnavailable, UnknownSelection


class LocationMetadata(BaseModel):
    country: str
    city: str | None = None
    continent: str | None = None


class CatalogMetadata(BaseModel):
    faculties: list[FacultyOption] = Field(default_factory=list)
    degree_faculty_ids: dict[str, list[int]] = Field(default_factory=dict)
    university_locations: dict[str, LocationMetadata] = Field(default_factory=dict)


class JsonCatalogRepository:
    """Serve all three API responses from the checked-in JSON snapshot."""

    def __init__(self, data_root: Path = DATA_ROOT, manifest: Path = MANIFEST) -> None:
        # Validate the manifest and every source file before the app starts serving.
        try:
            self._catalog = load_catalog(data_root, manifest)
            path = data_root / "catalog-metadata.json"
            self._metadata = (
                CatalogMetadata.model_validate_json(path.read_text())
                if path.exists() else CatalogMetadata()
            )
            faculty_ids = {faculty.id for faculty in self._metadata.faculties}
            if len(faculty_ids) != len(self._metadata.faculties) or any(
                not faculty.name.strip() for faculty in self._metadata.faculties
            ):
                raise ValueError("Invalid faculties")
            for name, ids in self._metadata.degree_faculty_ids.items():
                if self._catalog.degree(name) is None or not set(ids) <= faculty_ids:
                    raise ValueError("Invalid degree membership")
            for name, location in self._metadata.university_locations.items():
                university = self._catalog.university(name)
                if university is None or university.country != location.country:
                    raise ValueError("Invalid university location")
        except SourceUnavailable:
            raise CatalogUnavailable(CATALOG_UNAVAILABLE_MESSAGE) from None
        except (OSError, ValueError, ValidationError):
            raise CatalogUnavailable(CATALOG_UNAVAILABLE_MESSAGE) from None

    def startup(self) -> None:
        """The JSON snapshot needs no external resources or network access."""

    def close(self) -> None:
        """The JSON snapshot has no resources to release."""

    def catalog(self) -> CatalogResponse:
        return _catalog_response(self._catalog, self._metadata)

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


def _catalog_response(catalog: Catalog, metadata: CatalogMetadata) -> CatalogResponse:
    """Map the in-memory catalog to the public response model.

    Optional reviewed metadata enables filters without changing the frozen
    curriculum or mapping snapshot. Missing metadata remains unknown.
    """

    return CatalogResponse(
        faculties=metadata.faculties,
        degrees=[
            DegreeOption(
                name=item.name, degree=item.degree,
                faculty_ids=metadata.degree_faculty_ids.get(item.name, []),
            )
            for item in catalog.degrees
        ],
        universities=[
            UniversityOption(
                id=None,
                name=item.name,
                country=item.country,
                city=metadata.university_locations[item.name].city
                if item.name in metadata.university_locations else None,
                continent=metadata.university_locations[item.name].continent
                if item.name in metadata.university_locations else None,
                faculty_ids=[],
                image=None,
                website=None,
                image_attribution=None,
            )
            for item in catalog.universities
        ],
    )
