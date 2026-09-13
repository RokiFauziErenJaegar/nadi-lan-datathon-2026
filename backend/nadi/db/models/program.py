"""Katalog program, faktor risiko, aturan kelayakan, dan kepesertaan.

Bagian ini adalah basis pengetahuan yang membuat NADI dapat *merekomendasikan*,
bukan sekadar *menandai*. Rancangannya berdiri di atas satu gagasan:

    faktor risiko  →  jenis intervensi  →  program  →  OPD penanggung jawab

:class:`FaktorRisiko` sengaja dijadikan entitas tersendiri, bukan sekadar
label teks di dalam rekomendasi. Ia menjadi kosakata bersama antara tiga
bagian sistem yang selama ini sulit disambungkan:

* keluaran model - fitur mana yang mendorong skor naik,
* aturan penandaan - kondisi apa yang perlu diverifikasi,
* katalog program - masalah apa yang sebenarnya diselesaikan program ini.

Tanpa kosakata bersama, penjelasan model dan daftar rekomendasi akan berjalan
sendiri-sendiri, dan pengguna harus menghubungkannya di kepala masing-masing.
Dengan kosakata bersama, sistem dapat berkata: "skor naik karena sanitasi tidak
layak, dan berikut tiga program yang menangani persoalan itu beserta dinas yang
berwenang."

Katalog awal diturunkan dari riset regulasi yang tersimpan di
``docs/research/02-katalog-program-intervensi.md``. Setiap angka membawa
tingkat keyakinannya sendiri - lihat :class:`nadi.db.enums.TingkatKeyakinan`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Column,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from nadi.db.base import Base, TimestampMixin
from nadi.db.enums import (
    BasisDataProgram,
    DimensiRisiko,
    FrekuensiProgram,
    JenisIntervensi,
    OperatorAturan,
    SatuanManfaat,
    StatusKepesertaan,
    StatusProgram,
    SumberDana,
    TingkatEksekusi,
    TingkatKeyakinan,
    TipeAturan,
)
from nadi.db.types import JSONFleksibel, TeksEnum

if TYPE_CHECKING:
    from nadi.db.models.keluarga import Keluarga

# ---------------------------------------------------------------------------
# Tabel penghubung
# ---------------------------------------------------------------------------
program_opd = Table(
    "program_opd",
    Base.metadata,
    Column("program_id", ForeignKey("program.id", ondelete="CASCADE"), primary_key=True),
    Column("opd_id", ForeignKey("opd.id", ondelete="CASCADE"), primary_key=True),
    Column(
        "peran",
        String(24),
        nullable=False,
        default="pelaksana",
        doc="pelaksana, pendukung, atau pengusul",
    ),
)

program_faktor_risiko = Table(
    "program_faktor_risiko",
    Base.metadata,
    Column("program_id", ForeignKey("program.id", ondelete="CASCADE"), primary_key=True),
    Column("faktor_risiko_id", ForeignKey("faktor_risiko.id", ondelete="CASCADE"), primary_key=True),
    Column(
        "kekuatan",
        Float,
        nullable=False,
        default=1.0,
        doc="Seberapa langsung program ini menangani faktor tersebut, bernilai 0 sampai 1.",
    ),
)


# ---------------------------------------------------------------------------
# Organisasi Perangkat Daerah
# ---------------------------------------------------------------------------
class OPD(Base, TimestampMixin):
    """Satu Organisasi Perangkat Daerah.

    Rekomendasi yang tidak menyebut siapa yang harus bertindak akan berhenti di
    layar. Menautkan setiap program ke OPD penanggung jawab adalah syarat agar
    orkestrasi lintas dinas yang dijanjikan proposal benar-benar terjadi.
    """

    __tablename__ = "opd"
    __table_args__ = (UniqueConstraint("kode", name="uq_opd_kode"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    kode: Mapped[str] = mapped_column(String(48), nullable=False)
    nama: Mapped[str] = mapped_column(String(160), nullable=False)
    singkatan: Mapped[str] = mapped_column(String(32), nullable=False)
    tupoksi: Mapped[str | None] = mapped_column(Text, nullable=True)
    relevansi_kemiskinan: Mapped[str] = mapped_column(
        String(12),
        nullable=False,
        default="sedang",
        doc="tinggi, sedang, atau rendah - dipakai mengurutkan daftar penugasan.",
    )
    situs: Mapped[str | None] = mapped_column(String(200), nullable=True)
    aktif: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    program: Mapped[list["Program"]] = relationship(
        "Program", secondary=program_opd, back_populates="opd"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<OPD {self.singkatan}>"


# ---------------------------------------------------------------------------
# Faktor risiko
# ---------------------------------------------------------------------------
class FaktorRisiko(Base, TimestampMixin):
    """Satu faktor pendorong kemiskinan yang dapat dikenali dari data.

    Kode mengikuti penomoran hasil riset (R01 sampai R20) agar dapat dilacak
    kembali ke sumbernya.
    """

    __tablename__ = "faktor_risiko"
    __table_args__ = (
        UniqueConstraint("kode", name="uq_faktor_risiko_kode"),
        Index("ix_faktor_risiko_dimensi", "dimensi"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    kode: Mapped[str] = mapped_column(String(8), nullable=False, doc="Misalnya R01.")
    nama: Mapped[str] = mapped_column(String(160), nullable=False)
    deskripsi: Mapped[str | None] = mapped_column(Text, nullable=True)
    dimensi: Mapped[DimensiRisiko] = mapped_column(TeksEnum(DimensiRisiko, 24), nullable=False)

    indikator: Mapped[str | None] = mapped_column(
        Text, nullable=True, doc="Bagaimana faktor ini dikenali dari data, dalam bahasa manusia."
    )
    ekspresi_deteksi: Mapped[dict | None] = mapped_column(
        JSONFleksibel,
        nullable=True,
        doc="Aturan terstruktur untuk mendeteksi faktor ini dari sebuah snapshot.",
    )
    fitur_terkait: Mapped[list | None] = mapped_column(
        JSONFleksibel,
        nullable=True,
        doc="Nama fitur model yang memetakan ke faktor ini, penghubung keluaran SHAP ke rekomendasi.",
    )

    bobot_dasar: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=1.0,
        doc="Bobot faktor pada indeks kerentanan dasar yang interpretable.",
    )
    urutan_tampil: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    jenis_intervensi_utama: Mapped[JenisIntervensi | None] = mapped_column(
        TeksEnum(JenisIntervensi, 32), nullable=True
    )
    aktif: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    program: Mapped[list["Program"]] = relationship(
        "Program", secondary=program_faktor_risiko, back_populates="faktor_risiko"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<FaktorRisiko {self.kode} {self.nama}>"


# ---------------------------------------------------------------------------
# Program
# ---------------------------------------------------------------------------
class Program(Base, TimestampMixin):
    """Satu program perlindungan sosial atau pengentasan kemiskinan."""

    __tablename__ = "program"
    __table_args__ = (
        UniqueConstraint("kode", name="uq_program_kode"),
        Index("ix_program_status_jenis", "status", "jenis_intervensi"),
        Index("ix_program_desil", "desil_min", "desil_maks"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    kode: Mapped[str] = mapped_column(String(32), nullable=False, doc="Misalnya PKH atau SEMBAKO.")
    nama_resmi: Mapped[str] = mapped_column(String(200), nullable=False)
    singkatan: Mapped[str] = mapped_column(String(32), nullable=False)
    deskripsi: Mapped[str | None] = mapped_column(Text, nullable=True)

    jenis_intervensi: Mapped[JenisIntervensi] = mapped_column(
        TeksEnum(JenisIntervensi, 32), nullable=False
    )
    kementerian: Mapped[str | None] = mapped_column(String(160), nullable=True)
    tingkat_eksekusi: Mapped[TingkatEksekusi] = mapped_column(
        TeksEnum(TingkatEksekusi, 32),
        nullable=False,
        default=TingkatEksekusi.PUSAT_DISALURKAN_DI_DAERAH,
    )
    basis_data: Mapped[BasisDataProgram] = mapped_column(
        TeksEnum(BasisDataProgram, 24), nullable=False, default=BasisDataProgram.DTSEN
    )
    sumber_dana: Mapped[SumberDana] = mapped_column(
        TeksEnum(SumberDana, 24), nullable=False, default=SumberDana.APBN
    )
    frekuensi: Mapped[FrekuensiProgram] = mapped_column(
        TeksEnum(FrekuensiProgram, 24), nullable=False, default=FrekuensiProgram.BULANAN
    )

    # --- Gerbang kelayakan berbasis desil ---
    # Hampir seluruh program nasional memakai desil DTSEN sebagai saringan
    # pertama. Menyimpannya sebagai kolom tersendiri, bukan sekadar salah satu
    # baris aturan, membuat penyaringan kandidat dapat dilakukan basis data -
    # jauh lebih cepat daripada mengevaluasi aturan satu per satu.
    desil_min: Mapped[int | None] = mapped_column(Integer, nullable=True, default=1)
    desil_maks: Mapped[int | None] = mapped_column(Integer, nullable=True, default=4)

    mekanisme_penyaluran: Mapped[str | None] = mapped_column(Text, nullable=True)
    dasar_hukum: Mapped[list | None] = mapped_column(JSONFleksibel, nullable=True)
    sumber_url: Mapped[list | None] = mapped_column(JSONFleksibel, nullable=True)

    kuota_tahunan: Mapped[int | None] = mapped_column(
        Integer, nullable=True, doc="Batas jumlah penerima per tahun, bila ada."
    )
    biaya_satuan_tahunan: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        doc="Perkiraan biaya per penerima per tahun. Dipakai simulator kebijakan.",
    )

    status: Mapped[StatusProgram] = mapped_column(
        TeksEnum(StatusProgram, 16), nullable=False, default=StatusProgram.AKTIF
    )
    tingkat_keyakinan: Mapped[TingkatKeyakinan] = mapped_column(
        TeksEnum(TingkatKeyakinan, 24), nullable=False, default=TingkatKeyakinan.CUKUP_KUAT
    )
    catatan: Mapped[str | None] = mapped_column(Text, nullable=True)
    urutan_tampil: Mapped[int] = mapped_column(Integer, nullable=False, default=100)

    # --- Relasi ---
    opd: Mapped[list["OPD"]] = relationship(
        "OPD", secondary=program_opd, back_populates="program"
    )
    faktor_risiko: Mapped[list["FaktorRisiko"]] = relationship(
        "FaktorRisiko", secondary=program_faktor_risiko, back_populates="program"
    )
    manfaat: Mapped[list["ManfaatProgram"]] = relationship(
        "ManfaatProgram", back_populates="program", cascade="all, delete-orphan"
    )
    aturan: Mapped[list["AturanKelayakan"]] = relationship(
        "AturanKelayakan", back_populates="program", cascade="all, delete-orphan"
    )

    @property
    def opd_utama(self) -> "OPD | None":
        return self.opd[0] if self.opd else None

    @property
    def nilai_manfaat_tahunan(self) -> float:
        """Jumlah seluruh komponen manfaat berupa rupiah dalam setahun."""
        return sum(
            m.nominal_per_tahun or 0.0
            for m in self.manfaat
            if m.satuan is SatuanManfaat.RUPIAH
        )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Program {self.kode}>"


class ManfaatProgram(Base, TimestampMixin):
    """Satu komponen manfaat di dalam sebuah program.

    Diperlukan karena program seperti PKH tidak memiliki satu nominal tunggal:
    besarannya bergantung pada susunan keluarga - ada komponen ibu hamil, anak
    sekolah, lansia, dan disabilitas, yang dapat diterima bersamaan. Menyimpan
    satu angka saja akan membuat perkiraan manfaat keliru bagi hampir setiap
    keluarga, dan simulator kebijakan ikut keliru bersamanya.
    """

    __tablename__ = "manfaat_program"
    __table_args__ = (
        UniqueConstraint("program_id", "komponen", name="uq_manfaat_program_komponen"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    program_id: Mapped[int] = mapped_column(
        ForeignKey("program.id", ondelete="CASCADE"), nullable=False, index=True
    )

    komponen: Mapped[str] = mapped_column(String(48), nullable=False, doc="Misalnya anak_sma.")
    label: Mapped[str] = mapped_column(String(160), nullable=False)
    nominal_per_periode: Mapped[float | None] = mapped_column(Float, nullable=True)
    nominal_per_tahun: Mapped[float | None] = mapped_column(Float, nullable=True)
    satuan: Mapped[SatuanManfaat] = mapped_column(
        TeksEnum(SatuanManfaat, 16), nullable=False, default=SatuanManfaat.RUPIAH
    )
    frekuensi: Mapped[FrekuensiProgram] = mapped_column(
        TeksEnum(FrekuensiProgram, 24), nullable=False, default=FrekuensiProgram.BULANAN
    )

    syarat_komponen: Mapped[dict | None] = mapped_column(
        JSONFleksibel,
        nullable=True,
        doc="Syarat agar komponen ini berlaku, misalnya adanya anak jenjang SMA.",
    )
    tingkat_keyakinan: Mapped[TingkatKeyakinan] = mapped_column(
        TeksEnum(TingkatKeyakinan, 24), nullable=False, default=TingkatKeyakinan.CUKUP_KUAT
    )
    catatan: Mapped[str | None] = mapped_column(Text, nullable=True)

    program: Mapped["Program"] = relationship("Program", back_populates="manfaat")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ManfaatProgram {self.program_id}/{self.komponen}>"


class AturanKelayakan(Base, TimestampMixin):
    """Satu syarat kelayakan yang dapat dievaluasi mesin.

    Aturan disimpan sebagai data, bukan sebagai kode. Konsekuensinya penting
    bagi keberlanjutan: ketika kriteria sebuah program berubah - dan kriteria
    bansos berubah cukup sering - petugas dinas dapat memutakhirkannya lewat
    antarmuka, tanpa menunggu pengembang menerbitkan versi baru aplikasi. Ini
    yang dimaksud "knowledge base program dapat dipelihara OPD" pada bagian
    keberlanjutan proposal.
    """

    __tablename__ = "aturan_kelayakan"
    __table_args__ = (Index("ix_aturan_program_wajib", "program_id", "wajib"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    program_id: Mapped[int] = mapped_column(
        ForeignKey("program.id", ondelete="CASCADE"), nullable=False, index=True
    )

    tipe: Mapped[TipeAturan] = mapped_column(TeksEnum(TipeAturan, 24), nullable=False)
    bidang: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        doc="Nama bidang pada snapshot atau fitur turunan yang diperiksa.",
    )
    operator: Mapped[OperatorAturan] = mapped_column(TeksEnum(OperatorAturan, 16), nullable=False)
    nilai: Mapped[dict | list | None] = mapped_column(JSONFleksibel, nullable=True)

    wajib: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        doc="Aturan wajib menggugurkan kelayakan bila tidak terpenuhi; "
        "aturan tidak wajib hanya menambah nilai kecocokan.",
    )
    prioritas: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    keterangan: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        doc="Penjelasan berbahasa manusia yang ditampilkan sebagai alasan kepada pengguna.",
    )
    tingkat_keyakinan: Mapped[TingkatKeyakinan] = mapped_column(
        TeksEnum(TingkatKeyakinan, 24), nullable=False, default=TingkatKeyakinan.CUKUP_KUAT
    )

    program: Mapped["Program"] = relationship("Program", back_populates="aturan")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<AturanKelayakan {self.bidang} {self.operator.value}>"


# ---------------------------------------------------------------------------
# Kepesertaan
# ---------------------------------------------------------------------------
class KepesertaanProgram(Base, TimestampMixin):
    """Catatan bahwa sebuah keluarga menerima sebuah program pada rentang waktu.

    Tabel inilah yang dibandingkan dengan profil kebutuhan keluarga untuk
    menemukan ketidaksesuaian sasaran - keluarga sangat rentan yang belum
    tersentuh, maupun penerima yang kriterianya tidak lagi terpenuhi.
    """

    __tablename__ = "kepesertaan_program"
    __table_args__ = (
        Index("ix_kepesertaan_keluarga_program", "keluarga_id", "program_id"),
        Index("ix_kepesertaan_rentang", "gelombang_mulai", "gelombang_selesai"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    keluarga_id: Mapped[int] = mapped_column(
        ForeignKey("keluarga.id", ondelete="CASCADE"), nullable=False, index=True
    )
    program_id: Mapped[int] = mapped_column(
        ForeignKey("program.id", ondelete="RESTRICT"), nullable=False, index=True
    )

    gelombang_mulai: Mapped[int] = mapped_column(Integer, nullable=False)
    gelombang_selesai: Mapped[int | None] = mapped_column(
        Integer, nullable=True, doc="Kosong berarti masih berjalan."
    )
    status: Mapped[StatusKepesertaan] = mapped_column(
        TeksEnum(StatusKepesertaan, 24), nullable=False, default=StatusKepesertaan.AKTIF
    )
    nilai_manfaat_bulanan: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    komponen_diterima: Mapped[list | None] = mapped_column(
        JSONFleksibel, nullable=True, doc="Komponen manfaat yang berlaku bagi keluarga ini."
    )
    sumber_penetapan: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="dtsen",
        doc="dtsen, usulan_daerah, musyawarah_pekon, atau rekomendasi_nadi.",
    )
    catatan: Mapped[str | None] = mapped_column(Text, nullable=True)

    keluarga: Mapped["Keluarga"] = relationship("Keluarga")
    program: Mapped["Program"] = relationship("Program")

    def aktif_pada(self, gelombang: int) -> bool:
        if gelombang < self.gelombang_mulai:
            return False
        if self.gelombang_selesai is not None and gelombang >= self.gelombang_selesai:
            return False
        return self.status.sedang_menerima

    def __repr__(self) -> str:  # pragma: no cover
        return f"<KepesertaanProgram keluarga={self.keluarga_id} program={self.program_id}>"


__all__ = [
    "OPD",
    "AturanKelayakan",
    "FaktorRisiko",
    "KepesertaanProgram",
    "ManfaatProgram",
    "Program",
    "program_faktor_risiko",
    "program_opd",
]
