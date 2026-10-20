from .catalog import Catalog
from .course_codes import normalized_course_code
from .models import Mapping


def pair_mappings(catalog: Catalog, degree_name: str, university_name: str) -> tuple[Mapping, ...]:
    degree = catalog.degree(degree_name)
    university = catalog.university(university_name)
    if degree is None or university is None:
        raise KeyError("Unknown degree or university")
    return tuple(
        row
        for row in university.mappings
        if normalized_course_code(row.nus_course.code) in degree.codes
    )


def compare_rows(catalog: Catalog, degree_name: str, university_name: str) -> list[Mapping]:
    rows = pair_mappings(catalog, degree_name, university_name)
    return [
        row.model_copy(update={"nus_course": row.nus_course.model_copy(update={"units": 4})})
        for row in sorted(rows, key=lambda row: row.nus_course.code.upper())
    ]
