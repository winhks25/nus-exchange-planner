# Validation results

Feature: Recommend layout with NUSMods theme and shared application shell.
Started: 2026-10-21.

## Phase 1 — Setup baseline

### T001 — Constraints and source references

Workflow note: this checkout has no `.specify/` directory. The requested
`check_prerequisites.py` / `setup_tasks.py` JSON contract is unavailable, so the
existing feature directory `plan/recommend-sketch/` is authoritative. There is no
constitution and no extension hook registry to execute.

Read:

- `frontend/AGENTS.md`: this Next.js version may differ from prior knowledge; read the
  locally installed guides before writing application code.
- `frontend/node_modules/next/dist/docs/01-app/01-getting-started/03-layouts-and-pages.md`:
  the root layout is required, must render `html`/`body`, wraps route children, and
  layouts persist across navigation. Client pages render inside it.
- `frontend/node_modules/next/dist/docs/01-app/01-getting-started/05-server-and-client-components.md`:
  layouts/pages are Server Components by default; `"use client"` is required only for
  state, effects, event handlers or browser APIs. The client boundary should stay as
  small as possible (`AppSidebar` only, in a later phase).
- All artifacts in `plan/recommend-sketch/` (`spec.md`, `plan.md`, `research.md`,
  `data-model.md`, `contracts/recommend-ui.md`, `contracts/nusmods-theme.md`,
  `quickstart.md`, `tasks.md`) and the reference image
  `reference/recommend-home.png` (2202 x 1560 source; normalized 1888 x 1337 frame).

Applicable constraints recorded for implementation:

- Preserve the current Next.js 16 App Router / React 19 / TypeScript, Tailwind v4 and
  Base UI stack, plus Read-only FastAPI API. No backend, dependency upgrade, Bootstrap
  import, font download or production demo data.
- Preserve the user's uncommitted edits in `frontend/app/globals.css`,
  `frontend/app/page.tsx`, `frontend/components/UniversityCards.tsx` and the new
  `frontend/components/ui/badge.tsx`.
- Latest user constraints override sketch styling: keep screenshot layout and exact
  wording, use real API values, and apply the pinned NUSMods light theme.
- One shared shell: root layout owns exactly one AppShell/AppHeader; header contains
  only the lowercase `nus exchange planner` link; navigation is a sibling region.
- Static copy contract: `Recommend`, `Compare`, `Ready to study abroad?`,
  `Degree Programme`, `Choose your degree programme`, `NUS Modules`,
  `Partner University Modules`, `View Mappings -->` (ASCII arrow).
- Theme tokens: white `#ffffff`, body text `#69707a`, emphasis `#222324`, secondary nav
  `#848490`, placeholder `#aeb1b5`, border `#d3d6db`, subtle surface `#f3f5f8`,
  primary `#ff5138`, error `#b71c1c`; system font stack; 16px root; 400/500/700
  weights; body line-height 1.5, heading 1.2; `.25rem` control radius, `.35rem` card
  radius.
- Reference geometry: outer frame x18/y14 width1745 at 1888px, header divider y102,
  brand x83/y44, sidebar divider x303, hero anchor x417/y193, plane x1422/y172,
  picker 526x60 at x726/y405, featured card 634x270 at x678/y512, secondary cards
  505x214 at x440/x1010 y839, compact cards ~355x151 at x391/x835/x1244 y1095.
- Visual validation compares layout geometry only against the sketch PNG, never
  whole-image pixels, and uses the themed screenshot as the appearance baseline.

Pinned NUSMods source commit: `f487593c16f580cc6ea5fa6cff9bdc934de7c064`
(default light application theme; inherited Bootstrap 4.6.2 system font stack and
scale). Source links and token provenance are in
`contracts/nusmods-theme.md`.

Environment for the baseline:

| Item | Value |
| --- | --- |
| OS | macOS 26.5.1 (25F80) |
| Node | v22.23.3 |
| npm | 10.9.9 |
| Playwright | 1.56.1 (Desktop Chrome device profile) |
| Browser | Chromium bundled with Playwright 1.56.1 |
| Reference capture size | 1888 x 1337, deviceScaleFactor 1 |

### T002 — Working baseline and pre-change captures

`git status --short` at baseline (preserved, not reset):

- Modified: `frontend/app/globals.css`, `frontend/app/page.tsx`,
  `frontend/components/UniversityCards.tsx`.
- Untracked: `frontend/components/ui/badge.tsx`, `plan/recommend-sketch/`.
- Deleted by the feature setup: the old `plan/*.md` files that were superseded by
  `plan/recommend-sketch/`; no restoration attempted.

Inspected diff summary (baseline state, kept as-is):

- `globals.css`: cards were already moved from `.card` grid markup to
  `.university-card` + Base UI primitives; new/modified selectors include
  `.university-card`, `.university-card-header`, `.university-card-heading`,
  `.university-card-title`, `.country-badge`, `.university-card-content`,
  `.module-count`, `.nus-module-count`, `.partner-module-count`,
  `.university-card-footer`; old `.card-count` / `.card-secondary-counts` rules were
  removed.
- `page.tsx`: only the eyebrow copy changed to `NUS Exchange Planner`.
- `UniversityCards.tsx`: now composes `Card`/`CardHeader`/`CardTitle`/`CardContent`/
  `CardFooter` and `Badge`; uses `View Mappings →` (Unicode) and nests a `Button`
  inside a `Link`; keeps `text-6xl` and the legacy `top-card`/`half-card`/`third-card`
  classes. These are known issues owned by US6/US7, not Phase 1 changes.
