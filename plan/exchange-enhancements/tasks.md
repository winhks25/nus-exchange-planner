# Tasks — Exchange planner enhancements

Inputs: [spec](spec.md), [plan](plan.md), [original requirements](source-requirements.md), [wireframe](reference/universities.png).

Status: planning only; all implementation tasks remain unchecked. Paths are repository-relative. Files not currently present are intended deliverables. `<generated>` is the timestamp returned by the Supabase CLI, resolved once in T006 and reused thereafter. Read the spec defaults before implementation. No new automated test-writing tasks are included because neither TDD nor new tests were requested.

**Checklist:** `- [ ] Tnnn [P?] [USn?] action with file path`. `[P]` permits work alongside other independent tasks in the same ready phase, after earlier prerequisites are met; it is not permission to skip dependencies. Shared-file edits must be serialized.


## Phase 1: Setup

Capture the baseline and settle data contracts before changing behavior.

- [X] T001 Record current catalog payloads, recommendation order/counts, mappings deep links and schema/data inventory in `plan/exchange-enhancements/baseline.md`; inspect deployed columns and all consumers of degrees.faculty and nus_modules.offering_faculty, without printing credentials.
- [X] T002 Write the additive catalog contract and selection rules in `plan/exchange-enhancements/contracts.md`: faculties with stable IDs, degree faculty IDs, university stable ID/name/country/city/continent/faculty IDs/image/website and optional attribution; preserve existing fields and mapping query names.
- [X] T003 Record migration/backfill, unknown-data handling and the unresolved no-degree navigation acceptance decision in `plan/exchange-enhancements/decisions.md`; follow the explicit defaults in spec.md and distinguish confirmed source data from assumptions.

## Phase 2: Foundational prerequisites

Shared API and data preparation required by all stories.

- [X] T004 Create `backend/scripts/audit_exchange_enhancements.py` to report distinct legacy faculty labels, orphan relations, missing geography and university coverage; produce a dry-run report in `plan/exchange-enhancements/data-audit.md` with row counts and deterministic candidate mappings.
- [X] T005 Create `data/exchange-enhancements/faculty-aliases.json` from the audit, using reviewed canonical faculty names and explicit aliases; flag ambiguous/missing labels rather than merging unrelated faculties or deriving degree membership from module offerings.
- [X] T006 Use the Supabase CLI to generate `supabase/migrations/<generated>_exchange_enhancements.sql`; add faculties, degree_faculties, faculty_partner_universities, nullable nus_modules.faculty_id and nullable partner_universities.image/website. Use existing ID types, nonblank faculty names, unique relationship pairs, foreign keys and indexes for reverse lookups; no year or semester fields.
- [X] T007 In `supabase/migrations/<generated>_exchange_enhancements.sql`, enable RLS on new tables and grant only required SELECT access to the existing backend reader role using matching policies; preserve existing read-only access and avoid anonymous database writes.
- [X] T008 Implement repeatable, transactional backfill with dry-run mode in `backend/scripts/seed_exchange_enhancements.py`; preserve all valid existing degree/module/mapping relationships, resolve audited faculty aliases, retain unknown module faculty as null and legacy text until consumers migrate.
- [X] T009 Extend `backend/app/models.py` with additive catalog metadata and defaults for missing legacy fields; keep city, continent, image and website nullable and faculty memberships as lists without duplicating universities.
- [X] T010 Extend `backend/app/repositories/postgres_catalog.py` to fetch faculty memberships and all university metadata without inner-join exclusion or N+1 queries; preserve source order and existing ranking/mapping calculations.
- [X] T011 [P] Update `backend/app/repositories/json_catalog.py` to emit the additive catalog shape with empty memberships/null metadata where unavailable; preserve the frozen JSON source and existing recommendation/mapping behavior.
- [X] T012 [P] Mirror the agreed catalog shape in `frontend/lib/types.ts` and `frontend/lib/api.ts`; retain existing endpoint/query compatibility and AbortSignal behavior.
- [X] T013 Document and execute local/staging migration rehearsal in `plan/exchange-enhancements/migration-validation.md`: snapshot first, verify foreign keys/unique pairs/reader access, compare existing row counts and mapping outputs, rerun seeding safely and document rollback without deleting existing data.

