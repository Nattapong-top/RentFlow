import {defineConfig} from "@playwright/test";

const pythonExecutable =
  process.env.RENTFLOW_PYTHON ??
  (process.platform === "win32"
    ? "..\\.venv\\Scripts\\python.exe"
    : "../.venv/bin/python");

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: false,
  reporter: "list",
  use: {
    baseURL: "http://127.0.0.1:5174",
    browserName: "chromium",
    headless: true,
  },
  webServer: [
    {
      command:
        `"${pythonExecutable}" -m uvicorn --app-dir .. tests.e2e_server:app --host 127.0.0.1 --port 8001`,
      url: "http://127.0.0.1:8001/api/v1/rooms",
      reuseExistingServer: !process.env.CI,
      timeout: 30_000,
    },
    {
      command: "npm run dev -- --host 127.0.0.1 --port 5174 --strictPort --mode e2e",
      url: "http://127.0.0.1:5174",
      reuseExistingServer: !process.env.CI,
      timeout: 30_000,
    },
  ],
});
