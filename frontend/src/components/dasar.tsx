/**
 * Komponen dasar yang dipakai berulang di seluruh layar.
 *
 * Yang paling menentukan di sini adalah `LencanaRisiko`. Ia selalu menampilkan
 * ikon, tulisan, DAN warna sekaligus - tidak pernah warna saja. Dua dari empat
 * kategori risiko memang berkontras rendah pada latar terang, dan itu memang
 * disengaja: warna berperan sebagai penguat, sementara maknanya ditanggung ikon
 * dan tulisan. Dengan begitu tingkat risiko tetap terbaca oleh siapa pun,
 * termasuk pembaca dengan buta warna dan pada hasil cetak hitam putih.
 */

import {
  AlertCircle,
  CircleAlert,
  CircleCheck,
  Info,
  Loader2,
  OctagonAlert,
  TriangleAlert,
  X,
  type LucideIcon,
} from "lucide-react";
import { useEffect, type ReactNode } from "react";
import { LABEL_RISIKO, WARNA_RISIKO, type KategoriRisiko } from "../lib/warna";

// ---------------------------------------------------------------------------
export function Memuat({ pesan = "Memuat...", penuh = false }: { pesan?: string; penuh?: boolean }) {
  const isi = (
    <div className="flex items-center gap-3 text-sm text-slate-500">
      <Loader2 className="animate-spin" size={18} />
      {pesan}
    </div>
  );
  return penuh ? (
    <div className="flex min-h-screen items-center justify-center bg-slate-50">{isi}</div>
  ) : (
    <div className="flex items-center justify-center py-12">{isi}</div>
  );
}

