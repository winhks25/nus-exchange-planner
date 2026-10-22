"""Read-only inventory of the checked-in catalog sources (T010).

The script reports source checksums and exact, file-addressed data problems.
It never writes source files and never connects to a database.
"""

import argparse
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

# Direct script execution needs the backend directory on sys.path for `app`.
if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.course_codes import extract_course_codes, normalized_course_code
from app.models import COUNTRIES
from scripts.catalog_source import (
    MANIFEST_PATH,
    REPAIRS_PATH,
    REPO_ROOT,
    SourceError,
    SourceFile,
    extract_code_references,
    json_pointer,
    load_catalog_sources,
    read_source_file,
    repo_path,
    write_json,
)

DEFAULT_OUTPUT = REPO_ROOT / "plan" / "supabase-migration" / "data-audit.json"


def _clean_text(value: object) -> str | None:
    """Return a trimmed string, or None when the source value is not usable text."""

    if not isinstance(value, str):
        return None
    text = value.strip()
    return text or None


def _positive_number(value: object) -> float | None:
    """Accept finite positive JSON numbers, but never booleans or numeric strings."""

    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = float(value)
    return number if math.isfinite(number) and number > 0 else None


def _positive_int(value: object) -> int | None:
    """Accept positive JSON integers, but never booleans or floats."""

    if isinstance(value, bool) or not isinstance(value, int):
        return None
    return value if value > 0 else None


def _course_dict(row: dict[str, Any], key: str) -> dict[str, Any]:
    """Return a course object when the source row has the expected shape."""

    value = row.get(key)
    return value if isinstance(value, dict) else {}


def _issue(
    issues: list[dict[str, Any]],
    code: str,
    severity: str,
    file: str,
    pointer: str,
    message: str,
    mapping_index: int | None = None,
    context: dict[str, Any] | None = None,
) -> None:
    """Append one deterministic, source-addressed issue."""

    issues.append(
        {
            "code": code,
            "severity": severity,
            "file": file,
            "json_pointer": pointer,
            "mapping_index": mapping_index,
            "message": message,
            "context": context or {},
        }
    )


def _mapping_rows(source: SourceFile) -> list[Any] | None:
    """Return the raw mappings array, including malformed entries."""

    rows = source.parsed.get("mappings") if isinstance(source.parsed, dict) else None
    return rows if isinstance(rows, list) else None


def _university_name(source: SourceFile) -> str | None:
    """Return the source university name without inventing a fallback."""

    partner = source.parsed.get("partner_university") if isinstance(source.parsed, dict) else None
    return _clean_text(partner.get("name")) if isinstance(partner, dict) else None


def _edurec_id(source: SourceFile) -> str | None:
    """Return the partner's EduRec identifier when the source provides one."""

    partner = source.parsed.get("partner_university") if isinstance(source.parsed, dict) else None
    return _clean_text(partner.get("edurec_id")) if isinstance(partner, dict) else None


def _country_for_path(path: str) -> str | None:
    """Resolve the country folder beneath data/mapping to its display name."""

    parts = Path(path).parts
    if len(parts) < 4 or parts[0] != "data" or parts[1] != "mapping":
        return None
    return COUNTRIES.get(parts[2])


