/**
 * Kerangka tata letak: bilah samping, bilah atas, dan wadah isi.
 *
 * Menu disaring menurut kewenangan pengguna. Penyaringan ini kenyamanan, bukan
 * pengamanan - peladen tetap menolak permintaan yang melampaui kewenangan,
 * berapa pun alamat yang diketikkan langsung.
 */

import { useEffect, useRef, useState, type ReactNode } from "react";
import { NavLink, useLocation } from "react-router-dom";
import {
  Settings,
  Activity,
  AlertTriangle,
  BrainCircuit,
  ClipboardList,
  Gauge,
  LayoutDashboard,
  LogOut,
  Map as MapIcon,
  Menu,
  MessageSquareText,
  Package,
  Users,
  X,
  ChevronRight,
  MapPin,
  ShieldCheck,
} from "lucide-react";
import { KEWENANGAN, useAuth } from "../lib/auth";
import PilihanTampilan from "./PilihanTampilan";

interface Butir {
  ke: string;
  label: string;
  ikon: typeof LayoutDashboard;
  kewenangan?: string;
  keterangan: string;
}

const MENU: Butir[] = [
  { ke: "/", label: "Ringkasan", ikon: LayoutDashboard, kewenangan: KEWENANGAN.BACA_AGREGAT, keterangan: "Keadaan kabupaten dalam satu layar" },
  { ke: "/peta", label: "Peta Risiko", ikon: MapIcon, kewenangan: KEWENANGAN.BACA_PETA, keterangan: "Sebaran kerentanan menurut wilayah" },
  { ke: "/antrean", label: "Antrean Kasus", ikon: ClipboardList, kewenangan: KEWENANGAN.BACA_ANTREAN, keterangan: "Kasus yang perlu diperiksa petugas" },
  { ke: "/keluarga", label: "Keluarga", ikon: Users, kewenangan: KEWENANGAN.BACA_KELUARGA, keterangan: "Telusuri profil keluarga" },
  { ke: "/program", label: "Katalog Program", ikon: Package, kewenangan: KEWENANGAN.BACA_REKOMENDASI, keterangan: "Program, kriteria, dan OPD pelaksana" },
  { ke: "/monitoring", label: "Monitoring Hasil", ikon: Activity, kewenangan: KEWENANGAN.BACA_OUTCOME, keterangan: "Capaian intervensi dan kelompok pembandingnya" },
  { ke: "/simulasi", label: "Simulasi", ikon: Gauge, kewenangan: KEWENANGAN.JALANKAN_SIMULASI, keterangan: "Aritmetika cakupan, biaya, dan kapasitas" },
  { ke: "/copilot", label: "Copilot", ikon: MessageSquareText, kewenangan: KEWENANGAN.GUNAKAN_COPILOT, keterangan: "Tanya jawab berbasis pengetahuan sistem" },
  { ke: "/model", label: "Transparansi Model", ikon: BrainCircuit, kewenangan: KEWENANGAN.BACA_AGREGAT, keterangan: "Metrik, keadilan, dan batas kemampuan" },
  { ke: "/pengaturan", label: "Pengaturan AI", ikon: Settings, kewenangan: KEWENANGAN.KELOLA_SISTEM, keterangan: "Pilih penyedia model bahasa" },
];

