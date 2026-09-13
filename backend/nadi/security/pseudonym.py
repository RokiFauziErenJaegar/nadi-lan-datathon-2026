"""Pseudonimisasi identitas keluarga dan individu.

Undang-Undang Nomor 27 Tahun 2022 tentang Pelindungan Data Pribadi menuntut
prinsip minimalisasi data. NADI menerapkannya dengan cara berikut: pengenal
asli (id basis data) tidak pernah muncul di antarmuka, respons API, berkas
ekspor, maupun muatan yang dikirim ke layanan AI. Yang beredar hanyalah
**kode semu** yang stabil namun tidak dapat dibalik tanpa kunci rahasia.

Sifat yang dijamin:

* **Stabil** - id yang sama selalu menghasilkan kode semu yang sama, sehingga
  petugas dapat merujuk satu kasus lintas layar dan lintas hari.
* **Tak terbalikkan** - tanpa ``NADI_SECRET_KEY`` kode semu tidak dapat
  dikembalikan menjadi id asli; berkas ekspor yang bocor tidak membuka data.
* **Terpisah per jenis entitas** - kode keluarga dan kode individu berasal dari
  ruang berbeda, sehingga tidak dapat disilangkan.
* **Dapat dicabut** - mengganti kunci rahasia membatalkan seluruh kode lama.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import re
from typing import Final

from nadi.config import settings

# Alfabet Crockford Base32 tanpa huruf yang mudah tertukar saat dibacakan
# lewat telepon (I, L, O, U dihilangkan) - petugas lapangan sering menyebutkan
# kode ini secara lisan.
_ALPHABET: Final[str] = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"

# Awalan per jenis entitas.
PREFIX_KELUARGA: Final[str] = "KLG"
PREFIX_INDIVIDU: Final[str] = "IND"
PREFIX_KASUS: Final[str] = "KSS"
PREFIX_INTERVENSI: Final[str] = "ITV"

_POLA_KODE = re.compile(r"^(KLG|IND|KSS|ITV)-[0-9A-HJKMNP-TV-Z]{4}-[0-9A-HJKMNP-TV-Z]{4}$")


def _digest(ruang: str, nilai: str | int) -> bytes:
    """Hitung HMAC-SHA256 dengan kunci rahasia aplikasi."""
    pesan = f"{ruang}:{nilai}".encode("utf-8")
    kunci = settings.secret_key.encode("utf-8")
    return hmac.new(kunci, pesan, hashlib.sha256).digest()


def _ke_base32(data: bytes, panjang: int) -> str:
    """Ubah cernaan biner menjadi untai alfabet aman-baca."""
    angka = int.from_bytes(data, "big")
    keluar: list[str] = []
    for _ in range(panjang):
        angka, sisa = divmod(angka, len(_ALPHABET))
        keluar.append(_ALPHABET[sisa])
    return "".join(reversed(keluar))


def buat_kode(ruang: str, nilai: str | int, awalan: str, panjang: int = 8) -> str:
    """Bentuk kode semu, misalnya ``KLG-7F3A-2B9K``.

    Args:
        ruang: pemisah ruang nama, mencegah id yang sama pada tabel berbeda
            menghasilkan kode yang sama.
        nilai: pengenal asli.
        awalan: penanda jenis entitas yang tampil di antarmuka.
        panjang: jumlah karakter acak; 8 karakter Base32 setara 40 bit,
            memberi ruang sekitar satu triliun kemungkinan - jauh melebihi
            kebutuhan satu kabupaten.
    """
    inti = _ke_base32(_digest(ruang, nilai), panjang)
    tengah = panjang // 2
    return f"{awalan}-{inti[:tengah]}-{inti[tengah:]}"


def kode_keluarga(id_keluarga: str | int) -> str:
    """Kode semu untuk satu keluarga."""
    return buat_kode("keluarga", id_keluarga, PREFIX_KELUARGA)


def kode_individu(id_individu: str | int) -> str:
    """Kode semu untuk satu anggota keluarga."""
    return buat_kode("individu", id_individu, PREFIX_INDIVIDU)


def kode_kasus(id_kasus: str | int) -> str:
    """Kode semu untuk satu kasus pada antrean verifikasi."""
    return buat_kode("kasus", id_kasus, PREFIX_KASUS)


def kode_intervensi(id_intervensi: str | int) -> str:
    """Kode semu untuk satu catatan intervensi."""
    return buat_kode("intervensi", id_intervensi, PREFIX_INTERVENSI)


def valid_kode(kode: str) -> bool:
    """Periksa apakah untai berbentuk kode semu yang sah."""
    return bool(_POLA_KODE.match(kode.strip().upper()))


class PetaKodeSemu:
    """Peta dua arah antara id asli dan kode semu untuk satu permintaan.

    Lapisan API memerlukan pemetaan balik agar dapat menerjemahkan kode semu
    yang dikirim klien kembali menjadi id basis data. Karena HMAC tidak dapat
    dibalik secara matematis, pembalikan dilakukan dengan membangun peta dari
    himpunan id yang memang berhak diakses pengguna tersebut. Dengan cara ini
    kode semu milik keluarga di luar kewenangan pengguna tidak akan pernah
    dapat diterjemahkan - pembatasan akses ikut terjaga.
    """

    def __init__(self, ruang: str, awalan: str) -> None:
        self._ruang = ruang
        self._awalan = awalan
        self._maju: dict[str, str] = {}
        self._mundur: dict[str, str] = {}

    def daftarkan(self, id_asli: str | int) -> str:
        kunci = str(id_asli)
        if kunci in self._maju:
            return self._maju[kunci]
        kode = buat_kode(self._ruang, kunci, self._awalan)
        self._maju[kunci] = kode
        self._mundur[kode] = kunci
        return kode

    def daftarkan_banyak(self, id_asli: list[str | int]) -> list[str]:
        return [self.daftarkan(i) for i in id_asli]

    def ke_kode(self, id_asli: str | int) -> str:
        return self.daftarkan(id_asli)

    def ke_id(self, kode: str) -> str | None:
        """Kembalikan id asli, atau ``None`` bila kode di luar cakupan izin."""
        return self._mundur.get(kode.strip().upper())


def sidik_jari_dataset(nilai: bytes | str) -> str:
    """Sidik jari SHA-256 sebuah berkas atau untai, untuk jejak audit.

    Dipakai mencatat versi dataset dan model yang menghasilkan sebuah skor,
    sehingga setiap keputusan dapat ditelusuri kembali ke asalnya.
    """
    data = nilai.encode("utf-8") if isinstance(nilai, str) else nilai
    return base64.b16encode(hashlib.sha256(data).digest()).decode("ascii")[:16].lower()


__all__ = [
    "PREFIX_INDIVIDU",
    "PREFIX_INTERVENSI",
    "PREFIX_KASUS",
    "PREFIX_KELUARGA",
    "PetaKodeSemu",
    "buat_kode",
    "kode_individu",
    "kode_intervensi",
    "kode_kasus",
    "kode_keluarga",
    "sidik_jari_dataset",
    "valid_kode",
]
