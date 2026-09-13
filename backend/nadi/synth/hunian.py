"""Pembangkitan kondisi hunian dan kepemilikan aset.

Seluruh variabel di sini dibangkitkan **dari** kemampuan ekonomi keluarga,
bukan sebaliknya. Rumah dan aset adalah penanda kesejahteraan, bukan
penyebabnya - dan seluruh penargetan berbasis proksi di Indonesia berdiri di
atas anggapan itu. Membalik arahnya akan menghasilkan data yang terlalu mudah
ditebak model.

Caranya memakai gagasan kopula Gaussian, meski dituliskan sederhana. Untuk
setiap variabel dibentuk peubah laten yang berkorelasi dengan kekayaan pada
kekuatan tertentu, lalu peringkat peubah laten itu dipetakan ke kategori
mengikuti sebaran sasaran. Hasilnya memenuhi dua syarat sekaligus:

* sebaran tiap variabel **persis** sesuai sasaran yang ditetapkan, sehingga
  dapat dibandingkan dengan publikasi statistik resmi;
* hubungan antar-variabel tetap terjaga, sehingga keluarga berlantai tanah
  cenderung pula tidak berjamban - persis seperti kenyataannya.

Kekuatan korelasi sengaja tidak dibuat terlalu tinggi. Di lapangan selalu ada
keluarga berumah bagus yang jatuh miskin, dan keluarga berpenghasilan lumayan
yang rumahnya belum diperbaiki. Justru keluarga semacam inilah yang paling
sering salah sasaran, dan sistem ini perlu berlatih menghadapinya.
"""

from __future__ import annotations

import numpy as np

from nadi.db.enums import (
    BahanBakarMemasak,
    DayaListrik,
    FasilitasBAB,
    JenisAtap,
    JenisDinding,
    JenisKloset,
    JenisLantai,
    PembuanganTinja,
    StatusKepemilikanRumah,
    SumberAirMinum,
    SumberPenerangan,
)

# ===========================================================================
# Sebaran sasaran
# ===========================================================================
# Setiap butir berisi (daftar kode dari TERBURUK ke TERBAIK, proporsi sasaran).
# Proporsi mengacu pada keluarga desil 1 sampai 5 di kabupaten bercorak
# perdesaan, sehingga lebih rendah daripada rata-rata nasional.

SEBARAN_LANTAI = (
    [
        JenisLantai.TANAH.value,
        JenisLantai.BAMBU.value,
        JenisLantai.KAYU_KUALITAS_RENDAH.value,
        JenisLantai.LAINNYA.value,
        JenisLantai.SEMEN_BATA_MERAH.value,
        JenisLantai.KAYU_KUALITAS_TINGGI.value,
        JenisLantai.UBIN_TEGEL_TERASO.value,
        JenisLantai.KERAMIK.value,
        JenisLantai.PARKET_VINIL.value,
        JenisLantai.MARMER_GRANIT.value,
    ],
    [0.090, 0.010, 0.040, 0.005, 0.445, 0.020, 0.080, 0.300, 0.005, 0.005],
)

SEBARAN_DINDING = (
    [
        JenisDinding.BAMBU.value,
        JenisDinding.ANYAMAN_BAMBU.value,
        JenisDinding.BATANG_KAYU.value,
        JenisDinding.LAINNYA.value,
        JenisDinding.KAYU_PAPAN.value,
        JenisDinding.PLESTERAN_ANYAMAN.value,
        JenisDinding.TEMBOK.value,
    ],
    [0.015, 0.050, 0.010, 0.005, 0.160, 0.040, 0.720],
)

SEBARAN_ATAP = (
    [
        JenisAtap.IJUK_RUMBIA.value,
        JenisAtap.LAINNYA.value,
        JenisAtap.SIRAP.value,
        JenisAtap.ASBES.value,
        JenisAtap.SENG.value,
        JenisAtap.GENTENG.value,
        JenisAtap.BETON.value,
    ],
    [0.010, 0.005, 0.005, 0.110, 0.300, 0.550, 0.020],
)

