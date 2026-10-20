"""All-or-nothing, instance-local source catalog."""

import json
import logging
from dataclasses import dataclass
from pathlib import Path

from pydantic import ValidationError

from .course_codes import extract_course_codes, normalized_course_code
from .models import COUNTRIES, Degree, SourceMajors, SourceUniversity, University

LOG = logging.getLogger(__name__)
DATA_ROOT = Path(__file__).resolve().parents[2] / "data"
MANIFEST = Path(__file__).with_name("data_manifest.json")


class CatalogUnavailable(Exception):
    pass


@dataclass(frozen=True)
class Catalog:
    degrees: tuple[Degree, ...]
    universities: tuple[University, ...]

    def degree(self, name: str) -> Degree | None:
        return next((item for item in self.degrees if item.name == name), None)

    def university(self, name: str) -> University | None:
        return next((item for item in self.universities if item.name == name), None)


def discover_files(data_root: Path = DATA_ROOT) -> list[str]:
    return sorted(
        str(path.relative_to(data_root))
        for folder in (data_root / "majors", data_root / "mapping")
        for path in folder.rglob("*.json")
    )


def write_manifest(data_root: Path = DATA_ROOT, manifest: Path = MANIFEST) -> None:
    manifest.write_text(json.dumps({"files": discover_files(data_root)}, indent=2) + "\n")


def _parse_degree(item: dict) -> Degree:
    name, title = item["name"], item["degree"]
    if (
        not isinstance(name, str)
        or not name.strip()
        or not isinstance(title, str)
        or not title.strip()
    ):
        raise ValueError("Degree name and full title are required")
    return Degree(name=name, degree=title, codes=extract_course_codes(item))


def _parse_university(raw: object, relative: str) -> University:
    country_key = Path(relative).parts[1]
    if country_key not in COUNTRIES:
        raise ValueError(f"Unknown country folder: {country_key}")

    source = SourceUniversity.model_validate(raw)
    name = source.partner_university["name"]
    if not name.strip():
        raise ValueError(f"Blank or duplicate university: {name}")

    valid_mappings = []
    for mapping in source.mappings:
        if normalized_course_code(mapping.nus_course.code) is None:
            LOG.warning("Skipping invalid NUS code %r in %s", mapping.nus_course.code, relative)
            continue
        valid_mappings.append(mapping)

    return University(name=name, country=COUNTRIES[country_key], mappings=tuple(valid_mappings))


def load_catalog(data_root: Path = DATA_ROOT, manifest: Path = MANIFEST) -> Catalog:
    try:
        expected = json.loads(manifest.read_text())["files"]
        if (
            not isinstance(expected, list)
            or not expected
            or any(not isinstance(p, str) for p in expected)
        ):
            raise ValueError("Invalid expected-file manifest")
        actual = discover_files(data_root)
        if sorted(expected) != actual:
            raise ValueError(f"Source-file manifest mismatch: expected {expected}, found {actual}")

        degrees: list[Degree] = []
        universities: list[University] = []
        degree_names: set[str] = set()
        university_names: set[str] = set()
        for relative in expected:
            path = data_root / relative
            raw = json.loads(path.read_text())
            if relative.startswith("majors/"):
                source = SourceMajors.model_validate(raw)
                for item in source.majors:
                    degree = _parse_degree(item)
                    if degree.name in degree_names:
                        raise ValueError(f"Duplicate degree: {degree.name}")
                    degree_names.add(degree.name)
                    degrees.append(degree)
            elif relative.startswith("mapping/"):
                university = _parse_university(raw, relative)
                if university.name in university_names:
                    raise ValueError(f"Blank or duplicate university: {university.name}")
                university_names.add(university.name)
                universities.append(university)
            else:
                raise ValueError(f"Unexpected source path: {relative}")
        if not degrees or not universities:
            raise ValueError("Catalog requires degrees and universities")
        return Catalog(tuple(degrees), tuple(universities))
    except (OSError, ValueError, KeyError, TypeError, ValidationError) as exc:
        LOG.error("Catalog unavailable: %s", exc)
        raise CatalogUnavailable("Catalog data is unavailable. Please try again later.") from exc


if __name__ == "__main__":
    write_manifest()
