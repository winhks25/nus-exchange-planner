# Plan: Consistent page loading spinner

## Workflow and sources

The requested setup command `python3 .specify/scripts/python/setup_tasks.py --json` failed because `.specify/` does not exist. No template, constitution, or extension hook registry is available. Follow the existing `plan/<feature>/` convention and the speckit-tasks phase/checklist structure. This folder records the user's spinner request and confirmed shell behavior separately from the existing Recommend redesign. No application code is changed by task generation.

## Implementation approach

- Existing stack: Next.js App Router (manifest ^16.4.2), React 19.2, TypeScript, CSS modules, existing Playwright checks.
- Read `frontend/AGENTS.md` and installed Next.js loading/navigation documentation before implementation. The local `frontend/node_modules/next/dist/docs/01-app/03-api-reference/03-file-conventions/loading.md` was consulted during planning.
- Add `frontend/components/loading/LoadingState.tsx` and `loading-state.module.css`: a shared presentational component with `label` and `variant: "page" | "results"` props. Default label is “Loading page…”. A single `role="status"` contains text and an `aria-hidden` spinner; do not move focus. Consumers own main landmarks.
- Use a CSS border ring and transform rotation, existing `--primary`, `--border`, and `--foreground` tokens, and a reduced-motion override. The current application theme is the source of truth; older redesign prose must not reset it.
- `frontend/app/loading.tsx` provides the common route fallback under the root shell. Preserve `frontend/app/layout.tsx` and `frontend/components/layout/AppShell.tsx` ownership of the persistent header/sidebar.
- Both page components fetch catalog/results in effects. Route loading boundaries do not cover these requests: explicitly render LoadingState from their existing PageState values as well. Preserve abort cleanup and make stale request completions harmless if inspection reveals gaps.
- Replace Compare's local Suspense fallback too. Use page-sized loading for initial catalog/Suspense states and results-sized loading for selection requests. Ensure Compare URL initialization keeps its dependent loading sequence accurate.
- No data model, API contract, dependency, global request tracker, or router event abstraction is needed.

## Validation and delivery

Implement US1 first (shared component, route fallback, both initial-loading states), then US2 (both result-loading states). Manual verification covers throttled requests, route changes, errors, empty data, rapid selections, clear, deep links, reduced motion, and mobile. Existing `lint`, `typecheck`, `build`, and relevant Playwright scenarios are the regression gates; record failures honestly. Only update existing presentation assertions if the agreed UI requires it, retaining behavior/data assertions.

Preserve current uncommitted changes in `frontend/components/layout/app-shell.module.css`, `frontend/components/recommend/RecommendDegreeField.tsx`, and `frontend/components/recommend/recommend.module.css`; recheck the working tree before implementation.
