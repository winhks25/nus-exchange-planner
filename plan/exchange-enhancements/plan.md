# Implementation plan — Exchange planner enhancements

## Workflow and evidence

The speckit setup command was attempted; `.specify/scripts/python/setup_tasks.py` is absent. This checkout has no `.specify` template, constitution or extension registry. Use its established `plan/<feature>/` convention and the skill's phase/checklist structure. Supporting spec and plan are derived from the supplied requirements and inspected code, not a claim that a prior design workflow ran. No application code, database changes or uploads are executed in this planning task.

## Existing architecture

Next.js App Router + React + TypeScript, Tailwind v4 and Base UI. Routes are `frontend/app/page.tsx` and `frontend/app/mappings/page.tsx`; navigation is `frontend/components/layout/AppSidebar.tsx`. Reuse `frontend/components/ui/typable-dropdown.tsx`. Backend is FastAPI/Pydantic with a repository protocol, PostgreSQL and JSON adapters. `GET /api/v1/catalog` currently supplies degrees and university name/country; recommendation and mappings endpoints use existing degree/university names. PostgreSQL already stores city and continent. Mappings already auto-fetches when both degree and university exist, but URL hydration currently resets absent fields.

## Delivery design

Add faculty relationships and nullable metadata without changing mapping counts or ranking SQL. Extend catalog payload additively with faculties, degree faculty IDs and university ID/location/availability/image/website metadata. Keep existing name-based mapping query compatibility. Default missing new fields in legacy JSON mode. Use the catalog for immediate client-side geography and directory filtering; filter ranked recommendations without recalculating counts or order. Preserve the complete catalog rather than joining only universities with availability.

Implement pure faculty-selection and geographic-selection helpers, reusable accessible controls, a dedicated directory card and responsive collection, and a root-mounted Mappings state provider. Keep the existing tiered recommendation cards separate from the directory card. Add a `/universities` route and navigation entry. Implement card navigation last so the completed experience combines persisted selections with current query parameters and the existing abortable fetch effect.

## Database and assets

Audit deployed schema and source data before choosing a migration. Generate migration names via `supabase migration new exchange_enhancements`; tasks reference `supabase/migrations/<generated>_exchange_enhancements.sql` as the CLI-resolved path, not a literal filename. Use stable faculty IDs, unique degree/faculty and faculty/university pairs, foreign keys, reverse lookup indexes, RLS and the existing backend reader role. Store asset provenance in a reviewed manifest; use server-only credentials for a repeatable uploader. Public image reads are appropriate for university photographs; writes remain administrative. Recheck current Supabase documentation at implementation time. Do not recreate removed catalog metadata tables.

## Sequencing and validation

See tasks.md for executable steps, dependency edges and independent acceptance criteria. US2 ships on Recommend before directory integration. US3 provides a minimal functional card while US4 adds the full media presentation. US5 completes the cross-route mapping action. Audit data preservation, run existing backend checks and frontend lint/typecheck/build/appropriate Playwright flows, and manually exercise all supplied acceptance criteria. Read `frontend/AGENTS.md` and installed Next.js documentation before frontend implementation.
