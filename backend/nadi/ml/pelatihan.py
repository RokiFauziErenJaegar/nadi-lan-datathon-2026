"""Pelatihan model kerentanan berbasis gradient boosting.

Beberapa keputusan rancangan di sini diambil dengan sadar dan layak dijelaskan.

**Pembagian data bersifat menurut waktu, bukan acak.** Gelombang awal dipakai
melatih, gelombang berikutnya mengkalibrasi, gelombang terakhir menguji.
Pembagian acak akan menempatkan keadaan bulan Maret dan bulan September pada
keluarga yang sama di kedua sisi, sehingga model dinilai atas kemampuannya
mengingat, bukan meramalkan. Pembagian menurut waktu meniru keadaan
sesungguhnya: melatih dari riwayat, lalu memakainya menghadapi pemutakhiran
yang belum datang.

**Kalibrasi memakai gelombang tersendiri.** Gradient boosting menghasilkan
skor yang urutannya baik namun angkanya tidak dapat dibaca apa adanya. Karena
antarmuka NADI menampilkan angka peluang kepada manusia, dan karena ambang
keputusan memicu tindakan nyata, angka itu wajib berarti apa yang tertulis.
Regresi isotonik dipasang pada gelombang yang tidak dipakai melatih.

**Penjelasan memakai TreeSHAP bawaan LightGBM.** Pustaka ``shap`` tidak
diperlukan: LightGBM menghitung nilai TreeSHAP yang persis sama secara
langsung, jauh lebih cepat, dan tanpa menambah ketergantungan berukuran ratusan
megabita pada peladen.

**Bobot kelas tidak diubah.** Menaikkan bobot kelas positif akan memperbaiki
sebagian metrik namun merusak kalibrasi, padahal kalibrasi justru yang
diperlukan agar angka pada layar dapat dipercaya. Ketimpangan kelas ditangani
di tempat yang semestinya - pada cara metrik dibaca, yakni lewat ``recall@k``
pada anggaran verifikasi yang nyata, bukan lewat akurasi.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.isotonic import IsotonicRegression

from nadi.config import settings
from nadi.ml.dataset import DatasetLatih
from nadi.ml.evaluasi import HasilEvaluasi, evaluasi_lengkap
from nadi.ml.fitur import NAMA_FITUR, NAMA_FITUR_OPERASIONAL, PETA_FITUR

logger = logging.getLogger("nadi.ml.latih")

#: Parameter LightGBM. Dipilih condong ke arah kesederhanaan model.
#:
#: ``min_data_in_leaf`` sengaja besar. Model yang boleh membentuk daun berisi
#: dua puluh keluarga akan menemukan pola yang hanya berlaku pada dua puluh
#: keluarga itu, lalu meleset ketika dipakai. Pada penargetan bantuan sosial,
#: kekeliruan semacam itu berwujud petugas yang dikirim ke alamat yang salah -
#: dan keluarga yang benar-benar membutuhkan tidak dikunjungi siapa pun.
PARAMETER_LGBM: dict[str, Any] = {
    "objective": "binary",
    "metric": ["auc", "binary_logloss"],
    "boosting_type": "gbdt",
    "learning_rate": 0.05,
    "num_leaves": 31,
    "max_depth": 6,
    "min_data_in_leaf": 250,
    "feature_fraction": 0.80,
    "bagging_fraction": 0.80,
    "bagging_freq": 1,
    "lambda_l1": 0.1,
    "lambda_l2": 1.0,
    "verbose": -1,
    "num_threads": 0,
    "deterministic": True,
    "force_row_wise": True,
}


@dataclass
class PembagianData:
    """Pembagian dataset menurut gelombang waktu."""

    latih: DatasetLatih
    kalibrasi: DatasetLatih
    uji: DatasetLatih
    gelombang_latih: list[int]
    gelombang_kalibrasi: list[int]
    gelombang_uji: list[int]

    def ringkas(self) -> str:
        return (
            f"latih {self.latih.n:,} (gelombang {self.gelombang_latih}) | "
            f"kalibrasi {self.kalibrasi.n:,} (gelombang {self.gelombang_kalibrasi}) | "
            f"uji {self.uji.n:,} (gelombang {self.gelombang_uji})"
        ).replace(",", ".")


@dataclass
class ModelKerentanan:
    """Model terlatih beserta kalibrator dan riwayatnya."""

    booster: lgb.Booster
    kalibrator: IsotonicRegression | None = None
    nama_fitur: tuple[str, ...] = NAMA_FITUR
    metrik: dict = field(default_factory=dict)
    metrik_keadilan: dict = field(default_factory=dict)
    kepentingan_fitur: dict = field(default_factory=dict)
    gelombang_latih: list[int] = field(default_factory=list)
    gelombang_uji: list[int] = field(default_factory=list)
    jumlah_baris_latih: int = 0
    dilatih_pada: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    versi: str = "v1.0.0"
    catatan: list[str] = field(default_factory=list)

    # ------------------------------------------------------------------
    def _susun(self, X: pd.DataFrame) -> pd.DataFrame:
        """Pastikan kolom hadir dan berurutan persis seperti saat pelatihan.

        Urutan kolom yang bergeser adalah salah satu penyebab kekeliruan
        prediksi yang paling sulit dilacak, sebab tidak menimbulkan galat -
        model hanya diam-diam membaca luas lantai sebagai jumlah balita.
        """
        hilang = [n for n in self.nama_fitur if n not in X.columns]
        if hilang:
            raise ValueError(
                "Fitur berikut tidak ada pada masukan: " + ", ".join(hilang)
            )
        return X[list(self.nama_fitur)]

    def peluang_mentah(self, X: pd.DataFrame) -> np.ndarray:
        """Keluaran model sebelum kalibrasi. Baik untuk mengurutkan, tidak untuk ditampilkan."""
        return self.booster.predict(self._susun(X), num_iteration=self.booster.best_iteration)

    #: Batas bawah dan atas peluang yang boleh ditampilkan.
    #:
    #: Regresi isotonik dapat menghasilkan nol atau satu persis ketika seluruh
    #: contoh pada kelompok terujung berlabel sama. Angka itu benar secara
    #: aritmetika namun keliru untuk ditampilkan: menyatakan "peluang 100
    #: persen" berarti sistem mengaku tidak mungkin salah, padahal ia dilatih
    #: pada beberapa ribu keluarga dan menghadapi masa depan yang belum
    #: terjadi. Pembatasan ini menjaga agar sistem tidak pernah mengaku pasti.
    BATAS_PELUANG: tuple[float, float] = (0.005, 0.995)

    def peluang(self, X: pd.DataFrame) -> np.ndarray:
        """Peluang terkalibrasi keluarga jatuh atau tetap miskin pada gelombang berikutnya."""
        mentah = self.peluang_mentah(X)
        if self.kalibrator is None:
            hasil = mentah
        else:
            hasil = self.kalibrator.predict(mentah)
        return np.clip(hasil, *self.BATAS_PELUANG)

    def skor(self, X: pd.DataFrame) -> np.ndarray:
        """NADI Vulnerability Score pada rentang nol sampai seratus."""
        return np.round(self.peluang(X) * 100.0, 2)

    def kontribusi(self, X: pd.DataFrame) -> np.ndarray:
        """Nilai TreeSHAP per fitur.

        Returns:
            Larik berukuran (baris, jumlah fitur + 1). Kolom terakhir adalah
            nilai dasar, yakni keluaran model bila tak satu pun fitur diketahui.
            Jumlah seluruh kolom sama dengan keluaran model dalam skala log-odds.
        """
        return self.booster.predict(
            self._susun(X),
            num_iteration=self.booster.best_iteration,
            pred_contrib=True,
        )

    # ------------------------------------------------------------------
    def simpan(self, folder: Path | None = None) -> Path:
        folder = folder or settings.models_dir
        folder.mkdir(parents=True, exist_ok=True)
        jalur = folder / f"model_kerentanan_{self.versi}.joblib"
        joblib.dump(self, jalur, compress=3)
        logger.info("Model disimpan: %s (%.1f KB)", jalur.name, jalur.stat().st_size / 1024)
        return jalur

    @staticmethod
    def muat(jalur: Path) -> "ModelKerentanan":
        return joblib.load(jalur)


# ===========================================================================
# Pembagian
# ===========================================================================
def bagi_menurut_waktu(
    dataset: DatasetLatih,
    *,
    porsi_kalibrasi: int = 1,
    porsi_uji: int = 1,
) -> PembagianData:
    """Bagi dataset menurut gelombang: yang terlama melatih, yang terbaru menguji."""
    gelombang = sorted(int(g) for g in dataset.meta["gelombang"].unique())
    if len(gelombang) < porsi_kalibrasi + porsi_uji + 1:
        raise ValueError(
            f"Diperlukan minimal {porsi_kalibrasi + porsi_uji + 1} gelombang, "
            f"tersedia {len(gelombang)}."
        )

    g_uji = gelombang[-porsi_uji:]
    g_kal = gelombang[-(porsi_uji + porsi_kalibrasi) : -porsi_uji]
    g_latih = gelombang[: -(porsi_uji + porsi_kalibrasi)]

    return PembagianData(
        latih=dataset.saring_gelombang(g_latih),
        kalibrasi=dataset.saring_gelombang(g_kal),
        uji=dataset.saring_gelombang(g_uji),
        gelombang_latih=g_latih,
        gelombang_kalibrasi=g_kal,
        gelombang_uji=g_uji,
    )


# ===========================================================================
# Pelatihan
# ===========================================================================
def latih_model(
    dataset: DatasetLatih,
    *,
    fitur_dipakai: tuple[str, ...] = NAMA_FITUR_OPERASIONAL,
    parameter: dict[str, Any] | None = None,
    putaran_maksimum: int = 1500,
    henti_dini: int = 80,
    versi: str = "v1.0.0",
    benih: int | None = None,
) -> tuple[ModelKerentanan, PembagianData, HasilEvaluasi]:
    """Latih model kerentanan dan nilai kinerjanya pada gelombang penguji.

    Args:
        fitur_dipakai: himpunan fitur yang boleh dilihat model. Bawaannya
            :data:`nadi.ml.fitur.NAMA_FITUR_OPERASIONAL` - yaitu DTSEN
            ditambah sinyal lintas dinas, tanpa pengeluaran terukur. Melatih
            dengan seluruh fitur menghasilkan angka yang jauh lebih baik dan
            tidak dapat dijalankan, sebab pengeluaran terukur tidak akan
            tersedia saat sistem benar-benar dipakai.
    """
    bagi = bagi_menurut_waktu(dataset)
    logger.info("Pembagian data: %s", bagi.ringkas())

    param = {**PARAMETER_LGBM, **(parameter or {})}
    param["seed"] = benih if benih is not None else settings.random_seed
    param["bagging_seed"] = param["seed"] + 1
    param["feature_fraction_seed"] = param["seed"] + 2

    X_latih = bagi.latih.X[list(fitur_dipakai)]
    X_kal = bagi.kalibrasi.X[list(fitur_dipakai)]

    d_latih = lgb.Dataset(X_latih, label=bagi.latih.y.astype(int), free_raw_data=False)
    d_kal = lgb.Dataset(X_kal, label=bagi.kalibrasi.y.astype(int), reference=d_latih)

    logger.info("Melatih LightGBM pada %d baris, %d fitur...", len(X_latih), len(fitur_dipakai))
    booster = lgb.train(
        param,
        d_latih,
        num_boost_round=putaran_maksimum,
        valid_sets=[d_kal],
        valid_names=["kalibrasi"],
        callbacks=[
            lgb.early_stopping(henti_dini, verbose=False),
            lgb.log_evaluation(period=0),
        ],
    )
    logger.info("Selesai pada putaran ke-%d.", booster.best_iteration)

    model = ModelKerentanan(
        booster=booster,
        nama_fitur=tuple(fitur_dipakai),
        gelombang_latih=bagi.gelombang_latih,
        gelombang_uji=bagi.gelombang_uji,
        jumlah_baris_latih=len(X_latih),
        versi=versi,
    )

    # --- Kalibrasi ---
    # Gelombang kalibrasi dipakai dua kali: menghentikan pelatihan lebih dini
    # dan memasang kalibrator. Pemakaian ganda ini membuat kalibrasi sedikit
    # optimistis, namun jauh lebih ringan akibatnya daripada kehilangan satu
    # gelombang penuh dari data latih. Angka kalibrasi yang dilaporkan diambil
    # dari gelombang PENGUJI, yang tidak tersentuh keduanya.
    mentah_kal = model.peluang_mentah(X_kal)
    model.kalibrator = IsotonicRegression(out_of_bounds="clip", y_min=0.0, y_max=1.0)
    model.kalibrator.fit(mentah_kal, bagi.kalibrasi.y.astype(float))

    # --- Penilaian pada gelombang penguji ---
    p_uji = model.peluang(bagi.uji.X)
    hasil = evaluasi_lengkap(bagi.uji.y, p_uji, bagi.uji.meta)

    model.metrik = hasil.ke_dict()["peringkat"] | {"kalibrasi": hasil.ke_dict()["kalibrasi"]}
    model.metrik_keadilan = hasil.keadilan
    model.catatan = hasil.catatan
    model.kepentingan_fitur = _kepentingan(booster)

    logger.info("Hasil pada gelombang penguji: %s | %s",
                hasil.peringkat.ringkas(), hasil.kalibrasi.ringkas())
    for c in hasil.catatan:
        logger.warning("%s", c)

    return model, bagi, hasil


def _kepentingan(booster: lgb.Booster) -> dict[str, float]:
    """Kepentingan fitur menurut perolehan, dinormalkan menjadi persen."""
    nilai = booster.feature_importance(importance_type="gain")
    nama = booster.feature_name()
    total = float(nilai.sum()) or 1.0
    pasangan = sorted(zip(nama, nilai), key=lambda x: -x[1])
    return {n: round(float(v) / total * 100.0, 3) for n, v in pasangan}


# ===========================================================================
# Pemeriksaan ketahanan
# ===========================================================================
def uji_keluarga_terpisah(
    dataset: DatasetLatih,
    model_pembanding: ModelKerentanan,
    *,
    porsi_uji: float = 0.25,
    benih: int | None = None,
) -> dict[str, Any]:
    """Uji kemampuan model menghadapi keluarga yang belum pernah dilihat.

    Pembagian menurut waktu menguji hal yang berbeda: model boleh saja
    mengenali keluarga yang sama pada gelombang lain. Pemeriksaan ini memisahkan
    keluarga secara utuh, sehingga menjawab pertanyaan "apakah model tetap
    berguna bagi keluarga yang baru masuk pendataan" - keadaan yang terjadi
    setiap kali ada pemutakhiran data.
    """
    rng = np.random.default_rng(benih if benih is not None else settings.random_seed)
    keluarga = dataset.meta["keluarga_id"].unique()
    rng.shuffle(keluarga)
    batas = int(len(keluarga) * (1 - porsi_uji))
    keluarga_latih, keluarga_uji = keluarga[:batas], keluarga[batas:]

    bagian_latih = dataset.saring_keluarga(keluarga_latih)
    bagian_uji = dataset.saring_keluarga(keluarga_uji)

    param = {**PARAMETER_LGBM, "seed": int(rng.integers(1, 10**6))}
    d = lgb.Dataset(bagian_latih.X[list(model_pembanding.nama_fitur)], label=bagian_latih.y.astype(int))
    booster = lgb.train(param, d, num_boost_round=model_pembanding.booster.best_iteration or 300)

    p = booster.predict(bagian_uji.X[list(model_pembanding.nama_fitur)])
    hasil = evaluasi_lengkap(bagian_uji.y, p, bagian_uji.meta)
    return {
        "jumlah_keluarga_latih": int(len(keluarga_latih)),
        "jumlah_keluarga_uji": int(len(keluarga_uji)),
        "auc": round(hasil.peringkat.auc, 4),
        "recall_500": round(hasil.peringkat.pada_anggaran[500]["recall"], 4),
        "presisi_500": round(hasil.peringkat.pada_anggaran[500]["presisi"], 4),
    }


def uji_kecamatan_ditinggalkan(
    dataset: DatasetLatih,
    *,
    putaran: int = 300,
    benih: int | None = None,
) -> list[dict[str, Any]]:
    """Latih tanpa satu kecamatan, lalu uji pada kecamatan itu.

    Menjawab pertanyaan yang menentukan kelayakan replikasi: apakah model tetap
    berguna di wilayah yang pola kemiskinannya belum pernah dipelajarinya. Bila
    kinerja anjlok pada satu kecamatan, sistem ini belum layak dipakai di
    kabupaten lain tanpa pelatihan ulang - dan itu perlu dinyatakan terus
    terang, bukan disembunyikan di balik angka rata-rata.
    """
    hasil: list[dict[str, Any]] = []
    kecamatan = sorted(dataset.meta["kecamatan"].dropna().unique())
    benih_dasar = benih if benih is not None else settings.random_seed

    for i, kec in enumerate(kecamatan):
        penanda = (dataset.meta["kecamatan"] == kec).to_numpy()
        if penanda.sum() < 500 or (~penanda).sum() < 5000:
            continue

        X_latih = dataset.X.loc[~penanda, list(NAMA_FITUR_OPERASIONAL)]
        y_latih = dataset.y[~penanda]
        X_uji = dataset.X.loc[penanda, list(NAMA_FITUR_OPERASIONAL)]
        y_uji = dataset.y[penanda]
        if y_uji.sum() < 20:
            continue

        param = {**PARAMETER_LGBM, "seed": benih_dasar + i}
        booster = lgb.train(
            param, lgb.Dataset(X_latih, label=y_latih.astype(int)), num_boost_round=putaran
        )
        p = booster.predict(X_uji)
        m = evaluasi_lengkap(y_uji, p)
        hasil.append(
            {
                "kecamatan": kec,
                "jumlah_baris": int(penanda.sum()),
                "prevalensi": round(float(y_uji.mean()), 4),
                "auc": round(m.peringkat.auc, 4),
                "presisi_300": round(m.peringkat.pada_anggaran[300]["presisi"], 4),
            }
        )
    return hasil


__all__ = [
    "PARAMETER_LGBM",
    "ModelKerentanan",
    "PembagianData",
    "bagi_menurut_waktu",
    "latih_model",
    "uji_kecamatan_ditinggalkan",
    "uji_keluarga_terpisah",
]
