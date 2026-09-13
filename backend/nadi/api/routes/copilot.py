"""AI Policy Copilot - tanya jawab berbasis pengetahuan sistem."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field

from nadi.ai.copilot import dapatkan_copilot
from nadi.api.deps import PenggunaAktif, SesiDB, catat_audit, wajib
from nadi.config import settings
from nadi.db.models import CatatanPermintaanAI
from nadi.security.pii import PIILeakError
from nadi.security.rbac import Kewenangan

logger = logging.getLogger("nadi.api.copilot")
router = APIRouter(prefix="/copilot", tags=["copilot"])


class PermintaanTanya(BaseModel):
    pertanyaan: str = Field(min_length=3, max_length=600)


@router.post("/tanya", summary="Ajukan pertanyaan kepada copilot",
             dependencies=[Depends(wajib(Kewenangan.GUNAKAN_COPILOT))])
async def tanya(
    data: PermintaanTanya,
    sesi: SesiDB,
    request: Request,
    pengguna: PenggunaAktif,
) -> dict:
    """Jawab pertanyaan dari basis pengetahuan sistem.

    Setiap pemanggilan dicatat pada :class:`CatatanPermintaanAI`. Isi percakapan
    TIDAK disimpan - yang dicatat hanya bentuknya: ukuran muatan, hasil
    pemindaian pengenal pribadi, model yang menjawab, dan lamanya. Menyimpan isi
    percakapan justru akan menciptakan tempat penampungan data baru, persis yang
    hendak dihindari.
    """
    copilot = dapatkan_copilot(sesi)
    catatan = CatatanPermintaanAI(
        pengguna_id=pengguna.id,
        keperluan="copilot",
        penyedia=None,
        model=None,
    )

    try:
        hasil = await copilot.jawab(data.pertanyaan, peran_pengguna=pengguna.peran.label)
    except PIILeakError as exc:
        catatan.diblokir = True
        catatan.berhasil = False
        catatan.hasil_pindai_pii = exc.hasil.ringkas()
        catatan.galat = "muatan memuat pengenal pribadi"
        sesi.add(catatan)
        catat_audit(
            sesi, pengguna, "copilot_diblokir",
            ringkasan="Permintaan dibatalkan penjaga data pribadi",
            berhasil=False, request=request,
        )
        sesi.commit()
        raise

    catatan.model = hasil.model
    catatan.dari_cadangan = hasil.dari_cadangan
    catatan.durasi_ms = hasil.durasi_ms
    catatan.ukuran_muatan_bita = len(data.pertanyaan.encode("utf-8"))
    catatan.hasil_pindai_pii = "diredaksi" if hasil.pertanyaan_diredaksi else "bersih"
    catatan.berhasil = True
    sesi.add(catatan)

    catat_audit(
        sesi, pengguna, "copilot_tanya",
        ringkasan=f"{len(hasil.potongan_dipakai)} potongan dipakai, "
                  f"{'cadangan luring' if hasil.dari_cadangan else hasil.model}",
        request=request,
    )
    sesi.commit()

    return hasil.ke_dict()


@router.get("/contoh-pertanyaan", summary="Contoh pertanyaan yang dapat dijawab")
def contoh() -> dict:
    """Pertanyaan contoh, sekaligus menunjukkan batas kemampuan copilot."""
    return {
        "dapat_dijawab": [
            "Program apa saja yang menangani rumah tidak layak huni, dan dinas mana pelaksananya?",
            "Apa arti desil kesejahteraan dan dari mana angkanya berasal?",
            "Kecamatan mana yang tingkat kemiskinannya paling tinggi?",
            "Berapa nominal Program Keluarga Harapan untuk komponen anak SMA?",
            "Apa bedanya garis kemiskinan dan garis kerentanan?",
            "Seberapa akurat model kerentanan NADI?",
            "Faktor risiko apa saja yang ditangani Program Sembako?",
            "Mengapa Kecamatan Pagelaran Utara berisiko lebih tinggi?",
        ],
        "tidak_dapat_dijawab": [
            "Apakah keluarga KLG-XXXX layak menerima bantuan? "
            "(kelayakan ditetapkan verifikasi petugas dan musyawarah pekon, bukan copilot)",
            "Siapa nama kepala keluarga ini? "
            "(sistem tidak menyimpan nama, nomor induk kependudukan, maupun alamat)",
            "Berapa angka kemiskinan tahun depan? "
            "(sistem tidak memperkirakan angka makro)",
            "Bantuan siapa yang sebaiknya dihentikan? "
            "(sistem tidak dipakai untuk menghentikan bantuan siapa pun)",
        ],
        "status_layanan": {
            "siap": settings.llm_configured,
            "alasan": settings.alasan_llm_belum_siap,
            "mode": "daring" if settings.llm_configured else "luring",
            "catatan_mode_luring": (
                "Dalam mode luring, copilot tetap menjawab dari basis pengetahuan yang "
                "sama dengan bahasa templat. Seluruh angka identik; yang hilang hanya "
                "keluwesan kalimatnya. Seluruh skor, rekomendasi, dan simulasi tetap "
                "berjalan penuh sebab semuanya dihitung secara lokal."
            ),
        },
    }


@router.post("/muat-ulang", summary="Bangun ulang basis pengetahuan copilot",
             dependencies=[Depends(wajib(Kewenangan.KELOLA_MODEL))])
def muat_ulang(sesi: SesiDB) -> dict:
    """Susun ulang potongan pengetahuan setelah data atau katalog berubah."""
    copilot = dapatkan_copilot(sesi, muat_ulang=True)
    return {
        "jumlah_potongan": len(copilot.pengambil.potongan),
        "pesan": "Basis pengetahuan copilot dibangun ulang.",
    }


__all__ = ["router"]
