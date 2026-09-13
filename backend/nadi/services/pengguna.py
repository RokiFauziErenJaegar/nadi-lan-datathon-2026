"""Pengelolaan akun pengguna dan penyemaian akun demonstrasi.

Akun demonstrasi dibuat satu untuk setiap peran, dan itu disengaja: cara paling
meyakinkan menunjukkan bahwa pembatasan akses benar-benar bekerja adalah dengan
membiarkan penilai masuk sebagai pimpinan daerah, lalu mencoba membuka satu
keluarga - dan gagal. Pembatasan yang hanya dijelaskan lewat kalimat selalu
terdengar meyakinkan; yang dapat dicoba sendiri jauh lebih sulit dibantah.

Sandi demonstrasi sengaja ditampilkan pada dokumentasi. Nilainya sebagai
rahasia memang tidak ada - seluruh data pada sistem ini sintetis. Yang penting
adalah sistem menolak sandi lemah pada akun sungguhan, dan itu ditegakkan oleh
:func:`nadi.security.auth.kekuatan_sandi`.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from nadi.db.models import OPD, Pengguna
from nadi.security.auth import cernakan_sandi, kekuatan_sandi
from nadi.security.rbac import Peran

logger = logging.getLogger("nadi.pengguna")


@dataclass(frozen=True)
class AkunDemo:
    nama_pengguna: str
    sandi: str
    nama_lengkap: str
    jabatan: str
    peran: Peran
    kode_opd: str | None = None
    wilayah_akses: tuple[str, ...] = ()


#: Akun demonstrasi, satu untuk setiap peran.
AKUN_DEMO: tuple[AkunDemo, ...] = (
    AkunDemo(
        "admin",
        "NadiAdmin#2026",
        "Administrator Sistem",
        "Pranata Komputer, Diskominfo",
        Peran.ADMIN,
        "diskominfo",
    ),
    AkunDemo(
        "bupati",
        "NadiPimpinan#2026",
        "Pimpinan Daerah",
        "Bupati / Sekretaris Daerah",
        Peran.PIMPINAN,
        "setda",
    ),
    AkunDemo(
        "bappeda",
        "NadiPerencana#2026",
        "Perencana Bappeda",
        "Perencana Ahli Muda, Bappeda",
        Peran.PERENCANA,
        "bappeda",
    ),
    AkunDemo(
        "dinsos",
        "NadiDinsos#2026",
        "Operator Dinas Sosial",
        "Pengelola Data Kesejahteraan Sosial",
        Peran.DINAS_SOSIAL,
        "dinsos",
    ),
    AkunDemo(
        "pupr",
        "NadiPupr#2026",
        "Petugas Bidang Perumahan",
        "Pengelola Program RTLH, Dinas PUPR",
        Peran.OPD_PELAKSANA,
        "pupr",
    ),
    AkunDemo(
        "verifikator",
        "NadiVerif#2026",
        "Pendamping Sosial",
        "Pendamping PKH Kecamatan Pagelaran Utara",
        Peran.VERIFIKATOR,
        "dinsos",
        # Dibatasi pada satu kecamatan. Pembatasan ini bukan hiasan: kecamatan
        # inilah yang memuat tujuh dari lima belas pekon berstatus Berkembang,
        # sehingga demonstrasi pembatasan wilayah sekaligus memperlihatkan
        # kantong ketertinggalan yang sesungguhnya.
        ("18.10.09",),
    ),
)


def semai_pengguna(sesi: Session, *, timpa_sandi: bool = False) -> dict[str, int]:
    """Buat atau perbarui akun demonstrasi.

    Args:
        timpa_sandi: bila benar, sandi akun yang sudah ada ikut disetel ulang.
            Bawaannya salah agar sandi yang sudah diubah pengguna tidak
            terhapus tanpa sengaja saat penyemaian dijalankan ulang.
    """
    peta_opd = {o.kode: o.id for o in sesi.execute(select(OPD)).scalars().all()}
    hasil = {"baru": 0, "diperbarui": 0}

    for akun in AKUN_DEMO:
        layak, alasan = kekuatan_sandi(akun.sandi)
        if not layak:
            raise ValueError(f"Sandi akun '{akun.nama_pengguna}' tidak memenuhi syarat: {alasan}")

        obj = sesi.scalar(select(Pengguna).where(Pengguna.nama_pengguna == akun.nama_pengguna))
        baru = obj is None
        if obj is None:
            obj = Pengguna(nama_pengguna=akun.nama_pengguna)
            sesi.add(obj)
            hasil["baru"] += 1
        else:
            hasil["diperbarui"] += 1

        obj.nama_lengkap = akun.nama_lengkap
        obj.jabatan = akun.jabatan
        obj.peran = akun.peran
        obj.opd_id = peta_opd.get(akun.kode_opd) if akun.kode_opd else None
        obj.wilayah_akses = list(akun.wilayah_akses)
        obj.aktif = True
        if baru or timpa_sandi:
            obj.cernaan_sandi = cernakan_sandi(akun.sandi)

    sesi.flush()
    logger.info(
        "Akun demonstrasi disemai: %d baru, %d diperbarui.", hasil["baru"], hasil["diperbarui"]
    )
    return hasil


def cari_pengguna(sesi: Session, nama_pengguna: str) -> Pengguna | None:
    return sesi.scalar(
        select(Pengguna).where(Pengguna.nama_pengguna == nama_pengguna.strip().lower())
    )


__all__ = ["AKUN_DEMO", "AkunDemo", "cari_pengguna", "semai_pengguna"]
