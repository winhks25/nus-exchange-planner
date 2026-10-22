# Final validation (T040)

Date: 2026-10-22 (Asia/Singapore). Scope: Phase 7 of the Supabase catalog migration.

## Checks

| Check | Result |
| --- | --- |
| `UV_CACHE_DIR=/private/tmp/nus-uv-cache uv run --directory backend pytest -q` | 60 passed, 1 dependency deprecation warning |
| `UV_CACHE_DIR=/private/tmp/nus-uv-cache uv run --directory backend ruff check .` | Passed |
| `npm run lint --prefix frontend` | Passed |
| `npm run typecheck --prefix frontend` | Passed after the build completed |
| `npm run build --prefix frontend` | Passed; the two application pages were statically generated |
| `TEST_CATALOG_BACKEND=json npm run test:e2e --prefix frontend` | 65 passed |
| `TEST_CATALOG_BACKEND=postgres npm run test:e2e --prefix frontend` | 73 passed against a disposable local PostgreSQL database |
| `git diff --check` | Passed |

The first backend test attempt could not bind a loopback port under the filesystem sandbox. The rerun with local port access passed. An initial typecheck ran at the same time as the Next build and read generated type files while they were being replaced; the ordered rerun passed. These were execution-environment issues, not product failures.

## Requirements and evidence

| Requirement | Evidence |
| --- | --- |
| Traceable, repeatable import and unresolved row accounting | `import-results.md`, `repair-report.md`, `data-deltas.md`; backend import regression tests |
| JSON/PostgreSQL API parity and explicit repaired differences | `api-validation.md`; backend repository regression and contract tests |
| Database failure isolation and manual JSON rollback | `deployment-results.md`; backend failure tests and both browser suites |
| Least-privilege runtime role and migration history | `schema-audit.md`; backend role regression tests |
| Production deployment and smoke checks | `deployment-results.md`; catalog, recommendations, mappings, and frontend checks recorded there |
| Performance characterization | `performance.md`; representative plans and local contention measurements |
| Operator guidance and API contract | `README.md`, `supabase/README.md`, `backend/.env.example`, `quickstart.md`, and `plan/contracts/openapi.yaml` |

The tracked-file scan found only environment examples, placeholders, and explicit local-only test credentials. No production password, secret key, or real database URL was found. The generated `frontend/next-env.d.ts` change from Playwright was restored after the checks.

## Remaining limitations

- The hobby-plan deployment cannot select a function region near the Sydney database; production cold-start and load behavior were not stress-tested.
- Three Toronto source rows remain quarantined, and unresolved titles stay unknown. The frozen JSON rollback snapshot predates the reviewed repairs.
- The `.specify/` prerequisite script and extension-hook registry are absent in this repository, so those skill steps were not available. The existing `plan/supabase-migration/` task and evidence files were used directly.

All Phase 7 tasks have implementation or verification evidence and are marked complete. The broader feature's remaining data and deployment limitations are recorded above and in the linked evidence files.
