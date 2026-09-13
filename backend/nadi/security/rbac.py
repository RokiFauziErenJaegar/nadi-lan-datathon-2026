"""Peran, kewenangan, dan cakupan data.

Proposal NADI menyebut "akses berbasis peran" sebagai mitigasi risiko privasi.
Modul ini menerjemahkannya menjadi aturan yang dapat diperiksa mesin.

Dua lapis kendali yang berbeda dan sama-sama diperlukan:

**Kewenangan** (:class:`Kewenangan`) menjawab *tindakan apa* yang boleh
dilakukan seorang pengguna - membaca antrean, memverifikasi kasus, mencatat
intervensi, melatih ulang model.

**Cakupan data** (:class:`CakupanData`) menjawab *baris mana* yang boleh ia
lihat. Inilah yang mencegah seorang kepala daerah menelusuri satu keluarga
tertentu tanpa keperluan operasional, dan mencegah petugas satu dinas membaca
kasus milik dinas lain.

Keduanya dipisah dengan sengaja. Kewenangan yang sama dapat berlaku pada
cakupan yang berbeda: seorang perencana di Bappeda boleh membaca seluruh
wilayah namun hanya dalam bentuk agregat, sementara petugas Dinas Sosial boleh
membuka satu keluarga namun hanya di wilayah penugasannya.
"""

from __future__ import annotations

from enum import Enum
from typing import Iterable


class Peran(str, Enum):
    """Peran pengguna, dipetakan dari tabel Target Pengguna pada proposal."""

    ADMIN = "admin"
    PIMPINAN = "pimpinan"          # Bupati / Sekretaris Daerah
    PERENCANA = "perencana"        # Bappeda
    DINAS_SOSIAL = "dinas_sosial"  # Dinas Sosial - pemilik proses verifikasi
    OPD_PELAKSANA = "opd_pelaksana"  # OPD sektoral pelaksana intervensi
    VERIFIKATOR = "verifikator"    # Petugas lapangan / operator pekon

    @property
    def label(self) -> str:
        return {
            Peran.ADMIN: "Administrator Sistem",
            Peran.PIMPINAN: "Pimpinan Daerah (Bupati/Sekda)",
            Peran.PERENCANA: "Perencana (Bappeda)",
            Peran.DINAS_SOSIAL: "Dinas Sosial",
            Peran.OPD_PELAKSANA: "OPD Pelaksana Intervensi",
            Peran.VERIFIKATOR: "Verifikator Lapangan",
        }[self]

    @property
    def deskripsi(self) -> str:
        return {
            Peran.ADMIN: "Mengelola pengguna, katalog program, dan siklus hidup model.",
            Peran.PIMPINAN: "Memantau kondisi kabupaten dan menimbang skenario kebijakan.",
            Peran.PERENCANA: "Menganalisis wilayah, menyusun rencana, dan mengevaluasi hasil.",
            Peran.DINAS_SOSIAL: "Mengelola antrean verifikasi dan penetapan sasaran.",
            Peran.OPD_PELAKSANA: "Menerima penugasan dan mencatat pelaksanaan intervensi.",
            Peran.VERIFIKATOR: "Memeriksa kondisi keluarga di lapangan dan melaporkan hasilnya.",
        }[self]


class Kewenangan(str, Enum):
    """Tindakan yang dapat dilindungi secara terpisah."""

    # --- Membaca ---
    BACA_AGREGAT = "baca:agregat"
    BACA_PETA = "baca:peta"
    BACA_KELUARGA = "baca:keluarga"
    BACA_ANTREAN = "baca:antrean"
    BACA_REKOMENDASI = "baca:rekomendasi"
    BACA_OUTCOME = "baca:outcome"
    BACA_JEJAK_AUDIT = "baca:jejak_audit"

    # --- Alur kerja ---
    VERIFIKASI_KASUS = "tulis:verifikasi"
    TUGASKAN_KASUS = "tulis:penugasan"
    CATAT_INTERVENSI = "tulis:intervensi"
    CATAT_OUTCOME = "tulis:outcome"

    # --- Analitik ---
    JALANKAN_SIMULASI = "jalankan:simulasi"
    GUNAKAN_COPILOT = "jalankan:copilot"
    EKSPOR_DATA = "jalankan:ekspor"

    # --- Administrasi ---
    KELOLA_PROGRAM = "admin:program"
    KELOLA_PENGGUNA = "admin:pengguna"
    KELOLA_MODEL = "admin:model"
    # Menyunting konfigurasi layanan luar - alamat, kunci, model. Dipisahkan
    # dari KELOLA_MODEL karena keduanya menyangkut hal yang sama sekali
    # berbeda: yang satu model prediksi kerentanan milik sendiri, yang lain
    # kunci berbayar milik pihak ketiga. Hanya administrator sistem.
    KELOLA_SISTEM = "admin:sistem"