- `ui/badge.tsx`: new shadcn/Base UI badge primitive with cva variants (untracked).

Pre-change screenshots captured through the existing `frontend/playwright.config.ts`
server orchestration at 1888 x 1337, deviceScaleFactor 1 (temporary throwaway spec,
removed after capture):

- `reference/baseline/recommend-idle.png` — `/` before any interaction.
- `reference/baseline/recommend-results.png` — `/` with Computer Science results.
- `reference/baseline/compare-loaded.png` — `/compare` with Computer Science and
  University of Toronto, 6 mapping rows.

These are historical baseline evidence only; the sketch PNG remains the geometry
reference and the new themed screenshots will become the appearance baseline.

### T003 — Baseline automated checks

Commands run from `frontend/` with the working tree unchanged:

| Command | Result |
| --- | --- |
| `npm run lint` | PASS (exit 0, no output) |
| `npm run typecheck` | PASS (exit 0, no output) |
| `npm run test:e2e` | FAIL — 4 failed, 5 passed (40.7s) |

E2E failures and attribution:

1. `flows.spec.ts:3` Recommend keyboard search, ranking, zero card, and Compare deep
   link — fails at `expect(cards.first().locator(".card-count")).toHaveText("6mappable
   partner modules")`; the selector no longer exists after the baseline card markup
   change.
2. `flows.spec.ts:35` Artificial Intelligence counts reconcile from Recommend to
   Compare — same missing `.card-count` selector.
3. `flows.spec.ts:66` Recommend ranks by NUS modules and sizes cards by rank — same
   missing `.card-count` selector before reaching its width assertions. This test also
   still encodes stale old-layout expectations: secondary/featured width ratio
   0.45–0.51, compact/featured 0.29–0.35, a full-width featured card, and equal
   secondary row `y`. These belong to US7's replacement work.
4. `flows.spec.ts:142` keyboard boundaries, Escape, and zero-count navigation — same
   missing `.card-count` selector.

Additional stale selectors identified in `flows.spec.ts` (not yet changed):

- `.card-count` (all remaining assertions expecting `"<n>mappable partner modules"`).
- `.card-secondary-counts` (expecting `distinct NUS modules` and `mappings`).
- Old label lookups `Degree programme` / placeholder `Search degree programmes` that
  US5 will update for Recommend only while retaining Compare lookups.
- Old card text `View Mappings →` passed as a regex, which will still match the
  contracted `View Mappings -->` action text.

Passed baseline scenarios: clearing/invalid link/zero match; no-match and catalog
error; delayed old Compare response; warmed Recommend render (`WARM_RENDER_MS=25.7`);
Compare missing partner units. No data assertions were weakened; the failures are
kept as accurate baseline evidence and are owned by later phases.

## Phase 2 — Foundation: deterministic validation data

### T004 — Fixture data

Created `frontend/tests/fixtures/recommendations.ts`:

- `apiRecommendations`: eight unique synthetic universities with fields exactly
  matching `Recommendation` in `frontend/lib/types.ts`; includes a zero-count
  university and varied NUS/partner/mapping counts.
- `recommendationResultVariants`: `zero`, `one`, `two`, `five`, `six`, `seven`
  result arrays built from the same unique universities.
- `longNameRecommendations`: long university and long country names for wrapping
  checks.
- `fixtureCatalog` / `catalogWith` / `recommendationsFor`: typed catalog and
  recommendations response builders.
- `visualRecommendations`: the separate exact-copy visual fixture with six unique
  internal `id` values, repeated `University Name` / `Country`, NUS 10, partner 12,
  and `VISUAL_DISPLAY_RANK = 1` for the isolated harness. It is deliberately not
  part of any API response.

No fixture is wired into production code or read by `frontend/app/page.tsx`.

### T005 — Interception helpers

Created `frontend/tests/helpers/recommendation-fixtures.ts`:

- `mockCatalog` intercepts `**/api/v1/catalog` with a typed `Catalog`.
- `mockRecommendations` intercepts `**/api/v1/recommendations?**` with a typed
  `Recommendations` response.
- `installRecommendationFixtures` installs both mocks and returns the fixtures used.
- `selectDegree` focuses the shared picker, filters by the degree name, presses
  Enter, and awaits the expected article count. For a zero-result variant it waits
  for the loading status to clear and for the (empty, zero-height) results region to
  be attached.
- `openRecommendWithFixtures` combines installation, navigation and selection.

Verification: a temporary four-test smoke spec exercised the six-result, zero-result,
long-name/country and full API fixture paths through the real page; all four passed
(13.1s). The temporary spec was then removed, and only the two fixture/helper modules
remain. `flows.spec.ts` real-API scenarios were not modified.

### T006 — Fixture documentation and capture settings

Updated `plan/recommend-sketch/quickstart.md` with a "Fixture data and capture
settings" section covering fixture ownership, API mocks versus the isolated visual
harness, helper usage, and the fixed capture environment: macOS 26.5.1, Playwright
1.56.1 bundled Chromium (Desktop Chrome profile), viewport 1888 x 1337,
deviceScaleFactor 1. It restates that the old PNG is a geometry reference, not a
themed whole-image baseline, and that the test preview must stay out of production
routes and bundle entry points.

### Phase 2 checks

| Command | Result |
| --- | --- |
| `npm run lint` | PASS (exit 0) |
| `npm run typecheck` | PASS (exit 0) |

