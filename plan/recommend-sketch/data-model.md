# Phase 1 data and component model

No database, stored data or API changes.

## Existing entities

- Degree: `name` (major identifier), `degree` (full title). Selection uses name; filtering searches both.
- Recommendation: `university`, `country`, `distinct_nus_module_count`, `partner_module_count`, `mapping_count`. API owns validation/counting/ranking; frontend displays nonnegative count values without recomputation.
- Catalog: existing degree and university arrays, fetched by RecommendPage.

## View-only models

UniversityCard receives a Recommendation, selected degree name, 1-based ordinal rank and tier (`featured`, `secondary`, `compact`). Index 0 is featured; indices 1–2 secondary; subsequent indices compact. The collection preserves incoming order. No university is hidden to fit a row.

Derived visible strings: `#${rank}`, university, country, `${distinct_nus_module_count} NUS Modules`, `${partner_module_count} Partner University Modules`. Keep the exact plural labels even when the count is 1 to meet the copy contract. Link target uses existing URL-encoded degree and university names. mapping_count is retained but not displayed on Recommend.

The visual fixture has six unique internal fixture IDs, repeated `University Name` and `Country` labels, NUS=10 and partner=12, and displayed rank `#1` on each card to reproduce the drawing. This explicit test-only display override must never affect production ordinal rank. No mappings action in a fixture should be mistaken for a real university deep link.

## State transitions

- Mount → loading-catalog → idle on success, error on failure.
- Untouched idle with no degree → hero and picker only, no cards.
- Valid degree selection → clear old results → loading → new ordered results or error.
- Degree change → cancel obsolete request and clear old cards immediately.
- Clear/invalid selection → no cards and existing choose-degree feedback after interaction.
- Zero-count results → normal visible clickable cards; empty array → no phantom fixture cards.

Display status text only for its state; reference fixture intentionally isolates the normal visual composition. Reuse existing status and error semantics.

## Shared navigation state

AppShell is mounted once by the root layout and wraps every route. AppHeader has no page-specific state and renders only the lowercase `nus exchange planner` link. Navigation is a separate sibling region. AppSidebar derives the active link from the current pathname; it does not store a duplicate selected-page value. Route changes replace content while retaining shared chrome. No API or persisted data is needed for navigation state.

## Theme update

The NUSMods theme changes presentation tokens only. Data entities, state transitions, labels, live-value substitution, route parameters and shared-shell ownership above are unchanged. Theme source and role mappings live in contracts/nusmods-theme.md and contracts/recommend-ui.md.
