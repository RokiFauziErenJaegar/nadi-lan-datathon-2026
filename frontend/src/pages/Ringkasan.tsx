/**
 * Executive Command Center - keadaan kabupaten dalam satu layar.
 *
 * Beberapa keputusan penyajian yang diambil dengan sadar:
 *
 * **Batang kecamatan berwarna tunggal.** Panjang batang sudah menyampaikan
 * nilainya; mewarnainya menurut nilai yang sama berarti memakai kanal identitas
 * untuk mengulang keterangan yang sudah ada. Warna disimpan untuk hal yang
 * benar-benar memerlukannya.
 *
 * **Kategori risiko selalu membawa ikon dan tulisan.** Dua dari empat kategori
 * memang berkontras rendah pada latar terang; maknanya ditanggung ikon dan
 * tulisan, warna hanya memperkuat.
 *
 * **Satu sumbu pada setiap grafik.** Jumlah jiwa dan persentase adalah dua
 * besaran berbeda, sehingga ditampilkan pada dua grafik terpisah alih-alih
 * ditumpuk pada satu bidang dengan dua skala.
 */

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
import { ArrowRight, ArrowUpRight, HeartPulse, Layers3, MapPinned, TrendingDown, Users, Wallet } from "lucide-react";
import { Link } from "react-router-dom";
import { api, format } from "../lib/api";
import { KEWENANGAN, useAuth } from "../lib/auth";
import { TINTA, WARNA_RISIKO, type KategoriRisiko } from "../lib/warna";
import { Galat, Kartu, KartuStat, LencanaRisiko, Memuat, Penafian } from "../components/dasar";
import "../styles/ringkasan.css";

interface DataRingkasan {
  gelombang: number;
  cakupan: { keluarga: number; jiwa: number; keterangan: string };
  kemiskinan: {
    keluarga_miskin: number;
    jiwa_miskin: number;
    persen_jiwa_miskin: number;
    keluarga_rentan: number;
    keterangan_rentan: string;
    garis_kemiskinan: number;
    garis_kerentanan: number;
    rasio_rata_rata: number;
    desil_rata_rata: number;
  };
  risiko: {
    sebaran: { kategori: string; jumlah: number; skor_rata: number }[];
    memburuk_tajam: number;
    keterangan_memburuk: string;
  };
  perlindungan_sosial: {
    tanpa_bantuan: number;
    nilai_bantuan_bulanan: number;
    nilai_bantuan_tahunan: number;
  };
  antrean: { total: number; per_jenis: { jenis: string; label: string; jumlah: number }[] };
  tren: {
    gelombang: number;
    tanggal: string;
    jiwa: number;
    jiwa_miskin: number;
    persen_jiwa_miskin: number;
  }[];
  acuan_bps: Record<string, number | string>;
}

interface DataKecamatan {
  kecamatan: {
    kode: string;
    nama: string;
    keluarga_terdata: number;
    keluarga_miskin: number;
    persen_keluarga_miskin: number;
    skor_rata_rata: number;
    risiko_tinggi: number;
    tanpa_bantuan: number;
    klasifikasi: string;
  }[];
}

const BULAN_PENDEK = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"];

function labelGelombang(tanggal: string): string {
  const d = new Date(tanggal);
  if (Number.isNaN(d.getTime())) return tanggal;
  return `${BULAN_PENDEK[d.getMonth()]} ${d.getFullYear()}`;
}

/** Tooltip bersama, memakai warna tinta - bukan warna deret. */
function Tooltiptip({
  active,
  payload,
  label,
  satuan,
}: {
  active?: boolean;
  payload?: { value: number; name: string }[];
  label?: string;
  satuan?: string;
}) {
  if (!active || !payload?.length) return null;
  return (
    <div className="ringkasan-tooltip rounded-md border border-slate-200 bg-white px-3 py-2 shadow-naik">
      <div className="text-2xs font-medium text-slate-500">{label}</div>
      {payload.map((p) => (
        <div key={p.name} className="angka mt-0.5 text-sm font-semibold text-slate-800">
          {satuan === "persen" ? format.persen(p.value, 2) : format.angka(p.value)}
          <span className="ml-1 text-2xs font-normal text-slate-500">{p.name}</span>
        </div>
      ))}
    </div>
  );
}

