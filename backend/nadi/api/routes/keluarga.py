"""Household Digital Twin - profil keluarga sepanjang waktu."""

from __future__ import annotations

import json
import logging

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import text

from nadi.api.deps import KonteksPengguna, PenggunaAktif, SesiDB, catat_audit, wajib, wajib_buka_keluarga
from nadi.db import enums as E
from nadi.security.rbac import CakupanData, Kewenangan
from nadi.synth.parameter import ACUAN

logger = logging.getLogger("nadi.api.keluarga")
router = APIRouter(prefix="/keluarga", tags=["keluarga"])


def _periksa_wilayah(sesi, pengguna: PenggunaAktif, wilayah_id: int) -> None:
    """Tolak akses ke keluarga di luar wilayah penugasan."""
    if not pengguna.dibatasi_wilayah:
        return
    kode = sesi.execute(
        text(
            """
            SELECT COALESCE(induk.kode, w.kode) AS kode_kec
            FROM wilayah w LEFT JOIN wilayah induk ON induk.id = w.induk_id
            WHERE w.id = :id
            """
        ),
        {"id": wilayah_id},
    ).scalar()
    if kode not in pengguna.wilayah_akses:
        raise HTTPException(
            403,
            "Keluarga ini berada di luar wilayah penugasan Anda. "
            f"Wilayah yang dapat Anda akses: {', '.join(pengguna.wilayah_akses)}.",
        )


def _kode_ke_id(sesi, kode: str) -> tuple[int, int]:
    baris = sesi.execute(
        text("SELECT id, wilayah_id FROM keluarga WHERE kode_semu = :k"),
        {"k": kode.strip().upper()},
    ).one_or_none()
    if baris is None:
        raise HTTPException(404, f"Keluarga dengan kode '{kode}' tidak ditemukan.")
    return int(baris.id), int(baris.wilayah_id)


def _label(kelas, nilai):
    """Ubah kode menjadi label yang terbaca, tanpa menggagalkan kode asing."""
    if nilai is None:
        return None
    try:
        return kelas(nilai).label
    except (ValueError, KeyError):
        return f"kode tidak dikenal ({nilai})"


@router.get("/cari", summary="Cari keluarga menurut penyaring", dependencies=[Depends(wajib(Kewenangan.BACA_KELUARGA))])
def cari(
    sesi: SesiDB,
    pengguna: KonteksPengguna = Depends(wajib_buka_keluarga),
    kecamatan: str | None = Query(None, description="Kode kecamatan"),
    desa: str | None = Query(None, description="Kode pekon atau kelurahan"),
    kategori: str | None = Query(None, description="rendah, sedang, tinggi, sangat_tinggi"),
    hanya_miskin: bool = Query(False),
    tanpa_bantuan: bool = Query(False),
    gelombang: int | None = Query(None),
    batas: int = Query(50, ge=1, le=200),
    lewati: int = Query(0, ge=0),
) -> dict:
    """Cari keluarga menurut wilayah, kategori risiko, dan status bantuan."""
    g = gelombang if gelombang is not None else int(
        sesi.execute(text("SELECT MAX(gelombang) FROM snapshot_keluarga")).scalar() or 0
    )

    syarat = ["s.gelombang = :g"]
    param: dict = {"g": g, "batas": batas, "lewati": lewati}

    if pengguna.dibatasi_wilayah:
        # Lihat catatan pada nadi/api/routes/antrean.py: klausa IN memerlukan
        # satu parameter bernama per nilai, bukan sebuah tuple.
        kunci = [f"izin{i}" for i in range(len(pengguna.wilayah_akses))]
        syarat.append(
            "COALESCE(induk.kode, w.kode) IN (" + ", ".join(f":{k}" for k in kunci) + ")"
        )
        param.update(dict(zip(kunci, pengguna.wilayah_akses)))
    if kecamatan:
        syarat.append("COALESCE(induk.kode, w.kode) = :kec")
        param["kec"] = kecamatan
    if desa:
        syarat.append("w.kode = :desa")
        param["desa"] = desa
    if kategori:
        syarat.append("sk.kategori = :kat")
        param["kat"] = kategori
    if hanya_miskin:
        syarat.append("s.status_miskin = 1")
    if tanpa_bantuan:
        syarat.append("s.jumlah_program_diterima = 0")

    kueri = f"""
        SELECT k.kode_semu, w.nama AS desa, induk.nama AS kecamatan,
               s.desil_kesejahteraan, s.status_miskin, s.rasio_garis_kemiskinan,
               s.jumlah_anggota, s.jumlah_program_diterima,
               sk.skor, sk.kategori, sk.perubahan_dari_sebelumnya
        FROM snapshot_keluarga s
        JOIN keluarga k        ON k.id = s.keluarga_id
        JOIN wilayah w         ON w.id = k.wilayah_id
        LEFT JOIN wilayah induk ON induk.id = w.induk_id
        LEFT JOIN skor_kerentanan sk
               ON sk.keluarga_id = s.keluarga_id AND sk.gelombang = s.gelombang
        WHERE {' AND '.join(syarat)}
        ORDER BY COALESCE(sk.skor, 0) DESC
        LIMIT :batas OFFSET :lewati
    """
    baris = sesi.execute(text(kueri), param).all()

    return {
        "gelombang": g,
        "jumlah": len(baris),
        "keluarga": [
            {
                "kode": b.kode_semu,
                "desa": b.desa,
                "kecamatan": b.kecamatan,
                "desil": b.desil_kesejahteraan,
                "miskin": bool(b.status_miskin),
                "rasio_garis_kemiskinan": round(float(b.rasio_garis_kemiskinan or 0), 2),
                "jumlah_anggota": b.jumlah_anggota,
                "jumlah_program": b.jumlah_program_diterima,
                "skor": round(float(b.skor), 1) if b.skor is not None else None,
                "kategori": b.kategori,
                "perubahan_skor": round(float(b.perubahan_dari_sebelumnya), 1)
                if b.perubahan_dari_sebelumnya is not None
                else None,
            }
            for b in baris
        ],
    }


