"""Transform the checked-in catalog into normalized, importable records.

The importer consumes only the deterministic preview produced by T012. Entity
records are built and validated here before any database connection is opened,
so a malformed source fails without touching the target.
"""

from dataclasses import dataclass
from typing import Any

from app.course_codes import normalized_course_code
from scripts.catalog_preview import build_preview


class ImportError(RuntimeError):
    """Base class for importer failures that must not leak connection details."""


class ImportDataError(ImportError):
    """Raised when the source cannot be represented without inventing data."""


@dataclass(frozen=True)
class DegreeRecord:
    """One degree and its published presentation fields."""

    name: str
    full_title: str
    faculty: str
    source_order: int


@dataclass(frozen=True)
class NusModuleRecord:
    """One case-insensitive NUS course identity with optional verified metadata."""

    code: str
    name: str | None
    offering_faculty: str | None
    verified_units: float | None


@dataclass(frozen=True)
class DegreeModuleRecord:
    """One degree membership, including its source requirement mode."""

    degree: str
    module_code: str
    requirement_type: str | None


@dataclass(frozen=True)
class UniversityRecord:
    """One partner university in source order."""

    name: str
    country: str
    city: str | None
    continent: str | None
    source_order: int


@dataclass(frozen=True)
class PartnerModuleRecord:
    """One partner-scoped course identity with optional source metadata."""

    university: str
    code: str
    name: str | None
    verified_units: float | None


@dataclass(frozen=True)
class SpecializationRecord:
    """One degree-scoped specialization or CS focus area."""

    degree: str
    name: str
    kind: str
    source_order: int
    membership_note: str | None


@dataclass(frozen=True)
class SpecializationModuleRecord:
    """One explicit specialization membership; never a degree requirement."""

    degree: str
    specialization: str
    module_code: str


@dataclass(frozen=True)
class CatalogEntities:
    """All normalized entities and memberships that are safe to publish."""

    degrees: tuple[DegreeRecord, ...]
    nus_modules: tuple[NusModuleRecord, ...]
    degree_modules: tuple[DegreeModuleRecord, ...]
    universities: tuple[UniversityRecord, ...]
    partner_modules: tuple[PartnerModuleRecord, ...]
    specializations: tuple[SpecializationRecord, ...]
    specialization_modules: tuple[SpecializationModuleRecord, ...]


@dataclass(frozen=True)
class ImportPlan:
    """Everything the importer needs for one exact source snapshot."""

    preview: dict[str, Any]
    entities: CatalogEntities

    @property
    def source_checksum(self) -> str:
        return str(self.preview["source_snapshot"]["source_checksum_sha256"])

    @property
    def repair_checksum(self) -> str:
        return str(self.preview["source_snapshot"]["repair_checksum_sha256"])

    @property
    def summary(self) -> dict[str, Any]:
        return self.preview["summary"]


def build_import_plan() -> ImportPlan:
    """Build and validate the entity plan without opening a database connection."""

    preview = build_preview()
    entities = _build_entities(preview)
    return ImportPlan(preview=preview, entities=entities)


def _build_entities(preview: dict[str, Any]) -> CatalogEntities:
    """Convert preview dictionaries into typed, cross-checked entity records."""

    degrees = tuple(_degree_record(item) for item in preview["degrees"])
    nus_modules = tuple(_nus_module_record(item) for item in preview["nus_modules"])
    degree_modules = tuple(
        _degree_module_record(degree["name"], item)
        for degree in preview["degrees"]
        for item in degree["degree_modules"]
    )
    universities = tuple(_university_record(item) for item in preview["universities"])
    partner_modules = tuple(_partner_module_record(item) for item in preview["partner_modules"])
    specializations = tuple(_specialization_record(item) for item in preview["specializations"])
    specialization_modules = tuple(
        SpecializationModuleRecord(
            degree=item["degree"], specialization=item["name"], module_code=code
        )
        for item in preview["specializations"]
        for code in item["memberships"]
    )
    entities = CatalogEntities(
        degrees=degrees,
        nus_modules=nus_modules,
        degree_modules=degree_modules,
        universities=universities,
        partner_modules=partner_modules,
        specializations=specializations,
        specialization_modules=specialization_modules,
    )
    _validate_entities(entities)
    _validate_degree_eligibility(preview, entities)
    return entities


