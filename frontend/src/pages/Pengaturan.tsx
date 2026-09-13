/**
 * Pengaturan layanan AI - memilih penyedia tanpa menyentuh berkas konfigurasi.
 *
 * Urutan pada layar ini mengikuti urutan orang mengambil keputusan, bukan
 * urutan bidang pada berkas ``.env``: pilih penyedia, masukkan kunci, ambil
 * daftar modelnya, uji, baru simpan. Nama model sengaja tidak pernah perlu
 * diketik dari ingatan - salah ketik nama model adalah sebab kegagalan yang
 * paling sering, dan pesan galatnya paling tidak menolong.
 *
 * Dua hal yang disampaikan terus-menerus kepada pemakai, karena keduanya
 * menyangkut kepercayaan:
 *
 * Pertama, kunci yang sudah tersimpan **tidak dapat ditampilkan kembali** -
 * hanya bentuk tersamarnya. Membiarkan administrator menarik kembali kunci
 * lewat antarmuka berarti membiarkan siapa pun yang meminjam sesinya
 * melakukan hal yang sama.
 *
 * Kedua, **penghalang pengenal pribadi berlaku bagi penyedia mana pun**.
 * Mengganti penyedia tidak pernah melonggarkan pemeriksaan itu. Pilihan
 * "model lokal" ditampilkan sejajar dengan yang lain justru karena ia
 * menjawab pertanyaan kedaulatan data secara mutlak: tidak ada yang keluar
 * dari jaringan pemerintah daerah.
 */

import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  CheckCircle2,
  KeyRound,
  Loader2,
  RefreshCw,
  ServerCog,
  ShieldCheck,
  XCircle,
} from "lucide-react";
import { Galat, Kartu, Memuat, Penafian } from "../components/dasar";
import { api, GalatApi } from "../lib/api";
import { KEWENANGAN, useAuth } from "../lib/auth";

// ---------------------------------------------------------------------------
interface ButirKatalog {
  kode: string;
  nama: string;
  base_url: string;
  keterangan: string;
  butuh_kunci: boolean;
  model_disarankan: string[];
  petunjuk_kunci: string | null;
}

interface DataPengaturan {
  berlaku: {
    penyedia: string;
    base_url: string;
    model: string;
    api_key_tersamar: string | null;
    ada_kunci: boolean;
    aktif: boolean;
    maks_token: number;
    suhu: number;
    batas_waktu_detik: number;
    penghalang_pii: boolean;
  };
  siap: boolean;
  alasan_belum_siap: string | null;
  katalog: ButirKatalog[];
  keterangan_kunci: string;
  penghalang_pii: string;
}

interface HasilUji {
  berhasil: boolean;
  model?: string;
  durasi_ms?: number;
  contoh_jawaban?: string;
  pesan?: string;
}

// Nilai penanda yang memberi tahu peladen agar mempertahankan kunci yang ada.
const KUNCI_TETAP = "__TETAP__";

