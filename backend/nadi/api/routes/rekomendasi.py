"""Intervention Recommender - usulan program lintas OPD."""

from __future__ import annotations

import json
import logging

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import select, text

from nadi.api.deps import KonteksPengguna, PenggunaAktif, SesiDB, catat_audit, wajib, wajib_buka_keluarga
from nadi.db.models import Program
from nadi.ml.dataset import muat_fitur_penilaian
from nadi.security.rbac import Kewenangan
from nadi.services.rekomendasi import MesinRekomendasi, paket_intervensi

logger = logging.getLogger("nadi.api.rekomendasi")
router = APIRouter(prefix="/rekomendasi", tags=["rekomendasi"])

#: Matriks fitur ditahan di memori setelah pemuatan pertama.
#: Membangunnya menuntut pembacaan dua ratus empat puluh ribu baris dan
#: memakan belasan detik - terlalu lama untuk diulang pada setiap permintaan,
#: sementara isinya tidak berubah selama data tidak dimuat ulang.
_TEMBOLOK: dict[str, object] = {}


def _fitur(sesi):
    if "X" not in _TEMBOLOK:
        from nadi.db.session import mesin

        X, meta = muat_fitur_penilaian(mesin)
        _TEMBOLOK["X"] = X
        _TEMBOLOK["meta"] = meta
        _TEMBOLOK["indeks"] = {
            (int(r.keluarga_id), int(r.gelombang)): i
            for i, r in enumerate(meta.itertuples())
        }
        logger.info("Matriks fitur dimuat ke memori: %d baris.", len(X))
    return _TEMBOLOK["X"], _TEMBOLOK["meta"], _TEMBOLOK["indeks"]


def kosongkan_tembolok() -> None:
    """Dipanggil setelah data dimuat ulang agar tembolok tidak basi."""
    _TEMBOLOK.clear()


@router.get("/program", summary="Katalog program", dependencies=[Depends(wajib(Kewenangan.BACA_REKOMENDASI))])
def katalog(sesi: SesiDB, jenis: str | None = Query(None), opd: str | None = Query(None)) -> dict:
    """Seluruh program pada basis pengetahuan beserta ketentuannya."""
    kueri = select(Program).order_by(Program.urutan_tampil)
    program = list(sesi.execute(kueri).scalars().all())

    hasil = []
    for p in program:
        daftar_opd = [o.singkatan for o in p.opd]
        if opd and opd not in [o.kode for o in p.opd]:
            continue
        if jenis and (p.jenis_intervensi.value if hasattr(p.jenis_intervensi, "value") else p.jenis_intervensi) != jenis:
            continue
        hasil.append(
            {
                "kode": p.kode,
                "nama": p.nama_resmi,
                "singkatan": p.singkatan,
                "deskripsi": p.deskripsi,
                "jenis_intervensi": p.jenis_intervensi.value if hasattr(p.jenis_intervensi, "value") else p.jenis_intervensi,
                "kementerian": p.kementerian,
                "opd": daftar_opd,
                "tingkat_eksekusi": p.tingkat_eksekusi.value if hasattr(p.tingkat_eksekusi, "value") else p.tingkat_eksekusi,
                "tindakan_daerah": p.tingkat_eksekusi.tindakan_daerah if hasattr(p.tingkat_eksekusi, "tindakan_daerah") else None,
                "basis_data": p.basis_data.value if hasattr(p.basis_data, "value") else p.basis_data,
                "sumber_dana": p.sumber_dana.value if hasattr(p.sumber_dana, "value") else p.sumber_dana,
                "frekuensi": p.frekuensi.value if hasattr(p.frekuensi, "value") else p.frekuensi,
                "desil_min": p.desil_min,
                "desil_maks": p.desil_maks,
                "biaya_satuan_tahunan": p.biaya_satuan_tahunan,
                "kuota_tahunan": p.kuota_tahunan,
                "status": p.status.value if hasattr(p.status, "value") else p.status,
                "tingkat_keyakinan": p.tingkat_keyakinan.value if hasattr(p.tingkat_keyakinan, "value") else p.tingkat_keyakinan,
                "dasar_hukum": p.dasar_hukum or [],
                "catatan": p.catatan,
                "faktor_risiko": [{"kode": f.kode, "nama": f.nama} for f in p.faktor_risiko],
                "manfaat": [
                    {
                        "komponen": m.komponen,
                        "label": m.label,
                        "nominal_per_tahun": m.nominal_per_tahun,
                        "satuan": m.satuan.value if hasattr(m.satuan, "value") else m.satuan,
                        "tingkat_keyakinan": m.tingkat_keyakinan.value if hasattr(m.tingkat_keyakinan, "value") else m.tingkat_keyakinan,
                    }
                    for m in p.manfaat
                ],
                "jumlah_aturan": len(p.aturan),
            }
        )

    return {
        "jumlah": len(hasil),
        "program": hasil,
        "catatan": (
            "Nominal bantuan berubah mengikuti kebijakan tahunan. Setiap angka "
            "membawa tingkat keyakinannya sendiri; angka bertanda 'perkiraan' wajib "
            "dikonfirmasi ke dinas pengampu sebelum dipakai menyusun anggaran."
        ),
    }


