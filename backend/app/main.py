import logging
import os
from collections.abc import Callable
from contextlib import asynccontextmanager
from pathlib import Path
from typing import TypeVar

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .catalog import DATA_ROOT, MANIFEST
from .models import (
    CatalogResponse,
    ErrorResponse,
    MappingResponse,
    RecommendationsResponse,
)
from .repositories.base import (
    CATALOG_UNAVAILABLE_MESSAGE,
    CatalogRepository,
    CatalogUnavailable,
    UnknownSelection,
)
from .repositories.json_catalog import JsonCatalogRepository
from .repositories.postgres_catalog import PostgresCatalogRepository
from .settings import Settings

LOG = logging.getLogger(__name__)
T = TypeVar("T")


class _UnavailableRepository:
    """Fail closed when startup cannot provide any usable catalog source."""

    def startup(self) -> None:
        """No resources to prepare."""

    def close(self) -> None:
        """No resources to release."""

    def catalog(self) -> CatalogResponse:
        raise CatalogUnavailable(CATALOG_UNAVAILABLE_MESSAGE)

    def recommendations(self, degree: str) -> RecommendationsResponse:
        raise CatalogUnavailable(CATALOG_UNAVAILABLE_MESSAGE)

    def mappings(self, degree: str, university: str) -> MappingResponse:
        raise CatalogUnavailable(CATALOG_UNAVAILABLE_MESSAGE)


def build_repository(
    settings: Settings, data_root: Path = DATA_ROOT, manifest: Path = MANIFEST
) -> CatalogRepository:
    """Select one storage adapter from explicit configuration."""

    if settings.catalog_backend == "postgres":
        return PostgresCatalogRepository(settings)
    try:
        return JsonCatalogRepository(data_root, manifest)
    except CatalogUnavailable as exc:
        LOG.error("JSON catalog unavailable: %s", exc)
        return _UnavailableRepository()


def create_app(
    data_root: Path = DATA_ROOT,
    manifest: Path = MANIFEST,
    settings: Settings | None = None,
    repository: CatalogRepository | None = None,
) -> FastAPI:
    active_settings = settings if settings is not None else Settings.from_env()
    active_repository = repository or build_repository(active_settings, data_root, manifest)

    @asynccontextmanager
    async def lifespan(application: FastAPI):
        # Open external resources (notably the database pool) after app construction.
        try:
            application.state.repository.startup()
        except CatalogUnavailable as exc:
            LOG.error("Catalog repository startup failed: %s", exc)
            application.state.repository = _UnavailableRepository()
        try:
            yield
        finally:
            application.state.repository.close()

    app = FastAPI(
        title="NUS Exchange Planner API", version="1.0.0", lifespan=lifespan
    )
    app.state.repository = active_repository
    origins = [
        value.strip()
        for value in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
        if value.strip()
    ]
    app.add_middleware(
        CORSMiddleware, allow_origins=origins, allow_methods=["GET"], allow_headers=["*"]
    )

    def repository_call(operation: Callable[[], T]) -> T:
        """Translate shared repository errors into the existing HTTP contract."""

        try:
            return operation()
        except UnknownSelection as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except CatalogUnavailable as exc:
            detail = str(exc) or CATALOG_UNAVAILABLE_MESSAGE
            raise HTTPException(status_code=503, detail=detail) from exc

    @app.get(
        "/api/v1/catalog",
        response_model=CatalogResponse,
        responses={503: {"model": ErrorResponse, "description": "Catalog unavailable"}},
    )
    def get_catalog():
        return repository_call(app.state.repository.catalog)

    @app.get(
        "/api/v1/recommendations",
        response_model=RecommendationsResponse,
        responses={
            404: {"model": ErrorResponse, "description": "Unknown degree"},
            503: {"model": ErrorResponse, "description": "Catalog unavailable"},
        },
    )
    def recommendations(degree: str):
        return repository_call(lambda: app.state.repository.recommendations(degree))

    @app.get(
        "/api/v1/mappings",
        response_model=MappingResponse,
        response_model_exclude_none=True,
        responses={
            404: {"model": ErrorResponse, "description": "Unknown degree or university"},
            503: {"model": ErrorResponse, "description": "Catalog unavailable"},
        },
    )
    def mappings(degree: str, uni: str):
        return repository_call(lambda: app.state.repository.mappings(degree, uni))

    return app


app = create_app()
