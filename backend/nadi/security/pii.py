"""Penjaga data pribadi (PII guard).

Proposal NADI berjanji bahwa NIK dan data mentah keluarga **tidak pernah**
dikirim ke layanan LLM eksternal. Modul ini mengubah janji tersebut menjadi
penghalang teknis: setiap muatan yang akan meninggalkan server melewati
pemindaian di sini, dan permintaan ditolak bila terdeteksi pengenal pribadi.

Pertahanan dirancang berlapis dua:

1. **Struktural (utama)** - pembangun konteks hanya menyalin bidang dari
   daftar-izin eksplisit; nama, NIK, dan alamat tidak pernah masuk.
   Lihat :mod:`nadi.ai.context`.
2. **Pemindaian pola (jaring pengaman)** - modul ini. Berjalan tepat sebelum
   permintaan HTTP dikirim, sehingga kekeliruan pemrograman di lapisan mana pun
   tetap tertahan.

Prinsip yang dianut: lebih baik menolak permintaan yang sebenarnya aman
(positif palsu) daripada meloloskan satu NIK.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class PIIKind(str, Enum):
    """Jenis pengenal pribadi yang dikenali."""

    NIK_ATAU_KK = "nik_atau_kk"  # Nomor Induk Kependudukan / Kartu Keluarga (16 digit)
    NPWP = "npwp"  # Nomor Pokok Wajib Pajak
    BPJS_KIS = "bpjs_kis"  # Nomor kepesertaan BPJS/KIS (13 digit)
    NOMOR_TELEPON = "nomor_telepon"
    SUREL = "surel"
    RT_RW = "rt_rw"  # Alamat granular tingkat rukun tetangga
    DERET_ANGKA_PANJANG = "deret_angka_panjang"
    KOORDINAT_PRESISI = "koordinat_presisi"
    KUNCI_TERLARANG = "kunci_terlarang"


# ---------------------------------------------------------------------------
# Pola pengenal
# ---------------------------------------------------------------------------
# NIK dan nomor KK sama-sama 16 digit sehingga tidak dibedakan di sini.
#
# Dua bentuk yang dikenali: enam belas digit rapat, dan empat kelompok empat
# digit yang dipisah titik atau strip - dua cara paling lazim petugas
# mengetikkan NIK. Spasi sengaja TIDAK diterima sebagai pemisah: deret angka
# beruas spasi hampir selalu berupa data tabel (misalnya rangkaian tahun
# "2020 2021 2022 2023") dan menerimanya akan memblokir kueri tren yang sah.
_PATTERNS: list[tuple[PIIKind, re.Pattern[str]]] = [
    # NPWP diperiksa lebih dulu karena berformat khas dan mudah dikenali.
    (
        PIIKind.NPWP,
        re.compile(r"\b\d{2}\.\d{3}\.\d{3}\.\d-\d{3}\.\d{3}\b"),
    ),
    (
        # Enam belas digit rapat. Lookbehind ``(?<!\d\.)`` mencegah bagian
        # pecahan bilangan desimal panjang (misalnya 0.1234567890123456 yang
        # lazim keluar dari perhitungan numerik) ikut tertangkap, sementara
        # bentuk "no.1871234567890123" tetap terdeteksi.
        PIIKind.NIK_ATAU_KK,
        re.compile(r"(?<!\d)(?<!\d\.)\d{16}(?!\d)"),
    ),
    (
        PIIKind.NIK_ATAU_KK,
        re.compile(r"(?<!\d)\d{4}[.\-]\d{4}[.\-]\d{4}[.\-]\d{4}(?!\d)"),
    ),
    (
        PIIKind.BPJS_KIS,
        re.compile(r"(?<!\d)(?<!\d\.)\d{13}(?!\d)"),
    ),
    (
        PIIKind.NOMOR_TELEPON,
        re.compile(r"(?<!\d)(?:\+?62|0)8[1-9]\d{6,11}(?!\d)"),
    ),
    (
        PIIKind.SUREL,
        re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]{2,}"),
    ),
    (
        PIIKind.RT_RW,
        re.compile(r"\bRT\.?\s*\d{1,3}\b.{0,12}\bRW\.?\s*\d{1,3}\b", re.IGNORECASE),
    ),
    (
        # Titik koordinat dengan lima angka desimal atau lebih setara presisi
        # meteran - cukup untuk menunjuk satu rumah. Agregat wilayah selalu
        # dibulatkan sebelum dikirim keluar.
        PIIKind.KOORDINAT_PRESISI,
        re.compile(r"(?<![\d.])-?\d{1,3}\.\d{5,}\s*,\s*-?\d{1,3}\.\d{5,}(?![\d.])"),
    ),
    (
        PIIKind.DERET_ANGKA_PANJANG,
        re.compile(r"(?<!\d)\d{17,}(?!\d)"),
    ),
]

# Nama kunci JSON yang dilarang muncul dalam muatan keluar, apa pun isinya.
# Kehadiran kunci ini menandakan kebocoran struktural walaupun nilainya
# kebetulan lolos dari seluruh pola di atas.
FORBIDDEN_KEYS: frozenset[str] = frozenset(
    {
        "nik",
        "no_nik",
        "nomor_nik",
        "nik_kepala_keluarga",
        "no_kk",
        "nomor_kk",
        "kk",
        "nama",
        "nama_lengkap",
        "nama_kepala_keluarga",
        "nama_individu",
        "nama_anggota",
        "alamat",
        "alamat_lengkap",
        "jalan",
        "rt",
        "rw",
        "npwp",
        "no_bpjs",
        "nomor_bpjs",
        "no_kks",
        "nomor_rekening",
        "telepon",
        "no_hp",
        "email",
        "tanggal_lahir",
        "tempat_lahir",
        "latitude",
        "longitude",
        "lat",
        "lon",
        "lng",
    }
)


@dataclass(frozen=True)
class PIIFinding:
    """Satu temuan pengenal pribadi. Nilai mentah sengaja tidak disimpan."""

    kind: PIIKind
    lokasi: str
    contoh_tersamar: str

    def __str__(self) -> str:  # pragma: no cover - hanya untuk pesan galat
        return f"{self.kind.value} pada {self.lokasi} ({self.contoh_tersamar})"


@dataclass
class PIIScanResult:
    """Hasil pemindaian sebuah muatan."""

    temuan: list[PIIFinding] = field(default_factory=list)

    @property
    def bersih(self) -> bool:
        return not self.temuan

    def ringkas(self) -> str:
        if self.bersih:
            return "bersih"
        jenis = sorted({t.kind.value for t in self.temuan})
        return f"{len(self.temuan)} temuan: {', '.join(jenis)}"


class PIILeakError(RuntimeError):
    """Diangkat saat muatan yang akan keluar mengandung pengenal pribadi."""

    def __init__(self, hasil: PIIScanResult) -> None:
        self.hasil = hasil
        rincian = "\n  - ".join(str(t) for t in hasil.temuan)
        super().__init__(
            "Permintaan ke layanan AI eksternal DIBATALKAN karena terdeteksi "
            "pengenal pribadi.\n  - " + rincian + "\n"
            "Perbaiki pembangun konteks agar hanya mengirim atribut non-identitas."
        )


# ---------------------------------------------------------------------------
# Penyamaran nilai
# ---------------------------------------------------------------------------
def samarkan_nilai(nilai: object, sisa_depan: int = 2, sisa_belakang: int = 2) -> str:
    """Kembalikan bentuk tersamar sebuah nilai untuk keperluan log.

    Nilai asli tidak boleh pernah ditulis ke berkas log maupun pesan galat.
    """
    teks = str(nilai)
    if len(teks) <= sisa_depan + sisa_belakang:
        return "*" * len(teks)
    tengah = "*" * (len(teks) - sisa_depan - sisa_belakang)
    return teks[:sisa_depan] + tengah + teks[-sisa_belakang:]


# ---------------------------------------------------------------------------
# Pemindaian
# ---------------------------------------------------------------------------
def pindai_teks(teks: str, lokasi: str = "teks") -> list[PIIFinding]:
    """Pindai satu untai teks terhadap seluruh pola pengenal pribadi."""
    temuan: list[PIIFinding] = []
    for kind, pola in _PATTERNS:
        for m in pola.finditer(teks):
            temuan.append(
                PIIFinding(
                    kind=kind,
                    lokasi=lokasi,
                    contoh_tersamar=samarkan_nilai(m.group(0)),
                )
            )
    return temuan


def _jenis_untuk_kunci(kunci_norm: str) -> PIIKind:
    if "nik" in kunci_norm or kunci_norm.endswith("kk") or "kartu_keluarga" in kunci_norm:
        return PIIKind.NIK_ATAU_KK
    if "email" in kunci_norm or "surel" in kunci_norm:
        return PIIKind.SUREL
    if "telepon" in kunci_norm or "hp" in kunci_norm:
        return PIIKind.NOMOR_TELEPON
    if kunci_norm in {"lat", "lon", "lng", "latitude", "longitude"}:
        return PIIKind.KOORDINAT_PRESISI
    if kunci_norm in {"rt", "rw"}:
        return PIIKind.RT_RW
    return PIIKind.KUNCI_TERLARANG


def pindai_objek(obj: Any, lokasi: str = "$") -> list[PIIFinding]:
    """Telusuri struktur bersarang (dict/list/skalar) dan pindai seluruh isinya."""
    temuan: list[PIIFinding] = []

    if isinstance(obj, dict):
        for kunci, nilai in obj.items():
            kunci_norm = str(kunci).strip().lower()
            jalur = f"{lokasi}.{kunci}"
            if kunci_norm in FORBIDDEN_KEYS:
                temuan.append(
                    PIIFinding(
                        kind=_jenis_untuk_kunci(kunci_norm),
                        lokasi=jalur,
                        contoh_tersamar=f"kunci terlarang '{kunci_norm}'",
                    )
                )
            temuan.extend(pindai_objek(nilai, jalur))

    elif isinstance(obj, (list, tuple, set)):
        for i, item in enumerate(obj):
            temuan.extend(pindai_objek(item, f"{lokasi}[{i}]"))

    elif isinstance(obj, str):
        temuan.extend(pindai_teks(obj, lokasi))

    elif isinstance(obj, (int, float)) and not isinstance(obj, bool):
        # Angka 13 atau 16 digit yang tersimpan sebagai bilangan, bukan untai.
        temuan.extend(pindai_teks(str(obj), lokasi))

    return temuan


def pindai(muatan: Any) -> PIIScanResult:
    """Titik masuk utama: pindai muatan apa pun dan kembalikan hasilnya."""
    return PIIScanResult(temuan=pindai_objek(muatan))


def pastikan_bersih(muatan: Any) -> None:
    """Angkat :class:`PIILeakError` bila muatan mengandung pengenal pribadi."""
    hasil = pindai(muatan)
    if not hasil.bersih:
        raise PIILeakError(hasil)


def redaksi_teks(teks: str, pengganti: str = "[DIREDAKSI]") -> str:
    """Ganti seluruh pengenal pribadi di dalam teks dengan penanda.

    Dipakai untuk **masukan pengguna** pada Policy Copilot: bila pengguna
    terlanjur mengetikkan NIK di kolom tanya-jawab, nilainya diganti sebelum
    apa pun dikirim keluar.
    """
    hasil = teks
    for _, pola in _PATTERNS:
        hasil = pola.sub(pengganti, hasil)
    return hasil


def ringkas_untuk_log(muatan: Any) -> str:
    """Ringkasan aman untuk audit log: ukuran dan status pemindaian saja."""
    try:
        ukuran = len(json.dumps(muatan, ensure_ascii=False, default=str))
    except (TypeError, ValueError):
        ukuran = -1
    return f"ukuran={ukuran}B status={pindai(muatan).ringkas()}"


__all__ = [
    "FORBIDDEN_KEYS",
    "PIIFinding",
    "PIIKind",
    "PIILeakError",
    "PIIScanResult",
    "pastikan_bersih",
    "pindai",
    "pindai_objek",
    "pindai_teks",
    "redaksi_teks",
    "ringkas_untuk_log",
    "samarkan_nilai",
]
