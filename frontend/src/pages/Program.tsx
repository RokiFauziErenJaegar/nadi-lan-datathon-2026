/**
 * Katalog program dan faktor risiko.
 *
 * Setiap nominal membawa lencana tingkat keyakinannya. Sistem yang menampilkan
 * seluruh angka dengan nada sama meyakinkan akan kehilangan kepercayaan
 * penggunanya begitu satu angka terbukti keliru; menandai mana yang bersumber
 * peraturan dan mana yang masih perkiraan justru menjaga kepercayaan itu.
 */

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Building2, Landmark, Package } from "lucide-react";
import { api, format } from "../lib/api";
import { Galat, Kartu, LencanaKeyakinan, Memuat, Penafian } from "../components/dasar";

interface ProgramItem {
  kode: string;
  nama: string;
  singkatan: string;
  deskripsi: string | null;
  jenis_intervensi: string;
  kementerian: string | null;
  opd: string[];
  tindakan_daerah: string | null;
  sumber_dana: string;
  frekuensi: string;
  desil_min: number | null;
  desil_maks: number | null;
  biaya_satuan_tahunan: number | null;
  kuota_tahunan: number | null;
  status: string;
  tingkat_keyakinan: string;
  dasar_hukum: string[];
  catatan: string | null;
  faktor_risiko: { kode: string; nama: string }[];
  manfaat: { komponen: string; label: string; nominal_per_tahun: number | null; satuan: string; tingkat_keyakinan: string }[];
  jumlah_aturan: number;
}

interface FaktorItem {
  kode: string;
  nama: string;
  deskripsi: string | null;
  dimensi: string;
  indikator: string | null;
  bobot_dasar: number;
  terdeteksi_otomatis: boolean;
  program: { singkatan: string; kekuatan: number }[];
}

