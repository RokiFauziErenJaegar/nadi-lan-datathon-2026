"""Mismatch & Anomaly Queue - antrean kasus dan alur verifikasi."""

from __future__ import annotations

import json
import logging
from datetime import date, datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy import select, text

from nadi.api.deps import KonteksPengguna, PenggunaAktif, SesiDB, catat_audit, wajib
from nadi.db.enums import HasilVerifikasi, JenisAnomali, StatusKasus
from nadi.db.models import Kasus, Verifikasi
from nadi.security.rbac import Kewenangan

logger = logging.getLogger("nadi.api.antrean")
router = APIRouter(prefix="/antrean", tags=["antrean"])


@router.get("", summary="Daftar kasus untuk diperiksa", dependencies=[Depends(wajib(Kewenangan.BACA_ANTREAN))])
def daftar(
    sesi: SesiDB,
    pengguna: PenggunaAktif,
    jenis: str | None = Query(None),
    status: str | None = Query(None),
    kecamatan: str | None = Query(None),
    prioritas_maksimum: int = Query(5, ge=1, le=5),
    hanya_terbuka: bool = Query(True),
    gelombang: int | None = Query(None),
    batas: int = Query(50, ge=1, le=500),
    lewati: int = Query(0, ge=0),
) -> dict:
    """Antrean kasus, diurutkan menurut prioritas.

    Urutan bawaan menempatkan kasus keluarga yang terlewat lebih dahulu.
    Kesalahan memasukkan orang yang tidak berhak membebani anggaran; kesalahan
    melewatkan orang yang berhak membebani keluarga itu sendiri - dan mereka
    tidak muncul di daftar mana pun untuk mengeluh.
    """
    g = gelombang if gelombang is not None else int(
        sesi.execute(text("SELECT MAX(gelombang) FROM kasus")).scalar() or 0
    )

    syarat = ["k.gelombang = :g", "k.tingkat_prioritas <= :prio"]
    param: dict = {"g": g, "prio": prioritas_maksimum, "batas": batas, "lewati": lewati}

    if hanya_terbuka:
        syarat.append(
            "k.status NOT IN ('selesai','ditutup_tanpa_tindakan','terverifikasi_tidak_sesuai')"
        )
    if jenis:
        syarat.append("k.jenis = :jenis")
        param["jenis"] = jenis
    if status:
        syarat.append("k.status = :status")
        param["status"] = status
    if kecamatan:
        syarat.append("COALESCE(induk.kode, w.kode) = :kec")
        param["kec"] = kecamatan
    if pengguna.dibatasi_wilayah:
        # Setiap kode wilayah diberi parameter bernama tersendiri.
        #
        # Menuliskannya sebagai "IN :izin" dengan sebuah tuple tampak wajar dan
        # menghasilkan galat lima ratus: SQLAlchemy tidak memperluas tuple pada
        # klausa IN kecuali parameternya ditandai khusus. Yang terlihat oleh
        # pengguna adalah peladen rusak, padahal pembatasannya sendiri benar -
        # bentuk kegagalan yang paling menyesatkan.
        kunci = [f"izin{i}" for i in range(len(pengguna.wilayah_akses))]
        syarat.append(
            "COALESCE(induk.kode, w.kode) IN (" + ", ".join(f":{k}" for k in kunci) + ")"
        )
        param.update(dict(zip(kunci, pengguna.wilayah_akses)))

    kueri = f"""
        SELECT k.id, k.kode_semu, k.gelombang, k.jenis, k.status,
               k.skor_prioritas, k.tingkat_prioritas, k.ringkasan, k.alasan,
               k.sumber_deteksi, k.tenggat, k.dibuat_pada,
               kel.kode_semu AS kode_keluarga,
               w.nama AS desa, induk.nama AS kecamatan,
               opd.singkatan AS opd,
               sk.skor, sk.kategori,
               s.desil_kesejahteraan, s.jumlah_anggota, s.jumlah_program_diterima
        FROM kasus k
        JOIN keluarga kel      ON kel.id = k.keluarga_id
        JOIN wilayah w         ON w.id = kel.wilayah_id
        LEFT JOIN wilayah induk ON induk.id = w.induk_id
        LEFT JOIN opd          ON opd.id = k.opd_ditugaskan_id
        LEFT JOIN skor_kerentanan sk
               ON sk.keluarga_id = k.keluarga_id AND sk.gelombang = k.gelombang
        LEFT JOIN snapshot_keluarga s
               ON s.keluarga_id = k.keluarga_id AND s.gelombang = k.gelombang
        WHERE {' AND '.join(syarat)}
        ORDER BY k.skor_prioritas DESC, k.tingkat_prioritas ASC
        LIMIT :batas OFFSET :lewati
    """
    baris = sesi.execute(text(kueri), param).all()

    rekap = sesi.execute(
        text(
            """
            SELECT jenis, status, COUNT(*) AS n
            FROM kasus WHERE gelombang = :g GROUP BY jenis, status
            """
        ),
        {"g": g},
    ).all()

    return {
        "gelombang": g,
        "jumlah_ditampilkan": len(baris),
        "kasus": [
            {
                "kode": b.kode_semu,
                "kode_keluarga": b.kode_keluarga,
                "gelombang": int(b.gelombang),
                "jenis": b.jenis,
                "label_jenis": JenisAnomali(b.jenis).label if b.jenis else None,
                "status": b.status,
                "label_status": StatusKasus(b.status).label if b.status else None,
                "skor_prioritas": round(float(b.skor_prioritas), 1),
                "tingkat_prioritas": int(b.tingkat_prioritas),
                "ringkasan": b.ringkasan,
                "alasan": json.loads(b.alasan) if isinstance(b.alasan, str) else (b.alasan or []),
                "sumber_deteksi": b.sumber_deteksi,
                "desa": b.desa,
                "kecamatan": b.kecamatan,
                "opd_ditugaskan": b.opd,
                "tenggat": str(b.tenggat) if b.tenggat else None,
                "keluarga": {
                    "skor": round(float(b.skor), 1) if b.skor is not None else None,
                    "kategori": b.kategori,
                    "desil": b.desil_kesejahteraan,
                    "jumlah_anggota": b.jumlah_anggota,
                    "jumlah_program": b.jumlah_program_diterima,
                },
            }
            for b in baris
        ],
        "rekap": [
            {
                "jenis": r.jenis,
                "label": JenisAnomali(r.jenis).label if r.jenis else None,
                "status": r.status,
                "jumlah": int(r.n),
            }
            for r in rekap
        ],
        "catatan": (
            "Setiap kasus adalah usulan pemeriksaan, bukan keputusan. Tidak ada "
            "jalur pada sistem ini yang mengubahnya menjadi penghentian bantuan "
            "tanpa verifikasi manusia."
        ),
    }