class CakupanData(str, Enum):
    """Seberapa dalam seorang pengguna boleh melihat data."""

    AGREGAT_SAJA = "agregat_saja"
    """Hanya angka gabungan tingkat wilayah. Baris keluarga tidak dapat dibuka.

    Ambang penyembunyian sel kecil tetap berlaku - lihat
    :data:`AMBANG_SEL_KECIL`.
    """

    WILAYAH_TERTUGAS = "wilayah_tertugas"
    """Baris keluarga dapat dibuka, tetapi hanya di wilayah penugasan."""

    SELURUH_KABUPATEN = "seluruh_kabupaten"
    """Baris keluarga di seluruh kabupaten dapat dibuka."""


#: Jumlah minimum keluarga dalam satu sel agregat sebelum angkanya ditampilkan.
#: Di bawah ambang ini, satu titik pada peta dapat menunjuk satu rumah tertentu,
#: sehingga agregat berubah menjadi pengungkapan data pribadi.
AMBANG_SEL_KECIL: int = 10


# ---------------------------------------------------------------------------
# Matriks kewenangan
# ---------------------------------------------------------------------------
_BACA_UMUM = {
    Kewenangan.BACA_AGREGAT,
    Kewenangan.BACA_PETA,
    Kewenangan.BACA_OUTCOME,
}

MATRIKS_KEWENANGAN: dict[Peran, frozenset[Kewenangan]] = {
    Peran.ADMIN: frozenset(Kewenangan),
    Peran.PIMPINAN: frozenset(
        _BACA_UMUM
        | {
            Kewenangan.JALANKAN_SIMULASI,
            Kewenangan.GUNAKAN_COPILOT,
        }
    ),
    Peran.PERENCANA: frozenset(
        _BACA_UMUM
        | {
            Kewenangan.BACA_REKOMENDASI,
            Kewenangan.JALANKAN_SIMULASI,
            Kewenangan.GUNAKAN_COPILOT,
            Kewenangan.EKSPOR_DATA,
        }
    ),
    Peran.DINAS_SOSIAL: frozenset(
        _BACA_UMUM
        | {
            Kewenangan.BACA_KELUARGA,
            Kewenangan.BACA_ANTREAN,
            Kewenangan.BACA_REKOMENDASI,
            Kewenangan.BACA_JEJAK_AUDIT,
            Kewenangan.VERIFIKASI_KASUS,
            Kewenangan.TUGASKAN_KASUS,
            Kewenangan.CATAT_OUTCOME,
            Kewenangan.JALANKAN_SIMULASI,
            Kewenangan.GUNAKAN_COPILOT,
            Kewenangan.EKSPOR_DATA,
        }
    ),
    Peran.OPD_PELAKSANA: frozenset(
        _BACA_UMUM
        | {
            Kewenangan.BACA_KELUARGA,
            Kewenangan.BACA_ANTREAN,
            Kewenangan.BACA_REKOMENDASI,
            Kewenangan.CATAT_INTERVENSI,
            # CATAT_OUTCOME sengaja TIDAK diberikan kepada OPD pelaksana.
            #
            # Pelaksana mencatat apa yang ia salurkan; penilaian atas hasilnya
            # jatuh ke Dinas Sosial sebagai pengoordinasi. Membiarkan keduanya
            # pada satu tangan berarti membiarkan pelaksana menilai
            # pekerjaannya sendiri - dan angka monitoring yang dihasilkannya
            # tidak lagi berarti apa-apa bagi pimpinan yang membacanya.
            #
            # Pemisahan ini menutup satu-satunya celah pada matriks kewenangan
            # yang dapat membuat laporan capaian memoles dirinya sendiri.
            Kewenangan.GUNAKAN_COPILOT,
        }
    ),
    Peran.VERIFIKATOR: frozenset(
        {
            Kewenangan.BACA_AGREGAT,
            # Petugas lapangan memerlukan peta untuk menyusun rute kunjungan.
            # Cakupan datanya tetap terbatas pada wilayah penugasan.
            Kewenangan.BACA_PETA,
            Kewenangan.BACA_KELUARGA,
            Kewenangan.BACA_ANTREAN,
            Kewenangan.BACA_REKOMENDASI,
            Kewenangan.VERIFIKASI_KASUS,
        }
    ),
}

