/**
 * AI Policy Copilot.
 *
 * Setiap jawaban menampilkan potongan pengetahuan yang dipakainya. Copilot yang
 * menjawab tanpa menunjukkan sumbernya menuntut kepercayaan; yang menunjukkannya
 * memungkinkan pengguna memeriksa sendiri - dan menemukan bila keliru.
 *
 * Saat layanan model bahasa tidak tersedia, penanda mode luring ditampilkan
 * terbuka. Jawaban tetap disusun dari potongan pengetahuan yang sama, sehingga
 * seluruh angkanya identik; yang berbeda hanya keluwesan kalimatnya.
 */

import { useRef, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Bot, Send, User, WifiOff } from "lucide-react";
import { api } from "../lib/api";
import { Kartu, Penafian } from "../components/dasar";

interface Sumber {
  id: string;
  judul: string;
  jenis: string;
  sumber: string | null;
}

interface Jawaban {
  jawaban: string;
  sumber: Sumber[];
  dari_cadangan: boolean;
  model: string | null;
  durasi_ms: number;
  pertanyaan_diredaksi: boolean;
  catatan: string[];
  penafian: string;
}

interface Percakapan {
  peran: "pengguna" | "copilot";
  isi: string;
  data?: Jawaban;
}

export default function Copilot() {
  const [pertanyaan, setPertanyaan] = useState("");
  const [riwayat, setRiwayat] = useState<Percakapan[]>([]);
  const [sibuk, setSibuk] = useState(false);
  const bawah = useRef<HTMLDivElement>(null);

  const contoh = useQuery({
    queryKey: ["copilot-contoh"],
    queryFn: () =>
      api.ambil<{
        dapat_dijawab: string[];
        tidak_dapat_dijawab: string[];
        status_layanan: { siap: boolean; mode: string; alasan: string | null; catatan_mode_luring: string };
      }>("/copilot/contoh-pertanyaan"),
  });

  async function tanya(teks: string) {
    if (!teks.trim() || sibuk) return;
    setRiwayat((r) => [...r, { peran: "pengguna", isi: teks }]);
    setPertanyaan("");
    setSibuk(true);
    try {
      const h = await api.kirim<Jawaban>("/copilot/tanya", { pertanyaan: teks });
      setRiwayat((r) => [...r, { peran: "copilot", isi: h.jawaban, data: h }]);
    } catch (err) {
      setRiwayat((r) => [
        ...r,
        { peran: "copilot", isi: err instanceof Error ? err.message : "Gagal menjawab." },
      ]);
    } finally {
      setSibuk(false);
      setTimeout(() => bawah.current?.scrollIntoView({ behavior: "smooth" }), 60);
    }
  }

  const luring = contoh.data && !contoh.data.status_layanan.siap;

  return (
    <div className="grid gap-5 lg:grid-cols-[1fr_320px]">
      <div className="space-y-4">
        {luring && (
          <div className="flex items-start gap-2.5 rounded-lg border border-amber-200 bg-amber-50 p-3">
            <WifiOff size={16} className="mt-0.5 shrink-0 text-amber-600" />
            <div className="text-xs leading-relaxed text-amber-900">
              <span className="font-semibold">Mode luring.</span>{" "}
              {contoh.data?.status_layanan.catatan_mode_luring}
              <div className="mt-1 text-2xs text-amber-700">
                {contoh.data?.status_layanan.alasan}
              </div>
            </div>
          </div>
        )}

        <Kartu padat>
          <div className="min-h-[420px] space-y-4 p-4">
            {riwayat.length === 0 && (
              <div className="flex h-[380px] flex-col items-center justify-center text-center">
                <Bot size={32} className="mb-3 text-slate-300" />
                <p className="max-w-md text-sm text-slate-500">
                  Ajukan pertanyaan tentang program, faktor risiko, wilayah, atau cara
                  kerja model. Copilot menjawab dari basis pengetahuan sistem dan
                  menunjukkan sumbernya.
                </p>
              </div>
            )}

            {riwayat.map((p, i) => (
              <div key={i} className={`flex gap-3 ${p.peran === "pengguna" ? "justify-end" : ""}`}>
                {p.peran === "copilot" && (
                  <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-nadi-100">
                    <Bot size={15} className="text-nadi-700" />
                  </div>
                )}
                <div className={`max-w-[80%] ${p.peran === "pengguna" ? "order-first" : ""}`}>
                  <div
                    className={`rounded-lg px-3.5 py-2.5 text-sm leading-relaxed ${
                      p.peran === "pengguna"
                        ? "bg-nadi-700 text-white"
                        : "border border-slate-200 bg-white text-slate-700"
                    }`}
                  >
                    <div className="whitespace-pre-wrap">{p.isi}</div>
                  </div>

                  {p.data && (
                    <div className="mt-1.5 space-y-1.5">
                      {p.data.pertanyaan_diredaksi && (
                        <div className="rounded border border-amber-200 bg-amber-50 px-2 py-1 text-2xs text-amber-900">
                          Pertanyaan Anda memuat pengenal pribadi. Nilainya dihapus sebelum
                          apa pun dikirim ke luar peladen.
                        </div>
                      )}
                      {p.data.sumber.length > 0 && (
                        <details className="text-2xs">
                          <summary className="cursor-pointer text-slate-500 hover:text-slate-700">
                            {p.data.sumber.length} sumber dipakai
                            {p.data.dari_cadangan ? " · mode luring" : ` · ${p.data.model}`}
                          </summary>
                          <ul className="mt-1 space-y-0.5 pl-3">
                            {p.data.sumber.map((s) => (
                              <li key={s.id} className="text-slate-500">
                                <span className="font-medium text-slate-600">{s.judul}</span>
                                {s.sumber && <span className="text-slate-400"> · {s.sumber}</span>}
                              </li>
                            ))}
                          </ul>
                        </details>
                      )}
                    </div>
                  )}
                </div>
                {p.peran === "pengguna" && (
                  <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-slate-200">
                    <User size={15} className="text-slate-600" />
                  </div>
                )}
              </div>
            ))}

            {sibuk && (
              <div className="flex gap-3">
                <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-nadi-100">
                  <Bot size={15} className="text-nadi-700" />
                </div>
                <div className="rounded-lg border border-slate-200 bg-white px-3.5 py-2.5 text-sm text-slate-400">
                  Menyusun jawaban...
                </div>
              </div>
            )}
            <div ref={bawah} />
          </div>

          <form
            onSubmit={(e) => {
              e.preventDefault();
              tanya(pertanyaan);
            }}
            className="flex gap-2 border-t border-slate-100 p-3"
          >
            <input
              value={pertanyaan}
              onChange={(e) => setPertanyaan(e.target.value)}
              placeholder="Ajukan pertanyaan tentang program, wilayah, atau model..."
              className="masukan flex-1"
              disabled={sibuk}
            />
            <button type="submit" className="tombol-utama" disabled={sibuk || !pertanyaan.trim()}>
              <Send size={15} />
            </button>
          </form>
        </Kartu>
      </div>

      <div className="space-y-4">
        <Kartu judul="Contoh pertanyaan">
          <ul className="space-y-1.5">
            {contoh.data?.dapat_dijawab.map((q) => (
              <li key={q}>
                <button
                  onClick={() => tanya(q)}
                  disabled={sibuk}
                  className="w-full rounded-md border border-slate-200 px-2.5 py-2 text-left text-xs leading-relaxed text-slate-700 hover:border-nadi-300 hover:bg-nadi-50"
                >
                  {q}
                </button>
              </li>
            ))}
          </ul>
        </Kartu>

        <Kartu judul="Yang tidak dapat dijawab">
          <ul className="space-y-2">
            {contoh.data?.tidak_dapat_dijawab.map((q) => (
              <li key={q} className="text-2xs leading-relaxed text-slate-500">
                {q}
              </li>
            ))}
          </ul>
        </Kartu>

        <Penafian judul="Peran copilot">
          Copilot menjelaskan apa yang sudah ada di dalam sistem. Ia tidak
          menghasilkan penilaian baru tentang keluarga mana pun, tidak menetapkan
          kelayakan bantuan, dan tidak membuat keputusan apa pun.
        </Penafian>
      </div>
    </div>
  );
}
