import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Browser tests use a different API origin. Never let their compiled client
  // bundles overwrite the files served by an already-running local app.
  distDir: process.env.PLAYWRIGHT_TEST === "1" ? ".next-e2e" : ".next",
};

export default nextConfig;
