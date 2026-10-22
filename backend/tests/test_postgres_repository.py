import pytest

from app.repositories.base import CatalogUnavailable, UnknownSelection
from app.repositories.postgres_catalog import PostgresCatalogRepository
from tests.postgres_support import DatabaseTarget

PUBLISHED_BATCH = """
insert into public.catalog_import_batches (
  source_checksum, repair_checksum, status, is_current, completed_at
) values (repeat('a', 64), repeat('b', 64), 'completed', true, now());
"""


def test_unpublished_database_is_unavailable(repository: PostgresCatalogRepository):
    with pytest.raises(CatalogUnavailable):
        repository.catalog()


def test_catalog_uses_source_order_and_full_titles(
    repository: PostgresCatalogRepository, database: DatabaseTarget
):
    database.execute(
        PUBLISHED_BATCH
        + """
        insert into public.degrees (name, faculty, full_title, source_order) values
          ('Second', 'School of Computing', 'Bachelor of Second', 1),
          ('First', 'School of Computing', 'Bachelor of First', 0);
        insert into public.partner_universities (name, country, source_order) values
          ('Later University', 'Japan', 1),
          ('Earlier University', 'Canada', 0);
        """
    )

    catalog = repository.catalog()
    assert [item.model_dump() for item in catalog.degrees] == [
        {"name": "First", "degree": "Bachelor of First"},
        {"name": "Second", "degree": "Bachelor of Second"},
    ]
    assert [item.model_dump() for item in catalog.universities] == [
        {"name": "Earlier University", "country": "Canada"},
        {"name": "Later University", "country": "Japan"},
    ]


def test_completed_batch_without_degrees_is_unavailable(
    repository: PostgresCatalogRepository, database: DatabaseTarget
):
    database.execute(PUBLISHED_BATCH)
    with pytest.raises(CatalogUnavailable):
        repository.catalog()


def test_degree_without_full_title_is_treated_as_incomplete(
    repository: PostgresCatalogRepository, database: DatabaseTarget
):
    database.execute(
        PUBLISHED_BATCH
        + """
        insert into public.degrees (name, faculty, full_title, source_order)
        values ('Test', 'School of Computing', null, 0);
        insert into public.partner_universities (name, country, source_order)
        values ('One University', 'Japan', 0);
        """
    )
    with pytest.raises(CatalogUnavailable):
        repository.catalog()


RANKING_FIXTURE = """
insert into public.nus_modules (code) values
  ('CS2102'), ('CS2103'), ('CS2104'), ('CS2105');
insert into public.degrees (name, faculty, full_title, source_order)
values ('Test', 'School of Computing', 'Bachelor of Test', 0);
insert into public.degree_modules (degree_id, module_code, requirement_type)
select d.id, module_code, null
from public.degrees d
cross join (values ('CS2102'), ('CS2103'), ('CS2104'), ('CS2105')) modules(module_code)
where d.name = 'Test';
insert into public.partner_universities (name, country, source_order) values
  ('A University', 'Japan', 0),
  ('B University', 'Japan', 1),
  ('C University', 'Japan', 2),
  ('Z University', 'Japan', 3);
insert into public.pu_modules (code, partner_university_id)
select pairs.code, u.id
from public.partner_universities u
join (
  values
    ('A University', 'P1'),
    ('A University', 'P2'),
    ('A University', 'P3'),
    ('B University', 'Q1'),
    ('B University', 'Q2'),
    ('B University', 'Q3'),
    ('C University', 'R1'),
    ('C University', 'R2')
) pairs(university, code) on pairs.university = u.name;
insert into public.module_mappings (nus_module_code, pu_module_id)
select pairs.nus_code, pm.id
from (
  values
    ('A University', 'P1', 'CS2102'),
    ('A University', 'P2', 'CS2102'),
    ('A University', 'P3', 'CS2102'),
    ('B University', 'Q1', 'CS2103'),
    ('B University', 'Q2', 'CS2103'),
    ('B University', 'Q3', 'CS2104'),
    ('C University', 'R1', 'CS2103'),
    ('C University', 'R2', 'CS2105')
) pairs(university, partner_code, nus_code)
join public.partner_universities u on u.name = pairs.university
join public.pu_modules pm
  on pm.partner_university_id = u.id and pm.code = pairs.partner_code;
"""


def test_rankings_include_zero_counts_and_order_by_distinct_nus(
    repository: PostgresCatalogRepository, database: DatabaseTarget
):
    database.execute(PUBLISHED_BATCH + RANKING_FIXTURE)

    ranked = repository.recommendations("Test").recommendations
    assert [
        (
            item.university,
            item.partner_module_count,
            item.distinct_nus_module_count,
            item.mapping_count,
        )
        for item in ranked
    ] == [
        ("B University", 3, 2, 3),
        ("C University", 2, 2, 2),
        ("A University", 3, 1, 3),
        ("Z University", 0, 0, 0),
    ]


