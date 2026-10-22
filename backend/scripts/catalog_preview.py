"""Build the deterministic corrected import preview (T012).

The preview applies only source-addressed verified repairs. Unresolved rows stay
in the preview as quarantined source records, and every raw row remains available
for the importer's archive tables.
"""

import copy
import hashlib
import math
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.course_codes import extract_course_codes, normalized_course_code
from scripts.audit_catalog import build_inventory
from scripts.catalog_source import (
    MANIFEST_PATH,
    REPAIRS_PATH,
    REPO_ROOT,
    SourceError,
    SourceFile,
    combined_checksum,
    extract_code_references,
    json_pointer,
    load_catalog_sources,
    read_source_file,
    repo_path,
    write_json,
)

DEFAULT_PREVIEW = REPO_ROOT / "plan" / "supabase-migration" / "import-preview.json"
DEFAULT_DELTAS = REPO_ROOT / "plan" / "supabase-migration" / "data-deltas.md"
FACULTY_FALLBACK = "School of Computing"

FATAL_ROW_ISSUES = {
    "invalid_mapping_entry",
    "invalid_nus_code",
    "invalid_partner_code",
    "nus_title_conflict",
    "partner_title_conflict",
    "partner_unit_conflict",
}
REPAIRABLE_FIELDS = {
    "nus_course.code",
    "nus_course.title",
    "nus_course.units",
    "partner_course.code",
    "partner_course.title",
    "partner_course.units",
    "faculty",
    "source_page",
}


@dataclass(frozen=True)
class RepairSet:
    """Validated repairs and exact checksums for one import preview."""

    path: str | None
    sha256: str
    parsed: dict[str, Any]
    by_row: dict[tuple[str, int], list[dict[str, Any]]]
    verified: dict[tuple[str, int], dict[str, dict[str, Any]]]
    unresolved_rows: frozenset[tuple[str, int]]


def _empty_repair_set() -> RepairSet:
    return RepairSet(
        path=None,
        sha256=hashlib.sha256(b"").hexdigest(),
        parsed={},
        by_row={},
        verified={},
        unresolved_rows=frozenset(),
    )


