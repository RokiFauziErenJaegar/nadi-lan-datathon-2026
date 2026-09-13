/**
 * Mismatch & Anomaly Queue.
 *
 * Urutan bawaan menempatkan kasus keluarga yang terlewat lebih dahulu, dan itu
 * pilihan yang disengaja: kesalahan memasukkan orang yang tidak berhak
 * membebani anggaran, sedangkan kesalahan melewatkan orang yang berhak
 * membebani keluarga itu sendiri - dan mereka tidak muncul di daftar mana pun
 * untuk mengeluh.
 */

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { ChevronDown, ChevronRight, Filter, MapPin, ShieldQuestion } from "lucide-react";
import { api, format } from "../lib/api";
import { Galat, Kartu, LencanaRisiko, Memuat, Penafian } from "../components/dasar";

interface Alasan {
  kode: string;
  ringkasan: string;
  bukti: Record<string, unknown>;
  keyakinan: string;
}

interface Kasus {
  kode: string;
  kode_keluarga: string;
  jenis: string;
  label_jenis: string;
  status: string;
  label_status: string;
  skor_prioritas: number;
  tingkat_prioritas: number;
  ringkasan: string;
  alasan: Alasan[];
  sumber_deteksi: string;
  desa: string;
  kecamatan: string;
  opd_ditugaskan: string | null;
  keluarga: {
    skor: number | null;
    kategori: string | null;
    desil: number | null;
    jumlah_anggota: number | null;
    jumlah_program: number | null;
  };
}

interface DataAntrean {
  gelombang: number;
  jumlah_ditampilkan: number;
  kasus: Kasus[];
  rekap: { jenis: string; label: string; status: string; jumlah: number }[];
  catatan: string;
}

const WARNA_PRIORITAS: Record<number, string> = {
  1: "bg-red-100 text-red-800 border-red-200",
  2: "bg-orange-100 text-orange-800 border-orange-200",
  3: "bg-amber-100 text-amber-900 border-amber-200",
  4: "bg-slate-100 text-slate-700 border-slate-200",
  5: "bg-slate-100 text-slate-600 border-slate-200",
};

const WARNA_KEYAKINAN: Record<string, string> = {
  tinggi: "text-emerald-700",
  sedang: "text-amber-700",
  rendah: "text-slate-500",
};

