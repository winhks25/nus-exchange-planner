# Implementation validation guide

This document describes checks to run after implementation; planning alone does not pass them.

## Prerequisites

Use the repository's existing Node/npm and Python/uv environment. Install locked dependencies with `npm ci` in `frontend/` and `uv sync` in `backend/` if needed. Read `frontend/AGENTS.md` and locally installed Next.js layout guides before editing application code. Keep source JSON intact.

## Automated checks

From `frontend/`:

```sh
npm run lint
npm run typecheck
npm run build
npm run test:e2e
```

Playwright already starts the backend at 127.0.0.1:18765 and frontend at 127.0.0.1:18766; these ports must be available. Do not start duplicate servers. The new visual test file should also be runnable using `npx playwright test tests/recommend-visual.spec.ts` after it exists.

For interactive review, run `./dev` from the repository root using the documented local setup in README.md.

## Fixture data and capture settings

Deterministic data lives in `frontend/tests/fixtures/recommendations.ts`; interception
helpers live in `frontend/tests/helpers/recommendation-fixtures.ts`. Both are
test-only and must never be imported by `frontend/app/page.tsx`, production
components or any route entry.

- `apiRecommendations` provides unique synthetic universities with typed country and
  count fields; `recommendationResultVariants` covers 0/1/2/5/6/7-result lists;
  `longNameRecommendations` covers long university and country text.
- `visualRecommendations` is the separate exact-copy fixture for the isolated
  component harness only: six unique internal IDs, repeated `University Name` /
  `Country`, NUS 10 / partner 12, and a harness-supplied displayed rank of `#1`.
  It intentionally differs from the API fixture and must not appear in production or
  normal API-driven results.
- Usage in a spec:

  ```ts
  import { openRecommendWithFixtures } from "./helpers/recommendation-fixtures";
  import { recommendationResultVariants } from "./fixtures/recommendations";

  await openRecommendWithFixtures(page, {
    recommendations: recommendationResultVariants.six,
  });
  ```

  `openRecommendWithFixtures` intercepts `/api/v1/catalog` and
  `/api/v1/recommendations`, selects a valid degree and awaits the rendered card
  count. Use `installRecommendationFixtures` when a test needs to navigate or delay
  responses itself. Keep real-API scenarios in `frontend/tests/flows.spec.ts`;
  production-page tests use these API mocks, while repeated-placeholder display is
  reserved for the isolated component harness introduced in US6.

Fixed visual capture settings for all screenshots and geometry checks: macOS
26.5.1, Playwright 1.56.1 bundled Chromium (Desktop Chrome profile), viewport
1888×1337, deviceScaleFactor 1. The old PNG is a geometry reference only, never the
themed whole-image baseline.

## Visual reference scenario

1. Render the test-only six-card fixture with the source system font stack, clean SVG icons and no animations. Display all screenshot placeholder values including repeated #1; this does not change production ranks.
2. Capture at 1888×1337, deviceScaleFactor 1, and normalize the saved reference PNG to the same dimensions for comparison. Also inspect at 2202×1560 if responsive scaling is designed for the original canvas.
3. Compare side-by-side and with an opacity overlay: outer frame/header/panel, title and plane, degree field, 1/2/3 rows, action positions and component bounding boxes. Target key reference anchor positions and sizes within 8 normalized pixels; compare layout geometry only: the old glyph shapes, type sizes and sketch contours are intentionally superseded.
4. Verify exact strings from contracts/recommend-ui.md, including casing and ASCII action arrow. Compare each card tier separately and verify its new type sizes against the UI contract. Save captures and record actual remaining discrepancies; do not approve snapshots merely because they exist.
5. Ensure the fixture cannot appear in normal API-driven results. Separately test the empty-picker production state; it intentionally has no cards.

## Live functional scenario

1. Load `/`: new frame/nav/hero/field, no fixture cards. Focus picker; filter by major and degree title; select with keyboard. Verify visible label `Degree Programme` and placeholder `Choose your degree programme` before selection.
2. Select a valid degree: API-ordered university names/countries/ranks populate all cards. Primary label is NUS Modules; secondary is Partner University Modules. No visible mapping-row metric on these cards.
3. Toronto Artificial Intelligence regression: NUS 6, partner 9; action opens Compare with 9 rows. Western Australia Business Analytics still has 19 distinct partner modules and 22 rows. Validate API values rather than replacing them with reference 10/12.
4. Change/clear degree quickly: old results disappear; no stale response restores them. Verify loading/error/no-match feedback, zero-count cards and zero-result response without phantom cards.
5. Follow View Mappings by keyboard; encoded degree and university preselect Compare. Compare shows the same header, left navigation and outer frame as Recommend, with Compare marked active; its content still shows the correct three-count summary and mapping controls.
6. Test repeated/long names, long country labels and 0/1/2/5/6/7 result lists with mocked responses. Titles remain complete, footer stays clear of text, and no empty grid slots precede valid cards.

## Shared-shell validation

Navigate Recommend → Compare → Recommend, load `/compare` directly, and use browser back/forward. Confirm one header containing only the lowercase site-name link `nus exchange planner` and one separate navigation panel throughout, unchanged shell styling, correct active-link state and no duplicated chrome. Confirm new routes inherit the root-layout shell automatically. The shared shell stays mounted during client-side route changes; page content and its height may change naturally.

## Responsive and access checks

Capture at 1888,1440, 1280, 768 and 390px widths. Confirm documented row transitions, readable type and rank order; check 200% zoom, tab focus, Enter/Escape/Home/End/arrow controls, and listbox visibility beyond decorative borders. Inspect anchors for nested controls and decorative SVG for accessibility noise. Compare screenshots must show the intended shared shell while applying the shared theme to page-specific controls and mapping rows while preserving their layout. At each viewport compare header height, rail width, brand typography and icon placement across both routes. Confirm the same compact navigation behavior on narrow screens.

Update old tests' half/third width ratios, obsolete card-count selectors and old Recommend label expectations. Keep ranking, data consistency, keyboard and deep-link assertions. Follow contracts/recommend-ui.md and data-model.md rather than duplicating presentation rules in multiple test helpers.

## Theme acceptance

Verify computed colors, font stack, font sizes, weights, line heights, border widths and radii against contracts/nusmods-theme.md and the role table in contracts/recommend-ui.md. Confirm white field backgrounds, gray placeholders/dividers, coral active navigation and focus states, and smooth borders. Check dropdown hover/selected/error states. Use a fixed OS/browser for system-font screenshots. Confirm no hand-drawn font, light-blue sketch fills or 80px sketch hero remains. The saved sketch and earlier mockup must not be used as whole-image pixel baselines for the updated theme.

Use a geometry comparison against the old fixture plus a new reviewed themed screenshot baseline. Source-reference theme matching must not pull in NUSMods header height, sidebar width, page padding or additional UI. Confirm the unchanged exact-copy table and shared shell on both routes.

Header-specific acceptance: on both pages and all tested viewports, the header has exactly one visible content item—the site-name link—and no nav links, icon, subtitle, input or action. Mobile navigation must remain in its own row below the header.
