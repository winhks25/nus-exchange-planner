import { defineConfig, devices } from "@playwright/test";
export default defineConfig({
  testDir: "./tests", timeout: 30000, use: { ...devices["Desktop Chrome"], baseURL: "http://127.0.0.1:18766" },
  webServer: [
    { command: "uv run --directory ../backend uvicorn app.main:app --host 127.0.0.1 --port 18765", url: "http://127.0.0.1:18765/openapi.json", reuseExistingServer: false, timeout: 30000, env: { CORS_ORIGINS: "http://127.0.0.1:18766" } },
    { command: "npm run dev -- --hostname 127.0.0.1 --port 18766", url: "http://127.0.0.1:18766", reuseExistingServer: false, timeout: 30000, env: { NEXT_PUBLIC_API_BASE_URL: "http://127.0.0.1:18765" } },
  ],
});
