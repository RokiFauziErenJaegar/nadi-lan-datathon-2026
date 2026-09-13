"""Perhitungan matriks fitur dari kondisi keluarga.

Satu-satunya jalan dari data mentah menuju masukan model. Fungsi
:func:`bangun_fitur` dipanggil oleh proses pelatihan maupun oleh titik akhir
penilaian, sehingga tidak ada peluang keduanya menghitung hal yang berbeda.

Dua aturan ditegakkan struktur kode, bukan kedisiplinan penulisnya:

**Tidak menengok ke depan.** Fitur bertingkat waktu hanya dibentuk dengan
``groupby(...).shift(1)``, yang menarik nilai dari gelombang *sebelumnya*.
Tidak ada satu pun pemanggilan ``shift(-1)`` di berkas ini. Label berada di
gelombang berikutnya, dan fungsi ini tidak pernah menyentuhnya.

**Penilaian normatif berada di satu tempat.** Pertanyaan seperti "lantai
seperti apa yang disebut layak" dijawab di :mod:`nadi.db.enums`, lalu diambil
ke sini sebagai himpunan kode. Mengubah pendirian tentang kelayakan cukup
dilakukan sekali, dan seluruh sistem ikut berubah bersamaan.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from nadi.db.enums import (
    BahanBakarMemasak,
    DayaListrik,
    FasilitasBAB,
    JenisAtap,
    JenisDinding,
    JenisGuncangan,
    JenisKelamin,
    JenisKloset,
    JenisLantai,
    LapanganUsaha,
    PembuanganTinja,
    PendidikanTertinggi,
    StatusKegiatan,
    StatusPekerjaan,
    SumberAirMinum,
)
from nadi.ml.fitur import NAMA_FITUR

# ---------------------------------------------------------------------------
# Himpunan kode, diturunkan dari penilaian normatif pada modul enumerasi
# ---------------------------------------------------------------------------
LANTAI_LAYAK = frozenset(j.value for j in JenisLantai if j.layak)
DINDING_LAYAK = frozenset(j.value for j in JenisDinding if j.layak)
ATAP_LAYAK = frozenset(j.value for j in JenisAtap if j.layak)
AIR_LAYAK = frozenset(j.value for j in SumberAirMinum if j.layak)
BAB_LAYAK = frozenset(j.value for j in FasilitasBAB if j.layak)
KLOSET_LAYAK = frozenset(j.value for j in JenisKloset if j.layak)
TINJA_LAYAK = frozenset(j.value for j in PembuanganTinja if j.layak)
BAHAN_BAKAR_LAYAK = frozenset(j.value for j in BahanBakarMemasak if j.layak)
DAYA_RENDAH = frozenset(j.value for j in DayaListrik if j.indikator_ekonomi_rendah)
PEKERJAAN_RENTAN = frozenset(j.value for j in StatusPekerjaan if j.pekerjaan_rentan)
PEKERJAAN_TETAP = frozenset(j.value for j in StatusPekerjaan if j.berpenghasilan_tetap)
SEKTOR_MUSIMAN = frozenset(j.value for j in LapanganUsaha if j.rentan_musiman)
TAHUN_SEKOLAH = {j.value: j.tahun_sekolah for j in PendidikanTertinggi}
GUNCANGAN_PENDAPATAN = frozenset(
    j.value for j in JenisGuncangan if j.sifat == "pendapatan"
)

#: Ambang luas lantai per orang, dalam meter persegi.
LUAS_MINIMUM_PER_KAPITA = 7.2

#: Batas usia lanjut, mengikuti Undang-Undang Nomor 13 Tahun 1998 tentang
#: Kesejahteraan Lanjut Usia.
USIA_LANSIA = 60

# ---------------------------------------------------------------------------
# Bobot indeks aset
# ---------------------------------------------------------------------------
# Indeks aset dihitung sebagai jumlah berbobot, bukan lewat analisis komponen
# utama seperti pada indeks kekayaan gaya DHS. Pilihan ini menukar sedikit
# ketajaman statistik dengan sesuatu yang lebih dibutuhkan di sini: setiap
# bobot dapat ditunjuk, dipertanyakan, dan diubah oleh orang yang memahami
# konteks setempat - tanpa perlu memahami aljabar linear. Ketika seorang
# kepala dinas bertanya "mengapa keluarga ini dinilai lebih mampu", jawabannya
# harus berupa daftar barang, bukan muatan komponen.
#
# Nilai bobot mencerminkan harga perolehan relatif sekaligus daya angkatnya
# sebagai penyangga saat keluarga terdesak.
BOBOT_ASET: dict[str, float] = {
    "jumlah_mobil": 25.0,
    "jumlah_rumah_lainnya": 20.0,
    "jumlah_kapal_perahu_motor": 12.0,
    "jumlah_ac": 8.0,
    "jumlah_pemanas_air": 6.0,
    "jumlah_lemari_es": 5.0,
    "jumlah_ternak_besar": 5.0,
    "jumlah_tv_datar": 4.0,
    "jumlah_komputer": 4.0,
    "jumlah_sepeda_motor": 3.0,
    "jumlah_perahu": 2.0,
    "jumlah_smartphone": 1.5,
    "jumlah_tabung_gas": 1.0,
    "jumlah_ternak_kecil": 1.0,
    "jumlah_sepeda": 0.5,
    "jumlah_telepon_rumah": 0.5,
}

#: Bobot untuk aset berskala kontinu, dihitung per satuannya.
BOBOT_ASET_KONTINU: dict[str, float] = {
    "gram_emas_perhiasan": 0.2,  # per gram
    "luas_sawah_kebun_ha": 15.0,  # per hektar
}

#: Aset yang menghasilkan pemasukan, bukan sekadar menyimpan nilai.
ASET_PRODUKTIF = (
    "luas_sawah_kebun_ha",
    "jumlah_ternak_besar",
    "jumlah_ternak_kecil",
    "jumlah_kapal_perahu_motor",
    "punya_lahan_lainnya",
)


# ---------------------------------------------------------------------------
# Pembantu
# ---------------------------------------------------------------------------
def _kolom(df: pd.DataFrame, nama: str, bawaan: float = 0.0) -> pd.Series:
    """Ambil kolom, atau kembalikan deret berisi nilai bawaan bila tidak ada.

    Membuat fungsi ini tahan terhadap tabel yang belum memuat kolom pengayaan,
    sehingga dapat dipakai pada data yang belum lengkap tanpa menggagalkan
    seluruh perhitungan.
    """
    if nama in df.columns:
        return df[nama]
    return pd.Series(bawaan, index=df.index, name=nama)


def _bool(deret: pd.Series) -> pd.Series:
    """Ubah deret menjadi boolean, dengan nilai kosong dianggap salah.

    ``where`` dipakai alih-alih ``fillna`` karena ``fillna`` pada deret
    bertipe objek memicu peringatan penurunan tipe pada pandas versi baru,
    dan perilakunya dijadwalkan berubah.
    """
    return deret.where(deret.notna(), False).astype(bool)


def _num(deret: pd.Series) -> pd.Series:
    return pd.to_numeric(deret, errors="coerce").fillna(0.0)


# ---------------------------------------------------------------------------
# Agregat guncangan
# ---------------------------------------------------------------------------
def ringkas_guncangan(guncangan: pd.DataFrame) -> pd.DataFrame:
    """Ringkas kejadian guncangan menjadi satu baris per keluarga per gelombang."""
    if guncangan is None or guncangan.empty:
        return pd.DataFrame(
            columns=[
                "keluarga_id",
                "gelombang",
                "jumlah_guncangan_terkini",
                "ada_guncangan_pendapatan",
                "bobot_guncangan",
            ]
        )

    g = guncangan.copy()
    g["_pendapatan"] = g["jenis"].isin(GUNCANGAN_PENDAPATAN)
    g["_bencana"] = g["jenis"] == JenisGuncangan.BENCANA_ALAM.value
    # Keparahan berbobot kuadratik: guncangan berat jauh lebih menentukan
    # daripada tiga guncangan ringan yang terjadi bersamaan.
    g["_bobot"] = _num(g["keparahan"]) ** 2

    hasil = (
        g.groupby(["keluarga_id", "gelombang"])
        .agg(
            jumlah_guncangan_terkini=("jenis", "size"),
            ada_guncangan_pendapatan=("_pendapatan", "max"),
            ada_guncangan_bencana=("_bencana", "max"),
            bobot_guncangan=("_bobot", "sum"),
        )
        .reset_index()
    )
    hasil["ada_guncangan_pendapatan"] = hasil["ada_guncangan_pendapatan"].astype(bool)
    hasil["ada_guncangan_bencana"] = hasil["ada_guncangan_bencana"].astype(bool)
    return hasil


# ---------------------------------------------------------------------------
# Pembangun utama
# ---------------------------------------------------------------------------
def bangun_fitur(
    snapshot: pd.DataFrame,
    *,
    guncangan: pd.DataFrame | None = None,
    statistik_wilayah: pd.DataFrame | None = None,
    wilayah: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Bentuk matriks fitur dari tabel kondisi keluarga.

    Args:
        snapshot: satu baris per keluarga per gelombang, memakai nama kolom
            seperti pada :class:`nadi.db.models.keluarga.SnapshotKeluarga`.
        guncangan: kejadian guncangan, opsional.
        statistik_wilayah: rekap per wilayah per gelombang, opsional. Dipakai
            membentuk fitur konteks lingkungan.
        wilayah: daftar wilayah beserta klasifikasi desa atau kota, opsional.

    Returns:
        DataFrame berisi kolom ``keluarga_id``, ``gelombang``, dan seluruh nama
        pada :data:`nadi.ml.fitur.NAMA_FITUR`, dengan urutan kolom yang tetap.
    """
    if snapshot.empty:
        return pd.DataFrame(columns=["keluarga_id", "gelombang", *NAMA_FITUR])

    df = snapshot.sort_values(["keluarga_id", "gelombang"]).reset_index(drop=True)
    F = pd.DataFrame(index=df.index)
    F["keluarga_id"] = df["keluarga_id"]
    F["gelombang"] = df["gelombang"]

    # ------------------------------------------------------------------
    # Ekonomi
    # ------------------------------------------------------------------
    pengeluaran = _num(_kolom(df, "pengeluaran_per_kapita")).clip(lower=1.0)
    F["rasio_garis_kemiskinan"] = _num(_kolom(df, "rasio_garis_kemiskinan", 1.0))
    F["log_pengeluaran_per_kapita"] = np.log1p(pengeluaran)
    F["desil_kesejahteraan"] = _num(_kolom(df, "desil_kesejahteraan", 5))

    indeks_aset = pd.Series(0.0, index=df.index)
    for kolom, bobot in BOBOT_ASET.items():
        indeks_aset = indeks_aset + _num(_kolom(df, kolom)) * bobot
    for kolom, bobot in BOBOT_ASET_KONTINU.items():
        indeks_aset = indeks_aset + _num(_kolom(df, kolom)) * bobot
    indeks_aset = indeks_aset + _bool(_kolom(df, "punya_lahan_lainnya", False)).astype(float) * 5.0
    # Skala logaritmik: selisih antara tidak punya apa-apa dan punya satu sepeda
    # motor jauh lebih berarti daripada selisih antara dua dan tiga mobil.
    F["indeks_aset"] = np.log1p(indeks_aset)

    produktif = pd.Series(False, index=df.index)
    for kolom in ASET_PRODUKTIF:
        nilai = _kolom(df, kolom, 0)
        produktif = produktif | (
            _bool(nilai) if nilai.dtype == bool else (_num(nilai) > 0)
        )
    F["punya_aset_produktif"] = produktif

    # ------------------------------------------------------------------
    # Pekerjaan dan tanggungan
    # ------------------------------------------------------------------
    jumlah_bekerja = _num(_kolom(df, "jumlah_bekerja"))
    F["rasio_tanggungan"] = _num(_kolom(df, "rasio_tanggungan")).clip(upper=12.0)
    F["tidak_ada_yang_bekerja"] = jumlah_bekerja <= 0
    F["kk_pekerjaan_rentan"] = _kolom(df, "kk_status_pekerjaan", 0).isin(PEKERJAAN_RENTAN)
    F["kk_sektor_musiman"] = _kolom(df, "kk_lapangan_usaha", 0).isin(SEKTOR_MUSIMAN)
    F["kk_berpenghasilan_tetap"] = _kolom(df, "kk_status_pekerjaan", 0).isin(PEKERJAAN_TETAP)
    F["jumlah_usaha_keluarga"] = _num(_kolom(df, "jumlah_usaha_keluarga"))

    # ------------------------------------------------------------------
    # Pendidikan
    # ------------------------------------------------------------------
    F["kk_tahun_sekolah"] = (
        _kolom(df, "kk_pendidikan", 1).map(TAHUN_SEKOLAH).fillna(0.0).astype(float)
    )
    F["rata_lama_sekolah_dewasa"] = _num(_kolom(df, "rata_lama_sekolah_dewasa"))
    F["ada_anak_putus_sekolah"] = _bool(_kolom(df, "ada_anak_putus_sekolah", False))
    F["beban_anak_sekolah"] = _num(_kolom(df, "jumlah_anak_usia_sekolah"))

    # ------------------------------------------------------------------
    # Kesehatan
    # ------------------------------------------------------------------
    jumlah_anggota = _num(_kolom(df, "jumlah_anggota", 1)).clip(lower=1)
    F["ada_penyakit_biaya_tinggi"] = _bool(_kolom(df, "ada_penyakit_biaya_tinggi", False))
    F["ada_penyakit_kronis"] = _bool(_kolom(df, "ada_penyakit_kronis", False))
    cakupan = (_num(_kolom(df, "jumlah_ber_jkn")) / jumlah_anggota).clip(0.0, 1.0)
    F["cakupan_jkn"] = cakupan
    F["tanpa_jkn_sama_sekali"] = _num(_kolom(df, "jumlah_ber_jkn")) <= 0
    F["ada_gizi_bermasalah"] = _bool(_kolom(df, "ada_gizi_bermasalah", False))
    F["jumlah_disabilitas"] = _num(_kolom(df, "jumlah_disabilitas"))
    F["ada_ibu_hamil"] = _num(_kolom(df, "jumlah_ibu_hamil")) > 0

    # ------------------------------------------------------------------
    # Administrasi kependudukan
    # ------------------------------------------------------------------
    F["ada_masalah_dokumen"] = _num(_kolom(df, "jumlah_tanpa_dokumen")) > 0

    # ------------------------------------------------------------------
    # Hunian, air, dan sanitasi
    # ------------------------------------------------------------------
    luas_per_kapita = _num(_kolom(df, "luas_lantai_m2", 36.0)) / jumlah_anggota
    F["luas_lantai_per_kapita"] = luas_per_kapita
    F["hunian_padat"] = luas_per_kapita < LUAS_MINIMUM_PER_KAPITA

    lantai_layak = _kolom(df, "jenis_lantai_terluas", 0).isin(LANTAI_LAYAK)
    dinding_layak = _kolom(df, "jenis_dinding_terluas", 0).isin(DINDING_LAYAK)
    atap_layak = _kolom(df, "jenis_atap_terluas", 0).isin(ATAP_LAYAK)
    ketahanan_layak = lantai_layak & dinding_layak & atap_layak
    F["ketahanan_bangunan_tidak_layak"] = ~ketahanan_layak
    F["berbagi_rumah"] = _num(_kolom(df, "keluarga_dalam_rumah", 1)) > 1

    sanitasi_layak = (
        _kolom(df, "fasilitas_bab", 0).isin(BAB_LAYAK)
        & _kolom(df, "jenis_kloset", 0).isin(KLOSET_LAYAK)
        & _kolom(df, "pembuangan_akhir_tinja", 0).isin(TINJA_LAYAK)
    )
    air_layak = _kolom(df, "sumber_air_minum_utama", 0).isin(AIR_LAYAK)
    F["sanitasi_tidak_layak"] = ~sanitasi_layak
    F["air_minum_tidak_layak"] = ~air_layak
    F["listrik_daya_rendah"] = _kolom(df, "daya_terpasang", 0).isin(DAYA_RENDAH)
    F["memasak_bahan_bakar_tidak_layak"] = ~_kolom(df, "bahan_bakar_utama_memasak", 0).isin(
        BAHAN_BAKAR_LAYAK
    )

    # Empat kriteria resmi rumah layak huni, dihitung berapa yang tidak terpenuhi.
    F["jumlah_kriteria_rtlh"] = (
        (luas_per_kapita < LUAS_MINIMUM_PER_KAPITA).astype(int)
        + (~air_layak).astype(int)
        + (~sanitasi_layak).astype(int)
        + (~ketahanan_layak).astype(int)
    )

    # ------------------------------------------------------------------
    # Demografi
    # ------------------------------------------------------------------
    F["jumlah_anggota"] = jumlah_anggota
    F["kk_perempuan"] = _kolom(df, "kk_jenis_kelamin", 1) == JenisKelamin.PEREMPUAN.value
    F["kk_lansia"] = _num(_kolom(df, "kk_umur")) >= USIA_LANSIA
    F["jumlah_balita"] = _num(_kolom(df, "jumlah_balita"))
    F["jumlah_lansia"] = _num(_kolom(df, "jumlah_lansia"))

    # ------------------------------------------------------------------
    # Perlindungan sosial
    # ------------------------------------------------------------------
    jumlah_program = _num(_kolom(df, "jumlah_program_diterima"))
    F["jumlah_program_diterima"] = jumlah_program
    F["nilai_bantuan_per_kapita"] = _num(_kolom(df, "nilai_bantuan_bulanan")) / jumlah_anggota
    F["tanpa_bantuan_apa_pun"] = jumlah_program <= 0

    # ------------------------------------------------------------------
    # Guncangan
    # ------------------------------------------------------------------
    ringkasan = ringkas_guncangan(guncangan) if guncangan is not None else ringkas_guncangan(None)
    if not ringkasan.empty:
        gabung = df[["keluarga_id", "gelombang"]].merge(
            ringkasan, on=["keluarga_id", "gelombang"], how="left"
        )
        F["jumlah_guncangan_terkini"] = _num(gabung["jumlah_guncangan_terkini"]).values
        F["ada_guncangan_pendapatan"] = _bool(gabung["ada_guncangan_pendapatan"]).values
        F["ada_guncangan_bencana"] = _bool(gabung["ada_guncangan_bencana"]).values
        F["bobot_guncangan"] = _num(gabung["bobot_guncangan"]).values
    else:
        F["jumlah_guncangan_terkini"] = 0.0
        F["ada_guncangan_pendapatan"] = False
        F["ada_guncangan_bencana"] = False
        F["bobot_guncangan"] = 0.0

    # ------------------------------------------------------------------
    # Dinamika antar-gelombang
    # ------------------------------------------------------------------
    # Hanya ``shift(1)`` yang dipakai - menarik nilai dari gelombang sebelumnya.
    # Tidak ada ``shift(-1)`` di seluruh berkas ini.
    #
    # Kolom penggeser disalin ke bingkai terpisah lebih dulu agar perhitungan
    # tetap berjalan pada tabel yang belum memuat seluruh kolom, alih-alih
    # gagal dengan galat kunci yang tidak menjelaskan apa pun.
    riwayat = pd.DataFrame(
        {
            "keluarga_id": df["keluarga_id"],
            "rasio_garis_kemiskinan": _num(_kolom(df, "rasio_garis_kemiskinan", 1.0)),
            "pengeluaran_per_kapita": pengeluaran,
            "status_miskin": _bool(_kolom(df, "status_miskin", False)),
        }
    )
    kelompok = riwayat.groupby("keluarga_id")
    rasio_lalu = kelompok["rasio_garis_kemiskinan"].shift(1)
    pengeluaran_lalu = kelompok["pengeluaran_per_kapita"].shift(1)
    miskin_lalu = kelompok["status_miskin"].shift(1)

    F["delta_rasio_kemiskinan"] = (
        _num(_kolom(df, "rasio_garis_kemiskinan", 1.0)) - rasio_lalu
    ).fillna(0.0)
    # Gelombang pertama tidak memiliki pembanding; nilai kosong menjadi nol
    # sehingga perbandingan menghasilkan salah, bukan nilai kosong.
    F["tren_menurun"] = pengeluaran < _num(pengeluaran_lalu)
    F["pernah_miskin_sebelumnya"] = _bool(miskin_lalu)

    # ------------------------------------------------------------------
    # Konteks wilayah
    # ------------------------------------------------------------------
    F["persen_miskin_wilayah"] = 0.0
    F["wilayah_perdesaan"] = True

    if statistik_wilayah is not None and not statistik_wilayah.empty and "wilayah_id" in df.columns:
        stat = statistik_wilayah[["wilayah_id", "gelombang", "persentase_miskin"]].copy()
        gabung = df[["wilayah_id", "gelombang"]].merge(
            stat, on=["wilayah_id", "gelombang"], how="left"
        )
        F["persen_miskin_wilayah"] = _num(gabung["persentase_miskin"]).values

    if wilayah is not None and not wilayah.empty and "wilayah_id" in df.columns:
        w = wilayah.rename(columns={"id": "wilayah_id"})[["wilayah_id", "klasifikasi"]]
        gabung = df[["wilayah_id"]].merge(w, on="wilayah_id", how="left")
        F["wilayah_perdesaan"] = (
            gabung["klasifikasi"].fillna("perdesaan").eq("perdesaan").values
        )

    # ------------------------------------------------------------------
    # Kualitas data
    # ------------------------------------------------------------------
    F["umur_data_bulan"] = _num(_kolom(df, "umur_data_bulan"))
    F["kelengkapan_data"] = _num(_kolom(df, "kelengkapan_data", 1.0))

    # ------------------------------------------------------------------
    # Penyelarasan akhir
    # ------------------------------------------------------------------
    hilang = [n for n in NAMA_FITUR if n not in F.columns]
    if hilang:
        raise RuntimeError(
            "Fitur berikut terdaftar pada DAFTAR_FITUR namun tidak dihitung: "
            + ", ".join(hilang)
            + ". Daftar fitur dan pembangunnya harus selalu selaras."
        )

    hasil = F[["keluarga_id", "gelombang", *NAMA_FITUR]].copy()
    for nama in NAMA_FITUR:
        if hasil[nama].dtype == bool:
            hasil[nama] = hasil[nama].astype(np.int8)
        else:
            hasil[nama] = pd.to_numeric(hasil[nama], errors="coerce").astype(np.float32)
    return hasil