def _inventory_degrees(
    sources: list[SourceFile], issues: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], int]:
    """Inventory every degree and verify path-aware code extraction."""

    degrees: list[dict[str, Any]] = []
    seen_names: dict[str, str] = {}
    code_occurrences = 0
    for source in sources:
        if source.kind != "majors":
            continue
        majors = source.parsed.get("majors") if isinstance(source.parsed, dict) else None
        if not isinstance(majors, list):
            _issue(
                issues,
                "invalid_majors_shape",
                "error",
                source.path,
                "/majors",
                "The majors file must contain an array under /majors.",
            )
            continue
        for index, item in enumerate(majors):
            pointer = json_pointer("majors", index)
            if not isinstance(item, dict):
                _issue(
                    issues,
                    "invalid_degree_entry",
                    "error",
                    source.path,
                    pointer,
                    "Degree entry must be a JSON object.",
                    index,
                )
                continue
            name = _clean_text(item.get("name"))
            full_title = _clean_text(item.get("degree"))
            if name is None:
                _issue(
                    issues,
                    "missing_degree_name",
                    "error",
                    source.path,
                    f"{pointer}/name",
                    "Degree name is missing or blank.",
                    index,
                )
            if full_title is None:
                _issue(
                    issues,
                    "missing_degree_title",
                    "error",
                    source.path,
                    f"{pointer}/degree",
                    "Full degree title is missing or blank.",
                    index,
                )
            references = extract_code_references(item)
            codes = sorted({reference.code for reference in references})
            runtime_codes = extract_course_codes(item)
            code_extraction_match = frozenset(codes) == runtime_codes
            if not code_extraction_match:
                _issue(
                    issues,
                    "code_extraction_mismatch",
                    "error",
                    source.path,
                    pointer,
                    "Path-aware extraction does not match the runtime code extractor.",
                    index,
                    {
                        "runtime_codes": sorted(runtime_codes),
                        "path_codes": codes,
                    },
                )
            code_occurrences += len(codes)
            if name is not None:
                if name in seen_names:
                    _issue(
                        issues,
                        "duplicate_degree",
                        "error",
                        source.path,
                        f"{pointer}/name",
                        f"Degree {name!r} also appears at {seen_names[name]}.",
                        index,
                    )
                else:
                    seen_names[name] = f"{source.path}#{pointer}"
            degrees.append(
                {
                    "name": name,
                    "full_title": full_title,
                    "faculty": _clean_text(
                        source.parsed.get("school") if isinstance(source.parsed, dict) else None
                    ),
                    "source_order": index,
                    "file": source.path,
                    "code_count": len(codes),
                    "codes": codes,
                    "code_extraction_match": code_extraction_match,
                }
            )
    return degrees, code_occurrences


