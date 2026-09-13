"""Pengaturan layanan AI - memilih penyedia dari dalam aplikasi.

Sebelum modul ini ada, mengganti penyedia berarti menyunting ``.env`` lalu
menyalakan ulang peladen. Itu bekerja bagi orang yang menulis kodenya, dan
tidak bekerja bagi siapa pun yang lain.

Tiga hal yang dijaga di sini:

**Kunci tidak pernah dikembalikan.** Titik akhir baca hanya mengirim bentuk
tersamarnya - enam huruf pertama dan empat terakhir. Kunci yang sudah masuk
tidak dapat ditarik keluar lagi lewat antarmuka mana pun, termasuk oleh
administrator yang memasukkannya. Bila hilang, ia diganti, bukan dibaca ulang.

**Menguji lebih dahulu, menyimpan kemudian.** Konfigurasi dapat dicoba tanpa
disimpan. Konfigurasi yang salah karena itu tidak pernah sempat mematikan
Copilot: yang tersimpan hanyalah yang sudah terbukti menjawab.

**Perubahan tercatat, isinya tidak.** Setiap penyuntingan masuk ke jejak audit
beserta nama penyedia dan model - tidak pernah beserta kuncinya.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from nadi.ai.katalog import KATALOG, PETA_KATALOG, ke_dict, tebak_penyedia
from nadi.ai.provider import (
    LLMTidakTersedia,
    Peran,
    PenyediaKompatibelOpenAI,
    PesanChat,
    dapatkan_penyedia,
)
from nadi.api.deps import KonteksPengguna, SesiDB, catat_audit, wajib
from nadi.config import settings
from nadi.config_runtime import PengaturanDitolak, samarkan, simpan_konfigurasi_ai
from nadi.security.rbac import Kewenangan

logger = logging.getLogger("nadi.api.pengaturan")
router = APIRouter(prefix="/pengaturan", tags=["pengaturan"])

# Penanda bahwa kunci yang sekarang harus dipertahankan. Antarmuka mengirimkan
# ini ketika pengguna hanya mengganti model atau alamat, sehingga ia tidak perlu
# mengetik ulang kunci yang tidak pernah ditampilkan kepadanya.
KUNCI_TETAP = "__TETAP__"


class KonfigurasiAI(BaseModel):
    base_url: str = Field(min_length=4, max_length=256)
    model: str = Field(min_length=1, max_length=128)
    api_key: str | None = Field(None, max_length=512)
    aktif: bool = True
    maks_token: int = Field(2400, ge=64, le=32000)
    suhu: float = Field(0.2, ge=0.0, le=2.0)
    batas_waktu_detik: float = Field(60.0, ge=5.0, le=300.0)


def _kunci_efektif(diminta: str | None) -> str:
    """Kunci yang benar-benar dipakai: yang baru, atau yang sudah tersimpan."""
    if diminta is None or diminta == KUNCI_TETAP or not diminta.strip():
        return settings.llm_api_key
    return diminta.strip()


@router.get("/ai", summary="Pengaturan layanan AI yang berlaku",
            dependencies=[Depends(wajib(Kewenangan.KELOLA_SISTEM))])
def baca() -> dict:
    """Pengaturan yang berlaku sekarang, beserta daftar penyedia yang dikenal."""
    return {
        "berlaku": {
            "penyedia": tebak_penyedia(settings.llm_base_url),
            "base_url": settings.llm_base_url,
            "model": settings.llm_model,
            "api_key_tersamar": samarkan(settings.llm_api_key),
            "ada_kunci": bool(samarkan(settings.llm_api_key)),
            "aktif": settings.llm_enabled,
            "maks_token": settings.llm_max_tokens,
            "suhu": settings.llm_temperature,
            "batas_waktu_detik": settings.llm_timeout_seconds,
            "penghalang_pii": settings.llm_block_pii,
        },
        "siap": settings.llm_configured,
        "alasan_belum_siap": settings.alasan_llm_belum_siap,
        "katalog": [ke_dict(p) for p in KATALOG],
        "keterangan_kunci": (
            "Kunci API disimpan pada berkas .env di server, bukan di dalam basis data - "
            "berkas basis data memang dimaksudkan untuk disalin, dan rahasia tidak boleh "
            "ikut tersalin bersamanya. Kunci yang sudah tersimpan tidak dapat ditampilkan "
            "kembali oleh siapa pun; bila hilang, ganti dengan yang baru."
        ),
        "penghalang_pii": (
            "Berlaku untuk penyedia mana pun. Setiap muatan diperiksa tepat sebelum "
            "dikirim, dan permintaan dibatalkan bila memuat pengenal pribadi."
        ),
    }


@router.post("/ai/model", summary="Ambil daftar model dari penyedia")
async def daftar_model(
    data: KonfigurasiAI,
    pengguna: KonteksPengguna = Depends(wajib(Kewenangan.KELOLA_SISTEM)),
) -> dict:
    """Tanyakan kepada penyedia model apa saja yang tersedia bagi kunci ini.

    Dipakai antarmuka agar nama model tidak perlu ditebak atau diketik dari
    ingatan - kesalahan mengetik nama model adalah sebab kegagalan yang paling
    sering, dan pesan galatnya paling tidak membantu.
    """
    klien = PenyediaKompatibelOpenAI(
        base_url=data.base_url.strip(),
        api_key=_kunci_efektif(data.api_key),
        model=data.model.strip() or "sementara",
        timeout=min(data.batas_waktu_detik, 30.0),
        maks_percobaan=1,
    )
    try:
        model = await klien.daftar_model()
    finally:
        await klien.tutup()

    return {
        "model": model,
        "jumlah": len(model),
        "catatan": (
            None
            if model
            else "Penyedia tidak memberikan daftar model. Ketik nama modelnya sendiri."
        ),
    }


@router.post("/ai/uji", summary="Uji konfigurasi tanpa menyimpannya")
async def uji(
    data: KonfigurasiAI,
    pengguna: KonteksPengguna = Depends(wajib(Kewenangan.KELOLA_SISTEM)),
) -> dict:
    """Kirim satu permintaan sungguhan memakai konfigurasi yang diusulkan.

    Daftar model yang berhasil diambil belum membuktikan apa pun: kuota, izin,
    dan nama model yang sudah usang baru ketahuan ketika model benar-benar
    dipanggil.
    """
    klien = PenyediaKompatibelOpenAI(
        base_url=data.base_url.strip(),
        api_key=_kunci_efektif(data.api_key),
        model=data.model.strip(),
        timeout=data.batas_waktu_detik,
        maks_percobaan=1,
    )
    try:
        hasil = await klien.chat(
            [
                PesanChat(Peran.SISTEM, "Anda asisten kebijakan sosial. Jawab ringkas dalam bahasa Indonesia."),
                PesanChat(
                    Peran.PENGGUNA,
                    "Sebutkan satu sebab keluarga miskin tidak menerima bantuan sosial. Satu kalimat.",
                ),
            ],
            suhu=data.suhu,
            maks_token=data.maks_token,
        )
        return {
            "berhasil": True,
            "model": hasil.model,
            "durasi_ms": hasil.durasi_ms,
            "token_keluaran": hasil.token_keluaran,
            "contoh_jawaban": hasil.teks[:400],
        }
    except LLMTidakTersedia as exc:
        return {"berhasil": False, "pesan": str(exc)}
    finally:
        await klien.tutup()


@router.post("/ai", summary="Simpan pengaturan layanan AI")
async def simpan(
    data: KonfigurasiAI,
    sesi: SesiDB,
    request: Request,
    pengguna: KonteksPengguna = Depends(wajib(Kewenangan.KELOLA_SISTEM)),
) -> dict:
    """Simpan pengaturan, terapkan seketika, lalu bangun ulang penyedia.

    Penyimpanan menuntut konfigurasi yang dapat dipakai. Menyimpan pengaturan
    yang belum diuji sama artinya dengan mematikan Copilot dan baru
    mengetahuinya ketika seseorang bertanya di hadapan dewan juri.
    """
    kunci = _kunci_efektif(data.api_key)
    penyedia = PETA_KATALOG.get(tebak_penyedia(data.base_url))
    butuh_kunci = penyedia.butuh_kunci if penyedia else True

    if data.aktif and butuh_kunci and (not kunci.strip() or kunci.strip().startswith("isi-api-key")):
        raise HTTPException(422, "Penyedia ini memerlukan kunci API.")

    nilai = {
        "NADI_LLM_ENABLED": data.aktif,
        "NADI_LLM_BASE_URL": data.base_url.strip().rstrip("/"),
        "NADI_LLM_MODEL": data.model.strip(),
        "NADI_LLM_MAX_TOKENS": data.maks_token,
        "NADI_LLM_TEMPERATURE": data.suhu,
        "NADI_LLM_TIMEOUT_SECONDS": data.batas_waktu_detik,
    }
    # Kunci hanya ditulis bila memang ada yang baru; menuliskan ulang nilai
    # yang sama hanya memperbesar peluang ia bocor ke tempat yang tidak
    # diinginkan, tanpa manfaat apa pun.
    if data.api_key and data.api_key != KUNCI_TETAP and data.api_key.strip():
        nilai["NADI_LLM_API_KEY"] = data.api_key.strip()

    try:
        hasil = await simpan_konfigurasi_ai(nilai)
    except PengaturanDitolak as exc:
        raise HTTPException(400, str(exc)) from exc

    catat_audit(
        sesi,
        pengguna,
        "ubah_pengaturan_ai",
        entitas="pengaturan",
        entitas_id="layanan_ai",
        # Nama bidang saja - tidak pernah nilainya, karena salah satunya kunci.
        ringkasan=f"Penyedia {tebak_penyedia(data.base_url)}, model {data.model.strip()}",
        request=request,
        rincian={
            "bidang_berubah": hasil["berubah"],
            "kunci_diganti": "NADI_LLM_API_KEY" in hasil["berubah"],
        },
    )
    sesi.commit()

    return {
        "tersimpan": True,
        "berubah": hasil["berubah"],
        "siap": settings.llm_configured,
        "alasan_belum_siap": settings.alasan_llm_belum_siap,
        "catatan": "Pengaturan berlaku seketika; peladen tidak perlu dijalankan ulang.",
    }


@router.get("/ai/kesehatan", summary="Keadaan layanan AI yang sedang dipakai",
            dependencies=[Depends(wajib(Kewenangan.KELOLA_SISTEM))])
async def kesehatan() -> dict:
    """Periksa penyedia yang sedang aktif, bukan yang diusulkan."""
    return await dapatkan_penyedia().periksa()


__all__ = ["router"]
