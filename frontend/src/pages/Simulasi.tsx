/**
 * What-if Policy Simulator.
 *
 * Setiap hasil disertai penafian yang sama tegasnya: ini aritmetika cakupan dan
 * biaya, bukan perkiraan dampak kebijakan. Perbedaannya menentukan, dan
 * menghapusnya akan membuat angka yang terdengar berwibawa dipakai menyusun
 * anggaran satu kabupaten.
 */

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Calculator, Home, Users } from "lucide-react";
import { api, format } from "../lib/api";
import { TINTA } from "../lib/warna";
import { Galat, Kartu, KartuStat, Memuat, Penafian } from "../components/dasar";

type Alat = "rtlh" | "kapasitas" | "cakupan";

export default function Simulasi() {
  const [alat, setAlat] = useState<Alat>("rtlh");

  // --- Parameter RTLH ---
  const [bsps, setBsps] = useState(0);
  const [rst, setRst] = useState(0);
  const [apbd, setApbd] = useState(80);
  const [danaDesa, setDanaDesa] = useState(0);
  const [pemburukan, setPemburukan] = useState(0);

  // --- Parameter cakupan ---
  const [desilMaks, setDesilMaks] = useState(3);
  const [pagu, setPagu] = useState(50_000_000_000);

  const rtlh = useQuery({
    queryKey: ["sim-rtlh", bsps, rst, apbd, danaDesa, pemburukan],
    queryFn: () =>
      api.ambil<any>(
        `/simulasi/rtlh?bsps=${bsps}&rst=${rst}&rutilahu_apbd=${apbd}&dana_desa=${danaDesa}&pertumbuhan_backlog=${pemburukan}`,
      ),
    enabled: alat === "rtlh",
  });

  const kapasitas = useQuery({
    queryKey: ["sim-kapasitas"],
    queryFn: () => api.ambil<any>("/simulasi/kapasitas-verifikasi"),
    enabled: alat === "kapasitas",
  });

  const cakupan = useQuery({
    queryKey: ["sim-cakupan", desilMaks, pagu],
    queryFn: () =>
      api.ambil<any>(
        `/simulasi/cakupan?desil_maksimum=${desilMaks}&biaya_satuan_tahunan=2400000&pagu=${pagu}`,
      ),
    enabled: alat === "cakupan",
  });

  const penafian =
    "Simulasi ini adalah perhitungan aritmetika cakupan dan biaya berdasarkan aturan kelayakan program serta pagu yang dimasukkan. Simulasi ini BUKAN prediksi dampak kebijakan dan tidak mengandung klaim sebab-akibat.";

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap gap-2">
        {(
          [
            ["rtlh", "Penuntasan rumah tidak layak huni", Home],
            ["kapasitas", "Kapasitas verifikasi", Users],
            ["cakupan", "Cakupan dan biaya program", Calculator],
          ] as const
        ).map(([nilai, label, Ikon]) => (
          <button
            key={nilai}
            onClick={() => setAlat(nilai)}
            className={`flex items-center gap-1.5 rounded-md px-3 py-1.5 text-xs font-medium ${
              alat === nilai ? "bg-nadi-700 text-white" : "border border-slate-300 bg-white text-slate-700"
            }`}
          >
            <Ikon size={14} /> {label}
          </button>
        ))}
      </div>

      {/* ================= RTLH ================= */}
      {alat === "rtlh" && (
        <div className="grid gap-5 lg:grid-cols-[300px_1fr]">
          <Kartu judul="Kapasitas per sumber dana" keterangan="Unit rumah yang ditangani per tahun">
            <div className="space-y-3">
              {(
                [
                  ["BSPS APBN (Rp20 jt/unit)", bsps, setBsps, 400],
                  ["RST Kemensos (Rp20 jt/unit)", rst, setRst, 400],
                  ["Rutilahu APBD (Rp15 jt/unit)", apbd, setApbd, 400],
                  ["Dana Desa (Rp15 jt/unit)", danaDesa, setDanaDesa, 400],
                ] as const
              ).map(([label, nilai, setter, maks]) => (
                <div key={label}>
                  <div className="mb-1 flex items-baseline justify-between">
                    <label className="text-2xs text-slate-600">{label}</label>
                    <span className="angka text-xs font-semibold text-slate-800">{nilai}</span>
                  </div>
                  <input
                    type="range"
                    min={0}
                    max={maks}
                    step={10}
                    value={nilai}
                    onChange={(e) => setter(Number(e.target.value))}
                    className="w-full accent-nadi-700"
                  />
                </div>
              ))}

              <div className="border-t border-slate-100 pt-3">
                <div className="mb-1 flex items-baseline justify-between">
                  <label className="text-2xs text-slate-600">
                    Rumah yang memburuk per tahun
                  </label>
                  <span className="angka text-xs font-semibold text-slate-800">
                    {format.persen(pemburukan * 100, 1)}
                  </span>
                </div>
                <input
                  type="range"
                  min={0}
                  max={0.08}
                  step={0.005}
                  value={pemburukan}
                  onChange={(e) => setPemburukan(Number(e.target.value))}
                  className="w-full accent-nadi-700"
                />
                <p className="mt-1 text-2xs leading-relaxed text-slate-500">
                  Rumah juga menua. Pertanyaan ini biasanya dihindari, padahal pada
                  laju penanganan sekarang, pemburukan tiga persen per tahun saja
                  sudah membuat sisa kebutuhan tidak pernah tuntas.
                </p>
              </div>
            </div>
          </Kartu>

          <div className="space-y-5">
            {rtlh.isLoading ? (
              <Memuat />
            ) : rtlh.error ? (
              <Galat pesan={(rtlh.error as Error).message} />
            ) : (
              <>
                <div className="grid gap-4 sm:grid-cols-3">
                  <KartuStat
                    label="Sisa kebutuhan"
                    nilai={format.angka(rtlh.data.backlog)}
                    satuan="unit"
                    keterangan="Dinas Sosial Kabupaten Pringsewu, 2025"
                  />
                  <KartuStat
                    label="Kapasitas gabungan"
                    nilai={format.angka(rtlh.data.kapasitas_tahunan)}
                    satuan="unit/tahun"
                  />
                  <KartuStat
                    label="Tuntas dalam"
                    nilai={
                      rtlh.data.tuntas_dalam_horizon
                        ? format.angka(rtlh.data.tahun_tuntas)
                        : "tidak tuntas"
                    }
                    satuan={rtlh.data.tuntas_dalam_horizon ? "tahun" : ""}
                    nada={
                      !rtlh.data.tuntas_dalam_horizon || rtlh.data.tahun_tuntas > 15
                        ? "genting"
                        : rtlh.data.tahun_tuntas > 7
                          ? "perhatian"
                          : "baik"
                    }
                    keterangan={`Biaya ${format.rupiahRingkas(rtlh.data.biaya_tahunan)} per tahun`}
                  />
                </div>

                <Kartu judul="Lintasan sisa kebutuhan" keterangan="Unit yang belum tertangani, tahun demi tahun">
                  <ResponsiveContainer width="100%" height={230}>
                    <LineChart data={rtlh.data.lintasan} margin={{ top: 8, right: 12, bottom: 4, left: 4 }}>
                      <CartesianGrid stroke={TINTA.kisi} strokeDasharray="3 3" vertical={false} />
                      <XAxis
                        dataKey="tahun"
                        tick={{ fontSize: 11, fill: TINTA.kedua }}
                        axisLine={{ stroke: TINTA.sumbu }}
                        tickLine={false}
                        label={{ value: "tahun ke-", position: "insideBottom", offset: -2, fontSize: 10, fill: TINTA.redup }}
                      />
                      <YAxis tick={{ fontSize: 11, fill: TINTA.kedua }} axisLine={false} tickLine={false} width={52} />
                      <Tooltip
                        formatter={(v: number) => [format.angka(v), "unit tersisa"]}
                        labelFormatter={(l) => `Tahun ke-${l}`}
                        contentStyle={{ fontSize: 12, borderRadius: 6, border: "1px solid #e2e8f0" }}
                      />
                      <Line
                        type="monotone"
                        dataKey="sisa_unit"
                        stroke="#2a78d6"
                        strokeWidth={2}
                        dot={{ r: 3 }}
                        activeDot={{ r: 6 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                  {rtlh.data.catatan.map((c: string, i: number) => (
                    <p key={i} className="mt-1 text-xs leading-relaxed text-slate-600">{c}</p>
                  ))}
                </Kartu>

                {rtlh.data.rincian_sumber.length > 0 && (
                  <Kartu judul="Rincian per sumber dana" padat>
                    <div className="overflow-x-auto">
                    <table className="w-full min-w-[420px] text-sm">
                      <thead>
                        <tr className="border-b border-slate-200 text-left text-2xs uppercase tracking-wide text-slate-500">
                          <th className="px-4 py-2 font-medium">Sumber</th>
                          <th className="px-3 py-2 text-right font-medium">Unit/tahun</th>
                          <th className="px-3 py-2 text-right font-medium">Nominal/unit</th>
                          <th className="px-4 py-2 text-right font-medium">Biaya/tahun</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100">
                        {rtlh.data.rincian_sumber.map((s: any) => (
                          <tr key={s.kode}>
                            <td className="px-4 py-2">
                              <div className="text-xs font-medium text-slate-700">{s.nama}</div>
                              <div className="text-2xs text-slate-400">{s.sumber_dana}</div>
                            </td>
                            <td className="angka px-3 py-2 text-right text-slate-700">{s.unit_per_tahun}</td>
                            <td className="angka px-3 py-2 text-right text-slate-600">
                              {format.rupiahRingkas(s.nominal_per_unit)}
                            </td>
                            <td className="angka px-4 py-2 text-right font-semibold text-slate-800">
                              {format.rupiahRingkas(s.biaya_tahunan)}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                    </div>
                  </Kartu>
                )}
              </>
            )}
            <Penafian judul="Batas simulasi">{penafian}</Penafian>
          </div>
        </div>
      )}

      {/* ================= Kapasitas verifikasi ================= */}
      {alat === "kapasitas" && (
        <>
          {kapasitas.isLoading ? (
            <Memuat />
          ) : kapasitas.error ? (
            <Galat pesan={(kapasitas.error as Error).message} />
          ) : (
            <Kartu
              judul="Hasil terhadap kapasitas verifikasi"
              keterangan="Berapa keluarga yang benar-benar perlu ditangani berhasil ditemukan pada sekian kunjungan pertama"
            >
              <ResponsiveContainer width="100%" height={260}>
                <BarChart data={kapasitas.data.titik} margin={{ top: 8, right: 12, bottom: 4, left: 4 }}>
                  <CartesianGrid stroke={TINTA.kisi} strokeDasharray="3 3" vertical={false} />
                  <XAxis dataKey="k" tick={{ fontSize: 11, fill: TINTA.kedua }} axisLine={{ stroke: TINTA.sumbu }} tickLine={false} />
                  <YAxis tick={{ fontSize: 11, fill: TINTA.kedua }} axisLine={false} tickLine={false} width={46} />
                  <Tooltip
                    formatter={(v: number, n: string) => [format.angka(v), n === "tertangkap" ? "ditemukan" : n]}
                    labelFormatter={(l) => `${format.angka(Number(l))} kunjungan`}
                    contentStyle={{ fontSize: 12, borderRadius: 6, border: "1px solid #e2e8f0" }}
                  />
                  <Bar dataKey="tertangkap" name="tertangkap" fill="#2a78d6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>

              <div className="mt-3 overflow-x-auto">
                <table className="w-full min-w-[520px] text-sm">
                  <thead>
                    <tr className="border-b border-slate-200 text-left text-2xs uppercase tracking-wide text-slate-500">
                      <th className="py-2 pr-3 font-medium">Kapasitas</th>
                      <th className="py-2 pr-3 text-right font-medium">Ditemukan</th>
                      <th className="py-2 pr-3 text-right font-medium">Tambahan</th>
                      <th className="py-2 pr-3 text-right font-medium">Presisi</th>
                      <th className="py-2 text-right font-medium">Dibanding acak</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {kapasitas.data.titik.map((t: any) => (
                      <tr key={t.k}>
                        <td className="angka py-2 pr-3 text-slate-700">{format.angka(t.k)}</td>
                        <td className="angka py-2 pr-3 text-right font-semibold text-slate-800">
                          {format.angka(t.tertangkap)}
                        </td>
                        <td className="angka py-2 pr-3 text-right text-emerald-700">
                          +{format.angka(t.tambahan_dari_titik_sebelumnya)}
                        </td>
                        <td className="angka py-2 pr-3 text-right text-slate-600">
                          {format.persen(t.presisi * 100, 1)}
                        </td>
                        <td className="angka py-2 text-right font-semibold text-nadi-700">
                          {format.desimal(t.pengganda, 2)}×
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <Penafian judul="Cara membaca">{kapasitas.data.catatan}</Penafian>
            </Kartu>
          )}
        </>
      )}

      {/* ================= Cakupan ================= */}
      {alat === "cakupan" && (
        <div className="grid gap-5 lg:grid-cols-[300px_1fr]">
          <Kartu judul="Parameter">
            <div className="space-y-4">
              <div>
                <div className="mb-1 flex items-baseline justify-between">
                  <label className="text-2xs text-slate-600">Sasaran sampai desil</label>
                  <span className="angka text-xs font-semibold text-slate-800">{desilMaks}</span>
                </div>
                <input
                  type="range"
                  min={1}
                  max={6}
                  value={desilMaks}
                  onChange={(e) => setDesilMaks(Number(e.target.value))}
                  className="w-full accent-nadi-700"
                />
              </div>
              <div>
                <div className="mb-1 flex items-baseline justify-between">
                  <label className="text-2xs text-slate-600">Pagu anggaran</label>
                  <span className="angka text-xs font-semibold text-slate-800">
                    {format.rupiahRingkas(pagu)}
                  </span>
                </div>
                <input
                  type="range"
                  min={5_000_000_000}
                  max={300_000_000_000}
                  step={5_000_000_000}
                  value={pagu}
                  onChange={(e) => setPagu(Number(e.target.value))}
                  className="w-full accent-nadi-700"
                />
                <p className="mt-1 text-2xs text-slate-500">
                  Biaya per penerima Rp2,4 juta per tahun, setara Program Sembako.
                </p>
              </div>
            </div>
          </Kartu>

          <div className="space-y-5">
            {cakupan.isLoading ? (
              <Memuat />
            ) : cakupan.error ? (
              <Galat pesan={(cakupan.error as Error).message} />
            ) : (
              <>
                <div className="grid gap-4 sm:grid-cols-3">
                  <KartuStat label="Memenuhi syarat" nilai={format.angka(cakupan.data.jumlah_layak)} satuan="keluarga" />
                  <KartuStat
                    label="Tercakup pagu"
                    nilai={format.angka(cakupan.data.jumlah_tercakup)}
                    satuan="keluarga"
                    nada="baik"
                    keterangan={`${format.persen(cakupan.data.persen_terlayani, 1)} dari yang memenuhi syarat`}
                  />
                  <KartuStat
                    label="Layak namun tidak tercakup"
                    nilai={format.angka(cakupan.data.jumlah_tidak_tercakup)}
                    satuan="keluarga"
                    nada="genting"
                    keterangan="Inilah keterbatasan anggaran, dinyatakan sebagai daftar keluarga - bukan sebagai angka abstrak"
                  />
                </div>

                {cakupan.data.rincian_wilayah?.length > 0 && (
                  <Kartu judul="Yang tidak tercakup, menurut kecamatan" padat>
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b border-slate-200 text-left text-2xs uppercase tracking-wide text-slate-500">
                          <th className="px-4 py-2 font-medium">Kecamatan</th>
                          <th className="px-3 py-2 text-right font-medium">Layak</th>
                          <th className="px-3 py-2 text-right font-medium">Tercakup</th>
                          <th className="px-4 py-2 text-right font-medium">Tidak tercakup</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100">
                        {cakupan.data.rincian_wilayah.map((w: any) => (
                          <tr key={w.kecamatan}>
                            <td className="px-4 py-2 text-xs text-slate-700">{w.kecamatan}</td>
                            <td className="angka px-3 py-2 text-right text-slate-600">{format.angka(w.layak)}</td>
                            <td className="angka px-3 py-2 text-right text-slate-600">
                              {format.angka(w.tercakup)}
                              <span className="ml-1 text-2xs text-slate-400">{format.persen(w.persen, 0)}</span>
                            </td>
                            <td className="angka px-4 py-2 text-right font-semibold text-red-700">
                              {format.angka(w.tidak_tercakup)}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </Kartu>
                )}

                <Kartu judul="Asumsi yang dipakai">
                  <ul className="list-inside list-disc space-y-1 text-xs leading-relaxed text-slate-600">
                    {cakupan.data.asumsi.map((a: string, i: number) => (
                      <li key={i}>{a}</li>
                    ))}
                  </ul>
                </Kartu>
              </>
            )}
            <Penafian judul="Batas simulasi">{penafian}</Penafian>
          </div>
        </div>
      )}
    </div>
  );
}
