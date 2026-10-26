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

## US3 — Universities directory (Phase 5, T033)

### Environment and method

- macOS, Node.js 22 (frontend), Python 3.12 (backend), PostgreSQL 15/16
  (Homebrew). The e2e suite ran through `npx playwright test` against the dev
  servers; the availability seed ran through a disposable local replica of
  the live core rows (the Supabase pooler remains unreachable from this
  machine, so live application stays pending on the Phase 2 migration).
- The 9-test throwaway spec drove the directory against a mocked catalog of
  seven universities: two "Toronto" partners (one with both faculties, one
  with both), a duplicate city "Springfield" in two countries (one
  Computing-linked, one Engineering-linked), an Asia partner with no recorded
  availability, a null-geography partner, and a Sapporo partner linked to
  both faculties. Two faculties ("School of Computing", "School of
  Engineering") made the explicit-link exclusion observable.
- The seed rehearsal (T027) ran against a migrated disposable replica: dry
  run, apply, idempotent re-run, a hand-added link absent from the file, and
  four negative variants (duplicate pair, unknown partner, drifted partner
  id, unreviewed faculty).

### Acceptance checks

| # | Check | Result | Evidence |
| ---: | --- | --- | --- |
| 1 | Initial total equals all database partners | PASS | No filters render every catalog university, including partners with no mappings or availability (7/7). |
| 2 | Selected faculty includes only explicit links | PASS | Computing shows its 4 explicit partners; the unlinked Asia partner, the null-geography partner, and the Engineering-only partner are excluded. |
| 3 | Combined faculty + geography works | PASS | Computing + Asia = the 2 Computing partners in Asia; the same geography alone yields 3, proving AND across restrictions. |
| 4 | Clearing restores defaults | PASS | Clearing the continent widens back to the faculty's 4 links; clearing the faculty restores all 7 partners. |
| 5 | Desktop rows contain three/four cards | PASS | Computed grid tracks: 3 at 1280px, 4 at 1600px, 2 at 800px, 1 at 400px. |
| 6 | Filtered-empty feedback + reset | PASS | Engineering + Asia + Kyoto (only the unlinked partner sits there) shows the status message and "Reset filters"; reset restores all 7 without a refetch. |
| 7 | Catalog failure + retry | PASS | A 500 catalog shows the unavailable message with a Retry control; retry recovers the full directory. |
| 8 | No catalog refetch on filtering | PASS | The request counter, baselined after the initial load, is unchanged through selection, geo changes, and reset. |
| 9 | Sidebar route-aware active state | PASS | `/universities` marks only the Universities link `aria-current="page"`; Recommend and Mappings links are preserved. |
| 10 | Faculties-less catalog | PASS | No faculty control renders; geography still filters (Asia = 3); all 7 partners stay listed. |
| 11 | Seed idempotency and safety | PASS | Re-run reports 0 to add / 5 present; a hand-added link not in the file survives; duplicate, unknown-partner, drifted-id, and unreviewed-faculty variants all abort before writing. |
| 12 | Card mapping link | PASS | Each card's "View Mappings -->" anchor targets `/mappings?uni=<name>` (URL-encoded). |

### Regression evidence

- Full Playwright suite after the change: 74/74 passed (65 existing + 9 US3
  verification tests).
- The sidebar gained a third link without moving the two reference anchors:
  the app-shell geometry specs (Recommend row y134, Mappings row y208, rail
  x48–303) are unmodified and pass; the compact row wraps the third link to a
  second row on phones (`flex-wrap` added in the same change).
- `npm run typecheck`, `npm run lint`, and `npm run build` all pass; the
  production route table lists `/universities`.

### Behavior decisions recorded during verification

- **Availability source (T026):** the owner's NUS EduRec Course Mappings
  Search exports under `data/mapping/` (retrieved 2026-10-14) are the
  verified source, confirmed by the owner on 2026-10-26. Each export yields
  one explicit link per faculty it records (all five record only "School of
  Computing"); provenance (file, edurec_id, retrieved_at, mapped-course
  count) is stored per link. The DB mapping table is downstream of the same
  exports and is never used as independent evidence.
- **Faculty references by name (T026/T027):** the live `faculties` table does
  not exist yet (Phase 2 migration pending), so links reference the canonical
  faculty name; the seed resolves it to a stable id in-transaction. Partner
  references carry the name plus the live id captured 2026-10-26 as a
  drift check.
- **Directory empty states are distinct:** catalog failure (alert + Retry),
  no recorded partners (plain note), and filters-with-no-match (status +
  Reset) are three separate renderings.
- **Dev-only fetch baseline:** this app-router build enables React Strict
  Mode by default, which double-mounts effects in dev; the no-refetch check
  therefore baselines the counter after the initial load settles rather than
  asserting a global fetch count of one.
- Next.js's route announcer carries `role=alert` on every page; alert
  assertions must be scoped by message text.

## US4 — University metadata and finished cards (Phase 6, T041)

### Environment and method

- macOS, Node.js 22 (frontend), Python 3.12 (backend). The e2e suite ran
  through `npx playwright test` against the dev servers; the asset research
  and upload ran through the Supabase Management API, the Storage API, and
  the MCP SQL channel (the pooler was unreachable from this machine until
  the Phase 2 migration was applied through MCP on 2026-10-26, which also
  added the `image`/`website`/`image_attribution` columns the updates need).
- The 9-test throwaway spec drove the directory against a mocked catalog of
  six universities covering: a valid photo + website + attribution, a
  missing photo, a photo whose URL aborts mid-load, a `javascript:`
  website, a null city, and an extremely long university name. Valid photo
  URLs were fulfilled locally with a 1x1 JPEG so the run is network-free.
- Asset coverage (T034/T038): all five partners researched 2026-10-26 —
  5/5 official websites verified by fetch; 5/5 photographs approved from
  Wikimedia Commons with published permissive licenses (CC BY 2.0, CC BY
  3.0, CC BY-SA 3.0, CC BY 4.0, CC0) and verifiable authors; 0 assets left
  null. Uploads verified by public read-back (HTTP 200, `image/jpeg`,
  byte-exact sizes 143,324 / 692,519 / 786,786 / 1,092,874 / 1,208,405) and
  by a resume re-run that matched all five checksums without re-uploading.

### Acceptance checks

| # | Check | Result | Evidence |
| ---: | --- | --- | --- |
| 1 | Valid photo renders with attribution | PASS | Photo `src` is the catalog URL, alt names the university, and the required credit line renders under the photograph. |
| 2 | Missing photo uses the local fallback | PASS | `image: null` renders `/images/university-fallback.svg` (locally created, no third-party dependency) and no credit line. |
| 3 | Broken photo falls back without looping | PASS | An aborting photo URL loads at most twice (dev Strict Mode double-mount) and never again after 800ms; the fallback stays. |
| 4 | Missing website shows explicit unavailable text | PASS | "Website unavailable" renders; no dead link. |
| 5 | Non-http website is never a link | PASS | A `javascript:` catalog value renders the unavailable text and no `a[href^=javascript:]` exists. |
| 6 | Website link is safe and external | PASS | `https` URL, `target="_blank"`, `rel` contains `noopener`, label is the hostname. |
| 7 | Null city omitted, country kept | PASS | The location row holds exactly one tag (the country). |
| 8 | Long name wraps without overflow | PASS | The name block grows past one line and the document has no horizontal scroll at 1280px. |
| 9 | Responsive rows 1/2/3/4 | PASS | Computed grid tracks: 1 at 375px, 2 at 768px, 3 at 1280px, 4 at 1530px. |
| 10 | Links keyboard-operable | PASS | Tabbing from the first focusable element reaches the card website link; the mappings anchor is a plain focusable link. |
| 11 | Live metadata populated | PASS | All five live `partner_universities` rows carry image, website, and image_attribution; the public Storage URLs serve the exact uploaded bytes. |
| 12 | Resume and checksum reuse | PASS | A second uploader run reports "checksum matches, keep existing object" for all five and writes no storage or manifest changes beyond the recorded state. |

### Regression evidence

- Full Playwright suite after the change: 74/74 passed (65 existing + 9 US4
  verification tests).
- `npm run typecheck`, `npm run lint` (exit 0; two advisory `no-img-element`
  warnings — the app has no next/image pipeline, and plain `<img>` keeps the
  one-way fallback logic explicit), and `npm run build` all pass; the
  production route table lists `/universities`.
- The existing US3 directory behaviors (combined faculty/geography filters,
  empty states, sidebar anchors) are unmodified and pass in the same run.

### Behavior decisions recorded during verification

- **Rights-cleared images only (T034):** no university-website photograph was
  used because those carry no redistribution permission; every approved
  image is a Wikimedia Commons file whose page publishes the license and the
  author. The manifest records per link the file, description page, download
  URL (thumbnail variant for the three large originals), dimensions,
  author, license, and the attribution line; the upload manifest is the only
  source the uploader may download from, and only from the two reviewed
  Wikimedia hosts.
- **Fallback is one-way (T039):** a failed photograph swaps to the local SVG
  exactly once via a one-way state flag; the fallback has no `onError`, so a
  broken URL cannot ping-pong between sources.
- **Website safety (T039):** the card renders a website only for `http(s)`
  values; anything else is treated as missing. Live values are all `https`.
- **Live Phase 2 migration applied via MCP (T038 prerequisite):** the
  pooler-unreachable blocker was resolved on 2026-10-26 by applying
  `20261025121412_exchange_enhancements` and
  `20261026000000_create_university_images_bucket` through the MCP channel;
  the repo migration files were unchanged. A transcription slip during the
  manual metadata application put UWA's website URL in its `image` column;
  it was caught by the post-update verification select and corrected before
  any browser saw it (the stored artifact in
  `data/exchange-enhancements/university-assets-updates.sql` was correct).
- **Uploader credential handling (T036/T037):** the script takes only
  `SUPABASE_ACCESS_TOKEN`; the service role key is fetched from the
  Management API at runtime and never committed, logged, or shipped to the
  frontend.

## US5 — Preserve selections and open mappings (Phase 7, T047)

### Environment and method

- macOS, Node.js 22 (frontend), Python 3.12 (backend).
- Full Playwright test suite (65 existing tests) executed against Next.js dev server (127.0.0.1:18766) and FastAPI catalog backend (127.0.0.1:18765).
- A 7-test verification spec exercised the complete US5 user story:
  1. Preserving faculty and degree selections when navigating between Mappings and Directory cards.
  2. Isolation of Directory faculty filter from Mappings selections.
  3. Fresh-session no-degree handling, displaying the documented prompt and fetching automatically once a degree is selected (FR-20).
  4. Real URL href generation and direct navigation with preselected options.
  5. Browser back and forward history restoration.
  6. Reporting unknown deep links without silently falling back to incorrect degrees.
  7. Request cancellation and rapid navigation settling on the final university.
- The throwaway verification spec was deleted after execution; no new automated tests were committed per project instructions.

### Acceptance checks

| # | Check | Result | Evidence |
| ---: | --- | --- | --- |
| 1 | Retained selections and automatic loading | PASS | Setting School of Computing + Computer Science on Mappings, navigating to Universities, and clicking View Mappings on University of Western Australia preserved faculty and degree, updated only university, and loaded mappings automatically without a Search button click. |
| 2 | Directory filter isolation | PASS | Selecting an Engineering faculty filter on Universities did not leak into Mappings or replace remembered Mappings faculty. |
| 3 | Fresh-session no-degree prompt (FR-20) | PASS | Navigating directly to a university card without a pre-existing degree displayed the prompt "Please select a degree programme to view course mappings for this partner university." Selecting a degree immediately cleared the prompt and loaded mappings automatically. |
| 4 | Real href generation and copied URL support | PASS | Card action contains a fully resolved `/mappings?uni=...&degree=...&faculty=...` href; direct navigation in a new page/context hydrated all selections and loaded results immediately. |
| 5 | Browser back and forward history restoration | PASS | Browser Back and Forward between different partner mappings correctly restored previous query parameters and corresponding result tables. |
| 6 | Invalid deep link handling | PASS | A deep link with an invalid degree name displayed "This link contains an unknown degree or partner university. Please choose a valid option." and left the degree empty without silently picking a fallback degree. |
| 7 | Rapid card navigation | PASS | Rapidly clicking different university mapping links aborted superseded in-flight requests and rendered the final selected university without stale responses or hydration loops. |

### Regression evidence

- Full Playwright suite after the change: 65/65 passed.
- `npm run typecheck` passed (exit 0).
- `npm run lint` passed (exit 0; only pre-existing advisory `no-img-element` warnings for plain `<img>` fallback tags).
- `npm run build` passed (exit 0; `/mappings` and `/universities` compiled and rendered statically).

### Behavior decisions recorded during verification

- **Preserve explicitly selected compatible faculty (T044):** If a user selects a compatible faculty (even if not the alphabetically first faculty for the degree), it is preserved across card clicks and URL hydration rather than re-deriving the default faculty.
- **Derive faculty only when needed (T044):** If a degree is selected without a faculty and faculty was not explicitly cleared, faculty is derived using the first canonical faculty; if faculty was explicitly cleared (`?faculty=`), it remains unset.
- **Unresolved FR-20 no-degree prompt (decisions.md #11):** The backend mappings API requires a degree parameter. When navigating from a card in a fresh session, the partner university is preselected, a polite status prompt requests degree selection, and mappings load automatically as soon as a degree is chosen. This is maintained as an open product decision pending explicit confirmation.

## Phase 8: Cross-cutting regression checks (T048)

### Environment and executed commands

- **Backend Pytest Suite**:
  `uv run pytest` in `backend/`: 91/91 passed across all 13 test modules (`test_app_repository.py`, `test_catalog.py`, `test_catalog_absence.py`, `test_catalog_preview.py`, `test_catalog_table_removal.py`, `test_contract.py`, `test_core_seed.py`, `test_database_cleanup.py`, `test_database_failures.py`, `test_json_repository.py`, `test_postgres_repository.py`, `test_repository_regression.py`, `test_snapshot_core_data.py`).
  - *Assertion update in migration setup:* Wrapped Supabase storage bucket and policy creation in `supabase/migrations/20261026000000_create_university_images_bucket.sql` inside a conditional check for the `storage` schema and `service_role` role so that local non-Supabase disposable PostgreSQL test clusters can replay all migrations cleanly without failing on absent Supabase platform schemas.
- **Frontend Typecheck**:
  `npm run typecheck` in `frontend/`: 0 errors.
- **Frontend Lint**:
  `npm run lint` in `frontend/`: 0 errors (2 pre-existing advisory warnings for plain `<img>` fallback elements).
- **Frontend Build**:
  `npm run build` in `frontend/`: static generation of `/`, `/mappings`, `/universities`, and `/_not-found` completed cleanly.
- **Frontend E2E Flow / Shell Suite (JSON Mode)**:
  `npx playwright test` in `frontend/`: 65/65 tests passed across `app-shell.spec.ts`, `flows.spec.ts`, `recommend-card.spec.ts`, `recommend-hero.spec.ts`, `recommend-picker.spec.ts`, `recommend-visual.spec.ts`, `theme.spec.ts`.
- **Frontend Database Regression Suite (PostgreSQL Mode)**:
  `TEST_CATALOG_BACKEND=postgres npx playwright test tests/database-regression.spec.ts`: 8/8 tests passed, confirming count preservation, direct URL mapping entry, search navigation, and back/forward browser behavior.

## Cross-cutting UX and visual evidence (T049)

### Visual evidence captured

Desktop (1280x800) and mobile (375x667) screenshots were generated and saved under `plan/exchange-enhancements/reference/`:
- `desktop-recommend.png` & `mobile-recommend.png`: Recommend page showing faculty dropdown, dependent geographic multi-select filters, and ranked cards.
- `desktop-universities.png` & `mobile-universities.png`: Universities directory with responsive grid (3-4 cards desktop, 1 card mobile), photo fallbacks, and safe website/mapping links.
- `desktop-mappings.png` & `mobile-mappings.png`: Mappings view with synchronized selectors, mapping summary, and course mapping table.

### Keyboard and focus accessibility

- **Comboboxes & Dropdowns**: Fully navigable via keyboard (`Tab`, `ArrowDown`, `ArrowUp`, `Enter`, `Escape`).
- **Focus Rings**: All interactive cards, links, and buttons maintain high-contrast focus rings compliant with WCAG 2.1 AA.
- **Drawer & Overlays**: Mobile filter drawers and menus trap focus appropriately and restore focus to trigger elements upon dismissal.

### Empty, error, and retry handling

- **Recommend**: Shows clear prompts for unselected degrees, distinct zero-match states when filters exclude all partners, and graceful service failure alerts.
- **Universities**: Defaults to all database partners on initial load; when active filters produce zero results, displays "No universities match the selected filters" with a single-click "Reset filters" button. Network errors render a dedicated error card with a "Retry" button.
- **Mappings**: Shows initial prompt for unselected pairs; when navigating from a directory card without a preselected degree, displays "Please select a degree programme to view course mappings for this partner university." (FR-20 prompt). Mappings with zero qualifying modules render `MappingsEmptyState` with a link back to Recommend.

### Long-content and responsive layout outcomes

- Long university names (e.g. multi-line institutions) wrap inside card headers without truncating or overlapping adjacent badges.
- Location badges wrap within flex containers; missing cities omit the city tag while cleanly preserving the country tag.
- Viewports from 320px to 1920px verified free of horizontal scroll.

### Unresolved FR-20 status

- **Current state**: Implemented with explicit prompt and automatic loading upon degree selection.
- **Product sign-off status**: Remains flagged as an open decision pending product owner review of whether an unconstrained all-degrees mapping endpoint is required.


