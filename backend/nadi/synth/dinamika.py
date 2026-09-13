"""Dinamika antar-gelombang: guncangan, pengeluaran, dan perpindahan keadaan.

Di sinilah panel longitudinal terbentuk, dan di sinilah label yang dipelajari
model dilahirkan. Persamaan pokoknya sederhana namun setiap sukunya memiliki
alasan:

    log(pengeluaran per kapita) = kemampuan permanen
                                + tren periode
                                + simpangan sementara
                                + dampak guncangan yang tersisa
                                + tambahan dari bantuan

**Kemampuan permanen** tetap sepanjang waktu dan tidak pernah dilihat model.
**Simpangan sementara** mengikuti proses berkorelasi antar-periode: bulan yang
buruk cenderung diikuti bulan yang kurang baik, tetapi keadaan perlahan kembali
ke titik semula. **Dampak guncangan** hanya pulih sebagian setiap gelombang -
sisanya menetap, dan itulah sebabnya satu peristiwa buruk sanggup mengubah
lintasan sebuah keluarga bertahun-tahun kemudian.

Suku **tren periode** dikalibrasi ulang pada setiap gelombang sehingga angka
kemiskinan yang dihasilkan sama dengan angka BPS Kabupaten Pringsewu. Dengan
begitu, panel sintetis ini mereproduksi penurunan kemiskinan yang sebenarnya
terjadi - dari 9,14 persen pada 2023 menjadi 7,60 persen pada 2025 - alih-alih
sekadar bergerak sembarang arah.

Label yang dipelajari model adalah keadaan pada gelombang **berikutnya**:
apakah keluarga ini akan berada di bawah garis kemiskinan pada pemutakhiran
mendatang. Label itu dibentuk di sini, dan tidak satu pun fitur pada
:mod:`nadi.ml.pembangun_fitur` menyentuhnya.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from nadi.db.enums import JenisGuncangan, LapanganUsaha, TingkatKeparahan
from nadi.synth.parameter import ACUAN, PARAMETER
from nadi.synth.penargetan import (
    DAYA_SERAP_BANTUAN,
    ringkas_kepesertaan,
    tentukan_kepesertaan,
)

#: Sasaran angka kemiskinan tiap gelombang, dalam persen, dihitung pada cakupan
#: desil 1 sampai 5 - yakni populasi yang dibangkitkan generator ini.
#:
#: Cara menurunkannya perlu ketelitian, sebab tiga angka penduduk beredar untuk
#: Pringsewu dan hanya satu yang benar sebagai basis angka kemiskinan.
#:
#:   1. Ambil JUMLAH penduduk miskin dari BPS, bukan persentasenya:
#:      2024 = 34.420 jiwa, 2025 = 31.660 jiwa.
#:   2. Bagi dengan penduduk desil 1 sampai 5 menurut DTSEN, yaitu 241.740
#:      jiwa - cakupan populasi yang dibangkitkan generator.
#:   3. Hasilnya: 2023 = 15,53 persen, 2024 = 14,24 persen, 2025 = 13,10 persen.
#:
#: Memakai persentase BPS langsung terhadap penduduk DTSEN akan keliru, sebab
#: BPS menghitung terhadap proyeksi Sensus Penduduk 2020 yang berjumlah sekitar
#: 416 ribu jiwa, bukan terhadap 451 ribu jiwa versi DTSEN. Selisih basis
#: sebesar delapan persen itu menggeser seluruh sasaran sekitar satu koma tiga
#: poin persen - cukup besar untuk membuat panel tidak lagi sepadan dengan
#: keadaan sesungguhnya.
#:
#: Gelombang berjarak enam bulan mulai Maret 2023, mengikuti waktu pencacahan
#: Susenas. Gelombang September merupakan interpolasi, gelombang terakhir
#: ekstrapolasi kelanjutan tren.
SASARAN_KEMISKINAN_GELOMBANG: tuple[float, ...] = (
    15.53,  # Maret 2023      - setara 9,14 persen tingkat kabupaten
    14.89,  # September 2023  - interpolasi
    14.24,  # Maret 2024      - setara 8,32 persen (34.420 jiwa)
    13.67,  # September 2024  - interpolasi
    13.10,  # Maret 2025      - setara 7,60 persen (31.660 jiwa)
    12.64,  # September 2025  - ekstrapolasi
)


@dataclass
class KejadianGuncangan:
    """Kumpulan kejadian guncangan dalam bentuk larik rata."""

    keluarga_idx: np.ndarray
    gelombang: np.ndarray
    jenis: np.ndarray
    keparahan: np.ndarray
    dampak: np.ndarray


@dataclass
class PanelSintetis:
    """Panel longitudinal lengkap. Larik berbentuk (gelombang, keluarga)."""

    pengeluaran_per_kapita: np.ndarray
    rasio_garis_kemiskinan: np.ndarray
    status_miskin: np.ndarray
    desil: np.ndarray
    """Desil kesejahteraan MENURUT CATATAN - keluaran proxy means test.
    Inilah yang dimiliki pemerintah daerah dan yang dilihat model."""

    desil_sebenarnya: np.ndarray
    """Desil menurut pengeluaran yang sesungguhnya. TIDAK pernah disimpan ke
    basis data dan tidak pernah menjadi fitur; hanya dipakai menilai
    seberapa besar kekeliruan penduga, sebagaimana kajian evaluasi
    penargetan melakukannya."""

    desil_tercatat: np.ndarray
    nilai_bantuan_bulanan: np.ndarray
    jumlah_program_diterima: np.ndarray
    kepesertaan: list[dict[str, np.ndarray]]
    kelayakan: list[dict[str, np.ndarray]]
    jumlah_ber_jkn: np.ndarray
    umur_data_bulan: np.ndarray
    kelengkapan_data: np.ndarray
    guncangan: KejadianGuncangan
    hunian_per_gelombang: list[dict[str, np.ndarray]]

    #: Label yang dipelajari model: benar bila keluarga berada di bawah garis
    #: kemiskinan pada gelombang BERIKUTNYA. Gelombang terakhir bernilai
    #: kosong sebab tidak memiliki gelombang sesudahnya.
    label_miskin_berikutnya: np.ndarray
    label_tersedia: np.ndarray

    #: Batas desil dalam rupiah, ditetapkan pada gelombang pertama.
    batas_desil: np.ndarray

    catatan_kalibrasi: list[dict] = field(default_factory=list)

    @property
    def jumlah_gelombang(self) -> int:
        return int(self.status_miskin.shape[0])

    @property
    def jumlah_keluarga(self) -> int:
        return int(self.status_miskin.shape[1])


# ===========================================================================
# Guncangan
# ===========================================================================
def _laju_guncangan(
    *,
    lapangan_usaha: np.ndarray,
    ada_penyakit_kronis: np.ndarray,
    jumlah_lansia: np.ndarray,
) -> np.ndarray:
    """Hitung peluang sebuah keluarga terkena guncangan pada satu gelombang.

    Peluangnya tidak sama bagi semua orang, dan perbedaan itu bukan hiasan.
    Keluarga petani menghadapi cuaca dan harga panen; keluarga dengan anggota
    sakit menahun menghadapi biaya berobat yang sewaktu-waktu melonjak;
    keluarga berlansia menghadapi risiko kehilangan anggota. Ketiganya membuat
    kerentanan dapat diperkirakan sebelum kejadiannya - dan kemampuan
    memperkirakan itulah yang menjadi alasan sistem ini dibangun.
    """
    n = len(lapangan_usaha)
    laju = np.full(n, PARAMETER.peluang_dasar_guncangan, dtype=float)

    musiman = np.isin(
        lapangan_usaha, [j.value for j in LapanganUsaha if j.rentan_musiman]
    )
    laju = np.where(musiman, laju * PARAMETER.pengali_guncangan_sektor_musiman, laju)
    laju = np.where(
        ada_penyakit_kronis, laju * PARAMETER.pengali_guncangan_penyakit_kronis, laju
    )
    laju = np.where(jumlah_lansia > 0, laju * PARAMETER.pengali_guncangan_lansia, laju)
    return np.clip(laju, 0.0, 0.85)


def _pilih_jenis_guncangan(
    rng: np.random.Generator,
    n: int,
    *,
    musiman: np.ndarray,
    ada_penyakit: np.ndarray,
    ada_lansia: np.ndarray,
) -> np.ndarray:
    """Pilih jenis guncangan yang dialami, disesuaikan dengan ciri keluarga."""
    jenis = np.array(
        [
            JenisGuncangan.SAKIT_BERAT.value,
            JenisGuncangan.KEHILANGAN_PEKERJAAN.value,
            JenisGuncangan.GAGAL_PANEN.value,
            JenisGuncangan.KEMATIAN_PENCARI_NAFKAH.value,
            JenisGuncangan.BENCANA_ALAM.value,
            JenisGuncangan.KELAHIRAN_ANGGOTA_BARU.value,
            JenisGuncangan.PERCERAIAN.value,
            JenisGuncangan.KENAIKAN_HARGA_PANGAN.value,
            JenisGuncangan.KERUSAKAN_RUMAH.value,
            JenisGuncangan.ANAK_MASUK_JENJANG_BARU.value,
        ]
    )
    bobot = np.tile(
        np.array([0.20, 0.16, 0.10, 0.03, 0.05, 0.09, 0.03, 0.14, 0.08, 0.12]), (n, 1)
    )
    bobot[musiman, 2] *= 4.0  # gagal panen jauh lebih mungkin di sektor musiman
    bobot[ada_penyakit, 0] *= 2.2  # sakit berat
    bobot[ada_lansia, 3] *= 2.5  # kematian pencari nafkah
    bobot /= bobot.sum(axis=1, keepdims=True)

    # Pengambilan contoh kategori per baris dengan bobot berbeda-beda,
    # dikerjakan sekaligus lewat jumlah kumulatif.
    kumulatif = bobot.cumsum(axis=1)
    acak = rng.random((n, 1))
    indeks = (acak > kumulatif).sum(axis=1)
    return jenis[np.clip(indeks, 0, len(jenis) - 1)]


# ===========================================================================
# Kalibrasi
# ===========================================================================
def _cari_tren(
    log_dasar: np.ndarray,
    tambahan_bantuan: np.ndarray,
    bobot_jiwa: np.ndarray,
    garis: float,
    sasaran: float,
) -> float:
    """Cari geseran tren agar angka kemiskinan tepat sama dengan sasaran.

    Diselesaikan dengan pembagian dua karena bantuan bersifat menambah, bukan
    mengalikan, sehingga tidak ada rumus tertutup untuk geserannya. Dua puluh
    putaran sudah memberi ketelitian jauh melampaui kebutuhan.
    """

    def angka_kemiskinan(geser: float) -> float:
        c = np.exp(log_dasar + geser) + tambahan_bantuan
        return float(np.average(c < garis, weights=bobot_jiwa))

    bawah, atas = -1.5, 1.5
    for _ in range(40):
        tengah = (bawah + atas) / 2.0
        if angka_kemiskinan(tengah) > sasaran:
            bawah = tengah  # terlalu banyak yang miskin, naikkan pengeluaran
        else:
            atas = tengah
    return (bawah + atas) / 2.0


def _hitung_batas_desil(pengeluaran: np.ndarray, bobot_jiwa: np.ndarray) -> np.ndarray:
    """Tetapkan batas desil 1 sampai 5 dari sebaran gelombang pertama.

    Cakupan data ini adalah desil 1 sampai 5 penduduk kabupaten, yaitu separuh
    terbawah. Karena itu setiap desil di dalamnya menempati seperlima populasi
    yang dibangkitkan: desil 1 adalah 20 persen terbawah dari populasi ini,
    yang setara 10 persen terbawah dari seluruh penduduk kabupaten.

    Batas ditetapkan sekali lalu dipertahankan dalam nilai rupiah. Akibatnya
    keluarga yang membaik benar-benar naik desil, bahkan dapat keluar dari
    cakupan desil 5 - peristiwa yang di lapangan disebut graduasi, dan yang
    perlu dikenali sistem agar bantuan dapat dialihkan kepada yang lebih
    membutuhkan.
    """
    # Empat batas pertama membagi populasi menjadi lima bagian sama besar.
    # Batas kelima - pemisah desil 5 dan 6 - diletakkan pada persentil ke-97,
    # bukan pada nilai tertinggi.
    #
    # Perbedaannya menentukan. Memakai nilai tertinggi membuat batas itu
    # mustahil dilampaui siapa pun, sehingga tidak ada satu pun keluarga yang
    # dapat tercatat mentas dari cakupan desil 1 sampai 5 - dan seluruh kasus
    # penerima yang seharusnya sudah keluar dari daftar tidak akan pernah
    # muncul. Persentil ke-97 menyisakan ruang bagi keluarga yang benar-benar
    # membaik untuk terbaca demikian.
    titik = (0.20, 0.40, 0.60, 0.80, 0.97)
    urut = np.argsort(pengeluaran)
    bobot_urut = bobot_jiwa[urut]
    kumulatif = np.cumsum(bobot_urut) / bobot_urut.sum()
    batas = []
    for q in titik:
        posisi = min(int(np.searchsorted(kumulatif, q)), len(urut) - 1)
        batas.append(pengeluaran[urut[posisi]])
    return np.array(batas, dtype=float)


def _kalibrasi_derau_pmt(
    var_kemampuan: float, var_pengeluaran: float, sasaran_r2: float
) -> float:
    """Cari besar derau agar proxy means test mencapai daya jelas yang wajar.

    Ini koreksi paling menentukan pada seluruh generator, dan ditemukan lewat
    kekeliruan: pada rancangan awal, desil kesejahteraan dihitung langsung
    dengan mengelompokkan pengeluaran yang sebenarnya. Akibatnya desil menjadi
    sekadar bentuk kasar dari jawaban, model menyerapnya begitu saja - satu
    fitur menguasai delapan puluh enam persen keputusan - dan seluruh angka
    evaluasi menjadi tidak berarti.

    Di lapangan, desil DTSEN sama sekali bukan pengeluaran yang diukur. Ia
    keluaran proxy means test: sebuah regresi yang menduga kesejahteraan dari
    penanda tak langsung seperti kondisi rumah, aset, dan pendidikan. Kajian
    lintas negara mencatat daya jelasnya hanya berkisar 0,40 sampai 0,60 -
    dengan kata lain, sekitar separuh keragaman kesejahteraan antar-keluarga
    tetap tidak terjelaskan. Bukan karena metodenya buruk, melainkan karena
    memang begitu batas kemampuan penduga tak langsung.

    Fungsi ini menghitung berapa besar derau yang perlu ditambahkan agar
    hubungan antara desil dan pengeluaran sesungguhnya berada pada kisaran itu,
    sehingga model NADI menghadapi persoalan yang sama sulitnya dengan yang
    akan dihadapinya di lapangan.
    """
    if var_kemampuan <= 0 or var_pengeluaran <= 0:
        return 0.0

    # Daya jelas maksimum, tercapai bila penduga mengenali kemampuan permanen
    # dengan sempurna. Ragam sementara dan guncangan tetap tidak terduga.
    r2_maksimum = var_kemampuan / var_pengeluaran
    if sasaran_r2 >= r2_maksimum:
        return 0.0

    # R2 = Var(kem)^2 / ((Var(kem) + Var(derau)) * Var(pengeluaran))
    var_total_penduga = var_kemampuan**2 / (sasaran_r2 * var_pengeluaran)
    return float(np.sqrt(max(0.0, var_total_penduga - var_kemampuan)))


def _tetapkan_desil(pengeluaran: np.ndarray, batas: np.ndarray) -> np.ndarray:
    """Petakan pengeluaran ke desil 1 sampai 7.

    Nilai di atas batas desil 5 diberi desil 6 atau 7 menurut seberapa jauh ia
    melampaui, sehingga keluarga yang benar-benar mentas terbaca demikian dan
    tidak tertahan di desil 5 selamanya.
    """
    desil = np.searchsorted(batas, pengeluaran, side="right") + 1
    diatas = pengeluaran > batas[-1]
    jauh_diatas = pengeluaran > batas[-1] * 1.35
    desil = np.where(diatas, 6, desil)
    desil = np.where(jauh_diatas, 7, desil)
    return np.clip(desil, 1, 7).astype(np.int8)


# ===========================================================================
# Pembangkit panel
# ===========================================================================
def bangkitkan_panel(
    *,
    kemampuan: np.ndarray,
    jumlah_anggota: np.ndarray,
    lapangan_usaha: np.ndarray,
    ada_penyakit_kronis: np.ndarray,
    jumlah_anak_sekolah: np.ndarray,
    jumlah_balita: np.ndarray,
    jumlah_lansia: np.ndarray,
    jumlah_disabilitas: np.ndarray,
    jumlah_ibu_hamil: np.ndarray,
    jumlah_ber_jkn: np.ndarray,
    jumlah_tanpa_dokumen: np.ndarray,
    hunian_awal: dict[str, np.ndarray],
    rng: np.random.Generator,
    jumlah_gelombang: int | None = None,
) -> PanelSintetis:
    """Bangkitkan panel longitudinal lengkap."""
    n = len(kemampuan)
    T = jumlah_gelombang or PARAMETER.jumlah_gelombang
    garis = ACUAN.garis_kemiskinan
    bobot_jiwa = jumlah_anggota.astype(float)
    ada_masalah_dokumen = jumlah_tanpa_dokumen > 0

    # Jaminan kesehatan di luar jalur bantuan iuran - ditanggung pemberi kerja
    # atau dibayar sendiri. Nilainya tetap sepanjang waktu; yang berubah adalah
    # tambahan dari kepesertaan bantuan iuran pada tiap gelombang.
    jkn_non_bantuan = jumlah_ber_jkn.copy()

    musiman = np.isin(lapangan_usaha, [j.value for j in LapanganUsaha if j.rentan_musiman])
    laju_guncangan = _laju_guncangan(
        lapangan_usaha=lapangan_usaha,
        ada_penyakit_kronis=ada_penyakit_kronis,
        jumlah_lansia=jumlah_lansia,
    )

    # --- Larik keluaran ---
    pengeluaran = np.zeros((T, n), dtype=np.float64)
    rasio = np.zeros((T, n), dtype=np.float32)
    miskin = np.zeros((T, n), dtype=bool)
    desil = np.zeros((T, n), dtype=np.int8)
    desil_asli = np.zeros((T, n), dtype=np.int8)
    desil_tercatat = np.zeros((T, n), dtype=np.int8)
    nilai_bantuan = np.zeros((T, n), dtype=np.float32)
    jumlah_program = np.zeros((T, n), dtype=np.int8)
    ber_jkn = np.zeros((T, n), dtype=np.int16)
    umur_data = np.zeros((T, n), dtype=np.int16)
    kelengkapan = np.ones((T, n), dtype=np.float32)

    kepesertaan_per_gelombang: list[dict[str, np.ndarray]] = []
    kelayakan_per_gelombang: list[dict[str, np.ndarray]] = []
    hunian_per_gelombang: list[dict[str, np.ndarray]] = []
    catatan: list[dict] = []

    g_idx: list[np.ndarray] = []
    g_wave: list[np.ndarray] = []
    g_jenis: list[np.ndarray] = []
    g_parah: list[np.ndarray] = []
    g_dampak: list[np.ndarray] = []

    # --- Keadaan berjalan ---
    simpangan = rng.normal(0.0, PARAMETER.sd_guncangan_sementara, n)
    sisa_guncangan = np.zeros(n, dtype=float)
    hunian = {k: v.copy() for k, v in hunian_awal.items()}
    batas_desil: np.ndarray | None = None
    kepesertaan_lalu: dict[str, np.ndarray] | None = None
    bulan_sejak_mutakhir = rng.integers(0, PARAMETER.bulan_per_gelombang, n).astype(np.int16)

    # -----------------------------------------------------------------
    # Proxy means test - penduga kesejahteraan yang menghasilkan desil
    # -----------------------------------------------------------------
    # Desil DTSEN bukan pengeluaran yang diukur, melainkan keluaran sebuah
    # penduga tak langsung. Kekeliruannya karena itu tidak acak sepenuhnya:
    # sebagian menetap pada keluarga yang sama (cara pencacah menilai, keadaan
    # rumah yang menyesatkan, keluarga yang sulit ditemui), dan sebagian
    # berubah setiap kali pendataan diulang.
    #
    # Pembagian dua pertiga menetap dan sepertiga berubah dipilih agar
    # kekeliruan tidak hilang dengan sendirinya lewat pemutakhiran berulang -
    # sebab di lapangan pun tidak.
    ragam_sementara = PARAMETER.sd_guncangan_sementara**2 / (
        1.0 - PARAMETER.korelasi_antar_gelombang**2
    )
    var_kemampuan = float(np.var(kemampuan))
    var_pengeluaran_perkiraan = var_kemampuan + ragam_sementara + 0.012
    sd_derau_pmt = _kalibrasi_derau_pmt(
        var_kemampuan, var_pengeluaran_perkiraan, PARAMETER.sasaran_r2_pmt
    )
    sd_menetap = sd_derau_pmt * np.sqrt(2.0 / 3.0)
    sd_berubah = sd_derau_pmt * np.sqrt(1.0 / 3.0)

    derau_menetap = rng.normal(0.0, sd_menetap, n)
    pmt = kemampuan + derau_menetap + rng.normal(0.0, sd_berubah, n)
    batas_pmt = _hitung_batas_desil(np.exp(pmt), bobot_jiwa)

    # --- Kekeliruan pencatatan desil yang bersifat menetap ---
    # Ditetapkan sekali di awal dan tidak berubah sepanjang panel, sebab
    # inilah sifatnya: catatan yang keliru tetap keliru sampai ada yang
    # memeriksanya. Keluarga yang tercatat terlalu sejahtera akan terlewat
    # pada setiap penetapan penerima - dan merekalah yang paling perlu
    # ditemukan sistem ini.
    salah_catat = rng.random(n) < PARAMETER.peluang_salah_catat_desil
    arah = np.where(rng.random(n) < PARAMETER.bias_desil_ke_atas, 1, -1)
    besar = rng.choice([1, 2, 3], size=n, p=[0.55, 0.32, 0.13])
    bias_desil = np.where(salah_catat, arah * besar, 0).astype(np.int8)

    dampak_keparahan = np.array(
        [
            0.0,
            PARAMETER.dampak_guncangan_ringan,
            PARAMETER.dampak_guncangan_sedang,
            PARAMETER.dampak_guncangan_berat,
        ]
    )

    for t in range(T):
        # -------------------------------------------------------------
        # 0. Pemutakhiran data dan penilaian ulang kesejahteraan
        # -------------------------------------------------------------
        # Keluarga yang tidak didatangi ulang tetap membawa desil lamanya.
        # Inilah sumber ketidaksesuaian sasaran yang paling sering terjadi
        # sekaligus paling jarang disadari: bukan penilaian yang keliru,
        # melainkan penilaian yang benar pada keadaan yang sudah berubah.
        dimutakhirkan = rng.random(n) >= PARAMETER.peluang_data_kedaluwarsa
        if t > 0:
            pmt = np.where(
                dimutakhirkan,
                kemampuan + derau_menetap + rng.normal(0.0, sd_berubah, n),
                pmt,
            )
        bulan_sejak_mutakhir = np.where(
            dimutakhirkan, 0, bulan_sejak_mutakhir + PARAMETER.bulan_per_gelombang
        ).astype(np.int16)
        desil_pmt = _tetapkan_desil(np.exp(pmt), batas_pmt)

        # -------------------------------------------------------------
        # 1. Guncangan pada gelombang ini
        # -------------------------------------------------------------
        kena = rng.random(n) < laju_guncangan
        idx_kena = np.flatnonzero(kena)
        if idx_kena.size:
            keparahan = rng.choice(
                [
                    TingkatKeparahan.RINGAN.value,
                    TingkatKeparahan.SEDANG.value,
                    TingkatKeparahan.BERAT.value,
                ],
                size=idx_kena.size,
                p=[0.52, 0.34, 0.14],
            )
            jenis = _pilih_jenis_guncangan(
                rng,
                idx_kena.size,
                musiman=musiman[idx_kena],
                ada_penyakit=ada_penyakit_kronis[idx_kena],
                ada_lansia=jumlah_lansia[idx_kena] > 0,
            )
            dampak = dampak_keparahan[keparahan]
            sisa_guncangan[idx_kena] += dampak

            g_idx.append(idx_kena)
            g_wave.append(np.full(idx_kena.size, t, dtype=np.int8))
            g_jenis.append(jenis.astype(np.int8))
            g_parah.append(keparahan.astype(np.int8))
            g_dampak.append((dampak * 100.0).astype(np.float32))

        # -------------------------------------------------------------
        # 2. Kepesertaan program, ditetapkan dari desil yang TERCATAT
        # -------------------------------------------------------------
        desil_dipakai = desil_pmt

        # Terapkan kekeliruan pencatatan yang menetap. Sesudah baris ini,
        # desil yang dipakai menetapkan penerima adalah desil MENURUT CATATAN -
        # yang bagi sebagian keluarga memang tidak sama dengan keadaannya.
        desil_dipakai = np.clip(desil_dipakai.astype(np.int16) + bias_desil, 1, 7).astype(np.int8)
        desil_tercatat[t] = desil_dipakai

        kepesertaan, nilai, kelayakan = tentukan_kepesertaan(
            desil_tercatat=desil_dipakai,
            kepesertaan_sebelumnya=kepesertaan_lalu,
            jumlah_anggota=jumlah_anggota,
            jumlah_anak_sekolah=jumlah_anak_sekolah,
            jumlah_balita=jumlah_balita,
            jumlah_lansia=jumlah_lansia,
            jumlah_disabilitas=jumlah_disabilitas,
            jumlah_ibu_hamil=jumlah_ibu_hamil,
            cakupan_jkn=jkn_non_bantuan / np.maximum(1, jumlah_anggota),
            ada_masalah_dokumen=ada_masalah_dokumen,
            rng=rng,
        )
        kepesertaan_lalu = kepesertaan
        kepesertaan_per_gelombang.append(kepesertaan)
        kelayakan_per_gelombang.append(kelayakan)
        nilai_bantuan[t] = nilai
        jumlah_program[t] = ringkas_kepesertaan(kepesertaan)

        # Kepesertaan bantuan iuran menjamin seluruh anggota keluarga.
        # Inilah rantai sebab-akibat yang membuat pemantauan hasil bermakna:
        # ketika sebuah keluarga ditetapkan sebagai penerima, cakupan jaminan
        # kesehatannya melonjak pada gelombang yang sama, dan perubahan itu
        # terbaca pada perbandingan sebelum dan sesudah.
        penerima_pbi = kepesertaan.get("PBI-JKN")
        ber_jkn[t] = (
            np.where(penerima_pbi, jumlah_anggota, jkn_non_bantuan)
            if penerima_pbi is not None
            else jkn_non_bantuan
        )

        # -------------------------------------------------------------
        # 3. Pengeluaran
        # -------------------------------------------------------------
        simpangan = (
            PARAMETER.korelasi_antar_gelombang * simpangan
            + rng.normal(0.0, PARAMETER.sd_guncangan_sementara, n)
        )
        log_dasar = kemampuan + simpangan + sisa_guncangan
        tambahan = DAYA_SERAP_BANTUAN * nilai / np.maximum(1, jumlah_anggota)

        sasaran = SASARAN_KEMISKINAN_GELOMBANG[
            min(t, len(SASARAN_KEMISKINAN_GELOMBANG) - 1)
        ] / 100.0
        tren = _cari_tren(log_dasar, tambahan, bobot_jiwa, garis, sasaran)

        c = np.exp(log_dasar + tren) + tambahan
        pengeluaran[t] = c
        rasio[t] = c / garis
        miskin[t] = c < garis

        tercapai = float(np.average(miskin[t], weights=bobot_jiwa))
        catatan.append(
            {
                "gelombang": t,
                "sasaran_persen": round(sasaran * 100, 2),
                "tercapai_persen": round(tercapai * 100, 2),
                "geseran_tren": round(tren, 4),
                "median_pengeluaran": round(float(np.median(c)), 0),
                "r2_pmt": round(
                    float(np.corrcoef(pmt, np.log(np.maximum(c, 1.0)))[0, 1] ** 2), 4
                ),
            }
        )

        # -------------------------------------------------------------
        # 4. Desil
        # -------------------------------------------------------------
        # Yang disimpan sebagai desil kesejahteraan adalah keluaran penduga,
        # bukan hasil pengelompokan pengeluaran sesungguhnya - persis seperti
        # yang dimiliki pemerintah daerah. Desil menurut pengeluaran ikut
        # dihitung namun hanya untuk keperluan penilaian generator, dan tidak
        # pernah disimpan ke basis data maupun dilihat model.
        desil[t] = desil_pmt
        if batas_desil is None:
            batas_desil = _hitung_batas_desil(c, bobot_jiwa)
        desil_asli[t] = _tetapkan_desil(c, batas_desil)

        # -------------------------------------------------------------
        # 5. Kualitas data
        # -------------------------------------------------------------
        umur_data[t] = bulan_sejak_mutakhir + PARAMETER.bulan_per_gelombang // 2
        kelengkapan[t] = np.where(
            rng.random(n) < PARAMETER.peluang_data_tidak_lengkap,
            rng.uniform(0.55, 0.92, n),
            1.0,
        )

        # -------------------------------------------------------------
        # 6. Hunian
        # -------------------------------------------------------------
        hunian_per_gelombang.append({k: v.copy() for k, v in hunian.items()})
        if t < T - 1:
            _kembangkan_hunian(hunian, c, kemampuan, rng)

        # -------------------------------------------------------------
        # 7. Pemulihan sebagian dampak guncangan
        # -------------------------------------------------------------
        sisa_guncangan *= 1.0 - PARAMETER.pemulihan_guncangan

    # -----------------------------------------------------------------
    # Label
    # -----------------------------------------------------------------
    label = np.zeros((T, n), dtype=bool)
    tersedia = np.zeros((T, n), dtype=bool)
    label[: T - 1] = miskin[1:]
    tersedia[: T - 1] = True

    guncangan = KejadianGuncangan(
        keluarga_idx=np.concatenate(g_idx) if g_idx else np.array([], dtype=int),
        gelombang=np.concatenate(g_wave) if g_wave else np.array([], dtype=np.int8),
        jenis=np.concatenate(g_jenis) if g_jenis else np.array([], dtype=np.int8),
        keparahan=np.concatenate(g_parah) if g_parah else np.array([], dtype=np.int8),
        dampak=np.concatenate(g_dampak) if g_dampak else np.array([], dtype=np.float32),
    )

    return PanelSintetis(
        pengeluaran_per_kapita=pengeluaran,
        rasio_garis_kemiskinan=rasio,
        status_miskin=miskin,
        desil=desil,
        desil_sebenarnya=desil_asli,
        desil_tercatat=desil_tercatat,
        nilai_bantuan_bulanan=nilai_bantuan,
        jumlah_program_diterima=jumlah_program,
        kepesertaan=kepesertaan_per_gelombang,
        kelayakan=kelayakan_per_gelombang,
        jumlah_ber_jkn=ber_jkn,
        umur_data_bulan=umur_data,
        kelengkapan_data=kelengkapan,
        guncangan=guncangan,
        hunian_per_gelombang=hunian_per_gelombang,
        label_miskin_berikutnya=label,
        label_tersedia=tersedia,
        batas_desil=batas_desil if batas_desil is not None else np.zeros(5),
        catatan_kalibrasi=catatan,
    )


# ---------------------------------------------------------------------------
def _kembangkan_hunian(
    hunian: dict[str, np.ndarray],
    pengeluaran: np.ndarray,
    kemampuan: np.ndarray,
    rng: np.random.Generator,
) -> None:
    """Perbarui kondisi hunian dan aset untuk gelombang berikutnya.

    Rumah berubah pelan. Keluarga memperbaiki rumah ketika ada kelebihan uang,
    dan yang diperbaiki lebih dahulu biasanya yang paling mengganggu -
    lantai tanah sebelum jenis atap, jamban sebelum daya listrik. Perubahan
    dibuat jarang, sekitar lima persen keluarga per gelombang, agar pemantauan
    hasil intervensi tetap bermakna: bila hampir semua rumah membaik dengan
    sendirinya, perbaikan yang datang dari program tidak lagi dapat dibedakan.
    """
    n = len(pengeluaran)
    # Kelebihan kemampuan dibanding perkiraan permanen menjadi penanda ada
    # ruang untuk memperbaiki rumah.
    kelebihan = np.log(np.maximum(pengeluaran, 1.0)) - kemampuan
    peluang = np.clip(0.045 + 0.09 * kelebihan, 0.006, 0.24)
    membaik = rng.random(n) < peluang

    # --- Sanitasi lebih dahulu: paling murah dan paling besar dampaknya ---
    perlu_kloset = membaik & (hunian["jenis_kloset"] > 1)
    hunian["jenis_kloset"] = np.where(
        perlu_kloset, np.maximum(1, hunian["jenis_kloset"] - 1), hunian["jenis_kloset"]
    ).astype(np.int16)

    perlu_tinja = membaik & ~perlu_kloset & ~np.isin(hunian["pembuangan_akhir_tinja"], [1, 2])
    hunian["pembuangan_akhir_tinja"] = np.where(
        perlu_tinja, 1, hunian["pembuangan_akhir_tinja"]
    ).astype(np.int16)

    # --- Lantai tanah adalah keluhan yang paling cepat ditangani ---
    perlu_lantai = membaik & ~perlu_kloset & ~perlu_tinja & (hunian["jenis_lantai_terluas"] >= 7)
    hunian["jenis_lantai_terluas"] = np.where(
        perlu_lantai, 6, hunian["jenis_lantai_terluas"]
    ).astype(np.int16)

    # --- Dinding dan atap menyusul ---
    perlu_dinding = (
        membaik & ~perlu_kloset & ~perlu_tinja & ~perlu_lantai & (hunian["jenis_dinding_terluas"] >= 4)
    )
    hunian["jenis_dinding_terluas"] = np.where(
        perlu_dinding, 3, hunian["jenis_dinding_terluas"]
    ).astype(np.int16)

    perlu_atap = (
        membaik
        & ~perlu_kloset
        & ~perlu_tinja
        & ~perlu_lantai
        & ~perlu_dinding
        & (hunian["jenis_atap_terluas"] == 6)
    )
    hunian["jenis_atap_terluas"] = np.where(
        perlu_atap, 4, hunian["jenis_atap_terluas"]
    ).astype(np.int16)

    # --- Aset ---
    # Telepon pintar bertambah paling cepat, kendaraan menyusul.
    tambah_ponsel = rng.random(n) < np.clip(0.06 + 0.06 * kelebihan, 0.01, 0.20)
    hunian["jumlah_smartphone"] = np.clip(
        hunian["jumlah_smartphone"] + tambah_ponsel.astype(np.int16), 0, 6
    ).astype(np.int16)

    tambah_motor = rng.random(n) < np.clip(0.018 + 0.05 * kelebihan, 0.002, 0.10)
    hunian["jumlah_sepeda_motor"] = np.clip(
        hunian["jumlah_sepeda_motor"] + tambah_motor.astype(np.int16), 0, 4
    ).astype(np.int16)

    tambah_kulkas = rng.random(n) < np.clip(0.012 + 0.04 * kelebihan, 0.001, 0.08)
    hunian["jumlah_lemari_es"] = np.clip(
        hunian["jumlah_lemari_es"] + tambah_kulkas.astype(np.int16), 0, 2
    ).astype(np.int16)

    # --- Emas dijual saat terdesak ---
    # Ini jalur pertahanan pertama sebuah keluarga menghadapi guncangan, dan
    # sekaligus penanda bahwa keadaan sedang memburuk.
    terdesak = kelebihan < -0.18
    jual = terdesak & (rng.random(n) < 0.32)
    hunian["gram_emas_perhiasan"] = np.where(
        jual, np.maximum(0.0, hunian["gram_emas_perhiasan"] * 0.45), hunian["gram_emas_perhiasan"]
    )


__all__ = [
    "SASARAN_KEMISKINAN_GELOMBANG",
    "KejadianGuncangan",
    "PanelSintetis",
    "bangkitkan_panel",
]
