"""Pembangkitan susunan keluarga dan anggotanya.

Arah sebab-akibat pada berkas ini dipilih dengan sengaja, dan menentukan
apakah data yang dihasilkan berperilaku seperti kenyataan:

1. Ciri demografi dan pendidikan dibangkitkan lebih dahulu.
2. Dari ciri tersebut, ditambah bagian yang **tidak teramati**, terbentuk
   kemampuan ekonomi permanen sebuah keluarga.
3. Kondisi rumah dan kepemilikan aset dibangkitkan **dari** kemampuan tersebut.

Urutan ini mengikuti anggapan yang mendasari seluruh penargetan berbasis proksi
di Indonesia: rumah dan aset bukanlah penyebab kesejahteraan, melainkan
penandanya. Membalik urutan ini - membangkitkan aset lebih dahulu lalu
menurunkan pengeluaran darinya - akan menghasilkan data tempat model
memperoleh ketepatan yang mustahil, sebab hubungan antara penanda dan keadaan
menjadi sempurna tanpa gangguan.

Bagian tidak teramati itu - kemampuan berusaha, kekuatan jejaring keluarga,
ketahanan menghadapi penyakit - tidak pernah dilihat model. Keberadaannya
membuat sebagian keluarga hidup lebih baik daripada yang tampak dari berkas
datanya, dan sebagian lain lebih buruk. Persis seperti kenyataannya, dan
persis itulah yang menjaga angka evaluasi tetap jujur.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from nadi.db.enums import (
    BahanBakarMemasak,
    DayaListrik,
    FasilitasBAB,
    HubunganKK,
    JenisAtap,
    JenisDinding,
    JenisKelamin,
    JenisKloset,
    JenisLantai,
    PembuanganTinja,
    PendidikanTertinggi,
    StatusKegiatan,
    StatusKepemilikanRumah,
    StatusPekerjaan,
    StatusPerkawinan,
    SumberAirMinum,
    SumberPenerangan,
)
from nadi.synth.parameter import PARAMETER, SEBARAN

USIA_LANSIA = 60
USIA_BALITA = 5
USIA_SEKOLAH_MIN = 7
USIA_SEKOLAH_MAKS = 18
USIA_KERJA_MIN = 15


# ===========================================================================
# Struktur keluaran
# ===========================================================================
@dataclass
class PopulasiSintetis:
    """Hasil pembangkitan populasi, dalam bentuk larik sejajar.

    Bentuk larik dipilih ketimbang daftar objek karena seluruh perhitungan
    dinamika antar-gelombang berupa operasi vektor. Empat puluh ribu keluarga
    dikali enam gelombang berarti dua ratus empat puluh ribu baris; menyusunnya
    sebagai objek Python akan memakan waktu dan memori berlipat tanpa manfaat.
    """

    # --- Tingkat keluarga (panjang n) ---
    wilayah_idx: np.ndarray
    jumlah_anggota: np.ndarray
    kk_jenis_kelamin: np.ndarray
    kk_umur: np.ndarray
    kk_pendidikan: np.ndarray
    kk_lapangan_usaha: np.ndarray
    kk_status_pekerjaan: np.ndarray
    kk_status_kegiatan: np.ndarray

    kemampuan_laten: np.ndarray
    """Logaritma kemampuan ekonomi permanen. TIDAK PERNAH disimpan ke basis
    data dan tidak pernah menjadi fitur model. Disimpan di sini semata untuk
    membangkitkan pengeluaran dan untuk memeriksa kalibrasi generator."""

    bagian_tak_teramati: np.ndarray
    """Bagian kemampuan yang tidak dapat diterangkan ciri teramati mana pun.
    Inilah sumber ketidakpastian yang membuat persoalan ini realistis."""

    # --- Tingkat anggota (panjang total anggota) ---
    anggota_keluarga_idx: np.ndarray
    anggota_urutan: np.ndarray
    anggota_hubungan: np.ndarray
    anggota_jenis_kelamin: np.ndarray
    anggota_umur: np.ndarray
    anggota_pendidikan: np.ndarray
    anggota_partisipasi_sekolah: np.ndarray
    anggota_status_kegiatan: np.ndarray
    anggota_status_perkawinan: np.ndarray
    anggota_disabilitas: np.ndarray
    anggota_penyakit_kronis: np.ndarray
    anggota_hamil: np.ndarray
    anggota_gizi: np.ndarray
    anggota_jkn: np.ndarray
    anggota_jumlah_usaha: np.ndarray
    anggota_tanpa_dokumen: np.ndarray

    # --- Ringkasan tingkat keluarga, dihitung dari anggota ---
    jumlah_balita: np.ndarray
    jumlah_anak_sekolah: np.ndarray
    jumlah_lansia: np.ndarray
    jumlah_disabilitas: np.ndarray
    jumlah_bekerja: np.ndarray
    jumlah_ber_jkn: np.ndarray
    jumlah_ibu_hamil: np.ndarray
    jumlah_tanpa_dokumen: np.ndarray
    jumlah_usaha_keluarga: np.ndarray
    ada_penyakit_kronis: np.ndarray
    ada_gizi_bermasalah: np.ndarray
    rata_lama_sekolah_dewasa: np.ndarray

    @property
    def n(self) -> int:
        return int(len(self.jumlah_anggota))

    @property
    def n_anggota(self) -> int:
        return int(len(self.anggota_umur))


# ===========================================================================
# Pembantu
# ===========================================================================
def _pilih_kategori(rng: np.random.Generator, peluang: np.ndarray, n: int) -> np.ndarray:
    """Ambil contoh kategori berindeks nol menurut sebaran peluang."""
    p = np.asarray(peluang, dtype=float)
    p = p / p.sum()
    return rng.choice(len(p), size=n, p=p)


def _normal_terpotong(
    rng: np.random.Generator, rerata: float, sd: float, batas_bawah: float, batas_atas: float, n: int
) -> np.ndarray:
    nilai = rng.normal(rerata, sd, n)
    return np.clip(nilai, batas_bawah, batas_atas)


# ===========================================================================
# Pembangkit
# ===========================================================================
def bangkitkan_populasi(
    n: int,
    bobot_wilayah: np.ndarray,
    efek_wilayah: np.ndarray,
    rng: np.random.Generator,
) -> PopulasiSintetis:
    """Bangkitkan ``n`` keluarga beserta seluruh anggotanya.

    Args:
        n: banyaknya keluarga.
        bobot_wilayah: peluang penempatan pada tiap wilayah, sepanjang jumlah
            wilayah tingkat terbawah.
        efek_wilayah: pengaruh wilayah terhadap kemampuan ekonomi, dalam satuan
            logaritma. Wilayah yang lebih tertinggal bernilai negatif.
        rng: pembangkit bilangan acak yang sudah diberi benih.
    """
    # -----------------------------------------------------------------
    # 1. Penempatan wilayah
    # -----------------------------------------------------------------
    wilayah_idx = rng.choice(len(bobot_wilayah), size=n, p=bobot_wilayah / bobot_wilayah.sum())

    # -----------------------------------------------------------------
    # 2. Susunan dasar keluarga
    # -----------------------------------------------------------------
    jumlah_anggota = _pilih_kategori(rng, np.array(SEBARAN.peluang_jumlah_anggota), n) + 1

    kk_perempuan = rng.random(n) < SEBARAN.peluang_kk_perempuan
    kk_jenis_kelamin = np.where(
        kk_perempuan, JenisKelamin.PEREMPUAN.value, JenisKelamin.LAKI_LAKI.value
    )
    kk_umur = _normal_terpotong(
        rng, SEBARAN.umur_kk_rerata, SEBARAN.umur_kk_sd, 18, 92, n
    ).astype(np.int16)

    kk_pendidikan = (
        _pilih_kategori(rng, np.array(SEBARAN.peluang_pendidikan_kk), n) + 1
    ).astype(np.int8)

    kode_sektor = np.array(list(SEBARAN.peluang_sektor_kk.keys()))
    peluang_sektor = np.array(list(SEBARAN.peluang_sektor_kk.values()))
    kk_lapangan_usaha = kode_sektor[_pilih_kategori(rng, peluang_sektor, n)].astype(np.int8)

    kk_status_kegiatan = np.where(
        kk_lapangan_usaha == 20,
        StatusKegiatan.LAINNYA.value,
        StatusKegiatan.BEKERJA.value,
    ).astype(np.int8)
    kk_status_pekerjaan = _status_pekerjaan_dari_sektor(rng, kk_lapangan_usaha)

    # -----------------------------------------------------------------
    # 3. Kemampuan ekonomi permanen
    # -----------------------------------------------------------------
    kemampuan, tak_teramati = _bangkitkan_kemampuan(
        rng,
        kk_pendidikan=kk_pendidikan,
        kk_lapangan_usaha=kk_lapangan_usaha,
        kk_status_pekerjaan=kk_status_pekerjaan,
        kk_umur=kk_umur,
        kk_perempuan=kk_perempuan,
        jumlah_anggota=jumlah_anggota,
        efek_wilayah=efek_wilayah[wilayah_idx],
    )

    # -----------------------------------------------------------------
    # 4. Anggota keluarga
    # -----------------------------------------------------------------
    anggota = _bangkitkan_anggota(
        rng,
        jumlah_anggota=jumlah_anggota,
        kk_umur=kk_umur,
        kk_jenis_kelamin=kk_jenis_kelamin,
        kk_pendidikan=kk_pendidikan,
        kk_lapangan_usaha=kk_lapangan_usaha,
        kk_status_pekerjaan=kk_status_pekerjaan,
        kk_status_kegiatan=kk_status_kegiatan,
        kemampuan=kemampuan,
    )

    ringkasan = _ringkas_anggota(anggota, n, jumlah_anggota)

    return PopulasiSintetis(
        wilayah_idx=wilayah_idx,
        jumlah_anggota=jumlah_anggota,
        kk_jenis_kelamin=kk_jenis_kelamin,
        kk_umur=kk_umur,
        kk_pendidikan=kk_pendidikan,
        kk_lapangan_usaha=kk_lapangan_usaha,
        kk_status_pekerjaan=kk_status_pekerjaan,
        kk_status_kegiatan=kk_status_kegiatan,
        kemampuan_laten=kemampuan,
        bagian_tak_teramati=tak_teramati,
        **anggota,
        **ringkasan,
    )


# ---------------------------------------------------------------------------
def _status_pekerjaan_dari_sektor(
    rng: np.random.Generator, sektor: np.ndarray
) -> np.ndarray:
    """Tentukan kedudukan dalam pekerjaan, bergantung pada sektornya.

    Petani umumnya berusaha sendiri atau menjadi buruh tani lepas; pekerja
    konstruksi umumnya pekerja bebas; pegawai jasa pemerintahan hampir selalu
    berpenghasilan tetap. Perbedaan ini penting sebab kedudukan dalam pekerjaan
    menentukan seberapa terlindungi penghasilan sebuah keluarga.
    """
    n = len(sektor)
    hasil = np.full(n, StatusPekerjaan.BURUH_KARYAWAN_PEGAWAI.value, dtype=np.int8)

    pertanian = np.isin(sektor, [1, 2, 3, 4, 5, 6])
    hasil[pertanian] = rng.choice(
        [
            StatusPekerjaan.BERUSAHA_SENDIRI.value,
            StatusPekerjaan.BERUSAHA_DIBANTU_BURUH_TIDAK_TETAP.value,
            StatusPekerjaan.PEKERJA_BEBAS_PERTANIAN.value,
            StatusPekerjaan.PEKERJA_KELUARGA_TAK_DIBAYAR.value,
        ],
        size=int(pertanian.sum()),
        p=[0.42, 0.16, 0.33, 0.09],
    )

    konstruksi = sektor == 10
    hasil[konstruksi] = rng.choice(
        [
            StatusPekerjaan.PEKERJA_BEBAS_NON_PERTANIAN.value,
            StatusPekerjaan.BURUH_KARYAWAN_PEGAWAI.value,
        ],
        size=int(konstruksi.sum()),
        p=[0.72, 0.28],
    )

    dagang = np.isin(sektor, [11, 12])
    hasil[dagang] = rng.choice(
        [
            StatusPekerjaan.BERUSAHA_SENDIRI.value,
            StatusPekerjaan.BERUSAHA_DIBANTU_BURUH_TIDAK_TETAP.value,
            StatusPekerjaan.BURUH_KARYAWAN_PEGAWAI.value,
        ],
        size=int(dagang.sum()),
        p=[0.68, 0.14, 0.18],
    )

    transportasi = sektor == 13
    hasil[transportasi] = rng.choice(
        [
            StatusPekerjaan.BERUSAHA_SENDIRI.value,
            StatusPekerjaan.PEKERJA_BEBAS_NON_PERTANIAN.value,
        ],
        size=int(transportasi.sum()),
        p=[0.6, 0.4],
    )

    hasil[sektor == 20] = StatusPekerjaan.TIDAK_BEKERJA.value
    return hasil


# ---------------------------------------------------------------------------
def _bangkitkan_kemampuan(
    rng: np.random.Generator,
    *,
    kk_pendidikan: np.ndarray,
    kk_lapangan_usaha: np.ndarray,
    kk_status_pekerjaan: np.ndarray,
    kk_umur: np.ndarray,
    kk_perempuan: np.ndarray,
    jumlah_anggota: np.ndarray,
    efek_wilayah: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Bentuk logaritma kemampuan ekonomi permanen tiap keluarga.

    Returns:
        Pasangan berisi kemampuan total dan bagian yang tidak teramati.
    """
    n = len(kk_pendidikan)

    # Titik tolak: sedikit di bawah garis kemiskinan, sesuai cakupan desil bawah.
    dasar = np.log(560_000.0)

    # Pendidikan kepala keluarga - penduga kesejahteraan paling konsisten.
    tahun_sekolah = np.array(
        [PendidikanTertinggi(int(k)).tahun_sekolah for k in range(1, 9)]
    )
    pengaruh_pendidikan = 0.031 * tahun_sekolah[kk_pendidikan - 1]

    # Sektor pekerjaan.
    pengaruh_sektor = np.zeros(n)
    pengaruh_sektor[np.isin(kk_lapangan_usaha, [1, 4, 5])] = -0.09
    pengaruh_sektor[kk_lapangan_usaha == 3] = -0.02
    pengaruh_sektor[kk_lapangan_usaha == 10] = 0.03
    pengaruh_sektor[np.isin(kk_lapangan_usaha, [11, 12, 13])] = 0.07
    pengaruh_sektor[np.isin(kk_lapangan_usaha, [8, 14, 15])] = 0.11
    pengaruh_sektor[np.isin(kk_lapangan_usaha, [16, 17, 18])] = 0.19
    pengaruh_sektor[kk_lapangan_usaha == 20] = -0.28

    # Kedudukan dalam pekerjaan.
    pengaruh_kedudukan = np.zeros(n)
    pengaruh_kedudukan[
        np.isin(kk_status_pekerjaan, [StatusPekerjaan.PEKERJA_BEBAS_PERTANIAN.value, 6])
    ] = -0.11
    pengaruh_kedudukan[kk_status_pekerjaan == StatusPekerjaan.PEKERJA_KELUARGA_TAK_DIBAYAR.value] = -0.17
    pengaruh_kedudukan[kk_status_pekerjaan == StatusPekerjaan.BERUSAHA_DIBANTU_BURUH_TETAP.value] = 0.16
    pengaruh_kedudukan[kk_status_pekerjaan == StatusPekerjaan.BURUH_KARYAWAN_PEGAWAI.value] = 0.07

    # Umur: penghasilan naik lalu menurun setelah usia lanjut.
    umur = kk_umur.astype(float)
    pengaruh_umur = 0.011 * (umur - 30) - 0.00028 * (umur - 30) ** 2
    pengaruh_umur[umur >= USIA_LANSIA] -= 0.06

    # Kepala keluarga perempuan menghadapi hambatan pasar kerja yang nyata.
    pengaruh_gender = np.where(kk_perempuan, -0.08, 0.0)

    # Skala ekonomi rumah tangga: pengeluaran per kapita menurun seiring
    # bertambahnya anggota, sebab sebagian pengeluaran ditanggung bersama.
    pengaruh_ukuran = -0.055 * (jumlah_anggota - 3)

    # --- Bagian yang tidak teramati ---
    tak_teramati = rng.normal(0.0, PARAMETER.sd_kemampuan_tak_teramati, n)

    kemampuan = (
        dasar
        + pengaruh_pendidikan
        + pengaruh_sektor
        + pengaruh_kedudukan
        + pengaruh_umur
        + pengaruh_gender
        + pengaruh_ukuran
        + efek_wilayah
        + tak_teramati
    )
    return kemampuan, tak_teramati


