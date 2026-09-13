"""Pemuatan data awal dari berkas JSON ke basis data.

Basis pengetahuan NADI - daftar organisasi perangkat daerah, katalog faktor
risiko, dan katalog program - tersimpan sebagai berkas JSON di ``data/seed``,
bukan tertanam di dalam kode. Pilihan ini memenuhi janji keberlanjutan pada
proposal: petugas dinas dapat memutakhirkan kriteria dan nominal program tanpa
menunggu pengembang menerbitkan versi baru aplikasi.

Pemuatan bersifat idempoten. Menjalankannya berulang kali memperbarui baris
yang sudah ada alih-alih menggandakannya, sehingga aman dipanggil setiap kali
aplikasi dinyalakan maupun setelah berkas seed disunting.

Seluruh isi divalidasi sebelum disimpan. Berkas seed yang menyebut fitur atau
kode enumerasi yang tidak dikenal akan menggagalkan pemuatan disertai pesan
yang menunjuk letak persoalannya - jauh lebih baik daripada tersimpan diam-diam
lalu menghasilkan rekomendasi yang tidak pernah muncul tanpa penjelasan.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from nadi.config import settings
from nadi.db.enums import (
    BasisDataProgram,
    DimensiRisiko,
    FrekuensiProgram,
    JenisIntervensi,
    OperatorAturan,
    SatuanManfaat,
    StatusProgram,
    SumberDana,
    TingkatEksekusi,
    TingkatKeyakinan,
    TipeAturan,
)
from nadi.db.models.program import (
    OPD,
    AturanKelayakan,
    FaktorRisiko,
    ManfaatProgram,
    Program,
    program_faktor_risiko,
    program_opd,
)
from nadi.ml.fitur import PETA_FITUR

logger = logging.getLogger("nadi.seed")


class SeedTidakSah(ValueError):
    """Diangkat saat berkas data awal memuat rujukan yang tidak dikenal."""


@dataclass
class HasilMuat:
    """Ringkasan satu kali pemuatan data awal."""

    opd_baru: int = 0
    opd_diperbarui: int = 0
    faktor_baru: int = 0
    faktor_diperbarui: int = 0
    program_baru: int = 0
    program_diperbarui: int = 0
    manfaat: int = 0
    aturan: int = 0
    peringatan: list[str] = field(default_factory=list)

    def ringkas(self) -> str:
        return (
            f"OPD {self.opd_baru} baru / {self.opd_diperbarui} diperbarui; "
            f"faktor risiko {self.faktor_baru} baru / {self.faktor_diperbarui} diperbarui; "
            f"program {self.program_baru} baru / {self.program_diperbarui} diperbarui "
            f"({self.manfaat} komponen manfaat, {self.aturan} aturan kelayakan)"
        )


# ---------------------------------------------------------------------------
# Pembantu
# ---------------------------------------------------------------------------
def _baca(jalur: Path) -> dict[str, Any]:
    if not jalur.exists():
        raise SeedTidakSah(f"Berkas data awal tidak ditemukan: {jalur}")
    try:
        return json.loads(jalur.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SeedTidakSah(f"Berkas {jalur.name} bukan JSON yang sah: {exc}") from exc


def _enum(kelas, nilai, konteks: str):
    """Ubah untai menjadi anggota enumerasi, dengan pesan galat yang menuntun."""
    if nilai is None:
        return None
    try:
        return kelas(nilai)
    except ValueError as exc:
        sah = ", ".join(a.value for a in kelas)
        raise SeedTidakSah(
            f"{konteks}: nilai '{nilai}' tidak dikenal untuk {kelas.__name__}. "
            f"Nilai yang sah: {sah}"
        ) from exc


def _wajib_fitur(nama: str, konteks: str) -> str:
    """Pastikan sebuah nama merujuk fitur yang benar-benar ada."""
    if nama not in PETA_FITUR:
        raise SeedTidakSah(
            f"{konteks}: '{nama}' bukan nama fitur yang dikenal. "
            "Nama harus sesuai DAFTAR_FITUR pada nadi.ml.fitur. "
            "Aturan yang menunjuk fitur tidak ada tidak akan pernah terpenuhi, "
            "sehingga programnya tidak akan pernah direkomendasikan."
        )
    return nama


def _periksa_ekspresi(eks: Any, konteks: str) -> None:
    """Telusuri ekspresi deteksi dan pastikan seluruh rujukan fiturnya sah."""
    if not eks:
        return
    if not isinstance(eks, dict):
        raise SeedTidakSah(f"{konteks}: ekspresi deteksi harus berupa objek.")
    for kunci in ("semua", "salah_satu"):
        for syarat in eks.get(kunci, []):
            if "fitur" in syarat:
                _wajib_fitur(syarat["fitur"], konteks)
                _enum(OperatorAturan, syarat.get("operator"), konteks)
            else:
                _periksa_ekspresi(syarat, konteks)


# ---------------------------------------------------------------------------
# Pemuat per entitas
# ---------------------------------------------------------------------------
def _muat_opd(sesi: Session, data: dict[str, Any], hasil: HasilMuat) -> dict[str, OPD]:
    peta: dict[str, OPD] = {}
    for butir in data["opd"]:
        kode = butir["kode"]
        obj = sesi.scalar(select(OPD).where(OPD.kode == kode))
        if obj is None:
            obj = OPD(kode=kode)
            sesi.add(obj)
            hasil.opd_baru += 1
        else:
            hasil.opd_diperbarui += 1
        obj.nama = butir["nama"]
        obj.singkatan = butir["singkatan"]
        obj.tupoksi = butir.get("tupoksi")
        obj.relevansi_kemiskinan = butir.get("relevansi_kemiskinan", "sedang")
        obj.situs = butir.get("situs")
        obj.aktif = butir.get("aktif", True)
        peta[kode] = obj
    sesi.flush()
    return peta


def _muat_faktor_risiko(
    sesi: Session, data: dict[str, Any], hasil: HasilMuat
) -> dict[str, FaktorRisiko]:
    peta: dict[str, FaktorRisiko] = {}
    for butir in data["faktor_risiko"]:
        kode = butir["kode"]
        konteks = f"faktor_risiko.json/{kode}"
        _periksa_ekspresi(butir.get("ekspresi_deteksi"), konteks)
        for nama in butir.get("fitur_terkait") or []:
            _wajib_fitur(nama, konteks)

        obj = sesi.scalar(select(FaktorRisiko).where(FaktorRisiko.kode == kode))
        if obj is None:
            obj = FaktorRisiko(kode=kode)
            sesi.add(obj)
            hasil.faktor_baru += 1
        else:
            hasil.faktor_diperbarui += 1

        obj.nama = butir["nama"]
        obj.deskripsi = butir.get("deskripsi")
        obj.dimensi = _enum(DimensiRisiko, butir["dimensi"], konteks)
        obj.indikator = butir.get("indikator")
        obj.ekspresi_deteksi = butir.get("ekspresi_deteksi")
        obj.fitur_terkait = butir.get("fitur_terkait") or []
        obj.bobot_dasar = float(butir.get("bobot_dasar", 1.0))
        obj.urutan_tampil = int(butir.get("urutan_tampil", 100))
        obj.jenis_intervensi_utama = _enum(
            JenisIntervensi, butir.get("jenis_intervensi_utama"), konteks
        )
        obj.aktif = butir.get("aktif", True)

        if obj.ekspresi_deteksi is None:
            hasil.peringatan.append(
                f"Faktor risiko {kode} tidak memiliki ekspresi deteksi otomatis "
                "dan hanya dapat ditandai manual oleh petugas."
            )
        peta[kode] = obj
    sesi.flush()
    return peta


def _muat_program(
    sesi: Session,
    data: dict[str, Any],
    peta_opd: dict[str, OPD],
    peta_faktor: dict[str, FaktorRisiko],
    hasil: HasilMuat,
) -> None:
    for butir in data["program"]:
        kode = butir["kode"]
        konteks = f"program.json/{kode}"

        obj = sesi.scalar(select(Program).where(Program.kode == kode))
        if obj is None:
            obj = Program(kode=kode)
            sesi.add(obj)
            hasil.program_baru += 1
        else:
            hasil.program_diperbarui += 1

        obj.nama_resmi = butir["nama_resmi"]
        obj.singkatan = butir["singkatan"]
        obj.deskripsi = butir.get("deskripsi")
        obj.jenis_intervensi = _enum(JenisIntervensi, butir["jenis_intervensi"], konteks)
        obj.kementerian = butir.get("kementerian")
        obj.tingkat_eksekusi = _enum(TingkatEksekusi, butir["tingkat_eksekusi"], konteks)
        obj.basis_data = _enum(BasisDataProgram, butir["basis_data"], konteks)
        obj.sumber_dana = _enum(SumberDana, butir["sumber_dana"], konteks)
        obj.frekuensi = _enum(FrekuensiProgram, butir["frekuensi"], konteks)
        obj.desil_min = butir.get("desil_min")
        obj.desil_maks = butir.get("desil_maks")
        obj.mekanisme_penyaluran = butir.get("mekanisme_penyaluran")
        obj.dasar_hukum = butir.get("dasar_hukum") or []
        obj.sumber_url = butir.get("sumber_url") or []
        obj.kuota_tahunan = butir.get("kuota_tahunan")
        obj.biaya_satuan_tahunan = butir.get("biaya_satuan_tahunan")
        obj.status = _enum(StatusProgram, butir["status"], konteks)
        obj.tingkat_keyakinan = _enum(TingkatKeyakinan, butir["tingkat_keyakinan"], konteks)
        obj.catatan = butir.get("catatan")
        obj.urutan_tampil = int(butir.get("urutan_tampil", 100))
        sesi.flush()

        # --- Komponen manfaat: ditulis ulang seluruhnya ---
        # Pemutakhiran sebagian pada daftar komponen lebih rumit daripada
        # manfaatnya, dan menyisakan risiko komponen lama tertinggal setelah
        # sebuah program disederhanakan.
        sesi.execute(delete(ManfaatProgram).where(ManfaatProgram.program_id == obj.id))
        for m in butir.get("manfaat", []):
            konteks_m = f"{konteks}/manfaat/{m['komponen']}"
            syarat = m.get("syarat_komponen")
            if syarat and "fitur" in syarat:
                _wajib_fitur(syarat["fitur"], konteks_m)
            sesi.add(
                ManfaatProgram(
                    program_id=obj.id,
                    komponen=m["komponen"],
                    label=m["label"],
                    nominal_per_periode=m.get("nominal_per_periode"),
                    nominal_per_tahun=m.get("nominal_per_tahun"),
                    satuan=_enum(SatuanManfaat, m["satuan"], konteks_m),
                    frekuensi=_enum(FrekuensiProgram, m["frekuensi"], konteks_m),
                    syarat_komponen=syarat,
                    tingkat_keyakinan=_enum(
                        TingkatKeyakinan, m.get("tingkat_keyakinan", "cukup_kuat"), konteks_m
                    ),
                    catatan=m.get("catatan"),
                )
            )
            hasil.manfaat += 1

        # --- Aturan kelayakan: ditulis ulang seluruhnya ---
        sesi.execute(delete(AturanKelayakan).where(AturanKelayakan.program_id == obj.id))
        for a in butir.get("aturan", []):
            konteks_a = f"{konteks}/aturan/{a['bidang']}"
            sesi.add(
                AturanKelayakan(
                    program_id=obj.id,
                    tipe=_enum(TipeAturan, a["tipe"], konteks_a),
                    bidang=_wajib_fitur(a["bidang"], konteks_a),
                    operator=_enum(OperatorAturan, a["operator"], konteks_a),
                    nilai=a.get("nilai"),
                    wajib=bool(a.get("wajib", True)),
                    prioritas=int(a.get("prioritas", 100)),
                    keterangan=a.get("keterangan"),
                    tingkat_keyakinan=_enum(
                        TingkatKeyakinan, a.get("tingkat_keyakinan", "cukup_kuat"), konteks_a
                    ),
                )
            )
            hasil.aturan += 1

        # --- Tautan ke OPD, beserta perannya ---
        sesi.execute(delete(program_opd).where(program_opd.c.program_id == obj.id))
        for o in butir.get("opd", []):
            if o["kode"] not in peta_opd:
                raise SeedTidakSah(
                    f"{konteks}: OPD '{o['kode']}' tidak ada pada opd.json. "
                    "Rekomendasi tanpa penanggung jawab tidak dapat ditindaklanjuti siapa pun."
                )
            sesi.execute(
                program_opd.insert().values(
                    program_id=obj.id,
                    opd_id=peta_opd[o["kode"]].id,
                    peran=o.get("peran", "pelaksana"),
                )
            )

        # --- Tautan ke faktor risiko, beserta kekuatannya ---
        sesi.execute(
            delete(program_faktor_risiko).where(program_faktor_risiko.c.program_id == obj.id)
        )
        for f in butir.get("faktor_risiko", []):
            if f["kode"] not in peta_faktor:
                raise SeedTidakSah(
                    f"{konteks}: faktor risiko '{f['kode']}' tidak ada pada faktor_risiko.json."
                )
            sesi.execute(
                program_faktor_risiko.insert().values(
                    program_id=obj.id,
                    faktor_risiko_id=peta_faktor[f["kode"]].id,
                    kekuatan=float(f.get("kekuatan", 1.0)),
                )
            )
    sesi.flush()


# ---------------------------------------------------------------------------
# Titik masuk
# ---------------------------------------------------------------------------
def muat_basis_pengetahuan(sesi: Session, akar: Path | None = None) -> HasilMuat:
    """Muat OPD, faktor risiko, dan katalog program ke basis data.

    Args:
        sesi: sesi basis data yang aktif. Fungsi ini tidak melakukan commit -
            pemanggil yang menentukan batas transaksinya.
        akar: folder berisi berkas data awal. Bawaannya ``data/seed``.

    Raises:
        SeedTidakSah: bila berkas tidak ditemukan, bukan JSON yang sah, atau
            memuat rujukan yang tidak dikenal.
    """
    akar = akar or settings.seed_dir
    hasil = HasilMuat()

    peta_opd = _muat_opd(sesi, _baca(akar / "opd.json"), hasil)
    peta_faktor = _muat_faktor_risiko(sesi, _baca(akar / "faktor_risiko.json"), hasil)
    _muat_program(sesi, _baca(akar / "program.json"), peta_opd, peta_faktor, hasil)

    logger.info("Basis pengetahuan dimuat: %s", hasil.ringkas())
    for p in hasil.peringatan:
        logger.warning(p)
    return hasil


__all__ = ["HasilMuat", "SeedTidakSah", "muat_basis_pengetahuan"]
