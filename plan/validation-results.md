# MVP implementation validation

Date: 2026-10-20 (Asia/Singapore). Local checkout; production deployment was outside this implementation run. T023 and T024 were rerun against this checkout before commit.

## Source catalog and endpoint results

- Six degree options and five partner universities loaded from the expected-file manifest. Seven Toronto mapping rows had invalid NUS course codes and were logged and skipped, as specified.
- Computer Science rankings: Toronto 3 distinct modules (6 Compare rows), Korea 2 (2 rows), Kyoto 1 (1 row), Western Australia 0, Yonsei 0. Zero-count partners remain in the response and have valid Compare empty states.
- Business Analytics has an 11-count tie. Korea University sorts before University of Western Australia, The by display name. Source-order tie behavior was checked with a synthetic two-row `CS2102` fixture: `SECOND` stayed before `FIRST` after sorting.
- For every one of the 30 current degree–partner pairs, the recommendation count equalled Compare's distinct NUS-code count. This was rechecked through `GET /api/v1/recommendations` and `GET /api/v1/mappings` with FastAPI's test client: 6 degrees, 5 universities, 30 pairs, 0 mismatches. Compare preserved duplicate rows. `mapping_count` was ignored in a synthetic fixture.
- Missing and malformed expected source files produced 503 for the entire catalog. Unknown selection produced 404. An invalid mapping code was omitted. The API omitted absent partner units in a synthetic fixture.

## Browser scenarios

`UV_CACHE_DIR=/private/tmp/nus-uv-cache npm run test:e2e --prefix frontend`: **7 passed** in Chromium in the earlier run; **8 passed** after the count-clarity scenario was added on 2026-10-20 (see below). The scenarios cover initial blank Recommend, six option display, case-insensitive search, ArrowDown/Home/End/Enter/Escape and active-descendant behavior, zero-count card navigation, deep-link selection and invalid values, result clearing, empty pair, 503 service state, delayed stale Compare response, source-title preservation, and blank absent partner units. The 503 browser state uses a mocked catalog response; the Python test checks an actual malformed and missing source file against the API. The browser test uses port-isolated frontend and backend servers with matching CORS settings. Deployed-URL smoke checks in quickstart step 8 remain pending deployment.

## Checks and timing

| Check | Result |
| --- | --- |
| `UV_CACHE_DIR=/private/tmp/nus-uv-cache uv run --directory backend pytest -q` | 6 passed; one upstream Starlette `httpx` deprecation warning |
| `UV_CACHE_DIR=/private/tmp/nus-uv-cache uv run --directory backend ruff check .` | Passed |
| `npm run lint --prefix frontend` | Passed |
| `npm run typecheck --prefix frontend` | Passed |
| `npm run build --prefix frontend` | Passed; `/` and `/compare` statically prerendered |
| `UV_CACHE_DIR=/private/tmp/nus-uv-cache npm run test:e2e --prefix frontend` | 7 passed |
| Warmed Recommend selection to five rendered cards | 113.9 ms in Chromium, under one second |
| Cold backend Python process import, catalog startup, and schema access | 0.49 s real time via `/usr/bin/time -p env UV_CACHE_DIR=/private/tmp/nus-uv-cache uv run --directory backend python -c 'from app.main import app; print(len(app.openapi()["paths"]))'` |

The warmed figure is a local development-browser measurement, not a production latency guarantee. The cold figure measures backend process startup and schema access, not a deployed Vercel cold request. Production timings require deployment.

## OpenAPI contract comparison

`backend/tests/test_contract.py` checks the generated FastAPI schema against `plan/contracts/openapi.yaml`: the contract's `/api/v1` server prefix resolves to the generated path names; required query parameters, all response status codes, top-level and nested 200 response fields, and 404/503 `detail` bodies match. The contract now records FastAPI's generated 422 response for missing required query parameters. Optional `title` and `units` course fields stay optional in the schema and are omitted at runtime when absent. The generated schema permits null for those fields, but successful responses omit null fields through `response_model_exclude_none=True`.

## Count clarity regression validation

T033 was run on 2026-10-20 after T031 and T032.

