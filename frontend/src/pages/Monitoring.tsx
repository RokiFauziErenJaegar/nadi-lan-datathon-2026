/**
 * Outcome Monitoring - apa yang terjadi setelah bantuan disalurkan.
 *
 * Layar ini menutup lingkar yang dijanjikan proposal, dan seluruh
 * rancangannya berdiri di atas satu keputusan penyajian:
 *
 * **Angka capaian tidak pernah ditampilkan sendirian.**
 *
 * Enam puluh delapan persen keluarga membaik setelah menerima intervensi -
 * kalimat itu terdengar meyakinkan sampai orang mengetahui bahwa keluarga
 * sebanding yang tidak menerima apa pun juga membaik empat puluh lima persen.
 * Keluarga dengan skor kerentanan tinggi cenderung turun dengan sendirinya
 * pada pengukuran berikutnya; itu regresi ke rata-rata, bukan keberhasilan
 * program. Karena itu setiap batang capaian pada halaman ini berdampingan
 * dengan batang kelompok pembanding, dan selisih keduanyalah yang ditonjolkan
 * - bukan angka mentahnya.
 *
 * Dashboard pemerintah yang menampilkan angka capaian tanpa pembanding bukan
 * sekadar kurang teliti; ia menyesatkan pengambil keputusan yang mempercayainya.
 *
 * Hal kedua yang perlu diketahui pembaca kode ini: penilaian membaik, tetap,
 * atau memburuk tidak pernah diketik manusia. Ia dihitung peladen dari selisih
 * skor kerentanan antardua gelombang. Petugas hanya menekan tombol dan menulis
 * catatan. Tanpa pembatasan itu, angka pada layar ini akan menjadi laporan
 * capaian yang menilai dirinya sendiri.
 */

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Activity, ClipboardCheck, HandCoins, ScaleIcon } from "lucide-react";
import { Galat, Jendela, Kartu, KartuStat, Memuat, Penafian } from "../components/dasar";
import { api, format, GalatApi } from "../lib/api";
import { KEWENANGAN, useAuth } from "../lib/auth";
import { TINTA } from "../lib/warna";

// ---------------------------------------------------------------------------
// Bentuk data
// ---------------------------------------------------------------------------
interface ButirPenilaian {
  penilaian: string;
  jumlah: number;
  persen: number;
  persen_pembanding: number | null;
}

interface ButirProgram {
  program: string;
  dinilai: number;
  membaik: number;
  persen_membaik: number;
  selisih_rata: number;
}

interface DataRekap {
  per_status: { status: string; jumlah: number }[];
  dinilai: number;
  keterangan?: string;
  penilaian?: ButirPenilaian[];
  pembanding?: { tercocokkan: number; dari: number; keterangan: string };
  selisih_skor_rata?: number;
  keluar_dari_miskin?: number;
  masuk_ke_miskin?: number;
  per_program?: ButirProgram[];
  ambang_perubahan_bermakna: number;
  ambang_sel_kecil?: number;
  penafian: string;
}

interface ButirIntervensi {
  kode: string;
  status: string;
  tanggal_mulai: string | null;
  gelombang_mulai: number;
  nilai_manfaat_bulanan: number | null;
  program: string;
  program_nama: string;
  opd: string | null;
  kasus: string | null;
  keluarga: string;
  pekon: string;
  kecamatan: string;
  penilaian: string | null;
  selisih_skor: number | null;
  skor_sebelum: number | null;
  skor_sesudah: number | null;
  siap_dinilai: boolean;
}

interface DataDaftar {
  total: number;
  intervensi: ButirIntervensi[];
  penafian: string;
}

// ---------------------------------------------------------------------------
// Warna
// ---------------------------------------------------------------------------
// Penilaian adalah STATUS, bukan kategori. Membaik hijau, memburuk merah -
// keduanya diambil dari palet status yang sudah tervalidasi. "Tetap" sengaja
// kelabu, bukan kuning: keadaan yang tidak berubah bukan peringatan, dan
// mewarnainya kuning akan membuat seperlima keluarga tampak bermasalah tanpa
// alasan.
const WARNA_PENILAIAN: Record<string, string> = {
  membaik: "#0ca30c",
  tetap: "#94a3b8",
  memburuk: "#d03b3b",
};

// Kelompok pembanding memakai satu warna netral untuk seluruh kategori.
// Ia bukan status melainkan garis acuan, dan mewarnainya seperti status akan
// membuat pembaca mengira kedua batang menyampaikan hal yang sejenis.
const WARNA_PEMBANDING = "#cbd5e1";

