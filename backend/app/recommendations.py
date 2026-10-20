from .catalog import Catalog
from .matching import pair_mappings
from .models import Recommendation


def rank_universities(catalog: Catalog, degree_name: str) -> list[Recommendation]:
    if catalog.degree(degree_name) is None:
        raise KeyError("Unknown degree")
    ranked = []
    for university in catalog.universities:
        rows = pair_mappings(catalog, degree_name, university.name)
        ranked.append(
            Recommendation(
                university=university.name,
                country=university.country,
                partner_module_count=len({row.partner_course.code.upper() for row in rows}),
                distinct_nus_module_count=len({row.nus_course.code.upper() for row in rows}),
                mapping_count=len(rows),
            )
        )
    return sorted(ranked, key=lambda item: (-item.distinct_nus_module_count, item.university))
