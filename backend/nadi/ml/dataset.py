"""Pemuatan dataset pelatihan dari basis data.

Menyatukan kondisi keluarga, guncangan, dan konteks wilayah menjadi satu
matriks fitur beserta labelnya, siap dipakai melatih maupun menilai.

Dua hal dijaga ketat di sini.

**Label berasal dari masa depan, fitur tidak.** Label sebuah baris pada
gelombang ``t`` adalah status kemiskinan keluarga itu pada gelombang ``t+1``.
Seluruh fitur dihitung hanya dari gelombang ``t`` dan sebelumnya. Pemisahan ini
ditegakkan oleh bentuk kodenya: label dibentuk lewat penggeseran eksplisit di
berkas ini, sedangkan fitur dibangun modul lain yang bahkan tidak menerima
tabel label sebagai masukan.

**Konteks wilayah dihitung dari gelombang yang sama, bukan dari seluruh
periode.** Menghitung tingkat kemiskinan pekon dengan menggabungkan seluruh
gelombang akan menyelundupkan keadaan masa depan ke dalam fitur - kekeliruan
yang sulit terlihat namun sanggup melambungkan angka evaluasi tanpa dasar.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np
import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine

from nadi.ml.fitur import NAMA_FITUR
from nadi.ml.pembangun_fitur import bangun_fitur

logger = logging.getLogger("nadi.ml")

#: Kolom kondisi keluarga yang diperlukan pembangun fitur.
_KOLOM_SNAPSHOT = """
    s.id                          AS snapshot_id,
    s.keluarga_id,
    s.gelombang,
    k.wilayah_id,
    s.pengeluaran_per_kapita, s.pendapatan_bulanan, s.desil_kesejahteraan,
    s.peringkat_kesejahteraan, s.status_miskin, s.rasio_garis_kemiskinan,
    s.jumlah_anggota, s.jumlah_balita, s.jumlah_anak_usia_sekolah,
    s.jumlah_lansia, s.jumlah_disabilitas, s.jumlah_bekerja, s.rasio_tanggungan,
    s.kk_umur, s.kk_jenis_kelamin, s.kk_pendidikan, s.kk_status_kegiatan,
    s.kk_lapangan_usaha, s.kk_status_pekerjaan,
    s.status_kepemilikan_rumah, s.keluarga_dalam_rumah, s.luas_lantai_m2,
    s.jenis_lantai_terluas, s.jenis_dinding_terluas, s.jenis_atap_terluas,
    s.sumber_air_minum_utama, s.fasilitas_bab, s.jenis_kloset,
    s.pembuangan_akhir_tinja, s.sumber_penerangan_utama, s.daya_terpasang,
    s.bahan_bakar_utama_memasak,
    s.jumlah_tabung_gas, s.jumlah_lemari_es, s.jumlah_ac, s.jumlah_pemanas_air,
    s.jumlah_telepon_rumah, s.jumlah_tv_datar, s.jumlah_komputer,
    s.jumlah_smartphone, s.jumlah_sepeda, s.jumlah_sepeda_motor, s.jumlah_mobil,
    s.jumlah_perahu, s.jumlah_kapal_perahu_motor, s.gram_emas_perhiasan,
    s.luas_sawah_kebun_ha, s.punya_lahan_lainnya, s.jumlah_rumah_lainnya,
    s.jumlah_ternak_besar, s.jumlah_ternak_kecil,
    s.ada_penyakit_kronis, s.ada_penyakit_biaya_tinggi, s.ada_gizi_bermasalah,
    s.jumlah_ber_jkn, s.jumlah_ibu_hamil, s.jumlah_tanpa_dokumen,
    s.ada_anak_putus_sekolah, s.rata_lama_sekolah_dewasa, s.jumlah_usaha_keluarga,
    s.jumlah_program_diterima, s.nilai_bantuan_bulanan,
    s.kelengkapan_data, s.umur_data_bulan
