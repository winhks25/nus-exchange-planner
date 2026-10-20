import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .catalog import DATA_ROOT, MANIFEST, CatalogUnavailable, load_catalog
from .matching import compare_rows
from .models import CatalogResponse, ErrorResponse, MappingResponse, RecommendationsResponse
from .recommendations import rank_universities


def create_app(data_root: Path = DATA_ROOT, manifest: Path = MANIFEST) -> FastAPI:
    app = FastAPI(title="NUS Exchange Planner API", version="1.0.0")
    origins = [value.strip() for value in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",") if value.strip()]
    app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["GET"], allow_headers=["*"])
    try:
        catalog = load_catalog(data_root, manifest)
    except CatalogUnavailable:
        catalog = None

    def available():
        if catalog is None:
            raise HTTPException(status_code=503, detail="Catalog data is unavailable. Please try again later.")
        return catalog

    @app.get("/api/v1/catalog", response_model=CatalogResponse, responses={503: {"model": ErrorResponse, "description": "Catalog unavailable"}})
    def get_catalog():
        data = available()
        return CatalogResponse(
            degrees=[{"name": item.name, "degree": item.degree} for item in data.degrees],
            universities=[{"name": item.name, "country": item.country} for item in data.universities],
        )

    @app.get("/api/v1/recommendations", response_model=RecommendationsResponse, responses={404: {"model": ErrorResponse, "description": "Unknown degree"}, 503: {"model": ErrorResponse, "description": "Catalog unavailable"}})
    def recommendations(degree: str):
        data = available()
        try:
            return RecommendationsResponse(degree=degree, recommendations=rank_universities(data, degree))
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.get("/api/v1/mappings", response_model=MappingResponse, response_model_exclude_none=True, responses={404: {"model": ErrorResponse, "description": "Unknown degree or university"}, 503: {"model": ErrorResponse, "description": "Catalog unavailable"}})
    def mappings(degree: str, uni: str):
        data = available()
        try:
            rows = compare_rows(data, degree, uni)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return MappingResponse(
            degree=degree,
            university=uni,
            partner_module_count=len({row.partner_course.code.upper() for row in rows}),
            distinct_nus_module_count=len({row.nus_course.code.upper() for row in rows}),
            mappings=rows,
        )

    return app


app = create_app()