def _clean_text(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    text = value.strip()
    return text or None


def _positive_number(value: object) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = float(value)
    return number if math.isfinite(number) and number > 0 else None


def _positive_int(value: object) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    return value if value > 0 else None


def _non_negative_int(value: object) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    return value if value >= 0 else None


def _course(row: dict[str, Any], key: str) -> dict[str, Any]:
    value = row.get(key)
    return value if isinstance(value, dict) else {}


def _get_path(document: Any, parts: list[str]) -> Any:
    target = document
    for part in parts:
        if not isinstance(target, dict) or part not in target:
            raise SourceError(f"Repair path is missing: {'.'.join(parts)}")
        target = target[part]
    return target


def _pointer_for_field(index: int, field: str) -> str:
    return f"/mappings/{index}/{field.replace('.', '/')}"


def _issue(
    code: str,
    severity: str,
    file: str,
    pointer: str,
    message: str,
    mapping_index: int | None = None,
    context: dict[str, Any] | None = None,
    status: str = "open",
    repair_id: str | None = None,
) -> dict[str, Any]:
    return {
        "code": code,
        "severity": severity,
        "file": file,
        "json_pointer": pointer,
        "mapping_index": mapping_index,
        "message": message,
        "context": context or {},
        "status": status,
        "repair_id": repair_id,
    }


def load_repairs(sources: dict[str, SourceFile]) -> RepairSet:
    """Load repairs, verify their source addresses and exact before values."""

    path = REPO_ROOT / REPAIRS_PATH
    if not path.is_file():
        return _empty_repair_set()
    source = read_source_file(path)
    if not isinstance(source.parsed, dict):
        raise SourceError("Repair file must contain a JSON object")
    declared_checksums = source.parsed.get("source_file_sha256")
    if not isinstance(declared_checksums, dict):
        raise SourceError("Repair file must contain source_file_sha256")
    for file_path, checksum in declared_checksums.items():
        if file_path not in sources:
            raise SourceError(f"Repair file cites unknown source: {file_path}")
        if sources[file_path].sha256 != checksum:
            raise SourceError(f"Repair source checksum mismatch: {file_path}")

    repairs = source.parsed.get("repairs")
    if not isinstance(repairs, list):
        raise SourceError("Repair file must contain a repairs array")

    by_row: dict[tuple[str, int], list[dict[str, Any]]] = defaultdict(list)
    verified: dict[tuple[str, int], dict[str, dict[str, Any]]] = defaultdict(dict)
    unresolved_rows: set[tuple[str, int]] = set()
    repair_ids: set[str] = set()
    verified_count = 0
    unresolved_count = 0

    for repair in repairs:
        if not isinstance(repair, dict):
            raise SourceError("Every repair entry must be a JSON object")
        repair_id = _clean_text(repair.get("repair_id"))
        if repair_id is None or repair_id in repair_ids:
            raise SourceError("Repair IDs must be present and unique")
        repair_ids.add(repair_id)
        file_path = _clean_text(repair.get("source_file"))
        if file_path is None or file_path not in sources:
            raise SourceError(f"Repair {repair_id} cites an unknown source file")
        mapping_index = _non_negative_int(repair.get("mapping_index"))
        if mapping_index is None:
            raise SourceError(f"Repair {repair_id} has an invalid mapping_index")
        source_checksum = _clean_text(repair.get("source_sha256"))
        if source_checksum != sources[file_path].sha256:
            raise SourceError(f"Repair {repair_id} source checksum mismatch")
        status = repair.get("status")
        if status not in {"verified", "unresolved"}:
            raise SourceError(f"Repair {repair_id} has an invalid status")
        fields = repair.get("fields")
        if not isinstance(fields, dict):
            raise SourceError(f"Repair {repair_id} must contain a fields object")

        rows = sources[file_path].parsed.get("mappings")
        if not isinstance(rows, list) or mapping_index >= len(rows):
            raise SourceError(f"Repair {repair_id} points outside the mapping rows")
        raw_row = rows[mapping_index]
        if not isinstance(raw_row, dict):
            raise SourceError(f"Repair {repair_id} points at a non-object row")

        key = (file_path, mapping_index)
        by_row[key].append(repair)
        if status == "unresolved":
            unresolved_count += 1
            unresolved_rows.add(key)
            if fields:
                raise SourceError(f"Unresolved repair {repair_id} must not carry fields")
            continue

        verified_count += 1
        if not fields:
            raise SourceError(f"Verified repair {repair_id} must carry at least one field")
        for field, change in fields.items():
            if field not in REPAIRABLE_FIELDS:
                raise SourceError(f"Repair {repair_id} uses unsupported field {field}")
            if not isinstance(change, dict):
                raise SourceError(f"Repair {repair_id} field {field} must be an object")
            pointer = change.get("json_pointer")
            if pointer != _pointer_for_field(mapping_index, field):
                raise SourceError(f"Repair {repair_id} has an inconsistent JSON pointer")
            if "before" not in change or "after" not in change:
                raise SourceError(f"Repair {repair_id} must include before and after")
            current = _get_path(raw_row, field.split("."))
            if current != change["before"]:
                raise SourceError(
                    f"Repair {repair_id} before mismatch at {pointer}: "
                    f"expected {change['before']!r}, found {current!r}"
                )
            if field in verified[key]:
                raise SourceError(f"Repair {repair_id} repeats field {field}")
            verified[key][field] = change
            if field == "nus_course.code":
                after = normalized_course_code(change["after"])
                if after is None:
                    raise SourceError(f"Repair {repair_id} after value is not a valid code")
            if (
                field in {"nus_course.title", "partner_course.title"}
                and _clean_text(change["after"]) is None
            ):
                raise SourceError(f"Repair {repair_id} after title is blank")
            if (
                field in {"nus_course.units", "partner_course.units"}
                and _positive_number(change["after"]) is None
            ):
                raise SourceError(f"Repair {repair_id} after units are not positive")

    summary = source.parsed.get("summary")
    if not isinstance(summary, dict):
        raise SourceError("Repair file must contain a summary object")
    if summary.get("verified_repairs") != verified_count:
        raise SourceError("Repair summary verified count does not match repairs")
    if summary.get("unresolved_repairs") != unresolved_count:
        raise SourceError("Repair summary unresolved count does not match repairs")
    if summary.get("affected_rows") != len(by_row):
        raise SourceError("Repair summary affected row count does not match repairs")

    return RepairSet(
        path=source.path,
        sha256=source.sha256,
        parsed=source.parsed,
        by_row=dict(by_row),
        verified=dict(verified),
        unresolved_rows=frozenset(unresolved_rows),
    )


def _apply_repairs(
    row: dict[str, Any], changes: dict[str, dict[str, Any]]
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Apply already-validated repairs without mutating the archived raw row."""

    corrected = copy.deepcopy(row)
    applied = []
    for field in sorted(changes):
        change = changes[field]
        target = corrected
        parts = field.split(".")
        for part in parts[:-1]:
            target = target[part]
        if target.get(parts[-1]) != change["before"]:
            raise SourceError(f"Repair before value changed at {change['json_pointer']}")
        target[parts[-1]] = change["after"]
        applied.append(
            {
                "field": field,
                "json_pointer": change["json_pointer"],
                "before": change["before"],
                "after": change["after"],
            }
        )
    return corrected, applied


def _repair_for_issue(
    issue: dict[str, Any], repairs: RepairSet
) -> dict[str, Any] | None:
    key = (issue["file"], issue["mapping_index"])
    for repair in repairs.by_row.get(key, []):
        for change in repair.get("fields", {}).values():
            if change.get("json_pointer") == issue["json_pointer"]:
                return repair
    return None


def _degree_item(source: SourceFile, index: int) -> dict[str, Any]:
    majors = source.parsed.get("majors") if isinstance(source.parsed, dict) else None
    if not isinstance(majors, list) or index >= len(majors):
        raise SourceError(f"Degree index {index} is missing from {source.path}")
    item = majors[index]
    if not isinstance(item, dict):
        raise SourceError(f"Degree {source.path}#{index} is not an object")
    return item


def _reference_mode(path: str, text: str) -> str:
    if "specialisations" in path.split("."):
        return "specialization"
    if "choose" in path.lower() or re.search(r"\bor\b", text, re.IGNORECASE):
        return "choice"
    return "listed"


def _requirement_groups(item: dict[str, Any]) -> list[dict[str, Any]]:
    """Group list-item code occurrences and keep each item's own mode."""

    groups: dict[str, dict[str, Any]] = {}
    references = extract_code_references(item)
    if frozenset(reference.code for reference in references) != extract_course_codes(item):
        raise SourceError("Degree code extraction does not match runtime semantics")
    for reference in references:
        group = groups.setdefault(
            reference.list_path,
            {
                "path": reference.list_path,
                "texts": [],
                "codes": set(),
                "members": [],
            },
        )
        if reference.text not in group["texts"]:
            group["texts"].append(reference.text)
        group["codes"].add(reference.code)
        group["members"].append(
            {
                "code": reference.code,
                "text": reference.text,
                "mode": _reference_mode(reference.list_path, reference.text),
            }
        )

    for group in groups.values():
        modes = {member["mode"] for member in group["members"]}
        group["mode"] = next(iter(modes)) if len(modes) == 1 else "mixed"
        group["codes"] = sorted(group["codes"])

    return sorted(groups.values(), key=lambda group: group["path"])


def _requirement_type(mode: str, path: str) -> str:
    if mode == "specialization":
        name = path.split("specialisations.", 1)[-1]
        return f"specialization:{name}"
    return f"{mode}:{path}"


def _degree_modules(
    codes: list[str], groups: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    labels: dict[str, list[str]] = defaultdict(list)
    texts: dict[str, list[str]] = defaultdict(list)
    for group in groups:
        for member in group["members"]:
            label = _requirement_type(member["mode"], group["path"])
            if label not in labels[member["code"]]:
                labels[member["code"]].append(label)
            if member["text"] not in texts[member["code"]]:
                texts[member["code"]].append(member["text"])

    modules = []
    for code in sorted(codes):
        code_labels = labels.get(code, ["unclassified:degree"])
        modules.append(
            {
                "code": code,
                "requirement_type": "; ".join(code_labels),
                "labels": code_labels,
                "source_texts": texts.get(code, []),
            }
        )
    return modules


def _specialization_records(
    item: dict[str, Any], degree_name: str, source: SourceFile, degree_index: int
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    specializations = []
    issues = []
    electives = item.get("electives")
    if not isinstance(electives, dict):
        return specializations, issues

    values = electives.get("specialisations")
    if isinstance(values, dict):
        for order, (name, value) in enumerate(values.items()):
            pointer = json_pointer(
                "majors", degree_index, "electives", "specialisations", name
            )
            memberships: list[str] = []
            note = None
            if isinstance(value, list):
                memberships = sorted(extract_course_codes(value))
            elif isinstance(value, str):
                note = value.strip()
                issues.append(
                    _issue(
                        "specialization_memberships_missing",
                        "warning",
                        source.path,
                        pointer,
                        "Source gives a note instead of an explicit membership list.",
                        None,
                        {"degree": degree_name, "specialization": name, "note": note},
                    )
                )
            else:
                issues.append(
                    _issue(
                        "specialization_memberships_missing",
                        "warning",
                        source.path,
                        pointer,
                        "Source specialization has no usable membership list.",
                        None,
                        {"degree": degree_name, "specialization": name},
                    )
                )
            specializations.append(
                {
                    "degree": degree_name,
                    "name": name,
                    "kind": "specialization",
                    "source_order": order,
                    "source_pointer": pointer,
                    "source_value": value,
                    "memberships": memberships,
                    "membership_note": note,
                }
            )

    focus_areas = electives.get("focus_areas")
    if isinstance(focus_areas, list):
        for order, value in enumerate(focus_areas):
            if not isinstance(value, str) or not value.strip():
                continue
            name = value.strip()
            pointer = f"/majors/{degree_index}/electives/focus_areas/{order}"
            issues.append(
                _issue(
                    "focus_area_memberships_missing",
                    "warning",
                    source.path,
                    pointer,
                    "Source lists a focus-area name but no explicit course membership.",
                    None,
                    {"degree": degree_name, "focus_area": name},
                )
            )
            specializations.append(
                {
                    "degree": degree_name,
                    "name": name,
                    "kind": "focus_area",
                    "source_order": order,
                    "source_pointer": pointer,
                    "source_value": None,
                    "memberships": [],
                    "membership_note": "Focus-area membership catalog is linked externally.",
                }
            )
    return specializations, issues


def _mapping_sources(
    sources: list[SourceFile], universities: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    university_by_file = {item["file"]: item for item in universities}
    records = []
    source_order = 0
    for source in sources:
        if source.kind != "mapping":
            continue
        university = university_by_file.get(source.path)
        rows = source.parsed.get("mappings") if isinstance(source.parsed, dict) else None
        if university is None:
            raise SourceError(f"Mapping source is missing university metadata: {source.path}")
        if not isinstance(rows, list):
            raise SourceError(f"Mapping source has no mappings array: {source.path}")
        for index, row in enumerate(rows):
            records.append(
                {
                    "file": source.path,
                    "mapping_index": index,
                    "source_order": source_order,
                    "university": university["name"],
                    "country": university["country"],
                    "raw_row": row,
                }
            )
            source_order += 1
    return records


def _row_status(
    record: dict[str, Any],
    corrected: dict[str, Any],
    applied: list[dict[str, Any]],
    row_issues: list[dict[str, Any]],
    repairs: RepairSet,
) -> tuple[str, list[dict[str, Any]]]:
    key = (record["file"], record["mapping_index"])
    fatal = []
    for issue in row_issues:
        repair = _repair_for_issue(issue, repairs)
        if repair is not None and repair["status"] == "verified":
            continue
        if issue["code"] in FATAL_ROW_ISSUES:
            fatal.append(issue)

    nus_code = normalized_course_code(_clean_text(_course(corrected, "nus_course").get("code")))
    partner_code = _clean_text(_course(corrected, "partner_course").get("code"))
    if nus_code is None:
        fatal.append(
            _issue(
                "invalid_nus_code",
                "error",
                record["file"],
                f"/mappings/{record['mapping_index']}/nus_course/code",
                "Corrected NUS course code is still invalid.",
                record["mapping_index"],
            )
        )
    if partner_code is None:
        fatal.append(
            _issue(
                "invalid_partner_code",
                "error",
                record["file"],
                f"/mappings/{record['mapping_index']}/partner_course/code",
                "Corrected partner course code is blank.",
                record["mapping_index"],
            )
        )
    if key in repairs.unresolved_rows:
        fatal.append(
            _issue(
                "unresolved_repair",
                "error",
                record["file"],
                f"/mappings/{record['mapping_index']}",
                "The row has an unresolved repair and stays quarantined.",
                record["mapping_index"],
            )
        )
    if fatal:
        unique = {
            (issue["code"], issue["json_pointer"]): issue for issue in fatal
        }
        return "quarantined", list(unique.values())
    return ("repaired" if applied else "accepted"), []


def _build_mapping(
    record: dict[str, Any],
    corrected: dict[str, Any],
    status: str,
    applied: list[dict[str, Any]],
    degree_names_by_code: dict[str, list[str]],
    quarantine_reasons: list[dict[str, Any]],
) -> dict[str, Any]:
    raw_row = record["raw_row"] if isinstance(record["raw_row"], dict) else {}
    raw_nus = _course(raw_row, "nus_course")
    raw_partner = _course(raw_row, "partner_course")
    nus = _course(corrected, "nus_course")
    partner = _course(corrected, "partner_course")
    nus_code = normalized_course_code(_clean_text(nus.get("code")))
    partner_code = _clean_text(partner.get("code"))
    partner_identity = partner_code.upper() if partner_code else None
    return {
        "source_file": record["file"],
        "mapping_index": record["mapping_index"],
        "source_order": record["source_order"],
        "university": record["university"],
        "country": record["country"],
        "nus_module_code": nus_code,
        "partner_module_code": partner_identity,
        "source_nus_code": raw_nus.get("code"),
        "source_partner_code": raw_partner.get("code"),
        "source_nus_title": _clean_text(raw_nus.get("title")),
        "source_nus_units": _positive_number(raw_nus.get("units")),
        "source_partner_title": _clean_text(raw_partner.get("title")),
        "source_partner_units": _positive_number(raw_partner.get("units")),
        "source_faculty": _clean_text(raw_row.get("faculty")),
        "source_page": _positive_int(raw_row.get("source_page")),
        "mapping_nus_title": _clean_text(nus.get("title")),
        "mapping_nus_units": _positive_number(nus.get("units")),
        "mapping_partner_title": _clean_text(partner.get("title")),
        "mapping_partner_units": _positive_number(partner.get("units")),
        "mapping_faculty": _clean_text(corrected.get("faculty")),
        "mapping_page": _positive_int(corrected.get("source_page")),
        "outcome": status,
        "degree_names": degree_names_by_code.get(nus_code, []) if nus_code else [],
        "applied_repairs": applied,
        "quarantine_reasons": quarantine_reasons,
        "source_row": record["raw_row"],
        "corrected_row": corrected,
    }


def _nus_modules(
    degree_names_by_code: dict[str, list[str]],
    mappings: list[dict[str, Any]],
    repairs: RepairSet,
) -> list[dict[str, Any]]:
    verified_titles = {
        title
        for changes in repairs.verified.values()
        for field, change in changes.items()
        if field == "nus_course.title"
        and (title := _clean_text(change["after"])) is not None
    }

    rows_by_code: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in mappings:
        if row["nus_module_code"]:
            rows_by_code[row["nus_module_code"]].append(row)

    records = []
    for code in sorted(set(degree_names_by_code) | set(rows_by_code)):
        titles = sorted(
            {
                title
                for row in rows_by_code.get(code, [])
                if (title := row["mapping_nus_title"]) is not None
            }
        )
        repair_titles = sorted(title for title in titles if title in verified_titles)
        name = repair_titles[0] if len(repair_titles) == 1 else None
        records.append(
            {
                "code": code,
                "name": name,
                "name_source": "verified_repair" if name else "unknown",
                "offering_faculty": None,
                "verified_units": None,
                "degree_names": degree_names_by_code.get(code, []),
                "source_titles": titles,
                "source_row_count": len(rows_by_code.get(code, [])),
            }
        )
    return records


def _partner_modules(
    mappings: list[dict[str, Any]], repairs: RepairSet
) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in mappings:
        if row["partner_module_code"]:
            groups[(row["university"], row["partner_module_code"])].append(row)

    records = []
    for (university, code), rows in sorted(groups.items()):
        titles = sorted(
            {row["mapping_partner_title"] for row in rows if row["mapping_partner_title"]}
        )
        units = sorted(
            {
                row["mapping_partner_units"]
                for row in rows
                if row["mapping_partner_units"] is not None
            }
        )
        verified_units = units[0] if len(units) == 1 and any(
            any(
                repair["status"] == "verified"
                and "partner_course.units" in repair.get("fields", {})
                for repair in repairs.by_row.get(
                    (row["source_file"], row["mapping_index"]), []
                )
            )
            for row in rows
        ) else None
        records.append(
            {
                "university": university,
                "code": code,
                "name": titles[0] if len(titles) == 1 else None,
                "name_source": "source" if len(titles) == 1 else "unknown",
                "verified_units": verified_units,
                "source_codes": sorted({row["source_partner_code"] for row in rows}),
                "source_titles": titles,
                "source_order": min(row["source_order"] for row in rows),
                "source_row_count": len(rows),
            }
        )
    return records


def _source_files(
    catalog_sources: list[SourceFile],
    repairs: RepairSet,
    universities: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    manifest = read_source_file(MANIFEST_PATH)
    counts = {
        item["file"]: item
        for item in universities
        if item.get("file") is not None
    }
    files = [manifest, *catalog_sources]
    if repairs.path is not None:
        files.append(read_source_file(REPO_ROOT / repairs.path))
    records = []
    for source in sorted(files, key=lambda item: item.path):
        counts_item = counts.get(source.path, {})
        records.append(
            {
                "path": source.path,
                "kind": source.kind,
                "sha256": source.sha256,
                "byte_size": source.byte_size,
                "declared_mapping_count": counts_item.get("declared_mapping_count"),
                "actual_mapping_count": counts_item.get("actual_mapping_count"),
            }
        )
    return records


def _delta_counts(
    audit: dict[str, Any], preview: dict[str, Any]
) -> dict[str, Any]:
    degrees = audit["degrees"]
    before_rows = [row for row in audit["mapping_rows"] if row["nus_code"]]
    after_rows = preview["mappings"]
    degree_codes = {degree["name"]: set(degree["codes"]) for degree in degrees}
    university_names = [item["name"] for item in audit["universities"]]

    pairs = []
    for degree in degrees:
        for university in university_names:
            before = [
                row
                for row in before_rows
                if row["university"] == university
                and row["nus_code"] in degree_codes[degree["name"]]
            ]
            after = [
                row
                for row in after_rows
                if row["university"] == university
                and row["nus_module_code"] in degree_codes[degree["name"]]
            ]
            pairs.append(
                {
                    "degree": degree["name"],
                    "university": university,
                    "before_mappings": len(before),
                    "after_mappings": len(after),
                    "before_distinct_nus": len({row["nus_code"] for row in before}),
                    "after_distinct_nus": len({row["nus_module_code"] for row in after}),
                    "before_partner_modules": len(
                        {(row["university"], row["partner_code"]) for row in before}
                    ),
                    "after_partner_modules": len(
                        {(row["university"], row["partner_module_code"]) for row in after}
                    ),
                }
            )

    for pair in pairs:
        pair["mapping_delta"] = pair["after_mappings"] - pair["before_mappings"]
        pair["distinct_nus_delta"] = pair["after_distinct_nus"] - pair["before_distinct_nus"]
        pair["partner_delta"] = (
            pair["after_partner_modules"] - pair["before_partner_modules"]
        )

    rank_changes = []
    for degree in degrees:
        rows = [pair for pair in pairs if pair["degree"] == degree["name"]]
        before_ranked = sorted(
            rows,
            key=lambda item: (-item["before_distinct_nus"], item["university"]),
        )
        after_ranked = sorted(
            rows,
            key=lambda item: (-item["after_distinct_nus"], item["university"]),
        )
        before_order = [item["university"] for item in before_ranked]
        after_order = [item["university"] for item in after_ranked]
        if before_order != after_order:
            rank_changes.append(
                {
                    "degree": degree["name"],
                    "before": before_order,
                    "after": after_order,
                }
            )

    return {
        "pairs": pairs,
        "rank_changes": rank_changes,
        "changed_pairs": [
            pair
            for pair in pairs
            if pair["mapping_delta"] or pair["distinct_nus_delta"] or pair["partner_delta"]
        ],
    }


def build_preview() -> dict[str, Any]:
    """Build the complete corrected preview from source files and repairs."""

    audit = build_inventory()
    catalog_sources = load_catalog_sources()
    sources_by_path = {source.path: source for source in catalog_sources}
    repairs = load_repairs(sources_by_path)
    issues = [dict(issue) for issue in audit["issues"]]
    for issue in issues:
        issue["status"] = "open"
        issue["repair_id"] = None

    issues_by_row: dict[tuple[str, int], list[dict[str, Any]]] = defaultdict(list)
    for issue in issues:
        if issue["mapping_index"] is not None:
            issues_by_row[(issue["file"], issue["mapping_index"])].append(issue)

    mapping_records = _mapping_sources(catalog_sources, audit["universities"])

    corrected_rows = []
    for record in mapping_records:
        key = (record["file"], record["mapping_index"])
        raw_row = record["raw_row"]
        if not isinstance(raw_row, dict):
            corrected_rows.append(
                {
                    **record,
                    "status": "quarantined",
                    "corrected": {},
                    "applied": [],
                    "fatal": [
                        _issue(
                            "invalid_mapping_entry",
                            "error",
                            record["file"],
                            f"/mappings/{record['mapping_index']}",
                            "Mapping row is not a JSON object.",
                            record["mapping_index"],
                        )
                    ],
                }
            )
            continue
        corrected, applied = _apply_repairs(raw_row, repairs.verified.get(key, {}))
        row_issues = issues_by_row.get(key, [])
        status, fatal = _row_status(record, corrected, applied, row_issues, repairs)
        corrected_rows.append(
            {
                **record,
                "status": status,
                "corrected": corrected,
                "applied": applied,
                "fatal": fatal,
            }
        )

    for row in corrected_rows:
        key = (row["file"], row["mapping_index"])
        if row["status"] == "quarantined":
            for issue in issues_by_row.get(key, []):
                issue["status"] = "quarantined"
            for fatal in row["fatal"]:
                fatal["status"] = "quarantined"
                if not any(
                    issue["code"] == fatal["code"]
                    and issue["json_pointer"] == fatal["json_pointer"]
                    for issue in issues_by_row.get(key, [])
                ):
                    issues.append(fatal)
        else:
            for issue in issues_by_row.get(key, []):
                repair = _repair_for_issue(issue, repairs)
                if repair is None:
                    continue
                issue["status"] = "resolved"
                issue["repair_id"] = repair.get("repair_id")

    degree_names_by_code: dict[str, list[str]] = defaultdict(list)
    degrees = []
    specializations = []
    specialization_issues = []
    for degree in audit["degrees"]:
        item = _degree_item(
            next(source for source in catalog_sources if source.path == degree["file"]),
            degree["source_order"],
        )
        groups = _requirement_groups(item)
        codes = sorted(extract_course_codes(item))
        for code in codes:
            degree_names_by_code[code].append(degree["name"])
        degrees.append(
            {
                "name": degree["name"],
                "full_title": degree["full_title"],
                "code": _clean_text(item.get("code")),
                "faculty": degree["faculty"] or FACULTY_FALLBACK,
                "source_order": degree["source_order"],
                "source_file": degree["file"],
                "curriculum_url": _clean_text(item.get("curriculum_url")),
                "degree_units": _positive_number(item.get("degree_units")),
                "common_curriculum_units": _positive_number(
                    item.get("common_curriculum_units")
                ),
                "unrestricted_elective_units": _positive_number(
                    item.get("unrestricted_elective_units")
                ),
                "programme_requirements_units": _positive_number(
                    item.get("programme_requirements_units")
                ),
                "source_detail": _clean_text(item.get("source_detail")),
                "codes": codes,
                "code_groups": groups,
                "degree_modules": _degree_modules(codes, groups),
            }
        )
        records, record_issues = _specialization_records(
            item,
            degree["name"],
            next(source for source in catalog_sources if source.path == degree["file"]),
            degree["source_order"],
        )
        specializations.extend(records)
        specialization_issues.extend(record_issues)

    issues.extend(specialization_issues)

    mappings = []
    quarantined = []
    for row in corrected_rows:
        record = _build_mapping(
            row,
            row["corrected"],
            row["status"],
            row["applied"],
            degree_names_by_code,
            row["fatal"],
        )
        if row["status"] == "quarantined":
            quarantined.append(record)
        else:
            mappings.append(record)

    nus_modules = _nus_modules(degree_names_by_code, mappings, repairs)
    partner_modules = _partner_modules(mappings, repairs)

    source_files = _source_files(catalog_sources, repairs, audit["universities"])
    manifest = read_source_file(MANIFEST_PATH)
    source_checksum = combined_checksum([manifest, *catalog_sources])
    repair_checksum = (
        repairs.sha256 if repairs.path is not None else hashlib.sha256(b"").hexdigest()
    )

    issues.sort(key=lambda item: (item["file"], item["json_pointer"], item["code"]))
    issue_counts = Counter(
        (item["code"], item["severity"], item["status"]) for item in issues
    )
    applied_count = sum(1 for row in corrected_rows if row["status"] == "repaired")
    accepted_count = sum(1 for row in corrected_rows if row["status"] == "accepted")
    quarantined_count = sum(
        1 for row in corrected_rows if row["status"] == "quarantined"
    )

    preview: dict[str, Any] = {
        "schema_version": 1,
        "scope": "T012 corrected import preview",
        "prepared_on": repairs.parsed.get("prepared_on"),
        "academic_year": repairs.parsed.get("academic_year")
        or (
            next(
                (
                    source.parsed.get("academic_year")
                    for source in catalog_sources
                    if source.kind == "majors"
                ),
                None,
            )
        ),
        "checksum_definition": (
            "source_checksum_sha256 = SHA-256 of sorted '<path>\\0<file-sha256>\\n' "
            "lines for the manifest and catalog files; repair_checksum_sha256 = "
            "SHA-256 of the exact repair file bytes, or SHA-256 of empty bytes."
        ),
        "source_snapshot": {
            "source_checksum_sha256": source_checksum,
            "repair_checksum_sha256": repair_checksum,
            "files": source_files,
            "repair_file": repairs.path,
        },
        "summary": {
            "degrees": len(degrees),
            "universities": len(audit["universities"]),
            "nus_modules": len(nus_modules),
            "partner_modules": len(partner_modules),
            "specializations": len(specializations),
            "degree_modules": sum(len(degree["degree_modules"]) for degree in degrees),
            "specialization_modules": sum(
                len(item["memberships"]) for item in specializations
            ),
            "source_rows": len(corrected_rows),
            "raw_rows": len(corrected_rows),
            "active_rows": len(mappings),
            "accepted_rows": accepted_count,
            "repaired_rows": applied_count,
            "quarantined_rows": quarantined_count,
            "verified_repairs_applied": sum(
                1
                for entries in repairs.by_row.values()
                for repair in entries
                if repair["status"] == "verified"
            ),
            "verified_repair_fields_applied": sum(
                len(row["applied"]) for row in corrected_rows
            ),
            "unresolved_repairs": len(repairs.unresolved_rows),
        },
        "issues_by_code": {
            f"{code}:{severity}:{status}": count
            for (code, severity, status), count in sorted(issue_counts.items())
        },
        "degrees": degrees,
        "universities": [
            {
                "name": item["name"],
                "country": item["country"],
                "city": None,
                "continent": None,
                "source_order": item["source_order"],
                "source_file": item["file"],
                "edurec_id": item["edurec_id"],
                "declared_mapping_count": item["declared_mapping_count"],
                "actual_mapping_count": item["actual_mapping_count"],
                "active_mapping_count": sum(
                    1 for row in mappings if row["university"] == item["name"]
                ),
                "quarantined_mapping_count": sum(
                    1 for row in quarantined if row["university"] == item["name"]
                ),
            }
            for item in audit["universities"]
        ],
        "nus_modules": nus_modules,
        "partner_modules": partner_modules,
        "specializations": specializations,
        "mappings": mappings,
        "quarantined_mappings": quarantined,
        "issues": issues,
        "repairs": repairs.parsed.get("repairs", []),
    }
    deltas = _delta_counts(audit, preview)
    preview["summary"]["changed_pair_count"] = len(deltas["changed_pairs"])
    preview["summary"]["rank_changes"] = len(deltas["rank_changes"])
    preview["deltas"] = deltas
    return preview


def _markdown_table(headers: list[str], rows: list[list[object]]) -> list[str]:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    lines.extend("| " + " | ".join(str(value) for value in row) + " |" for row in rows)
    return lines


def write_delta_report(path: Path, preview: dict[str, Any]) -> None:
    """Write the human-readable account of every count and ranking change."""

    summary = preview["summary"]
    deltas = preview["deltas"]
    lines = [
        "# Catalog import data deltas (T012)",
        "",
        (
            "Generated by `backend/scripts/audit_catalog.py --preview` from the "
            "checked-in sources and `data/repairs/catalog_repairs.json`."
        ),
        "",
        f"- Source checksum: `{preview['source_snapshot']['source_checksum_sha256']}`",
        f"- Repair checksum: `{preview['source_snapshot']['repair_checksum_sha256']}`",
        f"- Academic year: `{preview['academic_year']}`",
        "",
        "## Row outcomes",
        "",
        *_markdown_table(
            ["Measure", "Count"],
            [
                ["Raw source rows", summary["raw_rows"]],
                ["Active mappings", summary["active_rows"]],
                ["Accepted without repair", summary["accepted_rows"]],
                ["Repaired and active", summary["repaired_rows"]],
                ["Quarantined", summary["quarantined_rows"]],
                ["Verified repair fields applied", summary["verified_repair_fields_applied"]],
                ["Unresolved repair rows", summary["unresolved_repairs"]],
            ],
        ),
        "",
        "## Entity counts",
        "",
        *_markdown_table(
            ["Entity", "Count"],
            [
                ["Degrees", summary["degrees"]],
                ["Universities", summary["universities"]],
                ["NUS modules", summary["nus_modules"]],
                ["Partner modules", summary["partner_modules"]],
                ["Degree module memberships", summary["degree_modules"]],
                ["Specializations and focus areas", summary["specializations"]],
                ["Specialization memberships", summary["specialization_modules"]],
            ],
        ),
        "",
        "## Repair impact",
        "",
    ]

    verified_rows = []
    for repair in preview["repairs"]:
        changes = repair.get("fields", {})
        if repair["status"] == "verified":
            detail = "; ".join(
                f"`{field}` {change['before']!r} -> {change['after']!r}"
                for field, change in changes.items()
            )
            verified_rows.append(
                [
                    repair["repair_id"],
                    repair["mapping_index"],
                    "verified",
                    detail or "(no field changes)",
                ]
            )
        else:
            verified_rows.append(
                [
                    repair["repair_id"],
                    repair["mapping_index"],
                    "unresolved",
                    repair.get("reason", ""),
                ]
            )
    lines.extend(
        _markdown_table(["Repair", "Row", "Status", "Before -> after / reason"], verified_rows)
    )
    lines.extend(["", "## Pair counts", ""])
    pair_rows = []
    for pair in deltas["pairs"]:
        pair_rows.append(
            [
                pair["degree"],
                pair["university"],
                (
                    f"{pair['before_mappings']} -> {pair['after_mappings']} "
                    f"({pair['mapping_delta']:+d})"
                ),
                (
                    f"{pair['before_distinct_nus']} -> {pair['after_distinct_nus']} "
                    f"({pair['distinct_nus_delta']:+d})"
                ),
                (
                    f"{pair['before_partner_modules']} -> {pair['after_partner_modules']} "
                    f"({pair['partner_delta']:+d})"
                ),
            ]
        )
    lines.extend(
        _markdown_table(
            [
                "Degree",
                "University",
                "Mappings",
                "Distinct NUS modules",
                "Partner modules",
            ],
            pair_rows,
        )
    )
    lines.extend(["", "## Ranking changes", ""])
    if deltas["rank_changes"]:
        for change in deltas["rank_changes"]:
            lines.append(f"- **{change['degree']}**: {change['before']} -> {change['after']}")
    else:
        lines.append(
            "No recommendation ranking changes: repaired rows did not add a new NUS "
            "module to any degree/university pair."
        )

    lines.extend(["", "## Quarantined rows", ""])
    if preview["quarantined_mappings"]:
        quarantine_rows = []
        for row in preview["quarantined_mappings"]:
            reasons = sorted({item["code"] for item in row["quarantine_reasons"]})
            quarantine_rows.append(
                [
                    row["source_file"],
                    row["mapping_index"],
                    row["source_nus_code"],
                    row["source_partner_code"],
                    ", ".join(reasons),
                ]
            )
        lines.extend(
            _markdown_table(
                ["File", "Index", "Raw NUS code", "Partner code", "Reasons"],
                quarantine_rows,
            )
        )
    else:
        lines.append("None.")
    lines.extend(["", "## Repaired pair changes", ""])
    changed = deltas["changed_pairs"]
    if changed:
        for pair in changed:
            lines.append(
                f"- **{pair['degree']} / {pair['university']}**: mappings "
                f"{pair['before_mappings']} -> {pair['after_mappings']}, distinct NUS "
                f"{pair['before_distinct_nus']} -> {pair['after_distinct_nus']}, "
                f"partner modules {pair['before_partner_modules']} -> "
                f"{pair['after_partner_modules']}."
            )
    else:
        lines.append("None.")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    """Write the preview and its delta report, then print a compact summary."""

    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preview-output", type=Path, default=DEFAULT_PREVIEW)
    parser.add_argument("--delta-output", type=Path, default=DEFAULT_DELTAS)
    args = parser.parse_args(argv)
    try:
        preview = build_preview()
    except SourceError as exc:
        print(f"Catalog preview failed: {exc}", file=sys.stderr)
        return 1
    write_json(args.preview_output, preview)
    write_delta_report(args.delta_output, preview)
    summary = preview["summary"]
    print(
        "Catalog preview: "
        f"{summary['active_rows']} active mappings, "
        f"{summary['repaired_rows']} repaired, "
        f"{summary['quarantined_rows']} quarantined; "
        f"{summary['nus_modules']} NUS modules, "
        f"{summary['partner_modules']} partner modules, "
        f"{summary['specializations']} specializations/focus areas"
    )
    print(f"Source checksum: {preview['source_snapshot']['source_checksum_sha256']}")
    print(f"Repair checksum: {preview['source_snapshot']['repair_checksum_sha256']}")
    print(f"Wrote {repo_path(args.preview_output)}")
    print(f"Wrote {repo_path(args.delta_output)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