def test_unknown_degree_is_not_a_server_error(
    repository: PostgresCatalogRepository, database: DatabaseTarget
):
    database.execute(PUBLISHED_BATCH + RANKING_FIXTURE)
    with pytest.raises(UnknownSelection, match="Unknown degree$"):
        repository.recommendations("Missing")


MAPPING_FIXTURE = """
insert into public.nus_modules (code, name) values
  ('CS2102', 'Verified Data'),
  ('CS2103', null),
  ('CS2104', null),
  ('CS2105', null),
  ('CS9999', null);
insert into public.degrees (name, faculty, full_title, source_order)
values ('Test', 'School of Computing', 'Bachelor of Test', 0);
insert into public.degree_modules (degree_id, module_code, requirement_type)
select d.id, module_code, null
from public.degrees d
cross join (values ('CS2102'), ('CS2103'), ('CS2104'), ('CS2105')) modules(module_code)
where d.name = 'Test';
insert into public.partner_universities (name, country, source_order) values
  ('A University', 'Japan', 0),
  ('Z University', 'Japan', 1);
insert into public.pu_modules (code, name, partner_university_id, verified_units)
select pairs.code, pairs.name, u.id, pairs.verified_units
from (
  values
    ('A University', 'P1', 'Verified Partner One', null),
    ('A University', 'P2', null, null),
    ('A University', 'P3', 'Partner Three', 0.5)
) pairs(university, code, name, verified_units)
join public.partner_universities u on u.name = pairs.university;
insert into public.module_mappings (
  nus_module_code,
  pu_module_id,
  source_order,
  source_nus_title,
  source_partner_title,
  source_partner_units
)
select
  pairs.nus_code,
  pm.id,
  pairs.source_order,
  pairs.nus_title,
  pairs.partner_title,
  pairs.partner_units
from (
  values
    ('A University', 'P1', 'CS2102', 1, 'Source Data', null, 3.0),
    ('A University', 'P3', 'CS2102', 0, null, 'Partner Three', null),
    ('A University', 'P2', 'CS2103', 2, null, 'Partner Two', null),
    ('A University', 'P2', 'CS2105', 3, null, null, null),
    ('A University', 'P1', 'CS9999', 4, 'Outside Degree', null, null)
) pairs(university, partner_code, nus_code, source_order, nus_title, partner_title, partner_units)
join public.partner_universities u on u.name = pairs.university
join public.pu_modules pm
  on pm.partner_university_id = u.id and pm.code = pairs.partner_code;
"""


def test_mappings_filter_sort_and_preserve_repeated_rows(
    repository: PostgresCatalogRepository, database: DatabaseTarget
):
    database.execute(PUBLISHED_BATCH + MAPPING_FIXTURE)

    response = repository.mappings("Test", "A University")
    assert response.partner_module_count == 3
    assert response.distinct_nus_module_count == 3
    assert [
        (row.nus_course.code, row.nus_course.title, row.partner_course.code)
        for row in response.mappings
    ] == [
        ("CS2102", "Verified Data", "P3"),
        ("CS2102", "Source Data", "P1"),
        ("CS2103", None, "P2"),
        ("CS2105", None, "P2"),
    ]
    assert all(row.nus_course.units == 4 for row in response.mappings)


def test_mapping_optional_fields_and_partner_unit_fallbacks(
    repository: PostgresCatalogRepository, database: DatabaseTarget
):
    database.execute(PUBLISHED_BATCH + MAPPING_FIXTURE)

    rows = repository.mappings("Test", "A University").mappings
    first, second, third, fourth = rows
    assert first.partner_course.title == "Partner Three"
    assert first.partner_course.units == 0.5
    assert second.partner_course.title == "Verified Partner One"
    assert second.partner_course.units == 3.0
    assert third.partner_course.title == "Partner Two"
    assert third.partner_course.units is None
    assert fourth.partner_course.title is None
    assert fourth.partner_course.units is None


def test_valid_empty_pair_returns_zero_counts(
    repository: PostgresCatalogRepository, database: DatabaseTarget
):
    database.execute(PUBLISHED_BATCH + MAPPING_FIXTURE)

    response = repository.mappings("Test", "Z University")
    assert response.partner_module_count == 0
    assert response.distinct_nus_module_count == 0
    assert response.mappings == []


def test_unknown_mapping_selections_raise_shared_error(
    repository: PostgresCatalogRepository, database: DatabaseTarget
):
    database.execute(PUBLISHED_BATCH + MAPPING_FIXTURE)

    with pytest.raises(UnknownSelection, match="Unknown degree or university$"):
        repository.mappings("Missing", "A University")
    with pytest.raises(UnknownSelection, match="Unknown degree or university$"):
        repository.mappings("Test", "Missing University")
