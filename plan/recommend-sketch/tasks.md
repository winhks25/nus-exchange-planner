# Tasks: Recommend layout with NUSMods theme and shared application shell

Generated: 2026-10-21. Status: Phases 1–7 complete (baseline, fixtures, US1 theme, US2 shell/header, US3 sidebar, US4 hero, US5 picker); later phases pending.

## Execution contract

This checklist implements [plan.md](plan.md), [spec.md](spec.md), [data-model.md](data-model.md), [UI contract](contracts/recommend-ui.md), [NUSMods theme contract](contracts/nusmods-theme.md) and [quickstart.md](quickstart.md). Paths in tasks are repository-relative; run filesystem operations from the repository root or resolve them to absolute paths.

One phase means one cohesive change, not one file or one task. Each phase has its own verification and can be reviewed separately. Do not combine theme, shell, hero, picker, card content and card layout in one implementation diff. Setup/foundation prepare validation only; the final phase accepts the integrated work without introducing new features. Responsive behavior belongs to each component's phase.

Latest user constraints win: preserve screenshot layout/wording, use real values, share header/sidebar across every route, and use the pinned NUSMods light theme instead of the original sketch styling. Keep the current Next.js/React/TypeScript, Tailwind/Base UI and read-only API. No backend changes, dependency upgrades, Bootstrap import, custom font download or production demo content.

Workflow adaptation: setup_tasks.py --json was attempted but .specify is absent, so no FEATURE_DIR/template JSON is available. Use this existing feature directory and the skill's checklist structure. Constitution and pre/post task hook registry are absent; no hooks are registered to execute. Story IDs/priorities are added to spec.md as a decomposition of existing requirements, not new scope. Focused browser/visual validation tasks implement the acceptance scenarios already required by that specification and plan.

Each story's test can run independently once its listed prerequisites exist; independent validation does not mean all phases can be implemented out of order. Test tasks come first to define the boundary, but do not introduce a new testing framework solely for this work. [P] marks independent files within the same phase after its prerequisites pass; it is not authorization to edit shared files concurrently or to start later phases early.

## Phase 1: Setup — establish the working baseline

**Single change:** Record the existing implementation and validation state.

**Prerequisites:** None.

**Boundary:** Documentation and baseline inspection only; no application edits or dependency upgrades.

**Independent acceptance:** Baseline records existing dirty files and failing checks accurately, with no feature work marked complete.

- [X] T001 Read frontend/AGENTS.md, relevant installed Next.js layout/client-boundary guides under frontend/node_modules/next/dist/docs/, and all feature artifacts in plan/recommend-sketch/; record applicable constraints and the NUSMods source SHA in plan/recommend-sketch/validation-results.md. The missing .specify template/constitution is a workflow limitation, not an implementation blocker.
- [X] T002 Inspect the working diff in frontend/app/globals.css, frontend/app/page.tsx, frontend/components/UniversityCards.tsx and frontend/components/ui/badge.tsx; record the baseline in plan/recommend-sketch/validation-results.md and preserve those edits. Capture Recommend and Compare before changes, using the existing frontend/playwright.config.ts setup.
- [X] T003 Run the existing frontend/package.json lint, typecheck and test:e2e scripts; record outcomes in plan/recommend-sketch/validation-results.md, explicitly identifying stale .card-count/.card-secondary-counts selectors and old card-width expectations in frontend/tests/flows.spec.ts. Do not weaken data assertions to make the baseline appear green.

## Phase 2: Foundation — deterministic validation data

**Single change:** Provide one reusable test-data foundation for later isolated phases.

**Prerequisites:** Phase 1.

**Boundary:** Test-only data and helpers; no product route, production fixture switch or UI change.

**Independent acceptance:** Fixtures include reference values, API-valid unique university names, edge cases and the complete existing response shape.

- [X] T004 Create frontend/tests/fixtures/recommendations.ts with six unique synthetic universities and country/count fields matching frontend/lib/types.ts; include zero counts, 0/1/2/5/6/7-result variants and long-name/country variants. Keep API fixtures distinct from the exact-copy visual fixture: the latter has six unique internal IDs, repeated University Name/Country, counts 10/12 and displayed #1, per plan/recommend-sketch/data-model.md.
- [X] T005 Create frontend/tests/helpers/recommendation-fixtures.ts to intercept the existing catalog/recommendations endpoints with typed responses, select a valid degree and await rendered results. Keep these helpers under tests; never import them from frontend/app/page.tsx or production components. Preserve real-API scenarios in frontend/tests/flows.spec.ts.
- [X] T006 Document fixture usage and fixed OS/browser, viewport 1888×1337 and deviceScaleFactor 1 in plan/recommend-sketch/quickstart.md. Use API mocks for production-page tests; reserve repeated-placeholder display for the isolated component harness introduced in US6. The old PNG is a geometry reference, never the themed screenshot baseline.

