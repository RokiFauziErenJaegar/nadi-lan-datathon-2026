// Konfigurasi tersendiri untuk membangun berkas uji.
//
// Konfigurasi utama memecah keluaran menjadi beberapa bongkah (manualChunks)
// agar peramban memuat peta dan grafik hanya ketika diperlukan. Pemecahan itu
// tidak berlaku - dan menimbulkan galat - pada build SSR yang dijalankan Node,
// sehingga berkas ini sengaja tidak mewarisinya.
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  logLevel: "warn",
  build: {
    ssr: "uji/asap.tsx",
    outDir: "uji/dist",
    emptyOutDir: true,
    minify: false,
    rollupOptions: { output: { entryFileNames: "asap.js" } },
  },
});
