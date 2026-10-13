import { defineConfig, devices } from "@playwright/test";

// Kept apart from the test suite: this drives the real stack and writes docs/media.
export default defineConfig({
  testDir: ".",
  testMatch: "capture.spec.ts",
  use: {
    ...devices["Desktop Chrome"],
    baseURL: "http://127.0.0.1:3000",
    viewport: { width: 1440, height: 900 },
    deviceScaleFactor: 1,
  },
});
