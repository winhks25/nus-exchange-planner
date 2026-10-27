# NUS Exchange Planner

Plan your NUS exchange semester without the guesswork. NUS Exchange Planner is a read-only exploration tool that helps NUS students discover partner universities and understand exactly which of their NUS courses map to a chosen exchange degree — so they can compare options and build a coherent study plan before applying.

## Description

The planner answers two questions every exchange student asks: *where can I go?* and *what does my degree actually require there?*. It pairs a curated catalog of NUS exchange partners with their course mappings, presented through three focused views — a recommendation engine ranked by module coverage, a browsable partner directory, and a detailed, deep-linkable mappings page. The app is read-only by design: it surfaces verified catalog data and never invents missing course titles, units, or locations.

## Tech Stack

**Frontend** — built with the latest Next.js and React.

- [Next.js 16](https://nextjs.org/) (App Router, `--webpack`)
- [React 19](https://react.dev/) + [TypeScript 5](https://www.typescriptlang.org/)
- [Tailwind CSS 4](https://tailwindcss.com/) with `class-variance-authority` / `clsx` for component styles
- [Base UI](https://base-ui.com/) for accessible primitives, [Lucide](https://lucide.dev/) for icons
- [Playwright](https://playwright.dev/) for end-to-end tests

**Backend** — a small FastAPI service that reads the catalog and returns JSON.

- [FastAPI](https://fastapi.tiangolo.com/) + [Pydantic v2](https://docs.pydantic.dev/)
- [psycopg 3](https://www.psycopg.org/psycopg3/) with a bounded transaction-pooler connection pool
- [uv](https://docs.astral.sh/uv/) for dependency management, [ruff](https://docs.astral.sh/ruff/) for linting, [pytest](https://docs.pytest.org/) for tests

**Data & deployment**

- Production catalog lives in [Supabase](https://supabase.com/) PostgreSQL, served through a read-only `catalog_reader` role
- A frozen JSON snapshot in `data/` ships as the offline/manual-rollback source
- Deployed as two [Vercel](https://vercel.com/) projects (backend API + Next.js web app)

## Features

- **Recommend** (`/`) — Ranks partner universities by the number of distinct mapped modules for a chosen degree. Filter by faculty and cascade through continent, country, and city selectors.
- **Universities** (`/universities`) — A full directory of exchange partners with rights-cleared photographs, location tags, official websites, and direct links into their course mappings.
- **Mappings** (`/mappings`) — Detailed course mappings between NUS and partner institutions, with remembered selection state and URL deep linking so links can be shared and resumed.

## Getting Started

Local development runs the frontend and backend together. The backend serves the checked-in JSON snapshot by default, so **no database credentials are required to run locally**.

### Prerequisites

- Python 3.12+ and [uv](https://docs.astral.sh/uv/)
- Node.js 20.9+ and npm

### Setup

```sh
uv sync --directory backend
npm ci --prefix frontend
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local
./dev
```

From then on, a single `./dev` command starts both servers (the API stops automatically when the frontend exits).

### Open it

- Frontend: <http://localhost:3000> and <http://localhost:3000/mappings>
- Backend API schema: <http://localhost:8001/openapi.json>

The API runs on port `8001` to avoid clashing with the frontend's dev server. Configuration lives in the ignored `backend/.env` and `frontend/.env.local` files:

| Variable | Purpose |
| --- | --- |
| `CATALOG_BACKEND` | `json` (default, no DB) or `postgres` (requires `DATABASE_URL`). Local defaults to `json`. |
| `DATABASE_URL` | Read-only `catalog_reader` connection string. Only needed for `postgres` mode. |
| `CORS_ORIGINS` | Comma-separated list of exact frontend origins (no trailing slash). |
| `NEXT_PUBLIC_API_BASE_URL` | Backend origin, without `/api/v1`. |

### Using the database locally

The default JSON snapshot means contributors can run the full app without any database access. To exercise the PostgreSQL backend locally, use a disposable seeded database rather than pointing a developer shell at Supabase. Production connects to the real Supabase catalog through the read-only runtime role; administrative SQL migrations and data maintenance use separate credentials that are never shared with the runtime.

## Tests & Checks

```sh
uv run --directory backend pytest -q
uv run --directory backend ruff check .
npm run lint --prefix frontend
npm run typecheck --prefix frontend
npm run build --prefix frontend
npm run test:e2e --prefix frontend
```

Backend tests create disposable local PostgreSQL databases; install PostgreSQL 15–17 and `openssl`. For the complete release gate — backend tests plus browser suites in both JSON and imported PostgreSQL modes — run:

```sh
./scripts/check-regressions.sh
```

This script never contacts Supabase or a developer database.

## Project Layout

```
.
├── api/              Backend entry point (Vercel runtime)
├── backend/          FastAPI application, repositories, and tests
├── data/             Frozen JSON catalog snapshot (offline source)
├── frontend/         Next.js web app, components, and E2E tests
├── scripts/          Seed, verify, and regression scripts
└── supabase/         Supabase schema and integration guide
```

## Documentation

- [Supabase integration guide](supabase/README.md)
- [Feature specification](docs/featureSpecs.md)