## Phase 3: US1 — change colors, fonts and typography only

**Single change:** Apply the NUSMods theme to existing pages before changing their structure.

**Prerequisites:** Phase 2.

**Boundary:** Theme styling only: retain current DOM, page layout, card grid, wording, dimensions and navigation placement. New components use these tokens in later phases.

**Independent acceptance:** Both routes use the source system font stack, white/gray/coral tokens and role sizes; existing layout rules and behavior remain intact.

- [X] T007 [P] [US1] Add focused computed-style assertions in frontend/tests/theme.spec.ts for body font stack/16px base, white surfaces, gray text, coral interaction tokens, 1px borders and source radii; compare against plan/recommend-sketch/contracts/nusmods-theme.md. Assert existing route content/controls remain present; do not encode future sidebar or grid structure.
- [X] T008 [P] [US1] Map semantic colors, exact system font stack, 400/500/700 weights, body 1.5 and heading 1.2 line heights, .25rem control and .35rem card radii into frontend/app/globals.css. Use #ffffff background, #69707a body, #222324 emphasis, #848490 navigation, #aeb1b5 placeholders, #d3d6db borders, #f3f5f8 subtle surfaces, #ff5138 primary and #b71c1c error. Replace conflicting old token values; do not install Bootstrap or download fonts.
- [X] T009 [US1] Replace hardcoded palette/type overrides in frontend/app/globals.css with the semantic theme: apply the UI contract role table to existing selectors (brand 20, nav 16, hero 40, field 16; tier title 32/24/20 and NUS 24/20/16; partner 14, badge 12, action 14). Remove oversized-number-only treatment. Retain margins, padding, grid tracks, widths, heights and wording; note any natural text reflow caused by the requested font changes.
- [X] T010 [US1] Apply source focus/hover/placeholder/dropdown states through frontend/app/globals.css and, only where existing classes override them, frontend/components/ui/input.tsx, frontend/components/ui/button.tsx and frontend/components/ui/badge.tsx. Use the .2rem coral focus ring and specified dropdown shadow; keep Compare control labels and layout untouched.
- [X] T011 [US1] Run frontend/tests/theme.spec.ts plus relevant existing flow checks; capture both routes and record theme-only results in plan/recommend-sketch/validation-results.md. Verify changed computed typography, unchanged layout declarations and no new controls. Resolve regressions introduced by this phase before advancing.

## Phase 4: US2 — introduce the shared frame and header

**Single change:** Mount a persistent application frame and brand header once for every route.

**Prerequisites:** US1.

**Boundary:** Frame/header ownership and geometry only. The header row contains only the site name. Until US3, keep the existing navigation in a separate temporary row below the header, never inside it; do not introduce a blank sidebar or redesign Recommend content.

**Independent acceptance:** Direct loads and client navigation render exactly one frame/header with the same dimensions; children remain usable on both routes.

- [X] T012 [P] [US2] Add frame/header checks in frontend/tests/app-shell.spec.ts: brand text exactly nus exchange planner links to /, one header exists on / and /compare, and shell/header DOM identity persists through client navigation. Assert the header contains only the site-name link: no navigation, logo icon, search, subtitle or actions at any viewport. Temporary navigation before US3 must be outside the header.
- [X] T013 [P] [US2] Create frontend/components/layout/AppHeader.tsx with only the site-name link (exact lowercase text nus exchange planner), plus frontend/components/layout/AppShell.tsx with header, a separate temporary navigation slot below it, and page-content slots. Keep document metadata in frontend/app/layout.tsx, no page selection state, and no new main landmark if page children already own main.
- [X] T014 [US2] Create frontend/components/layout/app-shell.module.css for the normalized outer frame (x18/y14, width1745 at viewport1888), header divider y102 and brand anchor x83/y44 using fluid constraints, source colors and .35rem smooth frame radius. Preserve content scroll, dropdown overflow and natural shell growth. Add narrow-screen containment now, without final sidebar styling.
- [X] T015 [US2] Replace the existing shell/header wrapper in frontend/app/layout.tsx with AppShell/AppHeader and place the existing Recommend/Compare links in AppShell’s separate temporary navigation row below the header. The header itself contains only nus exchange planner. Remove only superseded shell/header CSS from frontend/app/globals.css; keep both page bodies and state ownership intact. Do not create a legacy Compare shell.
- [X] T016 [US2] Run frontend/tests/app-shell.spec.ts and inspect both routes at desktop and 390px; record frame/header geometry, one-header semantics and navigation persistence in plan/recommend-sketch/validation-results.md. No forced fixed height or clipping is acceptable.

