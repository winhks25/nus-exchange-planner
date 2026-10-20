# Tasks: NUS Exchange Planner MVP

Source documents: `plan/featureSpecs.md`, `plan/implementation-plan.md`, `plan/data-model.md`, `plan/contracts/openapi.yaml`, and `plan/quickstart.md`.

This checkout has no `.specify/` directory, so the Spec Kit setup script and template are unavailable. This file follows the specified phase and checklist format under the existing `plan/` directory. The spec defines two user stories, ordered by page priority: **US1 Recommend** and **US2 Compare**. The original MVP spec did not request TDD tasks; the count repair explicitly requires regression checks in T028 and T032.

T001–T027 document the completed MVP implementation. T028–T033 document the completed count repair. T034–T038 document the completed Recommend ranking and layout change; these supersede partner-count ranking in completed T028–T029 and the original compact-grid layout in completed T016. Completed tasks remain as implementation history. T039–T052 are the pending frontend component work requested after those changes. The existing spec explicitly requires browser regression checks; T039 updates it for the new picker and card requirements.

## Phase 1: Setup

- [X] T001 Create the Python backend package and pin Python 3.12+, FastAPI, Pydantic, Uvicorn, and development dependencies in `backend/pyproject.toml` and `backend/uv.lock`.
- [X] T002 [P] Initialize Next.js App Router with React, TypeScript, npm lockfile, lint, and typecheck scripts in `frontend/package.json`, `frontend/package-lock.json`, `frontend/tsconfig.json`, and `frontend/app/layout.tsx`.
- [X] T003 Add environment examples for browser API URL and allowed origins in `frontend/.env.example` and `backend/.env.example`; use `NEXT_PUBLIC_API_BASE_URL` for the frontend and an explicit backend CORS origin list.
- [X] T004 Add a repository-root Vercel FastAPI entry point and backend dependency manifest in `api/index.py` and `requirements.txt`, keeping the backend Vercel project root at the repository root so `data/` is included; configure the frontend Vercel project root as `frontend/` in `README.md`.

## Phase 2: Foundational catalog and API

Complete before either user story. These tasks establish one validated dataset and reusable response models.

- [X] T005 Implement source-data discovery and a generated expected-file manifest in `backend/app/catalog.py` and `backend/app/data_manifest.json`: read every `data/majors/*.json` and `data/mapping/<country>/*.json` from a path derived from the package/repository location, never the process working directory; regenerate the manifest when source files change, and fail the entire catalog when any expected file is missing or malformed.
- [X] T006 Implement typed source validation and catalog models in `backend/app/models.py`: unique major `name`, full `degree` title, unique partner display name from `partner_university.name`, mapping array as the source of truth regardless of `mapping_count`, and explicit country labels `australia` → Australia, `canada` → Canada, `japan` → Japan, `korea` → South Korea; fail on an unknown country folder.
- [X] T007 Implement degree-code extraction in `backend/app/course_codes.py`: recursively visit dictionaries and lists in each degree; extract every code only from string entries inside lists, ignore dictionary keys and standalone prose strings, match `(?<![A-Za-z0-9])[A-Z]{2,3}[0-9]{4}[A-Z]?(?![A-Za-z0-9])` case-insensitively, uppercase and deduplicate matches.
- [X] T008 Implement mapping validation and immutable per-instance catalog construction in `backend/app/catalog.py`: skip and log mappings whose NUS course code fails the code rule, preserve source titles and file order, and make all endpoints return a clear 503 if any required source file is missing or malformed rather than partial results.
- [X] T009 Implement FastAPI application startup, configured CORS, shared catalog access, and JSON error responses in `backend/app/main.py`; expose `/api/v1/catalog` with degree `{name, degree}` and university `{name, country}` options as specified in `plan/contracts/openapi.yaml`.
- [X] T010 [P] Create the typed browser API client and response types in `frontend/lib/api.ts` and `frontend/lib/types.ts`: URL-encode query values, use `NEXT_PUBLIC_API_BASE_URL`, distinguish 404 from 503/network failures, and avoid duplicating ranking or mapping calculations in the frontend.
- [X] T011 [P] Create the shared accessible degree combobox in `frontend/components/DegreeCombobox.tsx`: focus/click opens all degrees; filter case-insensitively by partial major name or full degree title; ArrowUp/ArrowDown, Home/End, Enter, and Escape follow `plan/featureSpecs.md`; expose the highlighted option with `aria-activedescendant`; show the exact no-match message and select nothing.

