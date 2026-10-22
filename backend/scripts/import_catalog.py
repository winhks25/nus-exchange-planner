"""Transform the checked-in catalog into normalized, importable records.

The importer consumes only the deterministic preview produced by T012. Entity
records are built and validated here before any database connection is opened,
so a malformed source fails without touching the target.
"""

import argparse
import hashlib
import json
import logging
import os
import re
import sys
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import psycopg
from psycopg.conninfo import conninfo_to_dict, make_conninfo
from psycopg.types.json import Jsonb

from app.course_codes import normalized_course_code
from scripts.catalog_preview import build_preview
from scripts.catalog_source import (
    SourceFile,
    combined_checksum,
    load_archive_sources,
    write_json,
)

IMPORT_LOCK_KEY = "nus-exchange-planner:catalog-import"
REQUIRED_TABLES = (
    "public.degrees",
    "public.nus_modules",
    "public.degree_modules",
    "public.specializations",
    "public.specialization_modules",
    "public.partner_universities",
    "public.pu_modules",
    "public.module_mappings",
    "public.catalog_import_batches",
    "public.catalog_source_snapshots",
    "public.catalog_source_rows",
    "public.catalog_issues",
    "public.catalog_repairs",
)


class CatalogImportError(RuntimeError):
    """Base class for importer failures that must not leak connection details."""


class ImportDataError(CatalogImportError):
    """Raised when the source cannot be represented without inventing data."""


class ImportRefused(CatalogImportError):
    """Raised when publishing would overwrite a different or partial catalog."""


class SimulatedImportFailure(CatalogImportError):
    """Raised by the isolated failure exercise to prove transaction rollback."""


SOURCE_URL_PATTERN = re.compile(r"^https?://\S+$")
SOURCE_OUTCOMES = frozenset({"accepted", "repaired", "quarantined"})
ACTIVE_OUTCOMES = frozenset({"accepted", "repaired"})


@dataclass(frozen=True)
class DegreeRecord:
    """One degree and its published presentation fields."""

    name: str
    full_title: str
    faculty: str
    source_order: int


@dataclass(frozen=True)
class NusModuleRecord:
    """One case-insensitive NUS course identity with optional verified metadata."""

    code: str
    name: str | None
    offering_faculty: str | None
    verified_units: float | None


@dataclass(frozen=True)
class DegreeModuleRecord:
    """One degree membership, including its source requirement mode."""

    degree: str
    module_code: str
    requirement_type: str | None


@dataclass(frozen=True)
class UniversityRecord:
    """One partner university in source order."""

    name: str
    country: str
    city: str | None
    continent: str | None
    source_order: int


@dataclass(frozen=True)
class PartnerModuleRecord:
    """One partner-scoped course identity with optional source metadata."""

    university: str
    code: str
    name: str | None
    verified_units: float | None


@dataclass(frozen=True)
class SourceRowRecord:
    """One immutable raw mapping row, addressed by file and array index."""

    source_file: str
    mapping_index: int
    source_order: int
    raw_row: dict[str, Any]
    outcome: str
    university: str
    source_nus_code: str
    source_partner_code: str
    source_nus_title: str | None
    source_partner_title: str | None
    source_nus_units: float | None
    source_partner_units: float | None
    source_faculty: str | None
    source_page: int | None

    @property
    def key(self) -> tuple[str, int]:
        return self.source_file, self.mapping_index


@dataclass(frozen=True)
class MappingRecord:
    """One active mapping with its own source-row presentation."""

    source_file: str
    mapping_index: int
    university: str
    nus_module_code: str
    partner_module_code: str
    source_order: int
    source_nus_title: str | None
    source_nus_units: float | None
    source_partner_title: str | None
    source_partner_units: float | None
    source_faculty: str | None
    source_page: int | None

    @property
    def key(self) -> tuple[str, int]:
        return self.source_file, self.mapping_index


@dataclass(frozen=True)
class IssueRecord:
    """One source-addressed issue with its resolution state."""

    source_file: str
    mapping_index: int | None
    json_pointer: str
    code: str
    severity: str
    message: str
    status: str


@dataclass(frozen=True)
class RepairRecord:
    """One evidence-bearing repair row keyed by source pointer and citation URL."""

    source_file: str
    mapping_index: int
    json_pointer: str
    before_value: Any
    after_value: Any
    source_url: str
    source_title: str | None
    accessed_on: date
    academic_year: str | None
    evidence: str
    status: str


@dataclass(frozen=True)
class SpecializationRecord:
    """One degree-scoped specialization or CS focus area."""

    degree: str
    name: str
    kind: str
    source_order: int
    membership_note: str | None


@dataclass(frozen=True)
class SpecializationModuleRecord:
    """One explicit specialization membership; never a degree requirement."""

    degree: str
    specialization: str
    module_code: str


@dataclass(frozen=True)
class CatalogEntities:
    """All normalized entities and memberships that are safe to publish."""

    degrees: tuple[DegreeRecord, ...]
    nus_modules: tuple[NusModuleRecord, ...]
    degree_modules: tuple[DegreeModuleRecord, ...]
    universities: tuple[UniversityRecord, ...]
    partner_modules: tuple[PartnerModuleRecord, ...]
    specializations: tuple[SpecializationRecord, ...]
    specialization_modules: tuple[SpecializationModuleRecord, ...]


@dataclass(frozen=True)
class ImportPlan:
    """Everything the importer needs for one exact source snapshot."""

    preview: dict[str, Any]
    entities: CatalogEntities
    archives: tuple[SourceFile, ...]
    source_rows: tuple[SourceRowRecord, ...]
    mappings: tuple[MappingRecord, ...]
    issues: tuple[IssueRecord, ...]
    repairs: tuple[RepairRecord, ...]

    @property
    def source_checksum(self) -> str:
        return str(self.preview["source_snapshot"]["source_checksum_sha256"])

    @property
    def repair_checksum(self) -> str:
        return str(self.preview["source_snapshot"]["repair_checksum_sha256"])

    @property
    def summary(self) -> dict[str, Any]:
        return self.preview["summary"]

    @property
    def academic_year(self) -> str | None:
        value = self.preview.get("academic_year")
        return value if isinstance(value, str) else None

    @property
    def prepared_on(self) -> str | None:
        value = self.preview.get("prepared_on")
        return value if isinstance(value, str) else None

    @property
    def repair_file(self) -> str | None:
        value = self.preview["source_snapshot"].get("repair_file")
        return value if isinstance(value, str) else None


@dataclass(frozen=True)
class PublicationState:
    """The target's publication state before a write is attempted."""

    action: str
    reason: str
    batch_id: int | None
    existing_counts: dict[str, int]


