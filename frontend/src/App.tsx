import { Navigate, Route, Routes } from "react-router-dom";
import { useAuth } from "./lib/auth";
import Tata from "./components/Tata";
import Memuat from "./components/Memuat";
import HalamanMasuk from "./pages/Masuk";
import HalamanRingkasan from "./pages/Ringkasan";
import HalamanPeta from "./pages/Peta";
import HalamanAntrean from "./pages/Antrean";
import HalamanKeluarga from "./pages/Keluarga";
import HalamanProfilKeluarga from "./pages/ProfilKeluarga";
import HalamanProgram from "./pages/Program";
import HalamanSimulasi from "./pages/Simulasi";
import HalamanCopilot from "./pages/Copilot";
import HalamanModel from "./pages/Model";
import HalamanMonitoring from "./pages/Monitoring";
import HalamanPengaturan from "./pages/Pengaturan";

export default function App() {
  const { pengguna, memuat } = useAuth();

  if (memuat) {
    return <Memuat pesan="Memeriksa sesi..." penuh />;
  }

  if (!pengguna) {
    return (
      <Routes>
        <Route path="/masuk" element={<HalamanMasuk />} />
        <Route path="*" element={<Navigate to="/masuk" replace />} />
      </Routes>
    );
  }

  return (
    <Tata>
      <Routes>
        <Route path="/" element={<HalamanRingkasan />} />
        <Route path="/peta" element={<HalamanPeta />} />
        <Route path="/antrean" element={<HalamanAntrean />} />
        <Route path="/keluarga" element={<HalamanKeluarga />} />
        <Route path="/keluarga/:kode" element={<HalamanProfilKeluarga />} />
        <Route path="/program" element={<HalamanProgram />} />
        <Route path="/simulasi" element={<HalamanSimulasi />} />
        <Route path="/copilot" element={<HalamanCopilot />} />
        <Route path="/monitoring" element={<HalamanMonitoring />} />
        <Route path="/model" element={<HalamanModel />} />
        <Route path="/pengaturan" element={<HalamanPengaturan />} />
        <Route path="/masuk" element={<Navigate to="/" replace />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Tata>
  );
}
