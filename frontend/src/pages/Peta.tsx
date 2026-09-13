/**
 * GeoAI Poverty Radar - sebaran kerentanan pada peta.
 *
 * Beberapa keputusan yang menentukan:
 *
 * **Warna peta memakai satu rona, bukan hijau-kuning-merah.** Tingkat kemiskinan
 * sebuah pekon adalah BESARAN, bukan keadaan berjenjang. Satu rona dari terang
 * ke gelap menyampaikan "lebih gelap berarti lebih banyak" tanpa perlu
 * dijelaskan, sementara skala pelangi memaksa pembaca menghafal ambang yang
 * sebenarnya tidak ada.
 *
 * **Wilayah berjumlah keluarga terlalu sedikit tidak diwarnai.** Pada wilayah
 * sekecil itu, satu warna pada peta hampir sama dengan menunjuk satu rumah -
 * dan agregat berhenti menjadi agregat.
 *
 * Batas wilayah berasal dari layer batas desa Badan Informasi Geospasial, bukan
 * gambar pendekatan. Kode wilayahnya cocok seluruhnya dengan basis data.
 */

import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { GeoJSON, MapContainer, TileLayer } from "react-leaflet";
import type { Layer, PathOptions } from "leaflet";
import type { Feature, FeatureCollection } from "geojson";
import { EyeOff, Layers } from "lucide-react";
import { api, format } from "../lib/api";
import { RAMPA_SEKUENSIAL, warnaSekuensial } from "../lib/warna";
import { Galat, Kartu, Memuat, Penafian } from "../components/dasar";

const PUSAT: [number, number] = [-5.336, 104.933];

type Ukuran = "persentase_miskin" | "skor_rata_rata" | "persen_penerima_bantuan" | "persen_hunian_layak";

const UKURAN: { nilai: Ukuran; label: string; satuan: string; keterangan: string; terbalik?: boolean }[] = [
  {
    nilai: "persentase_miskin",
    label: "Tingkat kemiskinan",
    satuan: "% keluarga",
    keterangan: "Bagian keluarga dengan pengeluaran di bawah garis kemiskinan",
  },
  {
    nilai: "skor_rata_rata",
    label: "Skor kerentanan rata-rata",
    satuan: "dari 100",
    keterangan: "Rata-rata perkiraan peluang jatuh atau tetap miskin pada pemutakhiran berikutnya",
  },
  {
    nilai: "persen_penerima_bantuan",
    label: "Cakupan bantuan",
    satuan: "% keluarga",
    keterangan: "Bagian keluarga yang menerima setidaknya satu program",
    terbalik: true,
  },
  {
    nilai: "persen_hunian_layak",
    label: "Hunian layak huni",
    satuan: "% keluarga",
    keterangan: "Memenuhi keempat kriteria: kecukupan luas, air minum, sanitasi, dan ketahanan bangunan",
    terbalik: true,
  },
];

interface StatWilayah {
  kode: string;
  nama: string;
  jenis: string;
  nama_induk: string | null;
  jumlah_keluarga: number;
  aman_ditampilkan: boolean;
  jumlah_miskin?: number;
  persentase_miskin?: number;
  jumlah_rentan?: number;
  skor_rata_rata?: number;
  jumlah_risiko_tinggi?: number;
  persen_sanitasi_layak?: number;
  persen_air_minum_layak?: number;
  persen_hunian_layak?: number;
  persen_penerima_bantuan?: number;
}

