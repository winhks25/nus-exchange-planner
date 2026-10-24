# Final Regression Results — Phase 7 (US5)

Commit: `094c9c8` (test(cleanup): run targeted verification of refactored tooling (T062)).
Date: 2026-10-24. Platform: macOS, Python 3.12.14, pytest 9.1.1, Node.js 22.

---

## T064: Migration and Absence Tests

**Command:**
```bash
uv run --directory backend python -m pytest -v tests/test_catalog_table_removal.py tests/test_catalog_absence.py
```

**Result:** 21 passed, 0 failed, 0 skipped in 13.20s.

| Suite | Tests | Status |
| --- | --- | --- |
| `test_catalog_table_removal.py` | 14 | ✅ All passed |
| `test_catalog_absence.py` | 7 | ✅ All passed |

Assertions verified:
- Zero public `catalog_*` tables after fresh replay and upgrade path.
- No `source_row_id` column dependency on any core table.
- All 8 core tables present with constraints, RLS policies, and reader privileges.
- Data fingerprints including duplicate mappings preserved through upgrade.
- Migration aborts on unexpected dependency and conflicting lock.
- `reject_catalog_archive_mutation()` function absent.
- `catalog_reader` reads core tables after seeding; operational SQL cannot query removed relations.

---
