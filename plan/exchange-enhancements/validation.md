# Validation — Exchange planner enhancements

Per-story acceptance records. Each section records the environment, the
verification method, and the observed result for the acceptance criteria of
that story.

## US1 — Faculty-aware degree selection (Phase 3, T019)

Date: 2026-10-25. Status: PASS.

### Environment and method

- Local stack exactly as the Playwright config provisions it: Next dev
  server (127.0.0.1:18766), FastAPI catalog backend in JSON mode
  (127.0.0.1:18765), preview harness (127.0.0.1:18767).
- A throwaway Playwright spec (`frontend/tests/us1-verification.spec.ts`,
  12 tests) drove both pages against a mocked catalog that records
  faculties: three faculties (School of Computing id 1, School of
  Engineering id 2, School of Business id 3) and four degrees — a
  single-faculty degree, a multi-faculty degree spanning Computing and
  Business (ids 1 and 3), and a degree with no recorded membership.
  Recommendation and mapping requests were intercepted with request
  counters so refetch behavior could be asserted, not just rendered output.
  The spec was deleted after the run; per the plan no new tests are
  committed.
- The existing Playwright suite (65 tests) was also run unmodified.

### Acceptance checks

| # | Criterion (T019) | Result | Evidence |
| --- | --- | --- | --- |
| 1 | Searchable faculty on both pages | PASS | Case-insensitive search ("busi" → 1 option), ArrowDown/Enter selection, no-match state "No matching faculty." on Recommend; search-and-select exercised on Mappings via the same shared component. |
| 2 | Single-faculty degree auto-selection | PASS | Selecting Mechanical Engineering set the faculty to School of Engineering. |
| 3 | Multi-faculty degree auto-selection | PASS | Selecting Business Computing (ids 1 and 3) set the faculty to School of Business — the alphabetically first name, which also proves derivation is by name, not by smallest id. A degree without recorded membership stayed selected with the faculty unset. |
| 4 | Compatible retention | PASS | With Business Computing selected (faculty School of Business, 3 results), switching faculty to School of Computing kept the degree, the results, and fired zero additional recommendation requests. On Mappings the university, degree, mapping rows and URL all stayed consistent with exactly one mapping request. |
| 5 | Incompatible clearing | PASS | Switching faculty to School of Engineering cleared the degree and its results with no extra request; the degree list under the new faculty contained only Mechanical Engineering and the unaffiliated degree stayed hidden. On Mappings the university stayed selected, the result section was removed, and the URL dropped `degree` while keeping `faculty` and `uni`. |
| 6 | Clear controls | PASS | The Clear action emptied the faculty, kept the degree and its 3 results, and reopened all four degree options. |
| 7 | Existing result counts | PASS | Computer Science → 2 recommendation cards, Business Computing → 3; Mappings showed the mocked "2 mappable partner modules · 2 distinct NUS modules · 2 mappings" summary and 2 mapping rows. |

### Mappings URL and reload behavior

- Faculty is encoded alongside `degree`/`uni` (verified on the committed URL
  after an async `router.replace`; e.g. `faculty=School of Computing` after a
  compatible change).
- Mappings refetch only when the effective degree/university pair changes:
  across multiple faculty changes the mapping request counter stayed at 1;
  selecting a new degree under the active faculty raised it to exactly 2.
- A deep link with an inconsistent faculty+degree pair keeps the degree and
  drops the faculty, so mappings for the linked degree still load.

### Regression evidence

- Full Playwright suite after the change: 77/77 passed (65 existing + 12 US1
  verification tests).
- The faculty control renders only when the catalog records at least one
  faculty, so faculty-less catalogs (all existing fixtures and the JSON-mode
  backend) render byte-identical layouts: the pixel-pinned Recommend anchors
  (picker at 726/405, card rows at 512/839/1095) and the two-column Mappings
  grid are asserted by the unmodified specs and pass.
- `npm run typecheck`, `npm run lint`, and `npm run build` all pass after the
  change; the e2e suite ran against the dev server.

### Behavior decisions recorded during verification

- Clearing the degree also clears the faculty derived from it (FR-05
  atomicity); a selected degree with no faculty is a documented valid state.
- A Mappings deep link with an unknown faculty value gets its own note copy;
  the original degree/university note copy is unchanged byte-for-byte so
  existing links read exactly as before.
- `.selectors` switched from `1fr 1fr` to `repeat(auto-fit, minmax(280px,
  1fr))`: with two controls the track geometry is identical to before; with
  three it adds the faculty column on desktop widths.

## US2 — Geographic filtering (Phase 4, T025)

