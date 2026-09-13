/**
 * Uji asap antarmuka: memasang setiap halaman dan memastikan ia benar-benar
 * tampil.
 *
 * Perkakas ini lahir dari satu kekeliruan yang lolos dari seluruh pemeriksaan
 * yang ada. Halaman Pengaturan memanggil tiga `useMutation` di bawah cabang
 * `if (isLoading) return`. Render pertama memanggil nol hook mutasi, render
 * kedua memanggil tiga, dan React membatalkan seluruh pohon komponen. Yang
 * terlihat pemakai hanyalah halaman kosong.
 *
 * `tsc --noEmit` lolos - ini kekeliruan waktu jalan. `vite build` lolos -
 * membangun berkas bukan menjalankannya. Yang dapat menangkapnya hanyalah
 * memasang halaman itu sungguhan, menunggu datanya tiba, lalu melihat apakah
 * masih ada isinya. Itulah yang dikerjakan berkas ini.
 *
 * Dua keputusan yang membuatnya berguna:
 *
 * **Menggunakan peladen sungguhan, bukan tiruan.** Tanggapan tiruan hanya
 * menguji apa yang sudah kita bayangkan. Memanggil peladen yang sedang
 * berjalan sekaligus memeriksa bahwa bentuk tanggapan API benar-benar cocok
 * dengan yang dibaca komponen - ketidakcocokan kontrak sudah beberapa kali
 * menjadi sebab layar kosong pada proyek ini.
 *
 * **Menunggu render kedua.** Kekeliruan urutan hook tidak pernah muncul pada
 * render pertama. Ia baru muncul ketika data tiba dan komponen digambar ulang.
 * Karena itu setiap halaman ditunggu sampai kuerinya reda, bukan sekadar
 * dipasang lalu ditinggalkan.
 */

import { act } from "react";
import { createRoot, type Root } from "react-dom/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter, Route, Routes } from "react-router-dom";

import { PenyediaAuth } from "../src/lib/auth";
import Ringkasan from "../src/pages/Ringkasan";
import Peta from "../src/pages/Peta";
import Antrean from "../src/pages/Antrean";
import Keluarga from "../src/pages/Keluarga";
import ProfilKeluarga from "../src/pages/ProfilKeluarga";
import Program from "../src/pages/Program";
import Simulasi from "../src/pages/Simulasi";
import Copilot from "../src/pages/Copilot";
import Model from "../src/pages/Model";
import Monitoring from "../src/pages/Monitoring";
import Pengaturan from "../src/pages/Pengaturan";

export interface Hasil {
  nama: string;
  lulus: boolean;
  panjangTeks: number;
  sebab?: string;
  cuplikan: string;
  galat: string[];
}

interface Halaman {
  nama: string;
  jalur: string;
  pola: string;
  komponen: () => JSX.Element;
  // Penanda yang harus muncul pada teks halaman. Tanpa ini sebuah halaman
  // yang menampilkan pesan galat pun akan dianggap lulus, karena teknisnya
  // ia memang berhasil tergambar.
  //
  // Penanda WAJIB diambil dari isi halaman itu sendiri, bukan dari judulnya:
  // judul dan menu berada di komponen tata letak, yang sengaja tidak ikut
  // dipasang di sini supaya yang diuji benar-benar halamannya.
  petunjuk: string[];
}

const HALAMAN: Halaman[] = [
  { nama: "Ringkasan", jalur: "/", pola: "/", komponen: Ringkasan, petunjuk: ["keluarga"] },
  { nama: "Peta Risiko", jalur: "/peta", pola: "/peta", komponen: Peta, petunjuk: ["Ukuran yang dipetakan"] },
  { nama: "Antrean Kasus", jalur: "/antrean", pola: "/antrean", komponen: Antrean, petunjuk: ["Jenis kasus"] },
  { nama: "Keluarga", jalur: "/keluarga", pola: "/keluarga", komponen: Keluarga, petunjuk: ["keluarga ditampilkan"] },
  {
    nama: "Profil Keluarga",
    jalur: "/keluarga/__KODE__",
    pola: "/keluarga/:kode",
    komponen: ProfilKeluarga,
    petunjuk: ["skor", "Skor", "risiko", "Risiko"],
  },
  { nama: "Katalog Program", jalur: "/program", pola: "/program", komponen: Program, petunjuk: ["Program"] },
  { nama: "Simulasi", jalur: "/simulasi", pola: "/simulasi", komponen: Simulasi, petunjuk: ["Simulasi"] },
  { nama: "Copilot", jalur: "/copilot", pola: "/copilot", komponen: Copilot, petunjuk: ["Copilot", "pertanyaan"] },
  { nama: "Transparansi Model", jalur: "/model", pola: "/model", komponen: Model, petunjuk: ["Model", "AUC", "model"] },
  { nama: "Monitoring Hasil", jalur: "/monitoring", pola: "/monitoring", komponen: Monitoring, petunjuk: ["Monitoring", "pembanding"] },
  { nama: "Pengaturan AI", jalur: "/pengaturan", pola: "/pengaturan", komponen: Pengaturan, petunjuk: ["Penyedia", "Model"] },
];

