# Implementation plan: NUS Exchange Planner MVP

Status: design ready. Source of truth: `plan/featureSpecs.md` and `plan/overview.md`.

## Technical context

| Area | Decision |
| --- | --- |
| Frontend | Next.js App Router, React, TypeScript; deploy as a Vercel project |
| Backend | Python 3.12+, FastAPI, Pydantic; deploy as a separate Vercel FastAPI project |
| Data | Versioned JSON in `data/`; no database, login, or write API |
| API | Read-only JSON endpoints under `/api/v1`, with generated OpenAPI schema |
| Tests | pytest for data and API; Playwright for the two page flows and keyboard accessibility |
| Local tooling | `uv` for Python, npm for frontend; lock dependencies before implementation |

## Architecture

```text
Browser -> Next.js (Recommend / Compare) -> FastAPI -> versioned JSON files
```

Use two Vercel projects from this repository. The frontend gets `NEXT_PUBLIC_API_BASE_URL` pointing to the backend's stable production URL; preview environments need a corresponding preview API URL or a fixed staging API. Restrict backend CORS to configured frontend origins. Ship the `data/` directory in the backend function bundle and resolve its path from the application package, never from the process working directory. Validate every file and build one immutable in-memory catalog per function instance. Any missing or malformed file makes the catalog unavailable and returns a clear service error, rather than partial rankings. Invalid mapping NUS codes are logged and omitted.

The API owns code extraction, filtering, counting, and sorting. The frontend displays API results and never recomputes counts. A shared `DegreeCombobox` client component implements the specified keyboard and active-descendant behavior. `/compare` validates URL parameters against catalog options and keeps the selected pair in the URL for shareable links. Fetching states distinguish initial blank selection, loading, empty result, and service failure.

## Constitution check

This checkout has no `.specify/memory/constitution.md`, so there are no project constitution gates to evaluate. The design follows the explicit MVP scope: read-only JSON, no database, no accounts, and only two pages. Recheck if a constitution is added.

## Delivery sequence

1. Add `backend/` and `frontend/` workspaces and pinned dependency manifests. Configure Vercel roots and local environment examples.
2. Implement catalog loading and validation: discover all major files and mapping files, explicit country labels, recursive list-string course-code extraction, mapping code checks, and all-or-nothing load errors.
3. Implement API response models and the endpoints in `contracts/openapi.yaml`; generate or verify the runtime OpenAPI schema against the contract.
4. Build the degree combobox and API client, then Recommend ranking cards and Compare rows/empty state. Preserve stale-request safety when selections change.
5. Add focused pytest cases for extraction, duplicate mappings, zero matches, sorting, malformed files, and consistency. Add Playwright flows for search, keyboard selection, deep links, empty and error states.
6. Verify local end-to-end behavior and response time against the current dataset; deploy backend then frontend, set CORS and API URL, and run the same smoke scenarios against production.

## Acceptance gates

- Every current partner appears on Recommend, including zero counts; first card is prominent and remaining cards are compact.
- Each Recommend count equals the number of distinct NUS codes in Compare for the same pair; Compare may contain more rows when codes have multiple mappings.
- Both pickers and deep links follow `plan/featureSpecs.md`, including invalid values and keyboard behavior.
- A bad file never produces partial results; an invalid mapping code is skipped and logged.
- The current dataset renders results in under one second in a warmed local or deployed session. Record cold-start latency separately.

## Risks and decisions

- Vercel Python functions have deployment size and cold-start considerations; the current JSON dataset is small. Measure cold starts after deployment.
- File changes require backend redeployment. That is acceptable for the read-only MVP.
- University display names are the specified URL values. If duplicate names appear later, add stable IDs and migrate deep links.
- No implementation has started in this plan phase.
