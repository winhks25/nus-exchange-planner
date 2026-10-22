#!/usr/bin/env bash
# Release gate for the JSON-to-PostgreSQL catalog migration.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND="$ROOT/backend"
FRONTEND="$ROOT/frontend"

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing required command: $1" >&2
    exit 1
  fi
}

for command in uv node npm npx; do
  require_command "$command"
done

# Fail early when the disposable PostgreSQL toolchain is incomplete.
if ! uv run --directory "$BACKEND" python - <<'PY'
from scripts.postgres_validation import _find_binary

for binary in ("initdb", "pg_ctl", "psql", "openssl"):
    _find_binary(binary)
PY
then
  echo "PostgreSQL test binaries are unavailable; install PostgreSQL 15-17 and retry." >&2
  exit 1
fi

# Ignore developer database settings so no required suite can reach a real project.
unset CATALOG_BACKEND DATABASE_URL IMPORT_DATABASE_URL TEST_DATABASE_URL TEST_CATALOG_BACKEND

echo "==> Backend tests (JSON adapters plus disposable PostgreSQL fixtures)"
CATALOG_BACKEND=json uv run --directory "$BACKEND" pytest -q

echo "==> Browser regression (JSON rollback snapshot)"
(
  cd "$FRONTEND"
  TEST_CATALOG_BACKEND=json npx playwright test --reporter=line
)

echo "==> Browser regression (imported PostgreSQL catalog)"
(
  cd "$FRONTEND"
  TEST_CATALOG_BACKEND=postgres npx playwright test --reporter=line
)

echo "Migration regression gate passed."