export default function Ringkasan() {
  const { punya } = useAuth();
  const ringkasan = useQuery({
    queryKey: ["ringkasan"],
    queryFn: () => api.ambil<DataRingkasan>("/ringkasan"),
  });
  const kecamatan = useQuery({
    queryKey: ["ringkasan-kecamatan"],
    queryFn: () => api.ambil<DataKecamatan>("/ringkasan/kecamatan"),
  });

  if (ringkasan.isLoading) return <Memuat pesan="Memuat ringkasan kabupaten..." />;
  if (ringkasan.error)
    return <Galat pesan={(ringkasan.error as Error).message} />;

  const d = ringkasan.data!;
  const tren = d.tren.map((t) => ({
    ...t,
    label: labelGelombang(t.tanggal),
  }));
  const totalRisiko = d.risiko.sebaran.reduce((a, b) => a + b.jumlah, 0) || 1;
  const terkini = tren.find((t) => t.gelombang === d.gelombang);
  const bolehPeta = punya(KEWENANGAN.BACA_PETA);
  const bolehAntrean = punya(KEWENANGAN.BACA_ANTREAN);

  return (
    <div className="ringkasan-page space-y-5">
      <section className="ringkasan-hero" aria-labelledby="ringkasan-hero-title">
        <div className="ringkasan-hero-copy">
          <div className="ringkasan-eyebrow"><span />Pusat kendali intervensi</div>
          <h2 id="ringkasan-hero-title">Membaca risiko.<br /><span>Mengarahkan intervensi.</span></h2>
          <p>Gambaran kesejahteraan keluarga Kabupaten Pringsewu.<br className="ringkasan-desktop-break" /> Dari data yang terhubung, menuju pemeriksaan yang terarah.</p>
          <div className="ringkasan-hero-actions">
            {bolehAntrean && (
              <Link to="/antrean" className="ringkasan-action-primary">Tinjau antrean kasus <ArrowUpRight size={16} /></Link>
            )}
            {bolehPeta && (
              <Link to="/peta" className="ringkasan-action-secondary"><MapPinned size={15} /> Jelajahi peta risiko <ArrowRight size={15} /></Link>
            )}
          </div>
          <div className="ringkasan-hero-meta">
            <span><Layers3 size={12} /> Cakupan desil 1–5</span>
            <i aria-hidden="true" />
            <span>Data sintetis untuk demonstrasi</span>
          </div>
        </div>
        <div className="ringkasan-observatory">
          <svg className="ringkasan-orbit" viewBox="0 0 340 280" fill="none" aria-hidden="true">
            <defs>
              <radialGradient id="ringkasan-orbit-glow"><stop stopColor="#53dfdc" stopOpacity=".13" /><stop offset="1" stopColor="#53dfdc" stopOpacity="0" /></radialGradient>
              <linearGradient id="ringkasan-orbit-line" x1="45" y1="230" x2="280" y2="40" gradientUnits="userSpaceOnUse"><stop stopColor="#53dfdc" stopOpacity="0" /><stop offset=".5" stopColor="#53dfdc" stopOpacity=".8" /><stop offset="1" stopColor="#53dfdc" stopOpacity=".1" /></linearGradient>
            </defs>
            <circle cx="174" cy="139" r="139" fill="url(#ringkasan-orbit-glow)" />
            <g stroke="#53dfdc" strokeOpacity=".13">
              <circle cx="174" cy="139" r="112" />
              <circle cx="174" cy="139" r="87" strokeDasharray="2 7" />
              <circle cx="174" cy="139" r="61" />
              <path d="M174 13V265M48 139H300" strokeDasharray="3 6" />
              <ellipse cx="174" cy="139" rx="135" ry="47" transform="rotate(-34 174 139)" />
              <ellipse cx="174" cy="139" rx="113" ry="50" transform="rotate(54 174 139)" />
            </g>
            <path d="M67 197C125 211 249 113 283 67" stroke="url(#ringkasan-orbit-line)" strokeWidth="1.6" />
            <path d="M174 27A112 112 0 0 1 286 139" stroke="#53dfdc" strokeOpacity=".65" strokeWidth="1.5" />
            <g fill="#53dfdc">
              <circle cx="174" cy="27" r="3.5" /><circle cx="251" cy="98" r="3.5" /><circle cx="93" cy="181" r="3" /><circle cx="235" cy="233" r="2.5" /><circle cx="68" cy="103" r="2" />
            </g>
            <circle cx="251" cy="98" r="8" stroke="#53dfdc" strokeOpacity=".25" />
            <circle cx="93" cy="181" r="7" stroke="#53dfdc" strokeOpacity=".25" />
            <g stroke="#53dfdc" strokeOpacity=".32"><path d="M30 31H43M36.5 24.5V37.5M301 240H314M307.5 233.5V246.5" /></g>
          </svg>
          <div className="ringkasan-orbit-value"><span>Gelombang</span><strong>{String(d.gelombang).padStart(2, "0")}</strong><span>{terkini?.label ?? "Pemutakhiran terkini"}</span></div>
          <div className="ringkasan-orbit-caption"><span className="ringkasan-orbit-caption-line" />{format.angka(d.cakupan.keluarga)} keluarga dalam cakupan</div>
        </div>
      </section>
      <div className="ringkasan-section-heading">
        <div><span className="ringkasan-section-index">01</span><h2>Gambaran kabupaten</h2></div>
        <span className="ringkasan-section-note">Gelombang {d.gelombang}{terkini ? ` · ${terkini.label}` : ""}</span>
      </div>
      {/* ---------- Kartu angka pokok ---------- */}
      <div className="ringkasan-stat-grid grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <KartuStat
          label="Keluarga terdata"
          nilai={format.angka(d.cakupan.keluarga)}
          ikon={Users}
          keterangan={`${format.angka(d.cakupan.jiwa)} jiwa dalam cakupan desil 1–5`}
        />
        <KartuStat
          label="Keluarga miskin"
          nilai={format.angka(d.kemiskinan.keluarga_miskin)}
          ikon={Wallet}
          nada="genting"
          keterangan={`${format.persen(d.kemiskinan.persen_jiwa_miskin, 2)} dari jiwa terdata berada di bawah garis kemiskinan`}
        />
        <KartuStat
          label="Rentan, belum miskin"
          nilai={format.angka(d.kemiskinan.keluarga_rentan)}
          ikon={HeartPulse}
          nada="perhatian"
          keterangan="Pengeluaran antara satu sampai satu setengah kali garis kemiskinan — satu guncangan sudah cukup menjatuhkan"
        />
        <KartuStat
          label="Memburuk tajam"
          nilai={format.angka(d.risiko.memburuk_tajam)}
          ikon={TrendingDown}
          nada="genting"
          keterangan={d.risiko.keterangan_memburuk}
          bawah={bolehAntrean && (
            <Link
              to="/antrean"
              className="text-xs font-medium text-nadi-700 hover:text-nadi-900"
            >
              Lihat {format.angka(d.antrean.total)} kasus pada antrean →
            </Link>
          )}
        />
      </div>

      {/* ---------- Tren kemiskinan ---------- */}
      <div className="ringkasan-section-heading">
        <div><span className="ringkasan-section-index">02</span><h2>Dinamika & prioritas risiko</h2></div>
        <span className="ringkasan-section-note">{d.tren.length} gelombang pemutakhiran</span>
      </div>
      <div className="ringkasan-analysis-grid grid gap-5 lg:grid-cols-2">
        <Kartu
          judul="Jiwa miskin dalam cakupan sistem"
          keterangan="Enam gelombang pemutakhiran, Maret 2023 sampai September 2025"
        >
          <ResponsiveContainer width="100%" height={230}>
            <LineChart data={tren} margin={{ top: 8, right: 12, bottom: 4, left: 4 }}>
              <CartesianGrid stroke={`var(--ringkasan-chart-grid, ${TINTA.kisi})`} strokeDasharray="3 3" vertical={false} />
              <XAxis
                dataKey="label"
                tick={{ fontSize: 11, fill: `var(--ringkasan-chart-label, ${TINTA.kedua})` }}
                axisLine={{ stroke: `var(--ringkasan-chart-axis, ${TINTA.sumbu})` }}
                tickLine={false}
              />
              <YAxis
                tick={{ fontSize: 11, fill: `var(--ringkasan-chart-label, ${TINTA.kedua})` }}
                axisLine={false}
                tickLine={false}
                width={52}
                tickFormatter={(v) => format.angka(v as number)}
              />
              <Tooltip content={<Tooltiptip />} cursor={{ stroke: `var(--ringkasan-chart-axis, ${TINTA.sumbu})` }} />
              <Line
                type="monotone"
                dataKey="jiwa_miskin"
                name="jiwa"
                stroke="var(--ringkasan-chart-series, #2a78d6)"
                strokeWidth={2}
                dot={{ r: 4, strokeWidth: 2, fill: "var(--ringkasan-chart-dot, #fff)" }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
          <Penafian>
            Angka ini dikalibrasi terhadap publikasi BPS Kabupaten Pringsewu:{" "}
            {d.acuan_bps.persen_miskin_kabupaten_2023}% (2023),{" "}
            {d.acuan_bps.persen_miskin_kabupaten_2024}% (2024), dan{" "}
            {d.acuan_bps.persen_miskin_kabupaten_2025}% (2025) tingkat kabupaten.
            Persentase pada sistem ini lebih tinggi karena dihitung terhadap cakupan
            desil 1–5, bukan terhadap seluruh penduduk — jumlah orangnya sama.
          </Penafian>
        </Kartu>

        {/* ---------- Sebaran risiko ---------- */}
        <Kartu
          judul="Sebaran kategori risiko"
          keterangan="Perkiraan peluang keluarga berada di bawah garis kemiskinan pada pemutakhiran berikutnya"
        >
          <div className="ringkasan-risk-bars space-y-3">
            {(["sangat_tinggi", "tinggi", "sedang", "rendah"] as KategoriRisiko[]).map((k) => {
              const b = d.risiko.sebaran.find((x) => x.kategori === k);
              const jumlah = b?.jumlah ?? 0;
              const bagian = (jumlah / totalRisiko) * 100;
              return (
                <div key={k}>
                  <div className="mb-1 flex items-center justify-between gap-3">
                    <LencanaRisiko kategori={k} ukuran="kecil" />
                    <div className="angka text-sm font-semibold text-slate-800">
                      {format.angka(jumlah)}
                      <span className="ml-1.5 text-2xs font-normal text-slate-500">
                        {format.persen(bagian, 1)}
                      </span>
                    </div>
                  </div>
                  <div className="h-2 overflow-hidden rounded-full bg-slate-100">
                    <div
                      className="h-full rounded-full"
                      style={{
                        width: `${Math.max(bagian, 0.4)}%`,
                        backgroundColor: WARNA_RISIKO[k],
                      }}
                    />
                  </div>
                </div>
              );
            })}
          </div>

          <div className="ringkasan-risk-footer mt-4 grid grid-cols-2 gap-3 border-t border-slate-100 pt-4">
            <div>
              <div className="text-2xs text-slate-500">Tidak menerima bantuan apa pun</div>
              <div className="angka text-lg font-bold text-slate-800">
                {format.angka(d.perlindungan_sosial.tanpa_bantuan)}
              </div>
            </div>
            <div>
              <div className="text-2xs text-slate-500">Nilai bantuan tersalur per tahun</div>
              <div className="angka text-lg font-bold text-slate-800">
                {format.rupiahRingkas(d.perlindungan_sosial.nilai_bantuan_tahunan)}
              </div>
            </div>
          </div>
        </Kartu>
      </div>

      {/* ---------- Kecamatan ---------- */}
      <div className="ringkasan-section-heading">
        <div><span className="ringkasan-section-index">03</span><h2>Perspektif wilayah</h2></div>
        {kecamatan.data && <span className="ringkasan-section-note">{kecamatan.data.kecamatan.length} kecamatan terdata</span>}
      </div>
      <Kartu
        judul="Kecamatan menurut tingkat kemiskinan"
        keterangan="Persentase keluarga miskin pada gelombang terkini"
        aksi={bolehPeta && (
          <Link to="/peta" className="text-xs font-medium text-nadi-700 hover:text-nadi-900">
            Buka peta →
          </Link>
        )}
      >
        {kecamatan.isLoading ? (
          <Memuat pesan="Memuat data kecamatan..." />
        ) : (
          <>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart
                data={kecamatan.data?.kecamatan ?? []}
                layout="vertical"
                margin={{ top: 4, right: 48, bottom: 4, left: 4 }}
              >
                <CartesianGrid stroke={`var(--ringkasan-chart-grid, ${TINTA.kisi})`} strokeDasharray="3 3" horizontal={false} />
                <XAxis
                  type="number"
                  tick={{ fontSize: 11, fill: `var(--ringkasan-chart-label, ${TINTA.kedua})` }}
                  axisLine={false}
                  tickLine={false}
                  tickFormatter={(v) => `${v}%`}
                />
                <YAxis
                  type="category"
                  dataKey="nama"
                  tick={{ fontSize: 11, fill: `var(--ringkasan-chart-label, ${TINTA.kedua})` }}
                  axisLine={false}
                  tickLine={false}
                  width={110}
                />
                <Tooltip
                  content={<Tooltiptip satuan="persen" />}
                  cursor={{ fill: "var(--ringkasan-chart-hover, rgba(15,23,42,0.04))" }}
                />
                {/* Satu warna untuk seluruh batang: panjangnya sudah
                    menyampaikan nilainya. */}
                <Bar
                  dataKey="persen_keluarga_miskin"
                  name="keluarga miskin"
                  fill="var(--ringkasan-chart-series, #2a78d6)"
                  radius={[0, 4, 4, 0]}
                  barSize={16}
                />
              </BarChart>
            </ResponsiveContainer>

            <div className="ringkasan-region-table mt-4 overflow-x-auto">
              <table className="w-full min-w-[560px] text-sm">
                <thead>
                  <tr className="border-b border-slate-200 text-left text-2xs uppercase tracking-wide text-slate-500">
                    <th className="pb-2 pr-3 font-medium">Kecamatan</th>
                    <th className="pb-2 pr-3 text-right font-medium">Keluarga</th>
                    <th className="pb-2 pr-3 text-right font-medium">Miskin</th>
                    <th className="pb-2 pr-3 text-right font-medium">Risiko tinggi</th>
                    <th className="pb-2 text-right font-medium">Tanpa bantuan</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {kecamatan.data?.kecamatan.map((k) => (
                    <tr key={k.kode} className="hover:bg-slate-50">
                      <td className="py-2 pr-3">
                        <div className="font-medium text-slate-700">{k.nama}</div>
                        <div className="text-2xs text-slate-400">{k.klasifikasi}</div>
                      </td>
                      <td className="angka py-2 pr-3 text-right text-slate-600">
                        {format.angka(k.keluarga_terdata)}
                      </td>
                      <td className="angka py-2 pr-3 text-right text-slate-800">
                        {format.angka(k.keluarga_miskin)}
                        <span className="ml-1 text-2xs text-slate-400">
                          {format.persen(k.persen_keluarga_miskin, 1)}
                        </span>
                      </td>
                      <td className="angka py-2 pr-3 text-right text-slate-600">
                        {format.angka(k.risiko_tinggi)}
                      </td>
                      <td className="angka py-2 text-right text-slate-600">
                        {format.angka(k.tanpa_bantuan)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}
      </Kartu>

      {/* ---------- Antrean ---------- */}
      <div className="ringkasan-section-heading">
        <div><span className="ringkasan-section-index">04</span><h2>Langkah berikutnya</h2></div>
        <span className="ringkasan-section-note">{format.angka(d.antrean.total)} kasus dalam antrean</span>
      </div>
      <Kartu
        judul="Antrean kasus menunggu pemeriksaan"
        keterangan="Setiap kasus adalah usulan pemeriksaan, bukan keputusan"
        aksi={bolehAntrean && (
          <Link to="/antrean" className="text-xs font-medium text-nadi-700 hover:text-nadi-900">
            Buka antrean →
          </Link>
        )}
      >
        <div className="ringkasan-queue-grid grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {d.antrean.per_jenis.map((j) => (
            <div key={j.jenis} className="ringkasan-queue-item rounded-md border border-slate-200 p-3">
              <div className="angka text-xl font-bold text-slate-800">
                {format.angka(j.jumlah)}
              </div>
              <div className="mt-0.5 text-xs leading-snug text-slate-600">{j.label}</div>
            </div>
          ))}
        </div>
        <div className="mt-4">
          <Penafian judul="Batas sistem">
            Keluaran NADI berupa daftar prioritas pemeriksaan. Sistem ini tidak
            menetapkan penerima bantuan dan tidak menghentikan bantuan siapa pun.
            Penetapan tetap melalui musyawarah pekon dan keputusan pejabat
            berwenang. Seluruh data bersifat sintetis.
          </Penafian>
        </div>
      </Kartu>
    </div>
  );
}