## Phase 5: US3 — move navigation into the shared left panel

**Single change:** Add the same working left sidebar to all pages.

**Prerequisites:** US2.

**Boundary:** Navigation position, rail/content split and responsive navigation only; no hero, picker or card edits.

**Independent acceptance:** Sidebar is identical across routes, shows the right active link on direct loads/back/forward, and becomes compact navigation below 1024px.

- [X] T017 [P] [US3] Extend frontend/tests/app-shell.spec.ts with exact Recommend/Compare link labels, routes, aria-current, keyboard navigation, direct /compare load, back/forward and persistent shell identity; add a narrow viewport assertion for one visible compact navigation region.
- [X] T018 [P] [US3] Create frontend/components/layout/AppSidebar.tsx as the smallest client boundary needed for pathname-based active state. Use actual links to / and /compare, clean search/opposing-arrow icons, gray-mid inactive and coral active colors, 16px labels and line-height 1.6. Icons are decorative; current path is the single source of active state.
- [X] T019 [US3] Add rail geometry to frontend/components/layout/app-shell.module.css: approximately 284px inner width, divider x303, icon/text anchors x45/x83 and link rows y210/y284 at 1888px. Use a shared content column, natural-height divider and 44px interactive targets. Below 1024px replace the rail with a separate compact navigation row below the site-name-only header consistently on every page; keep reference desktop header height.
- [X] T020 [US3] Integrate AppSidebar into frontend/components/layout/AppShell.tsx and remove the temporary below-header navigation row/links from AppShell and frontend/app/layout.tsx. AppHeader stays site-name-only. Keep exactly one navigation region and one content outlet; preserve Compare content structure and all route queries.
- [X] T021 [US3] Run frontend/tests/app-shell.spec.ts and inspect / and /compare at 1888,1280,768 and390px plus 200% zoom. Record results in plan/recommend-sketch/validation-results.md; verify sidebar/header dimensions match across pages and no duplicate or hidden-focusable navigation remains.

## Phase 6: US4 — replace the Recommend hero only

**Single change:** Show the agreed heading and plane at their existing planned anchors.

**Prerequisites:** US3.

**Boundary:** Recommend hero and its whitespace only; picker and result components retain their current implementation.

**Independent acceptance:** One h1 reads Ready to study abroad?, the plane remains decorative, and no old eyebrow or marketing paragraph remains on Recommend.

- [X] T022 [P] [US4] Add hero assertions in frontend/tests/recommend-hero.spec.ts for exact h1 text, removal of old eyebrow/supporting copy on Recommend only, 40px desktop/32px mobile size and decorative non-focusable plane. Retain a Compare content assertion to catch global selector leakage.
- [X] T023 [P] [US4] Create frontend/components/recommend/RecommendHero.tsx with the exact heading Ready to study abroad? and clean outlined paper plane with coral detail. Add scoped hero rules to frontend/components/recommend/recommend.module.css: heading anchor x417/y193 and plane near x1422/y172 sized 116×115 at 1888px, source weight 500 and line-height 1.2. Use a reserved hero region so smaller theme type does not collapse planned whitespace.
- [X] T024 [US4] Replace only the hero markup in frontend/app/page.tsx with RecommendHero. Keep catalog fetching, effects, picker rendering and results conditions unchanged. Scope desktop and narrow hero layout in frontend/components/recommend/recommend.module.css; preserve one line at the reference width and allow natural wrapping on phones.
- [X] T025 [US4] Run frontend/tests/recommend-hero.spec.ts and inspect desktop/390px placement; record results in plan/recommend-sketch/validation-results.md. Verify smaller NUSMods typography does not lead to enlarging the font to fill the reference box.