"""


@dataclass
class DatasetLatih:
    """Matriks fitur, label, dan keterangan penyertanya."""

    X: pd.DataFrame
    """Matriks fitur. Kolomnya persis :data:`nadi.ml.fitur.NAMA_FITUR`."""

    y: np.ndarray
    """Label: benar bila keluarga berada di bawah garis kemiskinan pada
    gelombang berikutnya."""

    meta: pd.DataFrame
    """Keterangan tiap baris - keluarga, gelombang, wilayah, kecamatan, dan
    ciri yang diperlukan untuk memeriksa keadilan model. TIDAK dipakai sebagai
    fitur."""

    @property
    def n(self) -> int:
        return len(self.X)

    def saring_gelombang(self, gelombang: list[int]) -> "DatasetLatih":
        """Ambil bagian dataset untuk gelombang tertentu."""
        penanda = self.meta["gelombang"].isin(gelombang).to_numpy()
        return DatasetLatih(
            X=self.X.loc[penanda].reset_index(drop=True),
            y=self.y[penanda],
            meta=self.meta.loc[penanda].reset_index(drop=True),
        )

    def saring_keluarga(self, id_keluarga: np.ndarray) -> "DatasetLatih":
        """Ambil bagian dataset untuk keluarga tertentu."""
        penanda = self.meta["keluarga_id"].isin(id_keluarga).to_numpy()
        return DatasetLatih(
            X=self.X.loc[penanda].reset_index(drop=True),
            y=self.y[penanda],
            meta=self.meta.loc[penanda].reset_index(drop=True),
        )

    def ringkas(self) -> str:
        gel = sorted(self.meta["gelombang"].unique().tolist())
        return (
            f"{self.n:,} baris, {self.meta['keluarga_id'].nunique():,} keluarga, "
            f"gelombang {gel}, proporsi positif {self.y.mean() * 100:.2f}%"
        ).replace(",", ".")


# ---------------------------------------------------------------------------
def _baca_snapshot(mesin: Engine) -> pd.DataFrame:
    kueri = f"SELECT {_KOLOM_SNAPSHOT} FROM snapshot_keluarga s JOIN keluarga k ON k.id = s.keluarga_id"
    return pd.read_sql(text(kueri), mesin)


def _baca_guncangan(mesin: Engine) -> pd.DataFrame:
    return pd.read_sql(
        text("SELECT keluarga_id, gelombang, jenis, keparahan FROM guncangan"), mesin
    )


def _baca_wilayah(mesin: Engine) -> pd.DataFrame:
    return pd.read_sql(
        text(
            "SELECT id, kode, nama, jenis, induk_id, tingkat, klasifikasi FROM wilayah"
        ),
        mesin,
    )


def _hitung_konteks_wilayah(snapshot: pd.DataFrame) -> pd.DataFrame:
    """Hitung tingkat kemiskinan pekon PER GELOMBANG.

    Penghitungan dilakukan terpisah untuk setiap gelombang, bukan digabung
    seluruh periode. Menggabungkannya akan membuat fitur konteks memuat
    keterangan tentang gelombang yang belum terjadi - kebocoran yang tidak
    kentara namun membuat seluruh angka evaluasi tidak sah.
    """
    rekap = (
        snapshot.groupby(["wilayah_id", "gelombang"])
        .agg(
            jumlah_keluarga=("keluarga_id", "size"),
            persentase_miskin=("status_miskin", "mean"),
        )
        .reset_index()
    )
    rekap["persentase_miskin"] *= 100.0
    return rekap


def muat_dataset(mesin: Engine) -> DatasetLatih:
    """Bangun dataset pelatihan lengkap dari basis data."""
    snapshot = _baca_snapshot(mesin)
    if snapshot.empty:
        raise RuntimeError(
            "Tidak ada data kondisi keluarga. Jalankan backend/scripts/siapkan_data.py lebih dahulu."
        )

    guncangan = _baca_guncangan(mesin)
    wilayah = _baca_wilayah(mesin)
    konteks = _hitung_konteks_wilayah(snapshot)

    logger.info(
        "Memuat dataset: %d kondisi, %d guncangan, %d wilayah.",
        len(snapshot),
        len(guncangan),
        len(wilayah),
    )

    # --- Fitur ---
    X_penuh = bangun_fitur(
        snapshot,
        guncangan=guncangan,
        statistik_wilayah=konteks,
        wilayah=wilayah,
    )

    # --- Label: status kemiskinan pada gelombang BERIKUTNYA ---
    urut = snapshot.sort_values(["keluarga_id", "gelombang"]).reset_index(drop=True)
    urut["label"] = urut.groupby("keluarga_id")["status_miskin"].shift(-1)
    urut["label_tersedia"] = urut["label"].notna()

    kunci = ["keluarga_id", "gelombang"]
    gabung = X_penuh.merge(
        urut[kunci + ["label", "label_tersedia", "wilayah_id", "status_miskin"]],
        on=kunci,
        how="left",
    )

    # Gelombang terakhir tidak memiliki penerus, sehingga tidak dapat dilatih.
    layak = gabung["label_tersedia"].fillna(False).to_numpy().astype(bool)
    gabung = gabung.loc[layak].reset_index(drop=True)

    # --- Keterangan untuk pemeriksaan keadilan ---
    peta_wilayah = wilayah.set_index("id")
    kecamatan_dari_desa = {}
    nama_kecamatan = {}
    for wid, baris in peta_wilayah.iterrows():
        if baris["tingkat"] == 2 and pd.notna(baris["induk_id"]):
            kecamatan_dari_desa[wid] = int(baris["induk_id"])
        elif baris["tingkat"] == 1:
            nama_kecamatan[wid] = baris["nama"]

    meta = pd.DataFrame(
        {
            "keluarga_id": gabung["keluarga_id"].astype(int),
            "gelombang": gabung["gelombang"].astype(int),
            "wilayah_id": gabung["wilayah_id"].astype(int),
            "miskin_saat_ini": gabung["status_miskin"].astype(bool),
        }
    )
    meta["kecamatan_id"] = meta["wilayah_id"].map(kecamatan_dari_desa)
    meta["kecamatan"] = meta["kecamatan_id"].map(nama_kecamatan)
    meta["perdesaan"] = (
        meta["wilayah_id"]
        .map(peta_wilayah["klasifikasi"])
        .fillna("perdesaan")
        .eq("perdesaan")
    )
    meta["kk_perempuan"] = gabung["kk_perempuan"].astype(bool)

    X = gabung[list(NAMA_FITUR)].astype(np.float32).reset_index(drop=True)
    y = gabung["label"].astype(bool).to_numpy()

    hasil = DatasetLatih(X=X, y=y, meta=meta.reset_index(drop=True))
    logger.info("Dataset siap: %s", hasil.ringkas())
    return hasil


def muat_fitur_penilaian(mesin: Engine) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Bangun matriks fitur untuk SELURUH gelombang, termasuk yang terakhir.

    Berbeda dari :func:`muat_dataset` yang membuang gelombang terakhir karena
    tidak memiliki label, fungsi ini justru mempertahankannya - sebab gelombang
    terakhir adalah keadaan terkini, dan justru keluarga di sanalah yang perlu
    dinilai dan ditindaklanjuti hari ini. Melatih memerlukan masa lalu;
    memprioritaskan memerlukan masa kini.

    Returns:
        Pasangan berisi matriks fitur dan keterangan barisnya.
    """
    snapshot = _baca_snapshot(mesin)
    if snapshot.empty:
        raise RuntimeError("Tidak ada data kondisi keluarga.")

    guncangan = _baca_guncangan(mesin)
    wilayah = _baca_wilayah(mesin)
    konteks = _hitung_konteks_wilayah(snapshot)

    X = bangun_fitur(
        snapshot, guncangan=guncangan, statistik_wilayah=konteks, wilayah=wilayah
    )

    kunci = ["keluarga_id", "gelombang"]
    tambahan = snapshot[kunci + ["wilayah_id", "status_miskin", "snapshot_id"]]
    gabung = X.merge(tambahan, on=kunci, how="left")

    peta_wilayah = wilayah.set_index("id")
    kecamatan_dari_desa = {
        int(wid): int(b["induk_id"])
        for wid, b in peta_wilayah.iterrows()
        if b["tingkat"] == 2 and pd.notna(b["induk_id"])
    }
    nama_kecamatan = {
        int(wid): b["nama"] for wid, b in peta_wilayah.iterrows() if b["tingkat"] == 1
    }

    meta = pd.DataFrame(
        {
            "keluarga_id": gabung["keluarga_id"].astype(int),
            "gelombang": gabung["gelombang"].astype(int),
            "wilayah_id": gabung["wilayah_id"].astype(int),
            "snapshot_id": gabung["snapshot_id"].astype(int),
            "miskin_saat_ini": gabung["status_miskin"].astype(bool),
        }
    )
    meta["kecamatan_id"] = meta["wilayah_id"].map(kecamatan_dari_desa)
    meta["kecamatan"] = meta["kecamatan_id"].map(nama_kecamatan)
    meta["perdesaan"] = (
        meta["wilayah_id"].map(peta_wilayah["klasifikasi"]).fillna("perdesaan").eq("perdesaan")
    )
    meta["kk_perempuan"] = gabung["kk_perempuan"].astype(bool)

    return (
        gabung[list(NAMA_FITUR)].astype(np.float32).reset_index(drop=True),
        meta.reset_index(drop=True),
    )


__all__ = ["DatasetLatih", "muat_dataset", "muat_fitur_penilaian"]
