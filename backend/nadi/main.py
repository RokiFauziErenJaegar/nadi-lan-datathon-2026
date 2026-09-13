"""Titik masuk aplikasi NADI.

Satu proses melayani seluruhnya: API, layanan analitik, dan berkas antarmuka
yang sudah dibangun. Pilihan ini disengaja. Pemisahan menjadi beberapa layanan
memang lebih rapi di diagram, namun menambah titik gagal pada demonstrasi yang
berjalan di satu laptop - dan titik gagal itu selalu memilih waktu terburuk
untuk muncul.

Bila kelak dipasang di peladen daerah, pemisahan dapat dilakukan tanpa mengubah
kode fitur: seluruh lapisan sudah terpisah menurut tanggung jawabnya.
"""

from __future__ import annotations

import logging
import time
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, ORJSONResponse
from fastapi.staticfiles import StaticFiles

from nadi.ai.provider import dapatkan_penyedia, tutup_penyedia
from nadi.config import settings
from nadi.db.session import buat_seluruh_tabel, periksa_koneksi
from nadi.security.pii import PIILeakError
from nadi.security.rbac import AksesDitolak

logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s  %(levelname)-7s %(name)-18s %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("nadi")

KETERANGAN = """
**NADI - Navigasi AI Data Intervensi**

Sistem pendukung keputusan untuk deteksi dini kerentanan kemiskinan dan
orkestrasi intervensi lintas perangkat daerah di Kabupaten Pringsewu.

### Batas yang perlu diketahui sebelum memakai

* Seluruh data pada sistem ini bersifat **sintetis**. Tidak ada satu pun
  keluarga nyata di dalamnya. Data dibangkitkan menyerupai bentuk statistik
  penduduk Kabupaten Pringsewu berdasarkan publikasi BPS.
* Keluaran sistem berupa **antrean prioritas pemeriksaan**, bukan keputusan.
  Tidak ada jalur pada API ini yang menghentikan, mengurangi, atau menunda
  bantuan siapa pun.
* Skor kerentanan adalah **perkiraan berpeluang**, bukan pernyataan tentang
  keadaan seseorang. Setiap skor disertai alasan yang dapat diperiksa dan
  dibantah.
* Identitas keluarga **dipseudonimkan**. Nomor induk kependudukan, nama, dan
  alamat tidak tersimpan pada sistem ini.
"""


@asynccontextmanager
async def daur_hidup(app: FastAPI):
    """Siapkan sumber daya saat aplikasi menyala, lepaskan saat berhenti."""
    settings.ensure_directories()
    buat_seluruh_tabel()

    db = periksa_koneksi()
    logger.info("Basis data: %s", db)

    if settings.llm_configured:
        logger.info("Layanan AI: %s (model %s)", settings.llm_base_url, settings.llm_model)
    else:
        logger.warning(
            "Layanan AI belum siap: %s. Policy Copilot berjalan dalam mode luring - "
            "seluruh angka dan rekomendasi tetap tersedia, hanya penyajian bahasa "
            "alaminya yang digantikan templat.",
            settings.alasan_llm_belum_siap,
        )

    yield

    await tutup_penyedia()
    logger.info("NADI berhenti.")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=KETERANGAN,
    default_response_class=ORJSONResponse,
    lifespan=daur_hidup,
    docs_url="/dokumentasi",
    redoc_url="/dokumentasi-alternatif",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------
@app.middleware("http")
async def catat_waktu(request: Request, call_next):
    """Catat lama pemrosesan setiap permintaan.

    Berguna bukan untuk kerapian melainkan untuk salah satu janji terukur pada
    proposal: waktu penyusunan daftar prioritas. Angka itu hanya dapat
    dibuktikan bila memang diukur sejak awal.
    """
    mulai = time.perf_counter()
    tanggapan = await call_next(request)
    durasi = (time.perf_counter() - mulai) * 1000
    tanggapan.headers["X-Waktu-Proses-Ms"] = f"{durasi:.1f}"
    if durasi > 2000:
        logger.warning("Permintaan lambat: %s %s (%.0f ms)", request.method, request.url.path, durasi)
    return tanggapan