No product route, production fixture switch or UI change was made in this phase.

## Phase 3 — US1: NUSMods theme only

### T007 — Theme acceptance checks

Created `frontend/tests/theme.spec.ts` with four computed-style scenarios:

- Body declares the exact source stack in `--font-system`; Chromium normalizes
  `BlinkMacSystemFont` to `"system-ui"` in `getComputedStyle`, so the test asserts the
  declared custom property exactly and the computed value in its browser-normalized
  equivalent. Base is 16px/24px (1.5), body text `#69707a`, background white.
- Existing chrome: h1 40px/500/1.2, brand 20px/700, nav 16px/400 `#848490`, header
  bottom border 1px `#d3d6db`, nav hover coral. The test asserts the current header,
  Recommend/Compare links, hero and picker still exist and no results render before a
  selection; it does not encode the future sidebar or grid.
- Cards (six-result fixture): white surface, 1px `#d3d6db` border, `.35rem` radius,
  no ring/shadow; titles 32/24/20px at weight 500; NUS metrics 24/20/16px at weight
  500; partner text 14px/400 gray; badge 12px/400; action 14px/400 coral outlined.
- Picker/dropdown: 16px white field, 1px border, `.25rem` radius, `#aeb1b5`
  placeholder, coral focus border and `.2rem` 25%-alpha ring, dropdown 1px border,
  `.25rem` radius, `0 2px 6px rgba(0,0,0,.25)` shadow and `#f3f5f8` option hover.
- Compare (mocked catalog/mappings): existing Degree programme and Partner university
  controls, three-count summary and mapping row remain; the row uses the same white
  surface, 1px border, `.35rem` radius and gray text roles.

### T008/T009 — Semantic tokens and source type roles

`frontend/app/globals.css` now maps the pinned source values:

- White `#ffffff`; body `#69707a`; emphasis `#222324`; navigation `#848490`;
  placeholder `#aeb1b5`; border `#d3d6db`; subtle surface `#f3f5f8`; primary
  `#ff5138`; error `#b71c1c`.
- Exact Bootstrap 4.6.2 system font stack, 16px root, 400/500/700 weights, body
  line-height 1.5 and headings 1.2.
- `.25rem` control radius and `.35rem` card/frame radius via `--radius-sm/md/lg/xl`;
  no Bootstrap import, webfont download or new dependency.

Role mapping applied to the existing selectors: brand 20/700; nav 16/400; hero 40/500
(32px below 650px); picker label and field 16; card titles 32/24/20 and NUS metrics
24/20/16 at weight 500; partner 14; badge 12; action 14. The previous
number-only `2rem`/`1.35rem` strong overrides were removed so each value and its label
share the role size. Natural reflow only: at 1888px the hero fell from the old
`3.7rem` clamp maximum to the source 40px, and card text occupies less height because
the source scale is smaller; card boxes, grid tracks, gaps, margins and padding were
kept.

### T010 — Interaction states

- Field focus uses border `#ff5138` and `0 0 0 .2rem rgba(255,81,56,.25)`; hover uses
  the placeholder gray; placeholders are `#aeb1b5`.
- Dropdown uses the source 1px border, `.25rem` radius, `0 2px 6px rgba(0,0,0,.25)`
  shadow and `#f3f5f8` hover/active options.
- Nav hover and link/action text use coral; the card action remains bottom-right as an
  outlined coral anchor. Its existing nested Button markup is only neutralized
  visually here; removing the nested control is US6 scope.
- `frontend/components/ui/input.tsx`, `button.tsx` and `badge.tsx` were aligned to
  the same tokens (control radius, `.2rem`/25% ring, placeholder token, 12px/400
  badge) only where their utility classes override global element styles.

### T011 — Theme-only validation

| Command | Result |
| --- | --- |
| `npx playwright test tests/theme.spec.ts` | PASS — 4/4 (12.3s, 1 worker) |
| `npx playwright test tests/flows.spec.ts` | 5 passed, 4 failed — the same four baseline failures caused only by removed `.card-count`/`.card-secondary-counts` selectors; no new failure |
| `npm run lint` | PASS (exit 0) |
| `npm run typecheck` | PASS (exit 0) |

The four flow failures are exactly the baseline items owned by US6/US7:
`flows.spec.ts:3`, `:35`, `:66` and `:142` still look for the removed `.card-count`
before reaching their old layout assertions. The previously passing Compare, no-match,
error, stale-response, warmed-render (`WARM_RENDER_MS=23.9`) and blank-units scenarios
still pass.

Theme-only captures, same fixed macOS 26.5.1 / Playwright 1.56.1 Chromium /
deviceScaleFactor 1 environment:

| Capture | Size |
| --- | --- |
| `reference/theme/recommend-idle-1888.png` | 1888 x 1337 |
| `reference/theme/recommend-results-1888.png` | 1888 x 1337 |
| `reference/theme/compare-loaded-1888.png` | 1888 x 1337 |
| `reference/theme/recommend-results-390.png` | 390 x 1986 |
| `reference/theme/compare-loaded-390.png` | 390 x 1667 |

Layout review against the previous declarations found no changed layout rules:
`.shell` max-width/margin/padding, header flex/padding, `.hero` padding, the `.cards`
six-column grid/gap/margin, tier `grid-column` spans and paddings, card content inset,
`.selectors` grid/gap, and `.mapping-row` grid/gap/padding are unchanged. Only theme
colors, borders, radii and the requested type sizes changed, so no new controls or
route content were introduced. The Compare page retained its wording, control labels,
summary and row order.