SEBARAN_AIR = (
    [
        SumberAirMinum.AIR_SUNGAI.value,
        SumberAirMinum.MATA_AIR_TAK_TERLINDUNG.value,
        SumberAirMinum.SUMUR_TAK_TERLINDUNG.value,
        SumberAirMinum.AIR_HUJAN.value,
        SumberAirMinum.LAINNYA.value,
        SumberAirMinum.MATA_AIR_TERLINDUNG.value,
        SumberAirMinum.SUMUR_TERLINDUNG.value,
        SumberAirMinum.SUMUR_BOR_POMPA.value,
        SumberAirMinum.LEDING_ECERAN.value,
        SumberAirMinum.LEDING_METERAN.value,
        SumberAirMinum.AIR_ISI_ULANG.value,
        SumberAirMinum.AIR_KEMASAN.value,
    ],
    [0.020, 0.030, 0.110, 0.005, 0.005, 0.040, 0.300, 0.300, 0.020, 0.060, 0.090, 0.020],
)

SEBARAN_BAB = (
    [
        FasilitasBAB.TIDAK_ADA.value,
        FasilitasBAB.UMUM.value,
        FasilitasBAB.BERSAMA.value,
        FasilitasBAB.SENDIRI.value,
    ],
    [0.070, 0.050, 0.100, 0.780],
)

SEBARAN_KLOSET = (
    [
        JenisKloset.TIDAK_PAKAI.value,
        JenisKloset.CEMPLUNG_CUBLUK.value,
        JenisKloset.PLENGSENGAN.value,
        JenisKloset.LEHER_ANGSA.value,
    ],
    [0.070, 0.050, 0.060, 0.820],
)

SEBARAN_TINJA = (
    [
        PembuanganTinja.PANTAI_TANAH_LAPANG.value,
        PembuanganTinja.KOLAM_SAWAH_SUNGAI.value,
        PembuanganTinja.LUBANG_TANAH.value,
        PembuanganTinja.LAINNYA.value,
        PembuanganTinja.TANGKI_SEPTIK.value,
        PembuanganTinja.IPAL.value,
    ],
    [0.060, 0.090, 0.140, 0.010, 0.680, 0.020],
)

SEBARAN_PENERANGAN = (
    [
        SumberPenerangan.BUKAN_LISTRIK.value,
        SumberPenerangan.LISTRIK_NON_PLN.value,
        SumberPenerangan.LISTRIK_PLN_TANPA_METERAN.value,
        SumberPenerangan.LISTRIK_PLN_METERAN.value,
    ],
    [0.010, 0.020, 0.070, 0.900],
)

SEBARAN_DAYA = (
    [
        DayaListrik.TANPA_LISTRIK.value,
        DayaListrik.VA_450.value,
        DayaListrik.VA_900.value,
        DayaListrik.VA_1300.value,
        DayaListrik.VA_2200.value,
        DayaListrik.VA_LEBIH_2200.value,
    ],
    [0.010, 0.440, 0.400, 0.110, 0.030, 0.010],
)

SEBARAN_BAHAN_BAKAR = (
    [
        BahanBakarMemasak.KAYU_BAKAR.value,
        BahanBakarMemasak.ARANG.value,
        BahanBakarMemasak.BRIKET.value,
        BahanBakarMemasak.MINYAK_TANAH.value,
        BahanBakarMemasak.TIDAK_MEMASAK.value,
        BahanBakarMemasak.BIOGAS.value,
        BahanBakarMemasak.GAS_3KG.value,
        BahanBakarMemasak.GAS_KOTA.value,
        BahanBakarMemasak.GAS_LEBIH_3KG.value,
        BahanBakarMemasak.LISTRIK.value,
    ],
    [0.240, 0.010, 0.005, 0.010, 0.010, 0.005, 0.700, 0.005, 0.010, 0.005],
)

SEBARAN_KEPEMILIKAN_RUMAH = (
    [
        StatusKepemilikanRumah.LAINNYA.value,
        StatusKepemilikanRumah.KONTRAK_SEWA.value,
        StatusKepemilikanRumah.BEBAS_SEWA.value,
        StatusKepemilikanRumah.RUMAH_DINAS.value,
        StatusKepemilikanRumah.MILIK_SENDIRI.value,
    ],
    [0.005, 0.060, 0.080, 0.005, 0.850],
)

#: Kekuatan hubungan tiap variabel dengan kekayaan keluarga.
#: Nilai lebih tinggi berarti variabel itu lebih setia menandakan kesejahteraan.
KORELASI = {
    "lantai": 0.62,
    "dinding": 0.55,
    "atap": 0.45,
    "air": 0.42,
    "bab": 0.50,
    "kloset": 0.52,
    "tinja": 0.48,
    "penerangan": 0.38,
    "daya": 0.66,  # daya listrik adalah penanda paling setia dan paling sulit dipalsukan
    "bahan_bakar": 0.58,
    "kepemilikan_rumah": 0.22,  # hampir semua memiliki rumah sendiri, daya bedanya kecil
    "luas": 0.45,
}


