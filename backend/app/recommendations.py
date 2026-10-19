from .catalog import Catalog
from .matching import pair_mappings
from .models import Recommendation


def rank_universities(catalog: Catalog, degree_name: str) -> list[Recommendation]:
    if catalog.degree(degree_name) is None:
        raise KeyError("Unknown degree")
    ranked = [
        Recommendation(
            university=university.name,
            country=university.country,
            module_count=len({row.nus_course.code.upper() for row in pair_mappings(catalog, degree_name, university.name)}),
        )
        for university in catalog.universities
    ]
    return sorted(ranked, key=lambda item: (-item.module_count, item.university))
