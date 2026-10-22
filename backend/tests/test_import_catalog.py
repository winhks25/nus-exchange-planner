import copy
from dataclasses import replace

import pytest

from scripts.import_catalog import (
    ImportRefused,
    SimulatedImportFailure,
    _catalog_counts,
    _connect,
    apply_plan,
    build_import_plan,
    dry_run,
)
from scripts.verify_catalog import Reconciler


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


def test_dry_run_and_apply_publish_the_expected_catalog(database):
    plan = build_import_plan()

    preview = dry_run(plan, database.url)
    assert preview["action"] == "would_import"
    assert preview["existing_counts"]["batches"] == 0

    result = apply_plan(plan, database.url)
    assert result["action"] == "imported"
    assert result["batch_id"] == 1

    with _connect(database.url) as connection:
        counts = _catalog_counts(connection)
    assert counts == {
        "degrees": 6,
        "nus_modules": 152,
        "degree_modules": 226,
        "specializations": 19,
        "specialization_modules": 30,
        "partner_universities": 5,
        "pu_modules": 142,
        "module_mappings": 151,
        "source_snapshots": 8,
        "source_rows": 154,
        "issues": 34,
        "repairs": 44,
        "batches": 1,
    }


def test_identical_rerun_is_a_noop(database):
    plan = build_import_plan()
    apply_plan(plan, database.url)

    result = apply_plan(plan, database.url)

    assert result["action"] == "noop"
    assert result["batch_id"] == 1
    with _connect(database.url) as connection:
        assert _catalog_counts(connection)["batches"] == 1


def test_changed_snapshot_is_refused_without_overwriting(database):
    plan = build_import_plan()
    apply_plan(plan, database.url)
    changed_preview = copy.deepcopy(plan.preview)
    changed_preview["source_snapshot"]["source_checksum_sha256"] = "0" * 64
    changed = replace(plan, preview=changed_preview)

    with pytest.raises(ImportRefused, match="different or partial catalog"):
        apply_plan(changed, database.url)

    with _connect(database.url) as connection:
        counts = _catalog_counts(connection)
    assert counts["batches"] == 1
    assert counts["source_rows"] == 154


def test_injected_failure_rolls_back_the_entire_import(database):
    plan = build_import_plan()

    with pytest.raises(SimulatedImportFailure):
        apply_plan(plan, database.url, simulate_failure=True)

    with _connect(database.url) as connection:
        counts = _catalog_counts(connection)
    assert all(value == 0 for value in counts.values())


def _reconciliation_report(database, plan):
    with _connect(database.url) as connection:
        connection.read_only = True
        with connection.transaction():
            return Reconciler(connection, plan).run()


def test_reconciliation_accepts_a_fresh_publication(database):
    plan = build_import_plan()
    apply_plan(plan, database.url)

    report = _reconciliation_report(database, plan)

    assert report["ok"] is True
    assert report["summary"]["failed"] == 0
    assert report["batch_id"] == 1


def test_reconciliation_reports_a_missing_repair_row(database):
    plan = build_import_plan()
    apply_plan(plan, database.url)
    database.execute(
        "delete from public.catalog_repairs where id = (select min(id) from public.catalog_repairs)"
    )

    report = _reconciliation_report(database, plan)

    assert report["ok"] is False
    failed = {check["name"]: check for check in report["checks"] if not check["ok"]}
    assert "catalog repairs" in failed
    assert failed["catalog repairs"]["expected"]["records"] == 44
    assert failed["catalog repairs"]["actual"]["records"] == 43