def build_import_plan() -> ImportPlan:
    """Build and validate the complete plan without opening a database connection."""

    preview = build_preview()
    entities = _build_entities(preview)
    archives = tuple(load_archive_sources())
    _validate_archives(preview, archives)
    source_rows = _build_source_rows(preview)
    mappings = _build_mappings(preview, entities)
    issues = _build_issues(preview)
    repairs = _build_repairs(preview, source_rows)
    _validate_provenance(preview, source_rows, mappings, issues, repairs)
    return ImportPlan(
        preview=preview,
        entities=entities,
        archives=archives,
        source_rows=source_rows,
        mappings=mappings,
        issues=issues,
        repairs=repairs,
    )


def _build_entities(preview: dict[str, Any]) -> CatalogEntities:
    """Convert preview dictionaries into typed, cross-checked entity records."""

    degrees = tuple(_degree_record(item) for item in preview["degrees"])
    nus_modules = tuple(_nus_module_record(item) for item in preview["nus_modules"])
    degree_modules = tuple(
        _degree_module_record(degree["name"], item)
        for degree in preview["degrees"]
        for item in degree["degree_modules"]
    )
    universities = tuple(_university_record(item) for item in preview["universities"])
    partner_modules = tuple(_partner_module_record(item) for item in preview["partner_modules"])
    specializations = tuple(_specialization_record(item) for item in preview["specializations"])
    specialization_modules = tuple(
        SpecializationModuleRecord(
            degree=item["degree"], specialization=item["name"], module_code=code
        )
        for item in preview["specializations"]
        for code in item["memberships"]
    )
    entities = CatalogEntities(
        degrees=degrees,
        nus_modules=nus_modules,
        degree_modules=degree_modules,
        universities=universities,
        partner_modules=partner_modules,
        specializations=specializations,
        specialization_modules=specialization_modules,
    )
    _validate_entities(entities)
    _validate_degree_eligibility(preview, entities)
    return entities


def _validate_degree_eligibility(preview: dict[str, Any], entities: CatalogEntities) -> None:
    """Prove degree memberships still equal the legacy extractor's code set."""

    memberships: dict[str, set[str]] = {}
    for item in entities.degree_modules:
        memberships.setdefault(item.degree, set()).add(item.module_code)
    for degree in preview["degrees"]:
        expected = {str(code) for code in degree["codes"]}
        actual = memberships.get(degree["name"], set())
        if actual != expected:
            missing = sorted(expected - actual)
            unexpected = sorted(actual - expected)
            raise ImportDataError(
                f"Degree eligibility changed for {degree['name']}: "
                f"missing={missing}, unexpected={unexpected}"
            )


def _degree_record(item: dict[str, Any]) -> DegreeRecord:
    """Build one degree while preserving its full title and source order."""

    return DegreeRecord(
        name=_required_text(item.get("name"), "degree name"),
        full_title=_required_text(item.get("full_title"), "degree full_title"),
        faculty=_required_text(item.get("faculty"), "degree faculty"),
        source_order=_required_int(item.get("source_order"), "degree source_order"),
    )


def _nus_module_record(item: dict[str, Any]) -> NusModuleRecord:
    """Build one NUS course identity, leaving unknown names and units null."""

    code = _required_code(item.get("code"), "NUS module code", course_code=True)
    return NusModuleRecord(
        code=code,
        name=_optional_text(item.get("name"), "NUS module name"),
        offering_faculty=_optional_text(item.get("offering_faculty"), "NUS offering_faculty"),
        verified_units=_optional_positive(item.get("verified_units"), "NUS units"),
    )


def _degree_module_record(degree: str, item: dict[str, Any]) -> DegreeModuleRecord:
    """Keep the legacy extractor's per-course requirement label exactly."""

    return DegreeModuleRecord(
        degree=_required_text(degree, "degree membership degree"),
        module_code=_required_code(
            item.get("code"), "degree membership module code", course_code=True
        ),
        requirement_type=_optional_text(
            item.get("requirement_type"), "degree membership requirement_type"
        ),
    )


def _university_record(item: dict[str, Any]) -> UniversityRecord:
    """Build one partner university without inventing city or continent."""

    return UniversityRecord(
        name=_required_text(item.get("name"), "university name"),
        country=_required_text(item.get("country"), "university country"),
        city=_optional_text(item.get("city"), "university city"),
        continent=_optional_text(item.get("continent"), "university continent"),
        source_order=_required_int(item.get("source_order"), "university source_order"),
    )


def _partner_module_record(item: dict[str, Any]) -> PartnerModuleRecord:
    """Build one partner-scoped identity; display codes stay in the raw archive."""

    return PartnerModuleRecord(
        university=_required_text(item.get("university"), "partner module university"),
        code=_required_code(item.get("code"), "partner module code"),
        name=_optional_text(item.get("name"), "partner module name"),
        verified_units=_optional_positive(item.get("verified_units"), "partner module units"),
    )


def _specialization_record(item: dict[str, Any]) -> SpecializationRecord:
    """Keep the source kind, order and note for one degree-scoped option."""

    kind = _required_text(item.get("kind"), "specialization kind")
    if kind not in {"specialization", "focus_area"}:
        raise ImportDataError(f"Unsupported specialization kind: {kind}")
    return SpecializationRecord(
        degree=_required_text(item.get("degree"), "specialization degree"),
        name=_required_text(item.get("name"), "specialization name"),
        kind=kind,
        source_order=_required_int(item.get("source_order"), "specialization source_order"),
        membership_note=_optional_text(
            item.get("membership_note"), "specialization membership_note"
        ),
    )


def _validate_archives(preview: dict[str, Any], archives: tuple[SourceFile, ...]) -> None:
    """Prove the archived bytes are exactly the snapshot the preview addressed."""

    expected = {item["path"]: item for item in preview["source_snapshot"]["files"]}
    actual = {item.path: item for item in archives}
    if set(actual) != set(expected):
        raise ImportDataError(
            "Archive paths do not match the preview: "
            f"missing={sorted(set(expected) - set(actual))}, "
            f"unexpected={sorted(set(actual) - set(expected))}"
        )
    for path, item in expected.items():
        source = actual[path]
        if source.sha256 != item["sha256"] or source.byte_size != item["byte_size"]:
            raise ImportDataError(f"Archived source changed before import: {path}")

    # The source checksum covers the manifest and catalog files, not the repair file.
    catalog_archives = [item for item in archives if item.kind != "repairs"]
    if combined_checksum(catalog_archives) != preview["source_snapshot"]["source_checksum_sha256"]:
        raise ImportDataError("Archived catalog checksum does not match the preview")

    repair_file = preview["source_snapshot"]["repair_file"]
    repair_archives = [item for item in archives if item.kind == "repairs"]
    if repair_file is None:
        if repair_archives:
            raise ImportDataError("Unexpected repair archive for a repair-free preview")
        if preview["source_snapshot"]["repair_checksum_sha256"] != hashlib.sha256(b"").hexdigest():
            raise ImportDataError("Repair-free preview has a non-empty repair checksum")
        return
    matching = [item for item in repair_archives if item.path == repair_file]
    if len(matching) != 1:
        raise ImportDataError(f"Expected exactly one repair archive for {repair_file}")
    if matching[0].sha256 != preview["source_snapshot"]["repair_checksum_sha256"]:
        raise ImportDataError("Archived repair checksum does not match the preview")


