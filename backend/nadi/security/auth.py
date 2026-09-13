"""Sandi dan token akses.

Dua hal yang sering keliru diterapkan dan ditangani secara eksplisit di sini:

**Batas 72 bita pada bcrypt.** Algoritma bcrypt memotong masukan pada bita
ke-72. Sandi panjang yang berbeda setelah karakter ke-72 akan menghasilkan
cernaan yang sama - dua sandi berbeda menjadi saling menggantikan. Solusinya
adalah meringkas sandi dengan SHA-256 lebih dahulu sehingga panjang masukan
selalu tetap.

**Waktu kedaluwarsa token.** Token ditandatangani dengan kunci rahasia
aplikasi. Mengganti ``NADI_SECRET_KEY`` otomatis membatalkan seluruh sesi yang
sedang berjalan, yang merupakan jalur pencabutan darurat bila terjadi insiden.
"""

from __future__ import annotations

import base64
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt

from nadi.config import settings
from nadi.security.rbac import Peran

# Jenis token dibedakan agar token akses tidak dapat dipakai sebagai token
# penyegar, dan sebaliknya.
JENIS_AKSES = "akses"


class KredensialTidakSah(Exception):
    """Diangkat saat sandi salah atau token tidak dapat dipercaya."""


# ---------------------------------------------------------------------------
# Sandi
# ---------------------------------------------------------------------------
def _ringkas_sandi(sandi: str) -> bytes:
    """Ringkas sandi menjadi 44 bita agar batas 72 bita bcrypt tidak tersentuh.

    SHA-256 menghasilkan 32 bita; pengodean base64 menjadikannya 44 karakter
    ASCII yang aman dilewatkan ke bcrypt tanpa bita nol.
    """
    return base64.b64encode(hashlib.sha256(sandi.encode("utf-8")).digest())


def cernakan_sandi(sandi: str) -> str:
    """Hasilkan cernaan bcrypt untuk sebuah sandi."""
    if not sandi:
        raise ValueError("Sandi tidak boleh kosong.")
    return bcrypt.hashpw(_ringkas_sandi(sandi), bcrypt.gensalt(rounds=12)).decode("ascii")


def sandi_cocok(sandi: str, cernaan: str) -> bool:
    """Periksa sandi terhadap cernaan tersimpan, tahan terhadap serangan waktu."""
    if not sandi or not cernaan:
        return False
    try:
        return bcrypt.checkpw(_ringkas_sandi(sandi), cernaan.encode("ascii"))
    except (ValueError, TypeError):
        # Cernaan rusak atau berformat lama - diperlakukan sebagai tidak cocok.
        return False


def sandi_acak(panjang: int = 14) -> str:
    """Bentuk sandi acak yang mudah dibaca, untuk penyemaian akun demo."""
    abjad = "abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return "".join(secrets.choice(abjad) for _ in range(panjang))


def kekuatan_sandi(sandi: str) -> tuple[bool, str]:
    """Periksa kelayakan sandi. Kembalikan status dan alasannya."""
    if len(sandi) < 12:
        return False, "Sandi minimal 12 karakter."
    jenis = sum(
        [
            any(c.islower() for c in sandi),
            any(c.isupper() for c in sandi),
            any(c.isdigit() for c in sandi),
            any(not c.isalnum() for c in sandi),
        ]
    )
    if jenis < 3:
        return False, "Sandi harus memuat minimal tiga dari: huruf kecil, huruf besar, angka, simbol."
    return True, "Sandi memenuhi syarat."


# ---------------------------------------------------------------------------
# Token akses
# ---------------------------------------------------------------------------
def terbitkan_token(
    *,
    id_pengguna: int,
    nama_pengguna: str,
    peran: Peran,
    id_opd: int | None = None,
    kode_wilayah: list[str] | None = None,
    berlaku_menit: int | None = None,
) -> tuple[str, datetime]:
    """Terbitkan token akses dan kembalikan token beserta waktu kedaluwarsanya.

    Klaim ``opd`` dan ``wilayah`` dibawa di dalam token agar pembatasan cakupan
    data dapat ditegakkan tanpa membaca basis data pada setiap permintaan.
    """
    menit = berlaku_menit or settings.access_token_minutes
    terbit = datetime.now(timezone.utc)
    kedaluwarsa = terbit + timedelta(minutes=menit)

    klaim: dict[str, Any] = {
        "sub": str(id_pengguna),
        "nama": nama_pengguna,
        "peran": peran.value,
        "opd": id_opd,
        "wilayah": kode_wilayah or [],
        "jenis": JENIS_AKSES,
        "iat": int(terbit.timestamp()),
        "exp": int(kedaluwarsa.timestamp()),
        "jti": secrets.token_urlsafe(12),
    }
    token = jwt.encode(klaim, settings.secret_key, algorithm=settings.jwt_algorithm)
    return token, kedaluwarsa


def baca_token(token: str) -> dict[str, Any]:
    """Bongkar dan sahkan token akses.

    Raises:
        KredensialTidakSah: bila token kedaluwarsa, tanda tangannya tidak cocok,
            atau jenisnya bukan token akses.
    """
    try:
        klaim = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.jwt_algorithm],
            options={"require": ["exp", "sub", "jenis"]},
        )
    except jwt.ExpiredSignatureError as exc:
        raise KredensialTidakSah("Sesi telah berakhir. Silakan masuk kembali.") from exc
    except jwt.InvalidTokenError as exc:
        raise KredensialTidakSah("Token tidak sah.") from exc

    if klaim.get("jenis") != JENIS_AKSES:
        raise KredensialTidakSah("Jenis token tidak sesuai.")

    try:
        klaim["peran"] = Peran(klaim["peran"])
    except (KeyError, ValueError) as exc:
        raise KredensialTidakSah("Peran pada token tidak dikenali.") from exc

    return klaim


__all__ = [
    "JENIS_AKSES",
    "KredensialTidakSah",
    "baca_token",
    "cernakan_sandi",
    "kekuatan_sandi",
    "sandi_acak",
    "sandi_cocok",
    "terbitkan_token",
]
