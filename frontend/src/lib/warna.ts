/**
 * Sistem warna visualisasi data.
 *
 * Setiap warna di sini mengerjakan SATU tugas, dan tugas itulah yang menentukan
 * strukturnya:
 *
 * - **Status** (kategori risiko) - keadaan berjenjang dari baik sampai genting.
 *   Skala tetap, maknanya khusus, dan WAJIB disertai ikon serta tulisan. Dua di
 *   antaranya berkontras rendah pada latar terang secara sengaja; ikon dan
 *   tulisanlah yang menanggung maknanya, bukan warnanya.
 * - **Sekuensial** (peta dan peta panas) - besaran, satu rona dari terang ke
 *   gelap. Terang berarti mendekati nol.
 * - **Divergen** (kontribusi faktor) - kutub, dua rona berlawanan dengan
 *   titik tengah abu-abu netral. Merah mendorong risiko naik, biru menahannya.
 * - **Kategorikal** (deret terpisah) - identitas, delapan rona berurutan tetap.
 *   Tidak pernah diputar ulang: deret kesembilan dilipat menjadi "lainnya".
 *
 * Seluruh nilai berasal dari palet yang sudah diuji dengan alat pemeriksa,
 * bukan dipilih dengan mata. Pilihan pertama untuk kategori risiko - hijau tua,
 * kuning tua, jingga, merah tua - gugur pada dua pemeriksaan sekaligus:
 * hijaunya terbaca abu-abu, dan pasangan jingga dengan merah tua terlalu
 * berdekatan bahkan bagi pembaca berpenglihatan normal.
 */

// ---------------------------------------------------------------------------
// Status - kategori risiko
// ---------------------------------------------------------------------------
export const WARNA_RISIKO = {
  rendah: "#0ca30c",
  sedang: "#fab219",
  tinggi: "#ec835a",
  sangat_tinggi: "#d03b3b",
} as const;

export const LABEL_RISIKO = {
  rendah: "Risiko Rendah",
  sedang: "Risiko Sedang",
  tinggi: "Risiko Tinggi",
  sangat_tinggi: "Risiko Sangat Tinggi",
} as const;

/** Ikon penyerta. Warna tidak pernah berdiri sendiri. */
export const IKON_RISIKO = {
  rendah: "CircleCheck",
  sedang: "CircleAlert",
  tinggi: "TriangleAlert",
  sangat_tinggi: "OctagonAlert",
} as const;

export type KategoriRisiko = keyof typeof WARNA_RISIKO;

export const URUTAN_RISIKO: KategoriRisiko[] = [
  "sangat_tinggi",
  "tinggi",
  "sedang",
  "rendah",
];

export function kategoriDariSkor(skor: number | null | undefined): KategoriRisiko {
  if (skor === null || skor === undefined) return "rendah";
  if (skor >= 80) return "sangat_tinggi";
  if (skor >= 60) return "tinggi";
  if (skor >= 40) return "sedang";
  return "rendah";
}

// ---------------------------------------------------------------------------
// Sekuensial - besaran (peta, peta panas)
// ---------------------------------------------------------------------------
/**
 * Satu rona biru, dari terang ke gelap. Dipakai untuk besaran berkelanjutan
 * seperti tingkat kemiskinan pada peta.
 *
 * Perlu dibedakan dari palet status: tingkat kemiskinan sebuah pekon adalah
 * BESARAN, bukan keadaan berjenjang. Memakai hijau-kuning-merah untuk besaran
 * memaksa pembaca menghafal ambang yang tidak ada, sementara satu rona
 * menyampaikan "lebih gelap berarti lebih banyak" tanpa perlu dijelaskan.
 */
export const RAMPA_SEKUENSIAL = [
  "#cde2fb",
  "#9ec5f4",
  "#6da7ec",
  "#3987e5",
  "#256abf",
  "#184f95",
  "#0d366b",
] as const;

/** Pilih warna sekuensial menurut posisi nilai pada rentangnya. */
export function warnaSekuensial(
  nilai: number | null | undefined,
  minimum: number,
  maksimum: number,
): string {
  if (nilai === null || nilai === undefined || Number.isNaN(nilai)) return "#e2e8f0";
  if (maksimum <= minimum) return RAMPA_SEKUENSIAL[3];
  const bagian = Math.min(1, Math.max(0, (nilai - minimum) / (maksimum - minimum)));
  const indeks = Math.min(
    RAMPA_SEKUENSIAL.length - 1,
    Math.floor(bagian * RAMPA_SEKUENSIAL.length),
  );
  return RAMPA_SEKUENSIAL[indeks];
}

/** Warna tulisan yang terbaca di atas warna sekuensial tertentu. */
export function tintaDiAtas(warnaLatar: string): string {
  const gelap = ["#3987e5", "#256abf", "#184f95", "#0d366b"];
  return gelap.includes(warnaLatar) ? "#ffffff" : "#0f172a";
}

// ---------------------------------------------------------------------------
// Divergen - kutub (kontribusi faktor risiko)
// ---------------------------------------------------------------------------
/**
 * Biru dan merah dengan titik tengah abu-abu netral.
 *
 * Dipakai pada penjelasan skor: faktor yang mendorong risiko naik berwarna
 * merah, yang menahannya berwarna biru, dan garis nol berwarna abu-abu. Titik
 * tengah harus netral - memakai rona di tengah akan membuat "tidak berpengaruh"
 * tampak seperti sebuah nilai tersendiri.
 */
export const DIVERGEN = {
  menaikkan: "#d03b3b",
  menaikkanMuda: "#f0a3a3",
  netral: "#f0efec",
  menurunkan: "#2a78d6",
  menurunkanMuda: "#9ec5f4",
} as const;

export function warnaKontribusi(nilai: number): string {
  return nilai >= 0 ? DIVERGEN.menaikkan : DIVERGEN.menurunkan;
}

// ---------------------------------------------------------------------------
// Kategorikal - identitas deret
// ---------------------------------------------------------------------------
/**
 * Delapan rona berurutan tetap. Urutannya adalah mekanisme keamanan bagi
 * pembaca dengan buta warna, sehingga tidak pernah diubah maupun diputar ulang.
 * Deret kesembilan dilipat menjadi "lainnya", bukan diberi rona baru.
 */
export const KATEGORIKAL = [
  "#2a78d6",
  "#eb6834",
  "#1baf7a",
  "#eda100",
  "#e87ba4",
  "#008300",
  "#4a3aa7",
  "#e34948",
] as const;

export function warnaKategori(indeks: number): string {
  return KATEGORIKAL[indeks % KATEGORIKAL.length];
}

// ---------------------------------------------------------------------------
// Tinta dan permukaan
// ---------------------------------------------------------------------------
/**
 * Tulisan memakai warna tinta, TIDAK PERNAH warna deret. Nilai, label, dan
 * keterangan tetap berwarna tinta; penanda berwarna di sebelahnya yang
 * menyampaikan identitasnya.
 */
export const TINTA = {
  utama: "var(--tinta-utama, #0f172a)",
  kedua: "var(--tinta-kedua, #475569)",
  redup: "var(--tinta-redup, #94a3b8)",
  kisi: "var(--tinta-kisi, #e2e8f0)",
  sumbu: "var(--tinta-sumbu, #cbd5e1)",
  permukaan: "var(--tinta-permukaan, #ffffff)",
} as const;
