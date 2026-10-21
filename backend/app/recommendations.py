from .catalog import Catalog
from .matching import count_distinct_nus_modules, count_partner_modules, pair_mappings
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
                partner_module_count=count_partner_modules(rows),
                distinct_nus_module_count=count_distinct_nus_modules(rows),
                mapping_count=len(rows),
            )
        )
    return sorted(ranked, key=lambda item: (-item.distinct_nus_module_count, item.university))
