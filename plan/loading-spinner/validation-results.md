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
