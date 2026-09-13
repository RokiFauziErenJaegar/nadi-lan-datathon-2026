"""Penyuntingan konfigurasi saat aplikasi sedang berjalan.

Modul ini menangani satu hal yang kelihatannya sederhana namun mudah salah:
mengubah pengaturan layanan AI dari dalam aplikasi, tanpa mematikannya.

**Mengapa kunci API tidak disimpan di basis data.** Berkas ``data/nadi.db``
berukuran ratusan megabita dan memang dimaksudkan untuk disalin - ke laptop
lain, ke berkas cadangan, ke panitia lomba. Menaruh rahasia di dalamnya berarti
menyebarkannya bersama setiap salinan itu. Menyimpannya terenkripsi akan
menjawab keberatan tersebut, namun proyek ini tidak memasang pustaka
kriptografi, dan menggulung sendiri penyandian rahasia adalah kesalahan yang
jauh lebih besar daripada masalah yang hendak dipecahkan. Maka kunci tetap
tinggal di ``.env`` - satu berkas, di luar basis data, yang memang sudah
menjadi tempat rahasia sejak awal.

**Mengapa berkasnya ditulis secara atomik.** Penyuntingan langsung akan
menyisakan ``.env`` yang terpotong bila proses berhenti di tengah penulisan -
dan berkas itulah yang memuat ``NADI_SECRET_KEY``. Kehilangannya membuat
seluruh token masuk tidak sah dan seluruh kode semu berubah. Karena itu berkas
baru ditulis lengkap lebih dahulu, baru menggantikan yang lama dalam satu
langkah yang tidak dapat setengah jadi.

**Mengapa pengaturan di memori ikut diperbarui.** Membaca ulang ``.env`` saja
tidak cukup: seluruh modul sudah memegang rujukan ke objek ``settings`` yang
sama. Nilainya diubah di tempat, lalu penyedia AI dibangun ulang, sehingga
permintaan berikutnya langsung memakai pengaturan baru tanpa menyalakan ulang
peladen.
"""

from __future__ import annotations

import logging
import os
import re
import tempfile
from pathlib import Path

from nadi.config import PROJECT_ROOT, settings

logger = logging.getLogger("nadi.config")

BERKAS_ENV = PROJECT_ROOT / ".env"
CONTOH_ENV = PROJECT_ROOT / ".env.example"

_POLA_BARIS = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=")

# Bidang yang boleh disunting lewat antarmuka. Daftar putih, bukan daftar
# hitam: sebuah permintaan HTTP tidak boleh dapat menyentuh NADI_SECRET_KEY
# atau NADI_DATABASE_URL, betapapun bentuk badan permintaannya.
BIDANG_BOLEH_DIUBAH: frozenset[str] = frozenset(
    {
        "NADI_LLM_ENABLED",
        "NADI_LLM_BASE_URL",
        "NADI_LLM_API_KEY",
        "NADI_LLM_MODEL",
        "NADI_LLM_MAX_TOKENS",
        "NADI_LLM_TEMPERATURE",
        "NADI_LLM_TIMEOUT_SECONDS",
        "NADI_LLM_BLOCK_PII",
    }
)

# Peta dari nama variabel lingkungan ke nama bidang pada objek pengaturan,
# beserta cara mengubah untai menjadi jenis yang benar.
_PETA_SETTINGS: dict[str, tuple[str, type]] = {
    "NADI_LLM_ENABLED": ("llm_enabled", bool),
    "NADI_LLM_BASE_URL": ("llm_base_url", str),
    "NADI_LLM_API_KEY": ("llm_api_key", str),
    "NADI_LLM_MODEL": ("llm_model", str),
    "NADI_LLM_MAX_TOKENS": ("llm_max_tokens", int),
    "NADI_LLM_TEMPERATURE": ("llm_temperature", float),
    "NADI_LLM_TIMEOUT_SECONDS": ("llm_timeout_seconds", float),
    "NADI_LLM_BLOCK_PII": ("llm_block_pii", bool),
}


class PengaturanDitolak(ValueError):
    """Diangkat bila permintaan menyentuh bidang yang tidak boleh diubah."""


def _ke_untai(nilai: object) -> str:
    if isinstance(nilai, bool):
        return "true" if nilai else "false"
    return str(nilai)