export default function Tata({ children }: { children: ReactNode }) {
  const { pengguna, keluar, punya } = useAuth();
  const [bukaMenu, setBukaMenu] = useState(false);
  const lokasi = useLocation();
  const tombolMenu = useRef<HTMLButtonElement>(null);
  const panelMenu = useRef<HTMLElement>(null);

  useEffect(() => {
    if (!bukaMenu) return;
    const sebelumnya = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    panelMenu.current?.querySelector<HTMLButtonElement>('button')?.focus();
    const tutup = () => { setBukaMenu(false); tombolMenu.current?.focus(); };
    const tekan = (e: KeyboardEvent) => {
      if (e.key === "Escape") tutup();
      if (e.key === "Tab") {
        const fokus = Array.from(panelMenu.current?.querySelectorAll<HTMLElement>('a[href], button') ?? []);
        const awal = fokus[0];
        const akhir = fokus[fokus.length - 1];
        if (e.shiftKey && document.activeElement === awal) { e.preventDefault(); akhir?.focus(); }
        if (!e.shiftKey && document.activeElement === akhir) { e.preventDefault(); awal?.focus(); }
      }
    };
    const layar = window.matchMedia("(min-width: 1024px)");
    const berubah = () => { if (layar.matches) setBukaMenu(false); };
    window.addEventListener("keydown", tekan);
    layar.addEventListener("change", berubah);
    return () => {
      document.body.style.overflow = sebelumnya;
      window.removeEventListener("keydown", tekan);
      layar.removeEventListener("change", berubah);
    };
  }, [bukaMenu]);

  const menuTampil = MENU.filter((m) => !m.kewenangan || punya(m.kewenangan));

  return (
    <div className="nadi-app flex min-h-screen bg-slate-50">
      <a className="lewati-navigasi" href="#isi-utama">Langsung ke isi</a>
      {/* --- Bilah samping --- */}
      <aside
        ref={panelMenu}
        id="navigasi-utama"
        aria-label="Navigasi utama"
        role={bukaMenu ? "dialog" : undefined}
        aria-modal={bukaMenu || undefined}
        className={`nadi-sidebar fixed inset-y-0 left-0 z-40 w-64 transform bg-nadi-900 text-white transition-transform lg:sticky lg:top-0 lg:translate-x-0 ${
          bukaMenu ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="nadi-brand flex h-16 items-center justify-between border-b border-nadi-800 px-5">
          <div className="flex items-center gap-3">
            <span className="nadi-brand-mark futuristik-saja" aria-hidden="true"><Activity size={25} strokeWidth={1.8} /></span>
            <div>
              <div className="nadi-wordmark text-lg font-bold tracking-tight">NADI<span className="futuristik-saja nadi-brand-dot">.</span></div>
              <div className="nadi-brand-description text-2xs text-nadi-300">Navigasi AI Data Intervensi</div>
            </div>
          </div>
          <button
            className="nadi-icon-button lg:hidden"
            onClick={() => { setBukaMenu(false); tombolMenu.current?.focus(); }}
            aria-label="Tutup menu"
          >
            <X size={20} />
          </button>
        </div>

        <nav className="nadi-navigation space-y-0.5 p-3">
          <div className="nadi-nav-caption futuristik-saja">RUANG KERJA</div>
          {menuTampil.map((m, i) => {
            const Ikon = m.ikon;
            return (
              <div key={m.ke}>
              {m.ke === "/simulasi" && <div className="nadi-nav-caption nadi-nav-caption-secondary futuristik-saja">INTELIJENSI & ANALISIS</div>}
              <NavLink
                to={m.ke}
                onClick={() => {
                  if (bukaMenu) document.getElementById("isi-utama")?.focus();
                  setBukaMenu(false);
                }}
                title={m.keterangan}
                className={({ isActive }) =>
                  `nadi-nav-link flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors ${
                    isActive
                      ? "bg-nadi-700 font-medium text-white"
                      : "text-nadi-200 hover:bg-nadi-800 hover:text-white"
                  }`
                }
              >
                <Ikon size={18} />
                <span className="flex-1">{m.label}</span>
                <span className="nadi-nav-index futuristik-saja" aria-hidden="true">{String(i + 1).padStart(2, "0")}</span>
              </NavLink>
              </div>
            );
          })}
        </nav>

        {/* Peringatan data sintetis melekat pada bilah samping, bukan pada satu
            halaman. Ia harus terbaca dari layar mana pun agar tidak ada yang
            keliru menganggap angka ini menggambarkan keluarga sungguhan. */}
        <div className="nadi-data-note mx-3 mt-4 rounded-md border border-amber-500/30 bg-amber-500/10 p-3">
          <div className="flex items-start gap-2">
            <AlertTriangle size={14} className="mt-0.5 shrink-0 text-amber-300" />
            <div className="text-2xs leading-relaxed text-amber-100">
              <div className="font-semibold">Data sintetis</div>
              Seluruh data dibangkitkan menyerupai bentuk statistik Kabupaten
              Pringsewu. Tidak ada keluarga nyata di dalamnya.
            </div>
          </div>
        </div>

        <div className="nadi-account w-full border-t border-nadi-800 p-3">
          <div className="nadi-user-row mb-2 px-2">
            <div className="nadi-avatar futuristik-saja" aria-hidden="true">{pengguna?.nama_lengkap?.split(/\s+/).slice(0, 2).map(n => n[0]).join("")}</div>
            <div className="min-w-0">
            <div className="truncate text-sm font-medium">{pengguna?.nama_lengkap}</div>
            <div className="truncate text-2xs text-nadi-300">{pengguna?.label_peran}</div>
            {pengguna?.wilayah_akses?.length ? (
              <div className="mt-1 text-2xs text-amber-300">
                Akses terbatas: {pengguna.wilayah_akses.join(", ")}
              </div>
            ) : null}
            </div>
          </div>
          <button
            onClick={keluar}
            className="nadi-logout flex w-full items-center gap-2 rounded-md px-2 py-2 text-sm text-nadi-200 hover:bg-nadi-800 hover:text-white"
          >
            <LogOut size={16} />
            Keluar
          </button>
        </div>
      </aside>

      {bukaMenu && (
        <button
          className="fixed inset-0 z-30 bg-black/40 lg:hidden"
          aria-label="Tutup navigasi"
          tabIndex={-1}
          onClick={() => { setBukaMenu(false); tombolMenu.current?.focus(); }}
        />
      )}

      {/* --- Isi --- */}
      <div className="nadi-workspace flex min-w-0 flex-1 flex-col">
        <header className="nadi-topbar sticky top-0 z-20 flex h-16 items-center gap-4 border-b border-slate-200 bg-white px-4 lg:px-6">
          <button
            ref={tombolMenu}
            className="nadi-icon-button lg:hidden"
            onClick={() => setBukaMenu(true)}
            aria-label="Buka menu"
            aria-expanded={bukaMenu}
            aria-controls="navigasi-utama"
          >
            <Menu size={22} />
          </button>
          <div className="min-w-0 flex-1">
            <div className="nadi-breadcrumb futuristik-saja"><span>Ruang kerja</span><ChevronRight size={11} /></div>
            <h1 className="nadi-page-title truncate text-base font-semibold text-slate-800">
              {menuTampil.find((m) => m.ke === lokasi.pathname)?.label ??
                (lokasi.pathname.startsWith("/keluarga/") ? "Profil Keluarga" : "NADI")}
            </h1>
            <p className="nadi-page-description truncate text-xs text-slate-500">
              {menuTampil.find((m) => m.ke === lokasi.pathname)?.keterangan ??
                "Kabupaten Pringsewu, Provinsi Lampung"}
            </p>
          </div>
          <div className="nadi-region hidden text-right xl:flex">
            <MapPin size={15} className="futuristik-saja" aria-hidden="true" />
            <div>
            <div className="text-xs font-medium text-slate-700">Kabupaten Pringsewu</div>
            <div className="text-2xs text-slate-500">Provinsi Lampung</div>
            </div>
          </div>
          <PilihanTampilan />
        </header>

        <main id="isi-utama" tabIndex={-1} className="nadi-main min-w-0 flex-1 p-4 lg:p-6">{children}</main>
        <footer className="nadi-footer futuristik-saja"><span><ShieldCheck size={13} /> Data sintetis · Untuk demonstrasi</span><span>NADI <span className="nadi-footer-divider">/</span> LAN Datathon 2026</span></footer>
      </div>
    </div>
  );
}