@router.get("/faktor-risiko", summary="Katalog faktor risiko", dependencies=[Depends(wajib(Kewenangan.BACA_REKOMENDASI))])
def faktor_risiko(sesi: SesiDB) -> dict:
    """Dua puluh faktor risiko beserta program yang menanganinya."""
    baris = sesi.execute(
        text(
            """
            SELECT f.kode, f.nama, f.deskripsi, f.dimensi, f.indikator,
                   f.bobot_dasar, f.jenis_intervensi_utama, f.fitur_terkait,
                   f.ekspresi_deteksi
            FROM faktor_risiko f WHERE f.aktif = 1 ORDER BY f.urutan_tampil
            """
        )
    ).all()

    peta_program = {}
    for r in sesi.execute(
        text(
            """
            SELECT f.kode AS kode_faktor, p.singkatan, p.kode AS kode_program, pf.kekuatan
            FROM program_faktor_risiko pf
            JOIN faktor_risiko f ON f.id = pf.faktor_risiko_id
            JOIN program p       ON p.id = pf.program_id
            ORDER BY pf.kekuatan DESC
            """
        )
    ).all():
        peta_program.setdefault(r.kode_faktor, []).append(
            {"kode": r.kode_program, "singkatan": r.singkatan, "kekuatan": float(r.kekuatan)}
        )

    return {
        "jumlah": len(baris),
        "faktor": [
            {
                "kode": b.kode,
                "nama": b.nama,
                "deskripsi": b.deskripsi,
                "dimensi": b.dimensi,
                "indikator": b.indikator,
                "bobot_dasar": float(b.bobot_dasar),
                "jenis_intervensi_utama": b.jenis_intervensi_utama,
                "fitur_terkait": json.loads(b.fitur_terkait) if isinstance(b.fitur_terkait, str) else (b.fitur_terkait or []),
                "terdeteksi_otomatis": b.ekspresi_deteksi is not None,
                "program": peta_program.get(b.kode, []),
            }
            for b in baris
        ],
    }


@router.get("/keluarga/{kode}", summary="Usulan intervensi untuk satu keluarga",
            dependencies=[Depends(wajib(Kewenangan.BACA_REKOMENDASI))])
def untuk_keluarga(
    kode: str,
    sesi: SesiDB,
    request: Request,
    pengguna: KonteksPengguna = Depends(wajib_buka_keluarga),
    gelombang: int | None = Query(None),
    maksimum: int = Query(6, ge=1, le=15),
) -> dict:
    """Susun usulan program beserta alasan dan penugasan OPD-nya."""
    baris = sesi.execute(
        text("SELECT id FROM keluarga WHERE kode_semu = :k"), {"k": kode.strip().upper()}
    ).one_or_none()
    if baris is None:
        raise HTTPException(404, f"Keluarga '{kode}' tidak ditemukan.")
    keluarga_id = int(baris.id)

    g = gelombang if gelombang is not None else int(
        sesi.execute(text("SELECT MAX(gelombang) FROM snapshot_keluarga")).scalar() or 0
    )

    X, meta, indeks = _fitur(sesi)
    posisi = indeks.get((keluarga_id, g))
    if posisi is None:
        raise HTTPException(404, f"Tidak ada kondisi keluarga ini pada gelombang {g}.")

    dominan = sesi.execute(
        text(
            "SELECT faktor_dominan FROM skor_kerentanan WHERE keluarga_id = :id AND gelombang = :g"
        ),
        {"id": keluarga_id, "g": g},
    ).scalar()
    faktor = json.loads(dominan) if isinstance(dominan, str) else (dominan or [])

    mesin_rekomendasi = MesinRekomendasi(sesi)
    usulan = mesin_rekomendasi.usulkan(X, posisi, faktor_dominan=faktor, maksimum=maksimum)

    catat_audit(
        sesi, pengguna, "lihat_rekomendasi",
        entitas="keluarga", entitas_id=kode,
        ringkasan=f"{len(usulan)} usulan pada gelombang {g}", request=request,
    )
    sesi.commit()

    return {
        "kode_keluarga": kode,
        "gelombang": g,
        "faktor_dominan": faktor,
        "usulan": [u.ke_dict() for u in usulan],
        "paket": paket_intervensi(usulan),
        "penafian": (
            "Usulan ini disusun dari pencocokan aturan kelayakan dengan kondisi "
            "keluarga. Usulan BUKAN penetapan penerima. Penetapan tetap melalui "
            "musyawarah pekon dan keputusan pejabat berwenang."
        ),
    }


__all__ = ["kosongkan_tembolok", "router"]
