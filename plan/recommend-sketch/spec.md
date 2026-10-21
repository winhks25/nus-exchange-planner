# Feature requirements: Recommend layout with NUSMods theme

## User intent

Use the supplied screenshot's header, left panel and outer frame across the entire application. Keep its layout and wording on Recommend/home, but use the NUSMods theme, including font sizes, as defined in contracts/nusmods-theme.md. Plan implementation by component, including cards and left panel. Use the exact visible static wording. User clarification: university/card values are placeholders and must be replaced by real values.

## Required outcome

1. Apply the pinned NUSMods default light theme: white backgrounds, system sans-serif typography, gray text/borders and coral primary states. Replace hand-drawn outlines, blue fills and sketch type sizes; preserve layout and all wording.
2. One shared rounded outer frame, full-width header row containing only the lowercase site name `nus exchange planner`, left navigation panel and vertical divider on every application page, including Compare and future routes. The shared shell persists across navigation; only page content and active-link state change. Header/panel sizing, typography, icons and responsive behavior remain consistent across pages.
3. Source-scale system-font heading and clean paper-plane illustration in the same positions; centered degree picker below it.
4. Results arranged in rows of one featured, two secondary, then three compact cards per row. Featured is centered and narrower than the full content area. Every result remains visible in rank order.
5. Font sizes vary by card tier as well as semantic role. Use the contract's NUSMods-derived role sizes; do not retain the screenshot's handwritten size values.
6. Static text: `nus exchange planner`, `Recommend`, `Compare`, `Ready to study abroad?`, `Degree Programme`, `Choose your degree programme`, `NUS Modules`, `Partner University Modules`, `View Mappings -->`.
7. Real ranks, university names, countries and both module counts populate cards. No visible mapping-row count on Recommend. Mapping-row count stays in data and Compare.
8. Existing selection/search/status behavior and Compare URLs remain functional. No dummy result cards before selection in production.
9. Responsive layouts remain usable and preserve rank order; desktop reference fidelity does not require shrinking text into unreadability on phones.

## Precedence

These presentation requirements supersede conflicting Recommend presentation text in the old MVP documents. Non-presentation rules in `plan/featureSpecs.md` continue to apply. The shared shell applies to Compare as well. Compare adopts the same theme colors, typography and controls; its wording, layout and behavior remain unchanged.

## Acceptance

Use the exact-copy six-card fixture to assess the supplied screenshot, real responses to assess dynamic content, and the checks in quickstart.md to assess functionality and responsive behavior. The source image's repeated `#1` is fixture copy, not the production ranking algorithm.

## Theme precedence

The latest theme request overrides earlier aesthetic requirements and the generated mockup. Preserve screenshot geometry and exact text, but validate colors, fonts, sizes and component styling against contracts/nusmods-theme.md. Do not import NUSMods page layout, navigation items, branding or timetable features.

## Delivery user stories

These stories decompose the existing requirements for modular delivery; they add no product scope. P1 establishes the common application presentation; P2 delivers the Recommend content within it. Each story is a separate implementation phase in tasks.md.

### US1 — Consistent NUSMods theme (P1)

As a student, I see consistent NUSMods colors, system typography and control styling on both pages, without a layout change.

Traceability: Required outcomes 1, 5, 9; theme contract and UI typography table.

### US2 — Shared application frame and header (P1)

As a student, I see the same application frame and a header row containing only `nus exchange planner` on every route. Navigation is outside that row, including on mobile.

Traceability: Required outcome 2; root-layout ownership in data-model.md.

### US3 — Shared left navigation (P1)

As a student, I navigate between pages using the same left panel, with the current page clearly indicated.

Traceability: Required outcome 2; navigation and responsive UI contract.

### US4 — Recommend hero (P2)

As a student, I see the exact study-abroad heading and paper-plane illustration in the agreed position.

Traceability: Required outcomes 3, 6; reference coordinates and source typography.

### US5 — Centered degree picker (P2)

As a student, I choose a degree from the centered field with the exact label and placeholder while retaining keyboard search.

Traceability: Required outcomes 3, 6, 8; selection state transitions.

### US6 — Reusable university card (P2)

As a student, I can read real university details and two clearly labeled counts, then open their mappings.

Traceability: Required outcomes 5–8; Recommendation view model and action contract.

### US7 — Tiered recommendation layout (P2)

As a student, I see all ranked universities in the agreed 1–2–3 arrangement, with readable responsive layouts.

Traceability: Required outcomes 4, 8, 9; ordered collection and geometry contract.