def _build_source_rows(preview: dict[str, Any]) -> tuple[SourceRowRecord, ...]:
    """Flatten every raw row while retaining its original position and display values."""

    records = []
    for row in [*preview["mappings"], *preview["quarantined_mappings"]]:
        raw_row = row.get("source_row")
        if not isinstance(raw_row, dict):
            raise ImportDataError(
                f"Raw row {row.get('source_file')}#{row.get('mapping_index')} is not an object"
            )
        nus = _raw_course(raw_row, "nus_course", row)
        partner = _raw_course(raw_row, "partner_course", row)
        outcome = _required_text(row.get("outcome"), "source row outcome")
        if outcome not in SOURCE_OUTCOMES:
            raise ImportDataError(f"Unsupported source row outcome: {outcome}")
        records.append(
            SourceRowRecord(
                source_file=_required_text(row.get("source_file"), "source row file"),
                mapping_index=_required_int(row.get("mapping_index"), "source row mapping_index"),
                source_order=_required_int(row.get("source_order"), "source row source_order"),
                raw_row=raw_row,
                outcome=outcome,
                university=_required_text(row.get("university"), "source row university"),
                source_nus_code=_required_text(nus.get("code"), "raw NUS course code"),
                source_partner_code=_required_text(partner.get("code"), "raw partner course code"),
                source_nus_title=_optional_text(nus.get("title"), "raw NUS course title"),
                source_partner_title=_optional_text(
                    partner.get("title"), "raw partner course title"
                ),
                source_nus_units=_optional_positive(nus.get("units"), "raw NUS course units"),
                source_partner_units=_optional_positive(
                    partner.get("units"), "raw partner course units"
                ),
                source_faculty=_optional_text(raw_row.get("faculty"), "raw faculty"),
                source_page=_optional_positive_int(raw_row.get("source_page"), "raw source_page"),
            )
        )
    return tuple(sorted(records, key=lambda item: item.key))


def _raw_course(raw_row: dict[str, Any], key: str, row: dict[str, Any]) -> dict[str, Any]:
    """Return one required raw course object or fail with its source address."""

    value = raw_row.get(key)
    if not isinstance(value, dict):
        raise ImportDataError(
            f"Raw row {row.get('source_file')}#{row.get('mapping_index')} has no {key} object"
        )
    return value


def _build_mappings(
    preview: dict[str, Any], entities: CatalogEntities
) -> tuple[MappingRecord, ...]:
    """Build active mappings from corrected rows while keeping row presentation."""

    nus_codes = {item.code for item in entities.nus_modules}
    partner_keys = {(item.university, item.code) for item in entities.partner_modules}
    records = []
    for row in preview["mappings"]:
        nus_code = _required_code(row.get("nus_module_code"), "mapping NUS code")
        partner_code = _required_code(row.get("partner_module_code"), "mapping partner code")
        university = _required_text(row.get("university"), "mapping university")
        if nus_code not in nus_codes:
            raise ImportDataError(f"Mapping cites unknown NUS module: {nus_code}")
        if (university, partner_code) not in partner_keys:
            raise ImportDataError(
                f"Mapping cites unknown partner module: {university}/{partner_code}"
            )
        records.append(
            MappingRecord(
                source_file=_required_text(row.get("source_file"), "mapping source file"),
                mapping_index=_required_int(row.get("mapping_index"), "mapping source index"),
                university=university,
                nus_module_code=nus_code,
                partner_module_code=partner_code,
                source_order=_required_int(row.get("source_order"), "mapping source_order"),
                source_nus_title=_optional_text(row.get("mapping_nus_title"), "mapping NUS title"),
                source_nus_units=_optional_positive(
                    row.get("mapping_nus_units"), "mapping NUS units"
                ),
                source_partner_title=_optional_text(
                    row.get("mapping_partner_title"), "mapping partner title"
                ),
                source_partner_units=_optional_positive(
                    row.get("mapping_partner_units"), "mapping partner units"
                ),
                source_faculty=_optional_text(row.get("mapping_faculty"), "mapping faculty"),
                source_page=_optional_positive_int(row.get("mapping_page"), "mapping source_page"),
            )
        )
    return tuple(sorted(records, key=lambda item: item.key))


def _build_issues(preview: dict[str, Any]) -> tuple[IssueRecord, ...]:
    """Carry every source issue, including membership notes, into the import plan."""

    records = []
    for issue in preview["issues"]:
        context = issue.get("context") if isinstance(issue.get("context"), dict) else {}
        message = _required_text(issue.get("message"), "issue message")
        if issue.get("code") == "specialization_memberships_missing" and context.get("note"):
            message = f"{message} Note: {context['note']}"
        mapping_index = issue.get("mapping_index")
        if mapping_index is not None:
            mapping_index = _required_int(mapping_index, "issue mapping_index")
        pointer = issue.get("json_pointer")
        if pointer is None:
            pointer = ""
        if not isinstance(pointer, str) or (pointer and not pointer.startswith("/")):
            raise ImportDataError(f"Issue has an invalid JSON pointer: {pointer!r}")
        severity = _required_text(issue.get("severity"), "issue severity")
        if severity not in {"warning", "error"}:
            raise ImportDataError(f"Unsupported issue severity: {severity}")
        status = _required_text(issue.get("status"), "issue status")
        if status not in {"open", "resolved", "quarantined"}:
            raise ImportDataError(f"Unsupported issue status: {status}")
        records.append(
            IssueRecord(
                source_file=_required_text(issue.get("file"), "issue source file"),
                mapping_index=mapping_index,
                json_pointer=pointer,
                code=_required_text(issue.get("code"), "issue code"),
                severity=severity,
                message=message,
                status=status,
            )
        )
    return tuple(sorted(records, key=lambda item: (item.source_file, item.json_pointer, item.code)))