## Phase 3: User Story 1 — Recommend (P1)

**Goal:** A student chooses a degree on `/` and sees every partner ranked by the number of distinct qualifying NUS modules.

**Independent check:** Load `/`, select Computer Science by mouse and keyboard, confirm all partners appear in descending count/name order, a zero-count card remains accessible, and changing or clearing the degree immediately removes stale cards. No Search button appears. View Mappings produces the specified deep link.

- [X] T012 [US1] Implement one shared pair-filtering function in `backend/app/matching.py` that retains a university mapping only when its normalized NUS code is in the selected degree's code set; preserve duplicate rows for a code and source file order so Compare can reuse exactly this result.
- [X] T013 [US1] Implement ranking in `backend/app/recommendations.py`: count distinct NUS codes from the shared pair-filtered rows, include every university with zero counts, sort by count descending then university display name ascending, and return the fields in `plan/contracts/openapi.yaml`.
- [X] T014 [US1] Add `GET /api/v1/recommendations?degree=<major-name>` to `backend/app/main.py`; return 404 for an unknown degree and 503 for an unavailable catalog.
- [X] T015 [US1] Build the `/` page in `frontend/app/page.tsx` using `frontend/components/DegreeCombobox.tsx`: initially render only the empty picker; select a valid degree to fetch automatically; clear previous cards immediately on selection changes; on cleared/invalid input show exactly `Choose a degree to see results.`; show loading and service-error states without stale results.
- [X] T016 [US1] Build ranking cards in `frontend/components/UniversityCards.tsx`: display name, country, and module count; render rank #1 alone as a prominent full-width card and all others in a compact grid; keep zero-count cards visible and clickable; create `View Mappings` links to `/compare?degree=<encoded-major-name>&uni=<encoded-university-display-name>`.

## Phase 4: User Story 2 — Compare (P2)

**Goal:** A student chooses a degree and partner on `/compare` and sees every qualifying mapping row, including repeated NUS codes.

**Independent check:** Open a Recommend card's deep link; both selectors prefill, every qualifying mapping appears sorted by NUS code with stable tie order, and the distinct NUS code count equals the originating card count. Invalid URL values leave the affected selector empty with a note. A zero-match pair shows the empty state.

- [X] T017 [US2] Implement Compare projection in `backend/app/matching.py`: stable-sort shared pair-filtered rows by NUS code ascending while preserving file order for ties; retain one row per mapping; preserve source code/title/partner units; set NUS display units to 4 and leave absent partner units unset.
- [X] T018 [US2] Add `GET /api/v1/mappings?degree=<major-name>&uni=<university-display-name>` to `backend/app/main.py`, returning `degree`, `university`, `distinct_nus_module_count`, and `mappings` per `plan/contracts/openapi.yaml`; return an empty array for a valid zero-match pair, 404 for an unknown selection, and 503 for unavailable data.
- [X] T019 [US2] Build `/compare` selection and URL state in `frontend/app/compare/page.tsx`: reuse the degree combobox, add a plain partner dropdown sorted by display name with placeholder `select a partner university`, validate both URL query values against `/catalog`, show a note for invalid values, and keep valid selections encoded in the URL.
- [X] T020 [US2] Implement Compare request lifecycle in `frontend/app/compare/page.tsx`: show no rows until both selectors are valid, clear old rows immediately when either changes, ignore or cancel stale responses, and show distinct loading, empty, and service-error states.
- [X] T021 [US2] Render mapping rows in `frontend/components/MappingRows.tsx`: NUS course left and partner course right, each with code/name/units when present; display NUS units as 4, never default partner units, preserve truncated source titles, and keep repeated NUS-code rows visible.
- [X] T022 [US2] Add a no-qualifying-mappings message and a link back to Recommend in `frontend/components/CompareEmptyState.tsx`; use it only for a valid pair with an empty mappings array.

## Phase 5: Polish and cross-cutting validation

