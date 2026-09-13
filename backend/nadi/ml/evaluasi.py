"""Metrik evaluasi model penargetan.

Pilihan metrik di sini mengikuti kajian penargetan bantuan sosial, dan
menyimpang dari kebiasaan umum pembelajaran mesin karena satu alasan praktis:
**keluaran NADI adalah antrean, bukan keputusan.**

Yang menentukan manfaat sistem bukanlah berapa persen tebakannya benar,
melainkan berapa banyak keluarga yang benar-benar perlu ditangani berhasil
masuk ke dalam sekian ratus kasus pertama yang sanggup diperiksa petugas.
Karena itu metrik utamanya adalah ``recall@k``, dengan ``k`` sama dengan
kapasitas verifikasi yang nyata.

Akurasi sengaja tidak disediakan sebagai angka utama. Pada persoalan ini
akurasi bukan sekadar kurang berguna, melainkan menyesatkan: bila sebelas
persen keluarga berlabel positif, model yang menjawab "tidak" untuk semua
orang mencapai akurasi delapan puluh sembilan persen dan menemukan nol
keluarga. Angka yang terdengar mengesankan itu justru menandakan sistem yang
sama sekali tidak berguna.

Tiga kelompok metrik disediakan:

* **Peringkat** - AUC, korelasi Spearman, recall dan presisi pada berbagai
  ambang anggaran, serta angka pengganda dibanding pemeriksaan acak.
* **Kalibrasi** - Brier score, galat kalibrasi terharap, dan data diagram
  keandalan. Diperlukan sebab skor ditampilkan sebagai angka kepada manusia;
  "risiko 72 persen" harus benar-benar berarti tujuh puluh dua dari seratus.
* **Keadilan** - metrik yang sama, dipecah menurut kecamatan, jenis kelamin
  kepala keluarga, dan desa-kota. Model yang bekerja baik secara keseluruhan
  namun buruk di satu kecamatan akan mengalirkan anggaran ke arah yang keliru
  selama bertahun-tahun tanpa ada yang menyadarinya.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.metrics import brier_score_loss, roc_auc_score

#: Ambang anggaran verifikasi yang dilaporkan secara baku.
#: Angka ini bukan pilihan statistik melainkan pilihan operasional: berapa
#: banyak keluarga yang sanggup dikunjungi petugas dalam satu triwulan.
AMBANG_ANGGARAN: tuple[int, ...] = (100, 300, 500, 1000, 2000)


@dataclass
class MetrikPeringkat:
    """Metrik yang menilai kualitas urutan antrean."""

    auc: float
    spearman: float
    prevalensi: float
    jumlah_positif: int
    jumlah_baris: int
    pada_anggaran: dict[int, dict[str, float]] = field(default_factory=dict)

    def ringkas(self) -> str:
        bagian = [f"AUC {self.auc:.3f}", f"Spearman {self.spearman:.3f}"]
        for k in (300, 500):
            if k in self.pada_anggaran:
                bagian.append(f"recall@{k} {self.pada_anggaran[k]['recall'] * 100:.1f}%")
        return " | ".join(bagian)


@dataclass
class MetrikKalibrasi:
    """Metrik yang menilai apakah angka probabilitas dapat dipercaya."""

    brier: float
    ece: float
    keandalan: list[dict[str, float]] = field(default_factory=list)

    def ringkas(self) -> str:
        return f"Brier {self.brier:.4f} | ECE {self.ece:.4f}"


@dataclass
class HasilEvaluasi:
    peringkat: MetrikPeringkat
    kalibrasi: MetrikKalibrasi
    keadilan: dict[str, list[dict]] = field(default_factory=dict)
    catatan: list[str] = field(default_factory=list)

    def ke_dict(self) -> dict:
        return {
            "peringkat": {
                "auc": round(self.peringkat.auc, 4),
                "spearman": round(self.peringkat.spearman, 4),
                "prevalensi": round(self.peringkat.prevalensi, 4),
                "jumlah_positif": self.peringkat.jumlah_positif,
                "jumlah_baris": self.peringkat.jumlah_baris,
                "pada_anggaran": {
                    str(k): {n: round(v, 4) for n, v in butir.items()}
                    for k, butir in self.peringkat.pada_anggaran.items()
                },
            },
            "kalibrasi": {
                "brier": round(self.kalibrasi.brier, 5),
                "ece": round(self.kalibrasi.ece, 5),
                "keandalan": self.kalibrasi.keandalan,
            },
            "keadilan": self.keadilan,
            "catatan": self.catatan,
        }


# ---------------------------------------------------------------------------
# Peringkat
# ---------------------------------------------------------------------------
def metrik_pada_anggaran(
    y: np.ndarray, skor: np.ndarray, k: int
) -> dict[str, float]:
    """Hitung metrik untuk ``k`` kasus teratas pada antrean.

    Args:
        y: label sebenarnya.
        skor: skor risiko; makin tinggi makin diprioritaskan.
        k: kapasitas verifikasi - berapa banyak kasus yang sanggup diperiksa.
    """
    n = len(y)
    k = min(k, n)
    if k <= 0 or n == 0:
        return {}

    urut = np.argsort(-skor, kind="stable")[:k]
    tertangkap = int(y[urut].sum())
    total_positif = max(1, int(y.sum()))
    prevalensi = y.mean()

    presisi = tertangkap / k
    recall = tertangkap / total_positif

    # Batas atas recall yang mungkin dicapai pada anggaran ini. Menyajikan
    # recall tanpa batas atasnya menyesatkan ke dua arah sekaligus: pada
    # anggaran kecil, recall 6 persen terdengar buruk padahal batas tertingginya
    # memang hanya 12 persen; pada anggaran besar, recall 90 persen terdengar
    # hebat padahal tercapai dengan memeriksa hampir semua orang. Rasio
    # keduanya - berapa bagian dari yang mungkin benar-benar diraih - adalah
    # angka yang menilai model, bukan menilai besarnya anggaran.
    recall_maksimum = min(1.0, k / total_positif)
    efisiensi = recall / recall_maksimum if recall_maksimum > 0 else 0.0

    return {
        "k": float(k),
        "recall": recall,
        "recall_maksimum": recall_maksimum,
        "efisiensi_anggaran": efisiensi,
        "presisi": presisi,
        "pengganda": presisi / prevalensi if prevalensi > 0 else 0.0,
        "tertangkap": float(tertangkap),
        "terlewat": float(total_positif - tertangkap),
        "eksklusi_pada_anggaran": 1.0 - recall,
    }


def nilai_peringkat(
    y: np.ndarray,
    skor: np.ndarray,
    ambang: Sequence[int] = AMBANG_ANGGARAN,
) -> MetrikPeringkat:
    """Hitung seluruh metrik peringkat."""
    y = np.asarray(y).astype(bool)
    skor = np.asarray(skor, dtype=float)

    if y.sum() == 0 or y.all():
        auc = float("nan")
        rho = float("nan")
    else:
        auc = float(roc_auc_score(y, skor))
        # Korelasi Spearman dipakai, bukan Pearson, sebab penargetan hanya
        # berurusan dengan URUTAN keluarga, bukan dengan jarak antar-skor.
        rho = float(spearmanr(skor, y.astype(float)).statistic)

    return MetrikPeringkat(
        auc=auc,
        spearman=rho,
        prevalensi=float(y.mean()),
        jumlah_positif=int(y.sum()),
        jumlah_baris=int(len(y)),
        pada_anggaran={int(k): metrik_pada_anggaran(y, skor, int(k)) for k in ambang},
    )


def targeting_differential(y: np.ndarray, terpilih: np.ndarray) -> float:
    """Selisih cakupan antara kelompok sasaran dan bukan sasaran.

    Ukuran dari Ravallion: cakupan pada keluarga yang seharusnya disasar
    dikurangi cakupan pada yang tidak. Bernilai nol bila penargetan tidak lebih
    baik daripada pemilihan acak, dan bernilai satu bila sempurna.
    """
    y = np.asarray(y).astype(bool)
    terpilih = np.asarray(terpilih).astype(bool)
    if y.sum() == 0 or (~y).sum() == 0:
        return float("nan")
    return float(terpilih[y].mean() - terpilih[~y].mean())


def indeks_cgh(y: np.ndarray, terpilih: np.ndarray) -> float:
    """Indeks Coady-Grosh-Hoddinott.

    Bagian manfaat yang diterima kelompok sasaran, dibagi porsi kelompok itu
    dalam populasi. Bernilai satu berarti setara pembagian merata; nilai di
    atas satu berarti penargetan berpihak kepada kelompok sasaran.
    """
    y = np.asarray(y).astype(bool)
    terpilih = np.asarray(terpilih).astype(bool)
    total = terpilih.sum()
    if total == 0 or y.mean() == 0:
        return float("nan")
    return float((terpilih & y).sum() / total / y.mean())


# ---------------------------------------------------------------------------
# Kalibrasi
# ---------------------------------------------------------------------------
def nilai_kalibrasi(y: np.ndarray, peluang: np.ndarray, jumlah_bin: int = 12) -> MetrikKalibrasi:
    """Hitung Brier score, galat kalibrasi terharap, dan data diagram keandalan.

    Galat kalibrasi terharap adalah rata-rata tertimbang selisih antara
    peluang yang diperkirakan dan kejadian yang benar-benar teramati pada tiap
    kelompok. Nilai nol berarti angka yang ditampilkan dapat dibaca apa adanya.
    """
    y = np.asarray(y).astype(float)
    p = np.clip(np.asarray(peluang, dtype=float), 0.0, 1.0)

    brier = float(brier_score_loss(y, p)) if len(y) else float("nan")

    # Pengelompokan memakai kuantil, bukan selang yang sama lebar. Pada
    # persoalan dengan kelas langka, sebagian besar prediksi menumpuk di
    # peluang rendah, sehingga selang sama lebar akan menghasilkan kelompok
    # kosong dan galat kalibrasi yang tidak berarti.
    try:
        tepi = np.unique(np.quantile(p, np.linspace(0, 1, jumlah_bin + 1)))
    except (ValueError, IndexError):
        tepi = np.array([0.0, 1.0])
    if len(tepi) < 2:
        tepi = np.array([0.0, 1.0])

    indeks = np.clip(np.digitize(p, tepi[1:-1], right=False), 0, len(tepi) - 2)
    keandalan: list[dict[str, float]] = []
    ece = 0.0
    n = max(1, len(y))

    for b in range(len(tepi) - 1):
        penanda = indeks == b
        jumlah = int(penanda.sum())
        if jumlah == 0:
            continue
        rata_peluang = float(p[penanda].mean())
        rata_kejadian = float(y[penanda].mean())
        ece += (jumlah / n) * abs(rata_peluang - rata_kejadian)
        keandalan.append(
            {
                "bin": b,
                "batas_bawah": round(float(tepi[b]), 4),
                "batas_atas": round(float(tepi[b + 1]), 4),
                "jumlah": jumlah,
                "rata_peluang": round(rata_peluang, 4),
                "rata_kejadian": round(rata_kejadian, 4),
                "selisih": round(rata_peluang - rata_kejadian, 4),
            }
        )

    return MetrikKalibrasi(brier=brier, ece=float(ece), keandalan=keandalan)


# ---------------------------------------------------------------------------
# Keadilan
# ---------------------------------------------------------------------------
def nilai_keadilan(
    y: np.ndarray,
    skor: np.ndarray,
    kelompok: pd.Series,
    nama_kelompok: str,
    k: int = 500,
    minimum_baris: int = 200,
) -> list[dict]:
    """Pecah metrik peringkat menurut satu ciri kelompok.

    Ukuran yang dipakai adalah kesetaraan peluang: di antara keluarga yang
    memang berlabel positif, apakah peluang masuk antrean prioritas sama besar
    bagi setiap kelompok. Ukuran ini dipilih ketimbang kesetaraan proporsi
    keluaran, sebab kecamatan memang berbeda tingkat kemiskinannya - menuntut
    proporsi kasus yang sama di setiap kecamatan justru akan memindahkan
    perhatian menjauh dari tempat yang paling membutuhkan.

    Anggaran ``k`` dibagi berbanding lurus dengan ukuran kelompok, sehingga
    perbandingan antar-kelompok berlangsung setara.
    """
    y = np.asarray(y).astype(bool)
    skor = np.asarray(skor, dtype=float)
    nilai_kelompok = pd.Series(kelompok).reset_index(drop=True)

    hasil: list[dict] = []
    total = len(y)
    for nilai in sorted(nilai_kelompok.dropna().unique()):
        penanda = (nilai_kelompok == nilai).to_numpy()
        jumlah = int(penanda.sum())
        if jumlah < minimum_baris:
            continue

        y_k = y[penanda]
        s_k = skor[penanda]
        if y_k.sum() == 0 or y_k.all():
            continue

        k_kelompok = max(1, int(round(k * jumlah / total)))
        butir = metrik_pada_anggaran(y_k, s_k, k_kelompok)
        hasil.append(
            {
                "kelompok": nama_kelompok,
                "nilai": str(nilai),
                "jumlah_baris": jumlah,
                "prevalensi": round(float(y_k.mean()), 4),
                "auc": round(float(roc_auc_score(y_k, s_k)), 4),
                "k": int(k_kelompok),
                "recall_pada_k": round(butir.get("recall", float("nan")), 4),
                "presisi_pada_k": round(butir.get("presisi", float("nan")), 4),
                "pengganda": round(butir.get("pengganda", float("nan")), 3),
            }
        )
    return hasil


# ---------------------------------------------------------------------------
# Titik masuk
# ---------------------------------------------------------------------------
def evaluasi_lengkap(
    y: np.ndarray,
    peluang: np.ndarray,
    meta: pd.DataFrame | None = None,
    *,
    ambang: Sequence[int] = AMBANG_ANGGARAN,
    k_keadilan: int = 500,
) -> HasilEvaluasi:
    """Jalankan seluruh pemeriksaan dan kembalikan hasilnya."""
    peringkat = nilai_peringkat(y, peluang, ambang)
    kalibrasi = nilai_kalibrasi(y, peluang)

    keadilan: dict[str, list[dict]] = {}
    if meta is not None and len(meta) == len(y):
        for kolom, nama in (
            ("kecamatan", "kecamatan"),
            ("kk_perempuan", "kepala_keluarga_perempuan"),
            ("perdesaan", "wilayah_perdesaan"),
        ):
            if kolom in meta.columns:
                keadilan[nama] = nilai_keadilan(
                    y, peluang, meta[kolom], nama, k=k_keadilan
                )

    catatan: list[str] = []
    if peringkat.auc == peringkat.auc and peringkat.auc > 0.90:
        catatan.append(
            f"AUC {peringkat.auc:.3f} berada di atas 0,90. Pada persoalan penargetan "
            "kemiskinan, angka setinggi ini lebih sering menandakan kebocoran data "
            "daripada model yang baik. Kajian melaporkan batas atas yang wajar sekitar "
            "0,85 bahkan untuk proxy means test yang terkalibrasi sempurna. "
            "Periksa kembali daftar fitur sebelum mempercayai angka ini."
        )
    if peringkat.auc == peringkat.auc and peringkat.auc < 0.65:
        catatan.append(
            f"AUC {peringkat.auc:.3f} berada di bawah 0,65, yakni di bawah kinerja "
            "penargetan berbasis wilayah semata. Model belum layak dipakai "
            "memprioritaskan verifikasi."
        )
    if kalibrasi.ece > 0.05:
        catatan.append(
            f"Galat kalibrasi {kalibrasi.ece:.3f} tergolong besar. Angka peluang "
            "sebaiknya belum ditampilkan sebagai persentase kepada pengguna sebelum "
            "kalibrasi diperbaiki."
        )

    for nama, baris in keadilan.items():
        if len(baris) < 2:
            continue
        nilai_recall = [b["recall_pada_k"] for b in baris if b["recall_pada_k"] == b["recall_pada_k"]]
        if len(nilai_recall) >= 2:
            jurang = max(nilai_recall) - min(nilai_recall)
            if jurang > 0.15:
                catatan.append(
                    f"Selisih recall antar-{nama} mencapai {jurang * 100:.1f} poin persen. "
                    "Kelompok dengan recall terendah akan tertinggal secara berulang "
                    "pada setiap putaran penetapan sasaran."
                )

    return HasilEvaluasi(
        peringkat=peringkat, kalibrasi=kalibrasi, keadilan=keadilan, catatan=catatan
    )


__all__ = [
    "AMBANG_ANGGARAN",
    "HasilEvaluasi",
    "MetrikKalibrasi",
    "MetrikPeringkat",
    "evaluasi_lengkap",
    "indeks_cgh",
    "metrik_pada_anggaran",
    "nilai_kalibrasi",
    "nilai_keadilan",
    "nilai_peringkat",
    "targeting_differential",
]
