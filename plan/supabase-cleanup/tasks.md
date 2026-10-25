# Supabase cleanup tasks

Adapted from speckit-tasks: this repository has no `.specify/` setup script,
spec, template, constitution, or extension hooks. Scope comes from the user's
request and the supplied handoff, with its detailed task 7 taking precedence
over the stale introductory specialization reference.

## Phase 1: Setup
- [x] T001 Inspect live schema and record affected runtime paths in plan/supabase-cleanup/results.md.

## Phase 2: Foundation
- [x] T002 Capture the pre-change eight-table snapshot in plan/supabase-cleanup/before.json.

## Phase 3: US1 — Preserve app behavior after tasks 1–5 (P1)
Goal: catalog, recommendations and mappings work on the cleaned schema.
Independent test: actual PostgreSQL column drops followed by API requests as catalog_reader.
- [x] T003 [US1] Add cleaned-schema regression tests in backend/tests/test_database_cleanup.py.
- [x] T004 [US1] Support removed metadata and renamed units in backend/app/repositories/postgres_catalog.py.

## Phase 4: US2 — Official NUS module data (P1)
Goal: existing codes use official 2026–2027 titles and credits.
Independent test: validate source payloads and canonical units including non-four-credit modules.
- [x] T005 [US2] Validate and generate transactional cleanup SQL in backend/scripts/cleanup_catalog.py.
- [x] T006 [US2] Save official module evidence in plan/supabase-cleanup/nusmods.json and apply task 6.

## Phase 5: US3 — Partner geography (P2)
Goal: every existing university has verified main-campus geography.
Independent test: all five locations match cited official campus sources and source_order is absent.
- [x] T007 [P] [US3] Record official location evidence in plan/supabase-cleanup/locations.json.
- [x] T008 [US3] Apply task 7 through backend/scripts/cleanup_catalog.py and verify locations.

## Phase 6: Validation
- [x] T009 Run backend and frontend regression gates and record results in plan/supabase-cleanup/results.md.
- [x] T010 Review changes and commit source, tests and plan/supabase-cleanup/ evidence.

## Dependencies and delivery
T001 → T002 → US1 → US2 → US3 → validation. US3 source research (T007)
can run independently of US1/US2. US1 is the MVP: repair app reads before data
maintenance. Tests and implementation within each story are sequential; no
other independent same-story parallel tasks. All ten tasks have IDs and paths;
story phases carry US labels (US1: 2, US2: 2, US3: 2; shared: 4).