- [X] T023 Verify the current source files against the implemented loader and both endpoints; record representative pair counts, zero-count cases, source-order tie behavior, and Recommend-to-Compare distinct-code equality in `plan/validation-results.md`.
- [X] T024 Validate browser behavior against every scenario in `plan/quickstart.md`, including combobox keyboard/active-descendant behavior, invalid deep links, zero-count navigation, absent partner units, stale-request clearing, and malformed-data error state; record outcomes in `plan/validation-results.md`.
- [X] T025 Run lint, typecheck, Python checks, and a warmed under-one-second rendering measurement for the current dataset; record commands, results, and separately measured cold-start time in `plan/validation-results.md`.
- [X] T026 Document exact local run commands, Vercel backend-first deployment, repository-root backend project, `frontend/` frontend project, API URL/CORS environment settings, preview API strategy, and data-change redeploy process in `README.md`.
- [X] T027 Compare the generated FastAPI `/openapi.json` with `plan/contracts/openapi.yaml`, reconcile path prefixes, response fields, required query parameters, and 404/503 behavior in `backend/app/main.py` or the contract file, then record the result in `plan/validation-results.md`.

## Phase 6: Foundational count consistency repair

Complete before the new card and Compare labels. This phase corrects the ranking metric to distinct partner modules and makes all three counts available from the same qualifying pair filter.

- [X] T028 Add regression assertions in `backend/tests/test_catalog.py` and `backend/tests/test_contract.py` for all three filtered counts, partner-count ranking and tie order, all current degree–university pairs, duplicate partner-code rows, and zero-match pairs; assert Artificial Intelligence–Toronto is 9 partner/6 NUS/9 rows and Business Analytics–Western Australia is 19 partner/22 rows; require the revised fields in the API contract comparison.
- [X] T029 Replace the ambiguous recommendation `module_count` with `partner_module_count` and add `distinct_nus_module_count` and `mapping_count` in `backend/app/models.py`, `backend/app/recommendations.py`, `plan/contracts/openapi.yaml`, and `frontend/lib/types.ts`; add `partner_module_count` to Compare in `backend/app/models.py` and `backend/app/main.py`; calculate distinct uppercase partner codes, distinct uppercase NUS codes, and `len(pair_mappings(...))` from qualifying rows, rank by partner count descending then name, make T028 pass, and never use source JSON `mapping_count`.

## Phase 7: User Story 1 — Recommend count clarity (P1)

**Goal:** A student sees the actual number of distinct mappable partner modules and can distinguish it from NUS modules and mapping entries before opening Compare.

**Independent check:** Select Artificial Intelligence on `/`; the University of Toronto card shows 9 mappable partner modules, 6 distinct NUS modules, and 9 mappings with unambiguous labels. Its place in the ranking follows the partner-module count. A zero-match card shows 0 for all three.

- [X] T030 [US1] Update `frontend/components/UniversityCards.tsx` and `frontend/app/globals.css` to display `partner_module_count` as the primary “mappable partner modules” value, with `distinct_nus_module_count` and `mapping_count` as separately labeled secondary values on every card, including zero-count cards and the prominent first card.

## Phase 8: User Story 2 — Compare count clarity (P2)

**Goal:** A student can reconcile the partner-module, NUS-module, and mapping-row counts with the Compare list.

**Independent check:** Open the Toronto card's View Mappings link; Compare shows 9 distinct partner modules, 6 distinct NUS modules, 9 mappings, and a short explanation of repeated course codes while all 9 rows remain visible.

- [X] T031 [US2] Update the result summary in `frontend/app/compare/page.tsx` to use the same partner-module, NUS-module, and mapping labels as Recommend and explain repeated course codes; consume the API's `partner_module_count` and `distinct_nus_module_count`, use `result.mappings.length` for the row label, and preserve every row in `frontend/components/MappingRows.tsx`.

## Phase 9: Count regression validation

- [X] T032 Add a Playwright scenario in `frontend/tests/flows.spec.ts` that selects Artificial Intelligence, checks Toronto's 9 partner/6 NUS/9 mapping card labels and ranking, follows View Mappings, checks the matching Compare summary and nine visible rows, then checks a zero-count pair.
- [X] T033 Run the backend tests, frontend lint/typecheck, and Playwright suite; record the commands, results, the Toronto 9/6/9 evidence, and the Western Australia 19-partner/22-row evidence in `plan/validation-results.md`.

## Phase 10: User Story 1 — Recommend NUS ranking and card sizes (P1)