@router.get("/{kode}", summary="Profil lengkap satu keluarga", dependencies=[Depends(wajib(Kewenangan.BACA_KELUARGA))])
def profil(
    kode: str,
    sesi: SesiDB,
    request: Request,
    pengguna: KonteksPengguna = Depends(wajib_buka_keluarga),
) -> dict:
    """Digital twin satu keluarga: kondisi, riwayat, guncangan, dan skornya.

    Setiap pembukaan profil dicatat pada jejak audit. Ini bukan kecurigaan
    terhadap petugas melainkan pemenuhan kewajiban pengendali data pribadi:
    setiap akses terhadap data seseorang harus dapat dipertanggungjawabkan
    kepada orang tersebut.
    """
    keluarga_id, wilayah_id = _kode_ke_id(sesi, kode)
    _periksa_wilayah(sesi, pengguna, wilayah_id)

    catat_audit(
        sesi, pengguna, "buka_keluarga",
        entitas="keluarga", entitas_id=kode,
        ringkasan=f"Membuka profil {kode}", request=request,
    )
    sesi.commit()

    dasar = sesi.execute(
        text(
            """
            SELECT k.kode_semu, k.lintang, k.bujur, k.sumber_data, k.tanggal_terdaftar,
                   w.kode AS kode_desa, w.nama AS desa, w.jenis AS jenis_desa,
                   w.klasifikasi, induk.kode AS kode_kec, induk.nama AS kecamatan
            FROM keluarga k
            JOIN wilayah w ON w.id = k.wilayah_id
            LEFT JOIN wilayah induk ON induk.id = w.induk_id
            WHERE k.id = :id
            """
        ),
        {"id": keluarga_id},
    ).one()

    anggota = sesi.execute(
        text(
            """
            SELECT kode_semu, urutan, hubungan_kk, jenis_kelamin, tahun_lahir,
                   status_perkawinan, partisipasi_sekolah, pendidikan_tertinggi,
                   status_kegiatan, lapangan_usaha, status_pekerjaan, jumlah_usaha,
                   jenis_disabilitas, penyakit_kronis, status_gizi_balita,
                   sedang_hamil, punya_jaminan_kesehatan
            FROM anggota_keluarga WHERE keluarga_id = :id ORDER BY urutan
            """
        ),
        {"id": keluarga_id},
    ).all()

    riwayat = sesi.execute(
        text(
            """
            SELECT s.gelombang, s.tanggal_kondisi, s.pengeluaran_per_kapita,
                   s.rasio_garis_kemiskinan, s.status_miskin, s.desil_kesejahteraan,
                   s.jumlah_anggota, s.jumlah_program_diterima, s.nilai_bantuan_bulanan,
                   s.jumlah_ber_jkn, s.luas_lantai_m2, s.umur_data_bulan,
                   s.kelengkapan_data, s.jenis_lantai_terluas, s.jenis_dinding_terluas,
                   s.jenis_atap_terluas, s.sumber_air_minum_utama, s.fasilitas_bab,
                   s.jenis_kloset, s.pembuangan_akhir_tinja, s.daya_terpasang,
                   s.bahan_bakar_utama_memasak,
                   sk.skor, sk.kategori, sk.probabilitas, sk.perubahan_dari_sebelumnya,
                   sk.faktor_dominan, sk.kontribusi_fitur, sk.peringkat_kabupaten
            FROM snapshot_keluarga s
            LEFT JOIN skor_kerentanan sk
                   ON sk.keluarga_id = s.keluarga_id AND sk.gelombang = s.gelombang
            WHERE s.keluarga_id = :id ORDER BY s.gelombang
            """
        ),
        {"id": keluarga_id},
    ).all()

    guncangan = sesi.execute(
        text(
            """
            SELECT gelombang, tanggal_kejadian, jenis, keparahan, dampak_pendapatan_persen
            FROM guncangan WHERE keluarga_id = :id ORDER BY gelombang
            """
        ),
        {"id": keluarga_id},
    ).all()

    program = sesi.execute(
        text(
            """
            SELECT p.kode, p.nama_resmi, p.singkatan, p.jenis_intervensi,
                   kp.gelombang_mulai, kp.gelombang_selesai, kp.status
            FROM kepesertaan_program kp JOIN program p ON p.id = kp.program_id
            WHERE kp.keluarga_id = :id ORDER BY kp.gelombang_mulai
            """
        ),
        {"id": keluarga_id},
    ).all()

    kasus = sesi.execute(
        text(
            """
            SELECT kode_semu, gelombang, jenis, status, skor_prioritas,
                   tingkat_prioritas, ringkasan
            FROM kasus WHERE keluarga_id = :id ORDER BY gelombang DESC, skor_prioritas DESC
            """
        ),
        {"id": keluarga_id},
    ).all()

    terkini = riwayat[-1] if riwayat else None
    tahun_kini = ACUAN and 2026

    return {
        "keluarga": {
            "kode": dasar.kode_semu,
            "wilayah": {
                "desa": dasar.desa,
                "kode_desa": dasar.kode_desa,
                "jenis": dasar.jenis_desa,
                "kecamatan": dasar.kecamatan,
                "kode_kecamatan": dasar.kode_kec,
                "klasifikasi": dasar.klasifikasi,
            },
            "koordinat": {
                "lintang": dasar.lintang,
                "bujur": dasar.bujur,
                "catatan": "Koordinat digeser acak dalam radius 250 meter demi privasi.",
            },
            "sumber_data": dasar.sumber_data,
            "tanggal_terdaftar": str(dasar.tanggal_terdaftar) if dasar.tanggal_terdaftar else None,
        },
        "anggota": [
            {
                "kode": a.kode_semu,
                "urutan": a.urutan,
                "hubungan": _label(E.HubunganKK, a.hubungan_kk),
                "jenis_kelamin": _label(E.JenisKelamin, a.jenis_kelamin),
                "umur": tahun_kini - a.tahun_lahir,
                "status_perkawinan": _label(E.StatusPerkawinan, a.status_perkawinan),
                "partisipasi_sekolah": _label(E.PartisipasiSekolah, a.partisipasi_sekolah),
                "pendidikan": _label(E.PendidikanTertinggi, a.pendidikan_tertinggi),
                "kegiatan": _label(E.StatusKegiatan, a.status_kegiatan),
                "lapangan_usaha": _label(E.LapanganUsaha, a.lapangan_usaha),
                "status_pekerjaan": _label(E.StatusPekerjaan, a.status_pekerjaan),
                "jumlah_usaha": a.jumlah_usaha,
                "disabilitas": _label(E.JenisDisabilitas, a.jenis_disabilitas),
                "penyakit_kronis": _label(E.PenyakitKronis, a.penyakit_kronis),
                "status_gizi": _label(E.StatusGiziBalita, a.status_gizi_balita),
                "sedang_hamil": bool(a.sedang_hamil),
                "punya_jkn": bool(a.punya_jaminan_kesehatan),
            }
            for a in anggota
        ],
        "riwayat": [
            {
                "gelombang": int(r.gelombang),
                "tanggal": str(r.tanggal_kondisi),
                "pengeluaran_per_kapita": float(r.pengeluaran_per_kapita),
                "rasio_garis_kemiskinan": round(float(r.rasio_garis_kemiskinan), 3),
                "miskin": bool(r.status_miskin),
                "rentan": 1.0 <= float(r.rasio_garis_kemiskinan) < 1.5,
                "desil": int(r.desil_kesejahteraan),
                "jumlah_anggota": int(r.jumlah_anggota),
                "jumlah_program": int(r.jumlah_program_diterima),
                "nilai_bantuan_bulanan": float(r.nilai_bantuan_bulanan),
                "cakupan_jkn": round(int(r.jumlah_ber_jkn) / max(1, int(r.jumlah_anggota)), 2),
                "umur_data_bulan": int(r.umur_data_bulan),
                "kelengkapan_data": round(float(r.kelengkapan_data), 2),
                "hunian": {
                    "luas_lantai_m2": float(r.luas_lantai_m2),
                    "luas_per_kapita": round(float(r.luas_lantai_m2) / max(1, int(r.jumlah_anggota)), 1),
                    "lantai": _label(E.JenisLantai, r.jenis_lantai_terluas),
                    "dinding": _label(E.JenisDinding, r.jenis_dinding_terluas),
                    "atap": _label(E.JenisAtap, r.jenis_atap_terluas),
                    "air_minum": _label(E.SumberAirMinum, r.sumber_air_minum_utama),
                    "fasilitas_bab": _label(E.FasilitasBAB, r.fasilitas_bab),
                    "kloset": _label(E.JenisKloset, r.jenis_kloset),
                    "pembuangan_tinja": _label(E.PembuanganTinja, r.pembuangan_akhir_tinja),
                    "daya_listrik": _label(E.DayaListrik, r.daya_terpasang),
                    "bahan_bakar": _label(E.BahanBakarMemasak, r.bahan_bakar_utama_memasak),
                },
                "skor": round(float(r.skor), 1) if r.skor is not None else None,
                "kategori": r.kategori,
                "probabilitas": round(float(r.probabilitas), 4) if r.probabilitas is not None else None,
                "perubahan_skor": round(float(r.perubahan_dari_sebelumnya), 1)
                if r.perubahan_dari_sebelumnya is not None
                else None,
                "peringkat_kabupaten": r.peringkat_kabupaten,
                "faktor_dominan": json.loads(r.faktor_dominan) if r.faktor_dominan else [],
                "kontribusi_fitur": json.loads(r.kontribusi_fitur) if r.kontribusi_fitur else [],
            }
            for r in riwayat
        ],
        "guncangan": [
            {
                "gelombang": int(g.gelombang),
                "tanggal": str(g.tanggal_kejadian) if g.tanggal_kejadian else None,
                "jenis": _label(E.JenisGuncangan, g.jenis),
                "sifat": E.JenisGuncangan(g.jenis).sifat if g.jenis else None,
                "keparahan": _label(E.TingkatKeparahan, g.keparahan),
                "dampak_persen": float(g.dampak_pendapatan_persen),
            }
            for g in guncangan
        ],
        "program": [
            {
                "kode": p.kode,
                "nama": p.nama_resmi,
                "singkatan": p.singkatan,
                "jenis": p.jenis_intervensi,
                "gelombang_mulai": int(p.gelombang_mulai),
                "gelombang_selesai": int(p.gelombang_selesai) if p.gelombang_selesai is not None else None,
                "status": p.status,
                "berjalan": p.gelombang_selesai is None,
            }
            for p in program
        ],
        "kasus": [
            {
                "kode": k.kode_semu,
                "gelombang": int(k.gelombang),
                "jenis": k.jenis,
                "label_jenis": E.JenisAnomali(k.jenis).label if k.jenis else None,
                "status": k.status,
                "skor_prioritas": round(float(k.skor_prioritas), 1),
                "tingkat_prioritas": int(k.tingkat_prioritas),
                "ringkasan": k.ringkasan,
            }
            for k in kasus
        ],
        "ringkas": {
            "skor_terkini": round(float(terkini.skor), 1) if terkini and terkini.skor is not None else None,
            "kategori_terkini": terkini.kategori if terkini else None,
            "miskin_terkini": bool(terkini.status_miskin) if terkini else None,
            "jumlah_guncangan": len(guncangan),
            "jumlah_program_pernah": len(program),
            "jumlah_kasus_terbuka": sum(
                1 for k in kasus if E.StatusKasus(k.status).terbuka if k.status
            ),
        },
        "penafian": (
            "Skor kerentanan adalah perkiraan berpeluang, bukan pernyataan tentang "
            "keadaan keluarga ini. Skor tidak menghentikan, mengurangi, atau menunda "
            "bantuan apa pun. Keputusan tetap berada pada musyawarah pekon dan "
            "penetapan pejabat berwenang."
        ),
    }


__all__ = ["router"]