# ===========================================================================
# Pembantu
# ===========================================================================
def _laten(w_baku: np.ndarray, rho: float, rng: np.random.Generator) -> np.ndarray:
    """Bentuk peubah laten yang berkorelasi ``rho`` dengan kekayaan baku."""
    n = len(w_baku)
    return rho * w_baku + np.sqrt(max(0.0, 1.0 - rho**2)) * rng.standard_normal(n)


def _ke_kategori(laten: np.ndarray, sebaran: tuple[list[int], list[float]]) -> np.ndarray:
    """Petakan peringkat peubah laten ke kategori mengikuti sebaran sasaran.

    Pemetaan berbasis peringkat menjamin sebaran hasil **persis** sama dengan
    sasaran, berapa pun bentuk peubah latennya. Ini yang membuat data sintetis
    dapat diperbandingkan langsung dengan angka publikasi resmi.
    """
    kode, proporsi = sebaran
    p = np.asarray(proporsi, dtype=float)
    p = p / p.sum()
    batas = np.cumsum(p)

    n = len(laten)
    # Peringkat dinormalkan ke selang nol sampai satu.
    peringkat = laten.argsort().argsort() / max(1, n - 1)
    indeks = np.searchsorted(batas, peringkat * 0.999999, side="right")
    indeks = np.clip(indeks, 0, len(kode) - 1)
    return np.asarray(kode, dtype=np.int16)[indeks]


def _milik(
    w_baku: np.ndarray, proporsi_target: float, rho: float, rng: np.random.Generator
) -> np.ndarray:
    """Kepemilikan ya atau tidak, dengan proporsi yang persis sesuai sasaran.

    Pendekatan berbasis peringkat dipakai, bukan peluang logistik. Alasannya
    ditemukan lewat kekeliruan: menyusun peluang sebagai ``sigmoid(a + b*w)``
    lalu mengambil contoh darinya menghasilkan proporsi jauh di atas sasaran,
    sebab fungsi logistik bersifat cembung sehingga nilai rata-ratanya melampaui
    nilai pada titik rata-rata. Kepemilikan mobil yang disetel 2,5 persen
    keluar menjadi 9,1 persen - selisih yang cukup untuk membuat angka aset
    tidak dapat dipertanggungjawabkan.

    Cara di sini menjamin proporsi tepat sasaran sekaligus mempertahankan
    hubungannya dengan kekayaan.
    """
    laten = _laten(w_baku, rho, rng)
    ambang = np.quantile(laten, 1.0 - proporsi_target)
    return (laten >= ambang).astype(np.int16)


def _cacah(
    w_baku: np.ndarray, rerata_target: float, kepekaan: float, rng: np.random.Generator
) -> np.ndarray:
    """Jumlah unit yang dimiliki, dengan rata-rata persis sesuai sasaran.

    Laju Poisson disetel ``exp(b*w - b^2/2)`` sehingga nilai harapannya tepat
    sama dengan sasaran, sebab bagi peubah normal baku berlaku
    ``E[exp(b*w)] = exp(b^2/2)``. Tanpa pengurangan itu, rata-rata hasil selalu
    melampaui sasaran seiring membesarnya kepekaan.
    """
    laju = rerata_target * np.exp(kepekaan * w_baku - 0.5 * kepekaan**2)
    return rng.poisson(np.clip(laju, 0.0, 50.0)).astype(np.int16)