@router.get("/{kode}", summary="Rincian satu kasus", dependencies=[Depends(wajib(Kewenangan.BACA_ANTREAN))])
def rincian(kode: str, sesi: SesiDB) -> dict:
    """Rincian kasus beserta bukti dan riwayat verifikasinya."""
    k = sesi.scalar(select(Kasus).where(Kasus.kode_semu == kode.strip().upper()))
    if k is None:
        raise HTTPException(404, f"Kasus '{kode}' tidak ditemukan.")

    verifikasi = sesi.execute(
        text(
            """
            SELECT v.waktu, v.hasil, v.catatan, v.metode, v.setuju_dengan_sistem,
                   v.durasi_menit, v.kondisi_terkoreksi, p.nama_lengkap, p.peran
            FROM verifikasi v JOIN pengguna p ON p.id = v.pengguna_id
            WHERE v.kasus_id = :id ORDER BY v.waktu DESC
            """
        ),
        {"id": k.id},
    ).all()

    return {
        "kode": k.kode_semu,
        "kode_keluarga": k.keluarga.kode_semu,
        "gelombang": k.gelombang,
        "jenis": k.jenis.value if hasattr(k.jenis, "value") else k.jenis,
        "label_jenis": k.jenis.label if hasattr(k.jenis, "label") else None,
        "status": k.status.value if hasattr(k.status, "value") else k.status,
        "terbuka": k.terbuka,
        "skor_prioritas": round(float(k.skor_prioritas), 1),
        "tingkat_prioritas": k.tingkat_prioritas,
        "ringkasan": k.ringkasan,
        "alasan": k.alasan or [],
        "sumber_deteksi": k.sumber_deteksi,
        "opd_ditugaskan": k.opd_ditugaskan.singkatan if k.opd_ditugaskan else None,
        "tenggat": str(k.tenggat) if k.tenggat else None,
        "verifikasi": [
            {
                "waktu": str(v.waktu),
                "hasil": v.hasil,
                "label_hasil": HasilVerifikasi(v.hasil).label if v.hasil else None,
                "catatan": v.catatan,
                "metode": v.metode,
                "setuju_dengan_sistem": v.setuju_dengan_sistem,
                "durasi_menit": v.durasi_menit,
                "kondisi_terkoreksi": v.kondisi_terkoreksi,
                "petugas": v.nama_lengkap,
                "peran": v.peran,
            }
            for v in verifikasi
        ],
    }