**Goal:** A student sees partners ordered by how many distinct NUS modules they map, with card widths that follow rank: #1 full grid width, #2–#3 half width each, and all later cards one third width each at desktop size. Keep the three existing count labels; the primary displayed partner count does not determine rank.

**Independent check:** Select a degree where partner-module and NUS-module ordering differ; the cards follow distinct NUS count descending, then university name ascending for ties, with zero-count partners last. At desktop width #1 spans six grid tracks, #2 and #3 span three each, and #4 onward span two each. At narrow width all cards stack in rank order without horizontal overflow, and every View Mappings link remains usable.

- [X] T034 [US1] Update ranking regression cases in `backend/tests/test_catalog.py`: assert all current degree–university recommendations sort by `(-distinct_nus_module_count, university)`, add a synthetic pair where partner counts and NUS counts imply opposite orders, keep an alphabetical tie and a zero-match case, and verify duplicate mapping rows for one NUS code do not raise its rank.
- [X] T035 [US1] Change the sort key in `backend/app/recommendations.py` to `(-distinct_nus_module_count, university)` while retaining `partner_module_count`, `distinct_nus_module_count`, and `mapping_count` from the shared qualifying rows and including zero-count universities; make T034 pass without changing the API response fields.
- [X] T036 [P] [US1] Update the Recommend grid in `frontend/app/globals.css` and rank classes in `frontend/components/UniversityCards.tsx` so desktop cards span six, three, and two tracks for rank #1, ranks #2–#3, and rank #4 onward respectively; make the narrow-screen layout one column with no overflow and preserve readable count labels and clickable links.
- [X] T037 [US1] Update `frontend/tests/flows.spec.ts` to assert Recommend follows distinct NUS count order, preserves the three count labels and Compare deep link, and measures rank #2/#3 and later card widths against rank #1 at desktop viewport with grid-gap tolerance; also assert stacked cards and no horizontal overflow at a narrow viewport.

## Phase 11: Recommend change validation

- [X] T038 Run backend pytest, frontend lint/typecheck, and the focused Recommend Playwright flows; record commands, results, one degree where partner and NUS rank order differ, and desktop/mobile card-width evidence in `plan/validation-results.md`.

## Phase 12: Setup — shadcn/ui and updated requirements

- [X] T039 Update `plan/featureSpecs.md` and `plan/implementation-plan.md` to require a visible rank number, prominent university name, country, distinct NUS and distinct partner module counts, and a **View Mapping** action on every Recommend card; specify a shared typable picker for both degree fields and the Compare partner field, shadcn/ui Base UI Card for university and mapping cards, and preservation of the existing mapping-row count, ranking, URL, and responsive rules.
- [X] T040 Configure shadcn/ui for the existing Next.js app using the Base UI variant in `frontend/components.json`, `frontend/package.json`, `frontend/package-lock.json`, `frontend/postcss.config.mjs`, and `frontend/app/globals.css`: add the required Tailwind CSS pipeline and theme tokens while preserving the existing `@/*` alias, six-track card layout, and narrow-screen behavior; document the chosen setup in `plan/research.md`.

## Phase 13: Foundation — reusable frontend primitives

Complete before either new story phase. Keep `frontend/components/ui/` for reusable shadcn primitives and `frontend/components/` for domain components.

- [X] T041 [P] Add the shadcn/ui Base UI `Card`, `CardHeader`, `CardTitle`, `CardDescription`, `CardContent`, and `CardFooter` primitives in `frontend/components/ui/card.tsx`, plus the shadcn `Button` and `Input` primitives in `frontend/components/ui/button.tsx` and `frontend/components/ui/input.tsx`; add the shared class-name utility in `frontend/lib/utils.ts` and keep the installed variants identifiable as shadcn components.
- [X] T042 Build a controlled, generic typable picker in `frontend/components/ui/typable-dropdown.tsx` using the shared `Input`: accept typed options, value, label, placeholder, search text, display content, and empty message; support click/focus to show all options, case-insensitive filtering, mouse selection, clearing, ArrowUp/Down, Home/End, Enter, Escape, `aria-activedescendant`, and a labeled listbox without selecting unmatched text.
- [X] T043 Refactor `frontend/components/DegreeCombobox.tsx` into a thin adapter over `frontend/components/ui/typable-dropdown.tsx`, preserving the major-name stored value, major/full-degree search, full title in each option, exact no-match message, and existing selection callback used by both pages.

