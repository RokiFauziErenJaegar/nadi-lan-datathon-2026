"""Penjelasan skor: dari nilai TreeSHAP menjadi alasan yang dapat dibaca.

Proposal NADI menjanjikan bahwa skor tidak menjadi "kotak hitam". Modul ini
yang memenuhinya, dan caranya berlapis tiga sebab masing-masing lapis menjawab
pertanyaan yang berbeda.

**Lapis satu - kontribusi fitur.** Nilai TreeSHAP menyatakan berapa besar tiap
fitur mendorong atau menahan skor keluarga ini, dibanding keluarga rata-rata.
Sifatnya aditif: seluruh kontribusi ditambah nilai dasar menghasilkan tepat
keluaran model. Ini lapis yang benar secara matematis namun belum berguna bagi
petugas.

**Lapis dua - faktor risiko.** Kontribusi fitur dikelompokkan menurut faktor
risiko yang diwakilinya. "Luas lantai per orang", "jumlah kriteria rumah layak
huni", dan "ketahanan bangunan" bukanlah tiga temuan terpisah - ketiganya
mengatakan satu hal, yakni rumah tidak layak huni. Petugas perlu mendengar satu
hal itu, bukan tiga angka.

**Lapis tiga - kalimat.** Faktor teratas disusun menjadi kalimat berbahasa
Indonesia yang siap dibaca, tanpa melibatkan model bahasa sama sekali. Penting
bahwa lapis ini berjalan tanpa jaringan: bila layanan AI mati saat demonstrasi,
penjelasan tetap muncul utuh. Model bahasa nantinya hanya memperhalus
penyajian, tidak pernah menjadi sumber alasannya.

Satu peringatan yang wajib ikut ditampilkan di antarmuka: nilai TreeSHAP
menerangkan **apa yang dilihat model**, bukan **apa yang menyebabkan
kemiskinan**. Keduanya kerap tertukar, dan tertukarnya berbahaya - anggaran
dapat diarahkan untuk memperbaiki penanda alih-alih memperbaiki keadaan.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

from nadi.config import settings
from nadi.db.enums import DimensiRisiko
from nadi.ml.fitur import PETA_FITUR

logger = logging.getLogger("nadi.ml.jelas")

#: Ambang kontribusi terkecil yang layak ditampilkan, dalam satuan log-odds.
#: Kontribusi di bawah ini tidak mengubah kesimpulan apa pun dan hanya
#: memperpanjang daftar.
AMBANG_KONTRIBUSI = 0.02


@dataclass
class KontribusiFitur:
    """Sumbangan satu fitur terhadap skor seorang keluarga."""

    nama: str
    label: str
    nilai: float
    kontribusi: float
    dimensi: str
    kode_risiko: str | None
    arah: str
    """``menaikkan`` bila mendorong skor naik, ``menurunkan`` bila menahan."""

    def ke_dict(self) -> dict:
        return {
            "fitur": self.nama,
            "label": self.label,
            "nilai": round(float(self.nilai), 4),
            "kontribusi": round(float(self.kontribusi), 4),
            "dimensi": self.dimensi,
            "kode_risiko": self.kode_risiko,
            "arah": self.arah,
        }


@dataclass
class FaktorPendorong:
    """Satu faktor risiko beserta bobot dan bukti pendukungnya."""

    kode: str
    nama: str
    dimensi: str
    kontribusi: float
    bagian_persen: float
    bukti: list[KontribusiFitur] = field(default_factory=list)

    def ke_dict(self) -> dict:
        return {
            "kode": self.kode,
            "nama": self.nama,
            "dimensi": self.dimensi,
            "kontribusi": round(float(self.kontribusi), 4),
            "bagian_persen": round(float(self.bagian_persen), 1),
            "bukti": [b.ke_dict() for b in self.bukti],
        }


@dataclass
class PenjelasanSkor:
    """Penjelasan lengkap satu skor kerentanan."""

    skor: float
    peluang: float
    nilai_dasar: float
    faktor_pendorong: list[FaktorPendorong] = field(default_factory=list)
    faktor_penahan: list[FaktorPendorong] = field(default_factory=list)
    kontribusi_fitur: list[KontribusiFitur] = field(default_factory=list)
    kalimat: str = ""
    peringatan: str = (
        "Penjelasan ini menerangkan apa yang dibaca model, bukan sebab-akibat "
        "kemiskinan. Memperbaiki satu penanda tidak dengan sendirinya "
        "memperbaiki keadaan keluarga."
    )

    def ke_dict(self) -> dict:
        return {
            "skor": round(float(self.skor), 2),
            "peluang": round(float(self.peluang), 4),
            "nilai_dasar": round(float(self.nilai_dasar), 4),
            "faktor_pendorong": [f.ke_dict() for f in self.faktor_pendorong],
            "faktor_penahan": [f.ke_dict() for f in self.faktor_penahan],
            "kontribusi_fitur": [k.ke_dict() for k in self.kontribusi_fitur],
            "kalimat": self.kalimat,
            "peringatan": self.peringatan,
        }


# ===========================================================================
class Penjelas:
    """Mengubah keluaran TreeSHAP menjadi alasan yang dapat dibaca petugas."""

    def __init__(self, katalog_faktor: list[dict] | None = None) -> None:
        self.katalog = {
            f["kode"]: f for f in (katalog_faktor or self._muat_katalog())
        }

    @staticmethod
    def _muat_katalog() -> list[dict]:
        berkas = settings.seed_dir / "faktor_risiko.json"
        return json.loads(berkas.read_text(encoding="utf-8"))["faktor_risiko"]

    # ------------------------------------------------------------------
    def jelaskan(
        self,
        X: pd.DataFrame,
        kontribusi: np.ndarray,
        skor: np.ndarray,
        peluang: np.ndarray,
        indeks: int,
        *,
        maksimum_faktor: int = 5,
        maksimum_fitur: int = 12,
    ) -> PenjelasanSkor:
        """Susun penjelasan untuk satu baris.

        Args:
            X: matriks fitur, berkolomkan nama fitur sesuai urutan model.
            kontribusi: keluaran TreeSHAP berukuran (baris, fitur + 1).
            skor: skor nol sampai seratus.
            peluang: peluang terkalibrasi.
            indeks: baris yang dijelaskan.
        """
        nama_kolom = list(X.columns)
        baris_kontribusi = kontribusi[indeks]
        nilai_dasar = float(baris_kontribusi[-1])

        butir: list[KontribusiFitur] = []
        for j, nama in enumerate(nama_kolom):
            k = float(baris_kontribusi[j])
            if abs(k) < AMBANG_KONTRIBUSI:
                continue
            f = PETA_FITUR.get(nama)
            butir.append(
                KontribusiFitur(
                    nama=nama,
                    label=f.label if f else nama,
                    nilai=float(X.iloc[indeks, j]),
                    kontribusi=k,
                    dimensi=(f.dimensi.value if f else "lainnya"),
                    kode_risiko=(f.kode_risiko if f else None),
                    arah="menaikkan" if k > 0 else "menurunkan",
                )
            )

        butir.sort(key=lambda b: -abs(b.kontribusi))

        # Pengelompokan dilakukan LEBIH DAHULU, baru dipisah menurut arah.
        #
        # Urutan sebaliknya - memisah fitur positif dan negatif lalu
        # mengelompokkan keduanya - sempat dipakai dan menghasilkan keluaran
        # yang membingungkan: satu faktor risiko muncul serentak sebagai
        # pendorong dan penahan, sehingga kalimat penjelasannya berbunyi
        # "pendorong utama: pendapatan sangat rendah; faktor yang menahan:
        # pendapatan sangat rendah". Yang benar adalah menjumlahkan seluruh
        # sumbangan sebuah faktor lebih dahulu, lalu menilai arah bersihnya.
        semua_faktor = self._kelompokkan(butir)
        pendorong = [f for f in semua_faktor if f.kontribusi > 0]
        penahan = [f for f in semua_faktor if f.kontribusi < 0]

        penjelasan = PenjelasanSkor(
            skor=float(skor[indeks]),
            peluang=float(peluang[indeks]),
            nilai_dasar=nilai_dasar,
            faktor_pendorong=pendorong[:maksimum_faktor],
            faktor_penahan=penahan[:3],
            kontribusi_fitur=butir[:maksimum_fitur],
        )
        penjelasan.kalimat = self.susun_kalimat(penjelasan)
        return penjelasan

    # ------------------------------------------------------------------
    def _kelompokkan(self, butir: list[KontribusiFitur]) -> list[FaktorPendorong]:
        """Kelompokkan kontribusi fitur menurut faktor risiko yang diwakilinya."""
        kumpulan: dict[str, list[KontribusiFitur]] = {}
        for b in butir:
            kunci = b.kode_risiko or f"_{b.dimensi}"
            kumpulan.setdefault(kunci, []).append(b)

        # Pembagi memakai jumlah nilai mutlak sumbangan bersih tiap faktor,
        # bukan jumlah seluruh fitur. Dengan begitu bagian persen tiap faktor
        # menjumlah menjadi seratus dan dapat dibaca apa adanya oleh pengguna.
        bersih = {k: sum(b.kontribusi for b in v) for k, v in kumpulan.items()}
        total = sum(abs(v) for v in bersih.values()) or 1.0

        hasil: list[FaktorPendorong] = []
        for kunci, anggota in kumpulan.items():
            jumlah = bersih[kunci]
            info = self.katalog.get(kunci)
            if info:
                nama, dimensi = info["nama"], info["dimensi"]
            else:
                dimensi = anggota[0].dimensi
                try:
                    nama = DimensiRisiko(dimensi).label
                except ValueError:
                    nama = dimensi
            hasil.append(
                FaktorPendorong(
                    kode=kunci,
                    nama=nama,
                    dimensi=dimensi,
                    kontribusi=jumlah,
                    bagian_persen=abs(jumlah) / total * 100.0,
                    bukti=sorted(anggota, key=lambda b: -abs(b.kontribusi))[:4],
                )
            )
        return sorted(hasil, key=lambda f: -abs(f.kontribusi))

    # ------------------------------------------------------------------
    @staticmethod
    def susun_kalimat(penjelasan: PenjelasanSkor) -> str:
        """Susun ringkasan berbahasa Indonesia, tanpa melibatkan model bahasa.

        Dikerjakan dari templat dengan sengaja. Penjelasan atas keputusan yang
        memengaruhi siapa menerima bantuan harus dapat diulang persis dan
        diperiksa kembali berbulan-bulan kemudian - dua sifat yang tidak dapat
        dijamin oleh kalimat yang dibangkitkan model bahasa.
        """
        # Pembulatan ke bawah, bukan ke terdekat. Skor 99,5 yang ditulis
        # "100 dari 100" akan terbaca sebagai kepastian, sekaligus tidak cocok
        # dengan angka 99,5 yang tampil di sebelahnya pada layar yang sama.
        nilai = int(penjelasan.skor)

        if not penjelasan.faktor_pendorong:
            return (
                f"Skor kerentanan {nilai} dari 100. Tidak ada faktor "
                "risiko menonjol yang terdeteksi pada keluarga ini."
            )

        tingkat = (
            "sangat tinggi"
            if penjelasan.skor >= 80
            else "tinggi"
            if penjelasan.skor >= 60
            else "sedang"
            if penjelasan.skor >= 40
            else "rendah"
        )

        utama = penjelasan.faktor_pendorong[:3]
        daftar = "; ".join(
            f"{f.nama.lower()} ({f.bagian_persen:.0f} persen dari dorongan skor)"
            for f in utama
        )

        kalimat = (
            f"Skor kerentanan {nilai} dari 100, tergolong {tingkat}. "
            f"Pendorong utama: {daftar}."
        )

        if penjelasan.faktor_penahan:
            penahan = penjelasan.faktor_penahan[0]
            kalimat += f" Faktor yang menahan risiko: {penahan.nama.lower()}."

        return kalimat

    # ------------------------------------------------------------------
    def faktor_dominan(
        self, X: pd.DataFrame, kontribusi: np.ndarray, maksimum: int = 3
    ) -> list[list[str]]:
        """Kode faktor risiko dominan untuk SETIAP baris sekaligus.

        Dikerjakan secara vektor sebab menilai empat puluh ribu keluarga satu
        per satu memakan waktu berpuluh detik, sedangkan hasil ini diperlukan
        pada setiap penilaian ulang seluruh kabupaten.
        """
        nama_kolom = list(X.columns)
        kode_per_kolom = [
            (PETA_FITUR[n].kode_risiko if n in PETA_FITUR else None) for n in nama_kolom
        ]
        kode_unik = sorted({k for k in kode_per_kolom if k})

        sumbangan = np.zeros((len(X), len(kode_unik)), dtype=np.float32)
        for i, kode in enumerate(kode_unik):
            kolom = [j for j, k in enumerate(kode_per_kolom) if k == kode]
            if kolom:
                sumbangan[:, i] = kontribusi[:, kolom].sum(axis=1)

        urutan = np.argsort(-sumbangan, axis=1)[:, :maksimum]
        hasil: list[list[str]] = []
        for baris in range(len(X)):
            kode_baris = [
                kode_unik[j] for j in urutan[baris] if sumbangan[baris, j] > AMBANG_KONTRIBUSI
            ]
            hasil.append(kode_baris)
        return hasil


__all__ = [
    "AMBANG_KONTRIBUSI",
    "FaktorPendorong",
    "KontribusiFitur",
    "PenjelasanSkor",
    "Penjelas",
]
