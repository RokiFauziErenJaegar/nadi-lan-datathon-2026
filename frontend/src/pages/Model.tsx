/**
 * Transparansi model.
 *
 * Bagian terpenting pada layar ini bukan angka keberhasilannya, melainkan
 * daftar hal yang TIDAK dapat dilakukan sistem ini. Sistem yang hanya
 * menampilkan kelebihannya menuntut kepercayaan; sistem yang menyebutkan
 * batasnya justru layak dipercaya.
 */

import { useQuery } from "@tanstack/react-query";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Ban, CheckCircle2, ShieldAlert, Scale } from "lucide-react";
import { api, format } from "../lib/api";
import { TINTA } from "../lib/warna";
import { Galat, Kartu, KartuStat, Memuat, Penafian } from "../components/dasar";

export default function Model() {
  const aktif = useQuery({ queryKey: ["model-aktif"], queryFn: () => api.ambil<any>("/model/aktif") });
  const batas = useQuery({ queryKey: ["model-batas"], queryFn: () => api.ambil<any>("/model/batas") });
  const fitur = useQuery({ queryKey: ["model-fitur"], queryFn: () => api.ambil<any>("/model/fitur") });

  if (aktif.isLoading) return <Memuat pesan="Memuat keterangan model..." />;
  if (aktif.error) return <Galat pesan={(aktif.error as Error).message} />;

  const m = aktif.data;
  const anggaran = Object.entries(m.metrik?.pada_anggaran ?? {})
    .map(([k, v]: [string, any]) => ({ k: Number(k), ...v }))
    .sort((a, b) => a.k - b.k);
  const kepentingan = (m.fitur_paling_berpengaruh ?? []).slice(0, 10).map((f: any) => ({
    nama: f.label.length > 34 ? `${f.label.slice(0, 34)}…` : f.label,
    nilai: f.kepentingan_persen,
  }));
  const keadilanKec = m.keadilan?.kecamatan ?? [];

  return (
    <div className="space-y-5">
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <KartuStat
          label="AUC pada gelombang penguji"
          nilai={format.desimal(m.metrik?.auc, 3)}
          keterangan="Kajian lintas negara menempatkan batas atas yang wajar sekitar 0,85 bahkan untuk proxy means test yang terkalibrasi sempurna"
          nada={m.metrik?.auc > 0.9 ? "genting" : "baik"}
        />
        <KartuStat
          label="Galat kalibrasi"
          nilai={format.desimal(m.metrik?.kalibrasi?.ece, 4)}
          keterangan="Selisih rata-rata antara peluang yang ditampilkan dan kejadian yang benar-benar teramati"
          nada="baik"
        />
        <KartuStat
          label="Presisi pada 300 kunjungan"
          nilai={format.persen((anggaran.find((a) => a.k === 300)?.presisi ?? 0) * 100, 1)}
          keterangan={`${format.desimal(anggaran.find((a) => a.k === 300)?.pengganda, 2)}× lebih baik daripada memeriksa acak`}
        />
        <KartuStat
          label="Fitur dipakai"
          nilai={m.jumlah_fitur}
          keterangan={`Dilatih pada ${format.angka(m.jumlah_baris_latih)} baris, gelombang ${JSON.stringify(m.gelombang_latih)}`}
        />
      </div>

      {/* Anggaran verifikasi */}
      <Kartu
        judul="Kinerja pada anggaran verifikasi"
        keterangan="Metrik utama sistem ini bukan akurasi, melainkan berapa banyak keluarga yang benar-benar perlu ditangani berhasil masuk ke sekian kasus pertama yang sanggup diperiksa petugas"
        padat
      >
        <div className="overflow-x-auto">
          <table className="w-full min-w-[640px] text-sm">
            <thead>
              <tr className="border-b border-slate-200 text-left text-2xs uppercase tracking-wide text-slate-500">
                <th className="px-4 py-2 font-medium">Kapasitas</th>
                <th className="px-3 py-2 text-right font-medium">Presisi</th>
                <th className="px-3 py-2 text-right font-medium">Dibanding acak</th>
                <th className="px-3 py-2 text-right font-medium">Recall</th>
                <th className="px-3 py-2 text-right font-medium">Batas maksimum</th>
                <th className="px-4 py-2 text-right font-medium">Efisiensi anggaran</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {anggaran.map((a) => (
                <tr key={a.k}>
                  <td className="angka px-4 py-2 text-slate-700">{format.angka(a.k)}</td>
                  <td className="angka px-3 py-2 text-right font-semibold text-slate-800">
                    {format.persen(a.presisi * 100, 1)}
                  </td>
                  <td className="angka px-3 py-2 text-right font-semibold text-nadi-700">
                    {format.desimal(a.pengganda, 2)}×
                  </td>
                  <td className="angka px-3 py-2 text-right text-slate-600">
                    {format.persen(a.recall * 100, 1)}
                  </td>
                  <td className="angka px-3 py-2 text-right text-slate-400">
                    {format.persen(a.recall_maksimum * 100, 1)}
                  </td>
                  <td className="angka px-4 py-2 text-right text-slate-700">
                    {format.persen(a.efisiensi_anggaran * 100, 1)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="px-4 pb-4">
          <Penafian judul="Cara membaca recall">
            Recall selalu dibatasi kapasitas: memeriksa 500 keluarga tidak mungkin
            menemukan lebih dari 500. Kolom batas maksimum menunjukkan batas itu,
            dan efisiensi anggaran menunjukkan berapa bagian dari yang mungkin
            benar-benar diraih — angka yang menilai model, bukan menilai besarnya
            anggaran.
          </Penafian>
        </div>
      </Kartu>

      <div className="grid gap-5 lg:grid-cols-2">
        {/* Kepentingan fitur */}
        <Kartu judul="Fitur paling berpengaruh" keterangan="Sumbangan tiap fitur terhadap keputusan model">
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={kepentingan} layout="vertical" margin={{ top: 4, right: 32, bottom: 4, left: 4 }}>
              <CartesianGrid stroke={TINTA.kisi} strokeDasharray="3 3" horizontal={false} />
              <XAxis type="number" tick={{ fontSize: 10, fill: TINTA.kedua }} axisLine={false} tickLine={false} tickFormatter={(v) => `${v}%`} />
              <YAxis type="category" dataKey="nama" tick={{ fontSize: 10, fill: TINTA.kedua }} axisLine={false} tickLine={false} width={190} />
              <Tooltip
                formatter={(v: number) => [format.persen(v, 2), "kepentingan"]}
                contentStyle={{ fontSize: 12, borderRadius: 6, border: "1px solid #e2e8f0" }}
              />
              <Bar dataKey="nilai" fill="#2a78d6" radius={[0, 3, 3, 0]} barSize={13} />
            </BarChart>
          </ResponsiveContainer>
        </Kartu>

        {/* Keadilan */}
        <Kartu
          judul="Pemeriksaan keadilan"
          keterangan="Kinerja model dipecah menurut kecamatan. Model yang baik secara keseluruhan namun buruk di satu wilayah akan mengalirkan anggaran ke arah yang keliru selama bertahun-tahun tanpa disadari."
          padat
        >
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-200 text-left text-2xs uppercase tracking-wide text-slate-500">
                  <th className="px-4 py-2 font-medium">Kecamatan</th>
                  <th className="px-3 py-2 text-right font-medium">Baris</th>
                  <th className="px-3 py-2 text-right font-medium">Prevalensi</th>
                  <th className="px-4 py-2 text-right font-medium">AUC</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {keadilanKec.map((k: any) => (
                  <tr key={k.nilai}>
                    <td className="px-4 py-2 text-xs text-slate-700">{k.nilai}</td>
                    <td className="angka px-3 py-2 text-right text-slate-500">{format.angka(k.jumlah_baris)}</td>
                    <td className="angka px-3 py-2 text-right text-slate-600">
                      {format.persen(k.prevalensi * 100, 1)}
                    </td>
                    <td className="angka px-4 py-2 text-right font-semibold text-slate-800">
                      {format.desimal(k.auc, 3)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {keadilanKec.length > 1 && (
            <div className="px-4 pb-4 pt-2">
              <Penafian>
                Selisih AUC antar-kecamatan{" "}
                {format.desimal(
                  Math.max(...keadilanKec.map((k: any) => k.auc)) -
                    Math.min(...keadilanKec.map((k: any) => k.auc)),
                  3,
                )}
                . Selisih yang kecil berarti model bekerja setara di seluruh wilayah.
              </Penafian>
            </div>
          )}
        </Kartu>
      </div>

      {/* Lapis data */}
      {fitur.data && (
        <Kartu
          judul="Dari mana fitur model berasal"
          keterangan="Selisih antar-lapis adalah nilai tambah pemaduan data, dinyatakan sebagai angka alih-alih sebagai gagasan"
        >
          <div className="grid gap-3 sm:grid-cols-3">
            {Object.entries(fitur.data.lapis).map(([kunci, v]: [string, any]) => (
              <div key={kunci} className="rounded-md border border-slate-200 p-3">
                <div className="angka text-xl font-bold text-slate-800">{v.jumlah}</div>
                <div className="text-2xs font-medium text-slate-600">
                  {kunci.replace(/_/g, " ")}
                </div>
                <p className="mt-1 text-2xs leading-relaxed text-slate-500">{v.keterangan}</p>
              </div>
            ))}
          </div>
          <div className="mt-4 rounded-md border border-amber-200 bg-amber-50 p-3">
            <div className="text-xs font-semibold text-amber-900">
              {fitur.data.dikecualikan.jumlah} fitur sengaja dikeluarkan
            </div>
            <p className="mt-1 text-2xs leading-relaxed text-amber-800">
              {fitur.data.dikecualikan.alasan}
            </p>
            <div className="mt-1.5 flex flex-wrap gap-1">
              {fitur.data.dikecualikan.fitur.map((f: any) => (
                <span key={f.nama} className="lencana border border-amber-300 bg-white text-amber-900">
                  {f.label}
                </span>
              ))}
            </div>
          </div>
        </Kartu>
      )}

      {/* Batas */}
      {batas.data && (
        <div className="grid gap-5 lg:grid-cols-2">
          <Kartu judul="Yang dilakukan sistem ini">
            <ul className="space-y-2">
              {batas.data.yang_dilakukan.map((y: string, i: number) => (
                <li key={i} className="flex items-start gap-2 text-xs leading-relaxed text-slate-700">
                  <CheckCircle2 size={13} className="mt-0.5 shrink-0 text-emerald-600" />
                  {y}
                </li>
              ))}
            </ul>
          </Kartu>

          <Kartu judul="Yang TIDAK dilakukan sistem ini">
            <ul className="space-y-2">
              {batas.data.yang_tidak_dilakukan.map((y: string, i: number) => (
                <li key={i} className="flex items-start gap-2 text-xs leading-relaxed text-slate-700">
                  <Ban size={13} className="mt-0.5 shrink-0 text-red-600" />
                  {y}
                </li>
              ))}
            </ul>
          </Kartu>
        </div>
      )}

      {batas.data && (
        <Kartu judul="Batas teknis yang perlu diketahui">
          <ul className="space-y-3">
            {batas.data.batas_teknis.map((b: any, i: number) => (
              <li key={i} className="rounded-md border border-slate-200 p-3">
                <div className="flex items-start gap-2">
                  <ShieldAlert size={14} className="mt-0.5 shrink-0 text-amber-600" />
                  <div>
                    <div className="text-xs font-semibold text-slate-800">{b.batas}</div>
                    <p className="mt-0.5 text-2xs leading-relaxed text-slate-600">{b.keterangan}</p>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </Kartu>
      )}

      {batas.data && (
        <Kartu judul="Tata kelola">
          <dl className="space-y-3">
            {Object.entries(batas.data.tata_kelola).map(([k, v]) => (
              <div key={k} className="flex items-start gap-2">
                <Scale size={13} className="mt-0.5 shrink-0 text-slate-400" />
                <div>
                  <dt className="text-xs font-semibold capitalize text-slate-700">
                    {k.replace(/_/g, " ")}
                  </dt>
                  <dd className="mt-0.5 text-2xs leading-relaxed text-slate-600">{v as string}</dd>
                </div>
              </div>
            ))}
          </dl>
        </Kartu>
      )}

      {m.catatan && <Penafian judul="Catatan model">{m.catatan}</Penafian>}
    </div>
  );
}
