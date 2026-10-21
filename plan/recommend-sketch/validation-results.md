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