class PermintaanPenugasan(BaseModel):
    kode_opd: str
    tenggat: date | None = None
    catatan: str | None = Field(None, max_length=1000)


@router.post("/{kode}/tugaskan", summary="Tugaskan kasus ke OPD")
def tugaskan(
    kode: str,
    data: PermintaanPenugasan,
    sesi: SesiDB,
    request: Request,
    pengguna: KonteksPengguna = Depends(wajib(Kewenangan.TUGASKAN_KASUS)),
) -> dict:
    """Tetapkan OPD yang bertanggung jawab memeriksa kasus ini."""
    k = sesi.scalar(select(Kasus).where(Kasus.kode_semu == kode.strip().upper()))
    if k is None:
        raise HTTPException(404, f"Kasus '{kode}' tidak ditemukan.")

    opd_id = sesi.execute(
        text("SELECT id FROM opd WHERE kode = :k"), {"k": data.kode_opd}
    ).scalar()
    if opd_id is None:
        raise HTTPException(404, f"OPD '{data.kode_opd}' tidak ditemukan.")

    k.opd_ditugaskan_id = int(opd_id)
    k.tenggat = data.tenggat
    if k.status is StatusKasus.BARU:
        k.status = StatusKasus.DITUGASKAN

    catat_audit(
        sesi, pengguna, "tugaskan_kasus",
        entitas="kasus", entitas_id=kode,
        ringkasan=f"Ditugaskan ke {data.kode_opd}", request=request,
        rincian={"tenggat": str(data.tenggat) if data.tenggat else None},
    )
    sesi.commit()
    return {"kode": kode, "status": k.status.value, "opd": data.kode_opd}


class PermintaanVerifikasi(BaseModel):
    hasil: HasilVerifikasi
    catatan: str | None = Field(None, max_length=2000)
    metode: str = Field("kunjungan_lapangan", max_length=32)
    setuju_dengan_sistem: bool | None = None
    durasi_menit: int | None = Field(None, ge=0, le=600)
    kondisi_terkoreksi: dict | None = None


