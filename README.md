# NUS Exchange Planner

A read-only tool for NUS School of Computing students to find exchange partners with module mappings. **Recommend** (`/`) ranks every partner by the number of distinct degree modules with a mapping. **Compare** (`/compare`) shows every qualifying mapping row for a degree and partner, including repeated NUS codes.

The source of truth is the checked-in JSON in `data/`. The API validates the complete catalog at startup. A missing or malformed file makes all three endpoints return 503; invalid NUS mapping codes are logged and skipped. Module titles are shown exactly as stored, including truncated titles.

## Run locally

Install Python 3.12+, [uv](https://docs.astral.sh/uv/), Node.js 20.9+, and npm. From the repository root:

```sh
uv sync --directory backend
CORS_ORIGINS=http://localhost:3000 uv run --directory backend uvicorn app.main:app --reload --port 8000
```

In a second terminal:

```sh
npm ci --prefix frontend
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000 npm run dev --prefix frontend
```

Open `http://localhost:3000` and `http://localhost:3000/compare`. The backend schema is at `http://localhost:8000/openapi.json`. Copy the `.env.example` files if you prefer persistent local variables; the example values match these commands. `CORS_ORIGINS` is a comma-separated list of exact frontend origins without trailing slashes. `NEXT_PUBLIC_API_BASE_URL` is the backend origin, without `/api/v1`.

## Checks

```sh
uv run --directory backend pytest -q
uv run --directory backend ruff check .
npm run lint --prefix frontend
npm run typecheck --prefix frontend
npm run build --prefix frontend
npm run test:e2e --prefix frontend
```

Playwright starts isolated local servers on ports 18765 and 18766 and needs Chromium (`cd frontend && npx playwright install chromium`). See [validation results](plan/validation-results.md) for dataset counts, browser scenarios, and timings.

## Deploy on Vercel

Create two Vercel projects from this repository. Deploy the **backend first**, with project root set to the **repository root**. The recognized FastAPI entry point is root `index.py` (with `api/index.py` also exporting the app); root `requirements.txt` supplies production dependencies and `.python-version` selects Python 3.12. Keeping the backend project at the repository root includes `data/` and the manifest in its deployment bundle. Confirm `GET /api/v1/catalog` on the deployed backend before connecting the frontend. See [Vercel's FastAPI deployment guide](https://vercel.com/docs/frameworks/backend/fastapi) for project setup.

Create the frontend project with root directory **`frontend/`** and the Next.js framework preset. Set `NEXT_PUBLIC_API_BASE_URL` to the stable backend production origin, then deploy. On the backend project, set `CORS_ORIGINS` to the frontend production origin; add other exact origins separated by commas when needed. Environment changes require redeployment so the browser bundle and backend instance receive the new values.

For previews, use a stable staging backend and set the frontend preview `NEXT_PUBLIC_API_BASE_URL` to its origin. Add the frontend preview origin to that backend's `CORS_ORIGINS`. For arbitrary preview URLs, use a stable preview domain alias or deploy a matching preview API with an exact allowlisted frontend origin; the backend does not use a wildcard CORS rule.

When JSON source files are added, removed, or renamed, regenerate the expected-file manifest and redeploy the backend:

```sh
uv run --directory backend python -m app.catalog
uv run --directory backend pytest -q
```

Content edits to existing files also require backend redeployment. The catalog loads once per backend function instance. Recheck the deployed API and both pages after each data release. Deployment smoke checks are described in [the quickstart](plan/quickstart.md); this repository has not been deployed by this implementation run.

## Scope and limitations

See [project overview](plan/overview.md), [feature specifications](plan/featureSpecs.md), and [API contract](plan/contracts/openapi.yaml). The current catalog has six SoC majors and five partners. Some source module names are incomplete, such as `CS2106` in the Toronto file; the UI does not invent missing text. Partner units are displayed only when present; NUS units display as 4.
