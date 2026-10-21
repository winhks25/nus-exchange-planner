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
