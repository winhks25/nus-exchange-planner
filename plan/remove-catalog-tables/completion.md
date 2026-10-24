# Feature Completion: Catalog Table Removal (`remove-catalog-tables`)

Date: 2026-10-24.
Tested Commit: `115284b`.
Target Project: Supabase `wydziozsjibkvpgphpia` (region `ap-southeast-2`).

---

## 1. Executive Summary

The catalog table removal plan has been successfully implemented, verified, and closed.
The application's data architecture has been streamlined from a 13-table schema
with an operational importer and archive tables down to **eight normalized core application
tables**. The operational importer (`scripts.import_catalog`) and all metadata tables
have been permanently deleted, while preserving core entity data integrity, foreign
keys, row level security, API response parity, and explicit JSON fallback.

---

## 2. Objects Removed

Applied Migration: `supabase/migrations/20261024034234_remove_catalog_metadata.sql`
(recorded remotely via MCP as `20261024054553`).

### Dropped Tables (5)
1. `public.catalog_import_batches`
2. `public.catalog_source_snapshots`
3. `public.catalog_source_rows`
4. `public.catalog_issues`
5. `public.catalog_repairs`

### Dropped Column, Constraints, and Functions
- Column `public.module_mappings.source_row_id` dropped.
- Unique constraint `module_mappings_source_row_id_key` dropped.
- Foreign key constraint `module_mappings_source_row_id_fkey` dropped.
- Trigger guard function `public.reject_catalog_archive_mutation()` dropped.

All attached indexes, triggers, and table-level RLS policies were cleanly removed
by PostgreSQL ownership semantics without wildcard or `CASCADE` operations.

---

## 3. Preserved Core Tables and Data Evidence

The application now operates directly on the **eight core application tables**:

| Table | Retained Rows | Purpose / Content |
| --- | ---: | --- |
| `public.degrees` | 6 | Degree programs with non-null `full_title` |
| `public.degree_modules` | 226 | Degree-to-module associations and requirements |
| `public.nus_modules` | 152 | NUS courses (codes, optional titles) |
| `public.partner_universities` | 5 | Partner institutions, countries, cities, regions |
| `public.pu_modules` | 142 | Partner courses, optional titles and units |
| `public.module_mappings` | 151 | Course equivalencies, including intentional duplicate rows |
| `public.specializations` | 19 | Tracks and focus areas |
| `public.specialization_modules` | 30 | Track-to-module requirements |

### Data Fingerprint Integrity
- **Natural-key comparison against reviewed preview:** 8/8 tables matched (0 missing, 0 extra rows).
- **Core sequence continuity:** Sequences `degrees_id_seq`, `partner_universities_id_seq`, `pu_modules_id_seq`, `nus_modules_id_seq`, `module_mappings_id_seq` remain intact and contiguous.
- **Multiplicity preserved:** Repeated mapping pairs and overlapping degree memberships remain active and unaffected.
- **Reviewed repairs preserved:** Verified units and corrected course titles remain active in core entities; missing titles remain null without fabricated values.

---

## 4. Importer Retirement & Local Tooling

- **Retired Code:** `backend/scripts/import_catalog.py` has been deleted.
- **Fixture Generation:** `backend/scripts/generate_catalog_fixtures.py` is neutralized into a historical tombstone.
- **Disposable Local Seeder:** `backend/scripts/catalog_seed.py` performs atomic, single-transaction insertion of the 8 core tables from the offline preview. Enforces target validation and strictly refuses remote database URLs.
- **Read-Only Verification:** `backend/scripts/verify_catalog.py` reconciled directly against `scripts.catalog_preview.build_preview()` on core entities without batch/provenance joins (97/97 checks passed).
- **Automated Regression Gate:** Unified [scripts/check-regressions.sh](../../scripts/check-regressions.sh) provides a single fail-fast entry point for linting, typechecking, building, backend pytest, and browser flows.

---

## 5. Explicit Dual-Mode Architecture & JSON Fallback

The backend retains its explicit two-mode design:

```text
CATALOG_BACKEND=postgres  ────────►  Reads 8 core tables via catalog_reader role
                                     (Requires core readiness: 1 degree, 1 uni, non-null full_title)

CATALOG_BACKEND=json      ────────►  Reads static snapshot in data/ without database
```

### Fallback Instructions
In the event of a database incident:
1. In deployment settings, set `CATALOG_BACKEND=json` and clear `DATABASE_URL`.
2. Redeploy the service. The backend immediately serves the frozen static snapshot.
3. Database outages in PostgreSQL mode return a sanitized HTTP 503 and **never** fall back to JSON automatically.

### Repaired-vs-Frozen Differences
The frozen JSON snapshot and the repaired PostgreSQL database intentionally differ for four Toronto degree pairs (+1 mapping in PostgreSQL due to verified repairs):
- Artificial Intelligence / Toronto: 9 (JSON) vs 10 (PG)
- Business Analytics / Toronto: 18 (JSON) vs 19 (PG)
- Computer Science / Toronto: 6 (JSON) vs 7 (PG)
- Information Security / Toronto: 7 (JSON) vs 8 (PG)

---

## 6. Comprehensive Regression Results

All verification suites passed cleanly before sign-off:

| Suite / Check | Cases Tested | Execution Time | Result |
| --- | ---: | ---: | --- |
| **Backend Pytest** | 83 | 28.75s | ✅ 83 passed, 0 failed, 0 skipped |
| **Schema Removal & Absence** | 21 | 12.84s | ✅ 21 passed, 0 failed |
| **Playwright E2E (JSON mode)** | 65 | 39.8s | ✅ 65 passed, 0 failed |
| **Playwright E2E (PG mode)** | 73 | 47.8s | ✅ 73 passed, 0 failed |
| **API Baseline Comparator** | 41 | ~4s | ✅ 41 requests, 0 diffs, 0 failures |
| **Catalog Verifier** | 97 | ~6s | ✅ 97/97 checks passed |
| **Backend Ruff Linter** | 3 dirs | <1s | ✅ All checks passed |
| **Frontend ESLint** | Entire app | ~2s | ✅ 0 errors, 0 warnings |
| **Frontend TypeScript** | `tsc --noEmit` | ~2s | ✅ 0 errors |
| **Next.js Production Build** | Static pages | ~4s | ✅ Compiled successfully |
| **Latency Bounds** | Repeated reads | ~4s | ✅ <2ms warm average |

---

## 7. Real Limitations and Operational Boundary

To maintain complete documentation integrity, the following real operational limitations are explicitly documented:

1. **Application Deployment Scope:**
   Per the 2026-10-24 specification revision, **no application deployment was performed to Vercel**. The application code and cleanup were verified on localhost pointed at disposable databases and the live Supabase schema. Deploying the compatible runtime to production Vercel (`nus-exchange-planner-api`) or toggling `CATALOG_BACKEND=json` is an operator-run step.
2. **Partial Recovery Capture (T035):**
   Full `pg_dump` export was skipped per operator decision to apply changes via Supabase MCP. A data-only backup (`mapping-source-row-ids.csv` mapping all 151 mappings, and `sequence-state.csv`) was captured in `PRIVATE_BACKUP_DIR` outside git (`/Users/winhtutkhaungsoe/Backups/nus-exchange-planner/catalog-removal-20261023`).
3. **Migration Version Identifier:**
   The removal migration is checked into git as `supabase/migrations/20261024034234_remove_catalog_metadata.sql`, while the remote Supabase MCP execution registered version `20261024054553`.
4. **Old Runtime Incompatibility:**
   Legacy deployments running code prior to the core-readiness refactor (commit `af4d30e`) query `catalog_import_batches` and will return 503 until redeployed with the compatible runtime.

---

## 8. Runbooks & References

- **Maintenance Guide:** [Direct Supabase Maintenance Guide](quickstart.md)
- **Recovery Runbook:** [Recovery Procedure](recovery.md)
- **Detailed Regression Results:** [Regression Results](regression-results.md)
- **Acceptance Matrix:** [Acceptance Matrix](acceptance-matrix.md)
- **Cleanup Inventory:** [Cleanup Results](cleanup-results.md)