export default function Peta() {
  const [ukuran, setUkuran] = useState<Ukuran>("persentase_miskin");
  const [terpilih, setTerpilih] = useState<StatWilayah | null>(null);

  const batas = useQuery({
    queryKey: ["batas-wilayah"],
    queryFn: () => api.ambil<FeatureCollection>("/wilayah/batas"),
    staleTime: Infinity,
  });
  const statistik = useQuery({
    queryKey: ["statistik-desa"],
    queryFn: () => api.ambil<{ wilayah: StatWilayah[]; jumlah_disembunyikan: number; ambang_sel_kecil: number }>(
      "/wilayah/statistik?tingkat=2",
    ),
  });

  const petaStat = useMemo(() => {
    const m = new Map<string, StatWilayah>();
    statistik.data?.wilayah.forEach((w) => m.set(w.kode, w));
    return m;
  }, [statistik.data]);

  const konfig = UKURAN.find((u) => u.nilai === ukuran)!;

  const { minimum, maksimum } = useMemo(() => {
    const nilai = (statistik.data?.wilayah ?? [])
      .filter((w) => w.aman_ditampilkan)
      .map((w) => (w[ukuran] as number) ?? 0);
    if (!nilai.length) return { minimum: 0, maksimum: 1 };
    return { minimum: Math.min(...nilai), maksimum: Math.max(...nilai) };
  }, [statistik.data, ukuran]);

  function gaya(fitur?: Feature): PathOptions {
    const kode = (fitur?.properties as { KDEPUM?: string })?.KDEPUM ?? "";
    const w = petaStat.get(kode);
    if (!w || !w.aman_ditampilkan) {
      return { fillColor: "#e2e8f0", weight: 0.6, color: "#94a3b8", fillOpacity: 0.5, dashArray: "3" };
    }
    const nilai = (w[ukuran] as number) ?? 0;
    // Ukuran yang "makin tinggi makin baik" dibalik arahnya, sehingga warna
    // gelap selalu berarti "perlu perhatian" pada seluruh pilihan ukuran.
    const efektif = konfig.terbalik ? maksimum - (nilai - minimum) : nilai;
    return {
      fillColor: warnaSekuensial(efektif, minimum, maksimum),
      weight: terpilih?.kode === kode ? 2.4 : 0.6,
      color: terpilih?.kode === kode ? "#0f172a" : "#ffffff",
      fillOpacity: 0.82,
    };
  }

  function saatTiapFitur(fitur: Feature, layer: Layer) {
    const p = fitur.properties as { KDEPUM?: string; NAMOBJ?: string; WADMKC?: string };
    const w = petaStat.get(p.KDEPUM ?? "");
    layer.on({
      click: () => w && setTerpilih(w),
      mouseover: (e) => (e.target as L.Path).setStyle({ weight: 2, color: "#0f172a" }),
      mouseout: (e) => (e.target as L.Path).setStyle(gaya(fitur)),
    });
    const isi = w?.aman_ditampilkan
      ? `<strong>${p.NAMOBJ}</strong><br/><span style="color:#64748b">Kec. ${p.WADMKC}</span><br/>
         ${konfig.label}: <strong>${((w[ukuran] as number) ?? 0).toFixed(1).replace(".", ",")}</strong> ${konfig.satuan}<br/>
         <span style="color:#64748b">${format.angka(w.jumlah_keluarga)} keluarga terdata</span>`
      : `<strong>${p.NAMOBJ}</strong><br/><span style="color:#64748b">Angka disembunyikan: jumlah keluarga di bawah ambang penyajian</span>`;
    layer.bindTooltip(isi, { sticky: true, className: "text-xs" });
  }

  if (batas.isLoading || statistik.isLoading)
    return <Memuat pesan="Memuat batas wilayah dan statistik..." />;
  if (batas.error) return <Galat pesan={(batas.error as Error).message} />;

  return (
    <div className="space-y-5">
      {/* Penyaring dalam satu baris di atas peta */}
      <div className="flex flex-wrap items-center gap-2">
        <span className="flex items-center gap-1.5 text-xs font-medium text-slate-500">
          <Layers size={14} /> Ukuran yang dipetakan
        </span>
        {UKURAN.map((u) => (
          <button
            key={u.nilai}
            onClick={() => setUkuran(u.nilai)}
            className={`rounded-md px-3 py-1.5 text-xs font-medium transition-colors ${
              ukuran === u.nilai
                ? "bg-nadi-700 text-white"
                : "border border-slate-300 bg-white text-slate-700 hover:bg-slate-50"
            }`}
          >
            {u.label}
          </button>
        ))}
      </div>

      <div className="grid gap-5 lg:grid-cols-[1fr_320px]">
        <Kartu judul={konfig.label} keterangan={konfig.keterangan} padat>
          <div className="h-[520px] w-full overflow-hidden rounded-b-lg">
            <MapContainer center={PUSAT} zoom={11} className="h-full w-full" scrollWheelZoom>
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
              />
              {batas.data && (
                <GeoJSON
                  key={`${ukuran}-${terpilih?.kode ?? ""}`}
                  data={batas.data}
                  style={gaya}
                  onEachFeature={saatTiapFitur}
                />
              )}
            </MapContainer>
          </div>

          {/* Skala warna */}
          <div className="flex items-center gap-3 border-t border-slate-100 px-4 py-3">
            <span className="text-2xs text-slate-500">
              {konfig.terbalik ? "Cakupan tinggi" : format.desimal(minimum, 1)}
            </span>
            <div className="flex h-3 flex-1 overflow-hidden rounded">
              {RAMPA_SEKUENSIAL.map((w) => (
                <div key={w} className="flex-1" style={{ backgroundColor: w }} />
              ))}
            </div>
            <span className="text-2xs text-slate-500">
              {konfig.terbalik ? "Cakupan rendah" : format.desimal(maksimum, 1)}
            </span>
            <span className="ml-2 flex items-center gap-1 text-2xs text-slate-400">
              <EyeOff size={11} /> disembunyikan
            </span>
            <div className="h-3 w-6 rounded border border-slate-300 bg-slate-200" />
          </div>
        </Kartu>

        {/* Panel rincian */}
        <div className="space-y-4">
          {terpilih ? (
            <Kartu judul={terpilih.nama} keterangan={`Kec. ${terpilih.nama_induk ?? "-"} · ${terpilih.jenis}`}>
              {terpilih.aman_ditampilkan ? (
                <dl className="space-y-2.5 text-sm">
                  {[
                    ["Keluarga terdata", format.angka(terpilih.jumlah_keluarga)],
                    ["Keluarga miskin", `${format.angka(terpilih.jumlah_miskin)} (${format.persen(terpilih.persentase_miskin, 1)})`],
                    ["Rentan, belum miskin", format.angka(terpilih.jumlah_rentan)],
                    ["Skor kerentanan rata-rata", format.desimal(terpilih.skor_rata_rata, 1)],
                    ["Berisiko tinggi", format.angka(terpilih.jumlah_risiko_tinggi)],
                    ["Sanitasi layak", format.persen(terpilih.persen_sanitasi_layak, 1)],
                    ["Air minum layak", format.persen(terpilih.persen_air_minum_layak, 1)],
                    ["Hunian layak huni", format.persen(terpilih.persen_hunian_layak, 1)],
                    ["Menerima bantuan", format.persen(terpilih.persen_penerima_bantuan, 1)],
                  ].map(([k, v]) => (
                    <div key={k as string} className="flex items-baseline justify-between gap-3">
                      <dt className="text-xs text-slate-500">{k}</dt>
                      <dd className="angka text-sm font-semibold text-slate-800">{v}</dd>
                    </div>
                  ))}
                </dl>
              ) : (
                <p className="text-xs leading-relaxed text-slate-500">
                  Angka wilayah ini tidak ditampilkan karena jumlah keluarganya
                  berada di bawah ambang penyajian. Pada wilayah sekecil itu, angka
                  gabungan hampir sama dengan menunjuk satu keluarga tertentu.
                </p>
              )}
            </Kartu>
          ) : (
            <Kartu judul="Pilih wilayah">
              <p className="text-xs leading-relaxed text-slate-500">
                Sentuh atau klik sebuah pekon pada peta untuk melihat rinciannya.
              </p>
            </Kartu>
          )}

          <Penafian judul="Privasi pada peta">
            {statistik.data?.jumlah_disembunyikan ?? 0} wilayah tidak diwarnai
            karena jumlah keluarganya di bawah{" "}
            {statistik.data?.ambang_sel_kecil ?? 10}. Titik keluarga tidak pernah
            ditampilkan; koordinat yang tersimpan pun sudah digeser acak dalam
            radius 250 meter.
          </Penafian>

          <Penafian judul="Sumber batas wilayah">
            Layer batas desa Badan Informasi Geospasial, 131 pekon dan kelurahan,
            dengan kode wilayah sesuai Kepmendagri Nomor 300.2.2-2138/2025.
          </Penafian>
        </div>
      </div>
    </div>
  );
}