## Phase 7: US5 — restyle and position the degree picker

**Single change:** Center the degree field with the exact label and placeholder while preserving its interaction model.

**Prerequisites:** US4.

**Boundary:** Recommend degree field and necessary shared adapter extension only; no card-layout changes or Compare copy changes.

**Independent acceptance:** The field matches 526×60 reference bounds, uses exact wording, and search/select/clear/keyboard/stale-request behavior remains correct.

- [X] T026 [P] [US5] Add picker checks in frontend/tests/recommend-picker.spec.ts for label Degree Programme, placeholder Choose your degree programme, full-list focus, filtering by major/full title, arrows/Home/End/Enter/Escape, no-match and clearing. Check Compare retains Degree programme and Search degree programmes. Include delayed old recommendation response and catalog/error/loading states.
- [X] T027 [P] [US5] Extend frontend/components/DegreeCombobox.tsx with an optional placeholder prop defaulting to Search degree programmes; retain default label Degree programme and shared TypableDropdown semantics. Preserve the model constraint: "Selection uses name; filtering searches both." Do not implement a second picker.
- [X] T028 [US5] Create frontend/components/recommend/RecommendDegreeField.tsx as a presentation wrapper passing Degree Programme and Choose your degree programme. In frontend/components/recommend/recommend.module.css position the label near x990/y370 and field atx726/y405, width 526 height 60 at 1888px; use white surface, 16px type, source border/focus and .25rem radius. Use fluid width and visible listbox overflow on narrow screens.
- [X] T029 [US5] Integrate RecommendDegreeField in frontend/app/page.tsx without moving catalog/selection/results state into the wrapper. Preserve "Untouched idle with no degree → hero and picker only, no cards." and "Degree change → cancel obsolete request and clear old cards immediately." Update only Recommend accessible-label lookups in frontend/tests/flows.spec.ts, retaining Compare lookups.
- [X] T030 [US5] Run frontend/tests/recommend-picker.spec.ts plus relevant keyboard/error cases in frontend/tests/flows.spec.ts; record results in plan/recommend-sketch/validation-results.md. Check dropdown overlays later content, focus remains visible, clearing removes results and no fixture cards appear on first load.

## Phase 8: US6 — build and integrate one reusable university card

**Single change:** Replace card internals with the reusable themed card while keeping the current collection placement.

**Prerequisites:** US5.

**Boundary:** Card content, individual variants and action only. Tier dimensions may change; do not introduce final row grouping until US7.

**Independent acceptance:** Each tier has correct names, labels, source type, safe action markup, real counts and complete long text; navigation opens the correct pair.

- [ ] T031 [P] [US6] Create frontend/tests/recommend-card.spec.ts with API-driven assertions for title/country/rank, NUS-primary and Partner University Modules secondary, absence of a visible mapping-row metric, exact View Mappings --> anchor and encoded href. Cover 0/1 counts, long names, all three variants, one focus stop for the action and no button inside a link.
- [ ] T032 [P] [US6] Create frontend/components/recommend/UniversityCard.tsx accepting Recommendation, degree, 1-based rank and featured/secondary/compact tier; compose existing Card and Badge primitives. Preserve "Keep the exact plural labels even when the count is 1 to meet the copy contract." and "mapping_count is retained but not displayed on Recommend." Render API counts without recomputation; use one styled anchor with encoded degree/university parameters.
- [ ] T033 [US6] Add card variant rules to frontend/components/recommend/recommend.module.css: reference footprints 634×270,505×214,355×151 as constrained widths/minimum heights, .35rem radius, white surface/gray border, source title sizes 32/24/20 and primary metrics 24/20/16, partner 14, badge 12, action 14. Keep rank/name/count insets and lower-right footer; allow long text to grow without overlap. At390px use title 24, metric 20 and supporting/badge/action 14 with 44px hit targets.
- [ ] T034 [US6] Replace inline card markup in frontend/components/UniversityCards.tsx with UniversityCard, preserving input order and temporary collection layout. Apply "Index 0 is featured; indices 1–2 secondary; subsequent indices compact." Remove nested Button/Link and conflicting text-6xl. Update card text/count selectors in frontend/tests/flows.spec.ts without changing API expectations or suppressing old-layout failures scheduled for US7.
- [ ] T035 [US6] Add an isolated visual component harness at frontend/tests/fixtures/UniversityCardPreview.tsx for the repeated-copy fixture from frontend/tests/fixtures/recommendations.ts. Render it only through a test-only build/server entry configured in frontend/tests/fixtures/preview-server.mjs and, if necessary, frontend/package.json; do not add a public Next route or production display override. Reuse the real card component; explicit rank 1 is passed only by the harness. Confirm its action is intercepted within the harness rather than navigating to a fake live pair.
- [ ] T036 [US6] Run frontend/tests/recommend-card.spec.ts and live Recommend-to-Compare count checks from frontend/tests/flows.spec.ts; record results in plan/recommend-sketch/validation-results.md. Verify Toronto AI 6 NUS/9 partner/9 Compare rows and Western Australia Business Analytics 19 partner/22 Compare rows. Record any inherited fixture/data failures separately; never alter production data to satisfy expectations.

