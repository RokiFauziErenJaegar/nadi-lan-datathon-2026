"""What-if Policy Simulator - aritmetika cakupan, biaya, dan kapasitas."""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import text

from nadi.api.deps import SesiDB, wajib
from nadi.security.rbac import Kewenangan
from nadi.services.simulator import (
    BATAS_DANA_DESA,
    PENAFIAN,
    SUMBER_RTLH,
    hitung_cakupan,
    kurva_kapasitas,
    simulasi_dana_desa,
    simulasi_rtlh,
)
from nadi.synth.parameter import ACUAN

logger = logging.getLogger("nadi.api.simulasi")
router = APIRouter(prefix="/simulasi", tags=["simulasi"])


@router.get("/keterangan", summary="Batas dan kemampuan simulator")
def keterangan() -> dict:
    """Nyatakan terus terang apa yang dapat dan tidak dapat dijawab simulator."""
    return {
        "dapat_dijawab": [
            "Berapa keluarga tercakup bila ambang desil digeser, dan berapa biayanya.",
            "Berapa tahun sisa kebutuhan perbaikan rumah tuntas pada laju tertentu.",
            "Berapa keluarga terjangkau bantuan langsung tunai dari pagu Dana Desa satu pekon.",
            "Berapa tambahan keluarga yang ditemukan bila kapasitas verifikasi dinaikkan.",
        ],
        "tidak_dapat_dijawab": [
            "Berapa penurunan angka kemiskinan akibat sebuah kebijakan.",
            "Program mana yang lebih efektif dibanding program lain.",
            "Bagaimana perilaku penerima berubah setelah menerima bantuan.",
        ],
        "alasan": (
            "Menjawab pertanyaan kelompok kedua menuntut desain evaluasi dampak "
            "tersendiri - pembanding yang sepadan, atau penetapan acak. Data "
            "pengamatan saja tidak dapat memisahkan pengaruh program dari perbedaan "
            "yang memang sudah ada antar-keluarga. Angka yang dihasilkan akan "
            "terdengar berwibawa dan menyesatkan."
        ),
        "penafian": PENAFIAN,
    }


@router.get("/cakupan", summary="Kalkulator cakupan dan biaya",
            dependencies=[Depends(wajib(Kewenangan.JALANKAN_SIMULASI))])
def cakupan(
    sesi: SesiDB,
    desil_maksimum: int = Query(3, ge=1, le=10),
    biaya_satuan_tahunan: float = Query(2_400_000, gt=0),
    pagu: float | None = Query(None, gt=0),
    hanya_belum_menerima: bool = Query(False),
    gelombang: int | None = Query(None),
) -> dict:
    """Hitung berapa keluarga tercakup pagu, dan siapa yang tidak.

    Keluaran yang paling berharga adalah daftar keluarga yang layak namun tidak
    tercakup. Ia mengubah keterbatasan anggaran dari angka menjadi daftar yang
    dapat dibawa ke rapat.
    """
    g = gelombang if gelombang is not None else int(
        sesi.execute(text("SELECT MAX(gelombang) FROM snapshot_keluarga")).scalar() or 0
    )

    syarat = ["s.gelombang = :g", "s.desil_kesejahteraan <= :desil"]
    if hanya_belum_menerima:
        syarat.append("s.jumlah_program_diterima = 0")

    baris = sesi.execute(
        text(
            f"""
            SELECT k.kode_semu, induk.nama AS kecamatan, w.nama AS desa,
                   s.desil_kesejahteraan, s.jumlah_anggota,
                   COALESCE(sk.skor, 0) AS skor
            FROM snapshot_keluarga s
            JOIN keluarga k        ON k.id = s.keluarga_id
            JOIN wilayah w         ON w.id = k.wilayah_id
            LEFT JOIN wilayah induk ON induk.id = w.induk_id
            LEFT JOIN skor_kerentanan sk
                   ON sk.keluarga_id = s.keluarga_id AND sk.gelombang = s.gelombang
            WHERE {' AND '.join(syarat)}
            """
        ),
        {"g": g, "desil": desil_maksimum},
    ).all()

    df = pd.DataFrame(baris, columns=["kode_semu", "kecamatan", "desa", "desil", "jumlah_anggota", "skor"])
    hasil = hitung_cakupan(
        df,
        biaya_satuan_tahunan=biaya_satuan_tahunan,
        pagu=pagu,
        asumsi=[
            f"Sasaran dibatasi desil 1 sampai {desil_maksimum}.",
            f"Biaya per penerima Rp{biaya_satuan_tahunan:,.0f} per tahun.".replace(",", "."),
            "Pelayanan diurutkan menurut skor kerentanan, yang paling rentan lebih dahulu.",
            "Keluarga yang belum menerima program apa pun disaring lebih dahulu."
            if hanya_belum_menerima
            else "Seluruh keluarga pada rentang desil disertakan.",
        ],
    )
    return {"gelombang": g, **hasil.ke_dict()}


class PermintaanDanaDesa(BaseModel):
    pagu: float = Field(gt=0, description="Pagu Dana Desa satu pekon, dalam rupiah")
    porsi_blt: float = Field(0.15, ge=0, le=1)
    porsi_ketahanan_pangan: float = Field(0.20, ge=0, le=1)
    porsi_stunting: float = Field(0.10, ge=0, le=1)
    porsi_padat_karya: float = Field(0.15, ge=0, le=1)
    bulan_blt: int = Field(3, ge=1, le=12)


@router.post("/dana-desa", summary="Simulasi alokasi Dana Desa satu pekon",
             dependencies=[Depends(wajib(Kewenangan.JALANKAN_SIMULASI))])
