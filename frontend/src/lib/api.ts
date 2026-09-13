/**
 * Klien API tunggal untuk seluruh antarmuka.
 *
 * Tiga hal ditangani terpusat di sini, sehingga tidak perlu diulang pada
 * setiap layar:
 *
 * - Token akses disisipkan otomatis pada setiap permintaan.
 * - Tanggapan 401 mengakhiri sesi dan mengembalikan pengguna ke halaman masuk,
 *   alih-alih menampilkan galat yang tidak dapat ditindaklanjuti.
 * - Pesan galat dari peladen diteruskan apa adanya. Peladen menulis pesannya
 *   dalam bahasa Indonesia yang menjelaskan sebab dan jalan keluarnya;
 *   menggantinya dengan "terjadi kesalahan" akan membuang keterangan itu.
 */

const KUNCI_TOKEN = "nadi.token";
const KUNCI_PENGGUNA = "nadi.pengguna";

export interface Pengguna {
  id: number;
  nama_pengguna: string;
  nama_lengkap: string;
  jabatan?: string | null;
  peran: string;
  label_peran: string;
  deskripsi_peran?: string;
  opd?: string | null;
  wilayah_akses: string[];
  cakupan_data?: string;
  boleh_buka_keluarga?: boolean;
  kewenangan?: string[];
}

export class GalatApi extends Error {
  constructor(
    message: string,
    readonly status: number,
    readonly rincian?: unknown,
  ) {
    super(message);
    this.name = "GalatApi";
  }

  /** Benar bila galat berasal dari penjaga data pribadi. */
  get kebocoranDataPribadi(): boolean {
    return this.status === 422 && String(this.rincian ?? "").includes("data_pribadi");
  }
}

export const simpanan = {
  ambilToken: (): string | null => localStorage.getItem(KUNCI_TOKEN),
  simpanToken: (token: string) => localStorage.setItem(KUNCI_TOKEN, token),
  hapusToken: () => localStorage.removeItem(KUNCI_TOKEN),

  ambilPengguna: (): Pengguna | null => {
    const mentah = localStorage.getItem(KUNCI_PENGGUNA);
    if (!mentah) return null;
    try {
      return JSON.parse(mentah) as Pengguna;
    } catch {
      return null;
    }
  },
  simpanPengguna: (p: Pengguna) => localStorage.setItem(KUNCI_PENGGUNA, JSON.stringify(p)),
  hapusPengguna: () => localStorage.removeItem(KUNCI_PENGGUNA),

  bersihkan: () => {
    localStorage.removeItem(KUNCI_TOKEN);
    localStorage.removeItem(KUNCI_PENGGUNA);
  },
};

/** Dipanggil saat sesi berakhir, dipasang oleh penyedia autentikasi. */
let saatSesiBerakhir: (() => void) | null = null;
export function pasangPenanganSesiBerakhir(fn: () => void) {
  saatSesiBerakhir = fn;
}

async function permintaan<T>(
  jalur: string,
  opsi: RequestInit = {},
): Promise<T> {
  const token = simpanan.ambilToken();
  const tanggapan = await fetch(`/api${jalur}`, {
    ...opsi,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(opsi.headers ?? {}),
    },
  });

  if (tanggapan.status === 401) {
    simpanan.bersihkan();
    saatSesiBerakhir?.();
    throw new GalatApi("Sesi berakhir. Silakan masuk kembali.", 401);
  }

  if (!tanggapan.ok) {
    let pesan = `Permintaan gagal (${tanggapan.status})`;
    let rincian: unknown;
    try {
      const isi = await tanggapan.json();
      rincian = isi;
      pesan = isi.pesan ?? isi.detail ?? pesan;
      if (typeof pesan !== "string") pesan = JSON.stringify(pesan);
    } catch {
      /* tanggapan bukan JSON; pakai pesan bawaan */
    }
    throw new GalatApi(pesan, tanggapan.status, rincian);
  }

  if (tanggapan.status === 204) return undefined as T;
  return (await tanggapan.json()) as T;
}

export const api = {
  ambil: <T>(jalur: string) => permintaan<T>(jalur),
  kirim: <T>(jalur: string, isi?: unknown) =>
    permintaan<T>(jalur, { method: "POST", body: JSON.stringify(isi ?? {}) }),
};

// ---------------------------------------------------------------------------
// Pembantu penyajian angka
// ---------------------------------------------------------------------------
const formatAngka = new Intl.NumberFormat("id-ID");
const formatRupiah = new Intl.NumberFormat("id-ID", {
  style: "currency",
  currency: "IDR",
  maximumFractionDigits: 0,
});

export const format = {
  angka: (n: number | null | undefined): string =>
    n === null || n === undefined || Number.isNaN(n) ? "–" : formatAngka.format(n),

  rupiah: (n: number | null | undefined): string =>
    n === null || n === undefined || Number.isNaN(n) ? "–" : formatRupiah.format(n),

  /** Rupiah ringkas untuk kartu: 1,2 jt dan 3,4 M. */
  rupiahRingkas: (n: number | null | undefined): string => {
    if (n === null || n === undefined || Number.isNaN(n)) return "–";
    if (Math.abs(n) >= 1_000_000_000) return `Rp${(n / 1_000_000_000).toFixed(1).replace(".", ",")} M`;
    if (Math.abs(n) >= 1_000_000) return `Rp${(n / 1_000_000).toFixed(1).replace(".", ",")} jt`;
    if (Math.abs(n) >= 1_000) return `Rp${(n / 1_000).toFixed(0)} rb`;
    return formatRupiah.format(n);
  },

  persen: (n: number | null | undefined, desimal = 1): string =>
    n === null || n === undefined || Number.isNaN(n)
      ? "–"
      : `${n.toFixed(desimal).replace(".", ",")}%`,

  desimal: (n: number | null | undefined, desimal = 2): string =>
    n === null || n === undefined || Number.isNaN(n)
      ? "–"
      : n.toFixed(desimal).replace(".", ","),

  tanggal: (t: string | null | undefined): string => {
    if (!t) return "–";
    const d = new Date(t);
    if (Number.isNaN(d.getTime())) return t;
    return d.toLocaleDateString("id-ID", { day: "numeric", month: "long", year: "numeric" });
  },
};