## Phase 9: US7 — arrange recommendation cards into the final rows

**Single change:** Apply the planned 1–2–3 layout to the reusable cards without changing their internal content.

**Prerequisites:** US6.

**Boundary:** Collection grouping, placement and responsive layout only; no copy, theme or fetching changes.

**Independent acceptance:** Six-card desktop fixture matches reference anchors; every real item remains ordered and visible; partial rows and mobile widths have no phantom cards or overflow.

- [ ] T037 [P] [US7] Create frontend/tests/recommend-visual.spec.ts with six-card fixture geometry expectations at 1888×1337: one 634px featured card centered near x678/y512, two 505px cards near x440/x1010 y839, three 355px cards near x391/x835/x1244 y1095; allow the documented 8px tolerance on approximate anchors. Assert theme styles separately and do not pixel-compare against the sketch PNG.
- [ ] T038 [P] [US7] Refactor frontend/components/UniversityCards.tsx into explicit featured, secondary and compact row groups (first item, next two, remaining chunks of three). Preserve "The collection preserves incoming order. No university is hidden to fit a row." Use stable real identities, no filler cards and no re-sorting or slicing away later rows.
- [ ] T039 [US7] Implement collection geometry in frontend/components/recommend/recommend.module.css: centered narrow featured card, independent row widths/insets and 45–60px row gaps. At≥1440px retain 1/2/3; at 1024–1439px retain featured then pairs; below 1024px stack in order. Use constrained grid/flex containers, not absolute positioning or CSS transforms. Empty/partial rows must consume only actual content.
- [ ] T040 [US7] Extend frontend/tests/fixtures/UniversityCardPreview.tsx to render all six reference-copy cards using the same collection layout styling, and connect its capture to frontend/tests/recommend-visual.spec.ts. Keep repeated labels/#1 confined to this harness; also capture production UI with six unique API fixture universities to verify real ordinal ranks and keys.
- [ ] T041 [US7] Update obsolete half/third width assertions in frontend/tests/flows.spec.ts to current responsive layout rules and add 0/1/2/5/6/7-result, long-title, narrow-width and 200% zoom checks in frontend/tests/recommend-visual.spec.ts. Keep rank/data/deep-link assertions; verify empty initial state, rapid changes and all later compact rows remain visible.
- [ ] T042 [US7] Run frontend/tests/recommend-visual.spec.ts and frontend/tests/flows.spec.ts; capture 1888,1440,1280,768 and390px in the same OS/browser. Review new themed screenshots before accepting baselines; record geometry, hierarchy, footer clearance and source-token results in plan/recommend-sketch/validation-results.md. Preserve the theme/font difference from the original sketch.

## Phase 10: Final verification — accept the composed result

**Single change:** Verify the completed increments together and document evidence.

**Prerequisites:** US1–US7.

**Boundary:** Validation and documentation only; no new feature or catch-all redesign. Route defects back to their owning phase and rerun affected checks.

**Independent acceptance:** All introduced checks pass, inherited issues are identified explicitly, and both routes meet the documented feature contract.

