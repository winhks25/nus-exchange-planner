# Exchange planner enhancements

Source: [original requirements](source-requirements.md), preserved verbatim, and [wireframe](reference/universities.png). Date: 2026-10-25. This document organizes the requested requirements; priorities and edge-case defaults below are planning assumptions.

| Story | Priority | Outcome | Requirements |
| --- | --- | --- | --- |
| US1 | P1 | Faculty-aware degree selection on Recommend and Mappings | DB-01, FR-01–05 |
| US2 | P1 | Immediate dependent geographic filtering on Recommend and Universities | FR-06–11 |
| US3 | P1 | Browse all universities, optionally restricted by faculty | DB-02, FR-12–16 |
| US4 | P1 | Photograph, location, official website and mapping action on each card | DB-03, Feature 4 |
| US5 | P1 | Open mappings for a card while retaining other Mappings selections | FR-17–20 |

## Explicit planning defaults and unresolved inputs

- Existing schema uses `partner_universities`, `degrees.faculty` and `nus_modules.offering_faculty`; verify the deployed schema before migration. Prefer an additive nullable module `faculty_id` foreign key with audited backfill, retaining legacy text until its readers are migrated. Do not infer degree membership from the faculties offering its modules.
- A direct degree choice sets its alphabetically first faculty even when another compatible faculty was previously selected. Explicit faculty changes retain a compatible degree. Clearing faculty leaves the degree intact and exposes all degrees; choosing that degree again derives faculty. A degree without recorded membership remains selectable with faculty unset.
- Geographic options come from the full university catalog, constrained by parent geography; results combine all active categories. Remove invalid child selections when parent selections change. City identity includes country to disambiguate duplicate city names. Missing geographic values match only when that category is unrestricted.
- Initial directory includes all partners, even those without mappings or availability. A selected faculty uses only explicit availability links. Represent verified university-wide availability as explicit links to all relevant faculties; maintain this rule when faculties are added. Do not infer availability from existing course mappings.
- Three cards per row on ordinary desktop and four on wide desktop, two on tablet and one on mobile. The wireframe supplies layout and content hierarchy; retain the application's existing visual theme.
- Preserve Mappings state across routes in a root-mounted client provider. Explicit URL values override remembered values; a directory action replaces only the university. Never copy the directory faculty into Mappings implicitly.
- **No-degree case:** existing mappings API requires a degree. Proposed default: preselect the university and prompt for a degree, then load automatically once chosen. Do not silently choose a degree or add an all-degrees endpoint. This exception to unconditional FR-20 needs product confirmation before final acceptance; record it as an unresolved decision rather than claiming FR-20 fully satisfied.
- Availability data and reusable photos need verified sources. Missing photos/websites are allowed; unknown availability remains unknown. Record unresolved data coverage explicitly.

No automated test authoring or TDD was requested. Tasks include manual acceptance and execution of relevant existing checks, not a new test suite.
