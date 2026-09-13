"""Indeks kerentanan dasar yang dapat dijelaskan sepenuhnya.

Proposal NADI menyebut dua jalur pemodelan berdampingan: pendekatan dasar yang
dapat ditafsirkan, dan gradient boosting. Berkas ini memuat yang pertama, dan
keberadaannya bukan sekadar pelengkap.

Model ini menjawab pertanyaan yang wajar diajukan seorang pejabat sebelum
menandatangani apa pun: **apakah kecerdasan buatan ini benar-benar lebih baik
daripada aturan yang bisa saya hitung sendiri?** Tanpa pembanding, pertanyaan
itu tidak terjawab dan setiap klaim keunggulan hanya berupa pernyataan. Dengan
pembanding, jawabannya berupa angka - dan bila ternyata selisihnya kecil,
maka aturan sederhanalah yang layak dipakai. Temuan seperti itu pun jujur dan
patut disampaikan.

Cara kerjanya sepenuhnya aritmetika: setiap faktor risiko yang terdeteksi
menyumbang bobotnya, bobot dijumlahkan, lalu jumlahnya dipetakan ke rentang
nol sampai seratus. Seluruh perhitungan dapat diperiksa dengan kalkulator, dan
setiap angka pada layar dapat ditelusuri sampai ke aturan yang menghasilkannya.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.isotonic import IsotonicRegression

from nadi.config import settings
from nadi.ml.aturan import evaluasi_ekspresi

logger = logging.getLogger("nadi.ml.baseline")


@dataclass
class FaktorTerdeteksi:
    """Satu faktor risiko yang terdeteksi pada sebuah keluarga."""

    kode: str
    nama: str
    dimensi: str
    bobot: float
    kontribusi_persen: float


@dataclass
class IndeksDasar:
    """Indeks kerentanan berbobot dari katalog faktor risiko."""

    faktor: list[dict] = field(default_factory=list)
    bobot_maksimum: float = 0.0
    kalibrator: IsotonicRegression | None = None

    # ------------------------------------------------------------------
    @classmethod
    def dari_berkas(cls, berkas: Path | None = None) -> "IndeksDasar":
        """Bangun indeks dari berkas katalog faktor risiko."""
        berkas = berkas or (settings.seed_dir / "faktor_risiko.json")
        data = json.loads(berkas.read_text(encoding="utf-8"))["faktor_risiko"]

        faktor = [f for f in data if f.get("ekspresi_deteksi") and f.get("aktif", True)]
        dilewati = [f["kode"] for f in data if not f.get("ekspresi_deteksi")]
        if dilewati:
            logger.info(
                "Faktor tanpa aturan deteksi otomatis dilewati pada indeks dasar: %s",
                ", ".join(dilewati),
            )

        bobot_maks = sum(float(f.get("bobot_dasar", 1.0)) for f in faktor)
        return cls(faktor=faktor, bobot_maksimum=bobot_maks)

    # ------------------------------------------------------------------
    def deteksi(self, X: pd.DataFrame) -> pd.DataFrame:
        """Deteksi seluruh faktor risiko pada matriks fitur.

        Returns:
            Bingkai boolean berukuran (baris, jumlah faktor), berkolomkan kode
            faktor.
        """
        kolom = {}
        for f in self.faktor:
            kolom[f["kode"]] = evaluasi_ekspresi(f["ekspresi_deteksi"], X)
        return pd.DataFrame(kolom, index=X.index)

    def skor_mentah(self, X: pd.DataFrame) -> np.ndarray:
        """Jumlah bobot seluruh faktor yang terdeteksi."""
        terdeteksi = self.deteksi(X)
        bobot = np.array([float(f.get("bobot_dasar", 1.0)) for f in self.faktor])
        return terdeteksi.to_numpy().astype(float) @ bobot

    def skor(self, X: pd.DataFrame) -> np.ndarray:
        """Skor kerentanan pada rentang nol sampai seratus.

        Pemetaan bersifat linear terhadap bobot maksimum yang mungkin, bukan
        terhadap sebaran data. Akibatnya skor tetap dapat dibandingkan antar-
        gelombang dan antar-wilayah: nilai 60 berarti hal yang sama pada Maret
        maupun September, di Pagelaran maupun di Pringsewu. Pemetaan berbasis
        peringkat akan tampak lebih rapi sebarannya namun kehilangan sifat itu,
        sebab peringkat selalu bergantung pada siapa saja yang sedang dibandingkan.
        """
        if self.bobot_maksimum <= 0:
            return np.zeros(len(X))
        return np.clip(self.skor_mentah(X) / self.bobot_maksimum * 100.0, 0.0, 100.0)

    # ------------------------------------------------------------------
    def kalibrasi(self, X: pd.DataFrame, y: np.ndarray) -> "IndeksDasar":
        """Petakan skor menjadi peluang, memakai regresi isotonik.

        Diperlukan agar indeks dasar dapat diadu setara dengan gradient
        boosting: keduanya lalu menghasilkan peluang, sehingga Brier score dan
        galat kalibrasi dapat dibandingkan berdampingan, bukan hanya urutannya.
        """
        skor = self.skor_mentah(X)
        self.kalibrator = IsotonicRegression(out_of_bounds="clip", y_min=0.0, y_max=1.0)
        self.kalibrator.fit(skor, np.asarray(y, dtype=float))
        return self

    def peluang(self, X: pd.DataFrame) -> np.ndarray:
        """Peluang keluarga jatuh atau tetap miskin pada gelombang berikutnya."""
        skor = self.skor_mentah(X)
        if self.kalibrator is None:
            # Tanpa kalibrasi, skor dinormalkan seadanya. Nilainya berguna
            # untuk mengurutkan, tetapi TIDAK boleh ditampilkan sebagai persen.
            return np.clip(skor / max(1e-9, self.bobot_maksimum), 0.0, 1.0)
        return np.clip(self.kalibrator.predict(skor), 0.0, 1.0)

    # ------------------------------------------------------------------
    def jelaskan_baris(self, X: pd.DataFrame, indeks: int) -> list[FaktorTerdeteksi]:
        """Rinci faktor apa saja yang mendorong skor satu keluarga."""
        baris = X.iloc[[indeks]]
        hasil: list[FaktorTerdeteksi] = []
        total = 0.0
        sementara: list[tuple[dict, float]] = []

        for f in self.faktor:
            if bool(evaluasi_ekspresi(f["ekspresi_deteksi"], baris)[0]):
                bobot = float(f.get("bobot_dasar", 1.0))
                sementara.append((f, bobot))
                total += bobot

        for f, bobot in sorted(sementara, key=lambda x: -x[1]):
            hasil.append(
                FaktorTerdeteksi(
                    kode=f["kode"],
                    nama=f["nama"],
                    dimensi=f["dimensi"],
                    bobot=bobot,
                    kontribusi_persen=round(bobot / total * 100.0, 1) if total else 0.0,
                )
            )
        return hasil

    def ringkasan_faktor(self, X: pd.DataFrame) -> pd.DataFrame:
        """Seberapa sering setiap faktor terdeteksi pada seluruh populasi."""
        terdeteksi = self.deteksi(X)
        peta = {f["kode"]: f for f in self.faktor}
        baris = []
        for kode in terdeteksi.columns:
            f = peta[kode]
            baris.append(
                {
                    "kode": kode,
                    "nama": f["nama"],
                    "dimensi": f["dimensi"],
                    "bobot": float(f.get("bobot_dasar", 1.0)),
                    "jumlah": int(terdeteksi[kode].sum()),
                    "proporsi": float(terdeteksi[kode].mean()),
                }
            )
        return pd.DataFrame(baris).sort_values("proporsi", ascending=False)


__all__ = ["FaktorTerdeteksi", "IndeksDasar"]
