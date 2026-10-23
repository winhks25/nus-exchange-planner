# Deployment and target verification

Date: 2026-10-23 (Asia/Singapore). Scope: T004 read-only verification of the
linked Supabase target and the currently deployed origins. No production mutation
was performed.

## Verified target

| Item | Observed value | Evidence |
| --- | --- | --- |
| Linked project ref | `wydziozsjibkvpgphpia` | `supabase/.temp/project-ref`; `supabase/.temp/linked-project.json` |
| Linked project name | `nus-exchange-planner` | `supabase/.temp/linked-project.json` |
| Supabase API URL | `https://wydziozsjibkvpgphpia.supabase.co` | Supabase MCP project URL |
| Database | `postgres` | Read-only SQL via MCP |
| Server version | PostgreSQL `17.11` | Read-only SQL via MCP |
| Reported deployment database region | `ap-southeast-2` | `plan/supabase-migration/deployment-results.md` |
| Runtime role recorded by deployment | `catalog_reader` | `plan/supabase-migration/deployment-results.md` |

The historical project reference `wydziozsjibkvpgphpia` matches the actual linked
project. No target mismatch was found.

## Migration history

Read-only verification returned exactly three applied versions, matching the
checked-in migration files:

| Version | Name |
| --- | --- |
| `20261022000100` | `create_exchange_catalog` |
| `20261022000200` | `prepare_catalog_import` |
| `20261022000300` | `catalog_reader` |

The local `supabase/migrations/` directory contains the same three versions and no
pending local migration. The new removal migration does not exist yet (T027).

## Current production data boundary

Read-only counts at verification time:

| Object | Count |
| --- | ---: |
| `public.catalog_import_batches` | 1 |
| Completed/current batches | 1 |
| `public.catalog_source_snapshots` | 8 |
| `public.catalog_source_rows` | 154 |
| `public.catalog_issues` | 34 |
| `public.catalog_repairs` | 44 |
| `public.degrees` | 6 |
| `public.partner_universities` | 5 |
| `public.module_mappings` | 151 |

All five metadata tables and the eight core tables are present in `public` with
RLS enabled. This is the state the later export and removal tasks must preserve
and compare against.

## Deployed origins

| Item | Value | Check |
| --- | --- | --- |
| Backend production origin | `https://nus-exchange-planner-api.vercel.app` | `/api/v1/catalog` returned 200 |
| Backend OpenAPI | `https://nus-exchange-planner-api.vercel.app/openapi.json` | Returned 200 |
| Frontend production origin | `https://nus-exchange-planner-web.vercel.app` | `/` returned 200 |
| Backend mode indicator | PostgreSQL | `Artificial Intelligence / University of Toronto` returned 10 mapping rows, matching the repaired PostgreSQL catalog rather than the frozen JSON count of 9 |
| CORS | Exact frontend origin allowed | `Origin: https://nus-exchange-planner-web.vercel.app` returned `access-control-allow-origin` with that exact value |

The existing deployment record also lists backend project
`nus-exchange-planner-api`, frontend project `nus-exchange-planner-web`, and the
deployment IDs `nus-exchange-planner-3hir2iioj-…` (backend) and
`nus-exchange-planner-b64ftt60i-…` (frontend). Those are references, not a fresh
deployment performed by this task.

## CLI and access notes

- Supabase CLI was run through `npx --yes supabase@latest` at version `2.121.0`.
- `supabase migration list --linked` failed with
  `AccessTokenRequiredError` because no access token or login session is
  available in this environment.
- Remote identity, migration history, and counts were therefore read through the
  configured Supabase MCP connection. The MCP query path executed read-only SQL
  and printed no credentials, connection strings, or passwords.

## Checks before destructive work

The following must still be confirmed at the T034/T036 boundary:

1. The active backend deployment contains the compatible core-readiness runtime
   from T014; the existing record does not tie a Vercel deployment to a source
   commit.
2. The linked project has no pending migration other than the reviewed removal
   migration and no schema dependency unexpected by `schema-inventory.md`.
3. The production reader role still resolves to `catalog_reader` and has only the
   intended read access.
4. The T008 baseline remains fresh, or a new versioned baseline is captured
   before deletion.

No blocker prevents local preparation work. Production deletion remains gated on
the later tasks and is not authorized by this record.
