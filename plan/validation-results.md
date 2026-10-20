# MVP implementation validation

Date: 2026-10-20 (Asia/Singapore). Local checkout; production deployment was outside this implementation run. T023 and T024 were rerun against this checkout before commit.

## Source catalog and endpoint results

- Six degree options and five partner universities loaded from the expected-file manifest. Seven Toronto mapping rows had invalid NUS course codes and were logged and skipped, as specified.
- Computer Science rankings: Toronto 3 distinct modules (6 Compare rows), Korea 2 (2 rows), Kyoto 1 (1 row), Western Australia 0, Yonsei 0. Zero-count partners remain in the response and have valid Compare empty states.
- Business Analytics has an 11-count tie. Korea University sorts before University of Western Australia, The by display name. Source-order tie behavior was checked with a synthetic two-row `CS2102` fixture: `SECOND` stayed before `FIRST` after sorting.
- For every one of the 30 current degree–partner pairs, the recommendation count equalled Compare's distinct NUS-code count. This was rechecked through `GET /api/v1/recommendations` and `GET /api/v1/mappings` with FastAPI's test client: 6 degrees, 5 universities, 30 pairs, 0 mismatches. Compare preserved duplicate rows. `mapping_count` was ignored in a synthetic fixture.
- Missing and malformed expected source files produced 503 for the entire catalog. Unknown selection produced 404. An invalid mapping code was omitted. The API omitted absent partner units in a synthetic fixture.

## Browser scenarios

`UV_CACHE_DIR=/private/tmp/nus-uv-cache npm run test:e2e --prefix frontend`: **7 passed** in Chromium on 2026-10-20. The scenarios cover initial blank Recommend, six option display, case-insensitive search, ArrowDown/Home/End/Enter/Escape and active-descendant behavior, zero-count card navigation, deep-link selection and invalid values, result clearing, empty pair, 503 service state, delayed stale Compare response, source-title preservation, and blank absent partner units. The 503 browser state uses a mocked catalog response; the Python test checks an actual malformed and missing source file against the API. The browser test uses port-isolated frontend and backend servers with matching CORS settings. Deployed-URL smoke checks in quickstart step 8 remain pending deployment.

## Checks and timing

| Check | Result |
| --- | --- |
| `uv run --directory backend pytest -q` | 6 passed; one upstream Starlette `httpx` deprecation warning |
| `uv run --directory backend ruff check .` | Passed |
| `npm run lint --prefix frontend` | Passed |
| `npm run typecheck --prefix frontend` | Passed |
| `npm run build --prefix frontend` | Passed; `/` and `/compare` statically prerendered |
| `npm run test:e2e --prefix frontend` | 7 passed |
| Warmed Recommend selection to five rendered cards | 136.2 ms in the final Chromium run, under one second |
| Cold backend Python process import and catalog startup | 0.29 s real time via `/usr/bin/time -p uv run --directory backend python -c 'from app.main import app; print(len(app.openapi()["paths"]))'` |

The warmed figure is a local development-browser measurement, not a production latency guarantee. The cold figure measures backend process startup and schema access, not a deployed Vercel cold request. Production timings require deployment.

## OpenAPI contract comparison

`backend/tests/test_contract.py` checks the generated FastAPI schema against `plan/contracts/openapi.yaml`: the contract's `/api/v1` server prefix resolves to the generated path names; required query parameters, 200 response fields, and 404/503 `detail` bodies match. FastAPI also generates 422 responses for missing required query parameters. Optional `title` and `units` course fields stay optional in the schema and are omitted at runtime when absent.

## Dependency note

Next.js was updated to 16.4.2 after npm audit identified a critical issue in 16.2.0. The remaining five npm audit high findings are in the development-only `eslint-config-next` dependency chain (`fast-glob`, `micromatch`, and `braces`); npm audit does not offer a compatible fix for the current Next.js lint config. Production app dependencies have no remaining audit finding in this run.