# ---------------------------------------------------------------------------
# Penanganan galat
# ---------------------------------------------------------------------------
@app.exception_handler(PIILeakError)
async def tangani_kebocoran_pii(request: Request, exc: PIILeakError) -> JSONResponse:
    """Tangani percobaan pengiriman data pribadi ke layanan luar.

    Dijawab dengan 422, bukan 500. Ini bukan kegagalan peladen melainkan
    penolakan yang disengaja, dan pembedaannya penting: yang tercatat pada
    pemantauan haruslah "penghalang bekerja", bukan "sistem rusak".
    """
    logger.error("Permintaan dibatalkan oleh penjaga data pribadi: %s", exc.hasil.ringkas())
    return JSONResponse(
        status_code=422,
        content={
            "galat": "data_pribadi_terdeteksi",
            "pesan": (
                "Permintaan dibatalkan karena terdeteksi pengenal pribadi pada muatan "
                "yang akan dikirim ke layanan AI eksternal. Ini penghalang yang "
                "disengaja, bukan kegagalan sistem."
            ),
            "temuan": exc.hasil.ringkas(),
        },
    )


@app.exception_handler(AksesDitolak)
async def tangani_akses_ditolak(request: Request, exc: AksesDitolak) -> JSONResponse:
    return JSONResponse(
        status_code=403,
        content={
            "galat": "akses_ditolak",
            "pesan": str(exc),
            "peran": exc.peran.value,
            "kewenangan_diperlukan": exc.kewenangan.value,
        },
    )


# ---------------------------------------------------------------------------
# Titik akhir dasar
# ---------------------------------------------------------------------------
@app.get("/api/kesehatan", tags=["sistem"])
async def kesehatan() -> dict[str, Any]:
    """Periksa kesiapan seluruh bagian sistem."""
    penyedia = dapatkan_penyedia()
    return {
        "aplikasi": settings.app_name,
        "versi": settings.app_version,
        "lingkungan": settings.env,
        "basis_data": periksa_koneksi(),
        "layanan_ai": {
            "siap": settings.llm_configured,
            "alasan": settings.alasan_llm_belum_siap,
            "penyedia": penyedia.nama,
            "mode": "daring" if settings.llm_configured else "luring",
        },
        "privasi": {
            "penghalang_data_pribadi": settings.llm_block_pii,
            "pseudonimisasi": settings.pseudonymize,
        },
    }


@app.get("/api/kesehatan/ai", tags=["sistem"])
async def kesehatan_ai() -> dict[str, Any]:
    """Uji hubungan ke layanan AI dengan satu permintaan singkat."""
    return await dapatkan_penyedia().periksa()


def pasang_rute() -> None:
    """Daftarkan seluruh modul rute.

    Impor dilakukan di dalam fungsi agar kegagalan pada satu modul rute
    memberi pesan yang menunjuk modulnya, bukan menggagalkan seluruh aplikasi
    dengan galat impor yang tidak menjelaskan apa-apa.
    """
    from nadi.api.routes import (  # noqa: PLC0415
        antrean,
        copilot,
        intervensi,
        keluarga,
        masuk,
        model,
        pengaturan,
        rekomendasi,
        ringkasan,
        simulasi,
        wilayah,
    )

    for modul in (
        masuk,
        ringkasan,
        wilayah,
        keluarga,
        antrean,
        rekomendasi,
        intervensi,
        simulasi,
        copilot,
        model,
        pengaturan,
    ):
        app.include_router(modul.router, prefix="/api")


pasang_rute()


# ---------------------------------------------------------------------------
# Antarmuka
# ---------------------------------------------------------------------------
def pasang_antarmuka() -> None:
    """Sajikan berkas antarmuka yang sudah dibangun, bila tersedia."""
    dist = settings.frontend_dist
    if not dist.exists():
        logger.info(
            "Berkas antarmuka belum dibangun (%s tidak ada). "
            "Jalankan 'npm run build' di folder frontend, atau pakai peladen "
            "pengembangan Vite pada porta 5173.",
            dist,
        )
        return

    app.mount("/aset", StaticFiles(directory=dist / "assets"), name="aset")

    @app.get("/{jalur:path}", include_in_schema=False)
    async def sajikan_antarmuka(jalur: str):
        """Kembalikan halaman antarmuka untuk seluruh alamat non-API.

        Diperlukan karena antarmuka memakai perutean sisi klien: alamat seperti
        /keluarga/KLG-7F3A tidak berpadanan dengan berkas mana pun di cakram,
        namun harus tetap membuka aplikasi alih-alih menampilkan galat 404.
        """
        berkas = dist / jalur
        if jalur and berkas.is_file():
            return FileResponse(berkas)
        return FileResponse(dist / "index.html")

    logger.info("Antarmuka disajikan dari %s", dist)


pasang_antarmuka()


def jalankan() -> None:  # pragma: no cover - dipanggil dari baris perintah
    import uvicorn

    uvicorn.run(
        "nadi.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info",
    )


if __name__ == "__main__":  # pragma: no cover
    jalankan()
