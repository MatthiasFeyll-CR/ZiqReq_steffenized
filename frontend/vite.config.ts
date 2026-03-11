import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import path from "path";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    proxy: {
      "/api": {
        target: process.env.VITE_PROXY_API_TARGET ?? "http://localhost:8000",
        changeOrigin: true,
      },
      "/ws": {
        target: process.env.VITE_PROXY_WS_TARGET ?? "ws://localhost:8000",
        ws: true,
      },
    },
  },
});