def _validate_degree_eligibility(preview: dict[str, Any], entities: CatalogEntities) -> None:
    """Prove degree memberships still equal the legacy extractor's code set."""

    memberships: dict[str, set[str]] = {}
    for item in entities.degree_modules:
        memberships.setdefault(item.degree, set()).add(item.module_code)
    for degree in preview["degrees"]:
        expected = {str(code) for code in degree["codes"]}
        actual = memberships.get(degree["name"], set())
        if actual != expected:
            missing = sorted(expected - actual)
            unexpected = sorted(actual - expected)
            raise ImportDataError(
                f"Degree eligibility changed for {degree['name']}: "
                f"missing={missing}, unexpected={unexpected}"
            )


def _degree_record(item: dict[str, Any]) -> DegreeRecord:
    """Build one degree while preserving its full title and source order."""

    return DegreeRecord(
        name=_required_text(item.get("name"), "degree name"),
        full_title=_required_text(item.get("full_title"), "degree full_title"),
        faculty=_required_text(item.get("faculty"), "degree faculty"),
        source_order=_required_int(item.get("source_order"), "degree source_order"),
    )


def _nus_module_record(item: dict[str, Any]) -> NusModuleRecord:
    """Build one NUS course identity, leaving unknown names and units null."""

    code = _required_code(item.get("code"), "NUS module code", course_code=True)
    return NusModuleRecord(
        code=code,
        name=_optional_text(item.get("name"), "NUS module name"),
        offering_faculty=_optional_text(item.get("offering_faculty"), "NUS offering_faculty"),
        verified_units=_optional_positive(item.get("verified_units"), "NUS units"),
    )


def _degree_module_record(degree: str, item: dict[str, Any]) -> DegreeModuleRecord:
    """Keep the legacy extractor's per-course requirement label exactly."""

    return DegreeModuleRecord(
        degree=_required_text(degree, "degree membership degree"),
        module_code=_required_code(
            item.get("code"), "degree membership module code", course_code=True
        ),
        requirement_type=_optional_text(
            item.get("requirement_type"), "degree membership requirement_type"
        ),
    )


def _university_record(item: dict[str, Any]) -> UniversityRecord:
    """Build one partner university without inventing city or continent."""

    return UniversityRecord(
        name=_required_text(item.get("name"), "university name"),
        country=_required_text(item.get("country"), "university country"),
        city=_optional_text(item.get("city"), "university city"),
        continent=_optional_text(item.get("continent"), "university continent"),
        source_order=_required_int(item.get("source_order"), "university source_order"),
    )


def _partner_module_record(item: dict[str, Any]) -> PartnerModuleRecord:
    """Build one partner-scoped identity; display codes stay in the raw archive."""

    return PartnerModuleRecord(
        university=_required_text(item.get("university"), "partner module university"),
        code=_required_code(item.get("code"), "partner module code"),
        name=_optional_text(item.get("name"), "partner module name"),
        verified_units=_optional_positive(item.get("verified_units"), "partner module units"),
    )


def _specialization_record(item: dict[str, Any]) -> SpecializationRecord:
    """Keep the source kind, order and note for one degree-scoped option."""

    kind = _required_text(item.get("kind"), "specialization kind")
    if kind not in {"specialization", "focus_area"}:
        raise ImportDataError(f"Unsupported specialization kind: {kind}")
    return SpecializationRecord(
        degree=_required_text(item.get("degree"), "specialization degree"),
        name=_required_text(item.get("name"), "specialization name"),
        kind=kind,
        source_order=_required_int(item.get("source_order"), "specialization source_order"),
        membership_note=_optional_text(
            item.get("membership_note"), "specialization membership_note"
        ),
    )


