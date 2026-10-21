# Tasks: Consistent page loading spinner

Date: 2026-10-21. Status: ready for implementation; all tasks pending.

Sources: [spec.md](spec.md), [plan.md](plan.md). Paths below are repository-relative. The scope includes both current routes, common route fallbacks, initial catalog requests, and selection-triggered requests. Keep the header/sidebar visible. New routes inherit the common route fallback; future effect-based requests must explicitly reuse the component.

Workflow adaptation: `.specify/` and its setup script/template/constitution/hook registry are absent. The setup command was attempted. This checklist follows the skill's structure in the repository's established planning directory. No pre/post hooks are available. No new automated test tasks are added; acceptance below is manual plus existing checks.

## Phase 1: Setup

- [X] T001 Read frontend/AGENTS.md, the installed loading.md and linking-and-navigating.md guides under frontend/node_modules/next/dist/docs/01-app/, and plan/loading-spinner/spec.md; inspect the working diff and record the baseline and applicable constraints in plan/loading-spinner/validation-results.md without discarding existing edits.

## Phase 2: Foundation

- [X] T002 Create frontend/components/loading/LoadingState.tsx with a typed label prop (default “Loading page…”) and page/results variants; render one role="status" with visible text and an aria-hidden decorative ring, no main landmark, focus changes, timers, or fetching. Create frontend/components/loading/loading-state.module.css with centered responsive layouts, existing theme tokens, transform-only ring rotation, and a prefers-reduced-motion override that keeps text visible with a static ring.

**Gate:** Shared component supports both loading sizes and accessible status labeling before route/page integration.

## Phase 3: US1 — Page and route loading (P1, MVP)

**Goal:** Consistent initial and route loading within the persistent application shell.

**Independent verification:** Delay catalog responses on direct entry/refresh at `/` and `/compare`; verify one spinner/status, visible usable navigation, and replacement by ready/error content. Exercise a genuinely pending route boundary (using developer tools to suspend it if necessary), Compare Suspense, mobile layout, and reduced motion. Instant transitions should remain instant.

- [X] T003 [P] [US1] Add frontend/app/loading.tsx using the page variant of LoadingState inside one main landmark; verify frontend/app/layout.tsx keeps the fallback under its existing AppShell so header/sidebar persist and all descendant routes share the fallback.
- [X] T004 [P] [US1] Update frontend/app/page.tsx to render page-variant LoadingState with “Loading degree programmes…” while loading-catalog, replacing page content inside main until catalog success/error; retain the existing ready/error paths and request cleanup.
- [X] T005 [P] [US1] Update frontend/app/compare/page.tsx to render page-variant LoadingState with “Loading choices…” for loading-catalog and the existing Suspense fallback; ensure each rendered branch has one main landmark, preserve URL initialization and existing catalog errors, and avoid simultaneous duplicate loading indicators.

**Checkpoint:** US1 can ship as the MVP; result-fetch loading remains the existing status text until US2.

## Phase 4: US2 — Result loading (P1)

**Goal:** Reuse the spinner during recommendation and mapping requests while selectors remain usable.

**Independent verification:** Delay each result endpoint, change/clear selections, simulate failed and empty responses, and navigate away mid-request. Verify pending indicators disappear correctly and obsolete requests cannot overwrite newer results. Open Compare with valid degree/uni query values and verify continuous truthful loading through both dependent requests.

- [X] T006 [P] [US2] Update frontend/app/page.tsx to use results-variant LoadingState with “Finding partner universities…” for the loading state while keeping hero and degree selector visible; verify clear, success, empty results, error, and rapid selection transitions, adding request guards only if needed to prevent stale completion.
- [X] T007 [P] [US2] Update frontend/app/compare/page.tsx to use results-variant LoadingState with “Loading mappings…” while retaining hero/selectors; keep valid URL-driven catalog-to-mappings transitions loading until the appropriate request settles, and preserve invalid-link notes, clear behavior, error/empty results, cancellation, and stale-response protection.

## Phase 5: Polish and cross-cutting verification

- [ ] T008 Check both stories' acceptance scenarios at desktop and 390px mobile width, with reduced motion and throttled/failed requests; verify shared navigation remains interactive and there are no duplicate statuses, stuck spinners, or overflow, and record outcomes in plan/loading-spinner/validation-results.md.
- [ ] T009 Run lint, typecheck, build, and relevant existing Playwright scenarios using frontend/package.json (including frontend/tests/recommend-picker.spec.ts, frontend/tests/flows.spec.ts, and frontend/tests/app-shell.spec.ts); preserve existing status text assertions where applicable, adjust only assertions directly affected by the agreed presentation, and record commands, outcomes, and any pre-existing failures in plan/loading-spinner/validation-results.md.

## Dependencies

`T001 → T002 → US1 (T003, T004, T005) → US2 (T006, T007) → T008 → T009`

US2 uses the shared component and page integrations delivered by US1. Story checks are independently executable once their prerequisites exist. Do not concurrently edit a page for both stories.

## Parallel opportunities

- US1: after T002, T003 (route fallback), T004 (Recommend), and T005 (Compare) touch different files and can proceed in parallel.
- US2: after US1, T006 (Recommend) and T007 (Compare) can proceed in parallel.
- Verification result writes remain sequential to avoid collisions in validation-results.md.

These are scheduling opportunities, not instructions to spawn agents.

## Implementation strategy

Complete setup and foundation, then ship US1 as the smallest useful increment. Add US2 to satisfy the full confirmed scope, then verify all acceptance scenarios and existing checks. Do not force spinner display on already-ready pages or add minimum-duration delays. Mark tasks complete only with implementation/verification evidence.

## Checklist audit

9 tasks: setup 1, foundation 1, US1 3, US2 2, polish 2. IDs T001–T009 are sequential. Every task has an unchecked checkbox, task ID, concrete file path, and a story label only in story phases. Five tasks have valid parallel markers.
