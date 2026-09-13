"""GeoAI Poverty Radar - data wilayah dan peta."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text

from nadi.api.deps import PenggunaAktif, SesiDB, wajib
from nadi.config import settings
from nadi.security.rbac import AMBANG_SEL_KECIL, Kewenangan

router = APIRouter(prefix="/wilayah", tags=["wilayah"])


@lru_cache(maxsize=1)
def _muat_geojson() -> dict:
    """Muat batas wilayah sekali, lalu tahan di memori.

    Berkasnya berukuran 1,7 megabita dan tidak pernah berubah selama aplikasi
    berjalan. Membacanya ulang pada setiap permintaan peta akan menambah
    ratusan milidetik tanpa alasan.
    """
    berkas: Path = settings.geo_dir / "pringsewu_desa.geojson"
    if not berkas.exists():
        return {"type": "FeatureCollection", "features": []}
    return json.loads(berkas.read_text(encoding="utf-8"))


def _gelombang_terakhir(sesi) -> int:
    return int(sesi.execute(text("SELECT MAX(gelombang) FROM snapshot_keluarga")).scalar() or 0)


@router.get("/pohon", summary="Struktur wilayah bertingkat", dependencies=[Depends(wajib(Kewenangan.BACA_AGREGAT))])
def pohon(sesi: SesiDB) -> dict:
    """Daftar kabupaten, kecamatan, dan pekon beserta hubungannya."""
    baris = sesi.execute(
        text(
            """
            SELECT id, kode, nama, jenis, induk_id, tingkat, lintang, bujur,
                   luas_km2, jumlah_penduduk, klasifikasi
            FROM wilayah ORDER BY tingkat, kode
            """
        )
    ).all()
    return {
        "jumlah": len(baris),
        "wilayah": [
            {
                "id": b.id,
                "kode": b.kode,
                "nama": b.nama,
                "jenis": b.jenis,
                "induk_id": b.induk_id,
                "tingkat": b.tingkat,
                "lintang": b.lintang,
                "bujur": b.bujur,
                "luas_km2": b.luas_km2,
                "jumlah_penduduk": b.jumlah_penduduk,
                "klasifikasi": b.klasifikasi,
            }
            for b in baris
        ],
    }


@router.get("/batas", summary="Batas wilayah dalam format GeoJSON", dependencies=[Depends(wajib(Kewenangan.BACA_PETA))])
def batas() -> dict:
    """Batas 131 pekon dan kelurahan.

    Bersumber dari layer batas desa Badan Informasi Geospasial. Kode wilayah
    pada berkas ini cocok seluruhnya dengan kode Kepmendagri yang dipakai
    basis data, sehingga penggabungan berlangsung tanpa tabel penerjemah.
    """
    return _muat_geojson()


@router.get("/statistik", summary="Statistik per wilayah", dependencies=[Depends(wajib(Kewenangan.BACA_PETA))])
def statistik(
    sesi: SesiDB,
    pengguna: PenggunaAktif,
    gelombang: int | None = Query(None),
    tingkat: int = Query(2, ge=1, le=2, description="1 kecamatan, 2 pekon/kelurahan"),
) -> dict:
    """Angka gabungan tiap wilayah untuk pewarnaan peta.

    Wilayah yang jumlah keluarganya di bawah ambang tidak menampilkan angka.
    Pada wilayah sekecil itu, satu warna pada peta hampir sama dengan menunjuk
    satu rumah - dan agregat berhenti menjadi agregat.
    """
    g = gelombang if gelombang is not None else _gelombang_terakhir(sesi)

    if tingkat == 2:
        kueri = """
            SELECT w.id, w.kode, w.nama, w.jenis, w.lintang, w.bujur, w.klasifikasi,
                   induk.kode AS kode_induk, induk.nama AS nama_induk,
                   st.jumlah_keluarga, st.jumlah_individu, st.jumlah_miskin,
                   st.persentase_miskin, st.jumlah_rentan, st.skor_rata_rata,
                   st.jumlah_risiko_tinggi, st.jumlah_risiko_sangat_tinggi,
                   st.persen_sanitasi_layak, st.persen_air_minum_layak,
                   st.persen_hunian_layak, st.persen_penerima_bantuan
            FROM statistik_wilayah st
            JOIN wilayah w      ON w.id = st.wilayah_id
            LEFT JOIN wilayah induk ON induk.id = w.induk_id
            WHERE st.gelombang = :g AND w.tingkat = 2
            ORDER BY st.persentase_miskin DESC
        """
    else:
        kueri = """
            SELECT kec.id, kec.kode, kec.nama, kec.jenis, kec.lintang, kec.bujur,
                   kec.klasifikasi, NULL AS kode_induk, NULL AS nama_induk,
                   SUM(st.jumlah_keluarga)  AS jumlah_keluarga,
                   SUM(st.jumlah_individu)  AS jumlah_individu,
                   SUM(st.jumlah_miskin)    AS jumlah_miskin,
                   ROUND(SUM(st.jumlah_miskin) * 100.0 / NULLIF(SUM(st.jumlah_keluarga),0), 2) AS persentase_miskin,
                   SUM(st.jumlah_rentan)    AS jumlah_rentan,
                   ROUND(AVG(st.skor_rata_rata), 1) AS skor_rata_rata,
                   SUM(st.jumlah_risiko_tinggi) AS jumlah_risiko_tinggi,
                   SUM(st.jumlah_risiko_sangat_tinggi) AS jumlah_risiko_sangat_tinggi,
                   ROUND(AVG(st.persen_sanitasi_layak), 1) AS persen_sanitasi_layak,
                   ROUND(AVG(st.persen_air_minum_layak), 1) AS persen_air_minum_layak,
                   ROUND(AVG(st.persen_hunian_layak), 1)   AS persen_hunian_layak,
                   ROUND(AVG(st.persen_penerima_bantuan), 1) AS persen_penerima_bantuan
            FROM statistik_wilayah st
            JOIN wilayah desa ON desa.id = st.wilayah_id
            JOIN wilayah kec  ON kec.id = desa.induk_id
            WHERE st.gelombang = :g
            GROUP BY kec.id, kec.kode, kec.nama, kec.jenis, kec.lintang, kec.bujur, kec.klasifikasi
            ORDER BY persentase_miskin DESC
        """

    baris = sesi.execute(text(kueri), {"g": g}).all()
    hasil = []
    disembunyikan = 0

    for b in baris:
        jumlah = int(b.jumlah_keluarga or 0)
        aman = jumlah >= AMBANG_SEL_KECIL
        if not aman:
            disembunyikan += 1
        hasil.append(
            {
                "id": b.id,
                "kode": b.kode,
                "nama": b.nama,
                "jenis": b.jenis,
                "kode_induk": b.kode_induk,
                "nama_induk": b.nama_induk,
                "lintang": b.lintang,
                "bujur": b.bujur,
                "klasifikasi": b.klasifikasi,
                "jumlah_keluarga": jumlah,
                "aman_ditampilkan": aman,
                **(
                    {
                        "jumlah_individu": int(b.jumlah_individu or 0),
                        "jumlah_miskin": int(b.jumlah_miskin or 0),
                        "persentase_miskin": float(b.persentase_miskin or 0),
                        "jumlah_rentan": int(b.jumlah_rentan or 0),
                        "skor_rata_rata": float(b.skor_rata_rata or 0),
                        "jumlah_risiko_tinggi": int(b.jumlah_risiko_tinggi or 0),
                        "jumlah_risiko_sangat_tinggi": int(b.jumlah_risiko_sangat_tinggi or 0),
                        "persen_sanitasi_layak": float(b.persen_sanitasi_layak or 0),
                        "persen_air_minum_layak": float(b.persen_air_minum_layak or 0),
                        "persen_hunian_layak": float(b.persen_hunian_layak or 0),
                        "persen_penerima_bantuan": float(b.persen_penerima_bantuan or 0),
                    }
                    if aman
                    else {"alasan_disembunyikan": "jumlah keluarga di bawah ambang penyajian"}
                ),
            }
        )

    return {
        "gelombang": g,
        "tingkat": tingkat,
        "jumlah_wilayah": len(hasil),
        "jumlah_disembunyikan": disembunyikan,
        "ambang_sel_kecil": AMBANG_SEL_KECIL,
        "wilayah": hasil,
    }


@router.get("/{kode}", summary="Rincian satu wilayah", dependencies=[Depends(wajib(Kewenangan.BACA_AGREGAT))])
def rincian(kode: str, sesi: SesiDB, gelombang: int | None = Query(None)) -> dict:
    """Rincian satu wilayah beserta tren dan sebaran faktor risikonya."""
    w = sesi.execute(
        text("SELECT id, kode, nama, jenis, tingkat, induk_id, luas_km2, jumlah_penduduk, klasifikasi FROM wilayah WHERE kode = :k"),
        {"k": kode},
    ).one_or_none()
    if w is None:
        raise HTTPException(404, f"Wilayah dengan kode '{kode}' tidak ditemukan.")

    tren = sesi.execute(
        text(
            """
            SELECT gelombang, jumlah_keluarga, jumlah_miskin, persentase_miskin,
                   jumlah_rentan, skor_rata_rata, persen_penerima_bantuan,
                   persen_sanitasi_layak, persen_air_minum_layak, persen_hunian_layak
            FROM statistik_wilayah WHERE wilayah_id = :id ORDER BY gelombang
            """
        ),
        {"id": w.id},
    ).all()

    return {
        "wilayah": {
            "id": w.id,
            "kode": w.kode,
            "nama": w.nama,
            "jenis": w.jenis,
            "tingkat": w.tingkat,
            "luas_km2": w.luas_km2,
            "jumlah_penduduk": w.jumlah_penduduk,
            "klasifikasi": w.klasifikasi,
        },
        "tren": [
            {
                "gelombang": int(t.gelombang),
                "jumlah_keluarga": int(t.jumlah_keluarga or 0),
                "jumlah_miskin": int(t.jumlah_miskin or 0),
                "persentase_miskin": float(t.persentase_miskin or 0),
                "jumlah_rentan": int(t.jumlah_rentan or 0),
                "skor_rata_rata": float(t.skor_rata_rata or 0),
                "persen_penerima_bantuan": float(t.persen_penerima_bantuan or 0),
                "persen_sanitasi_layak": float(t.persen_sanitasi_layak or 0),
                "persen_air_minum_layak": float(t.persen_air_minum_layak or 0),
                "persen_hunian_layak": float(t.persen_hunian_layak or 0),
            }
            for t in tren
        ],
    }


__all__ = ["router"]