## Phase 3: US1 — Faculty-aware degree selection

P1. Search faculty, filter degrees, derive faculty from direct degree selection, and preserve only compatible choices.

- [X] T014 [P] [US1] Implement pure transitions in `frontend/lib/faculty-selection.ts`: direct degree selection uses English alphabetical faculty-name order with stable-ID tie-break; faculty changes keep compatible degrees and clear incompatible ones; apply documented clear/missing-membership behavior.
- [X] T015 [P] [US1] Build `frontend/components/FacultyCombobox.tsx` using `frontend/components/ui/typable-dropdown.tsx`; support typing, case-insensitive search, clear, keyboard navigation, accessible name and no-match state.
- [ ] T016 [US1] Update `frontend/components/DegreeCombobox.tsx` and `frontend/components/recommend/RecommendDegreeField.tsx` to accept faculty-filtered degree options while retaining existing display names, selection callbacks and accessibility.
- [ ] T017 [US1] Integrate faculty state and helpers in `frontend/app/page.tsx`; change faculty/degree atomically, clear stale results when degree is invalidated, and preserve existing recommendation loading/error/abort behavior.
- [ ] T018 [US1] Integrate faculty state and helpers in `frontend/app/mappings/page.tsx`; keep university selected on faculty changes, encode faculty alongside degree/uni, and clear or reload mapping results only when the effective degree changes.
- [ ] T019 [US1] Record US1 acceptance in `plan/exchange-enhancements/validation.md`: on both pages verify searchable faculty, single/multi-faculty degree auto-selection, compatible retention, incompatible clearing, clear controls and existing result counts.

## Phase 4: US2 — Geographic filtering

P1. Apply dependent multi-select geography immediately; validate on Recommend independently of the directory.

- [ ] T020 [P] [US2] Implement `frontend/lib/geography.ts` with continent/country/city option derivation from the full catalog, country-qualified city keys, OR within categories, AND across categories, empty-as-unrestricted semantics and deterministic sorting.
- [ ] T021 [P] [US2] Build accessible `frontend/components/GeographicFilters.tsx` with three multi-select controls, visible selected values and clear actions; expose controlled selection callbacks and keyboard/focus behavior without an Apply button.
- [ ] T022 [US2] Add parent-change reconciliation in `frontend/lib/geography.ts`: restrict countries by selected continents, cities by both parents, remove only invalid dependent selections and preserve still-valid choices in one state transition.
- [ ] T023 [US2] Integrate `frontend/components/GeographicFilters.tsx` in `frontend/app/page.tsx`; match recommendation university names to catalog metadata, filter immediately without refetching or reordering rankings, and keep counts unmodified.
- [ ] T024 [US2] Add filtered-empty feedback and reset controls in `frontend/app/page.tsx` and scoped layout styles in `frontend/components/recommend/recommend.module.css`; distinguish no selected degree, service failure and no geography matches.
- [ ] T025 [US2] Record US2 acceptance in `plan/exchange-enhancements/validation.md`: multiple continents/countries/cities, duplicate city names, invalid-child pruning, null geography, AND/OR behavior, immediate updates and restoration of original recommendation order on reset.

## Phase 5: US3 — Universities directory

P1. Browse every partner by default and combine faculty and geographic restrictions.