export default function Antrean() {
  const [jenis, setJenis] = useState<string>("");
  const [prioritas, setPrioritas] = useState(5);
  const [terbuka, setTerbuka] = useState<string | null>(null);

  const { data, isLoading, error } = useQuery({
    queryKey: ["antrean", jenis, prioritas],
    queryFn: () =>
      api.ambil<DataAntrean>(
        `/antrean?batas=60&prioritas_maksimum=${prioritas}${jenis ? `&jenis=${jenis}` : ""}`,
      ),
  });

  if (isLoading) return <Memuat pesan="Memuat antrean kasus..." />;
  if (error) return <Galat pesan={(error as Error).message} />;

  const d = data!;
  const rekapJenis = Object.values(
    d.rekap.reduce<Record<string, { jenis: string; label: string; jumlah: number }>>((a, r) => {
      a[r.jenis] = a[r.jenis] ?? { jenis: r.jenis, label: r.label, jumlah: 0 };
      a[r.jenis].jumlah += r.jumlah;
      return a;
    }, {}),
  ).sort((a, b) => b.jumlah - a.jumlah);

  return (
    <div className="space-y-5">
      {/* Penyaring dalam satu baris */}
      <div className="flex flex-wrap items-center gap-2">
        <span className="flex items-center gap-1.5 text-xs font-medium text-slate-500">
          <Filter size={14} /> Jenis kasus
        </span>
        <button
          onClick={() => setJenis("")}
          className={`rounded-md px-3 py-1.5 text-xs font-medium ${
            jenis === "" ? "bg-nadi-700 text-white" : "border border-slate-300 bg-white text-slate-700"
          }`}
        >
          Semua ({rekapJenis.reduce((a, b) => a + b.jumlah, 0)})
        </button>
        {rekapJenis.map((r) => (
          <button
            key={r.jenis}
            onClick={() => setJenis(r.jenis)}
            title={r.label}
            className={`rounded-md px-3 py-1.5 text-xs font-medium ${
              jenis === r.jenis
                ? "bg-nadi-700 text-white"
                : "border border-slate-300 bg-white text-slate-700 hover:bg-slate-50"
            }`}
          >
            {r.label.length > 34 ? `${r.label.slice(0, 34)}…` : r.label} ({r.jumlah})
          </button>
        ))}
        <span className="ml-auto flex items-center gap-2 text-xs text-slate-500">
          Prioritas sampai
          <select
            value={prioritas}
            onChange={(e) => setPrioritas(Number(e.target.value))}
            className="rounded-md border border-slate-300 px-2 py-1 text-xs"
          >
            {[1, 2, 3, 4, 5].map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </select>
        </span>
      </div>

      <Kartu
        judul={`${format.angka(d.jumlah_ditampilkan)} kasus ditampilkan`}
        keterangan="Diurutkan menurut prioritas. Kasus keluarga yang terlewat ditempatkan lebih dahulu."
        padat
      >
        <ul className="divide-y divide-slate-100">
          {d.kasus.map((k) => {
            const buka = terbuka === k.kode;
            return (
              <li key={k.kode}>
                <button
                  onClick={() => setTerbuka(buka ? null : k.kode)}
                  className="flex w-full items-start gap-3 px-4 py-3 text-left hover:bg-slate-50"
                >
                  <span
                    className={`mt-0.5 shrink-0 rounded border px-1.5 py-0.5 text-2xs font-bold ${
                      WARNA_PRIORITAS[k.tingkat_prioritas]
                    }`}
                    title={`Tingkat prioritas ${k.tingkat_prioritas}`}
                  >
                    P{k.tingkat_prioritas}
                  </span>

                  <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="text-sm font-medium text-slate-800">{k.label_jenis}</span>
                      {k.keluarga.kategori && (
                        <LencanaRisiko
                          kategori={k.keluarga.kategori}
                          skor={k.keluarga.skor}
                          ukuran="kecil"
                        />
                      )}
                      {k.sumber_deteksi === "statistik" && (
                        <span className="lencana border border-slate-200 bg-slate-50 text-slate-600">
                          <ShieldQuestion size={10} /> pencilan statistik
                        </span>
                      )}
                    </div>
                    <p className="mt-1 text-xs leading-relaxed text-slate-600">{k.ringkasan}</p>
                    <div className="mt-1.5 flex flex-wrap items-center gap-3 text-2xs text-slate-500">
                      <span className="flex items-center gap-1">
                        <MapPin size={10} /> {k.desa}, Kec. {k.kecamatan}
                      </span>
                      <span className="font-mono">{k.kode_keluarga}</span>
                      {k.opd_ditugaskan && (
                        <span className="rounded bg-nadi-50 px-1.5 py-0.5 font-medium text-nadi-800">
                          {k.opd_ditugaskan}
                        </span>
                      )}
                      <span>desil {k.keluarga.desil}</span>
                      <span>{k.keluarga.jumlah_program} program</span>
                    </div>
                  </div>

                  <span className="shrink-0 text-slate-400">
                    {buka ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
                  </span>
                </button>

                {buka && (
                  <div className="border-t border-slate-100 bg-slate-50 px-4 py-3">
                    <div className="mb-2 text-2xs font-semibold uppercase tracking-wide text-slate-500">
                      Bukti yang mendasari penandaan
                    </div>
                    <ul className="space-y-2">
                      {k.alasan.map((a, i) => (
                        <li key={i} className="rounded-md border border-slate-200 bg-white p-2.5">
                          <div className="flex items-start justify-between gap-3">
                            <span className="text-xs leading-relaxed text-slate-700">
                              {a.ringkasan}
                            </span>
                            <span
                              className={`shrink-0 text-2xs font-medium ${
                                WARNA_KEYAKINAN[a.keyakinan] ?? "text-slate-500"
                              }`}
                            >
                              keyakinan {a.keyakinan}
                            </span>
                          </div>
                          {a.bukti && Object.keys(a.bukti).length > 0 && (
                            <div className="angka mt-1.5 flex flex-wrap gap-x-4 gap-y-1 text-2xs text-slate-500">
                              {Object.entries(a.bukti).map(([nk, nv]) => (
                                <span key={nk}>
                                  {nk.replace(/_/g, " ")}:{" "}
                                  <span className="font-semibold text-slate-700">
                                    {typeof nv === "number" ? format.desimal(nv, 2) : String(nv)}
                                  </span>
                                </span>
                              ))}
                            </div>
                          )}
                        </li>
                      ))}
                    </ul>
                    <div className="mt-3 flex flex-wrap gap-2">
                      <Link to={`/keluarga/${k.kode_keluarga}`} className="tombol-utama text-xs">
                        Buka profil keluarga
                      </Link>
                      <span className="self-center text-2xs text-slate-500">
                        Kode kasus <span className="font-mono">{k.kode}</span> · status{" "}
                        {k.label_status}
                      </span>
                    </div>
                  </div>
                )}
              </li>
            );
          })}
        </ul>
      </Kartu>

      <Penafian judul="Kasus bukan keputusan">{d.catatan}</Penafian>
    </div>
  );
}
