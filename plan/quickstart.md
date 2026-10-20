# Quickstart validation guide

This is a validation plan for the implementation phase; application packages do not exist yet.

## Prerequisites

- Python 3.12+, `uv`, Node.js LTS, npm.
- Vercel account for deployment validation.
- Source JSON files under `data/`.

## Local run after implementation

From the repository root:

```sh
cd backend && uv sync && uv run uvicorn app.main:app --reload --port 8000
```

In another terminal:

```sh
cd frontend && npm ci && NEXT_PUBLIC_API_BASE_URL=http://localhost:8000 npm run dev
```

The implementation should provide corresponding `uv run pytest`, `npm run lint`, `npm run typecheck`, and `npm run test:e2e` commands. Open `http://localhost:3000` and `/compare`. The exact Vercel project setup will be documented in the implementation README.

## End-to-end checks

1. Focus the degree picker: all six SoC degrees appear. Type a substring of a major or full title; keyboard navigation and Enter select it. Escape closes without changing selection.
2. Select Computer Science. Every partner appears, sorted by count then name; zero-count partners remain clickable. The top partner has the prominent card.
3. Open any card's View Mappings. `/compare` contains encoded `degree` and `uni` query parameters, both pickers are preselected, and rows show NUS code/name/4 units and partner fields from source.
4. Verify each card's partner-module, NUS-module, and mapping counts match Compare's distinct partner codes, distinct NUS codes, and row count. Artificial Intelligence at Toronto is 9/6/9; Business Analytics at Western Australia is 19 partner modules across 22 rows. Repeated course codes may have multiple rows.
5. Clear or invalidate either picker; old results disappear immediately. A valid pair with no mappings shows the empty state and a route back to Recommend.
6. Load `/compare` with invalid query values; selectors remain empty as appropriate and a note explains the invalid link.
7. Temporarily remove or corrupt a data file in a local test copy; API returns 503 and the UI shows an error without partial cards or rows. Restore the file.
8. Run the automated checks, measure the current dataset's warmed result rendering under one second, and repeat smoke checks on deployed URLs.

See `plan/contracts/openapi.yaml` for response shapes and `plan/data-model.md` for counting and validation rules.