## Phase 3 follow-up — dark background (2026-10-21)

The user's follow-up screenshot supersedes the earlier light palette. Its most
common pixel is #222324, now used for body, cards and controls; #292929 is the
secondary surface. Text and borders were adapted for readability, with coral
accents, typography and layout retained. The theme contract records this override
for subsequent phases. Earlier theme captures above show the superseded palette.

Validation: `npx playwright test tests/theme.spec.ts` from frontend passed 4/4
(12.9s), covering body/chrome, cards, picker interaction styles and Compare.
`git diff --check` passed. The first test attempt could not access the sandboxed
uv cache; the rerun with local-server/cache permissions passed.

## Phase 4 — US2: shared frame and header

### T012 — Shell acceptance checks

Created `frontend/tests/app-shell.spec.ts` with six scenarios:

- Header content on direct loads of `/` and `/compare`: exactly one `<header>`
  with exactly one link whose text is exactly `nus exchange planner` (lowercase)
  and href `/`; no nav, svg, img, input, button, textarea, p, h1, ul or li inside.
- Reference geometry at 1888x1337: the header's parent (frame) starts at x18/y14
  with width 1745 (+/-8 normalized px); the header border bottom sits at y102 with
  88px height; the brand anchor sits at x83/y44.
- Compare keeps the same frame geometry and header content.
- Narrow containment at 390px: no horizontal page overflow, frame margins reduce
  to 12px, the brand and temp navigation remain visible, and the header stays
  free of navigation.
- Shell persistence: after waiting for hydration (picker visible), a
  `dataset.shellProbe` marker is set on the header node; clicking Compare performs
  client navigation (`performance.getEntriesByType("navigation")` stays 1), the
  same header node retains the marker on `/compare`, its bounding box width and
  height are unchanged, and `header nav` does not exist.

### T013/T014 — Shell components and frame CSS

- `frontend/components/layout/AppHeader.tsx`: stateless server component holding
  only the lowercase `nus exchange planner` Link to `/`.
- `frontend/components/layout/AppShell.tsx`: frame wrapper with header, an
  optional temporary navigation slot (`<nav aria-label="Primary">`) below the
  header, and a page-content slot. No page selection state; no new main landmark
  (pages own `<main>`). Document metadata stays in `frontend/app/layout.tsx`.
- `frontend/components/layout/app-shell.module.css`: frame `max-width 1745px`
  with margins 14/18/53/18 (right gap retains the reference outer margin instead
  of centering), 1px border and `.35rem` radius on source colors; header 88px
  tall with 65px left padding and bottom divider at y102; brand 20px/700 links;
  temporary nav row with the old header-nav link styles (16px/400 gray, coral
  hover); content keeps the old `.shell` content inset (max-width 1100, padding
  0 24px 60px) so both page bodies are unaffected; below 800px the frame margins
  and content padding are reduced before the US3 sidebar work. No overflow or
  fixed heights on content, so scroll, dropdown stacking and shell growth are
  preserved.

### T015 — Root layout integration

- `frontend/app/layout.tsx` now renders `<AppShell>` with the Recommend/Compare
  links passed as the temporary navigation slot; the header markup and
  `.shell`/`header`/`.brand` CSS were removed from `frontend/app/globals.css`
  (including the 650px header media rule), and none of the page-body styles or
  state ownership changed. No legacy Compare shell was created.
- `frontend/tests/theme.spec.ts` had its single stale locator updated:
  `.brand` (global class, now a hashed CSS-module class) became
  `page.locator("header").getByRole("link")`. All other theme assertions are
  unchanged and still pass.

### T016 — Shell validation

| Command (from `frontend/`) | Result |
| --- | --- |
| `npx playwright test tests/app-shell.spec.ts` | PASS — 6/6 (12.6s, 1 worker) |
| `npx playwright test tests/theme.spec.ts` | PASS — 4/4 (13.2s), no theme regression |
| `npx playwright test tests/flows.spec.ts` | 5 passed, 4 failed — exactly the four baseline `.card-count` failures owned by US6/US7; no new failure |
| `npm run lint` | PASS (exit 0) |
| `npm run typecheck` | PASS (exit 0) |

One-header semantics: direct loads and client navigation each show exactly one
`<header>` whose DOM node persists through the Recommend → Compare route change
(marker probe retained; navigation-entry count stays at 1, confirming client-side
navigation), and the header bounding box is identical across routes.

Shell-only captures (same fixed macOS 26.5.1 / Playwright 1.56.1 Chromium /
deviceScaleFactor 1 environment):

| Capture | Size |
| --- | --- |
| `reference/shell/recommend-1888.png` | 1888 x 1337 |
| `reference/shell/compare-1888.png` | 1888 x 1337 |
| `reference/shell/recommend-390.png` | 390 x 2007 (full page) |
| `reference/shell/compare-390.png` | 390 x 1737 (full page) |

Reviewed captures confirm: charcoal rounded frame starting x18/y14 with the
reference 125px right gap at 1888; brand-only header with full-width divider at
y102; the temporary Recommend/Compare row below the header on desktop and at
390px; recommendations/pickers/mapping rows render unchanged inside the retained
1100px content column; the frame grows with short content and no fixed height or
clipping occurs. The dev-tools badge visible in captures is a Next.js dev-only
overlay, not application UI.

