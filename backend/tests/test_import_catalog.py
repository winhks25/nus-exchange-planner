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


def test_plan_accounts_for_raw_rows_mappings_and_provenance():
    plan = build_import_plan()

    assert len(plan.archives) == 8
    assert len(plan.source_rows) == plan.summary["raw_rows"] == 154
    assert len(plan.mappings) == plan.summary["active_rows"] == 151
    assert len({item.key for item in plan.source_rows}) == 154
    assert len({item.key for item in plan.mappings}) == 151
    assert len(plan.issues) == 34
    assert len(plan.repairs) == 44


def test_repaired_rows_keep_raw_display_and_corrected_identity():
    plan = build_import_plan()
    rows = {item.key: item for item in plan.source_rows}
    mappings = {item.key: item for item in plan.mappings}
    key = ("data/mapping/canada/toronto.json", 50)

    assert rows[key].source_nus_code == "Foundations of Machine Le"
    assert rows[key].outcome == "repaired"
    assert mappings[key].nus_module_code == "CS3264"
    assert mappings[key].source_nus_title == "Foundations of Machine Learning"

    repaired = {
        (item.json_pointer, item.source_url): item
        for item in plan.repairs
        if item.mapping_index == 50
        and item.json_pointer == "/mappings/50/nus_course/code"
        and item.status == "verified"
    }
    assert repaired
    assert all(item.before_value == "Foundations of Machine Le" for item in repaired.values())
    assert all(item.after_value == "CS3264" for item in repaired.values())


def test_unresolved_membership_notes_are_retained_in_issue_messages():
    plan = build_import_plan()
    notes = [
        item.message
        for item in plan.issues
        if item.code == "specialization_memberships_missing" and "Note:" in item.message
    ]

    assert len(notes) == 6
    assert any(
        "See official curriculum page for prescribed course list." in message for message in notes
    )
    assert any("Optional; consult official specialisation list." in message for message in notes)


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