| Check | Result |
| --- | --- |
| `UV_CACHE_DIR=/private/tmp/nus-uv-cache uv run --directory backend pytest -q` | 7 passed; one upstream Starlette `httpx` deprecation warning |
| `UV_CACHE_DIR=/private/tmp/nus-uv-cache uv run --directory backend ruff check .` | Passed |
| `npm run lint --prefix frontend` | Passed |
| `npm run typecheck --prefix frontend` | Passed |
| `UV_CACHE_DIR=/private/tmp/nus-uv-cache npm run test:e2e --prefix frontend` | 8 passed in Chromium |

Count evidence from the catalog and both endpoints:

- Artificial Intelligence–University of Toronto: **9 mappable partner modules**, **6 distinct NUS modules**, **9 mapping rows**. The browser card shows all three labels and values, Compare's summary repeats them, and all nine `.mapping-row` elements remain visible. `CS3230` appears three times and `CS4248` twice, which the short summary explanation calls out.
- Artificial Intelligence–Yonsei University: 4 partner modules, 3 NUS modules, 4 mappings.
- Artificial Intelligence–University of Western Australia, The: 0/0/0. The Compare summary shows zero for all three values and the no-qualifying-mappings empty state appears.
- Business Analytics–University of Western Australia, The: **19 mappable partner modules**, **11 distinct NUS modules**, **22 mapping rows**, matching the required 19-partner/22-row regression example.
- The new Playwright scenario selects Artificial Intelligence by keyboard, asserts Toronto is rank #1 with the 9/6/9 card labels, follows View Mappings, checks the 9/6/9 Compare summary and nine rows, then selects the zero-count partner and checks the 0/0/0 summary and empty state.

## NUS ranking and card-size validation

T038 was run on 2026-10-20 after T034–T037. No API response fields changed; only the ordering and card layout changed.

| Check | Result |
| --- | --- |
| `UV_CACHE_DIR=/private/tmp/nus-uv-cache uv run --directory backend pytest -q` | 8 passed; one upstream Starlette `httpx` deprecation warning |
| `UV_CACHE_DIR=/private/tmp/nus-uv-cache uv run --directory backend ruff check .` | Passed |
| `npm run lint --prefix frontend` | Passed |
| `npm run typecheck --prefix frontend` | Passed |
| `UV_CACHE_DIR=/private/tmp/nus-uv-cache npm run test:e2e --prefix frontend` | 9 passed in Chromium |

Ranking evidence:

- Business Analytics rank order differs between the old partner-count key and the active NUS-count key. Partner order is Western Australia (19), Toronto (18), Korea (17), Yonsei (10), Kyoto (2); NUS order is Korea (11), Western Australia (11), Toronto (9), Yonsei (5), Kyoto (2). The Korea/Western Australia tie at 11 resolves by display name, and the Recommendation API returns that order.
- Information Security also differs: NUS order is Western Australia (6), Toronto (5), Korea (4), Yonsei (2), Kyoto (1), while partner order is Toronto (7), Western Australia (6), Korea (5), Yonsei (3), Kyoto (1).
- The synthetic regression fixture proves the keys oppose each other: partner counts rank A first while distinct NUS counts rank B, C, then A. Three mapping rows for one NUS code leave that partner's NUS count at 2, and a zero-match partner stays last.
- Artificial Intelligence and Computer Science retain their previous card order because NUS and partner counts agree for those degrees.

Card-size evidence from the Playwright Recommend scenario at the 1280×720 desktop viewport (content width 1052 px with a 16 px grid gap):

| Rank | Width | Share of rank #1 |
| --- | --- | --- |
| #1 | 1052.0 px | 1.000 |
| #2 | 518.0 px | 0.492 |
| #3 | 518.0 px | 0.492 |
| #4 | 340.0 px | 0.323 |

Ranks #2 and #3 share a row. At the 390×844 narrow viewport all five cards are 342.0 px wide at x = 24 and stack in rank order; the document has no horizontal overflow. Rank #1 remains Korea University with 17 mappable partner modules, 11 distinct NUS modules, and 18 mappings, and its View Mappings link targets the encoded Compare deep link.

## Dependency note

Next.js was updated to 16.4.2 after npm audit identified a critical issue in 16.2.0. The remaining five npm audit high findings are in the development-only `eslint-config-next` dependency chain (`fast-glob`, `micromatch`, and `braces`); npm audit does not offer a compatible fix for the current Next.js lint config. Production app dependencies have no remaining audit finding in this run.