def _build_repairs(
    preview: dict[str, Any], source_rows: tuple[SourceRowRecord, ...]
) -> tuple[RepairRecord, ...]:
    """Group evidence by source pointer and citation URL without losing any quote."""

    rows_by_key = {item.key: item for item in source_rows}
    grouped: dict[tuple[str, int, str, str], dict[str, Any]] = {}

    def add_evidence(
        key: tuple[str, int],
        pointer: str,
        before: Any,
        after: Any,
        status: str,
        evidence: dict[str, Any],
    ) -> None:
        url = _required_text(evidence.get("url"), "repair evidence URL")
        if not SOURCE_URL_PATTERN.fullmatch(url):
            raise ImportDataError(f"Repair evidence URL is invalid: {url}")
        entry = grouped.setdefault(
            (key[0], key[1], pointer, url),
            {
                "before": before,
                "after": after,
                "status": status,
                "quotes": [],
                "titles": [],
                "years": [],
                "dates": [],
            },
        )
        quote = _required_text(evidence.get("quote"), "repair evidence quote")
        if quote not in entry["quotes"]:
            entry["quotes"].append(quote)
        title = _optional_text(evidence.get("page_title"), "repair page title")
        if title and title not in entry["titles"]:
            entry["titles"].append(title)
        year = _optional_text(evidence.get("academic_year"), "repair academic year")
        if year and year not in entry["years"]:
            entry["years"].append(year)
        try:
            accessed = date.fromisoformat(
                _required_text(evidence.get("accessed_on"), "repair accessed_on")
            )
        except ValueError:
            raise ImportDataError("Repair accessed_on must be an ISO date") from None
        entry["dates"].append(accessed)

    for repair in preview["repairs"]:
        key = (
            _required_text(repair.get("source_file"), "repair source file"),
            _required_int(repair.get("mapping_index"), "repair mapping_index"),
        )
        if key not in rows_by_key:
            raise ImportDataError(f"Repair cites an unknown source row: {key}")
        status = _required_text(repair.get("status"), "repair status")
        if status not in {"verified", "unresolved"}:
            raise ImportDataError(f"Unsupported repair status: {status}")
        evidence_entries = repair.get("evidence")
        if not isinstance(evidence_entries, list) or not evidence_entries:
            raise ImportDataError(f"Repair {key} has no evidence")
        fields = repair.get("fields") if isinstance(repair.get("fields"), dict) else {}
        if status == "verified":
            for field, change in fields.items():
                if not isinstance(change, dict):
                    raise ImportDataError(f"Repair {key} field {field} is not an object")
                pointer = _required_text(change.get("json_pointer"), "repair JSON pointer")
                for evidence in evidence_entries:
                    add_evidence(
                        key,
                        pointer,
                        change.get("before"),
                        change.get("after"),
                        status,
                        evidence,
                    )
        else:
            unresolved_fields = repair.get("unresolved_fields")
            if not isinstance(unresolved_fields, list) or not unresolved_fields:
                raise ImportDataError(f"Unresolved repair {key} lists no fields")
            raw_row = rows_by_key[key].raw_row
            for field in unresolved_fields:
                if not isinstance(field, str) or not field:
                    raise ImportDataError(f"Repair {key} has an invalid field")
                pointer = f"/mappings/{key[1]}/{field.replace('.', '/')}"
                parts = field.split(".")
                for evidence in evidence_entries:
                    add_evidence(
                        key,
                        pointer,
                        _lookup_path(raw_row, parts),
                        None,
                        status,
                        evidence,
                    )

    records = []
    for (source_file, mapping_index, pointer, url), entry in sorted(grouped.items()):
        if not entry["quotes"] or not entry["dates"]:
            raise ImportDataError(f"Repair evidence is incomplete at {pointer}")
        records.append(
            RepairRecord(
                source_file=source_file,
                mapping_index=mapping_index,
                json_pointer=pointer,
                before_value=entry["before"],
                after_value=entry["after"],
                source_url=url,
                source_title=entry["titles"][0] if entry["titles"] else None,
                accessed_on=max(entry["dates"]),
                academic_year="; ".join(entry["years"]) or None,
                evidence="\n\n".join(entry["quotes"]),
                status=entry["status"],
            )
        )
    return tuple(records)


def _lookup_path(document: Any, parts: list[str]) -> Any:
    """Return a nested raw value or null when the path does not exist."""

    target = document
    for part in parts:
        if not isinstance(target, dict) or part not in target:
            return None
        target = target[part]
    return target


def _validate_provenance(
    preview: dict[str, Any],
    source_rows: tuple[SourceRowRecord, ...],
    mappings: tuple[MappingRecord, ...],
    issues: tuple[IssueRecord, ...],
    repairs: tuple[RepairRecord, ...],
) -> None:
    """Account for every raw row and one-to-one active mapping before publication."""

    _unique_values((item.key for item in source_rows), "source row identities")
    _unique_values((item.key for item in mappings), "active mapping identities")
    _unique_values(
        ((item.source_file, item.mapping_index, item.json_pointer, item.code) for item in issues),
        "issue identities",
    )
    _unique_values(
        (
            (item.source_file, item.mapping_index, item.json_pointer, item.source_url)
            for item in repairs
        ),
        "repair identities",
    )

    summary = preview["summary"]
    outcome_counts = {
        outcome: sum(1 for item in source_rows if item.outcome == outcome)
        for outcome in SOURCE_OUTCOMES
    }
    if len(source_rows) != summary["raw_rows"]:
        raise ImportDataError("Source row count does not match the preview summary")
    if len(mappings) != summary["active_rows"]:
        raise ImportDataError("Active mapping count does not match the preview summary")
    if outcome_counts["accepted"] != summary["accepted_rows"]:
        raise ImportDataError("Accepted row count does not match the preview summary")
    if outcome_counts["repaired"] != summary["repaired_rows"]:
        raise ImportDataError("Repaired row count does not match the preview summary")
    if outcome_counts["quarantined"] != summary["quarantined_rows"]:
        raise ImportDataError("Quarantined row count does not match the preview summary")

    # Active rows must have exactly one mapping; quarantined rows must have none.
    row_by_key = {item.key: item for item in source_rows}
    mapping_keys = {item.key for item in mappings}
    for item in source_rows:
        if item.outcome in ACTIVE_OUTCOMES and item.key not in mapping_keys:
            raise ImportDataError(f"Active source row has no mapping: {item.key}")
        if item.outcome == "quarantined" and item.key in mapping_keys:
            raise ImportDataError(f"Quarantined source row has a mapping: {item.key}")
    for key in mapping_keys:
        if row_by_key[key].outcome not in ACTIVE_OUTCOMES:
            raise ImportDataError(f"Mapping is not backed by an active row: {key}")

    # Every quarantine and every applied repair must have a matching source address.
    issue_keys = {(item.source_file, item.mapping_index) for item in issues}
    for item in source_rows:
        if item.outcome == "quarantined" and item.key not in issue_keys:
            raise ImportDataError(f"Quarantined source row has no issue: {item.key}")
    verified_keys = {
        (item.source_file, item.mapping_index) for item in repairs if item.status == "verified"
    }
    for item in mappings:
        if item.key in verified_keys and row_by_key[item.key].outcome != "repaired":
            raise ImportDataError(f"Repair cites a row not marked repaired: {item.key}")
    for item in repairs:
        key = (item.source_file, item.mapping_index)
        if key not in row_by_key:
            raise ImportDataError(f"Repair cites an unknown source row: {key}")
        if item.status == "unresolved" and row_by_key[key].outcome != "quarantined":
            raise ImportDataError(f"Unresolved repair row is not quarantined: {key}")


