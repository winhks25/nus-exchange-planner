import { defineConfig, devices } from "@playwright/test";

// Browser checks default to JSON; set TEST_CATALOG_BACKEND=postgres with
// TEST_DATABASE_URL to exercise a disposable preview-seeded database instead.
const backendEnvironment: Record<string, string> = {
  CORS_ORIGINS: "http://127.0.0.1:18766",
  CATALOG_BACKEND: process.env.TEST_CATALOG_BACKEND ?? "json",
  DATABASE_URL: process.env.TEST_DATABASE_URL ?? "",
};

export default defineConfig({
  testDir: "./tests",
  timeout: 30000,
  use: {
    ...devices["Desktop Chrome"],
    baseURL: "http://127.0.0.1:18766",
  },
  webServer: [
    {
      command: "uv run --directory ../backend uvicorn app.main:app --host 127.0.0.1 --port 18765",
      url: "http://127.0.0.1:18765/openapi.json",
      reuseExistingServer: false,
      timeout: 30000,
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
