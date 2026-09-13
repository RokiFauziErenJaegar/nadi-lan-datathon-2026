/**
 * Household Digital Twin - profil satu keluarga sepanjang waktu.
 *
 * Layar inilah yang menjawab pertanyaan "mengapa keluarga ini muncul di
 * antrean". Tiga hal disandingkan agar jawabannya utuh: lintasan keadaan dari
 * gelombang ke gelombang, guncangan yang menimpanya, dan kontribusi tiap faktor
 * terhadap skor.
 *
 * Kontribusi faktor memakai warna divergen - merah mendorong risiko naik, biru
 * menahannya, dengan garis nol berwarna netral. Peringatan yang menyertainya
 * bukan basa-basi: nilai kontribusi menerangkan apa yang DIBACA model, bukan apa
 * yang MENYEBABKAN kemiskinan. Keduanya mudah tertukar, dan tertukarnya membuat
 * anggaran diarahkan untuk memperbaiki penanda alih-alih memperbaiki keadaan.
 */

import { useQuery } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { ArrowLeft, Home, Users, Zap } from "lucide-react";
import { api, format } from "../lib/api";
import { DIVERGEN, TINTA } from "../lib/warna";
import { Galat, Kartu, LencanaRisiko, Memuat, Penafian } from "../components/dasar";

interface Kontribusi {
  f: string;
  n: number;
  k: number;
}

interface Riwayat {
  gelombang: number;
  tanggal: string;
  pengeluaran_per_kapita: number;
  rasio_garis_kemiskinan: number;
  miskin: boolean;
  rentan: boolean;
  desil: number;
  jumlah_anggota: number;
  jumlah_program: number;
  nilai_bantuan_bulanan: number;
  cakupan_jkn: number;
  umur_data_bulan: number;
  hunian: Record<string, string | number>;
  skor: number | null;
  kategori: string | null;
  perubahan_skor: number | null;
  peringkat_kabupaten: number | null;
  faktor_dominan: string[];
  kontribusi_fitur: Kontribusi[];
}

interface Profil {
  keluarga: {
    kode: string;
    wilayah: { desa: string; kecamatan: string; jenis: string; klasifikasi: string };
    koordinat: { catatan: string };
  };
  anggota: Record<string, string | number | boolean>[];
  riwayat: Riwayat[];
  guncangan: { gelombang: number; jenis: string; sifat: string; keparahan: string; dampak_persen: number }[];
  program: { singkatan: string; nama: string; gelombang_mulai: number; gelombang_selesai: number | null; berjalan: boolean }[];
  kasus: { kode: string; label_jenis: string; tingkat_prioritas: number; ringkasan: string }[];
  ringkas: Record<string, number | string | boolean | null>;
  penafian: string;
}

interface Usulan {
  singkatan: string;
  nama: string;
  skor_kecocokan: number;
  peringkat: number;
  layak: boolean;
  opd: string[];
  tindakan: string;
  alasan: string;
  aturan_tidak_terpenuhi: string[];
  perkiraan_manfaat_bulanan: number | null;
  catatan: string | null;
}

const LABEL_FITUR: Record<string, string> = {};

