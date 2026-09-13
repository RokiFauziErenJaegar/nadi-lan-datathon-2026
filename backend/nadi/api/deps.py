"""Dependensi bersama untuk seluruh titik akhir API.

Tiga hal ditegakkan di lapisan ini, sebelum satu baris pun logika fitur
dijalankan: siapa penggunanya, apa yang boleh dilakukannya, dan apa yang boleh
dilihatnya.

Pemisahan antara **kewenangan** dan **cakupan data** dipertahankan sampai ke
sini. Kewenangan memutuskan apakah sebuah titik akhir boleh dipanggil sama
sekali; cakupan data memutuskan baris mana yang boleh muncul pada jawabannya.
Seorang perencana di Bappeda memiliki kewenangan membaca peta risiko, namun
cakupannya hanya agregat - permintaan yang sama menghasilkan jawaban yang
berbeda baginya, dan itu memang seharusnya.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Annotated, Callable, Iterator

from fastapi import Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session

from nadi.db.models import JejakAudit, Pengguna
from nadi.db.session import dapatkan_sesi
from nadi.security.auth import KredensialTidakSah, baca_token
from nadi.security.rbac import (
    CakupanData,
    Kewenangan,
    Peran,
    berwenang,
    boleh_buka_keluarga,
    cakupan_peran,
)

logger = logging.getLogger("nadi.api")

SesiDB = Annotated[Session, Depends(dapatkan_sesi)]


@dataclass
class KonteksPengguna:
    """Identitas dan hak pengguna pada satu permintaan."""

    id: int
    nama_pengguna: str
    nama_lengkap: str
    peran: Peran
    opd_id: int | None
    wilayah_akses: list[str]

    @property
    def cakupan(self) -> CakupanData:
        return cakupan_peran(self.peran)

    @property
    def boleh_buka_keluarga(self) -> bool:
        return boleh_buka_keluarga(self.peran)

    @property
    def dibatasi_wilayah(self) -> bool:
        return (
            self.cakupan is CakupanData.WILAYAH_TERTUGAS and bool(self.wilayah_akses)
        )

    def punya(self, kewenangan: Kewenangan) -> bool:
        return berwenang(self.peran, kewenangan)

    def ke_dict(self) -> dict:
        return {
            "id": self.id,
            "nama_pengguna": self.nama_pengguna,
            "nama_lengkap": self.nama_lengkap,
            "peran": self.peran.value,
            "label_peran": self.peran.label,
            "opd_id": self.opd_id,
            "cakupan_data": self.cakupan.value,
            "boleh_buka_keluarga": self.boleh_buka_keluarga,
            "wilayah_akses": self.wilayah_akses,
            "kewenangan": sorted(k.value for k in Kewenangan if self.punya(k)),
        }


# ---------------------------------------------------------------------------
def _ambil_token(authorization: str | None) -> str:
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Diperlukan token akses. Silakan masuk terlebih dahulu.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    bagian = authorization.split(maxsplit=1)
    if len(bagian) != 2 or bagian[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Format tajuk otorisasi tidak sesuai. Gunakan 'Bearer <token>'.",
        )
    return bagian[1]


def pengguna_saat_ini(
    authorization: Annotated[str | None, Header()] = None,
) -> KonteksPengguna:
    """Baca dan sahkan token akses dari tajuk permintaan."""
    token = _ambil_token(authorization)
    try:
        klaim = baca_token(token)
    except KredensialTidakSah as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)
        ) from exc

    return KonteksPengguna(
        id=int(klaim["sub"]),
        nama_pengguna=klaim.get("nama", ""),
        nama_lengkap=klaim.get("nama", ""),
        peran=klaim["peran"],
        opd_id=klaim.get("opd"),
        wilayah_akses=list(klaim.get("wilayah") or []),
    )


PenggunaAktif = Annotated[KonteksPengguna, Depends(pengguna_saat_ini)]


def wajib(kewenangan: Kewenangan) -> Callable[[KonteksPengguna], KonteksPengguna]:
    """Bentuk dependensi yang menuntut satu kewenangan tertentu.

    Dipakai sebagai:

        @router.get("/antrean", dependencies=[Depends(wajib(Kewenangan.BACA_ANTREAN))])
    """

    def pemeriksa(pengguna: PenggunaAktif) -> KonteksPengguna:
        if not pengguna.punya(kewenangan):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Peran '{pengguna.peran.label}' tidak memiliki kewenangan "
                    f"'{kewenangan.value}'."
                ),
            )
        return pengguna

    return pemeriksa


def wajib_buka_keluarga(pengguna: PenggunaAktif) -> KonteksPengguna:
    """Tolak permintaan membuka baris keluarga bagi peran beragregat.

    Pemeriksaan ini disediakan terpisah karena menjaga sesuatu yang berbeda
    dari kewenangan biasa. Seorang pimpinan daerah memiliki kewenangan penuh
    atas kebijakan, namun tidak memerlukan - dan karena itu tidak diberi -
    kemampuan menelusuri satu keluarga tertentu. Membatasinya di sini menutup
    jalur penyalahgunaan yang paling sulit terdeteksi, sebab penyalahgunaan
    semacam itu tampak persis seperti pemakaian biasa.
    """
    if not pengguna.boleh_buka_keluarga:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                f"Peran '{pengguna.peran.label}' hanya berwenang mengakses data agregat. "
                "Data tingkat keluarga tidak diperlukan untuk fungsi ini dan karena itu "
                "tidak dibuka."
            ),
        )
    return pengguna


# ---------------------------------------------------------------------------
def catat_audit(
    sesi: Session,
    pengguna: KonteksPengguna | None,
    aksi: str,
    *,
    entitas: str | None = None,
    entitas_id: str | None = None,
    ringkasan: str | None = None,
    berhasil: bool = True,
    request: Request | None = None,
    rincian: dict | None = None,
) -> None:
    """Tulis satu baris jejak audit.

    Nama dan peran pengguna DISALIN, bukan sekadar dirujuk lewat kunci asing.
    Bila akun kelak dihapus atau perannya berubah, jejak tetap menunjukkan
    keadaan pada saat kejadian - yang justru menjadi inti sebuah jejak audit.
    """
    try:
        sesi.add(
            JejakAudit(
                pengguna_id=pengguna.id if pengguna else None,
                nama_pengguna=pengguna.nama_pengguna if pengguna else None,
                peran=pengguna.peran.value if pengguna else None,
                aksi=aksi,
                entitas=entitas,
                entitas_id=str(entitas_id) if entitas_id is not None else None,
                ringkasan=ringkasan,
                alamat_ip=request.client.host if request and request.client else None,
                agen_pengguna=(request.headers.get("user-agent", "")[:300] if request else None),
                berhasil=berhasil,
                rincian=rincian,
            )
        )
        sesi.flush()
    except Exception as exc:  # noqa: BLE001
        # Kegagalan menulis jejak audit tidak boleh menggagalkan permintaan
        # pengguna, namun wajib terlihat di log peladen.
        logger.error("Gagal menulis jejak audit untuk aksi '%s': %s", aksi, exc)


def muat_pengguna(sesi: Session, konteks: KonteksPengguna) -> Pengguna | None:
    """Ambil baris pengguna dari basis data bila diperlukan."""
    return sesi.get(Pengguna, konteks.id)


__all__ = [
    "KonteksPengguna",
    "PenggunaAktif",
    "SesiDB",
    "catat_audit",
    "muat_pengguna",
    "pengguna_saat_ini",
    "wajib",
    "wajib_buka_keluarga",
]