def _validate_entities(entities: CatalogEntities) -> None:
    """Reject duplicate identities or broken references before database work."""

    degree_names = _unique_values((item.name for item in entities.degrees), "degree names")
    _unique_values((item.source_order for item in entities.degrees), "degree source orders")
    nus_codes = _unique_values((item.code for item in entities.nus_modules), "NUS module codes")
    university_names = _unique_values(
        (item.name for item in entities.universities), "university names"
    )
    _unique_values(
        (item.source_order for item in entities.universities),
        "university source orders",
    )
    _unique_values(
        ((item.university, item.code) for item in entities.partner_modules),
        "partner module identities",
    )

    # Every membership, mapping code and partner course must resolve inside the plan.
    membership_keys = _unique_values(
        ((item.degree, item.module_code) for item in entities.degree_modules),
        "degree module memberships",
    )
    for degree, module_code in membership_keys:
        if degree not in degree_names:
            raise ImportDataError(f"Degree membership cites unknown degree: {degree}")
        if module_code not in nus_codes:
            raise ImportDataError(f"Degree membership cites unknown NUS module: {module_code}")

    for item in entities.partner_modules:
        if item.university not in university_names:
            raise ImportDataError(f"Partner module cites unknown university: {item.university}")

    # Specialization memberships are exported separately and never merged into degree_modules.
    specialization_keys = _unique_values(
        ((item.degree, item.name) for item in entities.specializations),
        "specialization identities",
    )
    _unique_values(
        ((item.degree, item.source_order) for item in entities.specializations),
        "specialization source orders",
    )
    for degree, _ in specialization_keys:
        if degree not in degree_names:
            raise ImportDataError(f"Specialization cites unknown degree: {degree}")

    membership_keys = _unique_values(
        (
            (item.degree, item.specialization, item.module_code)
            for item in entities.specialization_modules
        ),
        "specialization memberships",
    )
    for degree, specialization, module_code in membership_keys:
        if (degree, specialization) not in specialization_keys:
            raise ImportDataError(
                f"Specialization membership cites unknown option: {degree}/{specialization}"
            )
        if module_code not in nus_codes:
            raise ImportDataError(
                f"Specialization membership cites unknown NUS module: {module_code}"
            )


def _unique_values(values: Any, label: str) -> set[Any]:
    """Collect values and raise on duplicates instead of relying on a database error."""

    collected: set[Any] = set()
    for value in values:
        if value in collected:
            raise ImportDataError(f"Duplicate {label}: {value!r}")
        collected.add(value)
    return collected


def _required_text(value: object, label: str) -> str:
    """Return trimmed nonblank text or fail with a source-specific message."""

    text = _optional_text(value, label)
    if text is None:
        raise ImportDataError(f"Missing or blank {label}")
    return text


def _optional_text(value: object, label: str) -> str | None:
    """Normalize optional text and reject non-string source values."""

    if value is None:
        return None
    if not isinstance(value, str):
        raise ImportDataError(f"{label} must be text, got {type(value).__name__}")
    text = value.strip()
    return text or None


def _required_int(value: object, label: str) -> int:
    """Return a non-negative integer without coercing booleans or strings."""

    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ImportDataError(f"{label} must be a non-negative integer")
    return value


def _required_code(value: object, label: str, *, course_code: bool = False) -> str:
    """Return an uppercase code; NUS identities must also match the legacy pattern."""

    code = _required_text(value, label)
    if code != code.upper():
        raise ImportDataError(f"{label} must already be uppercase: {code}")
    if course_code and normalized_course_code(code) != code:
        raise ImportDataError(f"{label} is not a valid course code: {code}")
    return code


def _optional_positive(value: object, label: str) -> float | None:
    """Return a verified positive number, preserving unknown values as null."""

    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ImportDataError(f"{label} must be numeric or null")
    number = float(value)
    if number <= 0:
        raise ImportDataError(f"{label} must be positive or null")
    return number


def main() -> int:
    """Print a compact plan summary; database publishing is added in T016."""

    plan = build_import_plan()
    entities = plan.entities
    print(
        "Import plan: "
        f"{len(entities.degrees)} degrees, "
        f"{len(entities.universities)} universities, "
        f"{len(entities.nus_modules)} NUS modules, "
        f"{len(entities.partner_modules)} partner modules, "
        f"{len(entities.degree_modules)} degree memberships, "
        f"{len(entities.specializations)} specializations/focus areas, "
        f"{len(entities.specialization_modules)} specialization memberships"
    )
    print(f"Source checksum: {plan.source_checksum}")
    print(f"Repair checksum: {plan.repair_checksum}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
