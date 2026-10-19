import re
from typing import Any

COURSE_CODE = re.compile(r"(?<![A-Za-z0-9])[A-Z]{2,3}[0-9]{4}[A-Z]?(?![A-Za-z0-9])", re.IGNORECASE)


def extract_course_codes(value: Any) -> frozenset[str]:
    """Only list-item strings contribute codes; dictionaries and nested lists are traversed."""
    found: set[str] = set()

    def visit(node: Any, list_item: bool = False) -> None:
        if isinstance(node, dict):
            for child in node.values():
                visit(child)
        elif isinstance(node, list):
            for child in node:
                visit(child, True)
        elif list_item and isinstance(node, str):
            found.update(match.group().upper() for match in COURSE_CODE.finditer(node))

    visit(value)
    return frozenset(found)


def normalized_course_code(value: str) -> str | None:
    return value.upper() if COURSE_CODE.fullmatch(value) else None