def _validate_entities(entities: CatalogEntities) -> None:
    """Reject duplicate identities or broken references before database work."""

    degree_names = _unique_values((item.name for item in entities.degrees), "degree names")
    _unique_values((item.source_order for item in entities.degrees), "degree source orders")
    nus_codes = _unique_values((item.code for item in entities.nus_modules), "NUS module codes")
    university_names = _unique_values(
        (item.name for item in entities.universities), "university names"
    )
    _unique_values(
        (item.source_order for item in entities.universities),
        "university source orders",
    )
    _unique_values(
        ((item.university, item.code) for item in entities.partner_modules),
        "partner module identities",
    )

    # Every membership, mapping code and partner course must resolve inside the plan.
    membership_keys = _unique_values(
        ((item.degree, item.module_code) for item in entities.degree_modules),
        "degree module memberships",
    )
    for degree, module_code in membership_keys:
        if degree not in degree_names:
            raise ImportDataError(f"Degree membership cites unknown degree: {degree}")
        if module_code not in nus_codes:
            raise ImportDataError(f"Degree membership cites unknown NUS module: {module_code}")

    for item in entities.partner_modules:
        if item.university not in university_names:
            raise ImportDataError(f"Partner module cites unknown university: {item.university}")

    # Specialization memberships are exported separately and never merged into degree_modules.
    specialization_keys = _unique_values(
        ((item.degree, item.name) for item in entities.specializations),
        "specialization identities",
    )
    _unique_values(
        ((item.degree, item.source_order) for item in entities.specializations),
        "specialization source orders",
    )
    for degree, _ in specialization_keys:
        if degree not in degree_names:
            raise ImportDataError(f"Specialization cites unknown degree: {degree}")

    membership_keys = _unique_values(
        (
            (item.degree, item.specialization, item.module_code)
            for item in entities.specialization_modules
        ),
        "specialization memberships",
    )
    for degree, specialization, module_code in membership_keys:
        if (degree, specialization) not in specialization_keys:
            raise ImportDataError(
                f"Specialization membership cites unknown option: {degree}/{specialization}"
            )
        if module_code not in nus_codes:
            raise ImportDataError(
                f"Specialization membership cites unknown NUS module: {module_code}"
            )


def _unique_values(values: Any, label: str) -> set[Any]:
    """Collect values and raise on duplicates instead of relying on a database error."""

    collected: set[Any] = set()
    for value in values:
        if value in collected:
            raise ImportDataError(f"Duplicate {label}: {value!r}")
        collected.add(value)
    return collected


def _required_text(value: object, label: str) -> str:
    """Return trimmed nonblank text or fail with a source-specific message."""

    text = _optional_text(value, label)
    if text is None:
        raise ImportDataError(f"Missing or blank {label}")
    return text


def _optional_text(value: object, label: str) -> str | None:
    """Normalize optional text and reject non-string source values."""

    if value is None:
        return None
    if not isinstance(value, str):
        raise ImportDataError(f"{label} must be text, got {type(value).__name__}")
    text = value.strip()
    return text or None


def _required_int(value: object, label: str) -> int:
    """Return a non-negative integer without coercing booleans or strings."""

    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ImportDataError(f"{label} must be a non-negative integer")
    return value


def _optional_positive_int(value: object, label: str) -> int | None:
    """Return a positive source page number or null without coercing strings."""

    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ImportDataError(f"{label} must be a positive integer or null")
    return value


def _required_code(value: object, label: str, *, course_code: bool = False) -> str:
    """Return an uppercase code; NUS identities must also match the legacy pattern."""

    code = _required_text(value, label)
    if code != code.upper():
        raise ImportDataError(f"{label} must already be uppercase: {code}")
    if course_code and normalized_course_code(code) != code:
        raise ImportDataError(f"{label} is not a valid course code: {code}")
    return code


def _optional_positive(value: object, label: str) -> float | None:
    """Return a verified positive number, preserving unknown values as null."""

    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ImportDataError(f"{label} must be numeric or null")
    number = float(value)
    if number <= 0:
        raise ImportDataError(f"{label} must be positive or null")
    return number


def _project_ref_from_url(database_url: str) -> str | None:
    """Read a Supabase project ref from the host and never echo credentials."""

    parts = urlsplit(database_url)
    host = (parts.hostname or "").lower()
    username = parts.username or ""
    if host.endswith(".pooler.supabase.com") and "." in username:
        return username.split(".", 1)[1]
    if host.startswith("db.") and host.endswith(".supabase.co"):
        return host.split(".")[1]
    return None


def _expected_target_label(database_url: str) -> str:
    """Return the confirmation label a target URL requires."""

    project_ref = _project_ref_from_url(database_url)
    if project_ref:
        return project_ref
    host = (urlsplit(database_url).hostname or "").lower()
    if host in {"localhost", "127.0.0.1", "::1"} or host.startswith("/"):
        return "local"
    return host


def _validate_target(database_url: str, target: str) -> None:
    """Require an explicit confirmation that names the actual database target."""

    expected = _expected_target_label(database_url)
    if target != expected:
        raise ImportRefused(f"Target confirmation mismatch: expected {expected!r}, got {target!r}")


def _target_summary(database_url: str) -> dict[str, str | None]:
    """Describe a target without exposing usernames, passwords, or query strings."""

    parts = urlsplit(database_url)
    return {
        "host": parts.hostname,
        "database": parts.path.lstrip("/") or None,
        "project_ref": _project_ref_from_url(database_url),
    }


def _database_error_message(exc: Exception) -> str:
    """Keep driver errors actionable while omitting connection strings."""

    diagnostic = getattr(exc, "diag", None)
    detail = getattr(diagnostic, "message_primary", None) if diagnostic else None
    sqlstate = getattr(exc, "sqlstate", None)
    parts = [type(exc).__name__]
    if sqlstate:
        parts.append(str(sqlstate))
    if detail:
        parts.append(detail)
    return "Database operation failed: " + " - ".join(parts)


def _connect(database_url: str) -> psycopg.Connection:
    """Open a non-autocommit connection with prepared statements disabled."""

    try:
        params = conninfo_to_dict(database_url)
        host = str(params.get("host") or "").lower()
        local = host in {"localhost", "127.0.0.1", "::1"} or host.startswith("/")
        if not local and params.get("sslmode") not in {"require", "verify-ca", "verify-full"}:
            params["sslmode"] = "require"
        params.setdefault("application_name", "nus-exchange-planner-import")
        params.setdefault("connect_timeout", "15")
        return psycopg.connect(
            make_conninfo(**params),
            autocommit=False,
            prepare_threshold=None,
        )
    except (psycopg.Error, ValueError) as exc:
        raise CatalogImportError(_database_error_message(exc)) from None


def _require_schema(connection: psycopg.Connection) -> None:
    """Fail clearly when the target has not had the reviewed migrations applied."""

    missing = [
        table
        for table in REQUIRED_TABLES
        if connection.execute("select to_regclass(%s)", (table,)).fetchone()[0] is None
    ]
    if missing:
        raise ImportRefused(
            "Target schema is incomplete; apply the reviewed migrations first. "
            f"Missing: {', '.join(missing)}"
        )


