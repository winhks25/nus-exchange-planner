# Recommend/home: screenshot-led modular implementation plan

Date: 2026-10-21. Branch at planning time: `master`.
Status: Phase 0 research and Phase 1 design complete; implementation not started.

## Scope and source of truth

Use the reference header, left navigation panel and outer frame throughout the entire application, including Recommend, Compare and future pages. Preserve the supplied reference layout on Recommend (`/`), including whitespace, shell and panel geometry, paper-plane position and tiered university cards, while applying the NUSMods default light theme. Fonts, font sizes, colors, radii, borders and interaction styling now come from [the pinned theme contract](contracts/nusmods-theme.md). Layout and exact copy remain fixed. Use [the saved reference](reference/recommend-home.png), [UI contract](contracts/recommend-ui.md), and [feature requirements](spec.md) together. The user confirmed that university names, countries, ranks and counts are placeholders: render real values, retaining exact static copy.

This design supersedes the Recommend presentation clauses in `plan/featureSpecs.md` and `plan/implementation-plan.md`: featured card full-width sizing, half/third relative widths, partner-first count emphasis, visible mapping-row count, and previous action/picker/hero copy. All counting, ranking, fetching, keyboard behavior, and deep-link rules remain. Compare retains its own three-count summary and page content inside the new shared application shell.

## Workflow adaptation

The requested `.specify/scripts/python/setup_plan.py --json` was attempted and failed because this checkout has no `.specify` directory. There is no generated FEATURE_SPEC, template, constitution, or extension registry. This isolated feature folder follows the requested artifact structure without inventing a project constitution or overwriting the existing MVP plan. `spec.md` captures the current user requirements. No branch was created or changed. Pre-plan and post-plan hook checks: registry absent, skipped.

## Technical context

| Area | Existing choice / design |
| --- | --- |
| Application | Next.js App Router, React 19.2, TypeScript; manifest Next.js ^16.4.2 |
| Styling | Tailwind v4, globals.css, shadcn/Base UI Card and Badge primitives |
| Data | Existing read-only FastAPI; Recommendation and Catalog types unchanged |
| State | Existing client page owns selection, catalog, results, abortable requests and statuses |
| Assets | Clean decorative SVG icons; NUSMods system sans-serif stack, no font downloads |
| Validation | Existing Playwright flows plus reference fixture screenshots; lint, typecheck, build |
| Scope | Frontend presentation and focused tests; no backend or data migration |
| Reference | Original PNG 2202 × 1560; normalized measurement frame 1888 × 1337 |

Read `frontend/AGENTS.md` and the relevant installed Next.js guides before implementation. Existing uncommitted changes in globals.css, page.tsx, UniversityCards.tsx and ui/badge.tsx are the working baseline; do not reset them.

## Constitution and acceptance gates

No `.specify/memory/constitution.md` exists; constitutional evaluation is unavailable, not a claimed pass. Applicable requirements are checked before and after design:

- User reference and exact static wording: satisfied by explicit visual/copy contract.
- Modular delivery: satisfied by independently verifiable modules below.
- Live data integrity and navigation: existing API order/counts/deep links retained.
- Reuse of shared picker and Card primitives: retained.
- Shared application chrome: one persistent header, sidebar and outer frame in the root layout on every page; active navigation reflects the current route. Recommend content styles remain scoped; Compare functionality is regression-checked.
- Accessibility: real controls, visible focus, readable responsive sizes, decorative SVG excluded from accessibility tree.
- New dependencies: no runtime drawing library, font downloads or Bootstrap framework dependency; map source tokens into existing CSS/Tailwind components.

Post-design result: no known design gate violations. Layout fidelity and source-token matching are implementation acceptance gates and have not been verified by this planning work.

## Module boundaries

Proposed files under `frontend/` (names may follow local conventions):

- `components/recommend/UniversityCard.tsx`: one card, typed data + tier + rank + degree; no fetching.
- `components/UniversityCards.tsx`: existing public collection adapter; lays out ordered results using the new card.
- `components/layout/AppSidebar.tsx`: shared navigation links and icons, with route-aware active state.
- `components/layout/AppHeader.tsx`: shared header row containing only the site-name link `nus exchange planner` on every page; no navigation slot or other content.
- `components/layout/AppShell.tsx`: persistent outer frame, header/sidebar and page-content slot for the entire application.
- `components/recommend/RecommendHero.tsx`: exact heading and decorative plane.
- `components/recommend/RecommendDegreeField.tsx`: presentation wrapper over DegreeCombobox.
- `app/globals.css`: shared semantic theme tokens and source system font stack; avoid importing external framework resets.
- `components/layout/app-shell.module.css`: shared frame, header, sidebar, typography and responsive navigation styles.
- `components/recommend/recommend.module.css`: scoped Recommend content layout and tier typography.
- `components/DegreeCombobox.tsx`: optional placeholder customization; preserve current defaults for Compare.
- `app/page.tsx`: compose modules around existing state and effects.
- `app/layout.tsx`: mount AppShell once around all route children; remove the old header/navigation markup to avoid duplicate chrome.
- `tests/recommend-visual.spec.ts` and deterministic fixture data: visual contract and responsive checks.