## Post-phase 4 repair — isolate browser-test build output (2026-10-21)

The local app displayed “The mapping service is unavailable” even though
`http://localhost:8001/api/v1/catalog` returned 200 with six degrees and five
universities. The JavaScript served on port 3000 contained the test API origin
`http://127.0.0.1:18765`. Playwright used separate ports but shared `.next/`
with the regular development server, allowing its compiled bundles to overwrite
the live app's output. Once its temporary API stopped, catalog loading failed.

Added `frontend/next.config.ts` to select `.next-e2e/` when the Playwright
frontend sets `PLAYWRIGHT_TEST=1`. Normal development retains `.next/`.
Git and ESLint ignore test build output; TypeScript includes the generated test
route types. No product UI or later feature phase was implemented by this repair.

Validation:

- The normal dev server recompiled with `http://localhost:8001` after loading
  the new config, and stayed running throughout browser tests.
- `npm run test:e2e --prefix frontend -- tests/app-shell.spec.ts`: 6 passed.
- After the test servers stopped, a Chromium smoke check against the actual
  app on port 3000 confirmed catalog HTTP 200 from port 8001, Artificial
  Intelligence selection producing five university cards, and navigation to
  Compare producing nine mapping rows with no error alert.
- `npm run lint --prefix frontend`, `npm run typecheck --prefix frontend`, and
  `git diff --check`: passed. The inherited card-selector failures documented
  above are outside this repair; the full flow suite was not rerun.

## Phase 5 — US3: shared left navigation

### T017 — Sidebar acceptance checks

Extended `frontend/tests/app-shell.spec.ts` from six to thirteen scenarios:

- Shared navigation: direct loads of `/` and `/compare` show exactly one nav
  region whose only links are `Recommend` → `/` and `Compare` → `/compare`;
  only the link matching the current route carries `aria-current="page"`.
- Keyboard: tab order after the header brand reaches Recommend then Compare;
  Enter on the focused Compare link performs a client navigation and moves
  `aria-current` without a second navigation entry.
- Back/forward: breadcrumb `/compare → / → /compare → /` keeps one nav node
  (`dataset.shellProbe` retained), and `aria-current` always reflects the
  current path after `goBack`/`goForward`.
- Narrow viewport (390px): exactly one visible compact navigation region sits
  below the site-name-only header with both links and exact hrefs.
- Reference sidebar geometry at 1888x1337: the rail box starts at x18 and its
  divider edge lands at x303 (+/-8); link rows start at y210 and y284; icons
  align at x45 and label text at x83 for both rows; the Compare rail keeps the
  same x/width/y as the Recommend rail.

One early failure was a test bug (active-route branch derived the path from the
label instead of the item href) and was fixed before recording.

### T018/T019/T020 — Sidebar component, rail CSS and integration

- `frontend/components/layout/AppSidebar.tsx`: smallest required client
  boundary (`"use client"` + `usePathname`, confirmed against the installed
  Next.js docs). Real `Link`s to `/` and `/compare`; `aria-current="page"` when
  `pathname === href` (single source, no duplicated selection state). Clean
  24px decorative line SVGs (search for Recommend, opposing arrows for Compare)
  are `aria-hidden` and `pointer-events: none`, so the label span is the
  accessible name. Indirect hover and active colors use `--muted-foreground`
  and `--primary`; labels are 1rem/400 with line-height 1.6.
- `frontend/components/layout/app-shell.module.css`: `.body` grid adds the
  rail — 284px inner column plus 1px divider (285px border-box), first link row
  y210 via 108px top padding under the y102 header divider, 44px interactive
  rows with 30px gaps, icon x45/text x83 via 27px padding + 24px icon + 14px
  gap. The divider stretches with content (natural height). Below 1023px the
  same nav reflows into a compact row under the header (single-column grid,
  horizontal links, bottom divider, 14px/24px padding).
- `frontend/components/layout/AppShell.tsx` now renders `AppSidebar` inside a
  `.body` grid next to the single `.content` outlet; the temporary
  below-header navigation prop was removed from `AppShell`, and
  `frontend/app/layout.tsx` lost its Recommend/Compare `Link` imports/JSX.
  `AppHeader` remains site-name-only; there is exactly one nav region and one
  content outlet on every route; Compare content structure and all route
  queries are untouched.

### Accent-token reconciliation (user style override, not US3)

