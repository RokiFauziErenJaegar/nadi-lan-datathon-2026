"""Executive Command Center - ringkasan keadaan kabupaten."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import text

from nadi.api.deps import PenggunaAktif, SesiDB, wajib
from nadi.security.rbac import AMBANG_SEL_KECIL, Kewenangan
from nadi.synth.parameter import ACUAN

router = APIRouter(prefix="/ringkasan", tags=["ringkasan"])


def _gelombang_terakhir(sesi) -> int:
    return int(sesi.execute(text("SELECT MAX(gelombang) FROM snapshot_keluarga")).scalar() or 0)


def _label_anomali(kode: str | None) -> str | None:
    """Ubah kode jenis anomali menjadi kalimat yang dibaca petugas."""
    if not kode:
        return None
    from nadi.db.enums import JenisAnomali

    try:
        return JenisAnomali(kode).label
    except ValueError:
        return kode.replace("_", " ").capitalize()


@router.get("", summary="Ringkasan keadaan kabupaten", dependencies=[Depends(wajib(Kewenangan.BACA_AGREGAT))])
def ringkasan(
    sesi: SesiDB,
    pengguna: PenggunaAktif,
    gelombang: int | None = Query(None, description="Gelombang yang ditampilkan; bawaannya terkini"),
) -> dict:
    """Angka pokok yang perlu dilihat pimpinan dalam satu layar."""
    g = gelombang if gelombang is not None else _gelombang_terakhir(sesi)

    pokok = sesi.execute(
        text(
            """
            SELECT COUNT(*)                                   AS keluarga,
                   SUM(s.jumlah_anggota)                      AS jiwa,
                   SUM(s.status_miskin)                       AS miskin,
                   SUM(CASE WHEN s.status_miskin = 0 AND s.rasio_garis_kemiskinan < 1.5
                            THEN 1 ELSE 0 END)                AS rentan,
                   AVG(s.rasio_garis_kemiskinan)              AS rasio_rata,
                   SUM(CASE WHEN s.jumlah_program_diterima = 0 THEN 1 ELSE 0 END) AS tanpa_bantuan,
                   AVG(s.desil_kesejahteraan)                 AS desil_rata,
                   SUM(s.nilai_bantuan_bulanan)               AS bantuan_bulanan
            FROM snapshot_keluarga s WHERE s.gelombang = :g
            """
        ),
        {"g": g},
    ).one()

    risiko = sesi.execute(
        text(
            """
            SELECT kategori, COUNT(*) AS n, AVG(skor) AS rata
            FROM skor_kerentanan WHERE gelombang = :g GROUP BY kategori
            """
        ),
        {"g": g},
    ).all()

    tren = sesi.execute(
        text(
            """
            SELECT s.gelombang,
                   MIN(s.tanggal_kondisi)                     AS tanggal,
                   COUNT(*)                                   AS keluarga,
                   SUM(s.jumlah_anggota)                      AS jiwa,
                   SUM(s.status_miskin * s.jumlah_anggota)    AS jiwa_miskin,
                   AVG(s.status_miskin)                       AS bagian_kk_miskin
            FROM snapshot_keluarga s GROUP BY s.gelombang ORDER BY s.gelombang
            """
        )
    ).all()

    antrean = sesi.execute(
        text(
            """
            SELECT jenis, COUNT(*) AS n, AVG(skor_prioritas) AS rata
            FROM kasus WHERE gelombang = :g GROUP BY jenis ORDER BY n DESC
            """
        ),
        {"g": g},
    ).all()

    perburukan = sesi.execute(
        text(
            """
            SELECT COUNT(*) FROM skor_kerentanan
            WHERE gelombang = :g AND perubahan_dari_sebelumnya >= 12
            """
        ),
        {"g": g},
    ).scalar() or 0

    jiwa = int(pokok.jiwa or 0)
    jiwa_miskin = sum(int(t.jiwa_miskin or 0) for t in tren if t.gelombang == g)

    return {
        "gelombang": g,
        "cakupan": {
            "keluarga": int(pokok.keluarga or 0),
            "jiwa": jiwa,
            "keterangan": (
                "Cakupan sistem ini adalah keluarga desil 1 sampai 5 menurut DTSEN, "
                f"yakni sekitar {ACUAN.jumlah_keluarga_desil_1_5:,} keluarga di Kabupaten "
                "Pringsewu. Data yang ditampilkan bersifat sintetis."
            ).replace(",", "."),
        },
        "kemiskinan": {
            "keluarga_miskin": int(pokok.miskin or 0),
            "jiwa_miskin": jiwa_miskin,
            "persen_jiwa_miskin": round(jiwa_miskin / jiwa * 100, 2) if jiwa else 0,
            "keluarga_rentan": int(pokok.rentan or 0),
            "keterangan_rentan": (
                "Rentan berarti pengeluaran per kapita berada antara satu sampai satu "
                f"setengah kali garis kemiskinan (Rp{ACUAN.garis_kemiskinan:,.0f} sampai "
                f"Rp{ACUAN.garis_kerentanan:,.0f}). Kelompok ini belum tercatat miskin, "
                "namun satu guncangan sudah cukup menjatuhkannya."
            ).replace(",", "."),
            "garis_kemiskinan": ACUAN.garis_kemiskinan,
            "garis_kerentanan": ACUAN.garis_kerentanan,
            "garis_kerentanan_turunan": True,
            "rasio_rata_rata": round(float(pokok.rasio_rata or 0), 3),
            "desil_rata_rata": round(float(pokok.desil_rata or 0), 2),
        },
        "risiko": {
            "sebaran": [
                {"kategori": r.kategori, "jumlah": int(r.n), "skor_rata": round(float(r.rata or 0), 1)}
                for r in risiko
            ],
            "memburuk_tajam": int(perburukan),
            "keterangan_memburuk": (
                "Keluarga yang skor kerentanannya naik dua belas poin atau lebih sejak "
                "pemutakhiran sebelumnya. Sebagian besar di antaranya belum tercatat miskin."
            ),
        },
        "perlindungan_sosial": {
            "tanpa_bantuan": int(pokok.tanpa_bantuan or 0),
            "nilai_bantuan_bulanan": round(float(pokok.bantuan_bulanan or 0), 0),
            "nilai_bantuan_tahunan": round(float(pokok.bantuan_bulanan or 0) * 12, 0),
        },
        "antrean": {
            "total": sum(int(a.n) for a in antrean),
            "per_jenis": [
                {
                    "jenis": a.jenis,
                    # Label berbahasa manusia disertakan di sini, bukan disusun
                    # ulang di antarmuka. Menempatkannya di satu tempat menjaga
                    # agar kalimat yang dibaca petugas pada layar ringkasan sama
                    # persis dengan yang dibaca pada antrean kasus.
                    "label": _label_anomali(a.jenis),
                    "jumlah": int(a.n),
                    "prioritas_rata": round(float(a.rata or 0), 1),
                }
                for a in antrean
            ],
        },
        "tren": [
            {
                "gelombang": int(t.gelombang),
                "tanggal": str(t.tanggal),
                "jiwa": int(t.jiwa or 0),
                "jiwa_miskin": int(t.jiwa_miskin or 0),
                "persen_jiwa_miskin": round(int(t.jiwa_miskin or 0) / max(1, int(t.jiwa or 1)) * 100, 2),
                "persen_keluarga_miskin": round(float(t.bagian_kk_miskin or 0) * 100, 2),
            }
            for t in tren
        ],
        "acuan_bps": {
            "persen_miskin_kabupaten_2023": ACUAN.persen_miskin_2023,
            "persen_miskin_kabupaten_2024": ACUAN.persen_miskin_2024,
            "persen_miskin_kabupaten_2025": ACUAN.persen_miskin_2025,
            "keterangan": (
                "Angka kabupaten dihitung terhadap seluruh penduduk menurut proyeksi BPS. "
                "Angka pada sistem ini dihitung terhadap cakupan desil 1 sampai 5, "
                "sehingga persentasenya lebih tinggi meski jumlah orangnya sama."
            ),
        },
        "cakupan_pengguna": pengguna.cakupan.value,
    }


@router.get("/kecamatan", summary="Ringkasan per kecamatan", dependencies=[Depends(wajib(Kewenangan.BACA_AGREGAT))])
def per_kecamatan(sesi: SesiDB, gelombang: int | None = Query(None)) -> dict:
    """Peringkat kecamatan menurut beban kemiskinan dan kerentanan."""
    g = gelombang if gelombang is not None else _gelombang_terakhir(sesi)
    baris = sesi.execute(
        text(
            """
            SELECT kec.kode, kec.nama, kec.jumlah_penduduk, kec.luas_km2, kec.klasifikasi,
                   COUNT(*)                                    AS keluarga,
                   SUM(s.jumlah_anggota)                       AS jiwa,
                   SUM(s.status_miskin)                        AS miskin,
                   AVG(s.status_miskin) * 100.0                AS persen_miskin,
                   AVG(COALESCE(sk.skor, 0))                   AS skor_rata,
                   SUM(CASE WHEN sk.kategori IN ('tinggi','sangat_tinggi') THEN 1 ELSE 0 END) AS risiko_tinggi,
                   SUM(CASE WHEN s.jumlah_program_diterima = 0 THEN 1 ELSE 0 END) AS tanpa_bantuan
            FROM snapshot_keluarga s
            JOIN keluarga k   ON k.id = s.keluarga_id
            JOIN wilayah desa ON desa.id = k.wilayah_id
            JOIN wilayah kec  ON kec.id = desa.induk_id
            LEFT JOIN skor_kerentanan sk
                   ON sk.keluarga_id = s.keluarga_id AND sk.gelombang = s.gelombang
            WHERE s.gelombang = :g
            GROUP BY kec.kode, kec.nama, kec.jumlah_penduduk, kec.luas_km2, kec.klasifikasi
            ORDER BY persen_miskin DESC
            """
        ),
        {"g": g},
    ).all()

    return {
        "gelombang": g,
        "kecamatan": [
            {
                "kode": b.kode,
                "nama": b.nama,
                "penduduk_dukcapil": b.jumlah_penduduk,
                "luas_km2": b.luas_km2,
                "klasifikasi": b.klasifikasi,
                "keluarga_terdata": int(b.keluarga),
                "jiwa_terdata": int(b.jiwa or 0),
                "keluarga_miskin": int(b.miskin or 0),
                "persen_keluarga_miskin": round(float(b.persen_miskin or 0), 2),
                "skor_rata_rata": round(float(b.skor_rata or 0), 1),
                "risiko_tinggi": int(b.risiko_tinggi or 0),
                "tanpa_bantuan": int(b.tanpa_bantuan or 0),
                "aman_ditampilkan": int(b.keluarga) >= AMBANG_SEL_KECIL,
            }
            for b in baris
        ],
        "ambang_sel_kecil": AMBANG_SEL_KECIL,
    }


__all__ = ["router"]