def _dari_untai(teks: str, jenis: type):
    if jenis is bool:
        return teks.strip().lower() in {"1", "true", "yes", "ya", "on"}
    if jenis is int:
        return int(float(teks))
    if jenis is float:
        return float(teks)
    return teks


def tulis_env(nilai: dict[str, object]) -> list[str]:
    """Perbarui variabel tertentu pada ``.env``, sisanya dibiarkan utuh.

    Kembalikan daftar nama variabel yang benar-benar berubah nilainya.
    """
    asing = sorted(set(nilai) - BIDANG_BOLEH_DIUBAH)
    if asing:
        raise PengaturanDitolak(f"Bidang tidak boleh diubah lewat antarmuka: {', '.join(asing)}")

    if not BERKAS_ENV.exists():
        if not CONTOH_ENV.exists():
            raise PengaturanDitolak("Berkas .env tidak ada dan tidak ada contohnya.")
        BERKAS_ENV.write_text(CONTOH_ENV.read_text(encoding="utf-8"), encoding="utf-8")

    baris = BERKAS_ENV.read_text(encoding="utf-8").splitlines()
    tersisa = {k: _ke_untai(v) for k, v in nilai.items()}
    berubah: list[str] = []

    for i, isi in enumerate(baris):
        cocok = _POLA_BARIS.match(isi)
        if cocok and cocok.group(1) in tersisa:
            kunci = cocok.group(1)
            baru = f"{kunci}={tersisa.pop(kunci)}"
            if baru != isi:
                baris[i] = baru
                berubah.append(kunci)

    for kunci, isi in tersisa.items():
        baris.append(f"{kunci}={isi}")
        berubah.append(kunci)

    _tulis_atomik("\n".join(baris) + "\n")
    return berubah


def _tulis_atomik(isi: str) -> None:
    """Tulis .env lengkap lebih dahulu, baru gantikan yang lama.

    ``os.replace`` bersifat atomik selama berkas sementara berada pada volume
    yang sama, sehingga berkas dituliskan di direktori yang sama dengan
    tujuannya - bukan di direktori sementara sistem.
    """
    direktori = BERKAS_ENV.parent
    fd, sementara = tempfile.mkstemp(dir=str(direktori), prefix=".env.", suffix=".baru")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            f.write(isi)
            f.flush()
            os.fsync(f.fileno())
        os.replace(sementara, BERKAS_ENV)
    except BaseException:
        Path(sementara).unlink(missing_ok=True)
        raise


def terapkan_ke_memori(nilai: dict[str, object]) -> list[str]:
    """Ubah objek pengaturan di tempat agar berlaku tanpa menyalakan ulang."""
    diterapkan: list[str] = []
    for kunci, isi in nilai.items():
        pasangan = _PETA_SETTINGS.get(kunci)
        if pasangan is None:
            continue
        bidang, jenis = pasangan
        setattr(settings, bidang, _dari_untai(_ke_untai(isi), jenis))
        diterapkan.append(bidang)
    return diterapkan


async def simpan_konfigurasi_ai(nilai: dict[str, object]) -> dict:
    """Simpan pengaturan layanan AI, terapkan, lalu bangun ulang penyedianya."""
    from nadi.ai.provider import tutup_penyedia  # noqa: PLC0415 - hindari impor melingkar

    berubah = tulis_env(nilai)
    diterapkan = terapkan_ke_memori(nilai)

    # Penyedia lama memegang klien HTTP dengan tajuk Authorization yang sudah
    # usang. Ia ditutup supaya sambungannya dilepas, lalu dibangun ulang saat
    # permintaan berikutnya datang.
    await tutup_penyedia()

    logger.info("Pengaturan layanan AI diperbarui: %s", ", ".join(berubah) or "(tidak ada perubahan)")
    return {"berubah": berubah, "diterapkan": diterapkan}


def samarkan(rahasia: str | None) -> str | None:
    """Tampilkan bentuk kunci tanpa membocorkan isinya."""
    k = (rahasia or "").strip()
    if not k or k.startswith("isi-api-key"):
        return None
    if len(k) <= 12:
        return "*" * len(k)
    return f"{k[:6]}...{k[-4:]}"


__all__ = [
    "BIDANG_BOLEH_DIUBAH",
    "PengaturanDitolak",
    "samarkan",
    "simpan_konfigurasi_ai",
    "terapkan_ke_memori",
    "tulis_env",
]
