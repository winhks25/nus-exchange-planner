# Direct Supabase Catalog Maintenance Guide

This guide is the operational runbook for maintaining the NUS Exchange Planner
catalog in Supabase PostgreSQL following the retirement of the catalog metadata
tables (`catalog_import_batches`, `catalog_source_snapshots`, `catalog_source_rows`,
`catalog_issues`, `catalog_repairs`).

Catalog data now lives cleanly and directly in the **eight core application tables**:
- `degrees`
- `degree_modules`
- `nus_modules`
- `partner_universities`
- `pu_modules`
- `module_mappings`
- `specializations`
- `specialization_modules`

---

## 1. Operating Modes & Architecture

The application supports two explicit data backends:

| Backend | Configuration | Description |
| --- | --- | --- |
| **PostgreSQL** (`postgres`) | `CATALOG_BACKEND=postgres`<br>`DATABASE_URL=...` | Production mode. Serves catalog directly from Supabase PostgreSQL via the read-only `catalog_reader` role. Requires core readiness. |
| **JSON** (`json`) | `CATALOG_BACKEND=json`<br>`DATABASE_URL=` | Local development and manual rollback mode. Serves the static, frozen snapshot in `data/`. |

> [!IMPORTANT]
> Mode switching is strictly explicit via `CATALOG_BACKEND`. A database outage or
> core readiness failure in `postgres` mode returns a sanitized HTTP 503 and **never**
> falls back to JSON automatically.

---

## 2. Core Readiness Limitations

When running in `postgres` mode, the backend (`app.repositories.postgres_catalog`)
evaluates database readiness on startup and before serving requests. To be considered
ready, the database must satisfy all three invariants:

1. **At least one degree** exists in `degrees`.
2. **At least one partner university** exists in `partner_universities`.
3. **No null full titles**: Every row in `degrees` must have a non-null `full_title`.

If any check fails, the repository raises `CatalogReadinessError`, logging the exact
reason server-side while returning an HTTP 503 to API clients.

---

## 3. Schema Invariants & Maintenance Rules

When updating catalog data via direct SQL, observe the following invariants:

### A. Parent-Before-Child Dependency Order
Foreign keys use PostgreSQL's default `NO ACTION` constraint to prevent accidental
cascading deletes. Inserts and deletes must follow strict dependency order:

```text
degrees ────────────┬──► degree_modules
                    └──► specializations ──► specialization_modules

partner_universities ──► pu_modules ─────────┬──► module_mappings
                                             │
nus_modules ─────────────────────────────────┴──► (degree_modules, specialization_modules)
```

1. Insert parent entities (`degrees`, `partner_universities`, `nus_modules`).
2. Insert secondary entities (`specializations`, `pu_modules`).
3. Insert join / membership records (`degree_modules`, `specialization_modules`, `module_mappings`).

### B. Full Degree Titles
The `full_title` column in `degrees` is mandatory for core readiness (e.g. `'Bachelor of Computing in Computer Science'`). Never insert or leave a `NULL` full title.

### C. Nullable Titles and Positive Units
- **Module Titles**: `nus_modules.title` and `pu_modules.title` are nullable. If the source institution does not provide an official module title, store `NULL` — never invent or guess titles.
- **Units**: `pu_modules.units` and `module_mappings.verified_units` must be positive integers (`> 0`) when provided, or `NULL` if unknown. The database enforces `check (units > 0)` and `check (verified_units > 0)`.
- **NUS Units**: NUS modules default to 4 units in application logic when not specified.

### D. Deterministic Source Ordering
`degree_modules.source_order`, `partner_universities.source_order`, and
`module_mappings.source_order` preserve deterministic presentation ordering:
- Use consistent, sequential integers (1-based or 0-based) for rows belonging to a parent.
- Do not leave ordering arbitrary when inserting batches of mappings.

### E. Multiplicity (Duplicate Mappings)
Multiple rows with the same `(pu_module_id, nus_module_id)` pair in `module_mappings`
are valid and supported to preserve source-row equivalency semantics (e.g., distinct
curriculum approval tracks or differing faculties).

### F. Mandatory Transaction Wrapping
Always wrap multi-table modifications in a single SQL transaction (`BEGIN; ... COMMIT;`).
If any constraint fails, the entire transaction rolls back cleanly.

---

## 4. SQL Maintenance Examples

Run maintenance scripts through the Supabase SQL Editor or `psql` using administrative
(owner) credentials. **Never** use `catalog_reader` for maintenance.

### Example 1: Add a New Partner University with Mappings

```sql
BEGIN;

-- 1. Insert partner university
INSERT INTO partner_universities (
    slug,
    name,
    country,
    region,
    city,
    continent,
    university_type,
    source_order
) VALUES (
    'eth-zurich',
    'ETH Zurich',
    'Switzerland',
    'Europe',
    'Zurich',
    'Europe',
    'Partner University',
    6
) RETURNING id;
-- Assume returned id = 6

-- 2. Insert partner module
INSERT INTO pu_modules (
    pu_id,
    code,
    title,
    units
) VALUES (
    6,
    '252-0057-00L',
    'Computer Systems',
    6
) RETURNING id;
-- Assume returned id = 201

-- 3. Map partner module to existing NUS module (e.g., CS2106)
INSERT INTO module_mappings (
    pu_module_id,
    nus_module_id,
    is_active,
    verified_units,
    verified_title,
    source_order
) SELECT
    201,
    id,
    true,
    6,
    'Computer Systems',
    1
FROM nus_modules
WHERE code = 'CS2106';

COMMIT;
```