Date: 2026-10-25. Status: PASS.

### Environment and method

- Local stack exactly as the Playwright config provisions it: Next dev
  server (127.0.0.1:18766), FastAPI catalog backend in JSON mode
  (127.0.0.1:18765), preview harness (127.0.0.1:18767).
- A throwaway Playwright spec (`frontend/tests/us2-verification.spec.ts`,
  12 tests) drove the Recommend page against a mocked geography-rich catalog:
  seven universities covering a duplicate city name (Springfield in two
  countries), a null-geography university, a city (Sapporo) that belongs only
  to a university absent from the recommendations, and two Toronto
  universities sharing one (city, country) pair — plus seven recommendations
  including "Ghost University", a name absent from the catalog. Recommendation
  requests were intercepted with a counter so the no-refetch behavior could be
  asserted, not just rendered output. The spec was deleted after the run; per
  the plan no new tests are committed.
- The pure module logic (option derivation, matching, reconciliation) was also
  checked with a 24-case node harness against the same scenario data.
- The existing Playwright suite (65 tests) was also run unmodified.

### Acceptance checks

| # | Criterion (T025) | Result | Evidence |
| --- | --- | --- | --- |
| 1 | Multiple continents/countries/cities (OR within a category) | PASS | Asia + Europe → 3 cards in original relative order; both Springfields selected → 2 cards; Canada country alone → the 3 Canada recommendations. |
| 2 | Duplicate city names | PASS | With no parents the city panel offers "Springfield, France" and "Springfield, Korea" (unique names stay plain); selecting only the France key matches only Springfield Tech; under an Asia-only constraint the label reverts to the plain "Springfield". |
| 3 | Invalid child pruning on parent change | PASS | Asia+Europe + France+Japan + both visible cities selected; unchecking Europe pruned France from the country chips and the orphaned Springfield from the city chips while keeping Kyoto, leaving exactly the Kyoto Institute card. Clearing the country kept the still-valid city; previously pruned values were never re-added. |
| 4 | Null geography | PASS | The null-city/null-continent university drops out under an active continent or city category but stays visible with none active. The catalog-unknown recommendation matches the country category (country travels with the recommendation) but never the continent or city categories. |
| 5 | AND across categories | PASS | Asia+Europe then Country Korea → exactly the one Korea card; Asia then City Sapporo → zero matches (only a non-recommended university has that city). |
| 6 | Immediate update | PASS | Across continent → country → city changes and the reset, the recommendation request counter stayed at 1; no refetch, no reordering. |
| 7 | Original recommendation order restored on reset | PASS | From the filtered-empty state, "Reset filters" restored all 7 cards in exact API order with the placeholders ("Any continent" / "Any city") back and the counter still at 1. |
| 8 | Filtered-empty feedback | PASS | Zero matches renders "No universities match the selected geography." (role=status) with the Reset control; distinct from the no-degree hint and the service-failure alert, and from a degree with zero results. |
| 9 | Dependent option constraints | PASS | Asia → country options exactly Japan/Korea (no France/Canada); city options constrained by continents and countries alike. |
| 10 | No geography in catalog | PASS | A catalog with no recorded city/continent renders no filter row and unchanged results (regression guard for all existing fixtures). |

### Regression evidence

- Full Playwright suite after the change: 77/77 passed (65 existing + 12 US2
  verification tests).
- The filter row renders only when the catalog records a non-null city or
  continent on at least one university, so faculty-less/geography-less
  catalogs (all existing fixtures and the JSON-mode backend) render
  byte-identical layouts: the pixel-pinned Recommend anchors (picker at
  726/405, card rows at 512/839/1095) are asserted by the unmodified specs
  and pass.
- `npm run typecheck`, `npm run lint`, and `npm run build` all pass after the
  change; the e2e suite ran against the dev server.

### Behavior decisions recorded during verification

- The filter row's visibility trigger is a non-null `city` or `continent`
  (country is always present and would make the row unconditional).
- Visible card ranks are numbered by visible position (the existing card
  contract); filtering keeps the API relative order and the reset restores
  it, which is what "no reordering of the ranking" guarantees.
- Duplicate-city disambiguation is computed over the *visible* option set, so
  labels switch between "Springfield" and "Springfield, Country" as parent
  constraints change; the selection key is always the (city, country) pair.
- Parent reconciliation only ever prunes: clearing a parent widens the valid
  set, so still-valid dependent selections survive, and values pruned by an
  earlier narrowing are not re-added.
- A filtered-empty state requires at least one loaded result; a degree with
  zero recommendations keeps the normal empty-results rendering.
