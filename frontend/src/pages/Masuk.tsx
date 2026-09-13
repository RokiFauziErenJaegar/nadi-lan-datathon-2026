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
import { AlertCircle, LogIn, ShieldCheck } from "lucide-react";
import { api } from "../lib/api";
import { useAuth } from "../lib/auth";

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
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-nadi-900 via-nadi-800 to-nadi-950 p-4">
      <div className="grid w-full max-w-4xl gap-6 lg:grid-cols-[minmax(0,360px)_1fr]">
        {/* --- Formulir --- */}
        <div className="rounded-xl bg-white p-6 shadow-naik">
          <div className="mb-6">
            <div className="text-2xl font-bold tracking-tight text-nadi-900">NADI</div>
            <div className="text-sm text-slate-500">Navigasi AI Data Intervensi</div>
            <div className="mt-1 text-xs text-slate-400">
              Kabupaten Pringsewu, Provinsi Lampung
            </div>
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
              <div className="flex items-start gap-2 rounded-md border border-red-200 bg-red-50 p-2.5">
                <AlertCircle size={15} className="mt-0.5 shrink-0 text-red-600" />
                <span className="text-xs leading-relaxed text-red-700">{galat}</span>
              </div>
            )}

            <button type="submit" className="tombol-utama w-full" disabled={sibuk}>
              <LogIn size={16} />
              {sibuk ? "Memeriksa..." : "Masuk"}
            </button>
          </form>

          <div className="mt-5 flex items-start gap-2 rounded-md bg-slate-50 p-3">
            <ShieldCheck size={14} className="mt-0.5 shrink-0 text-slate-400" />
            <p className="text-2xs leading-relaxed text-slate-500">
              Seluruh data pada sistem ini bersifat sintetis. Tidak ada keluarga
              nyata di dalamnya, dan sistem tidak menyimpan nama, nomor induk
              kependudukan, maupun alamat.
            </p>
          </div>
        </div>

        {/* --- Akun demonstrasi --- */}
        <div className="rounded-xl border border-white/10 bg-white/5 p-6 backdrop-blur">
          <h2 className="text-sm font-semibold text-white">Akun untuk mencoba</h2>
          <p className="mt-1 text-xs leading-relaxed text-nadi-200">
            Masuklah sebagai peran yang berbeda untuk melihat bagaimana pembatasan
            akses bekerja. Coba buka data keluarga sebagai Pimpinan Daerah — sistem
            akan menolaknya, karena peran itu memang tidak memerlukannya.
          </p>

          <div className="mt-4 space-y-1.5">
            {akun.map((a) => (
              <button
                key={a.nama_pengguna}
                onClick={() => {
                  setNamaPengguna(a.nama_pengguna);
                  setSandi(a.sandi);
                  setGalat(null);
                }}
                className={`w-full rounded-md border px-3 py-2 text-left transition-colors ${
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
    </div>
  );
}
