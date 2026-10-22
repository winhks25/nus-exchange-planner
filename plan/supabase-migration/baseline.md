# Phase 1 baseline

Captured: 2026-10-22T04:55:20Z
Git revision: `745e24c723e43f3978df6e5a603afbf8a28d8140`
Python: 3.12.14 on macOS-26.5.1-arm64
Runtime packages: FastAPI 0.148.0, Pydantic 2.14.1, Uvicorn 0.54.0

This file records the JSON-mode behavior that the migration must preserve. The
machine-readable responses are in [baseline-responses.json](baseline-responses.json).
No credentials are read or recorded here.

## Working tree

Before Phase 1 started, the tracked tree was clean at the revision above. Two
untracked paths existed and were preserved: `plan/supabase-migration/` (this plan)
and `supabase/` (the manually applied initial migration). They were committed on
their own before implementation evidence was added.

## Source inventory and checksums

All checksums are SHA-256 of the exact checked-in files.

| Source | Raw mapping rows | SHA-256 |
|---|---:|---|
| `data/majors/nus_soc_majors.json` | - | `f62a00b1f57bab9066e6629cbb20dabb0f43129d17c7bf456dc423933f04dfc4` |
| `data/mapping/australia/west-au.json` | 32 | `987d1fe6343f72b41a51976f2767a0613b5028bb4371244863143ca8601aa95a` |
| `data/mapping/canada/toronto.json` | 55 | `ad1baec1ee241b7b2ba253a65874615f66471abb384bf93a3fb66fc1430ddef9` |
| `data/mapping/japan/kyoto.json` | 7 | `a42cb28be8372df929cd3c79b9860922ef15464758557689801ea004fdd48cd3` |
| `data/mapping/korea/korea.json` | 36 | `96cdd005ff1d79923e7d3d19025bad6565f9a58dcf6dd6da16046e929b3a5946` |
| `data/mapping/korea/yonsei.json` | 24 | `fd4b3635fa899f2e27c1a28592bf5c50f2908fe0992608d26d86a0c5ca269634` |
| `backend/app/data_manifest.json` | - | `eafa0af73582f31afe4e30ef02f62284bd9bfce3425ddff679a7fef5d1d6400f` |

The six source files produce **154 raw mapping rows**. The legacy loader accepts
**147 rows** and skips **7 rows**, all in `data/mapping/canada/toronto.json` at
array indexes 48-54. Those same seven rows have no NUS course title: the code
field contains a truncated course name rather than a course code. No partner
titles are missing.

| Metric | Baseline |
|---|---:|
| Degrees | 6 |
| Partner universities | 5 |
| Degree/university pairs | 30 |
| Raw mapping rows | 154 |
| Accepted mapping rows | 147 |
| Rejected mapping rows | 7 |
| Missing NUS titles | 7 |
| Missing partner titles | 0 |
| Non-empty degree/university pairs | 27 |
| Empty degree/university pairs | 3 |
| Mapping rows across all pairs | 190 |

The three empty pairs are Artificial Intelligence x University of Western
Australia, Computer Science x University of Western Australia, and Computer
Science x Yonsei University. They are valid-empty responses, not errors.

## Endpoint capture method

Responses were produced in-process with `fastapi.testclient.TestClient` from
`backend.app.main.create_app()` against the default data root and manifest. No
HTTP server, network call, database, or Supabase project was involved.

`baseline-responses.json` contains:

- `catalog`: the `GET /api/v1/catalog` response with status and body.
- `recommendations`: one `GET /api/v1/recommendations?degree=...` response for
  each of the six degrees, keyed by degree name.
- `mappings`: one `GET /api/v1/mappings?degree=...&uni=...` response for each of
  the thirty degree/university pairs, keyed by `degree || university`.

Every captured response has HTTP status 200. The catalog is in source order:
Artificial Intelligence, Business Analytics, Business Artificial Intelligence
Systems, Computer Science, Information Systems, Information Security. Universities
are University of Western Australia, University of Toronto, Kyoto University,
Korea University, Yonsei University.

## Recommendation ranking baseline

Ranking is distinct NUS module count descending, then university name ascending.
Counts are shown as `partner / distinct NUS / mapping rows`.

| Degree | Ranking |
|---|---|
| Artificial Intelligence | Toronto 9/6/9, Yonsei 4/3/4, Korea 2/2/2, Kyoto 1/1/1, Western Australia 0/0/0 |
| Business Analytics | Korea 17/11/18, Western Australia 19/11/22, Toronto 18/9/18, Yonsei 10/5/10, Kyoto 2/2/2 |
| Business Artificial Intelligence Systems | Korea 11/8/11, Western Australia 8/6/8, Yonsei 6/4/6, Toronto 4/3/4, Kyoto 1/1/1 |
| Computer Science | Toronto 6/3/6, Korea 2/2/2, Kyoto 1/1/1, Western Australia 0/0/0, Yonsei 0/0/0 |
| Information Systems | Korea 12/9/12, Western Australia 9/9/12, Toronto 9/5/9, Yonsei 7/5/7, Kyoto 3/3/3 |
| Information Security | Western Australia 6/6/6, Toronto 7/5/7, Korea 5/4/5, Yonsei 3/2/3, Kyoto 1/1/1 |

Business Analytics is the baseline case where NUS-count order and partner-count
order differ: Western Australia has more partner modules (19) but ties Korea on
distinct NUS modules (11), so Korea sorts first by name.

## Existing check outcomes

These are the pre-migration results. They are recorded as-is and are not caused
by database work; no application code was changed in Phase 1.

| Check | Command | Result |
|---|---|---|
| Backend tests | `backend/.venv/bin/python -m pytest -q` | 7 passed, 1 failed |
| Backend lint | `backend/.venv/bin/ruff check .` | Passed |
| Frontend lint | `npm run lint --prefix frontend` | Passed |
| Frontend types | `npm run typecheck --prefix frontend` | Passed |
| Frontend build | `npm run build --prefix frontend` | Passed |
| Frontend browser tests | `npx playwright test` in `frontend/` | 47 passed, 18 failed |

The backend failure is pre-existing: `tests/test_catalog.py::test_current_catalog_and_consistency`
still requests `University of Western Australia, The`, but commit `745e24c`
renamed the university to `University of Western Australia`, so the mapping
response is a 404 without `partner_module_count`. The browser failures are
baseline visual/geometry failures in the current UI, not migration regressions.
Both baselines must be compared against the post-migration suite, not assumed
green.

## Reproduction

Regenerate the machine-readable file by importing `create_app`, `load_catalog`,
and `TestClient` from the backend environment, then recording the catalog,
per-degree recommendation, and all degree/university mapping responses with
their status codes. Include the source checksums and the Git revision in the same
payload. Run the checks from their respective directories so `Ruff`, `pytest`,
ESLint, TypeScript, and Playwright resolve the checked-in configuration.
