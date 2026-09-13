import { useEffect, useId, useRef, useState, type KeyboardEvent } from "react";
import { Check, ChevronDown, Monitor, Sparkles, Sun } from "lucide-react";
import { useTema, type Tema } from "../lib/tema";
import "../styles/tampilan.css";

const PILIHAN: { nilai: Tema; nama: string; keterangan: string }[] = [
  { nilai: "klasik", nama: "Klasik", keterangan: "Terang & familiar" },
  { nilai: "futuristik", nama: "Futuristik", keterangan: "Gelap & imersif" },
];

export default function PilihanTampilan() {
  const { tema, setTema } = useTema();
  const [terbuka, setTerbuka] = useState(false);
  const id = useId();
  const wadah = useRef<HTMLDivElement>(null);
  const pemicu = useRef<HTMLButtonElement>(null);
  const opsi = useRef<(HTMLButtonElement | null)[]>([]);

  useEffect(() => {
    if (!terbuka) return;
    opsi.current[PILIHAN.findIndex((p) => p.nilai === tema)]?.focus();
    const diLuar = (event: PointerEvent) => {
      if (event.target instanceof Node && !wadah.current?.contains(event.target)) {
        setTerbuka(false);
      }
    };
    const tutupDenganEscape = (event: globalThis.KeyboardEvent) => {
      if (event.key === "Escape") {
        event.preventDefault();
        setTerbuka(false);
        pemicu.current?.focus();
      }
    };
    document.addEventListener("pointerdown", diLuar);
    document.addEventListener("keydown", tutupDenganEscape);
    return () => {
      document.removeEventListener("pointerdown", diLuar);
      document.removeEventListener("keydown", tutupDenganEscape);
    };
    // Fokus awal hanya saat panel dibuka; navigasi panah mengelola fokus sendiri.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [terbuka]);

  function navigasi(event: KeyboardEvent<HTMLButtonElement>, indeks: number) {
    let tujuan = indeks;
    if (["ArrowRight", "ArrowDown"].includes(event.key)) tujuan = (indeks + 1) % PILIHAN.length;
    else if (["ArrowLeft", "ArrowUp"].includes(event.key)) tujuan = (indeks + PILIHAN.length - 1) % PILIHAN.length;
    else if (event.key === "Home") tujuan = 0;
    else if (event.key === "End") tujuan = PILIHAN.length - 1;
    else return;
    event.preventDefault();
    setTema(PILIHAN[tujuan].nilai);
    opsi.current[tujuan]?.focus();
  }

  return (
    <div
      className="tampilan-pemilih"
      ref={wadah}
      onBlur={(event) => {
        if (!event.currentTarget.contains(event.relatedTarget)) setTerbuka(false);
      }}
    >
      <button
        ref={pemicu}
        type="button"
        className="tampilan-pemicu"
        aria-haspopup="dialog"
        aria-expanded={terbuka}
        aria-controls={terbuka ? `${id}-panel` : undefined}
        onClick={() => setTerbuka((nilai) => !nilai)}
      >
        <Monitor size={15} aria-hidden="true" />
        <span>Tampilan</span>
        <ChevronDown size={13} className={terbuka ? "tampilan-panah terbuka" : "tampilan-panah"} aria-hidden="true" />
      </button>
      {terbuka && (
        <div className="tampilan-panel" id={`${id}-panel`} role="dialog" aria-labelledby={`${id}-judul`}>
          <div className="tampilan-panel-judul" id={`${id}-judul`}>Ruang kerja, gaya Anda.</div>
          <p className="tampilan-panel-keterangan">Pilih suasana yang paling nyaman.</p>
          <div className="tampilan-opsi" role="radiogroup" aria-label="Tema tampilan">
            {PILIHAN.map((pilihan, indeks) => (
              <button
                key={pilihan.nilai}
                ref={(node) => { opsi.current[indeks] = node; }}
                type="button"
                role="radio"
                aria-checked={tema === pilihan.nilai}
                aria-label={`${pilihan.nama}, ${pilihan.keterangan}`}
                tabIndex={tema === pilihan.nilai ? 0 : -1}
                className={`tampilan-pilihan ${tema === pilihan.nilai ? "terpilih" : ""}`}
                onKeyDown={(event) => navigasi(event, indeks)}
                onClick={() => {
                  setTema(pilihan.nilai);
                  setTerbuka(false);
                  pemicu.current?.focus();
                }}
              >
                <span className={`tampilan-pratinjau tampilan-pratinjau-${pilihan.nilai}`} aria-hidden="true">
                  <span className="tampilan-mini-sidebar"><i /><i /><i /></span>
                  <span className="tampilan-mini-isi"><i /><span><i /><i /><i /></span><b /></span>
                  {tema === pilihan.nilai && <span className="tampilan-centang"><Check size={12} strokeWidth={3} /></span>}
                </span>
                <span className="tampilan-nama">
                  {pilihan.nilai === "futuristik" ? <Sparkles size={13} aria-hidden="true" /> : <Sun size={13} aria-hidden="true" />}
                  {pilihan.nama}
                </span>
                <span className="tampilan-deskripsi">{pilihan.keterangan}</span>
              </button>
            ))}
          </div>
          <p className="tampilan-catatan">Pilihan Anda tersimpan di perangkat ini.</p>
        </div>
      )}
    </div>
  );
}