def _catalog_counts(connection: psycopg.Connection) -> dict[str, int]:
    """Count every table that the importer owns so partial publications are visible."""

    row = connection.execute(
        """
        select
          (select count(*) from public.degrees),
          (select count(*) from public.nus_modules),
          (select count(*) from public.degree_modules),
          (select count(*) from public.specializations),
          (select count(*) from public.specialization_modules),
          (select count(*) from public.partner_universities),
          (select count(*) from public.pu_modules),
          (select count(*) from public.module_mappings),
          (select count(*) from public.catalog_source_snapshots),
          (select count(*) from public.catalog_source_rows),
          (select count(*) from public.catalog_issues),
          (select count(*) from public.catalog_repairs),
          (select count(*) from public.catalog_import_batches)
        """
    ).fetchone()
    keys = (
        "degrees",
        "nus_modules",
        "degree_modules",
        "specializations",
        "specialization_modules",
        "partner_universities",
        "pu_modules",
        "module_mappings",
        "source_snapshots",
        "source_rows",
        "issues",
        "repairs",
        "batches",
    )
    return dict(zip(keys, (int(value) for value in row), strict=True))


def _publication_state(connection: psycopg.Connection, plan: ImportPlan) -> PublicationState:
    """Decide whether this target may receive the initial publication."""

    batches = connection.execute(
        """
        select id, source_checksum, repair_checksum, status, is_current
        from public.catalog_import_batches
        order by id
        """
    ).fetchall()
    counts = _catalog_counts(connection)
    current = [row for row in batches if row[3] == "completed" and row[4]]
    matching = [
        row for row in current if row[1] == plan.source_checksum and row[2] == plan.repair_checksum
    ]
    if len(batches) == 1 and len(matching) == 1:
        if counts["degrees"] > 0 and counts["module_mappings"] > 0:
            return PublicationState(
                "noop",
                "matching source and repair checksums are already published",
                int(matching[0][0]),
                counts,
            )
        return PublicationState(
            "blocked",
            "a completed batch exists but its catalog rows are missing",
            int(matching[0][0]),
            counts,
        )
    if batches or any(counts.values()):
        return PublicationState(
            "blocked",
            "target already contains a different or partial catalog; "
            "this importer only publishes an empty target",
            None,
            counts,
        )
    return PublicationState(
        "import",
        "target is empty and ready for the reviewed catalog snapshot",
        None,
        counts,
    )


def _plan_counts(plan: ImportPlan) -> dict[str, int]:
    """Expose the deterministic source accounting used by the preview."""

    summary = plan.summary
    return {
        "archives": len(plan.archives),
        "degrees": len(plan.entities.degrees),
        "nus_modules": len(plan.entities.nus_modules),
        "degree_modules": len(plan.entities.degree_modules),
        "specializations": len(plan.entities.specializations),
        "specialization_modules": len(plan.entities.specialization_modules),
        "partner_universities": len(plan.entities.universities),
        "partner_modules": len(plan.entities.partner_modules),
        "source_rows": summary["raw_rows"],
        "active_rows": len(plan.mappings),
        "accepted_rows": summary["accepted_rows"],
        "repaired_rows": summary["repaired_rows"],
        "quarantined_rows": summary["quarantined_rows"],
        "issues": len(plan.issues),
        "repairs": len(plan.repairs),
    }


def _result_base(plan: ImportPlan) -> dict[str, Any]:
    """Build stable, secret-free fields shared by every run report."""

    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "source_checksum": plan.source_checksum,
        "repair_checksum": plan.repair_checksum,
        "planned_counts": _plan_counts(plan),
    }


def dry_run(plan: ImportPlan, database_url: str | None) -> dict[str, Any]:
    """Read target state without writing and report what an apply would do."""

    result = _result_base(plan)
    result["mode"] = "dry-run"
    if not database_url:
        result["action"] = "planned"
        result["reason"] = "no database URL supplied; only the offline plan was validated"
        return result
    with _connect(database_url) as connection:
        connection.read_only = True
        with connection.transaction():
            _require_schema(connection)
            state = _publication_state(connection, plan)
    result["target"] = _target_summary(database_url)
    result["action"] = {
        "import": "would_import",
        "noop": "noop",
        "blocked": "blocked",
    }[state.action]
    result["reason"] = state.reason
    result["batch_id"] = state.batch_id
    result["existing_counts"] = state.existing_counts
    return result


def _insert_batch(connection: psycopg.Connection, plan: ImportPlan) -> int:
    """Create the running batch marker before any catalog rows are written."""

    manifest = {
        "files": [
            {
                "path": archive.path,
                "kind": archive.kind,
                "sha256": archive.sha256,
                "byte_size": archive.byte_size,
            }
            for archive in plan.archives
        ],
        "source_checksum_sha256": plan.source_checksum,
        "repair_checksum_sha256": plan.repair_checksum,
        "academic_year": plan.academic_year,
        "prepared_on": plan.prepared_on,
        "repair_file": plan.repair_file,
    }
    row = connection.execute(
        """
        insert into public.catalog_import_batches (
          source_checksum,
          repair_checksum,
          status,
          is_current,
          source_manifest,
          source_file_count,
          raw_row_count,
          accepted_row_count,
          repaired_row_count,
          quarantined_row_count,
          note
        ) values (%s, %s, 'running', false, %s, %s, %s, %s, %s, %s, %s)
        returning id
        """,
        (
            plan.source_checksum,
            plan.repair_checksum,
            Jsonb(manifest),
            len(plan.archives),
            plan.summary["raw_rows"],
            plan.summary["accepted_rows"],
            plan.summary["repaired_rows"],
            plan.summary["quarantined_rows"],
            "Initial reviewed publication from the checked-in catalog snapshot.",
        ),
    ).fetchone()
    return int(row[0])


def _insert_snapshots(
    connection: psycopg.Connection, plan: ImportPlan, batch_id: int
) -> dict[str, int]:
    """Persist exact source text and parsed JSON for every archived file."""

    ids: dict[str, int] = {}
    for archive in plan.archives:
        row = connection.execute(
            """
            insert into public.catalog_source_snapshots (
              batch_id, file_path, source_kind, raw_text, parsed_json, sha256, byte_size
            ) values (%s, %s, %s, %s, %s, %s, %s)
            returning id
            """,
            (
                batch_id,
                archive.path,
                archive.kind,
                archive.raw_text,
                Jsonb(archive.parsed),
                archive.sha256,
                archive.byte_size,
            ),
        ).fetchone()
        ids[archive.path] = int(row[0])
    return ids


