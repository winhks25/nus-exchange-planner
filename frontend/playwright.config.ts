import { defineConfig, devices } from "@playwright/test";

const LOCAL_HOSTS = new Set(["127.0.0.1", "localhost", "::1"]);

// Reject accidental remote targets before Playwright starts any server.
function validatedBackend(): "json" | "postgres" {
  const backend = (process.env.TEST_CATALOG_BACKEND ?? "json").trim().toLowerCase();
  if (backend !== "json" && backend !== "postgres") {
    throw new Error("TEST_CATALOG_BACKEND must be json or postgres");
  }
  return backend;
}

function validatedDatabaseUrl(): string {
  const value = process.env.TEST_DATABASE_URL?.trim();
  if (!value) return "";

  let url: URL;
  try {
    url = new URL(value);
  } catch {
    throw new Error("TEST_DATABASE_URL must be a valid PostgreSQL URL");
  }
  if (url.protocol !== "postgres:" && url.protocol !== "postgresql:") {
    throw new Error("TEST_DATABASE_URL must use the postgres:// scheme");
  }
  if (!LOCAL_HOSTS.has(url.hostname.replace(/^\[|\]$/g, ""))) {
    throw new Error("TEST_DATABASE_URL must point at a local disposable PostgreSQL server");
  }
  return value;
}

const backend = validatedBackend();
const databaseUrl = validatedDatabaseUrl();
const backendEnvironment = {
  CORS_ORIGINS: "http://127.0.0.1:18766",
  CATALOG_BACKEND: backend,
  DATABASE_URL: databaseUrl,
  DB_POOL_MIN_SIZE: "0",
  DB_POOL_MAX_SIZE: "4",
  DB_CONNECT_TIMEOUT: "2",
};

const backendCommand =
  backend === "postgres" && !databaseUrl
    ? "uv run --directory ../backend python -m scripts.serve_catalog_api --host 127.0.0.1 --port 18765"
    : "uv run --directory ../backend uvicorn app.main:app --host 127.0.0.1 --port 18765";

export default defineConfig({
  testDir: "./tests",
  testIgnore: backend === "json" ? /database-regression\.spec\.ts/ : undefined,
  timeout: 30000,
  use: {
    ...devices["Desktop Chrome"],
    baseURL: "http://127.0.0.1:18766",
  },
  webServer: [
    {
      command: backendCommand,
      url: "http://127.0.0.1:18765/openapi.json",
      reuseExistingServer: false,
      timeout: 60000,
      gracefulShutdown: { signal: "SIGTERM", timeout: 15000 },
      env: backendEnvironment,
    },
    {
      command: "npm run dev -- --hostname 127.0.0.1 --port 18766",
      url: "http://127.0.0.1:18766",
      reuseExistingServer: false,
      timeout: 30000,
      env: {
        NEXT_PUBLIC_API_BASE_URL: "http://127.0.0.1:18765",
        PLAYWRIGHT_TEST: "1",
      },
    },
    {
      command: "node tests/fixtures/preview-server.mjs",
      url: "http://127.0.0.1:18767",
      reuseExistingServer: false,
      timeout: 30000,
    },
  ],
});