# ---------------------------------------------------------------------------
def _bangkitkan_anggota(
    rng: np.random.Generator,
    *,
    jumlah_anggota: np.ndarray,
    kk_umur: np.ndarray,
    kk_jenis_kelamin: np.ndarray,
    kk_pendidikan: np.ndarray,
    kk_lapangan_usaha: np.ndarray,
    kk_status_pekerjaan: np.ndarray,
    kk_status_kegiatan: np.ndarray,
    kemampuan: np.ndarray,
) -> dict[str, np.ndarray]:
    """Bangkitkan seluruh anggota keluarga dalam bentuk larik rata.

    Setiap anggota membawa indeks keluarganya, sehingga peringkasan ke tingkat
    keluarga cukup dilakukan dengan ``np.bincount`` - jauh lebih cepat daripada
    menelusuri keluarga satu per satu.
    """
    n = len(jumlah_anggota)
    total = int(jumlah_anggota.sum())

    keluarga_idx = np.repeat(np.arange(n), jumlah_anggota)
    awal = np.concatenate([[0], np.cumsum(jumlah_anggota)[:-1]])
    urutan = np.arange(total) - np.repeat(awal, jumlah_anggota)

    umur = np.zeros(total, dtype=np.int16)
    jenis_kelamin = np.zeros(total, dtype=np.int8)
    hubungan = np.zeros(total, dtype=np.int8)

    # --- Anggota pertama: kepala keluarga ---
    adalah_kk = urutan == 0
    umur[adalah_kk] = kk_umur
    jenis_kelamin[adalah_kk] = kk_jenis_kelamin
    hubungan[adalah_kk] = HubunganKK.KEPALA_KELUARGA.value

    umur_kk_per_anggota = kk_umur[keluarga_idx]
    kk_jk_per_anggota = kk_jenis_kelamin[keluarga_idx]

    # --- Anggota kedua: pasangan, bila keluarga beranggota lebih dari satu ---
    # Peluang keberadaan pasangan menurun pada kepala keluarga perempuan,
    # sebab sebagian besar di antaranya berstatus cerai mati atau cerai hidup.
    adalah_kedua = urutan == 1
    peluang_pasangan = np.where(
        kk_jk_per_anggota == JenisKelamin.PEREMPUAN.value, 0.30, 0.94
    )
    jadi_pasangan = adalah_kedua & (rng.random(total) < peluang_pasangan)

    selisih = rng.normal(0.0, 4.0, total)
    selisih += np.where(kk_jk_per_anggota == JenisKelamin.LAKI_LAKI.value, -3.0, 3.0)
    umur[jadi_pasangan] = np.clip(
        umur_kk_per_anggota[jadi_pasangan] + selisih[jadi_pasangan], 17, 95
    ).astype(np.int16)
    jenis_kelamin[jadi_pasangan] = np.where(
        kk_jk_per_anggota[jadi_pasangan] == JenisKelamin.LAKI_LAKI.value,
        JenisKelamin.PEREMPUAN.value,
        JenisKelamin.LAKI_LAKI.value,
    )
    hubungan[jadi_pasangan] = HubunganKK.ISTRI_SUAMI.value

    # --- Sisanya: anak, sesekali orang tua atau famili lain ---
    sisa = ~adalah_kk & ~jadi_pasangan
    # Peluang kehadiran orang tua atau mertua meningkat pada kepala keluarga
    # berusia paruh baya - keluarga tiga generasi yang lazim di perdesaan.
    peluang_orang_tua = np.where(
        (umur_kk_per_anggota >= 38) & (umur_kk_per_anggota <= 62), 0.13, 0.04
    )
    jadi_orang_tua = sisa & (rng.random(total) < peluang_orang_tua)
    jadi_anak = sisa & ~jadi_orang_tua

    umur[jadi_orang_tua] = np.clip(
        umur_kk_per_anggota[jadi_orang_tua] + rng.normal(26.0, 5.0, int(jadi_orang_tua.sum())),
        USIA_LANSIA,
        98,
    ).astype(np.int16)
    jenis_kelamin[jadi_orang_tua] = rng.choice([1, 2], size=int(jadi_orang_tua.sum()), p=[0.38, 0.62])
    hubungan[jadi_orang_tua] = HubunganKK.ORANG_TUA_MERTUA.value

    # Umur anak dibatasi umur kepala keluarga dikurangi usia minimum menjadi
    # orang tua, sehingga tidak muncul anak yang lebih tua daripada ayahnya.
    batas_umur_anak = np.clip(umur_kk_per_anggota - 20, 1, 42)
    proporsi = rng.beta(1.7, 1.5, total)
    umur[jadi_anak] = np.clip(
        batas_umur_anak[jadi_anak] * proporsi[jadi_anak], 0, 45
    ).astype(np.int16)
    jenis_kelamin[jadi_anak] = rng.choice([1, 2], size=int(jadi_anak.sum()), p=[0.51, 0.49])
    hubungan[jadi_anak] = HubunganKK.ANAK.value

    # -----------------------------------------------------------------
    # Pendidikan
    # -----------------------------------------------------------------
    pendidikan, partisipasi = _bangkitkan_pendidikan(
        rng,
        umur=umur,
        hubungan=hubungan,
        kk_pendidikan_per_anggota=kk_pendidikan[keluarga_idx],
        kemampuan_per_anggota=kemampuan[keluarga_idx],
        adalah_kk=adalah_kk,
        jadi_pasangan=jadi_pasangan,
    )

    # -----------------------------------------------------------------
    # Kegiatan utama
    # -----------------------------------------------------------------
    status_kegiatan = np.full(total, StatusKegiatan.LAINNYA.value, dtype=np.int8)
    status_kegiatan[partisipasi == 2] = StatusKegiatan.SEKOLAH.value
    status_kegiatan[adalah_kk] = kk_status_kegiatan
    dewasa_bukan_kk = (umur >= USIA_KERJA_MIN) & ~adalah_kk & (partisipasi != 2)

    # Peluang bekerja bagi anggota dewasa selain kepala keluarga. Pasangan
    # perempuan lebih sering tercatat mengurus rumah tangga, meskipun banyak di
    # antaranya bekerja membantu usaha keluarga tanpa upah.
    peluang_kerja = np.where(
        jadi_pasangan & (jenis_kelamin == JenisKelamin.PEREMPUAN.value), 0.42, 0.66
    )
    peluang_kerja = np.where(umur >= 70, 0.16, peluang_kerja)
    bekerja = dewasa_bukan_kk & (rng.random(total) < peluang_kerja)
    status_kegiatan[bekerja] = StatusKegiatan.BEKERJA.value

    tidak_bekerja = dewasa_bukan_kk & ~bekerja
    status_kegiatan[tidak_bekerja] = np.where(
        jenis_kelamin[tidak_bekerja] == JenisKelamin.PEREMPUAN.value,
        StatusKegiatan.MENGURUS_RUMAH_TANGGA.value,
        StatusKegiatan.MENCARI_PEKERJAAN.value,
    )

    # -----------------------------------------------------------------
    # Status perkawinan
    # -----------------------------------------------------------------
    status_perkawinan = np.full(total, StatusPerkawinan.BELUM_KAWIN.value, dtype=np.int8)
    status_perkawinan[jadi_pasangan] = StatusPerkawinan.KAWIN.value

    # Kepala keluarga berstatus kawin bila keluarganya memiliki pasangan.
    # Baris kepala keluarga selalu muncul satu kali per keluarga dan berurutan,
    # sehingga posisinya dapat ditandai langsung tanpa pencarian.
    posisi_kk = np.flatnonzero(adalah_kk)
    kk_kawin = np.zeros(total, dtype=bool)
    kk_kawin[posisi_kk[_punya_pasangan(keluarga_idx, jadi_pasangan, n)]] = True
    status_perkawinan[kk_kawin] = StatusPerkawinan.KAWIN.value
    kk_tanpa_pasangan = adalah_kk & ~kk_kawin
    status_perkawinan[kk_tanpa_pasangan] = np.where(
        umur[kk_tanpa_pasangan] >= 45,
        StatusPerkawinan.CERAI_MATI.value,
        StatusPerkawinan.BELUM_KAWIN.value,
    )
    status_perkawinan[jadi_orang_tua] = np.where(
        rng.random(total)[jadi_orang_tua] < 0.55,
        StatusPerkawinan.CERAI_MATI.value,
        StatusPerkawinan.KAWIN.value,
    )

    # -----------------------------------------------------------------
    # Kesehatan
    # -----------------------------------------------------------------
    peluang_kronis = np.where(
        umur >= 55, SEBARAN.peluang_penyakit_kronis_per_dewasa * 3.2,
        np.where(umur >= 35, SEBARAN.peluang_penyakit_kronis_per_dewasa * 1.4,
                 SEBARAN.peluang_penyakit_kronis_per_dewasa * 0.25),
    )
    kena_kronis = rng.random(total) < peluang_kronis
    penyakit_kronis = np.ones(total, dtype=np.int8)  # kode 1 berarti tidak ada
    jenis_kronis = rng.choice([2, 3, 4, 5, 6, 7, 8, 9], size=total, p=[0.34, 0.19, 0.12, 0.07, 0.09, 0.05, 0.04, 0.10])
    penyakit_kronis[kena_kronis] = jenis_kronis[kena_kronis]

    kena_disabilitas = rng.random(total) < np.where(
        umur >= 65, SEBARAN.peluang_disabilitas_per_orang * 3.0, SEBARAN.peluang_disabilitas_per_orang
    )
    disabilitas = np.ones(total, dtype=np.int8)
    jenis_disabilitas = rng.choice([2, 3, 4, 5, 6, 7, 8, 9], size=total, p=[0.16, 0.13, 0.08, 0.32, 0.13, 0.06, 0.07, 0.05])
    disabilitas[kena_disabilitas] = jenis_disabilitas[kena_disabilitas]

    # Sebaran status gizi balita. Prevalensi stunting pada kelompok
    # berpenghasilan rendah jauh di atas rata-rata nasional, sehingga proporsi
    # di sini sengaja lebih tinggi daripada angka seluruh penduduk.
    balita = umur < USIA_BALITA
    gizi = np.zeros(total, dtype=np.int8)
    gizi[balita] = rng.choice([1, 2, 3, 4], size=int(balita.sum()), p=[0.78, 0.08, 0.02, 0.12])

    perempuan_subur = (jenis_kelamin == JenisKelamin.PEREMPUAN.value) & (umur >= 17) & (umur <= 45)
    hamil = perempuan_subur & (rng.random(total) < SEBARAN.peluang_hamil_per_perempuan_usia_subur)

    # Jaminan kesehatan DI LUAR jalur bantuan iuran pemerintah - yakni yang
    # ditanggung pemberi kerja atau dibayar sendiri.
    #
    # Pembedaan ini penting dan sempat keliru dirancang. Kepesertaan bantuan
    # iuran bukanlah syarat yang menuntut keluarga belum memiliki jaminan;
    # justru sebaliknya, kepesertaan itulah yang MEMBUAT keluarga miskin
    # memiliki jaminan. Sebab dan akibatnya harus lurus, sebab pemantauan hasil
    # nantinya akan menunjukkan cakupan jaminan melonjak setelah sebuah
    # keluarga ditetapkan sebagai penerima - dan itu hanya masuk akal bila
    # arahnya benar sejak pembangkitan data.
    #
    # Kepesertaan diambil pada tingkat keluarga, bukan per orang, sebab
    # pendaftaran jaminan kesehatan memang dilakukan sekeluarga sekaligus.
    formal = np.isin(
        kk_status_pekerjaan,
        [
            StatusPekerjaan.BURUH_KARYAWAN_PEGAWAI.value,
            StatusPekerjaan.BERUSAHA_DIBANTU_BURUH_TETAP.value,
        ],
    )
    peringkat = np.argsort(np.argsort(kemampuan)) / max(1, n - 1)
    peluang_jkn_keluarga = np.where(formal, 0.82, 0.55) + 0.10 * (peringkat - 0.5)
    punya_jkn_non_bantuan = rng.random(n) < np.clip(peluang_jkn_keluarga, 0.05, 0.95)
    jkn = punya_jkn_non_bantuan[keluarga_idx]

    # -----------------------------------------------------------------
    # Usaha dan dokumen
    # -----------------------------------------------------------------
    # Kepemilikan usaha hanya melekat pada anggota yang bekerja. Bagi kepala
    # keluarga, bergantung pada kedudukannya dalam pekerjaan - hanya yang
    # berusaha sendiri atau dibantu buruh tidak tetap yang tercatat memiliki
    # usaha. Bagi anggota lain, peluangnya jauh lebih kecil sebab kebanyakan
    # bekerja pada usaha milik orang lain atau membantu usaha keluarga.
    bekerja_mask = status_kegiatan == StatusKegiatan.BEKERJA.value
    kk_berusaha = np.isin(
        kk_status_pekerjaan[keluarga_idx],
        [
            StatusPekerjaan.BERUSAHA_SENDIRI.value,
            StatusPekerjaan.BERUSAHA_DIBANTU_BURUH_TIDAK_TETAP.value,
        ],
    )
    peluang_usaha = np.where(adalah_kk & kk_berusaha, 0.82, 0.0)
    peluang_usaha = np.where(~adalah_kk & bekerja_mask, 0.11, peluang_usaha)
    jumlah_usaha = np.where(
        bekerja_mask & (rng.random(total) < peluang_usaha), 1, 0
    ).astype(np.int8)

    tanpa_dokumen = rng.random(total) < PARAMETER.peluang_masalah_dokumen
    # Bayi paling sering belum memiliki akta kelahiran, sehingga peluangnya
    # ditambahkan tersendiri di luar peluang dasar.
    tanpa_dokumen |= (umur < 2) & (rng.random(total) < 0.10)

    return {
        "anggota_keluarga_idx": keluarga_idx,
        "anggota_urutan": urutan.astype(np.int16),
        "anggota_hubungan": hubungan,
        "anggota_jenis_kelamin": jenis_kelamin,
        "anggota_umur": umur,
        "anggota_pendidikan": pendidikan,
        "anggota_partisipasi_sekolah": partisipasi,
        "anggota_status_kegiatan": status_kegiatan,
        "anggota_status_perkawinan": status_perkawinan,
        "anggota_disabilitas": disabilitas,
        "anggota_penyakit_kronis": penyakit_kronis,
        "anggota_hamil": hamil,
        "anggota_gizi": gizi,
        "anggota_jkn": jkn,
        "anggota_jumlah_usaha": jumlah_usaha,
        "anggota_tanpa_dokumen": tanpa_dokumen,
    }