const LABEL_PENILAIAN: Record<string, string> = {
  membaik: "Membaik",
  tetap: "Tetap",
  memburuk: "Memburuk",
};

const LABEL_STATUS: Record<string, string> = {
  direncanakan: "Direncanakan",
  disetujui: "Disetujui",
  berjalan: "Berjalan",
  selesai: "Selesai",
  dibatalkan: "Dibatalkan",
};

// ---------------------------------------------------------------------------
function TooltipBanding({
  active,
  payload,
  label,
}: {
  active?: boolean;
  payload?: { value: number; name: string }[];
  label?: string;
}) {
  if (!active || !payload?.length) return null;
  return (
    <div className="shadow-naik rounded-md border border-slate-200 bg-white px-3 py-2">
      <div className="text-2xs font-medium text-slate-500">{label}</div>
      {payload.map((p) => (
        <div key={p.name} className="angka mt-0.5 text-sm font-semibold text-slate-800">
          {format.persen(p.value, 1)}
          <span className="ml-1 text-2xs font-normal text-slate-500">{p.name}</span>
        </div>
      ))}
    </div>
  );
}

// ---------------------------------------------------------------------------
function JendelaNilai({
  kode,
  onTutup,
}: {
  kode: string;
  onTutup: () => void;
}) {
  const [catatan, setCatatan] = useState("");
  const klien = useQueryClient();

  const nilai = useMutation({
    mutationFn: () =>
      api.kirim<{ penilaian: string; selisih_skor: number; skor_sebelum: number; skor_sesudah: number }>(
        `/intervensi/${kode}/hasil`,
        { catatan: catatan.trim() || null },
      ),
    onSuccess: () => {
      // Tembolok bawaan bertahan lima menit dan tidak menyegar sendiri saat
      // jendela kembali difokuskan, jadi pembatalannya harus disebut satu per
      // satu - kalau tidak, angka di layar akan tertinggal dari basis data.
      klien.invalidateQueries({ queryKey: ["monitoring-rekap"] });
      klien.invalidateQueries({ queryKey: ["monitoring-daftar"] });
    },
  });

  const hasil = nilai.data;

  return (
    <Jendela
      judul={`Nilai hasil intervensi ${kode}`}
      keterangan="Seluruh angka dihitung sistem dari data kondisi keluarga. Yang Anda tambahkan hanya catatan penjelas."
      onTutup={onTutup}
      aksi={
        hasil ? (
          <button type="button" className="tombol-utama" onClick={onTutup}>
            Selesai
          </button>
        ) : (
          <>
            <button type="button" className="tombol-halus" onClick={onTutup}>
              Batal
            </button>
            <button
              type="button"
              className="tombol-utama"
              disabled={nilai.isPending}
              onClick={() => nilai.mutate()}
            >
              {nilai.isPending ? "Menghitung..." : "Hitung penilaian"}
            </button>
          </>
        )
      }
    >
      {hasil ? (
        <div className="space-y-3">
          <div className="flex items-baseline gap-2">
            <span
              className="rounded px-2 py-0.5 text-xs font-semibold text-white"
              style={{ backgroundColor: WARNA_PENILAIAN[hasil.penilaian] ?? TINTA.kedua }}
            >
              {LABEL_PENILAIAN[hasil.penilaian] ?? hasil.penilaian}
            </span>
            <span className="angka text-sm text-slate-600">
              skor {format.desimal(hasil.skor_sebelum)} &rarr; {format.desimal(hasil.skor_sesudah)}
              <span className="ml-1 font-semibold">
                ({hasil.selisih_skor > 0 ? "+" : ""}
                {format.desimal(hasil.selisih_skor)})
              </span>
            </span>
          </div>
          <Penafian>
            Angka ini menunjukkan perubahan kondisi, bukan sebabnya. Keluarga yang membaik
            setelah menerima intervensi belum tentu membaik karena intervensi tersebut.
          </Penafian>
        </div>
      ) : (
        <div className="space-y-4">
          <div>
            <label
              htmlFor="catatan-hasil"
              className="mb-1 block text-xs font-medium text-slate-600"
            >
              Catatan petugas <span className="font-normal text-slate-400">(opsional)</span>
            </label>
            <textarea
              id="catatan-hasil"
              className="masukan"
              rows={3}
              maxLength={2000}
              value={catatan}
              onChange={(e) => setCatatan(e.target.value)}
              placeholder="Keadaan yang teramati di lapangan, atau hal lain yang menjelaskan perubahan."
            />
          </div>
          {nilai.error && (
            <Galat
              judul="Penilaian tidak dapat dihitung"
              pesan={
                nilai.error instanceof GalatApi
                  ? nilai.error.message
                  : "Terjadi kesalahan yang tidak terduga."
              }
            />
          )}
        </div>
      )}
    </Jendela>
  );
}