CAKUPAN_BAWAAN: dict[Peran, CakupanData] = {
    Peran.ADMIN: CakupanData.SELURUH_KABUPATEN,
    # Pimpinan dan perencana sengaja dibatasi pada agregat. Keduanya tidak
    # memerlukan identitas keluarga untuk menjalankan tugasnya, dan membatasi
    # akses di sini menutup jalur penyalahgunaan yang paling sulit dideteksi.
    Peran.PIMPINAN: CakupanData.AGREGAT_SAJA,
    Peran.PERENCANA: CakupanData.AGREGAT_SAJA,
    Peran.DINAS_SOSIAL: CakupanData.SELURUH_KABUPATEN,
    Peran.OPD_PELAKSANA: CakupanData.WILAYAH_TERTUGAS,
    Peran.VERIFIKATOR: CakupanData.WILAYAH_TERTUGAS,
}


# ---------------------------------------------------------------------------
# Pemeriksaan
# ---------------------------------------------------------------------------
def kewenangan_peran(peran: Peran) -> frozenset[Kewenangan]:
    """Kembalikan seluruh kewenangan yang melekat pada sebuah peran."""
    return MATRIKS_KEWENANGAN.get(peran, frozenset())


def berwenang(peran: Peran, kewenangan: Kewenangan) -> bool:
    """Periksa apakah peran memiliki satu kewenangan tertentu."""
    return kewenangan in kewenangan_peran(peran)


def berwenang_semua(peran: Peran, kewenangan: Iterable[Kewenangan]) -> bool:
    """Periksa apakah peran memiliki seluruh kewenangan yang diminta."""
    dimiliki = kewenangan_peran(peran)
    return all(k in dimiliki for k in kewenangan)


def cakupan_peran(peran: Peran) -> CakupanData:
    """Cakupan data bawaan bagi sebuah peran."""
    return CAKUPAN_BAWAAN.get(peran, CakupanData.AGREGAT_SAJA)


def boleh_buka_keluarga(peran: Peran) -> bool:
    """Apakah peran ini boleh membuka baris satu keluarga."""
    return (
        berwenang(peran, Kewenangan.BACA_KELUARGA)
        and cakupan_peran(peran) is not CakupanData.AGREGAT_SAJA
    )


class AksesDitolak(PermissionError):
    """Diangkat saat pengguna mencoba tindakan di luar kewenangannya."""

    def __init__(self, peran: Peran, kewenangan: Kewenangan) -> None:
        self.peran = peran
        self.kewenangan = kewenangan
        super().__init__(
            f"Peran '{peran.label}' tidak memiliki kewenangan '{kewenangan.value}'."
        )


def wajib_berwenang(peran: Peran, kewenangan: Kewenangan) -> None:
    """Angkat :class:`AksesDitolak` bila kewenangan tidak dimiliki."""
    if not berwenang(peran, kewenangan):
        raise AksesDitolak(peran, kewenangan)


def ringkasan_matriks() -> list[dict[str, object]]:
    """Bentuk matriks kewenangan yang dapat ditampilkan di antarmuka.

    Menampilkan aturan akses secara terbuka kepada pengguna adalah bagian dari
    akuntabilitas: setiap orang dapat melihat apa yang boleh dilihat orang lain.
    """
    return [
        {
            "peran": peran.value,
            "label": peran.label,
            "deskripsi": peran.deskripsi,
            "cakupan_data": cakupan_peran(peran).value,
            "boleh_buka_keluarga": boleh_buka_keluarga(peran),
            "kewenangan": sorted(k.value for k in kewenangan_peran(peran)),
        }
        for peran in Peran
    ]


__all__ = [
    "AMBANG_SEL_KECIL",
    "AksesDitolak",
    "CAKUPAN_BAWAAN",
    "CakupanData",
    "Kewenangan",
    "MATRIKS_KEWENANGAN",
    "Peran",
    "berwenang",
    "berwenang_semua",
    "boleh_buka_keluarga",
    "cakupan_peran",
    "kewenangan_peran",
    "ringkasan_matriks",
    "wajib_berwenang",
]