## Phase 14: User Story 1 — complete Recommend university cards (P1)

**Goal:** Every ranked university card uses shadcn/ui Card and clearly presents the rank, large university name, country, distinct NUS module count, distinct partner module count, mapping-row count, and View Mapping action.

**Independent check:** Select Artificial Intelligence on `/`. Toronto appears at rank #1 with 6 distinct NUS modules, 9 distinct partner modules, and 9 mappings. All five cards expose the same fields, including zero-count cards; View Mapping opens the encoded Compare deep link. Desktop rank widths and narrow-screen stacking remain intact.

- [ ] T044 [US1] Extract one reusable `UniversityCard` in `frontend/components/UniversityCard.tsx` composed from `frontend/components/ui/card.tsx` and a Button-styled Next.js link: show `#<position>`, a visibly larger `CardTitle` for the university name, country, separately labeled `distinct_nus_module_count`, `partner_module_count`, and `mapping_count`, and the **View Mapping** action with the existing encoded `/compare?degree=...&uni=...` link.
- [ ] T045 [US1] Make `frontend/components/UniversityCards.tsx` map API-ordered recommendations to `UniversityCard` and update `frontend/app/globals.css` so the shadcn Card keeps rank #1 full width, #2–#3 half width, later cards one-third width on desktop, and one column without overflow on narrow screens; keep card order, zero-count visibility, readable labels, and keyboard-visible action focus.
- [ ] T046 [US1] Update Recommend assertions in `frontend/tests/flows.spec.ts` for all required university-card fields, prominent title, shadcn Card composition, exact View Mapping link/action, Toronto 9/6/9 counts, zero-count cards, and existing rank order and responsive widths.

## Phase 15: User Story 2 — typable Compare partner and mapping cards (P2)

**Goal:** Compare uses the same typable picker for both selectors, and each mapping row is a shadcn/ui Card while preserving the one-row-per-mapping view.

**Independent check:** Open a Recommend View Mapping link; both pickers prefill from the URL. Type part of a partner name, choose it by mouse or keyboard, and confirm the URL and mapping list update. Invalid URL values and unmatched text leave the affected selector empty with a note. Every qualifying mapping remains a separate Card, including repeated NUS codes and absent partner units.

- [X] T047 [P] [US2] Create `frontend/components/UniversityCombobox.tsx` as a thin adapter over `frontend/components/ui/typable-dropdown.tsx`: sort partners by display name, filter partial names case-insensitively, retain the `select a partner university` placeholder, and use the university name as the selected value.
- [X] T048 [US2] Replace the native partner `<select>` in `frontend/app/compare/page.tsx` with `UniversityCombobox`; use the shared picker for the degree field through `DegreeCombobox`, preserve URL prefill/validation and encoded URL updates, clear stale results immediately on edits, and retain loading, empty, and service-error states.
- [ ] T049 [P] [US2] Refactor `frontend/components/MappingRows.tsx` so each mapping is composed from shadcn `Card` sections; extract reusable course-side markup into `frontend/components/CourseDetails.tsx`, keep NUS left and partner right, preserve code/title/units, NUS display units of 4, absent partner units as blank, sorted order, and duplicate rows; adapt `frontend/app/globals.css` for small screens.
- [ ] T050 [US2] Update Compare flows in `frontend/tests/flows.spec.ts` to select a partner by typing, mouse, and keyboard; verify URL prefill, invalid/unmatched input, stale-request clearing, zero-match state, and mapping Card rows with repeated NUS codes, source titles, and absent partner units.

## Phase 16: Polish and cross-cutting validation

- [ ] T051 Refactor repeated page-level presentation in `frontend/app/page.tsx`, `frontend/app/compare/page.tsx`, and `frontend/components/ResultState.tsx` into small shared components for loading/error/empty messages where the behavior is identical; remove obsolete `.card`, `.mapping-row`, and native-select styling from `frontend/app/globals.css` while retaining page-specific layout and avoiding new API/count logic in the frontend.
- [ ] T052 Run `npm run lint`, `npm run typecheck`, `npm run build`, and the focused Playwright Recommend/Compare flows from `frontend/`; record outcomes and any accessibility or responsive limitations in `plan/validation-results.md`.

