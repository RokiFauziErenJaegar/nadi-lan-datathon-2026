/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // Warna utama diambil dari nuansa biru tua administrasi pemerintahan,
        // dipilih tenang alih-alih mencolok. Antarmuka yang dipakai berjam-jam
        // setiap hari harus mudah dipandang, bukan menarik perhatian.
        nadi: {
          50: "#eef4fb",
          100: "#d6e4f5",
          200: "#b0cbea",
          300: "#7fa9db",
          400: "#4d84c8",
          500: "#2c65ae",
          600: "#1f4d8c",
          700: "#1a3d6f",
          800: "#17335a",
          900: "#122a4a",
          950: "#0b1a30",
        },
        // Warna kategori risiko, dari palet status yang sudah diuji keterbacaannya
        // bagi pembaca dengan buta warna. Nilainya sama persis dengan yang
        // ditetapkan pada nadi.db.enums.KategoriRisiko dan src/lib/warna.ts.
        // WAJIB selalu disertai ikon dan tulisan - dua di antaranya berkontras
        // rendah pada latar terang secara sengaja.
        risiko: {
          rendah: "#0ca30c",
          sedang: "#fab219",
          tinggi: "#ec835a",
          sangat: "#d03b3b",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "Segoe UI", "Roboto", "sans-serif"],
        mono: ["ui-monospace", "SFMono-Regular", "Menlo", "monospace"],
      },
      fontSize: {
        "2xs": ["0.6875rem", { lineHeight: "1rem" }],
      },
      boxShadow: {
        kartu: "0 1px 2px 0 rgb(0 0 0 / 0.04), 0 1px 6px -1px rgb(0 0 0 / 0.06)",
        naik: "0 4px 12px -2px rgb(0 0 0 / 0.10)",
      },
    },
  },
  plugins: [],
};