def _punya_pasangan(keluarga_idx: np.ndarray, jadi_pasangan: np.ndarray, n: int) -> np.ndarray:
    """Kembalikan penanda per keluarga: apakah kepala keluarganya berpasangan."""
    hitung = np.bincount(keluarga_idx[jadi_pasangan], minlength=n)
    return hitung > 0


# ---------------------------------------------------------------------------
def _bangkitkan_pendidikan(
    rng: np.random.Generator,
    *,
    umur: np.ndarray,
    hubungan: np.ndarray,
    kk_pendidikan_per_anggota: np.ndarray,
    kemampuan_per_anggota: np.ndarray,
    adalah_kk: np.ndarray,
    jadi_pasangan: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Tetapkan jenjang pendidikan tertinggi dan partisipasi sekolah.

    Anak dari keluarga berkemampuan lebih rendah memiliki peluang putus sekolah
    lebih besar. Hubungan inilah yang membuat kemiskinan berpindah antar-
    generasi, dan tanpa memasukkannya ke dalam pembangkit, penanda anak putus
    sekolah tidak akan berkaitan dengan apa pun.
    """
    total = len(umur)
    pendidikan = np.ones(total, dtype=np.int8)
    partisipasi = np.full(total, 1, dtype=np.int8)  # 1 berarti tidak pernah sekolah

    # --- Kepala keluarga ---
    pendidikan[adalah_kk] = kk_pendidikan_per_anggota[adalah_kk]
    partisipasi[adalah_kk] = 3

    # --- Pasangan: berkorelasi dengan pendidikan kepala keluarga ---
    n_pasangan = int(jadi_pasangan.sum())
    if n_pasangan:
        geser = rng.choice([-1, 0, 1], size=n_pasangan, p=[0.28, 0.5, 0.22])
        pendidikan[jadi_pasangan] = np.clip(
            kk_pendidikan_per_anggota[jadi_pasangan] + geser, 1, 8
        )
        partisipasi[jadi_pasangan] = 3

    # --- Anggota lain ---
    lain = ~adalah_kk & ~jadi_pasangan

    # Balita dan anak prasekolah.
    prasekolah = lain & (umur < USIA_SEKOLAH_MIN)
    pendidikan[prasekolah] = PendidikanTertinggi.TIDAK_SEKOLAH.value
    partisipasi[prasekolah] = 1

    # Usia sekolah: sebagian putus sekolah, dengan peluang bergantung
    # kemampuan ekonomi keluarga.
    usia_sekolah = lain & (umur >= USIA_SEKOLAH_MIN) & (umur <= USIA_SEKOLAH_MAKS)
    peringkat_kemampuan = kemampuan_per_anggota - np.median(kemampuan_per_anggota)
    peluang_putus = np.clip(0.085 - 0.16 * peringkat_kemampuan, 0.012, 0.34)
    # Risiko putus sekolah melonjak pada peralihan jenjang, terutama setelah SMP.
    peluang_putus = np.where(umur >= 16, peluang_putus * 2.4, peluang_putus)
    putus = usia_sekolah & (rng.random(total) < peluang_putus)

    masih_sekolah = usia_sekolah & ~putus
    partisipasi[masih_sekolah] = 2
    partisipasi[putus] = 3

    jenjang_menurut_umur = np.select(
        [umur < 13, umur < 16, umur <= 18],
        [PendidikanTertinggi.SD.value, PendidikanTertinggi.SMP.value, PendidikanTertinggi.SMA.value],
        default=PendidikanTertinggi.SMA.value,
    )
    # Yang masih bersekolah baru menamatkan jenjang sebelumnya.
    pendidikan[masih_sekolah] = np.clip(jenjang_menurut_umur[masih_sekolah] - 1, 1, 8)
    pendidikan[putus] = np.clip(jenjang_menurut_umur[putus] - 1, 1, 8)

    # Anggota dewasa selain kepala keluarga dan pasangan.
    dewasa_lain = lain & (umur > USIA_SEKOLAH_MAKS)
    n_dewasa = int(dewasa_lain.sum())
    if n_dewasa:
        # Anggota lanjut usia berpendidikan jauh lebih rendah, mencerminkan
        # perluasan akses pendidikan yang baru terjadi belakangan.
        lansia_mask = dewasa_lain & (umur >= USIA_LANSIA)
        muda_mask = dewasa_lain & (umur < USIA_LANSIA)
        pendidikan[lansia_mask] = rng.choice(
            [1, 2, 3, 4, 5], size=int(lansia_mask.sum()), p=[0.14, 0.24, 0.42, 0.14, 0.06]
        )
        pendidikan[muda_mask] = rng.choice(
            [2, 3, 4, 5, 6, 7], size=int(muda_mask.sum()), p=[0.05, 0.19, 0.29, 0.39, 0.04, 0.04]
        )
        partisipasi[dewasa_lain] = 3

    return pendidikan, partisipasi


# ---------------------------------------------------------------------------
def _ringkas_anggota(
    anggota: dict[str, np.ndarray], n: int, jumlah_anggota: np.ndarray
) -> dict[str, np.ndarray]:
    """Ringkas ciri anggota menjadi angka tingkat keluarga."""
    idx = anggota["anggota_keluarga_idx"]
    umur = anggota["anggota_umur"]

    def hitung(penanda: np.ndarray) -> np.ndarray:
        return np.bincount(idx[penanda], minlength=n).astype(np.int16)

    def jumlahkan(nilai: np.ndarray) -> np.ndarray:
        return np.bincount(idx, weights=nilai, minlength=n)

    jumlah_balita = hitung(umur < USIA_BALITA)
    jumlah_anak_sekolah = hitung((umur >= USIA_SEKOLAH_MIN) & (umur <= USIA_SEKOLAH_MAKS))
    jumlah_lansia = hitung(umur >= USIA_LANSIA)
    jumlah_disabilitas = hitung(anggota["anggota_disabilitas"] > 1)
    jumlah_bekerja = hitung(anggota["anggota_status_kegiatan"] == StatusKegiatan.BEKERJA.value)
    jumlah_ber_jkn = hitung(anggota["anggota_jkn"])
    jumlah_ibu_hamil = hitung(anggota["anggota_hamil"])
    jumlah_tanpa_dokumen = hitung(anggota["anggota_tanpa_dokumen"])
    jumlah_usaha = jumlahkan(anggota["anggota_jumlah_usaha"].astype(float)).astype(np.int16)

    ada_kronis = hitung(anggota["anggota_penyakit_kronis"] > 1) > 0
    ada_gizi = hitung(np.isin(anggota["anggota_gizi"], [2, 3, 4])) > 0

    tahun_sekolah_peta = np.array(
        [0] + [PendidikanTertinggi(k).tahun_sekolah for k in range(1, 9)]
    )
    dewasa = umur >= 18
    tahun_dewasa = np.where(dewasa, tahun_sekolah_peta[anggota["anggota_pendidikan"]], 0.0)
    jumlah_dewasa = np.maximum(hitung(dewasa), 1)
    rata_sekolah = jumlahkan(tahun_dewasa) / jumlah_dewasa

    return {
        "jumlah_balita": jumlah_balita,
        "jumlah_anak_sekolah": jumlah_anak_sekolah,
        "jumlah_lansia": jumlah_lansia,
        "jumlah_disabilitas": jumlah_disabilitas,
        "jumlah_bekerja": jumlah_bekerja,
        "jumlah_ber_jkn": jumlah_ber_jkn,
        "jumlah_ibu_hamil": jumlah_ibu_hamil,
        "jumlah_tanpa_dokumen": jumlah_tanpa_dokumen,
        "jumlah_usaha_keluarga": jumlah_usaha,
        "ada_penyakit_kronis": ada_kronis,
        "ada_gizi_bermasalah": ada_gizi,
        "rata_lama_sekolah_dewasa": rata_sekolah,
    }


__all__ = ["PopulasiSintetis", "bangkitkan_populasi"]
