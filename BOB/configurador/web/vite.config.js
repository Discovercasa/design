import { defineConfig } from "vite";

export default defineConfig({
  // this computer only: nothing goes online without the user's OK. Pyodide is not watched: rewriting its .wasm
  // while the server runs (npm run motor) crashed the watcher (EBUSY, 2026-10-21)
  server: { host: "localhost", watch: { ignored: ["**/public/pyodide/**"] } },
  worker: { format: "es" },
  optimizeDeps: { exclude: ["pyodide"] },
});
