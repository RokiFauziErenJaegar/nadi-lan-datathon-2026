import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Peladen pengembangan meneruskan permintaan /api ke backend FastAPI,
// sehingga tidak ada perbedaan alamat antara mode pengembangan dan mode
// terpasang - dan tidak ada persoalan lintas asal yang perlu diakali.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: "dist",
    sourcemap: false,
    chunkSizeWarningLimit: 900,
    rollupOptions: {
      output: {
        // Peta dan grafik dipisah agar layar ringkasan tidak perlu menunggu
        // pustaka peta selesai diunduh.
        manualChunks: {
          peta: ["leaflet", "react-leaflet"],
          grafik: ["recharts"],
        },
      },
    },
  },
});