Re-running `tests/theme.spec.ts` after the phase surfaced 3/4 failures that
also reproduce at the pre-phase commit `60b032f` ("update cyan accents and
rounded header"): the tracked assertions expected coral `rgb(255, 81, 56)`
while the committed `--primary` is cyan `#00c5ff` (brand now uses the accent).
The committed focus rule `box-shadow: 0 0 0 .2rem --ring` was also invalid CSS,
so the focus ring had silently disappeared. As the latest user styling wins:
`tests/theme.spec.ts` now asserts the committed cyan accent and ring
(`#00c5ff` / `#00f9ff`), with `CORAL` renamed to `ACCENT`, and
`frontend/app/globals.css` uses `var(--ring)` in the focus rule. Theme spec
after repair: 4/4 passed (11.6s). US3's sidebar styling itself tracks tokens,
so it follows whichever accent the user pins next.

### T021 — Shell/sidebar validation

| Command (from `frontend/`) | Result |
| --- | --- |
| `npm run test:e2e -- tests/app-shell.spec.ts` | PASS — 13/13 (21.3s, 1 worker) |
| `npm run test:e2e -- tests/theme.spec.ts` | PASS — 4/4 (11.6s) |
| `npm run test:e2e -- tests/flows.spec.ts` | 5 passed, 4 failed — the same four stale `.card-count`/`.card-secondary-counts` card-selector files owned by US6/US7; no new failure |
| `npm run typecheck` (tsc) | PASS (exit 0) |
| `npx eslint` (layout components, layout.tsx, theme/app-shell specs) | PASS |

Measured layout facts (fixed macOS 26.5.1 / Playwright 1.56.1 bundled Chromium,
deviceScaleFactor 1; 200% zoom emulated as 944 CSS px at dpr 2):

| Viewport | Header | Nav rail/row | Nav rows | Overflow | Nav regions |
| --- | --- | --- | --- | --- | --- |
| 1888 `/` and `/compare` | x18 y14, 1745x88 | x18 y102, 285 wide (divider x303), height 345 | y210, y284; icon x45, text x83 | 0 | 1 |
| 1280 `/` | x18 y14, 1244x88 | 285-wide rail persists (>=1024px) | y210, y284 | 0 | 1 |
| 768 `/` | x12 y10, 744x88 | compact row x12 y98, 744x73 | horizontal, 44px targets | 0 | 1 |
| 390 `/` | x12 y10, 366x88 | compact row x12 y98, 366x73 | horizontal, 44px targets | 0 | 1 |
| 200% zoom `/` | 908x88 at CSS 944px | compact row 908x73 | horizontal | 0 | 1 |

Reviewed captures in `reference/sidebar/` (recommend/compare 1888,
recommend 1280/768/390, 1888-zoom200) confirm: identical rail width, divider
and brand header on both routes; Recommend cyan-active with the search icon
and Compare gray-mid with opposing arrows; exactly one navigation region at
every scale with no duplicate or hidden-focusable options; the dev-tools
badge in captures is a Next.js dev-only overlay, not application UI.

Sidebar/header dimensions match across pages per the app-shell spec, and no
duplicate or hidden-focusable navigation remains.

## Phase 6 — US4: Recommend hero only

### T022 — Hero acceptance checks
`frontend/tests/recommend-hero.spec.ts` covers:
- Recommend shows exactly one `h1` with the exact text `Ready to study abroad?`;
  the old eyebrow, headline and supporting sentence are absent within `main`.
- The plane is a single decorative `svg` in `main`: `aria-hidden`, not a
  link/tab stop, `pointer-events: none`.
- Reference anchors at 1888x1337 with 8px tolerance: heading x417/y193, 48px
  tall on one line; plane x1422/y172 at 116x115.
- 390px mobile: 32px/500 heading, plane visible, no horizontal overflow.
- Compare guard: its own eyebrow, `Compare module mappings.` h1, supporting
  sentence, both pickers and one mapping row survive the Recommend hero swap.

TDD ordering confirmed: the spec ran 3 failing / 1 skipped before T024 and
4/4 after.

### T023/T024 — Component, scoped styles, page integration
- `frontend/components/recommend/RecommendHero.tsx`: heading plus an outlined
  paper-plane SVG. The outline is light (`--text-secondary`); the fold detail
  follows the tracked accent token `--primary` (cyan under the committed
  override), honouring the "coral detail" wording via the token the user pins.
- `frontend/components/recommend/recommend.module.css` (new): reserved hero
  region `min-height: 296px` so the picker label starts at y370 (reference);
  heading absolute at x417/y193, 2.5rem/500/1.2, single line; plane absolute at
  x1422/y172, 116x115, `pointer-events: none`; <=1556px plane 84x83 inset
  right 66px; 1024-1140px heading left 305px (clears the rail); <=1023px
  heading left 24px; <=800px hero flows statically and the heading wraps
  naturally (plane 72x71); <=650px heading 2rem/32px, matching the global
  breakpoint.
- `frontend/app/page.tsx`: only the hero markup was replaced with
  `<RecommendHero />`; data fetching, effects, picker and results sections are
  untouched. `globals.css` is untouched because Compare still uses the global
  `.hero`/`.eyebrow` markup (out of phase scope).
- Absolute placement uses page coordinates (no positioned ancestor), which
  matches the reference; smaller source typography is NOT enlarged to fill the
  sketch's wider headline box (40px type renders 413px wide where the sketch
  hero spanned ~930px; the plane stays at x1422).

### Repair — content column width (shell defect surfaced by US4)
With the old in-flow 80px hero removed, the grid item `.content` (auto margins
+ max-width, no width) shrink-fit to its largest in-flow child: the picker
collapsed 675 -> 207px, contradicting the phase-4 "1100px capped content
column" design. Repair in `frontend/components/layout/app-shell.module.css`:
`.content { width: 100%; }` so the column is definite (1052px inside padding
at 1888) instead of shrink-fit. Header/rail untouched.

### Verification (macOS, Playwright 1.56.1 Chromium)

| Check (from frontend/) | Result |
| --- | --- |
| `npx playwright test tests/recommend-hero.spec.ts` | PASS 4/4 |
| `npx playwright test tests/theme.spec.ts` | PASS 4/4 |
| `npx playwright test tests/app-shell.spec.ts tests/flows.spec.ts` | 13 passed / 9 failed — identical to the pre-phase baseline: 5 app-shell failures inherited from the post-phase-5 restyle (brand casing, header geometry) and 4 stale `.card-count` flows failures owned by US6. No new failures. |
| `npm run typecheck` | PASS |
| `npm run lint` | PASS |

