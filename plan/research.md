# Research and design decisions

## Frontend and backend deployment

- **Decision:** Next.js App Router and FastAPI as separate Vercel projects.
- **Rationale:** Matches the requested stack and keeps the Python API independently deployable. Vercel supports FastAPI as a Python function; Next.js supports server components plus client components for interactive controls.
- **Alternatives considered:** One mixed deployment; a separate Python hosting provider. Separate Vercel projects make data bundling and environment configuration explicit.
- **References:** [Vercel FastAPI](https://vercel.com/docs/frameworks/backend/fastapi), [Next.js App Router](https://nextjs.org/docs/app), [Server and Client Components](https://nextjs.org/docs/app/getting-started/server-and-client-components).

## Data and computation

- **Decision:** Read checked-in JSON and form a validated in-memory catalog on each backend instance. Compute counts and rows from the same filtered mapping list.
- **Rationale:** Dataset is approximately 80 KB and the product has no write operations. One backend computation prevents Recommend/Compare drift.
- **Alternatives considered:** Postgres and frontend-side calculation. Both add unnecessary complexity; frontend-side calculation would duplicate business rules.

## API and interaction

- **Decision:** Expose catalog options, degree rankings, and pair mappings through typed read-only endpoints. Use major and university display names as public query values, matching the specified deep link.
- **Rationale:** Keeps the frontend thin and supports direct `/compare?degree=...&uni=...` loading.
- **Alternatives considered:** A single bulk-data endpoint. It couples the browser to raw file format and sends unrelated mappings.

## Dependency and testing choices

- **Decision:** Pin dependencies with lockfiles during implementation; use pytest and Playwright for behavior that can regress across the API/UI boundary.
- **Rationale:** The core risks are parsing, distinct counts, keyboard selection, URL state, and stale results.
- **Alternatives considered:** Snapshot-only tests; they do not establish count consistency or accessibility behavior.

## Unresolved questions

None blocking. Backend hosting was clarified as Vercel. Exact package versions should be selected and locked when implementation begins because framework support changes over time.