def _inventory_mappings(
    sources: list[SourceFile], issues: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Inventory every mapping row, including duplicates and metadata conflicts."""

    universities: list[dict[str, Any]] = []
    seen_universities: dict[str, str] = {}
    row_records: list[dict[str, Any]] = []
    nus_titles: dict[str, list[dict[str, Any]]] = defaultdict(list)
    partner_titles: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    partner_units: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    pair_occurrences: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    declared_total = 0
    raw_row_total = 0

    for source in sources:
        if source.kind != "mapping":
            continue
        university = _university_name(source)
        country = _country_for_path(source.path)
        rows = _mapping_rows(source)
        if rows is None:
            _issue(
                issues,
                "invalid_mappings_shape",
                "error",
                source.path,
                "/mappings",
                "The mapping file must contain an array under /mappings.",
            )
            rows = []
        declared = _positive_int(
            source.parsed.get("mapping_count") if isinstance(source.parsed, dict) else None
        )
        declared_total += declared or 0
        raw_row_total += len(rows)

        # A missing partner identity makes every row in the file unusable.
        if university is None:
            _issue(
                issues,
                "missing_partner_university",
                "error",
                source.path,
                "/partner_university/name",
                "Partner university name is missing or blank.",
            )
        elif university in seen_universities:
            _issue(
                issues,
                "duplicate_partner_university",
                "error",
                source.path,
                "/partner_university/name",
                f"University {university!r} also appears in {seen_universities[university]}.",
            )
        else:
            seen_universities[university] = source.path
        if country is None:
            _issue(
                issues,
                "unknown_country",
                "error",
                source.path,
                "",
                "Mapping path does not use a recognized country folder.",
            )
        if declared is None:
            _issue(
                issues,
                "missing_mapping_count",
                "warning",
                source.path,
                "/mapping_count",
                "Declared mapping_count is missing or not a positive integer.",
            )
        elif declared != len(rows):
            _issue(
                issues,
                "mapping_count_mismatch",
                "warning",
                source.path,
                "/mapping_count",
                f"Declared {declared} rows but found {len(rows)}.",
                context={"declared": declared, "actual": len(rows)},
            )

        # Measure every field once and reuse the normalized values for conflicts.
        for index, row in enumerate(rows):
            pointer = json_pointer("mappings", index)
            if not isinstance(row, dict):
                _issue(
                    issues,
                    "invalid_mapping_entry",
                    "error",
                    source.path,
                    pointer,
                    "Mapping row must be a JSON object.",
                    index,
                )
                continue
            nus_course = _course_dict(row, "nus_course")
            partner_course = _course_dict(row, "partner_course")
            raw_nus_code = _clean_text(nus_course.get("code"))
            raw_partner_code = _clean_text(partner_course.get("code"))
            nus_code = normalized_course_code(raw_nus_code) if raw_nus_code else None
            partner_code = raw_partner_code.upper() if raw_partner_code else None
            nus_title = _clean_text(nus_course.get("title"))
            partner_title = _clean_text(partner_course.get("title"))
            nus_units = _positive_number(nus_course.get("units"))
            partner_units_value = _positive_number(partner_course.get("units"))
            faculty = _clean_text(row.get("faculty"))
            page = _positive_int(row.get("source_page"))

            if nus_code is None:
                _issue(
                    issues,
                    "invalid_nus_code",
                    "error",
                    source.path,
                    f"{pointer}/nus_course/code",
                    f"NUS course code {nus_course.get('code')!r} is not a valid course code.",
                    index,
                    {"raw_code": nus_course.get("code")},
                )
            if nus_title is None:
                _issue(
                    issues,
                    "missing_nus_title",
                    "warning",
                    source.path,
                    f"{pointer}/nus_course/title",
                    "NUS course title is missing or blank.",
                    index,
                )
            if raw_partner_code is None:
                _issue(
                    issues,
                    "invalid_partner_code",
                    "error",
                    source.path,
                    f"{pointer}/partner_course/code",
                    "Partner course code is missing or blank.",
                    index,
                )
            if partner_title is None:
                _issue(
                    issues,
                    "missing_partner_title",
                    "warning",
                    source.path,
                    f"{pointer}/partner_course/title",
                    "Partner course title is missing or blank.",
                    index,
                )
            if partner_units_value is None:
                _issue(
                    issues,
                    "invalid_partner_units",
                    "warning",
                    source.path,
                    f"{pointer}/partner_course/units",
                    "Partner course units are missing, non-numeric, or not positive.",
                    index,
                )
            if faculty is None:
                _issue(
                    issues,
                    "missing_faculty",
                    "warning",
                    source.path,
                    f"{pointer}/faculty",
                    "Faculty metadata is missing or blank.",
                    index,
                )
            if page is None:
                _issue(
                    issues,
                    "missing_source_page",
                    "warning",
                    source.path,
                    f"{pointer}/source_page",
                    "Source page is missing or not a positive integer.",
                    index,
                )

            record = {
                "file": source.path,
                "mapping_index": index,
                "university": university,
                "country": country,
                "nus_code": nus_code,
                "raw_nus_code": raw_nus_code,
                "nus_title": nus_title,
                "nus_units": nus_units,
                "partner_code": partner_code,
                "raw_partner_code": raw_partner_code,
                "partner_title": partner_title,
                "partner_units": partner_units_value,
                "faculty": faculty,
                "source_page": page,
            }
            row_records.append(record)

            # Group non-null values for deterministic conflict detection.
            if nus_code is not None and nus_title is not None:
                nus_titles[nus_code].append(record)
            if partner_code is not None:
                if partner_title is not None:
                    partner_titles[(university or "", partner_code)].append(record)
                if partner_units_value is not None:
                    partner_units[(university or "", partner_code)].append(record)
                if nus_code is not None:
                    pair_occurrences[(university or "", nus_code, partner_code)].append(record)

        universities.append(
            {
                "name": university,
                "country": country,
                "source_order": len(universities),
                "file": source.path,
                "edurec_id": _edurec_id(source),
                "declared_mapping_count": declared,
                "actual_mapping_count": len(rows),
            }
        )

    _flag_conflicts(issues, nus_titles, "nus_title_conflict", "NUS")
    _flag_conflicts(issues, partner_titles, "partner_title_conflict", "Partner course")
    _flag_conflicts(issues, partner_units, "partner_unit_conflict", "Partner course units")
    _flag_repeated_pairs(issues, pair_occurrences)

    accepted = sum(1 for row in row_records if row["nus_code"] is not None)
    summary = {
        "raw_rows": raw_row_total,
        "malformed_mapping_rows": raw_row_total - len(row_records),
        "legacy_accepted_rows": accepted,
        "legacy_rejected_rows": raw_row_total - accepted,
        "missing_nus_titles": sum(1 for row in row_records if row["nus_title"] is None),
        "missing_partner_titles": sum(1 for row in row_records if row["partner_title"] is None),
        "missing_partner_units": sum(1 for row in row_records if row["partner_units"] is None),
        "declared_mapping_total": declared_total,
        "actual_mapping_total": raw_row_total,
        "valid_nus_codes": len({row["nus_code"] for row in row_records if row["nus_code"]}),
        "partner_codes": len(
            {
                (row["university"], row["partner_code"])
                for row in row_records
                if row["partner_code"]
            }
        ),
        "repeated_pairs": sum(1 for records in pair_occurrences.values() if len(records) > 1),
    }
    return row_records, {"universities": universities, "summary": summary}


def _flag_conflicts(
    issues: list[dict[str, Any]],
    groups: dict[Any, list[dict[str, Any]]],
    issue_code: str,
    label: str,
) -> None:
    """Flag each occurrence that disagrees with the group's first source value."""

    field_by_code = {
        "nus_title_conflict": "nus_title",
        "partner_title_conflict": "partner_title",
        "partner_unit_conflict": "partner_units",
    }
    field = field_by_code[issue_code]
    for key, records in groups.items():
        values = [record[field] for record in records]
        if len(set(values)) < 2:
            continue
        first = records[0][field]
        occurrences = [
            {
                "file": record["file"],
                "json_pointer": f"/mappings/{record['mapping_index']}/{_field_pointer(field)}",
                "value": record[field],
            }
            for record in records
        ]
        for record in records[1:]:
            if record[field] == first:
                continue
            pointer = f"/mappings/{record['mapping_index']}/{_field_pointer(field)}"
            _issue(
                issues,
                issue_code,
                "error",
                record["file"],
                pointer,
                f"{label} {key!r} has conflicting value {record[field]!r}; "
                f"first source value was {first!r}.",
                record["mapping_index"],
                {"values": sorted(set(values)), "occurrences": occurrences},
            )


def _field_pointer(field: str) -> str:
    """Map an internal field name to its location inside one source row."""

    return {
        "nus_title": "nus_course/title",
        "partner_title": "partner_course/title",
        "partner_units": "partner_course/units",
    }[field]


def _flag_repeated_pairs(
    issues: list[dict[str, Any]],
    groups: dict[tuple[str, str, str], list[dict[str, Any]]],
) -> None:
    """Flag duplicate university/NUS/partner pairs while preserving both rows."""

    for (university, nus_code, partner_code), records in groups.items():
        if len(records) < 2:
            continue
        occurrences = [
            {
                "file": record["file"],
                "json_pointer": f"/mappings/{record['mapping_index']}",
            }
            for record in records
        ]
        for record in records[1:]:
            _issue(
                issues,
                "repeated_pair",
                "warning",
                record["file"],
                f"/mappings/{record['mapping_index']}",
                f"Repeated pair {university} / {nus_code} / {partner_code}; "
                "the source positions must both be preserved.",
                record["mapping_index"],
                {"occurrences": occurrences},
            )


def build_inventory() -> dict[str, Any]:
    """Build the complete T010 document from the checked-in source files."""

    issues: list[dict[str, Any]] = []
    catalog_sources = load_catalog_sources()
    archive_sources = [read_source_file(MANIFEST_PATH)]
    if (REPO_ROOT / REPAIRS_PATH).is_file():
        archive_sources.append(read_source_file(REPO_ROOT / REPAIRS_PATH))

    degrees, degree_code_occurrences = _inventory_degrees(catalog_sources, issues)
    row_records, mapping_inventory = _inventory_mappings(catalog_sources, issues)
    summary = {
        **mapping_inventory["summary"],
        "degrees": len(degrees),
        "universities": len(mapping_inventory["universities"]),
        "degree_code_occurrences": degree_code_occurrences,
        "unique_degree_codes": len({code for degree in degrees for code in degree["codes"]}),
        "catalog_source_files": len(catalog_sources),
        "source_files": len(archive_sources) + len(catalog_sources),
    }

    # Compare recomputed counts with the Phase 1 baseline without trusting it blindly.
    expected = {
        "degrees": 6,
        "universities": 5,
        "raw_rows": 154,
        "legacy_accepted_rows": 147,
        "legacy_rejected_rows": 7,
        "missing_nus_titles": 7,
    }
    differences = {
        key: {"expected": value, "actual": summary.get(key)}
        for key, value in expected.items()
        if summary.get(key) != value
    }

    # Keep issue order stable so rerunning the audit produces identical bytes.
    issues.sort(key=lambda item: (item["file"], item["json_pointer"], item["code"]))
    issue_counts = Counter((item["code"], item["severity"]) for item in issues)
    source_files = [
        {
            "path": source.path,
            "kind": source.kind,
            "sha256": source.sha256,
            "byte_size": source.byte_size,
            "declared_mapping_count": next(
                (
                    university["declared_mapping_count"]
                    for university in mapping_inventory["universities"]
                    if university["file"] == source.path
                ),
                None,
            ),
            "actual_mapping_count": next(
                (
                    university["actual_mapping_count"]
                    for university in mapping_inventory["universities"]
                    if university["file"] == source.path
                ),
                None,
            ),
        }
        for source in sorted(archive_sources + catalog_sources, key=lambda item: item.path)
    ]
    return {
        "schema_version": 1,
        "scope": "T010 catalog source inventory",
        "source_files": source_files,
        "summary": {
            **summary,
            "issues_by_code": {
                code: {"severity": severity, "count": count}
                for (code, severity), count in sorted(issue_counts.items())
            },
        },
        "baseline": {
            "expected": expected,
            "matches": not differences,
            "differences": differences,
        },
        "issues": issues,
        "degrees": degrees,
        "universities": mapping_inventory["universities"],
        "mapping_rows": row_records,
        "repairs_file": REPAIRS_PATH if (REPO_ROOT / REPAIRS_PATH).is_file() else None,
    }


def main(argv: list[str] | None = None) -> int:
    """Write the inventory, or the corrected preview with ``--preview``."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--preview",
        action="store_true",
        help="write the corrected import preview and data delta report instead",
    )
    parser.add_argument(
        "--preview-output",
        type=Path,
        default=REPO_ROOT / "plan" / "supabase-migration" / "import-preview.json",
    )
    parser.add_argument(
        "--delta-output",
        type=Path,
        default=REPO_ROOT / "plan" / "supabase-migration" / "data-deltas.md",
    )
    parser.add_argument("--print-json", action="store_true", help="print the full document")
    args = parser.parse_args(argv)

    if args.preview:
        # Import lazily so the inventory remains usable without the preview module.
        from scripts.catalog_preview import build_preview, write_delta_report

        try:
            document = build_preview()
        except SourceError as exc:
            print(f"Catalog preview failed: {exc}", file=sys.stderr)
            return 1
        write_json(args.preview_output, document)
        write_delta_report(args.delta_output, document)
        if args.print_json:
            print(json.dumps(document, indent=2, sort_keys=True, ensure_ascii=False))
        summary = document["summary"]
        print(
            "Catalog preview: "
            f"{summary['active_rows']} active mappings, "
            f"{summary['repaired_rows']} repaired, "
            f"{summary['quarantined_rows']} quarantined; "
            f"{summary['nus_modules']} NUS modules, "
            f"{summary['partner_modules']} partner modules, "
            f"{summary['specializations']} specializations/focus areas"
        )
        print(f"Source checksum: {document['source_snapshot']['source_checksum_sha256']}")
        print(f"Repair checksum: {document['source_snapshot']['repair_checksum_sha256']}")
        print(f"Wrote {repo_path(args.preview_output)}")
        print(f"Wrote {repo_path(args.delta_output)}")
        return 0

    try:
        document = build_inventory()
    except SourceError as exc:
        print(f"Catalog inventory failed: {exc}", file=sys.stderr)
        return 1

    write_json(args.output, document)
    if args.print_json:
        print(json.dumps(document, indent=2, sort_keys=True, ensure_ascii=False))

    summary = document["summary"]
    print(
        "Catalog inventory: "
        f"{summary['degrees']} degrees, {summary['universities']} universities, "
        f"{summary['raw_rows']} mapping rows"
    )
    print(
        "Legacy loader: "
        f"{summary['legacy_accepted_rows']} accepted, {summary['legacy_rejected_rows']} rejected; "
        f"{summary['missing_nus_titles']} missing NUS titles"
    )
    for code, details in summary["issues_by_code"].items():
        print(f"  {code}: {details['count']} ({details['severity']})")
    print(f"Wrote {repo_path(args.output)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