@router.post("/{kode}/verifikasi", summary="Catat hasil verifikasi lapangan")
def verifikasi(
    kode: str,
    data: PermintaanVerifikasi,
    sesi: SesiDB,
    request: Request,
    pengguna: KonteksPengguna = Depends(wajib(Kewenangan.VERIFIKASI_KASUS)),
) -> dict:
    """Catat temuan petugas di lapangan.

    Kolom ``kondisi_terkoreksi`` adalah bagian terpenting dari titik akhir ini.
    Ketika petugas mendapati keadaan berbeda dari catatan sistem, koreksinya
    tidak berhenti sebagai catatan - ia menjadi bahan pelatihan ulang. Setiap
    kunjungan memperbaiki model, dan model yang membaik mengirim petugas ke
    tempat yang lebih tepat pada putaran berikutnya. Inilah lingkaran umpan
    balik yang dijanjikan proposal, dinyatakan sebagai satu kolom basis data.

    Kolom ``setuju_dengan_sistem`` mengukur sesuatu yang berbeda dan sama
    pentingnya: seberapa sering penandaan sistem terbukti benar di lapangan.
    Agregatnya adalah ketepatan yang sesungguhnya - bukan ketepatan pada data
    pengujian, melainkan pada kenyataan.
    """
    k = sesi.scalar(select(Kasus).where(Kasus.kode_semu == kode.strip().upper()))
    if k is None:
        raise HTTPException(404, f"Kasus '{kode}' tidak ditemukan.")

    sesi.add(
        Verifikasi(
            kasus_id=k.id,
            pengguna_id=pengguna.id,
            hasil=data.hasil,
            catatan=data.catatan,
            metode=data.metode,
            setuju_dengan_sistem=data.setuju_dengan_sistem,
            durasi_menit=data.durasi_menit,
            kondisi_terkoreksi=data.kondisi_terkoreksi,
        )
    )

    peta = {
        HasilVerifikasi.SESUAI: StatusKasus.TERVERIFIKASI_SESUAI,
        HasilVerifikasi.TIDAK_SESUAI: StatusKasus.TERVERIFIKASI_TIDAK_SESUAI,
        HasilVerifikasi.PERLU_DATA_TAMBAHAN: StatusKasus.PERLU_DATA_TAMBAHAN,
        HasilVerifikasi.TIDAK_DITEMUKAN: StatusKasus.PERLU_DATA_TAMBAHAN,
    }
    k.status = peta.get(data.hasil, StatusKasus.SEDANG_DIVERIFIKASI)
    if not k.status.terbuka:
        k.ditutup_pada = datetime.now(timezone.utc)

    catat_audit(
        sesi, pengguna, "verifikasi_kasus",
        entitas="kasus", entitas_id=kode,
        ringkasan=f"Hasil: {data.hasil.value}", request=request,
        rincian={
            "metode": data.metode,
            "setuju_dengan_sistem": data.setuju_dengan_sistem,
            "jumlah_koreksi": len(data.kondisi_terkoreksi or {}),
        },
    )
    sesi.commit()

    return {
        "kode": kode,
        "status_baru": k.status.value,
        "hasil": data.hasil.value,
        "catatan": (
            "Koreksi kondisi tersimpan sebagai bahan pelatihan ulang model."
            if data.kondisi_terkoreksi
            else None
        ),
    }


@router.get("/rekap/ketepatan", summary="Ketepatan penandaan menurut hasil lapangan",
            dependencies=[Depends(wajib(Kewenangan.BACA_ANTREAN))])
def ketepatan(sesi: SesiDB) -> dict:
    """Seberapa sering penandaan sistem terbukti benar di lapangan.

    Angka ini lebih berharga daripada metrik model mana pun, sebab ia diukur
    pada kenyataan alih-alih pada data pengujian. Bila jauh lebih rendah
    daripada yang dijanjikan model, yang perlu diperbaiki adalah modelnya -
    bukan cara angkanya disajikan.
    """
    baris = sesi.execute(
        text(
            """
            SELECT k.jenis,
                   COUNT(*)                         AS jumlah_verifikasi,
                   SUM(CASE WHEN v.setuju_dengan_sistem = 1 THEN 1 ELSE 0 END) AS setuju,
                   AVG(v.durasi_menit)              AS durasi_rata
            FROM verifikasi v JOIN kasus k ON k.id = v.kasus_id
            WHERE v.setuju_dengan_sistem IS NOT NULL
            GROUP BY k.jenis
            """
        )
    ).all()

    return {
        "per_jenis": [
            {
                "jenis": b.jenis,
                "label": JenisAnomali(b.jenis).label if b.jenis else None,
                "jumlah_verifikasi": int(b.jumlah_verifikasi),
                "jumlah_setuju": int(b.setuju or 0),
                "ketepatan": round(int(b.setuju or 0) / max(1, int(b.jumlah_verifikasi)), 3),
                "durasi_rata_menit": round(float(b.durasi_rata), 1) if b.durasi_rata else None,
            }
            for b in baris
        ],
        "catatan": (
            "Kosong berarti belum ada verifikasi lapangan yang tercatat. Pada "
            "pemakaian sungguhan, tabel ini menjadi ukuran ketepatan yang paling "
            "dapat dipercaya."
        ),
    }


__all__ = ["router"]