## Dependencies

```text
Setup T001–T004
  -> Foundation T005–T011
  -> US1 T012–T016
  -> US2 T017–T022
  -> Polish T023–T027
  -> Count foundation T028–T029
  -> US1 count clarity T030
  -> US2 count clarity T031
  -> Count validation T032–T033
  -> US1 NUS ranking T034–T035
  -> US1 rank card widths T036
  -> Recommend validation T037–T038
  -> Frontend requirements and shadcn setup T039–T040
  -> Shared primitives and picker T041–T043
  -> US1 university cards T044–T046
  -> US2 Compare picker and mapping cards T047–T050
  -> Frontend polish and validation T051–T052
```

US2 reuses the shared pair filter created in US1. T010 and T011 can proceed while backend catalog/API tasks are underway after setup. T023–T025 require both stories; T026 can be drafted earlier and finalized after deployment configuration is known.

T028 defines the count regression before T029 changes the API. T030 and T031 depend on T029 and can be implemented in parallel because they touch separate page components. T032 requires both pages; T033 requires every repair task.

T034 defines the new ranking regression before T035 changes the sort key. T036 touches separate frontend files and can proceed in parallel with T034–T035. T037 requires both the API order and layout; T038 follows all new tasks. This phase supersedes the historical partner-count rank rule without changing count meanings or Compare.

For the pending frontend work, T039 fixes the acceptance rules and T040 installs the existing-project shadcn setup. T041 makes Card/Button/Input available; T042 builds the generic picker and T043 adapts degree selection. T044–T045 depend on Card and Button, while T046 follows the completed Recommend UI. T047 depends on T042, T048 on T043 and T047, and T049 on Card. T050 follows T048–T049. T051 follows both page phases; T052 follows every pending task. No backend or API contract change is needed because both distinct counts and the mapping-row count already exist in `frontend/lib/types.ts`.

## Parallel examples

- **Setup:** T001 backend package and T002 frontend package touch separate files.
- **Foundation:** After API response shapes are fixed, T010 API client and T011 combobox touch separate frontend files and can proceed alongside backend catalog work.
- **US1:** After T014 fixes the endpoint behavior, T015 page state and T016 cards touch separate files; integrate them before the independent check.
- **US2:** After T018 fixes the endpoint behavior, T019 URL/selectors and T021 row display touch separate files; T020 integrates their request lifecycle.
- **Count repair:** After T029, T030 Recommend card labels and T031 Compare summary labels touch separate files and can proceed in parallel.
- **Recommend change:** T034 backend ranking tests and T036 frontend card grid touch separate files and can proceed in parallel; T037 follows both T035 and T036.
- **Frontend components:** After T040, T041 can be completed before the shared picker and either card. Once T041–T043 finish, T044 `UniversityCard` and T047 `UniversityCombobox` touch separate files and can proceed in parallel. T049 mapping cards can proceed alongside T047–T048 because it touches separate components; T046 and T050 follow their respective UI work.

## Implementation strategy

Build a working vertical slice for US1 first: validated catalog → recommendations endpoint → degree picker → cards and deep links. This is the smallest useful MVP increment. Then add US2 using the same pair filter; Compare makes the displayed counts auditable and completes the two-page MVP. Finish with cross-page checks and Vercel deployment documentation. Do not add accounts, a database, planning advice, approval status, timetable logic, credit conversion, or JSON editing.

For the count repair, rank by distinct mappable partner modules as defined in `plan/overview.md`, expose distinct NUS modules and qualifying mapping rows beside it, then verify all three numbers on Recommend and Compare. The first independently useful increment is the Toronto 9/6/9 card and matching deep link; complete the all-pair regression checks before marking the repair done.

For the new Recommend increment, use distinct NUS modules as the ranking key while retaining all three count values, then apply the six-track card grid and verify desktop proportions and narrow-screen stacking. The completed count repair above is historical; `plan/featureSpecs.md` now defines the active ranking and layout acceptance rules.

For the pending frontend increment, configure shadcn/ui for this existing app, build one accessible typable picker, and complete the Recommend cards first as the smallest independently useful slice. Then use the same picker in Compare and render each mapping row with shadcn Card. Finish by consolidating repeated presentation and validating both flows; keep counts and rank order sourced from the existing API.
