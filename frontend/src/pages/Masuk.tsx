/**
 * Halaman masuk.
 *
 * Daftar akun demonstrasi ditampilkan terbuka, dan itu disengaja. Cara paling
 * meyakinkan menunjukkan bahwa pembatasan akses benar-benar bekerja adalah
 * membiarkan penilai masuk sebagai pimpinan daerah, lalu mencoba membuka satu
 * keluarga - dan gagal. Pembatasan yang hanya dijelaskan selalu terdengar
 * meyakinkan; yang dapat dicoba sendiri jauh lebih sulit dibantah.
 */

import { useEffect, useState } from "react";
import { Activity, AlertCircle, ArrowUpRight, Compass, Layers3, LogIn, Radar, ShieldCheck } from "lucide-react";
import { api } from "../lib/api";
import { useAuth } from "../lib/auth";
import PilihanTampilan from "../components/PilihanTampilan";
import "../styles/masuk.css";

interface AkunDemo {
  nama_pengguna: string;
  sandi: string;
  nama_lengkap: string;
  jabatan: string;
  label_peran: string;
  cakupan: string;
}

export default function Masuk() {
  const { masuk } = useAuth();
  const [namaPengguna, setNamaPengguna] = useState("dinsos");
  const [sandi, setSandi] = useState("NadiDinsos#2026");
  const [galat, setGalat] = useState<string | null>(null);
  const [sibuk, setSibuk] = useState(false);
  const [akun, setAkun] = useState<AkunDemo[]>([]);

  useEffect(() => {
    api
      .ambil<{ akun: AkunDemo[] }>("/akun-demo")
      .then((d) => setAkun(d.akun))
      .catch(() => setAkun([]));
  }, []);

  async function kirim(e: React.FormEvent) {
    e.preventDefault();
    setGalat(null);
    setSibuk(true);
    try {
      await masuk(namaPengguna, sandi);
    } catch (err) {
      setGalat(err instanceof Error ? err.message : "Gagal masuk.");
    } finally {
      setSibuk(false);
    }
  }

  return (
    <div className="masuk-halaman flex min-h-screen items-center justify-center bg-gradient-to-br from-nadi-900 via-nadi-800 to-nadi-950 p-4">
      <header className="masuk-bilah">
        <a href="/" className="masuk-merek" aria-label="NADI, halaman awal">
          <span className="masuk-merek-ikon"><Activity size={23} strokeWidth={2.5} /></span>
          <span>NADI<span className="masuk-merek-sub">DATA INTELLIGENCE</span></span>
        </a>
        <div className="masuk-bilah-kanan"><span className="masuk-lokasi">PRINGSEWU · LAMPUNG</span><PilihanTampilan /></div>
      </header>
      <div className="masuk-tata grid w-full max-w-4xl gap-6 lg:grid-cols-[minmax(0,360px)_1fr]">
        <section className="masuk-cerita" aria-labelledby="masuk-judul">
          <div className="masuk-eyebrow"><span /> INTELIJEN DATA UNTUK DAMPAK NYATA</div>
          <h1 id="masuk-judul">Membaca data.<br />Memahami risiko.<br /><em>Menggerakkan aksi.</em></h1>
          <p className="masuk-pengantar">Ruang kendali intervensi sosial yang menghubungkan sinyal kerentanan dengan keputusan yang lebih terarah.</p>
          <div className="masuk-sinyal" aria-hidden="true">
            <div className="masuk-sinyal-kepala"><span><Radar size={14} /> PETA SINYAL KERENTANAN</span><span className="masuk-sinyal-label">ILUSTRASI</span></div>
            <div className="masuk-jaringan">
              <svg viewBox="0 0 480 166" fill="none" preserveAspectRatio="xMidYMid meet">
                <defs>
                  <linearGradient id="masuk-garis" x1="55" y1="150" x2="410" y2="0" gradientUnits="userSpaceOnUse"><stop stopColor="#2dd4bf" stopOpacity=".12" /><stop offset="1" stopColor="#67e8f9" stopOpacity=".75" /></linearGradient>
                  <radialGradient id="masuk-cahaya"><stop stopColor="#2dd4bf" stopOpacity=".25" /><stop offset="1" stopColor="#2dd4bf" stopOpacity="0" /></radialGradient>
                </defs>
                <ellipse cx="244" cy="85" rx="220" ry="80" fill="url(#masuk-cahaya)" />
                <g stroke="url(#masuk-garis)" strokeWidth="1">
                  <path d="M45 119 102 73 170 116 236 68 314 103 385 45 444 78M102 73 176 28 236 68 299 28 385 45M170 116 236 68 247 145 314 103 382 140 444 78M45 119 93 150 170 116 247 145M176 28 170 116M299 28 314 103M236 68 385 45" />
                </g>
                <g fill="#7ce9dc">
                  <circle cx="45" cy="119" r="3" /><circle cx="102" cy="73" r="4" /><circle cx="176" cy="28" r="3" /><circle cx="170" cy="116" r="4" /><circle cx="299" cy="28" r="3" /><circle cx="314" cy="103" r="4" /><circle cx="385" cy="45" r="4" /><circle cx="444" cy="78" r="3" /><circle cx="247" cy="145" r="3" /><circle cx="382" cy="140" r="3" /><circle cx="93" cy="150" r="2" />
                </g>
                <circle className="masuk-denyut" cx="236" cy="68" r="22" stroke="#5eead4" strokeOpacity=".3" />
                <circle cx="236" cy="68" r="13" fill="#163c43" stroke="#5eead4" strokeOpacity=".5" />
                <circle cx="236" cy="68" r="5" fill="#9ffff0" />
                <text x="255" y="62" fill="#c6e5e8" fontSize="10" fontFamily="inherit">PRINGSEWU</text>
              </svg>
            </div>
            <div className="masuk-alur"><span><Radar size={14} /> Deteksi dini</span><i /><span><Compass size={14} /> Prioritas terarah</span><i /><span><Layers3 size={14} /> Intervensi</span></div>
          </div>
          <div className="masuk-cerita-catatan"><ShieldCheck size={14} /><span>Data sintetis. Akses berbasis peran. Keputusan tetap pada manusia.</span></div>
        </section>
        {/* --- Formulir --- */}
        <div className="masuk-formulir rounded-xl bg-white p-6 shadow-naik">
          <div className="mb-6">
            <div className="masuk-formulir-klasik text-2xl font-bold tracking-tight text-nadi-900">NADI</div>
            <div className="masuk-formulir-klasik text-sm text-slate-500">Navigasi AI Data Intervensi</div>
            <div className="masuk-formulir-klasik mt-1 text-xs text-slate-400">
              Kabupaten Pringsewu, Provinsi Lampung
            </div>
            <div className="masuk-sambutan"><span>RUANG KERJA NADI</span><h2>Selamat datang.</h2><p>Masuk untuk mulai menghubungkan data dan aksi.</p></div>
          </div>

          <form onSubmit={kirim} className="space-y-4">
            <div>
              <label htmlFor="nama" className="mb-1 block text-xs font-medium text-slate-600">
                Nama pengguna
              </label>
              <input
                id="nama"
                className="masukan"
                value={namaPengguna}
                onChange={(e) => setNamaPengguna(e.target.value)}
                autoComplete="username"
                required
              />
            </div>
            <div>
              <label htmlFor="sandi" className="mb-1 block text-xs font-medium text-slate-600">
                Sandi
              </label>
              <input
                id="sandi"
                type="password"
                className="masukan"
                value={sandi}
                onChange={(e) => setSandi(e.target.value)}
                autoComplete="current-password"
                required
              />
            </div>

            {galat && (
              <div role="alert" className="flex items-start gap-2 rounded-md border border-red-200 bg-red-50 p-2.5">
                <AlertCircle size={15} className="mt-0.5 shrink-0 text-red-600" />
                <span className="text-xs leading-relaxed text-red-700">{galat}</span>
              </div>
            )}

            <button type="submit" className="masuk-tombol tombol-utama w-full" disabled={sibuk}>
              <LogIn size={16} />
              {sibuk ? "Memeriksa..." : "Masuk"}
            </button>
          </form>

          <div className="masuk-privasi mt-5 flex items-start gap-2 rounded-md bg-slate-50 p-3">
            <ShieldCheck size={14} className="mt-0.5 shrink-0 text-slate-400" />
            <p className="text-2xs leading-relaxed text-slate-500">
              Seluruh data pada sistem ini bersifat sintetis. Tidak ada keluarga
              nyata di dalamnya, dan sistem tidak menyimpan nama, nomor induk
              kependudukan, maupun alamat.
            </p>
          </div>
        </div>

        {/* --- Akun demonstrasi --- */}
        <div className="masuk-demo rounded-xl border border-white/10 bg-white/5 p-6 backdrop-blur">
          <div className="masuk-demo-kepala"><h2 className="text-sm font-semibold text-white">Jelajahi dari sudut pandang Anda</h2><span className="masuk-demo-label">AKUN DEMONSTRASI <ArrowUpRight size={13} /></span></div>
          <p className="masuk-demo-keterangan mt-1 text-xs leading-relaxed text-nadi-200">
            Masuklah sebagai peran yang berbeda untuk melihat bagaimana pembatasan
            akses bekerja. Coba buka data keluarga sebagai Pimpinan Daerah — sistem
            akan menolaknya, karena peran itu memang tidak memerlukannya.
          </p>

          <div className="masuk-demo-daftar mt-4 space-y-1.5">
            {akun.map((a) => (
              <button
                key={a.nama_pengguna}
                type="button"
                aria-pressed={namaPengguna === a.nama_pengguna}
                onClick={() => {
                  setNamaPengguna(a.nama_pengguna);
                  setSandi(a.sandi);
                  setGalat(null);
                }}
                className={`masuk-akun w-full rounded-md border px-3 py-2 text-left transition-colors ${
                  namaPengguna === a.nama_pengguna
                    ? "border-nadi-400 bg-nadi-700/60"
                    : "border-white/10 bg-white/5 hover:bg-white/10"
                }`}
              >
                <div className="flex items-baseline justify-between gap-2">
                  <span className="text-xs font-semibold text-white">{a.label_peran}</span>
                  <span className="font-mono text-2xs text-nadi-300">{a.nama_pengguna}</span>
                </div>
                <div className="mt-0.5 text-2xs text-nadi-200">{a.jabatan}</div>
                <div className="mt-0.5 text-2xs text-nadi-400">Cakupan: {a.cakupan}</div>
              </button>
            ))}
          </div>

          {akun.length === 0 && (
            <p className="mt-4 text-xs text-nadi-300">
              Daftar akun belum dapat dimuat. Pastikan peladen sudah berjalan.
            </p>
          )}
        </div>
      </div>
      <footer className="masuk-kaki"><span>Navigasi AI Data Intervensi</span><span>Kabupaten Pringsewu · LAN Datathon 2026</span></footer>
    </div>
  );
}
