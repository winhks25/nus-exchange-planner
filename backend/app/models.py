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
    # Stable faculty ids, sorted by faculty name then id; empty when no
    # membership is recorded.
    faculty_ids: list[int] = Field(default_factory=list)


class UniversityOption(BaseModel):
    # Stable database identity; null when the source cannot assign one.
    id: int | None = None
    name: str
    country: str
    # Nullable metadata: null means unknown, never inferred.
    city: str | None = None
    continent: str | None = None
    # Explicit faculty availability links; empty means none recorded.
    faculty_ids: list[int] = Field(default_factory=list)
    image: str | None = None
    website: str | None = None
    image_attribution: str | None = None


class FacultyOption(BaseModel):
    id: int
    name: str


class CatalogResponse(BaseModel):
    faculties: list[FacultyOption] = Field(default_factory=list)
    degrees: list[DegreeOption]
    universities: list[UniversityOption]


class ErrorResponse(BaseModel):
    detail: str


class Recommendation(BaseModel):
    university: str
    country: str
    partner_module_count: int
    distinct_nus_module_count: int
    mapping_count: int


class RecommendationsResponse(BaseModel):
    degree: str
    recommendations: list[Recommendation]


class MappingResponse(BaseModel):
    degree: str
    university: str
    partner_module_count: int
    distinct_nus_module_count: int
    mappings: list[Mapping]
