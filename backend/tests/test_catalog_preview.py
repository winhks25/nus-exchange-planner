from scripts.catalog_preview import build_preview


def test_preview_applies_repairs_and_quarantines_unresolved_rows():
    preview = build_preview()
    summary = preview["summary"]

    assert summary["raw_rows"] == 154
    assert summary["active_rows"] == 151
    assert summary["accepted_rows"] == 146
    assert summary["repaired_rows"] == 5
    assert summary["quarantined_rows"] == 3
    assert summary["verified_repairs_applied"] == 5
    assert summary["verified_repair_fields_applied"] == 9
    assert summary["unresolved_repairs"] == 3
    assert summary["degrees"] == 6
    assert summary["universities"] == 5
    assert summary["nus_modules"] == 152
    assert summary["partner_modules"] == 142
    assert summary["degree_modules"] == 226
    assert summary["specializations"] == 19
    assert summary["specialization_modules"] == 30

    assert [row["mapping_index"] for row in preview["quarantined_mappings"]] == [48, 49, 53]
    assert {row["source_nus_code"] for row in preview["quarantined_mappings"]} == {
        "Software Engineering",
        "Discrete Structures",
        "Programming Methodology",
    }

    repaired = {
        row["mapping_index"]: row
        for row in preview["mappings"]
        if row["outcome"] == "repaired"
    }
    assert set(repaired) == {24, 50, 51, 52, 54}
    assert repaired[24]["source_partner_units"] == 3.0
    assert repaired[24]["mapping_partner_units"] == 0.5
    assert repaired[50]["source_nus_code"] == "Foundations of Machine Le"
    assert repaired[50]["nus_module_code"] == "CS3264"
    assert repaired[50]["source_nus_title"] is None
    assert repaired[50]["mapping_nus_title"] == "Foundations of Machine Learning"
    assert repaired[51]["nus_module_code"] == "BT4240"
    assert repaired[52]["nus_module_code"] == "IT2002"
    assert repaired[54]["nus_module_code"] == "CS2100"


def test_preview_preserves_requirement_modes_and_specialization_scope():
    preview = build_preview()
    degrees = {degree["name"]: degree for degree in preview["degrees"]}

    ba_modules = {item["code"]: item for item in degrees["Business Analytics"]["degree_modules"]}
    assert ba_modules["MA1521"]["labels"] == ["listed:required.core"]
    assert ba_modules["BT4101"]["labels"] == ["choice:required.core"]
    assert "specialization:Machine Learning-based Analytics" in ba_modules["BT4240"]["labels"]

    ai_modules = {
        item["code"]: item for item in degrees["Artificial Intelligence"]["degree_modules"]
    }
    assert ai_modules["CS3263"]["labels"] == ["listed:required.ai_foundations"]
    assert ai_modules["CS4243"]["labels"] == ["choice:required.perception_choose_one"]

    specializations = {
        (item["degree"], item["name"]): item for item in preview["specializations"]
    }
    financial = specializations[("Business Analytics", "Financial Analytics")]
    assert financial["kind"] == "specialization"
    assert len(financial["memberships"]) == 10
    assert financial["membership_note"] is None

    focus = specializations[("Computer Science", "Algorithms & Theory")]
    assert focus["kind"] == "focus_area"
    assert focus["memberships"] == []

    bais = specializations[
        ("Business Artificial Intelligence Systems", "AI Governance and Management")
    ]
    assert bais["memberships"] == []
    assert bais["membership_note"] == "See official curriculum page for prescribed course list."


def test_preview_deltas_account_for_every_repaired_pair():
    preview = build_preview()
    changed = {
        (item["degree"], item["university"]): item
        for item in preview["deltas"]["changed_pairs"]
    }
    assert set(changed) == {
        ("Artificial Intelligence", "University of Toronto"),
        ("Business Analytics", "University of Toronto"),
        ("Computer Science", "University of Toronto"),
        ("Information Security", "University of Toronto"),
    }
    assert all(item["mapping_delta"] == 1 for item in changed.values())
    assert all(item["distinct_nus_delta"] == 0 for item in changed.values())
    assert all(item["partner_delta"] == 1 for item in changed.values())
    assert preview["deltas"]["rank_changes"] == []
    assert preview["summary"]["changed_pair_count"] == 4
    assert preview["summary"]["rank_changes"] == 0


def test_preview_is_deterministic_and_addresses_its_sources():
    first = build_preview()
    second = build_preview()

    assert first == second
    assert first["source_snapshot"]["source_checksum_sha256"] == (
        "b393cd0f6b34adb506a23ba810d65c083238339fab0b76a236167fdbef6901b9"
    )
    assert first["source_snapshot"]["repair_checksum_sha256"] == (
        "61268be6b39c1effc644d72c8cc4787287cdbcafc86d32fb3c48814d48064a3e"
    )
    assert {item["path"] for item in first["source_snapshot"]["files"]} == {
        "backend/app/data_manifest.json",
        "data/majors/nus_soc_majors.json",
        "data/mapping/australia/west-au.json",
        "data/mapping/canada/toronto.json",
        "data/mapping/japan/kyoto.json",
        "data/mapping/korea/korea.json",
        "data/mapping/korea/yonsei.json",
        "data/repairs/catalog_repairs.json",
    }
