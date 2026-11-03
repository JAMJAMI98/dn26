import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Production: `npm run build` -> dist/, served by the backend on one port (3000).
// Dev only: `npm run dev` on 5173 proxies API calls to the backend.
export default defineConfig({
  plugins: [react()],
  server: {
    allowedHosts: true,
    proxy: { "/api": "http://localhost:3000", "/health": "http://localhost:3000" },
  },
  build: { outDir: "dist" },
});
