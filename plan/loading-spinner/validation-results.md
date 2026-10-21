# Validation results: consistent page loading spinner

## T001 baseline (2026-10-21)

Recorded before implementation so later checks can be compared against the working tree as found.

### Repository state

- Base commit: `5afbe7a` (`docs(recommend): record left-aligned partial rows`).
- Existing uncommitted edits preserved, not reverted or included in spinner commits:
  - `frontend/components/layout/app-shell.module.css`
  - `frontend/components/recommend/RecommendDegreeField.tsx`
  - `frontend/components/recommend/recommend.module.css`
- `plan/loading-spinner/` was untracked at baseline.

### Baseline checks

| Command | Result |
|---------|--------|
| `npm run lint` | Pass |
| `npm run typecheck` | Pass |

No Playwright or build run was needed for the baseline; T009 runs the full regression gate after implementation.

### Applicable constraints

- Next.js 16 App Router: a route `loading.tsx` is nested inside its segment `layout.tsx`, wraps `page.tsx` in Suspense, and keeps shared layouts interactive. It does not cover client-side effect requests, so pages must render loading UI from their own state as well.
- The persistent shell lives in `frontend/app/layout.tsx` via `AppShell`; loading UI must replace page content only.
- Use existing CSS module conventions and theme tokens (`--primary`, `--border`, `--foreground`, `--muted-foreground`). No new dependency, animation library, data model, or API change.
- Loading component API: typed `label` prop defaulting to “Loading page…”, `variant: "page" | "results"`, one `role="status"`, visible label, decorative `aria-hidden` ring, no main landmark, focus movement, timers, or fetching.
- Reduced motion: static ring with text still visible.
- Keep existing status wording: “Loading degree programmes…”, “Loading choices…”, “Finding partner universities…”, “Loading mappings…”.
- Preserve abort cleanup and prevent stale completions from overwriting newer results.

## T002 foundation (2026-10-21)

- Added `frontend/components/loading/LoadingState.tsx` and `loading-state.module.css`.
- One `role="status"` includes the visible label and an `aria-hidden` ring; the component has no main landmark, focus management, timers, or fetching.
- `page` and `results` variants share the theme tokens and centered layout; rotation uses `transform` only and stops under `prefers-reduced-motion: reduce`.
- `npm run lint`: pass.
- `npm run typecheck`: pass.

## T008 cross-cutting verification (2026-10-21)

Method: a temporary Playwright probe ran against the dev server and real backend, then was removed. It delayed catalog, recommendation, and mapping responses by 800–1200 ms, forced 503 responses, and emulated desktop (1440x900), mobile (390x844), and reduced motion. It also mounted a temporary suspended server route to exercise the root `loading.tsx` boundary; that route was removed.

All 9 scenarios passed:

| Scenario | Result |
|----------|--------|
| Desktop initial loading | One “Loading degree programmes…” status, ring is `aria-hidden`, header/sidebar visible and enabled, no overflow; picker replaces the status. |
| Mobile 390px initial loading | Same status, fully contained at 390px, shell visible, no overflow. |
| Reduced motion | “Loading degree programmes…” remains visible; ring stays visible with `animation-name: none`. |
| Catalog failure | Existing alert replaces loading; no status remains after settling; navigation stays visible. |
| Recommendation loading | One “Finding partner universities…” status; hero, picker, and navigation remain visible; picker stays editable. |
| Clear during result loading | Clearing removes the status immediately; the delayed response cannot restore results. |
| Recommendation failure | Existing alert replaces loading; no stuck status. |
| Compare deep link | “Loading choices…” progresses to “Loading mappings…” with no empty-state flash; selectors stay visible; the result summary replaces the status. |
| Compare mobile + pending route | “Loading choices…” is contained at 390px. A suspended route rendered the shared “Loading page…” fallback inside the persistent shell before the page content. |

No duplicate status elements, stuck spinners, or horizontal overflow were observed. Ready/instant transitions were not forced to wait.

## T009 regression gate (2026-10-21)

| Command | Result |
|---------|--------|
| `npm run lint` | Pass |
| `npm run typecheck` | Pass |
| `npm run build` | Pass; routes `/` and `/compare` build as static. Pre-existing SWC fallback warnings remain. |
| `npx playwright test tests/recommend-picker.spec.ts tests/flows.spec.ts tests/app-shell.spec.ts` | 21 passed, 8 failed |
| `npm run test:e2e` (full suite) | 45 passed, 18 failed |

Failure classification (no spinner regression):

- Pre-existing at feature HEAD (9 full-suite failures; reproduced with the three unrelated redesign edits stashed): brand copy expects “nus exchange planner” while the UI renders “NUS Exchange Planner” (three app-shell checks); Recommend frame and rail reference anchors; four hero/theme checks (`recommend-hero` font, `theme` type scale, card surfaces, picker focus).
- Caused by the preserved uncommitted Recommend redesign edits (9 full-suite failures): Compare frame geometry, card width ratio, picker centering, two extra hero containment checks, and four `recommend-visual` row/title checks. These same checks pass with those edits stashed.
- No assertions were changed: none of the failures involve the loading presentation, and the spinner behavior checks pass. The temporary verification files were deleted, and the generated `next-env.d.ts` change was restored.
