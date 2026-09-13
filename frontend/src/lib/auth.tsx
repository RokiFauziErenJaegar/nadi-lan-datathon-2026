/**
 * Konteks autentikasi dan kewenangan.
 *
 * Menyimpan identitas pengguna serta menyediakan pemeriksaan kewenangan yang
 * dipakai antarmuka untuk menyembunyikan menu dan tombol.
 *
 * Perlu ditegaskan: penyembunyian di sisi antarmuka adalah kenyamanan, BUKAN
 * pengamanan. Penegakan yang sesungguhnya berada di peladen, pada setiap titik
 * akhir, lewat `nadi.api.deps.wajib`. Menu yang disembunyikan di sini semata
 * agar pengguna tidak menemui tombol yang selalu berujung penolakan - bukan
 * agar data terlindungi.
 */

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { api, pasangPenanganSesiBerakhir, simpanan, type Pengguna } from "./api";

interface NilaiAuth {
  pengguna: Pengguna | null;
  memuat: boolean;
  masuk: (namaPengguna: string, sandi: string) => Promise<void>;
  keluar: () => void;
  punya: (kewenangan: string) => boolean;
  bolehBukaKeluarga: boolean;
}

const KonteksAuth = createContext<NilaiAuth | null>(null);

interface TanggapanMasuk {
  token: string;
  kedaluwarsa: string;
  pengguna: Pengguna;
}

export function PenyediaAuth({ children }: { children: ReactNode }) {
  const [pengguna, setPengguna] = useState<Pengguna | null>(() => simpanan.ambilPengguna());
  const [memuat, setMemuat] = useState(true);

  const keluar = useCallback(() => {
    simpanan.bersihkan();
    setPengguna(null);
  }, []);

  useEffect(() => {
    pasangPenanganSesiBerakhir(() => setPengguna(null));
  }, []);

  useEffect(() => {
    // Token yang tersimpan di peramban bisa saja sudah kedaluwarsa sejak
    // kunjungan terakhir. Memeriksanya sekali di awal mencegah pengguna
    // menemui layar kosong lalu galat, alih-alih langsung diminta masuk.
    const token = simpanan.ambilToken();
    if (!token) {
      setMemuat(false);
      return;
    }
    api
      .ambil<Pengguna>("/saya")
      .then((p) => {
        setPengguna(p);
        simpanan.simpanPengguna(p);
      })
      .catch(() => keluar())
      .finally(() => setMemuat(false));
  }, [keluar]);

  const masuk = useCallback(async (namaPengguna: string, sandi: string) => {
    const hasil = await api.kirim<TanggapanMasuk>("/masuk", {
      nama_pengguna: namaPengguna,
      sandi,
    });
    simpanan.simpanToken(hasil.token);
    const lengkap = await api.ambil<Pengguna>("/saya");
    simpanan.simpanPengguna(lengkap);
    setPengguna(lengkap);
  }, []);

  const punya = useCallback(
    (kewenangan: string) => Boolean(pengguna?.kewenangan?.includes(kewenangan)),
    [pengguna],
  );

  const nilai = useMemo<NilaiAuth>(
    () => ({
      pengguna,
      memuat,
      masuk,
      keluar,
      punya,
      bolehBukaKeluarga: Boolean(pengguna?.boleh_buka_keluarga),
    }),
    [pengguna, memuat, masuk, keluar, punya],
  );

  return <KonteksAuth.Provider value={nilai}>{children}</KonteksAuth.Provider>;
}

export function useAuth(): NilaiAuth {
  const nilai = useContext(KonteksAuth);
  if (!nilai) throw new Error("useAuth harus dipakai di dalam PenyediaAuth.");
  return nilai;
}

/** Daftar kewenangan, disalin dari `nadi.security.rbac.Kewenangan`. */
export const KEWENANGAN = {
  BACA_AGREGAT: "baca:agregat",
  BACA_PETA: "baca:peta",
  BACA_KELUARGA: "baca:keluarga",
  BACA_ANTREAN: "baca:antrean",
  BACA_REKOMENDASI: "baca:rekomendasi",
  BACA_OUTCOME: "baca:outcome",
  BACA_JEJAK_AUDIT: "baca:jejak_audit",
  VERIFIKASI_KASUS: "tulis:verifikasi",
  TUGASKAN_KASUS: "tulis:penugasan",
  CATAT_INTERVENSI: "tulis:intervensi",
  CATAT_OUTCOME: "tulis:outcome",
  JALANKAN_SIMULASI: "jalankan:simulasi",
  GUNAKAN_COPILOT: "jalankan:copilot",
  KELOLA_MODEL: "admin:model",
  KELOLA_SISTEM: "admin:sistem",
} as const;
