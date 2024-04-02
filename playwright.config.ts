import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./scenarios",
  testMatch: "**/*.ts",
  retries: 0,
  workers: 1,
  reporter: "list"
});
