"""Autentikasi dan keterangan pengguna."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, Field

from nadi.api.deps import PenggunaAktif, SesiDB, catat_audit
from nadi.config import settings
from nadi.security.auth import sandi_cocok, terbitkan_token
from nadi.security.rbac import ringkasan_matriks
from nadi.services.pengguna import AKUN_DEMO, cari_pengguna

logger = logging.getLogger("nadi.api.masuk")
router = APIRouter(tags=["autentikasi"])

#: Lama penguncian akun setelah percobaan masuk gagal berulang.
PERCOBAAN_MAKSIMUM = 6
LAMA_KUNCI_MENIT = 15


class PermintaanMasuk(BaseModel):
    nama_pengguna: str = Field(min_length=1, max_length=64)
    sandi: str = Field(min_length=1, max_length=256)


class TanggapanMasuk(BaseModel):
    token: str
    jenis: str = "bearer"
    kedaluwarsa: datetime
    pengguna: dict


@router.post("/masuk", response_model=TanggapanMasuk, summary="Masuk ke sistem")
def masuk(data: PermintaanMasuk, sesi: SesiDB, request: Request) -> TanggapanMasuk:
    """Sahkan kredensial dan terbitkan token akses.

    Pesan penolakan sengaja dibuat sama untuk nama pengguna yang tidak ada
    maupun sandi yang keliru. Membedakannya akan memberi tahu penyerang bahwa
    sebuah nama pengguna memang terdaftar - keterangan yang tidak perlu
    diberikan secara cuma-cuma.
    """
    pengguna = cari_pengguna(sesi, data.nama_pengguna)
    pesan_gagal = "Nama pengguna atau sandi tidak sesuai."

    if pengguna is None:
        catat_audit(
            sesi, None, "masuk_gagal",
            ringkasan=f"Nama pengguna tidak dikenal: {data.nama_pengguna[:32]}",
            berhasil=False, request=request,
        )
        sesi.commit()
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, pesan_gagal)

    if pengguna.terkunci:
        sisa = int((pengguna.terkunci_sampai - datetime.now(timezone.utc)).total_seconds() / 60) + 1
        raise HTTPException(
            status.HTTP_429_TOO_MANY_REQUESTS,
            f"Akun terkunci sementara. Coba lagi dalam {sisa} menit.",
        )

    if not pengguna.aktif:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Akun tidak aktif.")

    if not sandi_cocok(data.sandi, pengguna.cernaan_sandi):
        pengguna.jumlah_gagal_masuk += 1
        if pengguna.jumlah_gagal_masuk >= PERCOBAAN_MAKSIMUM:
            pengguna.terkunci_sampai = datetime.now(timezone.utc) + timedelta(minutes=LAMA_KUNCI_MENIT)
            logger.warning("Akun '%s' dikunci setelah %d percobaan gagal.",
                           pengguna.nama_pengguna, pengguna.jumlah_gagal_masuk)
        catat_audit(
            sesi, None, "masuk_gagal",
            entitas="pengguna", entitas_id=pengguna.id,
            ringkasan=f"Sandi keliru, percobaan ke-{pengguna.jumlah_gagal_masuk}",
            berhasil=False, request=request,
        )
        sesi.commit()
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, pesan_gagal)

    pengguna.jumlah_gagal_masuk = 0
    pengguna.terkunci_sampai = None
    pengguna.terakhir_masuk = datetime.now(timezone.utc)

    token, kedaluwarsa = terbitkan_token(
        id_pengguna=pengguna.id,
        nama_pengguna=pengguna.nama_pengguna,
        peran=pengguna.peran,
        id_opd=pengguna.opd_id,
        kode_wilayah=list(pengguna.wilayah_akses or []),
    )
    catat_audit(
        sesi, None, "masuk_berhasil",
        entitas="pengguna", entitas_id=pengguna.id,
        ringkasan=f"{pengguna.nama_pengguna} ({pengguna.peran.value})",
        request=request,
    )
    sesi.commit()

    return TanggapanMasuk(
        token=token,
        kedaluwarsa=kedaluwarsa,
        pengguna={
            "id": pengguna.id,
            "nama_pengguna": pengguna.nama_pengguna,
            "nama_lengkap": pengguna.nama_lengkap,
            "jabatan": pengguna.jabatan,
            "peran": pengguna.peran.value,
            "label_peran": pengguna.peran.label,
            "deskripsi_peran": pengguna.peran.deskripsi,
            "opd": pengguna.opd.singkatan if pengguna.opd else None,
            "wilayah_akses": list(pengguna.wilayah_akses or []),
        },
    )


@router.get("/saya", summary="Keterangan pengguna yang sedang masuk")
def saya(pengguna: PenggunaAktif) -> dict:
    """Kembalikan identitas dan hak pengguna dari token yang dipakai."""
    return pengguna.ke_dict()


@router.get("/peran", summary="Matriks peran dan kewenangan")
def daftar_peran() -> dict:
    """Tampilkan seluruh peran beserta kewenangan dan cakupan datanya.

    Dibuka tanpa autentikasi dengan sengaja. Aturan siapa boleh melihat apa
    bukanlah rahasia - justru sebaliknya, keterbukaannya adalah bagian dari
    akuntabilitas. Setiap orang berhak mengetahui batas kewenangan pihak yang
    memegang datanya.
    """
    return {
        "peran": ringkasan_matriks(),
        "catatan": (
            "Peran pimpinan daerah dan perencana sengaja dibatasi pada data agregat. "
            "Keduanya tidak memerlukan identitas keluarga untuk menjalankan tugasnya, "
            "dan membatasi akses di sini menutup jalur penyalahgunaan yang paling "
            "sulit dideteksi."
        ),
    }


@router.get("/akun-demo", summary="Daftar akun demonstrasi")
def akun_demo() -> dict:
    """Daftar akun untuk mencoba sistem.

    Hanya tersedia di luar lingkungan produksi.
    """
    if settings.env == "production":
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Tidak tersedia.")
    return {
        "keterangan": (
            "Seluruh data pada sistem ini sintetis. Masuklah sebagai peran yang "
            "berbeda untuk melihat bagaimana pembatasan akses bekerja - "
            "coba buka satu keluarga sebagai pimpinan daerah, dan sistem akan menolak."
        ),
        "akun": [
            {
                "nama_pengguna": a.nama_pengguna,
                "sandi": a.sandi,
                "nama_lengkap": a.nama_lengkap,
                "jabatan": a.jabatan,
                "peran": a.peran.value,
                "label_peran": a.peran.label,
                "cakupan": "seluruh kabupaten" if not a.wilayah_akses else f"terbatas {', '.join(a.wilayah_akses)}",
            }
            for a in AKUN_DEMO
        ],
    }


__all__ = ["router"]