export default function ProfilKeluarga() {
  const { kode = "" } = useParams();

  const profil = useQuery({
    queryKey: ["profil", kode],
    queryFn: () => api.ambil<Profil>(`/keluarga/${kode}`),
  });
  const rekomendasi = useQuery({
    queryKey: ["rekomendasi", kode],
    queryFn: () =>
      api.ambil<{ usulan: Usulan[]; faktor_dominan: string[]; paket: Record<string, unknown> }>(
        `/rekomendasi/keluarga/${kode}`,
      ),
    enabled: Boolean(profil.data),
  });

  if (profil.isLoading) return <Memuat pesan="Memuat profil keluarga..." />;
  if (profil.error) return <Galat pesan={(profil.error as Error).message} />;

  const p = profil.data!;
  const terkini = p.riwayat[p.riwayat.length - 1];
  const tren = p.riwayat.map((r) => ({
    ...r,
    label: `G${r.gelombang}`,
    garis: 1,
  }));

  const kontribusi = (terkini?.kontribusi_fitur ?? [])
    .slice(0, 8)
    .map((c) => ({
      nama: LABEL_FITUR[c.f] ?? c.f.replace(/_/g, " "),
      nilai: c.k,
      angka: c.n,
    }))
    .sort((a, b) => a.nilai - b.nilai);

  return (
    <div className="space-y-5">
      <Link to="/antrean" className="inline-flex items-center gap-1.5 text-xs text-slate-500 hover:text-slate-800">
        <ArrowLeft size={14} /> Kembali ke antrean
      </Link>

      {/* ---------- Kepala ---------- */}
      <Kartu>
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <div className="font-mono text-lg font-bold text-slate-900">{p.keluarga.kode}</div>
            <div className="mt-0.5 text-sm text-slate-600">
              {p.keluarga.wilayah.jenis === "kelurahan" ? "Kelurahan" : "Pekon"}{" "}
              {p.keluarga.wilayah.desa}, Kec. {p.keluarga.wilayah.kecamatan}
              <span className="ml-2 text-2xs text-slate-400">{p.keluarga.wilayah.klasifikasi}</span>
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-4">
            <div className="text-right">
              <div className="text-2xs text-slate-500">Skor terkini</div>
              <LencanaRisiko kategori={terkini?.kategori} skor={terkini?.skor} />
            </div>
            <div className="text-right">
              <div className="text-2xs text-slate-500">Peringkat kabupaten</div>
              <div className="angka text-lg font-bold text-slate-800">
                {terkini?.peringkat_kabupaten ? `#${format.angka(terkini.peringkat_kabupaten)}` : "–"}
              </div>
            </div>
          </div>
        </div>

        <div className="mt-4 grid gap-3 border-t border-slate-100 pt-4 sm:grid-cols-2 lg:grid-cols-4">
          {[
            [Users, "Anggota keluarga", `${p.anggota.length} orang`],
            [Home, "Pengeluaran per kapita", format.rupiah(terkini?.pengeluaran_per_kapita)],
            [Zap, "Guncangan tercatat", `${p.guncangan.length} kejadian`],
            [Users, "Program berjalan", `${p.program.filter((x) => x.berjalan).length} program`],
          ].map(([Ikon, label, nilai], i) => {
            const I = Ikon as typeof Users;
            return (
              <div key={i} className="flex items-center gap-2.5">
                <I size={16} className="shrink-0 text-slate-300" />
                <div className="min-w-0">
                  <div className="text-2xs text-slate-500">{label as string}</div>
                  <div className="angka truncate text-sm font-semibold text-slate-800">
                    {nilai as string}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </Kartu>

      {/* ---------- Lintasan ---------- */}
      <div className="grid gap-5 lg:grid-cols-2">
        <Kartu
          judul="Lintasan terhadap garis kemiskinan"
          keterangan="Nilai 1,00 berarti tepat di garis kemiskinan; di bawahnya berarti miskin"
        >
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={tren} margin={{ top: 8, right: 12, bottom: 4, left: 4 }}>
              <CartesianGrid stroke={TINTA.kisi} strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="label" tick={{ fontSize: 11, fill: TINTA.kedua }} axisLine={{ stroke: TINTA.sumbu }} tickLine={false} />
              <YAxis tick={{ fontSize: 11, fill: TINTA.kedua }} axisLine={false} tickLine={false} width={40} />
              <Tooltip
                formatter={(v: number) => [format.desimal(v, 2), "rasio garis kemiskinan"]}
                labelFormatter={(l) => `Gelombang ${String(l).slice(1)}`}
                contentStyle={{ fontSize: 12, borderRadius: 6, border: "1px solid #e2e8f0" }}
              />
              <ReferenceLine y={1} stroke={DIVERGEN.menaikkan} strokeDasharray="4 4" strokeWidth={1.5} />
              <ReferenceLine y={1.5} stroke={TINTA.sumbu} strokeDasharray="2 4" />
              <Line
                type="monotone"
                dataKey="rasio_garis_kemiskinan"
                stroke="#2a78d6"
                strokeWidth={2}
                dot={{ r: 4, strokeWidth: 2, fill: "#fff" }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
          <p className="mt-1 text-2xs text-slate-500">
            Garis putus merah adalah garis kemiskinan; garis abu-abu di atasnya adalah
            garis kerentanan (satu setengah kali garis kemiskinan).
          </p>
        </Kartu>

        <Kartu
          judul="Faktor yang membentuk skor"
          keterangan="Merah mendorong risiko naik, biru menahannya"
        >
          {kontribusi.length ? (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={kontribusi} layout="vertical" margin={{ top: 4, right: 16, bottom: 4, left: 4 }}>
                <CartesianGrid stroke={TINTA.kisi} strokeDasharray="3 3" horizontal={false} />
                <XAxis type="number" tick={{ fontSize: 10, fill: TINTA.kedua }} axisLine={false} tickLine={false} />
                <YAxis
                  type="category"
                  dataKey="nama"
                  tick={{ fontSize: 10, fill: TINTA.kedua }}
                  axisLine={false}
                  tickLine={false}
                  width={150}
                />
                <Tooltip
                  formatter={(v: number) => [format.desimal(v, 3), "kontribusi"]}
                  contentStyle={{ fontSize: 12, borderRadius: 6, border: "1px solid #e2e8f0" }}
                />
                <ReferenceLine x={0} stroke={TINTA.sumbu} strokeWidth={1.5} />
                <Bar dataKey="nilai" radius={[0, 3, 3, 0]} barSize={13}>
                  {kontribusi.map((c, i) => (
                    <Cell key={i} fill={c.nilai >= 0 ? DIVERGEN.menaikkan : DIVERGEN.menurunkan} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p className="py-8 text-center text-xs text-slate-400">
              Penjelasan rinci tersedia untuk dua gelombang terakhir.
            </p>
          )}
          <Penafian>
            Nilai ini menerangkan apa yang <em>dibaca</em> model, bukan apa yang{" "}
            <em>menyebabkan</em> kemiskinan. Memperbaiki satu penanda tidak dengan
            sendirinya memperbaiki keadaan keluarga.
          </Penafian>
        </Kartu>
      </div>

      {/* ---------- Riwayat ---------- */}
      <Kartu judul="Riwayat kondisi" keterangan="Enam gelombang pemutakhiran" padat>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[820px] text-sm">
            <thead>
              <tr className="border-b border-slate-200 text-left text-2xs uppercase tracking-wide text-slate-500">
                <th className="px-4 py-2 font-medium">Gelombang</th>
                <th className="px-3 py-2 text-right font-medium">Pengeluaran/kapita</th>
                <th className="px-3 py-2 text-right font-medium">Rasio GK</th>
                <th className="px-3 py-2 text-right font-medium">Desil</th>
                <th className="px-3 py-2 text-right font-medium">Program</th>
                <th className="px-3 py-2 text-right font-medium">Cakupan JKN</th>
                <th className="px-3 py-2 text-right font-medium">Umur data</th>
                <th className="px-4 py-2 font-medium">Risiko</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {p.riwayat.map((r) => (
                <tr key={r.gelombang} className={r.miskin ? "bg-red-50/40" : ""}>
                  <td className="px-4 py-2">
                    <div className="text-xs font-medium text-slate-700">G{r.gelombang}</div>
                    <div className="text-2xs text-slate-400">{format.tanggal(r.tanggal)}</div>
                  </td>
                  <td className="angka px-3 py-2 text-right text-slate-700">
                    {format.rupiah(r.pengeluaran_per_kapita)}
                  </td>
                  <td className="angka px-3 py-2 text-right">
                    <span className={r.miskin ? "font-semibold text-red-700" : r.rentan ? "text-amber-700" : "text-slate-700"}>
                      {format.desimal(r.rasio_garis_kemiskinan, 2)}
                    </span>
                  </td>
                  <td className="angka px-3 py-2 text-right text-slate-600">{r.desil}</td>
                  <td className="angka px-3 py-2 text-right">
                    <span className={r.jumlah_program === 0 ? "font-semibold text-amber-700" : "text-slate-600"}>
                      {r.jumlah_program}
                    </span>
                  </td>
                  <td className="angka px-3 py-2 text-right text-slate-600">
                    {format.persen(r.cakupan_jkn * 100, 0)}
                  </td>
                  <td className="angka px-3 py-2 text-right text-slate-500">{r.umur_data_bulan} bln</td>
                  <td className="px-4 py-2">
                    <LencanaRisiko kategori={r.kategori} skor={r.skor} ukuran="kecil" />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Kartu>

      {/* ---------- Guncangan, program, anggota ---------- */}
      <div className="grid gap-5 lg:grid-cols-3">
        <Kartu judul="Guncangan tercatat" keterangan="Kejadian yang mengubah keadaan secara mendadak">
          {p.guncangan.length ? (
            <ul className="space-y-2">
              {p.guncangan.map((g, i) => (
                <li key={i} className="rounded-md border border-slate-200 p-2.5">
                  <div className="flex items-start justify-between gap-2">
                    <span className="text-xs font-medium text-slate-800">{g.jenis}</span>
                    <span className="angka shrink-0 text-2xs font-semibold text-red-700">
                      {g.dampak_persen > 0 ? "+" : ""}
                      {format.desimal(g.dampak_persen, 0)}%
                    </span>
                  </div>
                  <div className="mt-0.5 text-2xs text-slate-500">
                    Gelombang {g.gelombang} · {g.keparahan} · guncangan {g.sifat}
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-xs text-slate-400">Tidak ada guncangan tercatat.</p>
          )}
        </Kartu>

        <Kartu judul="Riwayat program" keterangan="Bantuan yang pernah dan sedang diterima">
          {p.program.length ? (
            <ul className="space-y-2">
              {p.program.map((pr, i) => (
                <li key={i} className="flex items-start justify-between gap-2 rounded-md border border-slate-200 p-2.5">
                  <div className="min-w-0">
                    <div className="text-xs font-medium text-slate-800">{pr.singkatan}</div>
                    <div className="truncate text-2xs text-slate-500">{pr.nama}</div>
                  </div>
                  <span
                    className={`lencana shrink-0 border ${
                      pr.berjalan
                        ? "border-emerald-200 bg-emerald-50 text-emerald-800"
                        : "border-slate-200 bg-slate-50 text-slate-600"
                    }`}
                  >
                    {pr.berjalan ? "berjalan" : `G${pr.gelombang_mulai}–G${pr.gelombang_selesai}`}
                  </span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-xs font-medium text-amber-700">
              Keluarga ini tidak pernah menerima satu pun program bantuan.
            </p>
          )}
        </Kartu>

        <Kartu judul="Anggota keluarga" keterangan={`${p.anggota.length} orang`}>
          <ul className="space-y-2">
            {p.anggota.map((a, i) => (
              <li key={i} className="rounded-md border border-slate-200 p-2.5">
                <div className="flex items-baseline justify-between gap-2">
                  <span className="text-xs font-medium text-slate-800">{a.hubungan as string}</span>
                  <span className="angka text-2xs text-slate-500">{a.umur as number} th</span>
                </div>
                <div className="mt-0.5 text-2xs leading-relaxed text-slate-500">
                  {a.jenis_kelamin as string} · {a.pendidikan as string} · {a.kegiatan as string}
                </div>
                {(a.disabilitas !== "Tidak ada" || a.penyakit_kronis !== "Tidak ada" || a.sedang_hamil) && (
                  <div className="mt-1 flex flex-wrap gap-1">
                    {a.disabilitas !== "Tidak ada" && (
                      <span className="lencana border border-slate-200 bg-slate-50">{a.disabilitas as string}</span>
                    )}
                    {a.penyakit_kronis !== "Tidak ada" && (
                      <span className="lencana border border-amber-200 bg-amber-50 text-amber-900">
                        {a.penyakit_kronis as string}
                      </span>
                    )}
                    {a.sedang_hamil && (
                      <span className="lencana border border-sky-200 bg-sky-50 text-sky-800">hamil</span>
                    )}
                  </div>
                )}
              </li>
            ))}
          </ul>
        </Kartu>
      </div>

      {/* ---------- Rekomendasi ---------- */}
      <Kartu
        judul="Usulan intervensi"
        keterangan="Disusun dari pencocokan aturan kelayakan dengan kondisi keluarga"
      >
        {rekomendasi.isLoading ? (
          <Memuat pesan="Menyusun usulan..." />
        ) : rekomendasi.error ? (
          <Galat pesan={(rekomendasi.error as Error).message} />
        ) : (
          <>
            <div className="mb-3 flex flex-wrap items-center gap-2 text-xs">
              <span className="text-slate-500">Faktor risiko dominan:</span>
              {rekomendasi.data?.faktor_dominan.map((f) => (
                <span key={f} className="lencana border border-nadi-200 bg-nadi-50 font-mono text-nadi-800">
                  {f}
                </span>
              ))}
            </div>
            <ul className="space-y-2.5">
              {rekomendasi.data?.usulan.map((u) => (
                <li
                  key={u.singkatan}
                  className={`rounded-md border p-3 ${
                    u.peringkat === 1 ? "border-nadi-300 bg-nadi-50/50" : "border-slate-200"
                  }`}
                >
                  <div className="flex flex-wrap items-start justify-between gap-2">
                    <div className="min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="angka text-2xs font-bold text-slate-400">#{u.peringkat}</span>
                        <span className="text-sm font-semibold text-slate-800">{u.singkatan}</span>
                        <span
                          className={`lencana border ${
                            u.layak
                              ? "border-emerald-200 bg-emerald-50 text-emerald-800"
                              : "border-amber-200 bg-amber-50 text-amber-900"
                          }`}
                        >
                          {u.layak ? "syarat terpenuhi" : "bersyarat"}
                        </span>
                      </div>
                      <div className="mt-0.5 text-2xs text-slate-500">{u.nama}</div>
                    </div>
                    <div className="text-right">
                      <div className="angka text-sm font-bold text-slate-800">
                        {format.desimal(u.skor_kecocokan, 0)}
                      </div>
                      <div className="text-2xs text-slate-400">kecocokan</div>
                    </div>
                  </div>

                  <p className="mt-2 text-xs leading-relaxed text-slate-600">{u.alasan}</p>

                  {!u.layak && u.aturan_tidak_terpenuhi.length > 0 && (
                    <div className="mt-2 rounded border border-amber-200 bg-amber-50 p-2">
                      <div className="text-2xs font-semibold text-amber-900">Yang masih kurang:</div>
                      <ul className="mt-0.5 list-inside list-disc text-2xs text-amber-800">
                        {u.aturan_tidak_terpenuhi.map((a, i) => (
                          <li key={i}>{a}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {u.catatan && (
                    <p className="mt-2 rounded bg-slate-50 p-2 text-2xs leading-relaxed text-slate-600">
                      {u.catatan}
                    </p>
                  )}

                  <div className="mt-2 flex flex-wrap items-center gap-3 text-2xs text-slate-500">
                    <span className="rounded bg-nadi-50 px-1.5 py-0.5 font-medium text-nadi-800">
                      {u.opd.join(", ") || "OPD belum ditetapkan"}
                    </span>
                    <span>{u.tindakan}</span>
                    {u.perkiraan_manfaat_bulanan ? (
                      <span className="angka">
                        perkiraan {format.rupiah(u.perkiraan_manfaat_bulanan)}/bulan
                      </span>
                    ) : null}
                  </div>
                </li>
              ))}
            </ul>
          </>
        )}
      </Kartu>

      <Penafian judul="Batas penggunaan">{p.penafian}</Penafian>
    </div>
  );
}
