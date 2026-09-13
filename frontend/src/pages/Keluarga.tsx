/** Penelusuran keluarga menurut wilayah, kategori risiko, dan status bantuan. */

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { Search } from "lucide-react";
import { api, format } from "../lib/api";
import { Galat, Kartu, LencanaRisiko, Memuat, Penafian } from "../components/dasar";

interface Baris {
  kode: string;
  desa: string;
  kecamatan: string;
  desil: number;
  miskin: boolean;
  rasio_garis_kemiskinan: number;
  jumlah_anggota: number;
  jumlah_program: number;
  skor: number | null;
  kategori: string | null;
  perubahan_skor: number | null;
}

export default function Keluarga() {
  const [kategori, setKategori] = useState("");
  const [hanyaMiskin, setHanyaMiskin] = useState(false);
  const [tanpaBantuan, setTanpaBantuan] = useState(false);

  const pertanyaan = new URLSearchParams({ batas: "60" });
  if (kategori) pertanyaan.set("kategori", kategori);
  if (hanyaMiskin) pertanyaan.set("hanya_miskin", "true");
  if (tanpaBantuan) pertanyaan.set("tanpa_bantuan", "true");

  const { data, isLoading, error } = useQuery({
    queryKey: ["cari-keluarga", kategori, hanyaMiskin, tanpaBantuan],
    queryFn: () => api.ambil<{ keluarga: Baris[]; jumlah: number }>(`/keluarga/cari?${pertanyaan}`),
  });

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-center gap-2">
        <span className="flex items-center gap-1.5 text-xs font-medium text-slate-500">
          <Search size={14} /> Penyaring
        </span>
        <select
          value={kategori}
          onChange={(e) => setKategori(e.target.value)}
          className="rounded-md border border-slate-300 px-3 py-1.5 text-xs"
        >
          <option value="">Semua kategori risiko</option>
          <option value="sangat_tinggi">Risiko sangat tinggi</option>
          <option value="tinggi">Risiko tinggi</option>
          <option value="sedang">Risiko sedang</option>
          <option value="rendah">Risiko rendah</option>
        </select>
        {[
          ["Hanya yang miskin", hanyaMiskin, setHanyaMiskin] as const,
          ["Tidak menerima bantuan", tanpaBantuan, setTanpaBantuan] as const,
        ].map(([label, nilai, setter]) => (
          <button
            key={label}
            onClick={() => setter(!nilai)}
            className={`rounded-md px-3 py-1.5 text-xs font-medium ${
              nilai ? "bg-nadi-700 text-white" : "border border-slate-300 bg-white text-slate-700"
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {isLoading ? (
        <Memuat pesan="Mencari keluarga..." />
      ) : error ? (
        <Galat pesan={(error as Error).message} />
      ) : (
        <Kartu
          judul={`${format.angka(data?.jumlah ?? 0)} keluarga ditampilkan`}
          keterangan="Diurutkan menurut skor kerentanan tertinggi"
          padat
        >
          <div className="overflow-x-auto">
            <table className="w-full min-w-[760px] text-sm">
              <thead>
                <tr className="border-b border-slate-200 text-left text-2xs uppercase tracking-wide text-slate-500">
                  <th className="px-4 py-2 font-medium">Kode</th>
                  <th className="px-3 py-2 font-medium">Wilayah</th>
                  <th className="px-3 py-2 text-right font-medium">Desil</th>
                  <th className="px-3 py-2 text-right font-medium">Rasio GK</th>
                  <th className="px-3 py-2 text-right font-medium">Anggota</th>
                  <th className="px-3 py-2 text-right font-medium">Program</th>
                  <th className="px-3 py-2 font-medium">Risiko</th>
                  <th className="px-4 py-2 text-right font-medium">Perubahan</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {data?.keluarga.map((k) => (
                  <tr key={k.kode} className="hover:bg-slate-50">
                    <td className="px-4 py-2">
                      <Link
                        to={`/keluarga/${k.kode}`}
                        className="font-mono text-xs font-medium text-nadi-700 hover:text-nadi-900"
                      >
                        {k.kode}
                      </Link>
                    </td>
                    <td className="px-3 py-2">
                      <div className="text-xs text-slate-700">{k.desa}</div>
                      <div className="text-2xs text-slate-400">Kec. {k.kecamatan}</div>
                    </td>
                    <td className="angka px-3 py-2 text-right text-slate-700">{k.desil}</td>
                    <td className="angka px-3 py-2 text-right">
                      <span className={k.miskin ? "font-semibold text-red-700" : "text-slate-700"}>
                        {format.desimal(k.rasio_garis_kemiskinan, 2)}
                      </span>
                    </td>
                    <td className="angka px-3 py-2 text-right text-slate-600">{k.jumlah_anggota}</td>
                    <td className="angka px-3 py-2 text-right">
                      <span
                        className={
                          k.jumlah_program === 0 ? "font-semibold text-amber-700" : "text-slate-600"
                        }
                      >
                        {k.jumlah_program}
                      </span>
                    </td>
                    <td className="px-3 py-2">
                      <LencanaRisiko kategori={k.kategori} skor={k.skor} ukuran="kecil" />
                    </td>
                    <td className="angka px-4 py-2 text-right text-xs">
                      {k.perubahan_skor === null ? (
                        <span className="text-slate-300">–</span>
                      ) : (
                        <span
                          className={
                            k.perubahan_skor > 5
                              ? "font-semibold text-red-700"
                              : k.perubahan_skor < -5
                                ? "font-semibold text-emerald-700"
                                : "text-slate-500"
                          }
                        >
                          {k.perubahan_skor > 0 ? "+" : ""}
                          {format.desimal(k.perubahan_skor, 1)}
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Kartu>
      )}

      <Penafian judul="Identitas keluarga">
        Sistem ini tidak menyimpan nama, nomor induk kependudukan, maupun alamat.
        Yang beredar hanyalah kode semu yang tidak dapat dibalik menjadi
        identitas tanpa kunci rahasia. Setiap pembukaan profil keluarga tercatat
        pada jejak audit beserta pelakunya.
      </Penafian>
    </div>
  );
}