Header requirement: the full-width top row contains only `nus exchange planner` (lowercase), linking to `/`. Navigation lives in the left panel, or a separate row below the header on mobile. Keep the agreed header geometry and theme typography.

Shared layout approach: root layout owns document/metadata/global base and a single AppShell wrapping all page children. AppHeader and AppSidebar retain the same dimensions, fonts, colors, icons and responsive behavior across routes. Only the active navigation indicator and page-content slot change during navigation. A small client-side navigation component derives aria-current from the pathname while the root layout remains a server component. Do not add a legacy Compare shell or duplicate shell markup in page components. Scope Recommend-only hero, picker and card styles to its content wrapper; apply common theme tokens deliberately to Compare controls and mapping rows without altering their layout or behavior.

## Modular build sequence

Each module is reviewable on its own before page assembly. A test-only component/fixture harness may be used; do not publish demo data as live results.

| Step | Work | Depends on | Done when |
| --- | --- | --- | --- |
| 0. Visual foundation | Pinned NUSMods theme tokens, system font stack, type role mappings, unchanged geometry | None | Computed styles match source-token contract; layout anchors match PNG |
| 1. Cards | Build one UniversityCard, then featured/secondary/compact variants; exact labels and single-anchor action | 0 | All three size/type variants match fixture; long names wrap; no nested interactive control |
| 2. Card collection | Build 1/2/3 row composition; center featured; continue later rows in threes | 1 | Six-card fixture matches proportions; 0/1/2/5/6/7 results produce no gaps reserved for nonexistent cards |
| 3. Left panel | Recommend and Compare links, clean search and opposing-arrow icons in theme colors, vertical divider | 0 | Same panel on every page; correct route-aware active-link semantics; links keyboard-operable |
| 4. Header and shell | Shared brand, round outer frame, horizontal divider, root-layout shell | 0, 3 | Header/panel align on Recommend and Compare; divider follows content; shell persists across navigation |
| 5. Hero | System-font heading at source h1 size and paper-plane line art | 0 | One-line reference desktop heading; icon aligned and hidden from assistive tech |
| 6. Degree field | Exact label and placeholder, centered white themed control, preserve shared picker behavior | 0 | Search/select/clear/Escape/arrow keys work; dropdown overlays cards without clipping |
| 7. Page assembly | Compose Recommend hero, field, collection and live state inside the shared shell | 2, 4, 5, 6 | Selection shows real ranked values; errors/loading/clear work; deep links correct |
| 8. Responsive and fidelity pass | Medium/mobile layouts, theme-token and geometry verification and screenshots | 7 | Visual and functional acceptance passes on both routes, including identical responsive chrome |

Do not implement all markup in page.tsx or duplicate the shared picker. Tier variants control sizes directly; do not CSS-transform entire cards to shrink them, which would distort text, hit targets and layout.

## Risks and resolutions

- NUSMods system font varies by OS; capture visual baselines on a fixed OS/browser and verify the declared stack.
- Old sketch type sizes are superseded by the source-backed role table. Keep container geometry and whitespace even when the new type is smaller; preserve 44px interaction targets.
- Real names are longer than placeholders. Permit wrapping and natural card growth, preserve complete names, and reserve footer space.
- The old functional tests encode obsolete presentation selectors and dimensions. Revise those assertions without dropping ranking/count/deep-link coverage.
- A selected degree replaces the placeholder with its name. Layout comparison uses a controlled fixture; normal live state follows application behavior.

## Deliverables

`spec.md`, `research.md`, `data-model.md`, `contracts/recommend-ui.md`, `contracts/nusmods-theme.md`, `quickstart.md`, and saved reference PNG. This workflow stops at design; no application code or task implementation is included.

## Detailed execution checklist

See [tasks.md](tasks.md) for the authoritative implementation sequence requested by the user: baseline and fixture preparation, then separate theme, shared frame/header, shared sidebar, hero, picker, card component and card layout phases, followed by verification. This refines the illustrative delivery table above without changing the design. Each phase integrates and verifies only its own change. Story IDs and priorities are recorded in spec.md.