// ---------------------------------------------------------------------------
export default function Pengaturan() {
  const { punya } = useAuth();
  const klien = useQueryClient();

  const { data, isLoading, error } = useQuery({
    queryKey: ["pengaturan-ai"],
    queryFn: () => api.ambil<DataPengaturan>("/pengaturan/ai"),
    enabled: punya(KEWENANGAN.KELOLA_SISTEM),
  });

  const [penyedia, setPenyedia] = useState("");
  const [baseUrl, setBaseUrl] = useState("");
  const [model, setModel] = useState("");
  const [kunci, setKunci] = useState("");
  const [maksToken, setMaksToken] = useState(2400);
  const [suhu, setSuhu] = useState(0.2);
  const [modelTersedia, setModelTersedia] = useState<string[]>([]);
  const [lanjutan, setLanjutan] = useState(false);
  const [batasWaktu, setBatasWaktu] = useState(60);

  // Isi borang dari pengaturan yang berlaku, sekali saja saat data tiba.
  useEffect(() => {
    if (!data) return;
    setPenyedia(data.berlaku.penyedia);
    setBaseUrl(data.berlaku.base_url);
    setModel(data.berlaku.model);
    setMaksToken(data.berlaku.maks_token);
    setSuhu(data.berlaku.suhu);
    setBatasWaktu(data.berlaku.batas_waktu_detik);
  }, [data]);

  // ---------------------------------------------------------------------
  // SELURUH hook harus berada di atas setiap cabang keluar-awal.
  //
  // Versi pertama halaman ini menaruh ketiga useMutation di bawah cabang
  // "if (isLoading) return", sehingga render pertama memanggil nol hook
  // mutasi dan render kedua memanggil tiga. React membandingkan jumlah hook
  // antarrender; begitu jumlahnya berubah, seluruh pohon komponen dibatalkan
  // dan yang tersisa di layar hanyalah halaman kosong - tanpa pesan galat
  // apa pun yang menjelaskan sebabnya.
  //
  // TypeScript tidak dapat menangkapnya: ini kekeliruan waktu jalan, bukan
  // kekeliruan tipe. Karena itu badan permintaan di bawah membaca state,
  // bukan objek `data`, supaya ia tetap sah dipanggil sebelum data tiba.
  // ---------------------------------------------------------------------
  const badan = () => ({
    base_url: baseUrl.trim(),
    model: model.trim(),
    api_key: kunci.trim() || KUNCI_TETAP,
    aktif: true,
    maks_token: maksToken,
    suhu,
    batas_waktu_detik: batasWaktu,
  });

  const ambilModel = useMutation({
    mutationFn: () => api.kirim<{ model: string[]; catatan: string | null }>(
      "/pengaturan/ai/model", badan()),
    onSuccess: (r) => setModelTersedia(r.model),
  });

  const uji = useMutation({
    mutationFn: () => api.kirim<HasilUji>("/pengaturan/ai/uji", badan()),
  });

  const simpan = useMutation({
    mutationFn: () => api.kirim<{ tersimpan: boolean; siap: boolean }>("/pengaturan/ai", badan()),
    onSuccess: () => {
      setKunci("");
      klien.invalidateQueries({ queryKey: ["pengaturan-ai"] });
    },
  });

  if (!punya(KEWENANGAN.KELOLA_SISTEM))
    return (
      <Galat
        judul="Tidak berwenang"
        pesan="Hanya administrator sistem yang dapat mengubah pengaturan layanan AI."
      />
    );
  if (isLoading) return <Memuat pesan="Memuat pengaturan..." penuh />;
  if (error)
    return (
      <Galat pesan={error instanceof GalatApi ? error.message : "Gagal memuat pengaturan."} />
    );
  if (!data) return <Memuat pesan="Memuat pengaturan..." penuh />;

  const d = data;
  const terpilih = d.katalog.find((p) => p.kode === penyedia);
  const butuhKunci = terpilih?.butuh_kunci ?? true;
  const adaKunci = kunci.trim().length > 0 || d.berlaku.ada_kunci;

  function pilihPenyedia(p: ButirKatalog) {
    setPenyedia(p.kode);
    setModelTersedia([]);
    uji.reset();
    simpan.reset();
    if (p.base_url) setBaseUrl(p.base_url);
    // Model bawaan hanya diusulkan bila yang sekarang jelas milik penyedia
    // lain; kalau tidak, pilihan pengguna dibiarkan apa adanya.
    if (p.model_disarankan.length && !p.model_disarankan.includes(model)) {
      setModel(p.model_disarankan[0]);
    }
  }

  return (
    <div className="space-y-4">
      <header>
        <h1 className="text-lg font-semibold text-slate-800">Pengaturan Layanan AI</h1>
        <p className="mt-0.5 text-sm text-slate-500">
          Pilih penyedia model bahasa untuk Policy Copilot. Seluruh skor, rekomendasi, dan
          simulasi tetap dihitung di dalam sistem ini — layanan AI hanya menyusun kalimatnya.
        </p>
      </header>

      {/* --- Keadaan sekarang ------------------------------------------- */}
      <div
        className={`kartu flex flex-wrap items-center gap-3 px-4 py-3 ${
          d.siap ? "border-emerald-200 bg-emerald-50/50" : "border-amber-200 bg-amber-50/50"
        }`}
      >
        {d.siap ? (
          <CheckCircle2 size={18} className="shrink-0 text-emerald-600" />
        ) : (
          <XCircle size={18} className="shrink-0 text-amber-600" />
        )}
        <div className="min-w-0 flex-1">
          <div className="text-sm font-medium text-slate-800">
            {d.siap ? "Layanan AI aktif" : "Layanan AI belum siap"}
          </div>
          <div className="mt-0.5 text-xs text-slate-600">
            {d.siap ? (
              <>
                <span className="font-medium">{d.berlaku.model}</span> melalui{" "}
                {terpilih?.nama ?? d.berlaku.base_url}
                {d.berlaku.api_key_tersamar && (
                  <span className="angka ml-2 text-slate-400">
                    kunci {d.berlaku.api_key_tersamar}
                  </span>
                )}
              </>
            ) : (
              (d.alasan_belum_siap ??
                "Copilot berjalan dalam mode luring: seluruh angka tetap tersedia, hanya kalimatnya yang memakai templat.")
            )}
          </div>
        </div>
      </div>

      {/* --- Penyedia ----------------------------------------------------- */}
      <Kartu
        judul="Penyedia"
        keterangan="Seluruh pilihan berbicara protokol yang sama. Yang membedakan hanya alamat, biaya, dan tempat data diproses."
      >
        <div className="grid gap-2 sm:grid-cols-2">
          {d.katalog.map((p) => {
            const aktif = p.kode === penyedia;
            return (
              <button
                key={p.kode}
                type="button"
                onClick={() => pilihPenyedia(p)}
                aria-pressed={aktif}
                className={`rounded-lg border px-3 py-2.5 text-left transition ${
                  aktif
                    ? "border-sky-400 bg-sky-50 ring-1 ring-sky-200"
                    : "border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50"
                }`}
              >
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-slate-800">{p.nama}</span>
                  {!p.butuh_kunci && (
                    <span className="rounded bg-emerald-100 px-1.5 py-0.5 text-2xs font-medium text-emerald-800">
                      tanpa kunci
                    </span>
                  )}
                  {aktif && <CheckCircle2 size={13} className="ml-auto shrink-0 text-sky-600" />}
                </div>
                <p className="mt-1 text-xs leading-relaxed text-slate-500">{p.keterangan}</p>
              </button>
            );
          })}
        </div>
      </Kartu>

      {/* --- Rincian ------------------------------------------------------ */}
      <Kartu judul="Sambungan">
        <div className="space-y-4">
          <div>
            <label htmlFor="base-url" className="mb-1 block text-xs font-medium text-slate-600">
              Alamat API
            </label>
            <input
              id="base-url"
              className="masukan angka"
              value={baseUrl}
              onChange={(e) => setBaseUrl(e.target.value)}
              placeholder="https://api.penyedia.com/v1"
              spellCheck={false}
            />
          </div>

          {butuhKunci && (
            <div>
              <label htmlFor="kunci" className="mb-1 block text-xs font-medium text-slate-600">
                Kunci API
                {d.berlaku.ada_kunci && (
                  <span className="ml-1 font-normal text-slate-400">
                    — tersimpan {d.berlaku.api_key_tersamar}, biarkan kosong bila tidak diganti
                  </span>
                )}
              </label>
              <div className="relative">
                <KeyRound
                  size={14}
                  className="pointer-events-none absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-400"
                />
                <input
                  id="kunci"
                  type="password"
                  className="masukan angka pl-8"
                  value={kunci}
                  onChange={(e) => setKunci(e.target.value)}
                  placeholder={d.berlaku.ada_kunci ? "••••••••••••" : "Tempelkan kunci di sini"}
                  autoComplete="off"
                  spellCheck={false}
                />
              </div>
              {terpilih?.petunjuk_kunci && (
                <p className="mt-1 text-2xs text-slate-500">{terpilih.petunjuk_kunci}</p>
              )}
            </div>
          )}

          <div>
            <div className="mb-1 flex items-end justify-between gap-2">
              <label htmlFor="model" className="block text-xs font-medium text-slate-600">
                Model
              </label>
              <button
                type="button"
                className="tombol-halus text-2xs"
                disabled={ambilModel.isPending || !baseUrl.trim() || (butuhKunci && !adaKunci)}
                onClick={() => ambilModel.mutate()}
              >
                {ambilModel.isPending ? (
                  <span className="flex items-center gap-1">
                    <Loader2 size={11} className="animate-spin" /> Mengambil...
                  </span>
                ) : (
                  <span className="flex items-center gap-1">
                    <RefreshCw size={11} /> Ambil daftar model
                  </span>
                )}
              </button>
            </div>
            <input
              id="model"
              className="masukan angka"
              list="daftar-model"
              value={model}
              onChange={(e) => setModel(e.target.value)}
              placeholder="nama-model"
              spellCheck={false}
            />
            <datalist id="daftar-model">
              {(modelTersedia.length ? modelTersedia : (terpilih?.model_disarankan ?? [])).map(
                (m) => (
                  <option key={m} value={m} />
                ),
              )}
            </datalist>
            <p className="mt-1 text-2xs text-slate-500">
              {modelTersedia.length
                ? `${modelTersedia.length} model tersedia untuk kunci ini — ketik untuk menyaring.`
                : terpilih?.model_disarankan.length
                  ? `Disarankan: ${terpilih.model_disarankan.join(", ")}`
                  : "Ketik nama model sesuai dokumentasi penyedia."}
            </p>
          </div>

          <button
            type="button"
            className="text-2xs font-medium text-slate-500 hover:text-slate-700"
            onClick={() => setLanjutan((v) => !v)}
          >
            {lanjutan ? "Sembunyikan" : "Tampilkan"} pengaturan lanjutan
          </button>

          {lanjutan && (
            <div className="grid gap-4 rounded-lg bg-slate-50 p-3 sm:grid-cols-2">
              <div>
                <label htmlFor="maks-token" className="mb-1 block text-xs font-medium text-slate-600">
                  Batas token jawaban
                </label>
                <input
                  id="maks-token"
                  type="number"
                  className="masukan angka"
                  min={64}
                  max={32000}
                  step={100}
                  value={maksToken}
                  onChange={(e) => setMaksToken(Number(e.target.value))}
                />
                <p className="mt-1 text-2xs text-slate-500">
                  Model penalar menghabiskan sebagian anggaran ini untuk berpikir sebelum
                  menjawab. Di bawah 2000 sebagian di antaranya tidak sempat menuliskan
                  jawabannya sama sekali.
                </p>
              </div>
              <div>
                <label htmlFor="suhu" className="mb-1 block text-xs font-medium text-slate-600">
                  Suhu
                </label>
                <input
                  id="suhu"
                  type="number"
                  className="masukan angka"
                  min={0}
                  max={2}
                  step={0.1}
                  value={suhu}
                  onChange={(e) => setSuhu(Number(e.target.value))}
                />
                <p className="mt-1 text-2xs text-slate-500">
                  Rendah berarti jawaban lebih konsisten. Keluarga gpt-5 dan o-series
                  mengabaikannya; NADI menyesuaikan sendiri.
                </p>
              </div>
            </div>
          )}
        </div>
      </Kartu>

      {/* --- Uji dan simpan ----------------------------------------------- */}
      <Kartu judul="Uji lalu simpan">
        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            className="tombol-halus"
            disabled={uji.isPending || !model.trim() || !baseUrl.trim()}
            onClick={() => uji.mutate()}
          >
            {uji.isPending ? (
              <span className="flex items-center gap-1.5">
                <Loader2 size={13} className="animate-spin" /> Menguji...
              </span>
            ) : (
              <span className="flex items-center gap-1.5">
                <ServerCog size={13} /> Uji sambungan
              </span>
            )}
          </button>
          <button
            type="button"
            className="tombol-utama"
            disabled={simpan.isPending || !model.trim() || !baseUrl.trim()}
            onClick={() => simpan.mutate()}
          >
            {simpan.isPending ? "Menyimpan..." : "Simpan pengaturan"}
          </button>
          <span className="text-2xs text-slate-500">
            Berlaku seketika; peladen tidak perlu dijalankan ulang.
          </span>
        </div>

        {uji.data && (
          <div
            className={`mt-3 rounded-lg border px-3 py-2.5 ${
              uji.data.berhasil
                ? "border-emerald-200 bg-emerald-50"
                : "border-rose-200 bg-rose-50"
            }`}
          >
            {uji.data.berhasil ? (
              <>
                <div className="flex items-center gap-1.5 text-sm font-medium text-emerald-900">
                  <CheckCircle2 size={14} /> Berhasil — {uji.data.model} dalam{" "}
                  {uji.data.durasi_ms} ms
                </div>
                <p className="mt-1 text-xs leading-relaxed text-slate-600">
                  {uji.data.contoh_jawaban}
                </p>
              </>
            ) : (
              <>
                <div className="flex items-center gap-1.5 text-sm font-medium text-rose-900">
                  <XCircle size={14} /> Gagal
                </div>
                <p className="mt-1 text-xs leading-relaxed text-rose-800">{uji.data.pesan}</p>
              </>
            )}
          </div>
        )}

        {ambilModel.error && (
          <p className="mt-2 text-xs text-rose-700">
            {ambilModel.error instanceof GalatApi
              ? ambilModel.error.message
              : "Gagal mengambil daftar model."}
          </p>
        )}
        {simpan.error && (
          <p className="mt-2 text-xs text-rose-700">
            {simpan.error instanceof GalatApi ? simpan.error.message : "Gagal menyimpan."}
          </p>
        )}
        {simpan.data?.tersimpan && (
          <p className="mt-2 flex items-center gap-1.5 text-xs font-medium text-emerald-800">
            <CheckCircle2 size={13} /> Tersimpan dan langsung berlaku.
          </p>
        )}
      </Kartu>

      <Kartu judul="Keamanan" keterangan="Berlaku bagi penyedia mana pun yang dipilih.">
        <div className="space-y-2.5 text-xs leading-relaxed text-slate-600">
          <div className="flex items-start gap-2">
            <ShieldCheck size={14} className="mt-0.5 shrink-0 text-emerald-600" />
            <span>{d.penghalang_pii}</span>
          </div>
          <div className="flex items-start gap-2">
            <KeyRound size={14} className="mt-0.5 shrink-0 text-slate-400" />
            <span>{d.keterangan_kunci}</span>
          </div>
        </div>
        <Penafian>
          Mengganti penyedia tidak mengubah satu pun angka pada sistem ini. Skor kerentanan,
          faktor risiko, rekomendasi program, dan hasil simulasi seluruhnya dihitung secara
          lokal sebelum layanan AI dipanggil. Bila layanan AI mati, yang hilang adalah gaya
          bahasa jawabannya — bukan analisisnya.
        </Penafian>
      </Kartu>
    </div>
  );
}