### Example 2: Add a New Degree Program

```sql
BEGIN;

-- 1. Insert degree with non-null full_title
INSERT INTO degrees (
    code,
    name,
    full_title
) VALUES (
    'AI',
    'Artificial Intelligence',
    'Bachelor of Computing in Artificial Intelligence'
) RETURNING id;
-- Assume returned id = 7

-- 2. Associate existing core NUS modules with the degree
INSERT INTO degree_modules (
    degree_id,
    nus_module_id,
    is_active,
    source_order
)
SELECT
    7,
    id,
    true,
    ROW_NUMBER() OVER (ORDER BY code)
FROM nus_modules
WHERE code IN ('CS1101S', 'CS2040S', 'CS2109S', 'CS3244');

COMMIT;
```

### Example 3: Deactivate an Obsolete Mapping

```sql
BEGIN;

-- Soft-deactivate the mapping rather than deleting to preserve referential history
UPDATE module_mappings
SET is_active = false
WHERE pu_module_id = (SELECT id FROM pu_modules WHERE pu_id = 6 AND code = '252-0057-00L')
  AND nus_module_id = (SELECT id FROM nus_modules WHERE code = 'CS2106');

COMMIT;
```

---

## 5. Supported Local Tooling

The repository provides focused command-line tools for testing, validation, and maintenance:

### A. Local Seeder (`scripts.catalog_seed`)
Seeds a **disposable local test database** with core entities parsed from the reviewed
preview.
```bash
# Seed a local PostgreSQL instance:
uv run --directory backend python -m scripts.catalog_seed \
  --database-url postgresql://postgres:postgres@localhost:54322/postgres
```
> [!CAUTION]
> `scripts.catalog_seed` is restricted to local development targets (e.g. `localhost`,
> `127.0.0.1`). It strictly rejects remote Supabase URLs to prevent accidental data overwrites.

### B. Catalog Preview (`scripts.catalog_preview`)
Parses raw data files in `data/` and reviewed repairs in `data/repairs/` offline and
generates entity previews without contacting any database.
```bash
uv run --directory backend python -m scripts.catalog_preview --summary
```

### C. Catalog Verifier (`scripts.verify_catalog`)
Performs read-only reconciliation of a running PostgreSQL database against the
reviewed preview or API expectations.
```bash
# Reconcile database against preview:
uv run --directory backend python -m scripts.verify_catalog \
  --reconcile --target-project-ref wydziozsjibkvpgphpia
```

### D. Snapshot Core Data (`scripts.snapshot_core_data`)
Extracts a normalized, deterministic JSON snapshot of the eight core tables from a
live PostgreSQL target for audits or backups.
```bash
uv run --directory backend python -m scripts.snapshot_core_data \
  --database-url postgresql://postgres:postgres@localhost:54322/postgres \
  --output core_snapshot.json
```

### E. Baseline API Comparison (`scripts.compare_api_baseline`)
Compares active API responses from a localhost runtime against recorded golden
responses in `plan/remove-catalog-tables/baseline-responses.json`.
```bash
uv run --directory backend python -m scripts.compare_api_baseline --api-url http://localhost:8001
```

### F. Regression Gate (`scripts/check-regressions.sh`)
Runs the full prerequisite and regression gate across Ruff, backend pytest, frontend
typechecks, Playwright browser journeys, and absence tests.
```bash
./scripts/check-regressions.sh
```

---

## 6. Schema Migrations

Apply database schema changes through the Supabase CLI using project administrative
credentials:

```bash
# List applied and pending migrations:
npx supabase@latest migration list

# Push pending migrations to remote Supabase project:
npx supabase@latest db push
```

Historical migration history:
- `20261022000100_create_exchange_catalog.sql`: Initial 8-table catalog schema.
- `20261022000200_prepare_catalog_import.sql`: Historical provenance tables (now dropped).
- `20261022000300_catalog_reader.sql`: Read-only role and SELECT privileges.
- `20261024034234_remove_catalog_metadata.sql`: Dropped metadata tables & `source_row_id`.

---

## 7. Backups, Fallback, and Disaster Recovery

### Private Backups
- Never store raw database dumps or database credentials in public git repositories.
- Store database snapshots generated via `pg_dump` or `scripts.snapshot_core_data`
  in an encrypted, access-controlled vault or private object store outside the git tree.

### Disaster Recovery and Rollback
In the event of a critical database incident:
1. **Immediate Fallback**: Switch the backend service to frozen JSON mode:
   - In backend deployment settings, set `CATALOG_BACKEND=json` and clear `DATABASE_URL`.
   - Redeploy the backend. The API will immediately serve the frozen static catalog from `data/`.
2. **Point-in-Time Recovery**: Consult [recovery runbook](recovery.md) for full
   instructions on restoring core tables from private snapshots or replaying schema migrations.
