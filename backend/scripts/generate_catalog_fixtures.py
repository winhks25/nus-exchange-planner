"""Historical utility for generating pre-removal fixtures.

This script was executed once in Phase 2 (T010) before retiring the production
importer to capture backend/tests/fixtures/core_dataset.json and
backend/tests/fixtures/pre_catalog_removal.sql.

With the importer retired in Phase 6, this script is preserved for historical
record and raises an informative error if re-invoked.
"""

import sys


class FixtureGenerationError(RuntimeError):
    """Raised when generation cannot produce trustworthy fixtures."""


def main(argv: list[str] | None = None) -> int:
    """Historical entry point: fixtures are frozen in backend/tests/fixtures/."""
    raise FixtureGenerationError(
        "generate_catalog_fixtures was a one-time tool executed in Phase 2 (T010). "
        "The production importer (scripts.import_catalog) has been retired in Phase 6. "
        "Fixtures are frozen in backend/tests/fixtures/."
    )


if __name__ == "__main__":
    sys.exit(main())