def periksa_keselarasan_fitur() -> list[str]:
    """Kembalikan daftar fitur yang terdaftar namun belum dihitung.

    Dipakai oleh pengujian sebagai jaring pengaman: menambahkan entri baru pada
    ``DAFTAR_FITUR`` tanpa menuliskan perhitungannya adalah kekeliruan yang
    mudah terjadi dan akan menghasilkan kolom berisi nol tanpa peringatan.
    """
    contoh = pd.DataFrame(
        {
            "keluarga_id": [1, 1],
            "gelombang": [0, 1],
            "pengeluaran_per_kapita": [400000.0, 380000.0],
            "rasio_garis_kemiskinan": [0.9, 0.85],
            "status_miskin": [True, True],
            "jumlah_anggota": [4, 4],
        }
    )
    try:
        bangun_fitur(contoh)
    except RuntimeError as exc:
        return str(exc).split(": ", 1)[-1].split(". ")[0].split(", ")
    return []


__all__ = [
    "ASET_PRODUKTIF",
    "BOBOT_ASET",
    "BOBOT_ASET_KONTINU",
    "LUAS_MINIMUM_PER_KAPITA",
    "USIA_LANSIA",
    "bangun_fitur",
    "periksa_keselarasan_fitur",
    "ringkas_guncangan",
]
