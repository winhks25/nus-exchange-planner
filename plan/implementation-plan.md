# Implementation plan: NUS Exchange Planner MVP

Status: design ready. Source of truth: `plan/featureSpecs.md` and `plan/overview.md`.

## Technical context

| Area | Decision |
| --- | --- |
| Frontend | Next.js App Router, React, TypeScript; shadcn/ui Base UI components with Tailwind CSS v4; deploy as a Vercel project |
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

The API owns code extraction, filtering, counting, and sorting. Each recommendation exposes distinct partner module count, distinct NUS module count, and qualifying mapping-row count from the same pair-filtered rows; rank by distinct NUS module count. Compare exposes both distinct counts and the rows. The frontend displays API results and never recomputes recommendation counts. One shared `TypeableCombobox` client component implements the specified filtering, clearing, keyboard, and active-descendant behavior for both degree fields and the Compare partner field; `DegreeCombobox` is a thin adapter over it. `/compare` validates URL parameters against catalog options and keeps the selected pair in the URL for shareable links. Fetching states distinguish initial blank selection, loading, empty result, and service failure. University cards and mapping rows are composed from shadcn/ui Base UI `Card` primitives under `frontend/components/ui/`, while the existing rank order, three count labels, URL format, six-track desktop layout, and narrow-screen stacking rules remain in force.

## Constitution check

This checkout has no `.specify/memory/constitution.md`, so there are no project constitution gates to evaluate. The design follows the explicit MVP scope: read-only JSON, no database, no accounts, and only two pages. Recheck if a constitution is added.

## Delivery sequence

1. Add `backend/` and `frontend/` workspaces and pinned dependency manifests. Configure Vercel roots and local environment examples.
2. Implement catalog loading and validation: discover all major files and mapping files, explicit country labels, recursive list-string course-code extraction, mapping code checks, and all-or-nothing load errors.
3. Implement API response models and the endpoints in `contracts/openapi.yaml`; generate or verify the runtime OpenAPI schema against the contract.
4. Build the shared typable picker and API client, then Recommend ranking cards and Compare rows/empty state. Compose the cards and rows from shadcn/ui Base UI `Card` primitives while keeping API-owned counts, ranking, and URL state. Preserve stale-request safety when selections change.
5. Add focused pytest cases for extraction, duplicate mappings, zero matches, sorting, malformed files, and consistency. Add Playwright flows for search, keyboard selection, deep links, empty and error states.
6. Verify local end-to-end behavior and response time against the current dataset; deploy backend then frontend, set CORS and API URL, and run the same smoke scenarios against production.

## Acceptance gates

- Every current partner appears on Recommend, including zero counts, sorted by distinct NUS module count descending then name ascending. Every card exposes a visible rank number, a prominent university name, country, all three separately labeled counts, and a View Mapping action. At desktop width the first card spans the grid, ranks 2–3 each span half its width, and the rest each span one third; cards stack without overflow on narrow screens.
- Each Recommend partner count equals the number of distinct partner codes in Compare, its NUS count equals the number of distinct NUS codes, and its mapping count equals the number of Compare rows for the same pair. Both pages label all three values separately. The Artificial Intelligence–University of Toronto regression case is 9 partner modules, 6 NUS modules, and 9 mappings; Business Analytics–University of Western Australia has 19 partner modules across 22 rows.
- Both pickers and deep links follow `plan/featureSpecs.md`, including invalid values and keyboard behavior. Both degree fields and the Compare partner field use the same typable picker component.
- A bad file never produces partial results; an invalid mapping code is skipped and logged.
- The current dataset renders results in under one second in a warmed local or deployed session. Record cold-start latency separately.

## Risks and decisions

- Vercel Python functions have deployment size and cold-start considerations; the current JSON dataset is small. Measure cold starts after deployment.
- File changes require backend redeployment. That is acceptable for the read-only MVP.
- University display names are the specified URL values. If duplicate names appear later, add stable IDs and migrate deep links.
- shadcn/ui uses the Base UI variant (`@base-ui/react`) with Tailwind CSS v4 configured through PostCSS and CSS theme tokens. Tokens map to the existing palette so the pre-migration layout keeps its colors and spacing.
- No implementation has started in this plan phase.
