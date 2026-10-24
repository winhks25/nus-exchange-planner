"""Focused checks for the read-only core snapshot helper."""

import copy

import pytest

from scripts import snapshot_core_data
from scripts.postgres_validation import DatabaseTarget
from scripts.snapshot_core_data import (
    CORE_TABLES,
    SnapshotError,
    _compare_snapshots,
    _protect_remote_output,
    _validate_target,
    read_snapshot,
)

pytestmark = pytest.mark.regression


def test_snapshot_captures_retained_rows_and_mapping_links(
    published_catalog: DatabaseTarget,
) -> None:
    snapshot, source_rows = read_snapshot(
        published_catalog.owner_url, include_source_row_ids=False
    )

    # Every allowlisted table records its columns, exact rows, and fingerprint.
    assert set(snapshot["tables"]) == set(CORE_TABLES)
    assert {
        table: detail["row_count"] for table, detail in snapshot["tables"].items()
    } == {
        "degrees": 6,
        "nus_modules": 152,
        "degree_modules": 226,
        "partner_universities": 5,
        "pu_modules": 142,
        "specializations": 19,
        "specialization_modules": 30,
        "module_mappings": 151,
    }
    assert snapshot["mapping_multiplicity"]["rows"] == 151
    assert all(
        detail["fingerprint"].startswith("sha256:")
        for detail in snapshot["tables"].values()
    )

    # On final schema without source_row_id column, requesting source_rows raises SnapshotError
    assert source_rows is None
    with pytest.raises(SnapshotError, match="source_row_id is absent"):
        read_snapshot(published_catalog.owner_url, include_source_row_ids=True)


def test_identical_snapshots_match_in_ids_mode(published_catalog: DatabaseTarget) -> None:
    baseline, _ = read_snapshot(published_catalog.owner_url)
    candidate, _ = read_snapshot(published_catalog.owner_url)

    result = _compare_snapshots(baseline, candidate, "ids")

    assert result["equal"] is True
    assert all(detail["equal"] for detail in result["tables"].values())
    assert result["sequences"]["equal"] is True
    assert result["tables"]["module_mappings"]["baseline_count"] == 151


def test_natural_key_mode_ignores_generated_ids(published_catalog: DatabaseTarget) -> None:
    baseline, _ = read_snapshot(published_catalog.owner_url)
    shifted = copy.deepcopy(baseline)

    # Offset every generated key and its foreign-key reference consistently.
    for table, key in (
        ("degrees", "id"),
        ("partner_universities", "id"),
        ("pu_modules", "id"),
        ("specializations", "id"),
        ("module_mappings", "id"),
        ("degree_modules", "degree_id"),
        ("pu_modules", "partner_university_id"),
        ("specializations", "degree_id"),
        ("specialization_modules", "specialization_id"),
        ("module_mappings", "pu_module_id"),
    ):
        for row in shifted["tables"][table]["rows"]:
            row[key] += 100

    ids_result = _compare_snapshots(baseline, shifted, "ids")
    natural_result = _compare_snapshots(baseline, shifted, "natural")

    assert ids_result["equal"] is False
    assert natural_result["equal"] is True
    assert all(detail["equal"] for detail in natural_result["tables"].values())


def test_remote_capture_requires_confirmation_and_private_output(tmp_path) -> None:
    remote_url = "postgresql://db.example.com:5432/catalog"

    with pytest.raises(SnapshotError, match="requires --target"):
        _validate_target(remote_url, None)
    with pytest.raises(SnapshotError, match="Target confirmation mismatch"):
        _validate_target(remote_url, "wrong")
    with pytest.raises(SnapshotError, match="outside the repository"):
        _protect_remote_output(
            snapshot_core_data.REPO_ROOT / "private-snapshot.json",
            "db.example.com",
            "--output",
        )
    assert _validate_target(remote_url, "db.example.com") == "db.example.com"
    assert _protect_remote_output(
        tmp_path / "snapshot.json", "db.example.com", "--output"
    ) is None