- [ ] T026 [US3] Create `data/exchange-enhancements/faculty-availability.json` with verified faculty–partner IDs and source provenance; explicitly expand documented university-wide agreements, record unverified coverage and never infer availability from mapping existence.
- [ ] T027 [US3] Extend `backend/scripts/seed_exchange_enhancements.py` to import availability idempotently, reject unknown IDs and duplicates, preserve valid existing relationships and document how university-wide links are maintained when a faculty is added.
- [ ] T028 [P] [US3] Implement `frontend/lib/university-filters.ts` to combine optional explicit faculty membership with the shared geographic predicate; with no filters return every catalog university, including partners with no mappings or recorded availability.
- [ ] T029 [P] [US3] Create the initial `frontend/components/universities/UniversityDirectoryCard.tsx` with university name, location and a View Mappings anchor to `/mappings?uni=...`; US4 adds complete media presentation and US5 adds state-preserving navigation.
- [ ] T030 [US3] Create `frontend/app/universities/page.tsx` to fetch the complete catalog with cancellation, render loading/error/retry/empty states, and compose faculty/geographic controls with the filtered card collection; clearing faculty restores unlinked partners.
- [ ] T031 [US3] Create `frontend/components/universities/universities.module.css` with three columns at ordinary desktop widths, four at wide widths, two on tablet and one on mobile; retain shared shell and avoid fixed card heights that truncate names.
- [ ] T032 [US3] Add Universities to `frontend/components/layout/AppSidebar.tsx` with route-aware active state and keyboard-operable navigation; preserve Recommend and Mappings links.
- [ ] T033 [US3] Record US3 acceptance in `plan/exchange-enhancements/validation.md`: initial total equals all database partners, selected faculty includes only explicit links, combined geography works, clearing restores defaults, and desktop rows contain three/four cards.

## Phase 6: US4 — University metadata and finished cards

P1. Populate official websites and reusable photos; render resilient cards matching the supplied wireframe.

- [ ] T034 [P] [US4] Create `data/exchange-enhancements/university-assets.json` by researching each partner: record official website, image source, author, license/permission, required attribution and acquisition status; leave unsupported assets null and report coverage rather than claiming arbitrary images are reusable.
- [ ] T035 [P] [US4] Add `frontend/public/images/university-fallback.svg` as a locally created neutral university illustration, with no third-party licensing dependency.
- [ ] T036 [US4] Create `backend/scripts/upload_university_assets.py` with dry-run/resume modes, HTTPS URL validation, image MIME/size checks, deterministic object names and checksum-based reuse; download only manifest-approved photographs and upload using server-only credentials.
- [ ] T037 [US4] Document/create the photograph bucket and read/write policy setup in `supabase/README.md`; allow intended public image reads, restrict writes to the administrative uploader, document allowed types/size limits and verify current Supabase docs before execution.
- [ ] T038 [US4] Use `backend/scripts/upload_university_assets.py` to populate partner_universities.image/website only after successful upload/verification; retain existing valid metadata on failure, write per-university outcomes and runtime attribution data to `data/exchange-enhancements/university-assets.json`.
- [ ] T039 [US4] Complete `frontend/components/universities/UniversityDirectoryCard.tsx` with top photograph, full name, city/country tags, safe official website link or explicit unavailable text, required image attribution and View Mappings action; handle missing and failed images without fallback loops.
- [ ] T040 [US4] Style card image ratio, border/radius, text hierarchy, footer action and wrapping in `frontend/components/universities/universities.module.css` against `plan/exchange-enhancements/reference/universities.png`; reserve image dimensions and lazy-load offscreen images.
- [ ] T041 [US4] Record US4 acceptance and asset coverage in `plan/exchange-enhancements/validation.md`: valid/missing/broken images, valid/missing websites, required attribution, null city, long university names, responsive rows and keyboard-operable links.

## Phase 7: US5 — Preserve selections and open mappings

P1. Replace only the chosen university and automatically load with retained valid Mappings selections.

- [ ] T042 [P] [US5] Create `frontend/components/mappings/MappingsSelectionProvider.tsx` to remember Mappings faculty, degree and university across route unmounts; mount through `frontend/app/layout.tsx`, isolate this state from directory/Recommend selections and handle catalog reconciliation.
- [ ] T043 [P] [US5] Implement `frontend/lib/mappings-navigation.ts` with a pure URL merge helper: explicit degree/faculty query values override remembered fields; a directory click changes only uni, encodes names safely and preserves other supported parameters; distinguish missing from explicitly cleared values.
- [ ] T044 [US5] Refactor URL hydration/update logic in `frontend/app/mappings/page.tsx` to merge the persistent selection state and URL once the catalog is ready; preserve an explicitly selected compatible faculty, derive one only when needed, and report stale/unknown IDs without silently choosing another degree.
- [ ] T045 [US5] Wire `frontend/components/universities/UniversityDirectoryCard.tsx` to the navigation helper and remembered Mappings selections; generate a real href so copied links/new tabs retain known choices and do not pass the directory faculty as a replacement.
- [ ] T046 [US5] Finalize automatic fetching in `frontend/app/mappings/page.tsx` after merged selections settle; reuse the existing abortable request, suppress stale responses, avoid hydration loops and extra Search clicks, and apply the documented no-degree prompt pending resolution of FR-20.
- [ ] T047 [US5] Record US5 acceptance in `plan/exchange-enhancements/validation.md`: set faculty/degree in Mappings, visit directory, choose a different university and verify retained choices/automatic results; also exercise fresh-session no-degree handling, copied URLs, back/forward, invalid links and rapid card navigation.

