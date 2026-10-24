#!/usr/bin/env bash
# Release and regression gate for the exchange planner application.
# Verifies backend and frontend quality, schema integrity, and end-to-end browser flows.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND="$ROOT/backend"
FRONTEND="$ROOT/frontend"

# Check required command line tools
require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing required command: $1" >&2
    exit 1
  fi
}

for cmd in uv node npm npx; do
  require_command "$cmd"
done

# Fail fast when required local PostgreSQL binaries are missing
if ! uv run --directory "$BACKEND" python - <<'PY'
from scripts.postgres_validation import _find_binary

for binary in ("initdb", "pg_ctl", "psql", "openssl"):
    _find_binary(binary)
PY
then
  echo "PostgreSQL test binaries are unavailable; install PostgreSQL 15-17 and retry." >&2
  exit 1
fi

# Clear developer and production database variables to enforce test isolation
unset CATALOG_BACKEND DATABASE_URL IMPORT_DATABASE_URL TEST_DATABASE_URL TEST_CATALOG_BACKEND

# Run static quality and type checks
echo "==> Backend lint check (Ruff)"
uv run --directory "$BACKEND" ruff check app scripts tests

echo "==> Frontend lint check"
npm --prefix "$FRONTEND" run lint

echo "==> Frontend type check"
npm --prefix "$FRONTEND" run typecheck

echo "==> Frontend production build"
npm --prefix "$FRONTEND" run build

# Run backend test suites
echo "==> Backend tests (contracts, repository adapters, failure scenarios, and core seed)"
CATALOG_BACKEND=json uv run --directory "$BACKEND" pytest -q

echo "==> Schema absence and upgrade verification"
uv run --directory "$BACKEND" pytest -q tests/test_catalog_table_removal.py tests/test_catalog_absence.py

# Run Playwright browser regressions sequentially
echo "==> Browser regression: JSON fallback mode"
(
  cd "$FRONTEND"
  TEST_CATALOG_BACKEND=json npx playwright test --reporter=line
)

echo "==> Browser regression: Core-seeded PostgreSQL mode"
(
  cd "$FRONTEND"
  TEST_CATALOG_BACKEND=postgres npx playwright test --reporter=line
)

echo "Regression gate passed successfully."