Measured at 1888x1337: heading x417.0 y193.0 413.2x48 (one line); plane at
x1422.0 y172.0, 116x115; picker label returns to x507 y370 at its full 600px
width. At 390: 32px heading wraps in flow, plane 72x71, overflow 0.

Captures (fixed env) in `reference/hero/`: `recommend-idle-1888.png`,
`compare-loaded-1888.png` (CS x Toronto, 6 mapping rows), and
`recommend-idle-390.png` (full page), reviewed against the anchors above.

## Phase 7 — US5: restyle and position the degree picker

### T026 — Picker acceptance checks
`frontend/tests/recommend-picker.spec.ts` adds seven API-mocked checks:
- Recommend exposes the exact label `Degree Programme`, placeholder
  `Choose your degree programme`, no cards on first load, and the reference
  field bounds. At 1888x1337 the field is asserted within 8px of x726/y405 and
  526x60; the label text centre is asserted within 8px of x990.
- Focus opens the full degree list; filtering matches both the major name and
  the full degree title; no-match keeps the existing message.
- ArrowDown/ArrowUp, Home, End, Enter and Escape preserve selection semantics.
- Clearing removes rendered results immediately and restores the placeholder.
- A delayed Computer Science response cannot replace a newer AI selection.
- Catalog loading and error states remain explicit and keep the picker absent on
  failure.
- Compare retains `Degree programme` and `Search degree programmes`.

TDD ordering confirmed: the spec ran 1 passed / 6 failed before implementation
and 7/7 after.

### T027 — Shared picker placeholder override
`frontend/components/DegreeCombobox.tsx` accepts an optional `placeholder` prop
defaulting to `Search degree programmes`; the default label stays
`Degree programme`. Compare therefore keeps its original copy and shared
TypableDropdown semantics, including name-based selection and title/name search.
No second picker was added.

### T028/T029 — Wrapper, scoped styles and page integration
- `frontend/components/recommend/RecommendDegreeField.tsx` is a presentation
  wrapper passing `Degree Programme` and `Choose your degree programme`; the page
  continues to own catalog, selection, abortable requests and status state.
- `frontend/components/recommend/recommend.module.css` sets a fluid
  `min(526px, 100%)` frame, 53px top spacing at the reference width (clamped to
  24px on phones), 60px field height, 16px type, centred label/value, `.25rem`
  radius and the pinned focus ring. Above 1600px the frame keeps the reference's
  slightly left-of-centre anchor; it centres naturally at smaller widths.
- The field uses the committed dark `--card` surface, not the earlier white
  surface wording in T028: the user's dark-theme override in
  `contracts/nusmods-theme.md` supersedes that colour while the geometry, border
  and focus treatment remain as specified.
- `frontend/app/page.tsx` mounts `RecommendDegreeField` in the existing catalog
  branch without moving state. Recommend label lookups in
  `frontend/tests/flows.spec.ts` now use `Degree Programme`; Compare lookups stay
  `Degree programme`. Theme/app-shell lookups need no change because Playwright
  role-name matching is case-insensitive.

### T030 — Validation (macOS, Playwright 1.56.1 Chromium)

| Check (from frontend/) | Result |
| --- | --- |
| `npx playwright test tests/recommend-picker.spec.ts` | PASS 7/7 |
| `npx playwright test tests/recommend-picker.spec.ts tests/flows.spec.ts tests/theme.spec.ts tests/app-shell.spec.ts --workers=1` | 23 passed / 10 failed — no phase-7 regression: 5 inherited app-shell failures (brand casing, header/sidebar geometry), 4 stale `.card-count` flows failures owned by US6, and 1 inherited theme failure from the user's hero restyle (48px expected, 44px rendered). |
| `npm run lint` | PASS |
| `npm run typecheck` | PASS |

Phase-7 relevant flows cases: `no match and service error have clear states` and
`Compare ignores a delayed response for an old pair` pass; `keyboard boundaries,
Escape, and zero-count navigation` completes End/Home/Escape successfully and
fails only at the US6-owned `.card-count` selector.

Interaction checks: the open listbox starts above the first card and
`document.elementFromPoint` inside it resolves to the listbox; focus keeps the
cyan border and `0 0 0 3.2px` ring; clearing removes cards; the idle page renders
no fixture cards. Measured field: 526x60 at x726/y405 and label centre x990
(1888); at 390 the field is 342x60 with no horizontal overflow and the listbox
stays within the viewport.

Captures in `reference/picker/` (fixed environment):
`recommend-idle-1888.png`, `recommend-dropdown-1888.png` (listbox over the first
card), `recommend-idle-390.png`, and `recommend-dropdown-390.png`.

## Phase 8 — US6: reusable university card

### T031 — Card acceptance checks
`frontend/tests/recommend-card.spec.ts` adds four API-driven scenarios:
- Tier order: index 0 is featured, indices 1–2 secondary and indices 3+ compact;
  each card shows its 1-based rank, h2 title, country badge, `NUS Modules` primary
  count and `Partner University Modules` secondary count.
- `mapping_count` stays out of the card: the fixture with 22 mappings renders no
  "22" metric, and no `distinct`/`mappable` copy remains.
- Action: exactly one link per card, exact ASCII text `View Mappings -->`, encoded
  degree/university href, one focus stop and no button nested inside the link.
- 0/1 counts keep the plural labels; long names/countries stay complete above the
  footer without horizontal overflow.
