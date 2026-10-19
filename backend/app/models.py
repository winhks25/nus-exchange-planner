from pydantic import BaseModel, ConfigDict, Field

COUNTRIES = {
    "australia": "Australia",
    "canada": "Canada",
    "japan": "Japan",
    "korea": "South Korea",
}


class Course(BaseModel):
    model_config = ConfigDict(frozen=True, extra="ignore")
    code: str
    title: str | None = None
    units: float | None = None


class Mapping(BaseModel):
    model_config = ConfigDict(frozen=True, extra="ignore")
    nus_course: Course
    partner_course: Course


class SourceUniversity(BaseModel):
    partner_university: dict[str, str]
    mappings: list[Mapping]


class SourceMajors(BaseModel):
    majors: list[dict]


class Degree(BaseModel):
    model_config = ConfigDict(frozen=True)
    name: str
    degree: str
    codes: frozenset[str] = Field(exclude=True)


class University(BaseModel):
    model_config = ConfigDict(frozen=True)
    name: str
    country: str
    mappings: tuple[Mapping, ...] = Field(exclude=True)


class DegreeOption(BaseModel):
    name: str
    degree: str


class UniversityOption(BaseModel):
    name: str
    country: str


class CatalogResponse(BaseModel):
    degrees: list[DegreeOption]
    universities: list[UniversityOption]


class ErrorResponse(BaseModel):
    detail: str


class Recommendation(BaseModel):
    university: str
    country: str
    module_count: int


class RecommendationsResponse(BaseModel):
    degree: str
    recommendations: list[Recommendation]


class MappingResponse(BaseModel):
    degree: str
    university: str
    distinct_nus_module_count: int
    mappings: list[Mapping]