/** Beri kesempatan kepada kueri untuk reda, lalu paksa React menggambar ulang. */
async function tunggu(klien: QueryClient, batasMs = 12000): Promise<void> {
  const mulai = Date.now();
  while (Date.now() - mulai < batasMs) {
    await act(async () => {
      await new Promise((r) => setTimeout(r, 120));
    });
    const sibuk = klien.isFetching() > 0 || klien.isMutating() > 0;
    if (!sibuk && Date.now() - mulai > 400) return;
  }
}

async function pasang(h: Halaman, kode: string): Promise<Hasil> {
  const galat: string[] = [];
  const konsolAsli = console.error;
  console.error = (...arg: unknown[]) => {
    const pesan = arg.map((a) => (a instanceof Error ? a.message : String(a))).join(" ");
    // Peringatan yang tidak menandakan kerusakan disaring, supaya yang tersisa
    // benar-benar layak dibaca.
    if (/not wrapped in act|useLayoutEffect does nothing on the server/i.test(pesan)) return;
    galat.push(pesan.slice(0, 300));
    konsolAsli(...arg);
  };

  const wadah = document.createElement("div");
  document.body.appendChild(wadah);
  const klien = new QueryClient({
    defaultOptions: { queries: { retry: false, gcTime: 0, staleTime: 0 } },
  });

  let akar: Root | null = null;
  let sebab: string | undefined;
  let teks = "";

  try {
    await act(async () => {
      akar = createRoot(wadah);
      akar.render(
        <QueryClientProvider client={klien}>
          <PenyediaAuth>
            <MemoryRouter initialEntries={[h.jalur.replace("__KODE__", kode)]}>
              <Routes>
                <Route path={h.pola} element={<h.komponen />} />
              </Routes>
            </MemoryRouter>
          </PenyediaAuth>
        </QueryClientProvider>,
      );
    });
    await tunggu(klien);
    teks = (wadah.textContent ?? "").replace(/\s+/g, " ").trim();
  } catch (e) {
    sebab = e instanceof Error ? `${e.name}: ${e.message}` : String(e);
  } finally {
    console.error = konsolAsli;
    try {
      if (akar) await act(async () => (akar as Root).unmount());
    } catch {
      /* pembongkaran yang gagal tidak menambah keterangan apa pun */
    }
    wadah.remove();
    klien.clear();
  }

  if (!sebab && teks.length < 40) sebab = `halaman nyaris kosong (${teks.length} karakter)`;
  if (!sebab && !h.petunjuk.some((p) => teks.includes(p)))
    sebab = `tidak satu pun penanda ditemukan: ${h.petunjuk.join(", ")}`;
  if (!sebab && galat.length) sebab = galat[0];

  return {
    nama: h.nama,
    lulus: !sebab,
    panjangTeks: teks.length,
    sebab,
    // Cuplikan disertakan justru pada kegagalan: tanpa melihat apa yang
    // sebenarnya tergambar, mustahil membedakan halaman yang rusak dari
    // penanda uji yang salah tulis.
    cuplikan: teks.slice(0, 220),
    galat,
  };
}

export async function jalankan(kodeKeluarga: string): Promise<Hasil[]> {
  const hasil: Hasil[] = [];
  for (const h of HALAMAN) {
    hasil.push(await pasang(h, kodeKeluarga));
  }
  return hasil;
}
