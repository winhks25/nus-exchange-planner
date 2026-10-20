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

## shadcn/ui Base UI setup

- **Decision:** Use the shadcn/ui Base UI style (`base-nova`) on the existing Next.js 16 App Router project, with Tailwind CSS v4, `class-variance-authority`, `clsx`, `tailwind-merge`, `@base-ui/react`, and the `shadcn` Tailwind utility stylesheet. Keep `components.json` style `base-nova`, the `@/*` TypeScript alias, and the CSS variables in `frontend/app/globals.css`.
- **Rationale:** Matches the requested Base UI variant without starting a new app; Tailwind v4's CSS-first configuration avoids a `tailwind.config` file. Reusable primitives live in `frontend/components/ui/` and domain components remain in `frontend/components/`. Mapping shadcn color tokens to the existing palette preserves the current visual design while the old component CSS is migrated incrementally.
- **Files:** `frontend/components.json`, `frontend/postcss.config.mjs`, `frontend/package.json`, `frontend/package-lock.json`, `frontend/app/globals.css`, `frontend/lib/utils.ts`, and the generated `frontend/components/ui/{card,button,input}.tsx`.
- **Alternatives considered:** Radix or React Aria variants (rejected by the task), a fresh shadcn scaffold (would discard the existing pages and styles), and keeping an unmanaged CSS-in-JS approach (would not provide the requested shadcn primitives).
- **Consequences:** The custom `.card`, `.mapping-row`, and native-select rules continue to apply during the migration phases, so the shadcn primitives are available without forcing a visual rewrite in the same change.

## Unresolved questions

None blocking. Backend hosting was clarified as Vercel. Exact package versions should be selected and locked when implementation begins because framework support changes over time.
