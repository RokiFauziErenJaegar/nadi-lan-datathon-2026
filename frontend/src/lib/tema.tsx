import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useLayoutEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

export type Tema = "futuristik" | "klasik";
const KUNCI_TEMA = "nadi-tampilan";

function normalisasiTema(nilai: string | null | undefined): Tema {
  return nilai === "klasik" ? "klasik" : "futuristik";
}

function bacaTema(): Tema {
  try {
    return normalisasiTema(localStorage.getItem(KUNCI_TEMA));
  } catch {
    return normalisasiTema(document.documentElement.dataset.theme);
  }
}

const KonteksTema = createContext<{ tema: Tema; setTema: (tema: Tema) => void } | null>(null);

export function TemaProvider({ children }: { children: ReactNode }) {
  const [tema, ubahTema] = useState<Tema>(bacaTema);

  useLayoutEffect(() => {
    document.documentElement.dataset.theme = tema;
    document.documentElement.style.colorScheme = tema === "futuristik" ? "dark" : "light";
  }, [tema]);

  const setTema = useCallback((pilihan: Tema) => {
    ubahTema(pilihan);
    try {
      localStorage.setItem(KUNCI_TEMA, pilihan);
    } catch {
      // Pilihan tetap berlaku untuk sesi ini ketika penyimpanan dibatasi.
    }
  }, []);

  useEffect(() => {
    const sinkronkan = (event: StorageEvent) => {
      if (event.key === KUNCI_TEMA || event.key === null) {
        ubahTema(normalisasiTema(event.newValue));
      }
    };
    window.addEventListener("storage", sinkronkan);
    return () => window.removeEventListener("storage", sinkronkan);
  }, []);

  const nilai = useMemo(() => ({ tema, setTema }), [tema, setTema]);
  return <KonteksTema.Provider value={nilai}>{children}</KonteksTema.Provider>;
}

export function useTema() {
  const nilai = useContext(KonteksTema);
  if (!nilai) throw new Error("useTema harus dipakai di dalam TemaProvider.");
  return nilai;
}
