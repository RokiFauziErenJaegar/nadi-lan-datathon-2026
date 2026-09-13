/**
 * Kerangka tata letak: bilah samping, bilah atas, dan wadah isi.
 *
 * Menu disaring menurut kewenangan pengguna. Penyaringan ini kenyamanan, bukan
 * pengamanan - peladen tetap menolak permintaan yang melampaui kewenangan,
 * berapa pun alamat yang diketikkan langsung.
 */

import { useState, type ReactNode } from "react";
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
} from "lucide-react";
import { KEWENANGAN, useAuth } from "../lib/auth";

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

  const menuTampil = MENU.filter((m) => !m.kewenangan || punya(m.kewenangan));

  return (
    <div className="flex min-h-screen bg-slate-50">
      {/* --- Bilah samping --- */}
      <aside
        className={`fixed inset-y-0 left-0 z-40 w-64 transform bg-nadi-900 text-white transition-transform lg:static lg:translate-x-0 ${
          bukaMenu ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="flex h-16 items-center justify-between border-b border-nadi-800 px-5">
          <div>
            <div className="text-lg font-bold tracking-tight">NADI</div>
            <div className="text-2xs text-nadi-300">Navigasi AI Data Intervensi</div>
          </div>
          <button
            className="lg:hidden"
            onClick={() => setBukaMenu(false)}
            aria-label="Tutup menu"
          >
            <X size={20} />
          </button>
        </div>

        <nav className="space-y-0.5 p-3">
          {menuTampil.map((m) => {
            const Ikon = m.ikon;
            return (
              <NavLink
                key={m.ke}
                to={m.ke}
                onClick={() => setBukaMenu(false)}
                title={m.keterangan}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors ${
                    isActive
                      ? "bg-nadi-700 font-medium text-white"
                      : "text-nadi-200 hover:bg-nadi-800 hover:text-white"
                  }`
                }
              >
                <Ikon size={18} />
                {m.label}
              </NavLink>
            );
          })}
        </nav>

        {/* Peringatan data sintetis melekat pada bilah samping, bukan pada satu
            halaman. Ia harus terbaca dari layar mana pun agar tidak ada yang
            keliru menganggap angka ini menggambarkan keluarga sungguhan. */}
        <div className="mx-3 mt-4 rounded-md border border-amber-500/30 bg-amber-500/10 p-3">
          <div className="flex items-start gap-2">
            <AlertTriangle size={14} className="mt-0.5 shrink-0 text-amber-300" />
            <div className="text-2xs leading-relaxed text-amber-100">
              <div className="font-semibold">Data sintetis</div>
              Seluruh data dibangkitkan menyerupai bentuk statistik Kabupaten
              Pringsewu. Tidak ada keluarga nyata di dalamnya.
            </div>
          </div>
        </div>

        <div className="absolute bottom-0 w-full border-t border-nadi-800 p-3">
          <div className="mb-2 px-2">
            <div className="truncate text-sm font-medium">{pengguna?.nama_lengkap}</div>
            <div className="truncate text-2xs text-nadi-300">{pengguna?.label_peran}</div>
            {pengguna?.wilayah_akses?.length ? (
              <div className="mt-1 text-2xs text-amber-300">
                Akses terbatas: {pengguna.wilayah_akses.join(", ")}
              </div>
            ) : null}
          </div>
          <button
            onClick={keluar}
            className="flex w-full items-center gap-2 rounded-md px-2 py-2 text-sm text-nadi-200 hover:bg-nadi-800 hover:text-white"
          >
            <LogOut size={16} />
            Keluar
          </button>
        </div>
      </aside>

      {bukaMenu && (
        <div
          className="fixed inset-0 z-30 bg-black/40 lg:hidden"
          onClick={() => setBukaMenu(false)}
        />
      )}

      {/* --- Isi --- */}
      <div className="flex min-w-0 flex-1 flex-col">
        <header className="sticky top-0 z-20 flex h-16 items-center gap-4 border-b border-slate-200 bg-white px-4 lg:px-6">
          <button
            className="lg:hidden"
            onClick={() => setBukaMenu(true)}
            aria-label="Buka menu"
          >
            <Menu size={22} />
          </button>
          <div className="min-w-0 flex-1">
            <h1 className="truncate text-base font-semibold text-slate-800">
              {menuTampil.find((m) => m.ke === lokasi.pathname)?.label ??
                (lokasi.pathname.startsWith("/keluarga/") ? "Profil Keluarga" : "NADI")}
            </h1>
            <p className="truncate text-xs text-slate-500">
              {menuTampil.find((m) => m.ke === lokasi.pathname)?.keterangan ??
                "Kabupaten Pringsewu, Provinsi Lampung"}
            </p>
          </div>
          <div className="hidden text-right sm:block">
            <div className="text-xs font-medium text-slate-700">Kabupaten Pringsewu</div>
            <div className="text-2xs text-slate-500">Provinsi Lampung</div>
          </div>
        </header>

        <main className="min-w-0 flex-1 p-4 lg:p-6">{children}</main>
      </div>
    </div>
  );
}