## Phase 8: Polish and cross-cutting validation

Close data, accessibility and regression gaps before shipping.

- [ ] T048 Run relevant existing backend pytest suites and frontend lint/typecheck/build plus existing flow/shell checks; record commands, outcomes and any obsolete assertion updates in `plan/exchange-enhancements/validation.md`, preserving count/ranking/deep-link coverage.
- [ ] T049 Execute all story acceptance criteria and capture desktop/mobile evidence under `plan/exchange-enhancements/reference/`; record keyboard/focus, empty/error/retry and long-content outcomes in `plan/exchange-enhancements/validation.md`, including unresolved FR-20 status.
- [ ] T050 Document migration order, seed/upload commands, data provenance, incomplete availability/assets and recovery steps in `supabase/README.md` and `README.md`; link feature artifacts and ensure no administrative credentials enter frontend bundles.
- [ ] T051 Complete requirement traceability and release readiness in `plan/exchange-enhancements/completion.md`; map DB-01–03 and FR-01–20 to tasks/evidence, rerun preservation comparisons and leave unmet data/product decisions explicitly open.

## Independent acceptance checkpoints

| Story | Independently observable completion |
| --- | --- |
| US1 | Both existing pages implement the full faculty/degree transition matrix and still retrieve correct results. |
| US2 | Recommend immediately filters existing ranked results with dependent multi-select AND/OR semantics; directory consumes the same helper in US3. |
| US3 | Directory lists all partners by default and correctly combines faculty/geography; a minimal card exists without waiting for photographs. |
| US4 | Directory cards match the supplied content hierarchy and remain usable for null/broken metadata; sourced assets carry required attribution. |
| US5 | A directory click replaces only university, preserves valid Mappings state and automatically fetches when a degree exists; the no-degree acceptance decision must be settled to close FR-20. |

## Dependencies and delivery graph

```text
Setup → Foundation → US1 ──────────────────┐
                   → US2 → US3 → US4      ├→ US5 → final validation
                              └───────────┘
```

US1 and US2 can begin after Foundation, but serialize their edits to `frontend/app/page.tsx`. US3 needs the shared geography behavior from US2. US4 can research assets early but integrates after the US3 card. US5 needs the US1 selection semantics and US3 card; it may proceed alongside US4 if card-file edits are coordinated. Foundation changes shared types before any UI integration. Database migration/backfill precedes enabling the new PostgreSQL query shape.

## Parallel execution examples

- Foundation: after model/contract completion, adapt JSON responses and frontend types independently; do not run migrations concurrently with seeding.
- US1: build `FacultyCombobox.tsx` while implementing `faculty-selection.ts`; integrate pages after both are ready.
- US2: build `GeographicFilters.tsx` while implementing `geography.ts`; integrate only once pruning semantics are complete.
- US3: implement `university-filters.ts` and the initial directory card separately after availability import; then assemble the page.
- US4: research the asset manifest and create the fallback SVG independently; uploader execution waits for reviewed rights and bucket setup.
- US5: implement the state provider and URL merge helper independently; then integrate hydration and navigation sequentially.

## Implementation strategy

1. Deliver Setup/Foundation plus US1 as the smallest useful MVP: faculty-aware choices on existing pages.
2. Deliver US2 on Recommend, then US3 with minimal cards, so filtering and availability can be verified before asset acquisition finishes.
3. Finish US4 media/cards and US5 state-preserving navigation. The directory is not feature-complete until its finished cards and navigation satisfy the source requirements.
4. Run final checks, resolve the no-degree FR-20 decision and disclose incomplete source-data coverage. Do not mark tasks complete based only on writing code; each phase's acceptance evidence is required.
