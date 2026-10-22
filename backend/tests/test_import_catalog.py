from scripts.import_catalog import build_import_plan


def test_import_plan_accounts_for_every_preview_entity():
    plan = build_import_plan()
    entities = plan.entities
    summary = plan.summary

    assert len(entities.degrees) == summary["degrees"] == 6
    assert len(entities.universities) == summary["universities"] == 5
    assert len(entities.nus_modules) == summary["nus_modules"] == 152
    assert len(entities.partner_modules) == summary["partner_modules"] == 142
    assert len(entities.degree_modules) == summary["degree_modules"] == 226
    assert len(entities.specializations) == summary["specializations"] == 19
    assert len(entities.specialization_modules) == summary["specialization_modules"] == 30


def test_specialization_memberships_keep_their_own_requirement_label():
    plan = build_import_plan()
    degree_modules = {
        (item.degree, item.module_code): item for item in plan.entities.degree_modules
    }
    specialization_modules = {
        (item.degree, item.module_code) for item in plan.entities.specialization_modules
    }

    # The legacy extractor includes specialization codes in degree eligibility.
    assert ("Business Analytics", "BT4240") in specialization_modules
    assert "specialization:Machine Learning-based Analytics" in (
        degree_modules[("Business Analytics", "BT4240")].requirement_type
    )


def test_focus_areas_keep_their_kind_and_external_membership_note():
    plan = build_import_plan()
    focus_areas = {
        (item.degree, item.name): item
        for item in plan.entities.specializations
        if item.kind == "focus_area"
    }

    algorithms = focus_areas[("Computer Science", "Algorithms & Theory")]
    assert algorithms.source_order == 0
    assert algorithms.membership_note == "Focus-area membership catalog is linked externally."
    assert not any(
        item.specialization == "Algorithms & Theory"
        for item in plan.entities.specialization_modules
    )
