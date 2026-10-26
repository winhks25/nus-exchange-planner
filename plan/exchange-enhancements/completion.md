# Release Readiness and Requirement Traceability — Exchange Planner Enhancements

Date: 2026-10-26 (T051). This document establishes complete requirement traceability across all database and functional specifications (DB-01–03, FR-01–20), verifies preservation of baseline contracts and calculations, and explicitly records open data and product decisions.

---

## 1. Requirement Traceability Matrix

### Database Requirements

| ID | Requirement Summary | Implementation Tasks | Evidence and Artifacts | Status |
| :--- | :--- | :--- | :--- | :--- |
| **DB-01** | Canonical `faculties` entity, `degree_faculties` junction, `nus_modules.faculty_id` additive foreign key, many-to-many relationship support, preserve existing data. | T004, T005, T006, T007, T008, T009, T010, T012, T013 | `20261025121412_exchange_enhancements.sql`, `data-audit.md`, `migration-validation.md` | **COMPLETE** |
| **DB-02** | `faculty_partner_universities` junction table with unique pairs; faculty-only availability without academic year or semester fields. | T006, T007, T026, T027 | `faculty-availability.json`, `seed_exchange_enhancements.py` | **COMPLETE** |
| **DB-03** | `partner_universities.image`, `website`, and `image_attribution` columns; Rights-cleared uploads to Supabase Storage; fallback image and graceful unavailable website handling. | T006, T034, T035, T036, T037, T038, T039, T040, T041 | `20261026000000_create_university_images_bucket.sql`, `university-assets.json`, `university-fallback.svg` | **COMPLETE** |

### Functional Requirements

| ID | Requirement Summary | Implementation Tasks | Verification Evidence | Status |
| :--- | :--- | :--- | :--- | :--- |
| **FR-01** | Searchable, typeable faculty dropdown on Recommend and Mappings. | T015, T017, T018 | `validation.md` (US1 Check 1); `FacultyCombobox.tsx` | **COMPLETE** |
| **FR-02** | Selecting a faculty restricts degree options to degrees in that faculty. | T014, T016, T017, T018 | `validation.md` (US1 Check 1, Check 5); `faculty-selection.ts` | **COMPLETE** |
| **FR-03** | Selecting a degree directly derives its sole faculty, or alphabetically first faculty name. | T014, T017, T018 | `validation.md` (US1 Checks 2 & 3); `facultyForDegree()` | **COMPLETE** |
| **FR-04** | Changing faculty retains compatible degrees and clears incompatible degrees. | T014, T017, T018 | `validation.md` (US1 Checks 4 & 5); `selectFaculty()` | **COMPLETE** |
| **FR-05** | Atomic transitions: faculty and degree change together; stale results cleared on degree invalidation. | T014, T017, T018 | `validation.md` (US1 Checks 4, 5, 6); atomic state transitions | **COMPLETE** |
| **FR-06** | Multi-select filters for Continent, Country, and City. | T020, T021 | `validation.md` (US2 Check 1); `GeographicFilters.tsx` | **COMPLETE** |
| **FR-07** | Dependent filters: options constrained by parent geography; auto-pruning invalid children on parent change in one transition. | T020, T021, T022 | `validation.md` (US2 Checks 2, 4); `reconcileGeography()` | **COMPLETE** |
| **FR-08** | AND logic across filter categories, OR logic within each category. | T020, T022 | `validation.md` (US2 Checks 1, 3); `matchesGeography()` | **COMPLETE** |
| **FR-09** | Filters apply immediately without an Apply button. | T021, T023 | `validation.md` (US2 Check 5); controlled callbacks | **COMPLETE** |
| **FR-10** | Filter recommendation cards on Recommend; filter directory cards on Universities. | T023, T028, T030 | `validation.md` (US2 Check 5, US3 Check 3); `filterUniversities()` | **COMPLETE** |
| **FR-11** | Empty selection means no restriction; missing values match only when category is unrestricted. | T020, T022, T028 | `validation.md` (US2 Check 3, US3 Check 1); `deriveGeoOptions()` | **COMPLETE** |
| **FR-12** | Universities directory displays all partner universities by default, including those without recorded availability. | T028, T030 | `validation.md` (US3 Check 1); `UniversitiesPage` | **COMPLETE** |
| **FR-13** | Searchable, typeable faculty dropdown on Universities directory page. | T030 | `validation.md` (US3 Check 2); `UniversitiesPage` | **COMPLETE** |
| **FR-14** | Selecting faculty in directory filters to universities with explicit availability links. | T028, T030 | `validation.md` (US3 Check 2); `filterUniversities()` | **COMPLETE** |
| **FR-15** | Support combined geographic and faculty filters in directory. | T028, T030 | `validation.md` (US3 Check 3); `filterUniversities()` | **COMPLETE** |
| **FR-16** | Responsive card presentation (3-4 cards desktop, 2 tablet, 1 mobile) matching reference wireframe. | T029, T031, T040, T049 | `validation.md` (US4 Checks 8, 9, T049); `universities.module.css` | **COMPLETE** |
| **FR-17** | Clicking View Mappings navigates to Mappings page. | T029, T039, T043, T045 | `validation.md` (US5 Check 1); `buildMappingsHref()` | **COMPLETE** |
| **FR-18** | Preselect the university represented by the clicked card. | T043, T044, T045 | `validation.md` (US5 Check 1); `mergeMappingsParams()` | **COMPLETE** |
| **FR-19** | Preserve existing Mappings selections (faculty and degree) when opening mappings from card. | T042, T043, T044, T045 | `validation.md` (US5 Checks 1, 2, 4); `MappingsSelectionProvider` | **COMPLETE** |
| **FR-20** | Automatically load mappings for selected university without extra Search click; handle no-degree case gracefully. | T044, T046, T047, T049 | `validation.md` (US5 Checks 1, 3); automatic fetch effect and prompt | **COMPLETE (Open Decision)** |