def dana_desa(data: PermintaanDanaDesa) -> dict:
    """Bagi pagu Dana Desa dan periksa kepatuhannya terhadap batas regulasi."""
    h = simulasi_dana_desa(
        data.pagu,
        porsi_blt=data.porsi_blt,
        porsi_ketahanan_pangan=data.porsi_ketahanan_pangan,
        porsi_stunting=data.porsi_stunting,
        porsi_padat_karya=data.porsi_padat_karya,
        bulan_blt=data.bulan_blt,
    )
    return {
        "pagu": h.pagu,
        "sah": h.sah,
        "pelanggaran": h.pelanggaran,
        "alokasi": h.alokasi,
        "kpm_blt": h.kpm_blt,
        "bulan_blt": h.bulan_blt,
        "catatan": h.catatan,
        "batas_regulasi": BATAS_DANA_DESA,
        "penafian": h.penafian,
    }


@router.get("/rtlh", summary="Simulasi penuntasan rumah tidak layak huni",
            dependencies=[Depends(wajib(Kewenangan.JALANKAN_SIMULASI))])
def rtlh(
    backlog: int | None = Query(None, ge=1),
    bsps: int = Query(0, ge=0, description="Unit per tahun dari BSPS APBN"),
    rst: int = Query(0, ge=0, description="Unit per tahun dari RST Kemensos"),
    rutilahu_apbd: int = Query(80, ge=0, description="Unit per tahun dari APBD kabupaten"),
    dana_desa: int = Query(0, ge=0, description="Unit per tahun dari Dana Desa"),
    pertumbuhan_backlog: float = Query(0.0, ge=0, le=0.2,
                                       description="Bagian rumah yang memburuk per tahun"),
) -> dict:
    """Hitung berapa tahun sisa kebutuhan perbaikan rumah akan tuntas.

    Parameter ``pertumbuhan_backlog`` mengajukan pertanyaan yang biasanya
    dihindari: rumah juga menua. Pada laju penanganan sekarang, memasukkan
    pemburukan tiga persen per tahun saja sudah membuat sisa kebutuhan tidak
    pernah tuntas.
    """
    h = simulasi_rtlh(
        backlog=backlog,
        kapasitas={
            "BSPS": bsps,
            "RST": rst,
            "RUTILAHU-D": rutilahu_apbd,
            "DANA-DESA": dana_desa,
        },
        pertumbuhan_backlog_tahunan=pertumbuhan_backlog,
    )
    return {
        "backlog": h.backlog,
        "kapasitas_tahunan": h.kapasitas_tahunan,
        "tahun_tuntas": None if h.tahun_tuntas == float("inf") else h.tahun_tuntas,
        "tuntas_dalam_horizon": h.tahun_tuntas != float("inf"),
        "biaya_tahunan": h.biaya_tahunan,
        "biaya_total": h.biaya_total,
        "rincian_sumber": h.rincian_sumber,
        "lintasan": h.lintasan,
        "catatan": h.catatan,
        "acuan": {
            "backlog_pringsewu": ACUAN.backlog_rtlh,
            "kuota_apbd_tahunan": ACUAN.kuota_rutilahu_apbd_tahunan,
            "sumber": "Dinas Sosial Kabupaten Pringsewu, realisasi 2025",
        },
        "sumber_tersedia": [
            {
                "kode": s.kode,
                "nama": s.nama,
                "nominal_per_unit": s.nominal_per_unit,
                "sumber_dana": s.sumber_dana,
                "tingkat_keyakinan": s.tingkat_keyakinan,
            }
            for s in SUMBER_RTLH
        ],
        "penafian": h.penafian,
    }


@router.get("/kapasitas-verifikasi", summary="Kurva hasil terhadap kapasitas verifikasi",
            dependencies=[Depends(wajib(Kewenangan.JALANKAN_SIMULASI))])
def kapasitas(sesi: SesiDB, gelombang: int | None = Query(None)) -> dict:
    """Berapa tambahan keluarga yang ditemukan bila petugas ditambah.

    Kurvanya melandai, dan itulah jawabannya. Seratus kunjungan pertama bernilai
    jauh lebih besar daripada seratus kunjungan berikutnya - kenyataan yang
    sering hilang ketika penambahan kapasitas dibicarakan sebagai garis lurus.
    """
    g = gelombang if gelombang is not None else int(
        sesi.execute(text("SELECT MAX(gelombang) FROM skor_kerentanan")).scalar() or 0
    )
    # Gelombang terakhir tidak memiliki hasil yang sudah diketahui, sehingga
    # kurva dibentuk dari gelombang sebelumnya - satu-satunya yang hasilnya
    # sudah dapat diperiksa.
    g_evaluasi = max(0, g - 1)

    baris = sesi.execute(
        text(
            """
            SELECT sk.skor, s_depan.status_miskin AS miskin_berikutnya
            FROM skor_kerentanan sk
            JOIN snapshot_keluarga s_depan
              ON s_depan.keluarga_id = sk.keluarga_id
             AND s_depan.gelombang = sk.gelombang + 1
            WHERE sk.gelombang = :g
            """
        ),
        {"g": g_evaluasi},
    ).all()

    if not baris:
        raise HTTPException(404, "Belum ada skor yang hasilnya dapat diperiksa.")

    skor = np.array([float(b.skor) for b in baris])
    y = np.array([bool(b.miskin_berikutnya) for b in baris])
    hasil = kurva_kapasitas(y, skor)
    hasil["gelombang_dinilai"] = g_evaluasi
    hasil["keterangan"] = (
        f"Dihitung pada gelombang {g_evaluasi}, yakni gelombang terakhir yang "
        "hasilnya sudah dapat diperiksa."
    )
    return hasil


__all__ = ["router"]