- [ ] T043 Run npm run lint, npm run typecheck, npm run build and npm run test:e2e from frontend/ using frontend/package.json; record exact commands, results and any remaining failures in plan/recommend-sketch/validation-results.md. Reuse frontend/playwright.config.ts server orchestration and avoid duplicate servers on 18765/18766.
- [ ] T044 Execute the complete plan/recommend-sketch/quickstart.md scenarios and record evidence in plan/recommend-sketch/validation-results.md: shared shell/direct loads/back-forward, exact copy, live counts, stale responses, responsive geometry, source theme, accessibility and warmed render time. Confirm test preview entry and mock data are absent from production routes/bundle entry points.
- [ ] T045 Update completion checkboxes in plan/recommend-sketch/tasks.md only after each owning phase passes; append a concise final scope and screenshot/evidence index to plan/recommend-sketch/validation-results.md. Keep plan/recommend-sketch/plan.md and quickstart.md aligned with any justified implementation path adjustments; leave unimplemented work unchecked.

## Dependencies and delivery order

```text
Phase 1 baseline → Phase 2 fixtures
  → US1 theme → US2 frame/header → US3 sidebar
  → US4 hero → US5 degree picker → US6 card → US7 collection
  → Final integrated verification
```

This sequence intentionally differs from the earlier plan's illustrative build order: the user's task request prioritizes one isolated change at a time. It is the authoritative execution order; design outcomes remain unchanged. Component code may be reusable before assembly, but each phase integrates its own change into a working app. There is no later "wire everything up" phase.

- UI contract maps to US2–US7; theme contract maps to US1 and the variants in US2–US7.
- Degree/Catalog and fetch state are preserved in US5; Recommendation view props/counts/deep links in US6; order/tier assignment in US6–US7; route state in US3.
- Compare receives the shared theme and shell in US1–US3. Its content layout and behavior are regression-checked, not redesigned.
- Do not use the absent sixth live university as a reason to omit the three-card fixture row; use test data.

## Safe parallel opportunities

The default delivery path is sequential phases. Within each story, the following pairs can be authored independently after the phase prerequisites pass; execute their checks after implementation is integrated:

- US1: T007 + T008 — acceptance checks and initial implementation touch different files. All subsequent tasks in this phase are sequential; CSS/adapter/page integrations are not parallel edits.
- US2: T012 + T013 — acceptance checks and initial implementation touch different files. All subsequent tasks in this phase are sequential; CSS/adapter/page integrations are not parallel edits.
- US3: T017 + T018 — acceptance checks and initial implementation touch different files. All subsequent tasks in this phase are sequential; CSS/adapter/page integrations are not parallel edits.
- US4: T022 + T023 — acceptance checks and initial implementation touch different files. All subsequent tasks in this phase are sequential; CSS/adapter/page integrations are not parallel edits.
- US5: T026 + T027 — acceptance checks and initial implementation touch different files. All subsequent tasks in this phase are sequential; CSS/adapter/page integrations are not parallel edits.
- US6: T031 + T032 — acceptance checks and initial implementation touch different files. All subsequent tasks in this phase are sequential; CSS/adapter/page integrations are not parallel edits.
- US7: T037 + T038 — acceptance checks and initial implementation touch different files. All subsequent tasks in this phase are sequential; CSS/adapter/page integrations are not parallel edits.

The isolated fixture harness is a validation detail, not an application feature. Prefer a lightweight test-only renderer using existing tooling; if a new test runner dependency would be necessary, document that tradeoff before changing the package manifest, and preserve the no-production-preview boundary.

## Implementation strategy and MVP

Smallest useful increment: phases 1–3 (baseline, fixture foundation, US1 theme). This delivers the NUSMods presentation without layout changes. The minimum coherent shared-shell milestone adds US2–US3 (through phase 5). Neither milestone completes the requested redesign: US4–US7 and final verification remain required.

After each phase: review only its intended change, run its focused checks and typecheck, document results, then proceed. Maintain old behavior between phases. Existing stale tests must be attributed to the baseline or the phase that owns their replacement; do not disable them or describe the whole suite as passing until final validation actually passes.

## Task counts and format audit

Total: **45 tasks** across **10 phases**.

| Phase | Story | Tasks |
| --- | --- | --- |
| 1 | Setup — establish the working baseline | 3 |
| 2 | Foundation — deterministic validation data | 3 |
| 3 | US1 | 5 |
| 4 | US2 | 5 |
| 5 | US3 | 5 |
| 6 | US4 | 4 |
| 7 | US5 | 5 |
| 8 | US6 | 6 |
| 9 | US7 | 6 |
| 10 | Final verification — accept the composed result | 3 |

All tasks use an unchecked checkbox, unique sequential T ID, a story label only for user-story phases, and explicit repository-relative file paths. [P] appears only on independently editable task pairs. No tasks have been executed by generating this document.