# ===========================================================================
# Pembangkit utama
# ===========================================================================
def bangkitkan_hunian_dan_aset(
    kemampuan: np.ndarray,
    lapangan_usaha: np.ndarray,
    jumlah_anggota: np.ndarray,
    rng: np.random.Generator,
    *,
    sd_derau_kekayaan: float = 0.45,
) -> dict[str, np.ndarray]:
    """Bangkitkan kondisi hunian dan kepemilikan aset pada gelombang awal.

    Args:
        kemampuan: logaritma kemampuan ekonomi permanen tiap keluarga.
        lapangan_usaha: kode sektor pekerjaan kepala keluarga. Menentukan
            kepemilikan lahan dan ternak, yang tidak semata bergantung
            kekayaan - petani miskin dapat memiliki lahan sempit, sedangkan
            pedagang berpenghasilan lebih baik boleh jadi tidak memiliki lahan
            sama sekali.
        jumlah_anggota: banyaknya anggota, menentukan luas lantai yang wajar.
        rng: pembangkit bilangan acak.
        sd_derau_kekayaan: seberapa longgar hubungan antara kekayaan yang
            tampak dari harta dan kemampuan ekonomi sesungguhnya. Nilai nol
            berarti keduanya menyatu sempurna - keadaan yang tidak pernah
            ditemui di lapangan, dan yang akan membuat model terlalu mudah
            menebak.
    """
    n = len(kemampuan)

    # Kekayaan tampak: kemampuan permanen ditambah derau. Derau inilah yang
    # melahirkan keluarga berumah layak namun berpenghasilan rendah, dan
    # sebaliknya - dua jenis keluarga yang paling sering salah sasaran.
    kekayaan = kemampuan + rng.normal(0.0, sd_derau_kekayaan, n)
    w = (kekayaan - kekayaan.mean()) / max(1e-9, kekayaan.std())

    hasil: dict[str, np.ndarray] = {}

    # -----------------------------------------------------------------
    # Hunian
    # -----------------------------------------------------------------
    hasil["jenis_lantai_terluas"] = _ke_kategori(_laten(w, KORELASI["lantai"], rng), SEBARAN_LANTAI)
    hasil["jenis_dinding_terluas"] = _ke_kategori(
        _laten(w, KORELASI["dinding"], rng), SEBARAN_DINDING
    )
    hasil["jenis_atap_terluas"] = _ke_kategori(_laten(w, KORELASI["atap"], rng), SEBARAN_ATAP)
    hasil["status_kepemilikan_rumah"] = _ke_kategori(
        _laten(w, KORELASI["kepemilikan_rumah"], rng), SEBARAN_KEPEMILIKAN_RUMAH
    )

    # Luas lantai bertambah menurut kekayaan dan jumlah anggota, namun tidak
    # sebanding - rumah keluarga besar yang miskin justru menjadi sesak.
    laten_luas = _laten(w, KORELASI["luas"], rng)
    log_luas = (
        np.log(38.0)
        + 0.26 * laten_luas
        + 0.085 * (jumlah_anggota - 3)
        + rng.normal(0.0, 0.16, n)
    )
    hasil["luas_lantai_m2"] = np.clip(np.exp(log_luas), 8.0, 400.0)

    # Sebagian kecil rumah dihuni lebih dari satu keluarga. Peluangnya lebih
    # besar pada keluarga kurang mampu, dan menjadi bentuk kepadatan hunian
    # yang tidak terbaca dari angka luas lantai.
    peluang_berbagi = 1.0 / (1.0 + np.exp(-(np.log(0.09 / 0.91) - 0.55 * w)))
    hasil["keluarga_dalam_rumah"] = np.where(
        rng.random(n) < peluang_berbagi, rng.choice([2, 3], size=n, p=[0.86, 0.14]), 1
    ).astype(np.int16)

    # -----------------------------------------------------------------
    # Air, sanitasi, dan energi
    # -----------------------------------------------------------------
    hasil["sumber_air_minum_utama"] = _ke_kategori(_laten(w, KORELASI["air"], rng), SEBARAN_AIR)

    # Ketiga variabel sanitasi dibangkitkan dari satu peubah laten bersama,
    # ditambah sedikit derau masing-masing. Di lapangan ketiganya memang
    # bergerak bersama: keluarga yang tidak berjamban tentu tidak memiliki
    # tangki septik. Membangkitkannya sendiri-sendiri akan menghasilkan
    # gabungan yang mustahil.
    laten_sanitasi = _laten(w, KORELASI["bab"], rng)
    hasil["fasilitas_bab"] = _ke_kategori(
        laten_sanitasi + rng.normal(0, 0.30, n), SEBARAN_BAB
    )
    hasil["jenis_kloset"] = _ke_kategori(
        laten_sanitasi + rng.normal(0, 0.30, n), SEBARAN_KLOSET
    )
    hasil["pembuangan_akhir_tinja"] = _ke_kategori(
        laten_sanitasi + rng.normal(0, 0.35, n), SEBARAN_TINJA
    )

    laten_listrik = _laten(w, KORELASI["daya"], rng)
    hasil["sumber_penerangan_utama"] = _ke_kategori(
        laten_listrik + rng.normal(0, 0.40, n), SEBARAN_PENERANGAN
    )
    hasil["daya_terpasang"] = _ke_kategori(laten_listrik, SEBARAN_DAYA)
    hasil["bahan_bakar_utama_memasak"] = _ke_kategori(
        _laten(w, KORELASI["bahan_bakar"], rng), SEBARAN_BAHAN_BAKAR
    )

    # -----------------------------------------------------------------
    # Aset
    # -----------------------------------------------------------------
    # Kepemilikan ya atau tidak. Angka kedua adalah proporsi sasaran, angka
    # ketiga adalah kekuatan hubungannya dengan kekayaan - barang mewah lebih
    # setia menandakan kemampuan ekonomi dibanding barang yang hampir merata.
    hasil["jumlah_tabung_gas"] = _milik(w, 0.080, 0.50, rng)
    hasil["jumlah_lemari_es"] = _milik(w, 0.330, 0.58, rng)
    hasil["jumlah_ac"] = _milik(w, 0.015, 0.70, rng)
    hasil["jumlah_pemanas_air"] = _milik(w, 0.010, 0.70, rng)
    hasil["jumlah_telepon_rumah"] = _milik(w, 0.008, 0.40, rng)
    hasil["jumlah_tv_datar"] = _milik(w, 0.240, 0.55, rng)
    hasil["jumlah_komputer"] = _milik(w, 0.090, 0.62, rng)
    hasil["jumlah_mobil"] = _milik(w, 0.025, 0.74, rng)
    hasil["jumlah_perahu"] = _milik(w, 0.004, 0.15, rng)
    hasil["jumlah_kapal_perahu_motor"] = _milik(w, 0.003, 0.30, rng)
    hasil["jumlah_rumah_lainnya"] = _milik(w, 0.025, 0.66, rng)
    hasil["punya_lahan_lainnya"] = _milik(w, 0.090, 0.52, rng).astype(bool)

    hasil["jumlah_sepeda"] = _cacah(w, 0.36, 0.22, rng)
    hasil["jumlah_sepeda_motor"] = np.clip(_cacah(w, 0.92, 0.42, rng), 0, 4)
    # Telepon pintar kini hampir merata; jumlahnya lebih ditentukan banyaknya
    # anggota dewasa daripada oleh kekayaan.
    laju_ponsel = np.clip(0.52 * jumlah_anggota, 0.3, 4.0) * np.exp(0.20 * w - 0.02)
    hasil["jumlah_smartphone"] = np.clip(rng.poisson(laju_ponsel), 0, 6).astype(np.int16)

    # Emas menjadi tabungan yang paling lazim dan paling cepat dicairkan saat
    # keluarga terdesak. Sebagian besar tidak memilikinya sama sekali.
    punya_emas = _milik(w, 0.30, 0.60, rng).astype(bool)
    gram = np.where(punya_emas, rng.gamma(1.6, 3.4, n) * np.exp(0.42 * w - 0.09), 0.0)
    hasil["gram_emas_perhiasan"] = np.round(np.clip(gram, 0.0, 400.0), 2)

    # -----------------------------------------------------------------
    # Lahan dan ternak - ditentukan sektor pekerjaan, bukan semata kekayaan
    # -----------------------------------------------------------------
    petani = np.isin(lapangan_usaha, [1, 2, 3, 6])
    peternak = np.isin(lapangan_usaha, [5])
    nelayan = np.isin(lapangan_usaha, [4])

    peluang_lahan = np.where(petani, 0.78, np.where(peternak, 0.45, 0.10))
    punya_lahan = rng.random(n) < peluang_lahan
    luas_ha = np.where(
        punya_lahan, rng.gamma(1.5, 0.30, n) * np.exp(0.30 * w), 0.0
    )
    hasil["luas_sawah_kebun_ha"] = np.round(np.clip(luas_ha, 0.0, 12.0), 4)

    hasil["jumlah_ternak_besar"] = np.where(
        peternak,
        rng.poisson(2.4 * np.exp(0.35 * w)),
        np.where(petani, rng.poisson(0.35 * np.exp(0.35 * w)), rng.poisson(0.04)),
    ).astype(np.int16)
    hasil["jumlah_ternak_kecil"] = np.where(
        peternak,
        rng.poisson(6.5 * np.exp(0.25 * w)),
        np.where(petani, rng.poisson(1.6 * np.exp(0.25 * w)), rng.poisson(0.18)),
    ).astype(np.int16)

    hasil["jumlah_perahu"] = np.where(
        nelayan, rng.poisson(0.9), hasil["jumlah_perahu"]
    ).astype(np.int16)

    return hasil


__all__ = [
    "KORELASI",
    "bangkitkan_hunian_dan_aset",
]