// ---------------------------------------------------------------------------
export default function Monitoring() {
  const { punya } = useAuth();
  const bolehMenilai = punya(KEWENANGAN.CATAT_OUTCOME);
  const [sedangDinilai, setSedangDinilai] = useState<string | null>(null);
  const [hanyaBelum, setHanyaBelum] = useState(false);

  const rekap = useQuery({
    queryKey: ["monitoring-rekap"],
    queryFn: () => api.ambil<DataRekap>("/intervensi/rekap/monitoring"),
  });

  const daftar = useQuery({
    queryKey: ["monitoring-daftar", hanyaBelum],
    queryFn: () =>
      api.ambil<DataDaftar>(
        `/intervensi?batas=60&hanya_belum_dinilai=${hanyaBelum ? "true" : "false"}`,
      ),
  });

  if (rekap.isLoading) return <Memuat pesan="Memuat capaian intervensi..." penuh />;
  if (rekap.error)
    return (
      <Galat
        pesan={rekap.error instanceof GalatApi ? rekap.error.message : "Gagal memuat data."}
      />
    );

  const d = rekap.data!;
  const jumlahIntervensi = d.per_status.reduce((n, s) => n + s.jumlah, 0);
  const membaik = d.penilaian?.find((p) => p.penilaian === "membaik");
  const selisihPembanding =
    membaik && membaik.persen_pembanding !== null
      ? membaik.persen - membaik.persen_pembanding
      : null;

  const dataBanding = (d.penilaian ?? []).map((p) => ({
    penilaian: LABEL_PENILAIAN[p.penilaian] ?? p.penilaian,
    kunci: p.penilaian,
    intervensi: p.persen,
    pembanding: p.persen_pembanding ?? 0,
  }));

  return (
    <div className="space-y-4">
      <header>
        <h1 className="text-lg font-semibold text-slate-800">Monitoring Hasil</h1>
        <p className="mt-0.5 text-sm text-slate-500">
          Apa yang terjadi pada keluarga setelah intervensi tercatat, dibandingkan dengan
          keluarga sebanding yang tidak menerimanya.
        </p>
      </header>

      <Penafian judul="Perubahan, bukan sebab">{d.penafian}</Penafian>

      {/* --- Corong: dari penyaluran sampai penilaian --------------------- */}
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <KartuStat
          ikon={HandCoins}
          label="Intervensi tercatat"
          nilai={format.angka(jumlahIntervensi)}
          keterangan="Penyaluran yang tertaut ke kasus hasil deteksi"
        />
        <KartuStat
          ikon={ClipboardCheck}
          label="Sudah dinilai hasilnya"
          nilai={format.angka(d.dinilai)}
          keterangan={
            jumlahIntervensi
              ? `${format.persen((d.dinilai / jumlahIntervensi) * 100)} dari seluruh intervensi`
              : undefined
          }
        />
        <KartuStat
          ikon={ScaleIcon}
          label="Selisih terhadap pembanding"
          nilai={selisihPembanding === null ? "–" : `${selisihPembanding > 0 ? "+" : ""}${format.desimal(selisihPembanding, 1)} pp`}
          keterangan="Kelebihan tingkat membaik di atas kelompok pembanding"
        />
        <KartuStat
          ikon={Activity}
          label="Keluar dari kemiskinan"
          nilai={format.angka(d.keluar_dari_miskin)}
          keterangan={`${format.angka(d.masuk_ke_miskin)} keluarga justru jatuh miskin pada rentang yang sama`}
        />
      </div>

      {/* --- Perbandingan: inti seluruh halaman --------------------------- */}
      <Kartu
        judul="Capaian dibandingkan kelompok pembanding"
        keterangan={d.pembanding?.keterangan}
      >
        {!d.penilaian?.length ? (
          <p className="text-sm text-slate-500">{d.keterangan ?? "Belum ada data."}</p>
        ) : (
          <>
            <div className="mb-3 flex flex-wrap items-center gap-4 text-xs text-slate-600">
              <span className="flex items-center gap-1.5">
                <span
                  className="inline-block h-2.5 w-2.5 rounded-sm"
                  style={{ backgroundColor: WARNA_PENILAIAN.membaik }}
                />
                Menerima intervensi
              </span>
              <span className="flex items-center gap-1.5">
                <span
                  className="inline-block h-2.5 w-2.5 rounded-sm"
                  style={{ backgroundColor: WARNA_PEMBANDING }}
                />
                Pembanding: tidak menerima apa pun
              </span>
            </div>

            <ResponsiveContainer width="100%" height={210}>
              <BarChart
                data={dataBanding}
                layout="vertical"
                margin={{ top: 4, right: 56, bottom: 4, left: 4 }}
                barGap={2}
              >
                <CartesianGrid stroke={TINTA.kisi} strokeDasharray="3 3" horizontal={false} />
                <XAxis
                  type="number"
                  domain={[0, 100]}
                  tick={{ fontSize: 11, fill: TINTA.kedua }}
                  axisLine={false}
                  tickLine={false}
                  tickFormatter={(v) => `${v}%`}
                />
                <YAxis
                  type="category"
                  dataKey="penilaian"
                  tick={{ fontSize: 12, fill: TINTA.kedua }}
                  axisLine={false}
                  tickLine={false}
                  width={84}
                />
                <Tooltip content={<TooltipBanding />} cursor={{ fill: "rgba(15,23,42,0.04)" }} />
                <Bar dataKey="intervensi" name="menerima intervensi" radius={[0, 4, 4, 0]} barSize={14}>
                  {dataBanding.map((b) => (
                    <Cell key={b.kunci} fill={WARNA_PENILAIAN[b.kunci] ?? TINTA.kedua} />
                  ))}
                </Bar>
                <Bar
                  dataKey="pembanding"
                  name="pembanding"
                  fill={WARNA_PEMBANDING}
                  radius={[0, 4, 4, 0]}
                  barSize={14}
                />
              </BarChart>
            </ResponsiveContainer>

            <table className="mt-2 w-full text-sm">
              <thead>
                <tr className="text-2xs uppercase tracking-wide text-slate-400">
                  <th className="py-1 text-left font-medium">Penilaian</th>
                  <th className="py-1 text-right font-medium">Keluarga</th>
                  <th className="py-1 text-right font-medium">Intervensi</th>
                  <th className="py-1 text-right font-medium">Pembanding</th>
                  <th className="py-1 text-right font-medium">Selisih</th>
                </tr>
              </thead>
              <tbody>
                {d.penilaian.map((p) => {
                  const selisih =
                    p.persen_pembanding === null ? null : p.persen - p.persen_pembanding;
                  return (
                    <tr key={p.penilaian} className="border-t border-slate-100">
                      <td className="py-1.5">
                        <span className="flex items-center gap-1.5">
                          <span
                            className="inline-block h-2 w-2 rounded-sm"
                            style={{ backgroundColor: WARNA_PENILAIAN[p.penilaian] }}
                          />
                          {LABEL_PENILAIAN[p.penilaian] ?? p.penilaian}
                        </span>
                      </td>
                      <td className="angka py-1.5 text-right text-slate-600">
                        {format.angka(p.jumlah)}
                      </td>
                      <td className="angka py-1.5 text-right font-medium text-slate-800">
                        {format.persen(p.persen)}
                      </td>
                      <td className="angka py-1.5 text-right text-slate-500">
                        {p.persen_pembanding === null ? "–" : format.persen(p.persen_pembanding)}
                      </td>
                      <td className="angka py-1.5 text-right font-semibold text-slate-800">
                        {selisih === null
                          ? "–"
                          : `${selisih > 0 ? "+" : ""}${format.desimal(selisih, 1)} pp`}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>

            <p className="mt-3 text-xs leading-relaxed text-slate-500">
              Selisih skor kerentanan rata-rata {format.desimal(d.selisih_skor_rata)} poin.
              Perubahan disebut bermakna bila melampaui {format.desimal(d.ambang_perubahan_bermakna, 0)} poin,
              kira-kira nol koma tujuh simpangan baku perubahan skor antargelombang.
              Sebanyak {format.angka(d.pembanding?.tercocokkan)} dari {format.angka(d.pembanding?.dari)} intervensi
              berhasil dicocokkan dengan kelompok pembanding.
            </p>
          </>
        )}
      </Kartu>

      {/* --- Per program -------------------------------------------------- */}
      {!!d.per_program?.length && (
        <Kartu
          judul="Menurut program"
          keterangan={`Hanya program dengan sekurangnya ${d.ambang_sel_kecil ?? 10} intervensi yang dinilai. Angka ini tidak membandingkan mutu program - keluarga yang menerimanya berbeda-beda sejak awal.`}
        >
          <table className="w-full text-sm">
            <thead>
              <tr className="text-2xs uppercase tracking-wide text-slate-400">
                <th className="py-1 text-left font-medium">Program</th>
                <th className="py-1 text-right font-medium">Dinilai</th>
                <th className="py-1 text-right font-medium">Membaik</th>
                <th className="py-1 text-right font-medium">Selisih skor</th>
              </tr>
            </thead>
            <tbody>
              {d.per_program.map((p) => (
                <tr key={p.program} className="border-t border-slate-100">
                  <td className="py-1.5 font-medium text-slate-700">{p.program}</td>
                  <td className="angka py-1.5 text-right text-slate-600">{format.angka(p.dinilai)}</td>
                  <td className="angka py-1.5 text-right text-slate-800">
                    {format.persen(p.persen_membaik)}
                  </td>
                  <td className="angka py-1.5 text-right text-slate-600">
                    {p.selisih_rata > 0 ? "+" : ""}
                    {format.desimal(p.selisih_rata)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Kartu>
      )}

      {/* --- Daftar intervensi -------------------------------------------- */}
      <Kartu
        judul="Intervensi tercatat"
        keterangan="Penyaluran yang tertaut ke kasus hasil deteksi sistem."
        aksi={
          <label className="flex cursor-pointer items-center gap-1.5 text-xs text-slate-600">
            <input
              type="checkbox"
              checked={hanyaBelum}
              onChange={(e) => setHanyaBelum(e.target.checked)}
              className="rounded border-slate-300"
            />
            Hanya yang belum dinilai
          </label>
        }
        padat
      >
        {daftar.isLoading ? (
          <div className="p-4">
            <Memuat pesan="Memuat daftar..." />
          </div>
        ) : !daftar.data?.intervensi.length ? (
          <p className="p-4 text-sm text-slate-500">Tidak ada intervensi yang cocok.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-100 text-2xs uppercase tracking-wide text-slate-400">
                  <th className="px-4 py-2 text-left font-medium">Kode</th>
                  <th className="px-2 py-2 text-left font-medium">Program</th>
                  <th className="px-2 py-2 text-left font-medium">Wilayah</th>
                  <th className="px-2 py-2 text-left font-medium">Status</th>
                  <th className="px-2 py-2 text-right font-medium">Skor</th>
                  <th className="px-2 py-2 text-left font-medium">Penilaian</th>
                  {bolehMenilai && <th className="px-4 py-2 text-right font-medium">Aksi</th>}
                </tr>
              </thead>
              <tbody>
                {daftar.data.intervensi.map((b) => (
                  <tr key={b.kode} className="border-b border-slate-50 hover:bg-slate-50/60">
                    <td className="angka px-4 py-2 text-xs text-slate-500">{b.kode}</td>
                    <td className="px-2 py-2">
                      <div className="font-medium text-slate-700">{b.program}</div>
                      {b.opd && <div className="text-2xs text-slate-400">{b.opd}</div>}
                    </td>
                    <td className="px-2 py-2 text-xs text-slate-600">
                      {b.pekon}
                      <span className="text-slate-400"> &middot; {b.kecamatan}</span>
                    </td>
                    <td className="px-2 py-2 text-xs text-slate-600">
                      {LABEL_STATUS[b.status] ?? b.status}
                    </td>
                    <td className="angka px-2 py-2 text-right text-xs text-slate-600">
                      {b.skor_sebelum === null
                        ? "–"
                        : `${format.desimal(b.skor_sebelum, 0)} → ${format.desimal(b.skor_sesudah, 0)}`}
                    </td>
                    <td className="px-2 py-2">
                      {b.penilaian ? (
                        <span className="flex items-center gap-1.5 text-xs text-slate-700">
                          <span
                            className="inline-block h-2 w-2 rounded-sm"
                            style={{ backgroundColor: WARNA_PENILAIAN[b.penilaian] }}
                          />
                          {LABEL_PENILAIAN[b.penilaian] ?? b.penilaian}
                        </span>
                      ) : (
                        <span className="text-xs text-slate-400">Belum dinilai</span>
                      )}
                    </td>
                    {bolehMenilai && (
                      <td className="px-4 py-2 text-right">
                        <button
                          type="button"
                          className="tombol-halus text-xs"
                          onClick={() => setSedangDinilai(b.kode)}
                        >
                          {b.siap_dinilai ? "Nilai hasil" : "Nilai ulang"}
                        </button>
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Kartu>

      {sedangDinilai && (
        <JendelaNilai kode={sedangDinilai} onTutup={() => setSedangDinilai(null)} />
      )}
    </div>
  );
}
