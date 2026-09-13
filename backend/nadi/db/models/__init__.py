"""Seluruh model basis data NADI.

Mengimpor paket ini mendaftarkan setiap tabel pada metadata SQLAlchemy.
Urutan impor mengikuti arah ketergantungan kunci asing, dari yang paling
mendasar menuju yang paling bergantung, agar penyelesaian relasi tidak
memerlukan rujukan maju yang sulit dilacak saat terjadi galat.
"""

from nadi.db.models.wilayah import StatistikWilayah, Wilayah
from nadi.db.models.program import (
    OPD,
    AturanKelayakan,
    FaktorRisiko,
    KepesertaanProgram,
    ManfaatProgram,
    Program,
    program_faktor_risiko,
    program_opd,
)
from nadi.db.models.sistem import (
    CatatanPermintaanAI,
    JejakAudit,
    PengaturanSistem,
    Pengguna,
)
from nadi.db.models.keluarga import (
    AnggotaKeluarga,
    Guncangan,
    Keluarga,
    SnapshotKeluarga,
)
from nadi.db.models.analitik import Kasus, Rekomendasi, SkorKerentanan, VersiModel
from nadi.db.models.kerja import HasilIntervensi, Intervensi, Verifikasi

__all__ = [
    "OPD",
    "AnggotaKeluarga",
    "AturanKelayakan",
    "CatatanPermintaanAI",
    "FaktorRisiko",
    "Guncangan",
    "HasilIntervensi",
    "Intervensi",
    "JejakAudit",
    "Kasus",
    "Keluarga",
    "KepesertaanProgram",
    "ManfaatProgram",
    "PengaturanSistem",
    "Pengguna",
    "Program",
    "Rekomendasi",
    "SkorKerentanan",
    "SnapshotKeluarga",
    "StatistikWilayah",
    "VersiModel",
    "Verifikasi",
    "Wilayah",
    "program_faktor_risiko",
    "program_opd",
]