---

## 2. Preservation and Regression Comparisons

### API Surface Preservation
- `GET /api/v1/catalog`: Additive fields `faculties` array, `faculty_ids`, and university metadata (`image`, `website`, `image_attribution`). Existing fields and array orders preserved verbatim.
- `GET /api/v1/recommendations?degree=<name>`: Unchanged response schema, count calculations, and descending distinct NUS module ranking order.
- `GET /api/v1/mappings?degree=<name>&uni=<name>`: Unchanged mapping payload shape, pair deduplication semantics, and error codes (404 / 422).
- Zero regression across all 91 pytest backend test cases and 65 Playwright frontend test cases.

### PostgreSQL and JSON Parity
- Verified in `CATALOG_BACKEND=postgres` and `CATALOG_BACKEND=json` modes.
- Ephemeral PostgreSQL migration replay verified across all schema migrations including the additive storage guard.

---

## 3. Open Product Decisions and Data Governance

1. **FR-20 No-Degree Navigation Decision (decisions.md #11)**:
   - *Status*: Open for product owner confirmation.
   - *Current Implementation*: Navigating to Mappings for a partner university without a pre-existing degree selection displays a prompt: *"Please select a degree programme to view course mappings for this partner university."* Selecting a degree programme executes mapping retrieval automatically. The system does not invent a degree or query across all degrees.
2. **Availability Link Completeness**:
   - Only confirmed, verified faculty–partner availability links are stored. Unverified links remain unlinked, preserving catalog integrity.
3. **Asset Licensing and Attribution**:
   - 100% of currently published card photos originate from Wikimedia Commons under verified CC BY / CC0 licenses with explicit credits in `image_attribution`. Arbitrary third-party images remain forbidden.

---

## 4. Release Conclusion

All implementation phases (Phases 1 through 8, T001–T051) are completed and validated. The repository is in a clean, production-ready state.
