"""Shared, side-effect-free access to the checked-in catalog source files."""

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.course_codes import COURSE_CODE, extract_course_codes

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = REPO_ROOT / "data"
MANIFEST_PATH = REPO_ROOT / "backend" / "app" / "data_manifest.json"

MAJORS_DIR = "majors"
MAPPING_DIR = "mapping"
REPAIRS_PATH = "data/repairs/catalog_repairs.json"


class SourceError(ValueError):
    """Raised when a source file cannot be read or does not match its manifest."""


@dataclass(frozen=True)
class CodeReference:
    """One course-code occurrence inside a list-item string."""

    code: str
    pointer: str
    text: str
    list_path: str


@dataclass(frozen=True)
class SourceFile:
    """Exact bytes plus parsed JSON for one archived source file."""

    path: str
    kind: str
    raw_bytes: bytes
    raw_text: str
    parsed: Any
    sha256: str
    byte_size: int


def sha256_bytes(data: bytes) -> str:
    """Return the lowercase SHA-256 digest for exact source bytes."""

    return hashlib.sha256(data).hexdigest()


def repo_path(path: Path) -> str:
    """Return a stable repository-relative path for reports and archives."""

    return path.resolve().relative_to(REPO_ROOT).as_posix()


def json_pointer_escape(token: str) -> str:
    """Escape one JSON Pointer token as required by RFC 6901."""

    return token.replace("~", "~0").replace("/", "~1")


def json_pointer(*tokens: object) -> str:
    """Build an RFC 6901 pointer from object keys and array indexes."""

    return "".join(f"/{json_pointer_escape(str(token))}" for token in tokens)


def source_kind(path: Path) -> str:
    """Classify a source path by the archive kind used by the database schema."""

    relative = repo_path(path)
    if relative == repo_path(MANIFEST_PATH):
        return "manifest"
    if relative == REPAIRS_PATH:
        return "repairs"
    if relative.startswith("data/majors/"):
        return "majors"
    if relative.startswith("data/mapping/"):
        return "mapping"
    raise SourceError(f"Unsupported source path: {relative}")


def read_source_file(path: Path) -> SourceFile:
    """Read exact bytes and parse JSON without rewriting the source file."""

    try:
        raw_bytes = path.read_bytes()
        raw_text = raw_bytes.decode("utf-8")
        parsed = json.loads(raw_text)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SourceError(f"Cannot read JSON source {repo_path(path)}: {type(exc).__name__}") from None
    return SourceFile(
        path=repo_path(path),
        kind=source_kind(path),
        raw_bytes=raw_bytes,
        raw_text=raw_text,
        parsed=parsed,
        sha256=sha256_bytes(raw_bytes),
        byte_size=len(raw_bytes),
    )


def discover_catalog_paths() -> list[Path]:
    """Return every majors and mapping JSON file in stable path order."""

    majors = sorted((DATA_ROOT / MAJORS_DIR).rglob("*.json"))
    mappings = sorted((DATA_ROOT / MAPPING_DIR).rglob("*.json"))
    return majors + mappings


def manifest_paths() -> list[str]:
    """Read the runtime manifest and normalize its entries to repository paths."""

    try:
        document = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SourceError(f"Cannot read manifest: {type(exc).__name__}") from None
    files = document.get("files") if isinstance(document, dict) else None
    if (
        not isinstance(files, list)
        or not files
        or not all(isinstance(item, str) and item.strip() for item in files)
    ):
        raise SourceError("Manifest must contain a non-empty list of file paths")
    return sorted(f"data/{item.strip().lstrip('/')}" for item in files)


def load_catalog_sources() -> list[SourceFile]:
    """Load every actual majors/mapping file and verify it matches the manifest."""

    actual = [read_source_file(path) for path in discover_catalog_paths()]
    actual_paths = sorted(source.path for source in actual)
    expected_paths = manifest_paths()
    if actual_paths != expected_paths:
        missing = sorted(set(expected_paths) - set(actual_paths))
        unexpected = sorted(set(actual_paths) - set(expected_paths))
        raise SourceError(
            f"Source-file manifest mismatch; missing={missing}, unexpected={unexpected}"
        )
    return actual


def load_archive_sources() -> list[SourceFile]:
    """Load the manifest plus every catalog source file that the importer archives."""

    files = [read_source_file(MANIFEST_PATH), *load_catalog_sources()]
    if (REPO_ROOT / REPAIRS_PATH).is_file():
        files.append(read_source_file(REPO_ROOT / REPAIRS_PATH))
    return sorted(files, key=lambda source: source.path)


def extract_code_references(value: Any) -> list[CodeReference]:
    """Record every code from list-item strings, mirroring extract_course_codes.

    The traversal deliberately ignores strings stored directly in dictionaries,
    because the runtime loader only extracts codes from list entries.
    """

    references: list[CodeReference] = []

    def visit(node: Any, pointer: str, list_path: tuple[str, ...], list_item: bool = False) -> None:
        if isinstance(node, dict):
            for key, child in node.items():
                visit(child, f"{pointer}/{json_pointer_escape(str(key))}", (*list_path, str(key)))
        elif isinstance(node, list):
            for index, child in enumerate(node):
                visit(child, f"{pointer}/{index}", list_path, True)
        elif list_item and isinstance(node, str):
            for match in COURSE_CODE.finditer(node):
                references.append(
                    CodeReference(
                        code=match.group().upper(),
                        pointer=pointer,
                        text=node,
                        list_path=".".join(list_path),
                    )
                )

    visit(value, "", ())
    return references


def assert_code_semantics(value: Any, references: list[CodeReference]) -> None:
    """Fail if path-aware extraction ever diverges from the runtime extractor."""

    if frozenset(reference.code for reference in references) != extract_course_codes(value):
        raise SourceError("Path-aware code extraction does not match runtime semantics")


def write_json(path: Path, document: Any) -> None:
    """Write deterministic, human-readable JSON with a trailing newline."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(document, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