- The isolated preview serves six repeated-copy cards, displays rank `#1` on every
  card and intercepts the fixture link instead of leaving the harness.

TDD evidence: before implementation the file failed 3/3 at the missing `data-tier`
attribute and old count copy; after implementation it passed 4/4.

### T032/T033 — Component and tier styles
- `frontend/components/recommend/UniversityCard.tsx` composes the existing
  `Card`, `CardHeader`, `CardTitle`, `CardContent`, `CardFooter` and `Badge`
  primitives. Props are `recommendation`, `degree`, 1-based `rank` and
  `featured | secondary | compact` tier. Counts come straight from the API;
  `mapping_count` is unused by the view. The only control is one plain anchor to
  `/compare?degree=<encoded>&uni=<encoded>`.
- `frontend/components/recommend/recommend.module.css` adds the temporary 6-column
  collection grid and card rules: 634x270 / 505x214 / 355x151 constrained
  footprints, `.35rem` radius, 1px border, 32/24/20 titles, 24/20/16 NUS metrics,
  14px partner/action and 12px badge type. Lower-right footer, rank/count insets
  and natural growth for long text are preserved.
- At `max-width: 650px` cards stack in one column with 24px titles, 20px NUS
  metrics, 14px supporting/badge/action text and a 44px action target.

Note: task text still names the earlier white surface; the committed dark tokens
(`--card`/`--border`) remain authoritative, matching the user theme override.

### T034 — Collection integration and flow selectors
- `frontend/components/UniversityCards.tsx` now maps incoming order onto
  `UniversityCard` tiers and keeps the section/region label. The old inline card
  markup, nested `Button`/`Link`, Unicode arrow and `text-6xl` are gone.
- Obsolete `.university-card*`, `.card*`, `.top-card`/`.half-card`/`.third-card`
  rules were removed from `frontend/app/globals.css`; the temporary collection
  grid moved to the scoped Recommend module.
- `frontend/tests/flows.spec.ts` now checks the new labels (`NUS Modules`,
  `Partner University Modules`) and exact ranks. API expectations, Compare
  behavior and deep links are unchanged. The old width-ratio assertions were
  intentionally left for US7.
- `frontend/tests/theme.spec.ts` card lookups now use semantic elements
  (`p`, badge text and the action link) rather than removed class names. Card
  surface, radius, title/metric sizes and footer assertions pass; the remaining
  theme failures are inherited accent-token expectations.

Focused result: `npx playwright test tests/flows.spec.ts` -> 8 passed / 1 failed.
The single failure is `flows.spec.ts:63` reaching the stale US7 width ratios
(secondary/featured 0.706 against the old 0.45–0.51); all preceding rank/count
assertions in that test pass.

### T035 — Isolated preview harness
- `frontend/tests/fixtures/UniversityCardPreview.tsx` renders the six
  `visualRecommendations` through the real `UniversityCard` with
  `VISUAL_DISPLAY_RANK = 1`, repeated `University Name`/`Country`, NUS 10 and
  partner 12.
- `frontend/tests/fixtures/preview-server.mjs` is a Node-only server that
  transpiles the real TSX, serves the scoped card CSS on port 18767 and intercepts
  fixture links. It is not a Next route and is not imported by application code.
- `frontend/playwright.config.ts` starts the harness beside the API and frontend
  servers; `recommend-card.spec.ts` confirms the preview cards, repeated rank and
  intercepted action.

### T036 — Validation (macOS, Playwright 1.56.1 Chromium)

| Check (from frontend/) | Result |
| --- | --- |
| `npx playwright test tests/recommend-card.spec.ts` | PASS 4/4 (9–10s) |
| `npx playwright test tests/flows.spec.ts` | 8 passed / 1 failed — only the US7-owned stale card-width ratios at `flows.spec.ts:63` |
| `npx playwright test` | 34 passed / 10 failed — all ten are inherited and documented below |
| `npm run typecheck` | PASS |
| `npm run lint` | PASS |
| Full-suite time | 40.4s |

Full-suite failures, all present before this phase or scheduled for US7:
- 5 app-shell cases: lowercase brand copy, frame/header anchors, rail anchors and
  390px brand copy inherited from the post-phase-5 restyle.
- 3 theme cases: Comic Sans hero family/line-height and cyan-vs-committed accent
  expectations after the user's hero/color changes.
- 1 hero case: system-font expectation superseded by Comic Sans.
- 1 flow case: old card width ratios owned by US7.

Live count checks from the API (no data changed):
- Artificial Intelligence / University of Toronto: NUS 6, partner 9,
  mapping_count 9, Compare rows 9.
- Business Analytics / University of Western Australia, The: NUS 11, partner 19,
  mapping_count 22, Compare rows 22. The browser flow also verifies Korea
  University NUS 11 / partner 17 and the encoded Compare deep link.

The phase adds no production demo cards, no public preview route and no backend
changes.

### Post-phase 8 follow-up — featured card width
The user asked for rank 1 to span the same length as the cards below it. The
featured and secondary max-width caps were removed, so all three rows share the
full content width (1052px at the 1888px reference viewport) while the 6-column
tier ratios still hold. At 390px every card stacks at 100%.

Validation from `frontend/`:
`npx playwright test tests/recommend-card.spec.ts tests/flows.spec.ts` -> 13/13
passed. This includes the former US7 width-ratio check: featured 1052px, each
secondary 518px and each compact 340px, with 16px gaps.
