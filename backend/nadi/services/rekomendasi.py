"""Mesin rekomendasi intervensi lintas OPD.

Menghubungkan tiga hal yang selama ini berdiri sendiri-sendiri: apa yang
dikatakan model tentang sebuah keluarga, apa yang ditawarkan katalog program,
dan siapa yang berwenang menjalankannya.

Rekomendasi disusun dari empat pertimbangan, dengan bobot yang ditetapkan
terbuka pada :data:`BOBOT`:

**Kelayakan** menjadi gerbang, bukan nilai. Program yang aturan wajibnya tidak
terpenuhi tidak dinaikkan peringkatnya - ia ditandai sebagai kandidat bersyarat
beserta keterangan apa yang masih kurang. Perbedaan ini penting bagi petugas:
seringkali yang kurang itu justru dapat dilengkapi hari itu juga.

**Kesesuaian faktor risiko** menjadi penimbang utama. Program yang menangani
persoalan yang benar-benar mendorong skor keluarga ini naik dinilai lebih
tinggi daripada program yang sekadar memenuhi syarat administratif.

**Kesiapan pelaksanaan** ikut dipertimbangkan. Program yang penetapannya
berada di pusat tidak dapat "diberikan" oleh dinas daerah - yang dapat
dilakukan hanyalah mengusulkan. Rekomendasi menyebutkan tindakan yang benar
agar tidak berhenti sebagai daftar keinginan.

**Urutan yang masuk akal.** Satu aturan mendahului seluruh perhitungan: bila
keluarga memiliki persoalan dokumen kependudukan, pengurusan dokumen
ditempatkan paling atas. Mendaftarkan keluarga tanpa nomor induk kependudukan
ke program bantuan hanya akan berujung penolakan beberapa bulan kemudian -
dan selama bulan-bulan itu, tidak ada yang berubah bagi mereka.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from nadi.db.enums import SatuanManfaat, StatusProgram, TingkatEksekusi
from nadi.db.models import Program
from nadi.ml.aturan import evaluasi_syarat, jelaskan_syarat
from nadi.ml.fitur import PETA_FITUR

logger = logging.getLogger("nadi.rekomendasi")

#: Bobot penyusun nilai kecocokan. Dituliskan terbuka agar dapat
#: diperdebatkan dan disesuaikan oleh dinas, bukan tersembunyi di dalam rumus.
BOBOT = {
    "faktor_risiko": 0.55,
    "aturan_pendukung": 0.25,
    "kesiapan": 0.12,
    "keyakinan_katalog": 0.08,
}

#: Program yang harus didahulukan apa pun keadaannya, beserta syarat pemicunya.
PENDAHULU: tuple[tuple[str, str], ...] = (("ADMINDUK", "ada_masalah_dokumen"),)

#: Nilai kesiapan menurut tingkat pelaksanaan. Program yang dapat ditetapkan
#: sendiri oleh daerah lebih cepat terwujud daripada yang menunggu kuota pusat.
KESIAPAN = {
    TingkatEksekusi.DAERAH: 1.00,
    TingkatEksekusi.DESA: 0.85,
    TingkatEksekusi.PUSAT_DISALURKAN_DI_DAERAH: 0.60,
    TingkatEksekusi.MANDIRI_ONLINE: 0.45,
}

KEYAKINAN_NILAI = {
    "pasti": 1.00,
    "cukup_kuat": 0.80,
    "perkiraan": 0.50,
    "tidak_ditemukan": 0.25,
}


@dataclass
class UsulanProgram:
    """Satu program yang diusulkan bagi sebuah keluarga."""

    kode: str
    nama: str
    singkatan: str
    skor_kecocokan: float
    peringkat: int
    layak: bool
    jenis_intervensi: str
    opd: list[str]
    tindakan: str
    faktor_disasar: list[str] = field(default_factory=list)
    aturan_terpenuhi: list[str] = field(default_factory=list)
    aturan_tidak_terpenuhi: list[str] = field(default_factory=list)
    perkiraan_manfaat_bulanan: float | None = None
    komponen_berlaku: list[str] = field(default_factory=list)
    alasan: str = ""
    tingkat_keyakinan: str = "cukup_kuat"
    catatan: str | None = None

    def ke_dict(self) -> dict[str, Any]:
        return {
            "kode": self.kode,
            "nama": self.nama,
            "singkatan": self.singkatan,
            "skor_kecocokan": round(self.skor_kecocokan, 1),
            "peringkat": self.peringkat,
            "layak": self.layak,
            "jenis_intervensi": self.jenis_intervensi,
            "opd": self.opd,
            "tindakan": self.tindakan,
            "faktor_disasar": self.faktor_disasar,
            "aturan_terpenuhi": self.aturan_terpenuhi,
            "aturan_tidak_terpenuhi": self.aturan_tidak_terpenuhi,
            "perkiraan_manfaat_bulanan": self.perkiraan_manfaat_bulanan,
            "komponen_berlaku": self.komponen_berlaku,
            "alasan": self.alasan,
            "tingkat_keyakinan": self.tingkat_keyakinan,
            "catatan": self.catatan,
        }


# ===========================================================================
class MesinRekomendasi:
    """Menyusun usulan intervensi dari katalog program dan profil risiko."""

    def __init__(self, sesi: Session, *, sertakan_tidak_pasti: bool = False) -> None:
        kueri = select(Program).options(
            selectinload(Program.aturan),
            selectinload(Program.manfaat),
            selectinload(Program.opd),
            selectinload(Program.faktor_risiko),
        )
        if not sertakan_tidak_pasti:
            kueri = kueri.where(Program.status == StatusProgram.AKTIF)

        self.program = list(sesi.execute(kueri).scalars().all())
        self.peta_kekuatan = self._muat_kekuatan(sesi)
        logger.info("Mesin rekomendasi siap dengan %d program.", len(self.program))

    @staticmethod
    def _muat_kekuatan(sesi: Session) -> dict[tuple[int, int], float]:
        """Ambil kekuatan hubungan program dengan faktor risiko."""
        from nadi.db.models.program import program_faktor_risiko

        baris = sesi.execute(select(program_faktor_risiko)).all()
        return {(b.program_id, b.faktor_risiko_id): float(b.kekuatan) for b in baris}

    # ------------------------------------------------------------------
    def usulkan(
        self,
        X: pd.DataFrame,
        indeks: int,
        *,
        faktor_dominan: list[str] | None = None,
        maksimum: int = 6,
        sertakan_bersyarat: bool = True,
    ) -> list[UsulanProgram]:
        """Susun daftar usulan program bagi satu keluarga.

        Args:
            X: matriks fitur; hanya baris ``indeks`` yang dibaca.
            faktor_dominan: kode faktor risiko yang paling mendorong skor,
                dari penjelasan model. Bila kosong, penilaian jatuh sepenuhnya
                pada aturan kelayakan.
            sertakan_bersyarat: sertakan program yang belum memenuhi seluruh
                syarat, disertai keterangan apa yang kurang.
        """
        baris = X.iloc[[indeks]]
        dominan = set(faktor_dominan or [])
        usulan: list[UsulanProgram] = []

        for p in self.program:
            hasil = self._nilai_program(p, baris, dominan)
            if hasil is None:
                continue
            if not hasil.layak and not sertakan_bersyarat:
                continue
            usulan.append(hasil)

        # Program prasyarat naik ke puncak, mendahului seluruh perhitungan.
        for kode, pemicu in PENDAHULU:
            if pemicu in baris.columns and bool(baris[pemicu].iloc[0]):
                for u in usulan:
                    if u.kode == kode:
                        u.skor_kecocokan = 100.0
                        u.catatan = (
                            "Didahulukan: selama dokumen kependudukan belum lengkap, "
                            "program bantuan lain tidak dapat ditetapkan bagi keluarga ini."
                        )

        usulan.sort(key=lambda u: (-u.layak, -u.skor_kecocokan))
        for i, u in enumerate(usulan[:maksimum], 1):
            u.peringkat = i
        return usulan[:maksimum]

    # ------------------------------------------------------------------
    def _nilai_program(
        self, p: Program, baris: pd.DataFrame, dominan: set[str]
    ) -> UsulanProgram | None:
        """Nilai kecocokan satu program terhadap satu keluarga."""
        terpenuhi: list[str] = []
        tidak: list[str] = []
        layak = True
        poin_pendukung = 0.0
        bobot_pendukung = 0.0

        for a in p.aturan:
            syarat = {
                "bidang": a.bidang,
                "operator": a.operator.value if hasattr(a.operator, "value") else a.operator,
                "nilai": a.nilai,
            }
            try:
                lulus = bool(evaluasi_syarat(syarat, baris)[0])
            except Exception:  # noqa: BLE001 - aturan rusak tidak boleh menggagalkan seluruh usulan
                logger.warning("Aturan tidak dapat dinilai: %s pada %s", a.bidang, p.kode)
                continue

            nilai_baris = baris[a.bidang].iloc[0] if a.bidang in baris.columns else None
            kalimat = a.keterangan or jelaskan_syarat(syarat, nilai_baris)

            if a.wajib:
                if lulus:
                    terpenuhi.append(kalimat)
                else:
                    layak = False
                    tidak.append(kalimat)
            else:
                bobot = 1.0 / max(1.0, float(a.prioritas) / 10.0)
                bobot_pendukung += bobot
                if lulus:
                    poin_pendukung += bobot
                    terpenuhi.append(kalimat)

        nilai_pendukung = poin_pendukung / bobot_pendukung if bobot_pendukung else 0.5

        # --- Kesesuaian dengan faktor risiko yang mendorong skor ---
        kode_faktor = [f.kode for f in p.faktor_risiko]
        beririsan = [k for k in kode_faktor if k in dominan]
        if dominan and kode_faktor:
            kekuatan = [
                self.peta_kekuatan.get((p.id, f.id), 1.0)
                for f in p.faktor_risiko
                if f.kode in dominan
            ]
            nilai_faktor = float(np.clip(sum(kekuatan) / max(1, len(dominan)), 0.0, 1.0))
        else:
            nilai_faktor = 0.0

        kesiapan = KESIAPAN.get(p.tingkat_eksekusi, 0.5)
        keyakinan = KEYAKINAN_NILAI.get(
            p.tingkat_keyakinan.value if hasattr(p.tingkat_keyakinan, "value") else str(p.tingkat_keyakinan),
            0.6,
        )

        skor = 100.0 * (
            BOBOT["faktor_risiko"] * nilai_faktor
            + BOBOT["aturan_pendukung"] * nilai_pendukung
            + BOBOT["kesiapan"] * kesiapan
            + BOBOT["keyakinan_katalog"] * keyakinan
        )
        if not layak:
            # Kandidat bersyarat tetap ditampilkan namun jelas berada di bawah
            # program yang sudah memenuhi seluruh syarat.
            skor *= 0.45

        # --- Perkiraan manfaat ---
        manfaat, komponen = self._hitung_manfaat(p, baris)

        return UsulanProgram(
            kode=p.kode,
            nama=p.nama_resmi,
            singkatan=p.singkatan,
            skor_kecocokan=round(skor, 1),
            peringkat=0,
            layak=layak,
            jenis_intervensi=p.jenis_intervensi.value
            if hasattr(p.jenis_intervensi, "value")
            else str(p.jenis_intervensi),
            opd=[o.singkatan for o in p.opd],
            tindakan=p.tingkat_eksekusi.tindakan_daerah
            if hasattr(p.tingkat_eksekusi, "tindakan_daerah")
            else "Usulkan",
            faktor_disasar=beririsan or kode_faktor[:3],
            aturan_terpenuhi=terpenuhi[:5],
            aturan_tidak_terpenuhi=tidak[:5],
            perkiraan_manfaat_bulanan=manfaat,
            komponen_berlaku=komponen,
            alasan=self._susun_alasan(p, beririsan, layak, tidak),
            tingkat_keyakinan=p.tingkat_keyakinan.value
            if hasattr(p.tingkat_keyakinan, "value")
            else str(p.tingkat_keyakinan),
            catatan=p.catatan[:280] if p.catatan else None,
        )

    # ------------------------------------------------------------------
    @staticmethod
    def _hitung_manfaat(p: Program, baris: pd.DataFrame) -> tuple[float | None, list[str]]:
        """Perkirakan manfaat bulanan berdasarkan komponen yang berlaku.

        Program seperti PKH tidak memiliki satu nominal tunggal - besarannya
        bergantung susunan keluarga. Menghitung komponen yang benar-benar
        berlaku membuat perkiraan ini berguna bagi penyusunan anggaran, bukan
        sekadar angka contoh.
        """
        total = 0.0
        komponen: list[str] = []
        ada_rupiah = False

        for m in p.manfaat:
            if m.satuan is not SatuanManfaat.RUPIAH:
                continue
            ada_rupiah = True
            syarat = m.syarat_komponen
            if syarat:
                bidang = syarat.get("fitur") or syarat.get("bidang")
                if bidang and bidang in baris.columns:
                    try:
                        if not bool(evaluasi_syarat(syarat, baris)[0]):
                            continue
                    except Exception:  # noqa: BLE001
                        continue
            if m.nominal_per_tahun:
                total += float(m.nominal_per_tahun) / 12.0
                komponen.append(m.komponen)

        if not ada_rupiah:
            return None, []
        if total == 0.0 and p.biaya_satuan_tahunan:
            return round(float(p.biaya_satuan_tahunan) / 12.0, 0), []
        return round(total, 0), komponen

    # ------------------------------------------------------------------
    @staticmethod
    def _susun_alasan(
        p: Program, beririsan: list[str], layak: bool, tidak: list[str]
    ) -> str:
        bagian: list[str] = []
        if beririsan:
            bagian.append(
                f"Menangani faktor risiko dominan keluarga ini ({', '.join(beririsan)})."
            )
        else:
            bagian.append(f"Program {p.jenis_intervensi.value.replace('_', ' ')}.")

        if layak:
            bagian.append("Seluruh syarat wajib terpenuhi.")
        else:
            bagian.append(
                "Belum memenuhi syarat: " + "; ".join(tidak[:2]) + "."
            )

        tindakan = (
            p.tingkat_eksekusi.tindakan_daerah
            if hasattr(p.tingkat_eksekusi, "tindakan_daerah")
            else "Usulkan"
        )
        opd = ", ".join(o.singkatan for o in p.opd) or "OPD belum ditetapkan"
        bagian.append(f"Tindakan: {tindakan} melalui {opd}.")
        return " ".join(bagian)


# ===========================================================================
def paket_intervensi(usulan: list[UsulanProgram]) -> dict[str, Any]:
    """Rangkum usulan menjadi paket lintas OPD yang siap ditugaskan.

    Rekomendasi yang berdiri sendiri-sendiri akan menghasilkan enam surat ke
    enam dinas. Pengelompokan menurut OPD mengubahnya menjadi beberapa
    penugasan yang masing-masing dapat ditindaklanjuti satu pihak - bentuk yang
    benar-benar dapat dijalankan.
    """
    per_opd: dict[str, list[UsulanProgram]] = {}
    for u in usulan:
        if not u.layak:
            continue
        for o in u.opd or ["belum_ditetapkan"]:
            per_opd.setdefault(o, []).append(u)

    total = sum(u.perkiraan_manfaat_bulanan or 0.0 for u in usulan if u.layak)
    return {
        "jumlah_usulan": len(usulan),
        "jumlah_layak": sum(1 for u in usulan if u.layak),
        "perkiraan_manfaat_bulanan_total": round(total, 0),
        "perkiraan_manfaat_tahunan_total": round(total * 12, 0),
        "penugasan": [
            {
                "opd": opd,
                "jumlah_program": len(daftar),
                "program": [u.singkatan for u in daftar],
                "tindakan": sorted({u.tindakan for u in daftar}),
            }
            for opd, daftar in sorted(per_opd.items(), key=lambda x: -len(x[1]))
        ],
    }


__all__ = ["BOBOT", "KESIAPAN", "MesinRekomendasi", "UsulanProgram", "paket_intervensi"]