// ---------------------------------------------------------------------------
export function Galat({ pesan, judul = "Tidak dapat memuat data" }: { pesan: string; judul?: string }) {
  return (
    <div className="rounded-lg border border-red-200 bg-red-50 p-4">
      <div className="flex items-start gap-3">
        <AlertCircle size={18} className="mt-0.5 shrink-0 text-red-600" />
        <div>
          <div className="text-sm font-semibold text-red-800">{judul}</div>
          <div className="mt-1 text-sm leading-relaxed text-red-700">{pesan}</div>
        </div>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
const IKON: Record<KategoriRisiko, LucideIcon> = {
  rendah: CircleCheck,
  sedang: CircleAlert,
  tinggi: TriangleAlert,
  sangat_tinggi: OctagonAlert,
};

/** Latar lembut sepadan tiap kategori, agar lencana tetap terbaca. */
const LATAR: Record<KategoriRisiko, string> = {
  rendah: "bg-emerald-50 text-emerald-900 border-emerald-200",
  sedang: "bg-amber-50 text-amber-900 border-amber-200",
  tinggi: "bg-orange-50 text-orange-900 border-orange-200",
  sangat_tinggi: "bg-red-50 text-red-900 border-red-200",
};

export function LencanaRisiko({
  kategori,
  skor,
  ukuran = "sedang",
}: {
  kategori: KategoriRisiko | string | null | undefined;
  skor?: number | null;
  ukuran?: "kecil" | "sedang";
}) {
  const k = (kategori ?? "rendah") as KategoriRisiko;
  const Ikon = IKON[k] ?? CircleCheck;
  const kelas = LATAR[k] ?? LATAR.rendah;
  const kecil = ukuran === "kecil";

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border font-medium ${kelas} ${
        kecil ? "px-2 py-0.5 text-2xs" : "px-2.5 py-1 text-xs"
      }`}
      title={LABEL_RISIKO[k]}
    >
      <Ikon size={kecil ? 11 : 13} style={{ color: WARNA_RISIKO[k] }} />
      <span>{LABEL_RISIKO[k]}</span>
      {skor !== null && skor !== undefined && (
        <span className="angka font-semibold">{Math.round(skor)}</span>
      )}
    </span>
  );
}

// ---------------------------------------------------------------------------
export function KartuStat({
  label,
  nilai,
  satuan,
  keterangan,
  ikon: Ikon,
  nada = "netral",
  bawah,
}: {
  label: string;
  nilai: ReactNode;
  satuan?: string;
  keterangan?: string;
  ikon?: LucideIcon;
  nada?: "netral" | "perhatian" | "genting" | "baik";
  bawah?: ReactNode;
}) {
  const warnaNada = {
    netral: "text-slate-900",
    baik: "text-emerald-700",
    perhatian: "text-amber-700",
    genting: "text-red-700",
  }[nada];

  return (
    <div className={`kartu kartu-stat kartu-stat-${nada} p-4`}>
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0">
          <div className="kartu-stat-label text-xs font-medium text-slate-500">{label}</div>
          <div className={`kartu-stat-nilai angka mt-1 text-2xl font-bold leading-tight ${warnaNada}`}>
            {nilai}
            {satuan && <span className="ml-1 text-sm font-medium text-slate-400">{satuan}</span>}
          </div>
        </div>
        {Ikon && <span className="kartu-stat-ikon"><Ikon size={20} className="shrink-0 text-slate-300" /></span>}
      </div>
      {keterangan && (
        <p className="kartu-stat-keterangan mt-2 text-xs leading-relaxed text-slate-500">{keterangan}</p>
      )}
      {bawah && <div className="mt-3 border-t border-slate-100 pt-3">{bawah}</div>}
    </div>
  );
}

// ---------------------------------------------------------------------------
export function Penafian({ children, judul }: { children: ReactNode; judul?: string }) {
  return (
    <div className="penafian">
      <div className="flex items-start gap-2">
        <Info size={13} className="mt-0.5 shrink-0 text-slate-400" />
        <div>
          {judul && <div className="mb-0.5 font-semibold text-slate-700">{judul}</div>}
          {children}
        </div>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
export function Kartu({
  judul,
  keterangan,
  aksi,
  children,
  padat = false,
}: {
  judul?: string;
  keterangan?: string;
  aksi?: ReactNode;
  children: ReactNode;
  padat?: boolean;
}) {
  return (
    <section className="kartu">
      {judul && (
        <header className="flex items-start justify-between gap-3 border-b border-slate-100 px-4 py-3">
          <div className="min-w-0">
            <h2 className="text-sm font-semibold text-slate-700">{judul}</h2>
            {keterangan && (
              <p className="mt-0.5 text-xs leading-relaxed text-slate-500">{keterangan}</p>
            )}
          </div>
          {aksi && <div className="shrink-0">{aksi}</div>}
        </header>
      )}
      <div className={padat ? "" : "p-4"}>{children}</div>
    </section>
  );
}

// ---------------------------------------------------------------------------
/**
 * Jendela bertumpuk untuk satu keputusan kecil.
 *
 * Dibuat di sini, bukan dipungut dari pustaka luar, karena seluruh antarmuka
 * ini menolak ketergantungan yang tidak benar-benar dibutuhkan - dan yang
 * dibutuhkan hanyalah tirai, satu kotak, serta tombol tutup.
 *
 * Tirainya menutup jendela ketika diklik, sementara kotaknya menahan klik agar
 * tidak menutup diri sendiri. Tombol Escape juga menutup, karena orang yang
 * ragu akan menekan Escape lebih dahulu sebelum mencari tombol batal.
 */
export function Jendela({
  judul,
  keterangan,
  onTutup,
  children,
  aksi,
}: {
  judul: string;
  keterangan?: string;
  onTutup: () => void;
  children: ReactNode;
  aksi?: ReactNode;
}) {
  useEffect(() => {
    const tekan = (e: KeyboardEvent) => {
      if (e.key === "Escape") onTutup();
    };
    window.addEventListener("keydown", tekan);
    // Halaman di belakang tidak boleh ikut bergulir saat jendela terbuka.
    const semula = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      window.removeEventListener("keydown", tekan);
      document.body.style.overflow = semula;
    };
  }, [onTutup]);

  return (
    <div
      className="fixed inset-0 z-40 flex items-end justify-center bg-slate-900/40 p-0 sm:items-center sm:p-4"
      onClick={onTutup}
      role="presentation"
    >
      <div
        className="shadow-naik w-full max-w-lg rounded-t-xl bg-white sm:rounded-xl"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-label={judul}
      >
        <header className="flex items-start justify-between gap-3 border-b border-slate-100 px-4 py-3">
          <div className="min-w-0">
            <h2 className="text-sm font-semibold text-slate-700">{judul}</h2>
            {keterangan && (
              <p className="mt-0.5 text-xs leading-relaxed text-slate-500">{keterangan}</p>
            )}
          </div>
          <button
            type="button"
            onClick={onTutup}
            aria-label="Tutup"
            className="shrink-0 rounded p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-600"
          >
            <X size={16} />
          </button>
        </header>
        <div className="p-4">{children}</div>
        {aksi && (
          <footer className="flex justify-end gap-2 border-t border-slate-100 px-4 py-3">{aksi}</footer>
        )}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
/** Lencana tingkat keyakinan sebuah angka. */
export function LencanaKeyakinan({ tingkat }: { tingkat: string | null | undefined }) {
  const peta: Record<string, { label: string; kelas: string }> = {
    pasti: { label: "Sumber resmi", kelas: "bg-emerald-50 text-emerald-800 border-emerald-200" },
    cukup_kuat: { label: "Cukup kuat", kelas: "bg-sky-50 text-sky-800 border-sky-200" },
    perkiraan: { label: "Perkiraan", kelas: "bg-amber-50 text-amber-900 border-amber-200" },
    tidak_ditemukan: { label: "Belum ada sumber", kelas: "bg-slate-100 text-slate-700 border-slate-200" },
  };
  const t = peta[tingkat ?? ""] ?? peta.cukup_kuat;
  return (
    <span className={`lencana border ${t.kelas}`} title="Kekuatan sumber angka ini">
      {t.label}
    </span>
  );
}

export default Memuat;