export default function Program() {
  const [tab, setTab] = useState<"program" | "faktor">("program");
  const [terbuka, setTerbuka] = useState<string | null>(null);

  const program = useQuery({
    queryKey: ["katalog-program"],
    queryFn: () => api.ambil<{ program: ProgramItem[]; catatan: string }>("/rekomendasi/program"),
  });
  const faktor = useQuery({
    queryKey: ["katalog-faktor"],
    queryFn: () => api.ambil<{ faktor: FaktorItem[] }>("/rekomendasi/faktor-risiko"),
    enabled: tab === "faktor",
  });

  return (
    <div className="space-y-5">
      <div className="flex gap-2">
        {(
          [
            ["program", "Katalog program", Package],
            ["faktor", "Faktor risiko", Landmark],
          ] as const
        ).map(([nilai, label, Ikon]) => (
          <button
            key={nilai}
            onClick={() => setTab(nilai)}
            className={`flex items-center gap-1.5 rounded-md px-3 py-1.5 text-xs font-medium ${
              tab === nilai ? "bg-nadi-700 text-white" : "border border-slate-300 bg-white text-slate-700"
            }`}
          >
            <Ikon size={14} /> {label}
          </button>
        ))}
      </div>

      {tab === "program" ? (
        program.isLoading ? (
          <Memuat pesan="Memuat katalog program..." />
        ) : program.error ? (
          <Galat pesan={(program.error as Error).message} />
        ) : (
          <>
            <Kartu
              judul={`${program.data?.program.length} program pada basis pengetahuan`}
              keterangan="Dapat dipelihara petugas dinas tanpa mengubah kode aplikasi"
              padat
            >
              <ul className="divide-y divide-slate-100">
                {program.data?.program.map((p) => {
                  const buka = terbuka === p.kode;
                  return (
                    <li key={p.kode}>
                      <button
                        onClick={() => setTerbuka(buka ? null : p.kode)}
                        className="flex w-full items-start gap-3 px-4 py-3 text-left hover:bg-slate-50"
                      >
                        <div className="min-w-0 flex-1">
                          <div className="flex flex-wrap items-center gap-2">
                            <span className="text-sm font-semibold text-slate-800">{p.singkatan}</span>
                            <LencanaKeyakinan tingkat={p.tingkat_keyakinan} />
                            {p.status !== "aktif" && (
                              <span className="lencana border border-amber-200 bg-amber-50 text-amber-900">
                                status belum pasti
                              </span>
                            )}
                          </div>
                          <div className="mt-0.5 text-xs text-slate-600">{p.nama}</div>
                          <div className="mt-1 flex flex-wrap items-center gap-3 text-2xs text-slate-500">
                            <span className="flex items-center gap-1">
                              <Building2 size={10} /> {p.opd.join(", ") || "belum ditetapkan"}
                            </span>
                            <span>desil {p.desil_min}–{p.desil_maks}</span>
                            <span>{p.sumber_dana.replace(/_/g, " ").toUpperCase()}</span>
                            {p.biaya_satuan_tahunan ? (
                              <span className="angka">
                                {format.rupiahRingkas(p.biaya_satuan_tahunan)}/penerima/tahun
                              </span>
                            ) : null}
                            <span>{p.jumlah_aturan} aturan kelayakan</span>
                          </div>
                        </div>
                      </button>

                      {buka && (
                        <div className="space-y-3 border-t border-slate-100 bg-slate-50 px-4 py-3">
                          {p.deskripsi && (
                            <p className="text-xs leading-relaxed text-slate-700">{p.deskripsi}</p>
                          )}

                          {p.manfaat.length > 0 && (
                            <div>
                              <div className="mb-1.5 text-2xs font-semibold uppercase tracking-wide text-slate-500">
                                Komponen manfaat
                              </div>
                              <div className="space-y-1">
                                {p.manfaat.map((m) => (
                                  <div
                                    key={m.komponen}
                                    className="flex items-center justify-between gap-3 rounded border border-slate-200 bg-white px-2.5 py-1.5"
                                  >
                                    <span className="text-xs text-slate-700">{m.label}</span>
                                    <span className="flex items-center gap-2">
                                      <span className="angka text-xs font-semibold text-slate-800">
                                        {m.satuan === "rupiah" && m.nominal_per_tahun
                                          ? `${format.rupiah(m.nominal_per_tahun)}/tahun`
                                          : m.nominal_per_tahun
                                            ? `${format.angka(m.nominal_per_tahun)} ${m.satuan}`
                                            : m.satuan}
                                      </span>
                                      <LencanaKeyakinan tingkat={m.tingkat_keyakinan} />
                                    </span>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}

                          <div className="flex flex-wrap gap-1.5">
                            {p.faktor_risiko.map((f) => (
                              <span
                                key={f.kode}
                                title={f.nama}
                                className="lencana border border-nadi-200 bg-nadi-50 text-nadi-800"
                              >
                                <span className="font-mono">{f.kode}</span> {f.nama.slice(0, 30)}
                              </span>
                            ))}
                          </div>

                          {p.dasar_hukum.length > 0 && (
                            <div className="text-2xs text-slate-500">
                              Dasar hukum: {p.dasar_hukum.join("; ")}
                            </div>
                          )}
                          {p.catatan && (
                            <p className="rounded border border-slate-200 bg-white p-2 text-2xs leading-relaxed text-slate-600">
                              {p.catatan}
                            </p>
                          )}
                          <div className="text-2xs text-slate-500">
                            Tindakan yang dapat dilakukan daerah:{" "}
                            <span className="font-medium text-slate-700">{p.tindakan_daerah}</span>
                          </div>
                        </div>
                      )}
                    </li>
                  );
                })}
              </ul>
            </Kartu>
            <Penafian judul="Tentang angka pada katalog">{program.data?.catatan}</Penafian>
          </>
        )
      ) : faktor.isLoading ? (
        <Memuat pesan="Memuat faktor risiko..." />
      ) : (
        <Kartu
          judul={`${faktor.data?.faktor.length} faktor risiko`}
          keterangan="Kosakata bersama yang menyambungkan penjelasan model dengan rekomendasi program"
          padat
        >
          <ul className="divide-y divide-slate-100">
            {faktor.data?.faktor.map((f) => (
              <li key={f.kode} className="px-4 py-3">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="font-mono text-xs font-bold text-nadi-700">{f.kode}</span>
                  <span className="text-sm font-medium text-slate-800">{f.nama}</span>
                  <span className="lencana border border-slate-200 bg-slate-50 text-slate-600">
                    {f.dimensi.replace(/_/g, " ")}
                  </span>
                  <span className="angka text-2xs text-slate-500">bobot {f.bobot_dasar}</span>
                  {!f.terdeteksi_otomatis && (
                    <span className="lencana border border-amber-200 bg-amber-50 text-amber-900">
                      hanya penandaan manual
                    </span>
                  )}
                </div>
                {f.deskripsi && (
                  <p className="mt-1 text-xs leading-relaxed text-slate-600">{f.deskripsi}</p>
                )}
                {f.indikator && (
                  <p className="mt-1 text-2xs leading-relaxed text-slate-500">
                    <span className="font-medium">Cara dikenali:</span> {f.indikator}
                  </p>
                )}
                {f.program.length > 0 && (
                  <div className="mt-1.5 flex flex-wrap gap-1">
                    {f.program.map((p) => (
                      <span key={p.singkatan} className="lencana border border-slate-200 bg-white text-slate-700">
                        {p.singkatan}
                      </span>
                    ))}
                  </div>
                )}
              </li>
            ))}
          </ul>
        </Kartu>
      )}
    </div>
  );
}