def _insert_source_rows(
    connection: psycopg.Connection,
    plan: ImportPlan,
    snapshots: dict[str, int],
) -> dict[tuple[str, int], int]:
    """Insert one row per source position and keep repaired raw values intact."""

    ids: dict[tuple[str, int], int] = {}
    for item in plan.source_rows:
        row = connection.execute(
            """
            insert into public.catalog_source_rows (
              snapshot_id,
              mapping_index,
              raw_json,
              source_nus_code,
              source_partner_code,
              source_nus_title,
              source_partner_title,
              source_nus_units,
              source_partner_units,
              source_faculty,
              source_page,
              outcome
            ) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            returning id
            """,
            (
                snapshots[item.source_file],
                item.mapping_index,
                Jsonb(item.raw_row),
                item.source_nus_code,
                item.source_partner_code,
                item.source_nus_title,
                item.source_partner_title,
                item.source_nus_units,
                item.source_partner_units,
                item.source_faculty,
                item.source_page,
                item.outcome,
            ),
        ).fetchone()
        ids[item.key] = int(row[0])
    return ids


def _insert_degrees(connection: psycopg.Connection, plan: ImportPlan) -> dict[str, int]:
    """Insert degree identities and return their generated ids."""

    ids: dict[str, int] = {}
    for item in plan.entities.degrees:
        row = connection.execute(
            """
            insert into public.degrees (name, faculty, full_title, source_order)
            values (%s, %s, %s, %s)
            returning id
            """,
            (item.name, item.faculty, item.full_title, item.source_order),
        ).fetchone()
        ids[item.name] = int(row[0])
    return ids


def _insert_nus_modules(connection: psycopg.Connection, plan: ImportPlan) -> None:
    """Insert normalized NUS courses, preserving genuinely unknown metadata."""

    with connection.cursor() as cursor:
        cursor.executemany(
            """
            insert into public.nus_modules (code, name, offering_faculty, verified_units)
            values (%s, %s, %s, %s)
            """,
            [
                (item.code, item.name, item.offering_faculty, item.verified_units)
                for item in plan.entities.nus_modules
            ],
        )


def _insert_degree_modules(
    connection: psycopg.Connection,
    plan: ImportPlan,
    degree_ids: dict[str, int],
) -> None:
    """Insert each degree membership once, retaining its requirement label."""

    with connection.cursor() as cursor:
        cursor.executemany(
            """
            insert into public.degree_modules (degree_id, module_code, requirement_type)
            values (%s, %s, %s)
            """,
            [
                (
                    degree_ids[item.degree],
                    item.module_code,
                    item.requirement_type,
                )
                for item in plan.entities.degree_modules
            ],
        )


def _insert_universities(connection: psycopg.Connection, plan: ImportPlan) -> dict[str, int]:
    """Insert partner universities and return their generated ids."""

    ids: dict[str, int] = {}
    for item in plan.entities.universities:
        row = connection.execute(
            """
            insert into public.partner_universities (
              name, country, city, continent, source_order
            ) values (%s, %s, %s, %s, %s)
            returning id
            """,
            (item.name, item.country, item.city, item.continent, item.source_order),
        ).fetchone()
        ids[item.name] = int(row[0])
    return ids


def _insert_partner_modules(
    connection: psycopg.Connection,
    plan: ImportPlan,
    universities: dict[str, int],
) -> dict[tuple[str, str], int]:
    """Insert partner-scoped course identities and return their ids."""

    ids: dict[tuple[str, str], int] = {}
    for item in plan.entities.partner_modules:
        row = connection.execute(
            """
            insert into public.pu_modules (
              code, name, partner_university_id, verified_units
            ) values (%s, %s, %s, %s)
            returning id
            """,
            (
                item.code,
                item.name,
                universities[item.university],
                item.verified_units,
            ),
        ).fetchone()
        ids[(item.university, item.code)] = int(row[0])
    return ids


def _insert_mappings(
    connection: psycopg.Connection,
    plan: ImportPlan,
    source_rows: dict[tuple[str, int], int],
    partner_modules: dict[tuple[str, str], int],
) -> None:
    """Insert one normalized mapping for each active source row position."""

    with connection.cursor() as cursor:
        cursor.executemany(
            """
            insert into public.module_mappings (
              nus_module_code,
              pu_module_id,
              source_row_id,
              source_order,
              source_nus_title,
              source_nus_units,
              source_partner_title,
              source_partner_units,
              source_faculty
            ) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            [
                (
                    item.nus_module_code,
                    partner_modules[(item.university, item.partner_module_code)],
                    source_rows[item.key],
                    item.source_order,
                    item.source_nus_title,
                    item.source_nus_units,
                    item.source_partner_title,
                    item.source_partner_units,
                    item.source_faculty,
                )
                for item in plan.mappings
            ],
        )


def _insert_specializations(
    connection: psycopg.Connection,
    plan: ImportPlan,
    degree_ids: dict[str, int],
) -> None:
    """Insert specializations/focus areas and their ordered memberships.

    Membership notes stay in the source-addressed issue rows so unknown or
    externally linked curriculum details are retained without inventing a list.
    """

    memberships: dict[tuple[str, str], list[str]] = {}
    for item in plan.entities.specialization_modules:
        memberships.setdefault((item.degree, item.specialization), []).append(item.module_code)
    for item in plan.entities.specializations:
        row = connection.execute(
            """
            insert into public.specializations (
              degree_id, name, kind, source_order
            ) values (%s, %s, %s, %s)
            returning id
            """,
            (
                degree_ids[item.degree],
                item.name,
                item.kind,
                item.source_order,
            ),
        ).fetchone()
        specialization_id = int(row[0])
        codes = memberships.get((item.degree, item.name), [])
        if codes:
            with connection.cursor() as cursor:
                cursor.executemany(
                    """
                    insert into public.specialization_modules (
                      specialization_id, module_code
                    ) values (%s, %s)
                    """,
                    [(specialization_id, code) for code in codes],
                )


def _insert_issues(
    connection: psycopg.Connection,
    plan: ImportPlan,
    batch_id: int,
    snapshots: dict[str, int],
    source_rows: dict[tuple[str, int], int],
) -> None:
    """Persist every source-addressed issue and its resolution state."""

    for item in plan.issues:
        connection.execute(
            """
            insert into public.catalog_issues (
              batch_id,
              snapshot_id,
              source_row_id,
              json_pointer,
              issue_code,
              severity,
              message,
              status
            ) values (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                batch_id,
                snapshots[item.source_file],
                source_rows.get((item.source_file, item.mapping_index))
                if item.mapping_index is not None
                else None,
                item.json_pointer,
                item.code,
                item.severity,
                item.message,
                item.status,
            ),
        )


def _insert_repairs(
    connection: psycopg.Connection,
    plan: ImportPlan,
    batch_id: int,
    snapshots: dict[str, int],
    source_rows: dict[tuple[str, int], int],
) -> None:
    """Persist verified and unresolved repair evidence at source pointers."""

    for item in plan.repairs:
        connection.execute(
            """
            insert into public.catalog_repairs (
              batch_id,
              snapshot_id,
              source_row_id,
              json_pointer,
              before_value,
              after_value,
              source_url,
              source_title,
              accessed_on,
              academic_year,
              evidence,
              status
            ) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                batch_id,
                snapshots[item.source_file],
                source_rows[(item.source_file, item.mapping_index)],
                item.json_pointer,
                Jsonb(item.before_value),
                Jsonb(item.after_value),
                item.source_url,
                item.source_title,
                item.accessed_on,
                item.academic_year,
                item.evidence,
                item.status,
            ),
        )


def _complete_batch(connection: psycopg.Connection, plan: ImportPlan, batch_id: int) -> None:
    """Mark the batch complete only after every row and archive is present."""

    updated = connection.execute(
        """
        update public.catalog_import_batches
        set status = 'completed',
            is_current = true,
            completed_at = now(),
            note = %s
        where id = %s and status = 'running'
        """,
        (
            "Initial publication completed from the reviewed import plan.",
            batch_id,
        ),
    ).rowcount
    if updated != 1:
        raise ImportDataError("Import batch could not be marked complete")


def apply_plan(
    plan: ImportPlan,
    database_url: str,
    *,
    simulate_failure: bool = False,
) -> dict[str, Any]:
    """Publish the initial catalog in one transaction, or prove a clean rollback."""

    with _connect(database_url) as connection, connection.transaction():
        _require_schema(connection)
        connection.execute(
            "select pg_advisory_xact_lock(hashtextextended(%s, 0))",
            (IMPORT_LOCK_KEY,),
        )
        state = _publication_state(connection, plan)
        if state.action == "blocked":
            raise ImportRefused(state.reason)
        result = _result_base(plan)
        result["mode"] = "apply"
        result["target"] = _target_summary(database_url)
        result["existing_counts"] = state.existing_counts
        if state.action == "noop":
            result["action"] = "noop"
            result["reason"] = state.reason
            result["batch_id"] = state.batch_id
            return result
        batch_id = _insert_batch(connection, plan)
        snapshots = _insert_snapshots(connection, plan, batch_id)
        source_rows = _insert_source_rows(connection, plan, snapshots)
        degree_ids = _insert_degrees(connection, plan)
        _insert_nus_modules(connection, plan)
        _insert_degree_modules(connection, plan, degree_ids)
        universities = _insert_universities(connection, plan)
        partner_modules = _insert_partner_modules(connection, plan, universities)
        _insert_mappings(connection, plan, source_rows, partner_modules)
        _insert_specializations(connection, plan, degree_ids)
        _insert_issues(connection, plan, batch_id, snapshots, source_rows)
        _insert_repairs(connection, plan, batch_id, snapshots, source_rows)
        if simulate_failure:
            raise SimulatedImportFailure("Injected failure after catalog inserts")
        _complete_batch(connection, plan, batch_id)
        result["action"] = "imported"
        result["reason"] = "initial catalog publication committed"
        result["batch_id"] = batch_id
        return result


def _print_summary(result: dict[str, Any]) -> None:
    """Print a compact, secret-free report for terminal use."""

    print(f"Mode: {result['mode']}")
    print(f"Action: {result['action']}")
    if target := result.get("target"):
        database = target.get("database") or ""
        print(f"Target: {target.get('host')}/{database}".rstrip("/"))
    if result.get("batch_id"):
        print(f"Batch: {result['batch_id']}")
    print(f"Source checksum: {result['source_checksum']}")
    print(f"Repair checksum: {result['repair_checksum']}")
    counts = result["planned_counts"]
    print(
        "Rows: "
        f"{counts['source_rows']} raw, "
        f"{counts['active_rows']} active, "
        f"{counts['accepted_rows']} accepted, "
        f"{counts['repaired_rows']} repaired, "
        f"{counts['quarantined_rows']} quarantined"
    )
    print(f"Reason: {result['reason']}")


def _emit(result: dict[str, Any], args: argparse.Namespace) -> None:
    """Write an optional deterministic report and print the requested format."""

    if args.output:
        write_json(args.output, result)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False))
    else:
        _print_summary(result)


def _exit_code(result: dict[str, Any]) -> int:
    """Use a distinct nonzero status for refusals and rolled-back failures."""

    if result["action"] == "blocked":
        return 2
    if result["action"] == "rolled_back":
        return 1
    return 0


def _parser() -> argparse.ArgumentParser:
    """Build the explicitly safe import CLI."""

    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--dry-run",
        action="store_true",
        help="validate and report without writing (default)",
    )
    mode.add_argument(
        "--apply",
        action="store_true",
        help="publish the catalog in one transaction",
    )
    parser.add_argument(
        "--database-url",
        help="PostgreSQL URL; defaults to IMPORT_DATABASE_URL",
    )
    parser.add_argument(
        "--target-project-ref",
        help="expected Supabase project ref, or 'local' for a local database",
    )
    parser.add_argument(
        "--confirm-project-ref",
        help="must exactly repeat --target-project-ref when applying",
    )
    parser.add_argument("--json", action="store_true", help="print the full report as JSON")
    parser.add_argument("--output", type=Path, help="also write the report to this path")
    parser.add_argument(
        "--simulate-failure",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Plan, inspect, or publish the checked-in catalog."""

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    parser = _parser()
    args = parser.parse_args(argv)
    database_url = args.database_url or os.environ.get("IMPORT_DATABASE_URL")
    if args.simulate_failure and not args.apply:
        parser.error("--simulate-failure requires --apply")
    if args.apply:
        if not database_url:
            parser.error("--apply requires --database-url or IMPORT_DATABASE_URL")
        if not args.target_project_ref or not args.confirm_project_ref:
            parser.error("--apply requires --target-project-ref and --confirm-project-ref")
        if args.target_project_ref != args.confirm_project_ref:
            parser.error("--confirm-project-ref must exactly match --target-project-ref")

    plan: ImportPlan | None = None
    try:
        if database_url and args.target_project_ref:
            _validate_target(database_url, args.target_project_ref)
        plan = build_import_plan()
        if not args.apply:
            result = dry_run(plan, database_url)
        else:
            try:
                result = apply_plan(
                    plan,
                    database_url,
                    simulate_failure=args.simulate_failure,
                )
            except SimulatedImportFailure:
                result = _result_base(plan)
                result["mode"] = "apply"
                result["action"] = "rolled_back"
                result["reason"] = "injected failure rolled back the entire transaction"
                result["batch_id"] = None
                result["target"] = _target_summary(database_url)
                with _connect(database_url) as connection:
                    connection.read_only = True
                    with connection.transaction():
                        result["existing_counts"] = _catalog_counts(connection)
        _emit(result, args)
        return _exit_code(result)
    except CatalogImportError as exc:
        error = {
            "error": str(exc),
            "source_checksum": plan.source_checksum if plan else None,
            "repair_checksum": plan.repair_checksum if plan else None,
        }
        if args.json:
            print(json.dumps(error, indent=2, sort_keys=True))
        else:
            print(f"error: {exc}", file=sys.stderr)
        return 2 if isinstance(exc, ImportRefused) else 1
    except psycopg.Error as exc:
        message = _database_error_message(exc)
        if args.json:
            print(json.dumps({"error": message}, indent=2, sort_keys=True))
        else:
            print(f"error: {message}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
