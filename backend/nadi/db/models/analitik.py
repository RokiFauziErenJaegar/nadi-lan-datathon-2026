"""Keluaran analitik: versi model, skor, penandaan kasus, dan rekomendasi.

Satu prinsip menaungi seluruh tabel di bagian ini: **setiap angka harus dapat
ditelusuri kembali ke asalnya.**

Skor tidak berdiri sendiri - ia menyimpan versi model yang menghasilkannya,
sidik jari data yang melatihnya, dan rincian kontribusi tiap fitur. Kasus tidak
sekadar menyandang label - ia membawa bukti yang membuatnya ditandai.
Rekomendasi tidak hanya menyebut nama program - ia mencatat aturan mana yang
terpenuhi dan mana yang tidak.

Kerepotan ini disengaja. Sistem yang memengaruhi siapa menerima bantuan harus
sanggup menjawab pertanyaan "mengapa" berbulan-bulan kemudian, ketika model
sudah dilatih ulang dan orang yang membuat keputusan sudah berpindah tugas.
Pelajaran dari kegagalan sistem serupa di negara lain hampir selalu bermuara
pada hal yang sama: tidak ada yang dapat menjelaskan ulang bagaimana sebuah
keputusan terbentuk.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from nadi.db.base import Base, TimestampMixin, sekarang_utc
from nadi.db.enums import JenisAnomali, KategoriRisiko, StatusKasus
from nadi.db.types import JSONFleksibel, TeksEnum

if TYPE_CHECKING:
    from nadi.db.models.keluarga import Keluarga
    from nadi.db.models.program import OPD, Program
    from nadi.db.models.sistem import Pengguna


# ---------------------------------------------------------------------------
# Versi model
# ---------------------------------------------------------------------------
class VersiModel(Base, TimestampMixin):
    """Satu model terlatih beserta metrik dan asal-usulnya.

    Menyimpan metrik bersama modelnya, bukan di dalam laporan terpisah, menutup
    celah yang mudah terjadi: laporan yang mengklaim AUC tertentu sementara
    model yang benar-benar berjalan di peladen adalah versi lain.
    """

    __tablename__ = "versi_model"
    __table_args__ = (
        UniqueConstraint("nama", "versi", name="uq_versi_model_nama_versi"),
        Index("ix_versi_model_aktif", "jenis", "aktif"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nama: Mapped[str] = mapped_column(String(64), nullable=False)
    versi: Mapped[str] = mapped_column(String(24), nullable=False, doc="Misalnya v1.0.0.")
    jenis: Mapped[str] = mapped_column(
        String(24),
        nullable=False,
        doc="baseline, gbm, anomali, atau kalibrator.",
    )
    algoritma: Mapped[str | None] = mapped_column(String(64), nullable=True)

    dilatih_pada: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=sekarang_utc
    )
    gelombang_latih: Mapped[list | None] = mapped_column(
        JSONFleksibel, nullable=True, doc="Gelombang yang dipakai melatih model."
    )
    gelombang_uji: Mapped[list | None] = mapped_column(JSONFleksibel, nullable=True)
    jumlah_baris_latih: Mapped[int | None] = mapped_column(Integer, nullable=True)
    jumlah_fitur: Mapped[int | None] = mapped_column(Integer, nullable=True)

    metrik: Mapped[dict | None] = mapped_column(
        JSONFleksibel,
        nullable=True,
        doc="AUC, recall pada ambang, presisi, Brier score, dan metrik per kelompok.",
    )
    metrik_keadilan: Mapped[dict | None] = mapped_column(
        JSONFleksibel,
        nullable=True,
        doc="Selisih kinerja antar kelompok: desa-kota, jenis kelamin kepala keluarga, kecamatan.",
    )
    kepentingan_fitur: Mapped[dict | None] = mapped_column(JSONFleksibel, nullable=True)

    sidik_jari_dataset: Mapped[str | None] = mapped_column(
        String(32), nullable=True, doc="Sidik jari data latih, agar hasil dapat direproduksi."
    )
    jalur_artefak: Mapped[str | None] = mapped_column(String(300), nullable=True)
    catatan: Mapped[str | None] = mapped_column(Text, nullable=True)
    aktif: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, doc="Model yang sedang dipakai melayani permintaan."
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<VersiModel {self.nama} {self.versi} aktif={self.aktif}>"


# ---------------------------------------------------------------------------
# Skor kerentanan
# ---------------------------------------------------------------------------
class SkorKerentanan(Base, TimestampMixin):
    """NADI Vulnerability Score untuk satu keluarga pada satu gelombang.

    Dua angka disimpan berdampingan dan sengaja tidak digabungkan:

    * :attr:`skor` - keluaran model gradient boosting, lebih tajam.
    * :attr:`skor_baseline` - indeks berbobot yang dapat dijelaskan seluruhnya
      dengan aritmetika sederhana.

    Menyimpan keduanya memungkinkan sistem menjawab pertanyaan yang wajar
    diajukan seorang pejabat: "apakah kecerdasan buatan ini benar-benar lebih
    baik daripada aturan biasa?" Perbandingan keduanya menjadi bukti, bukan
    klaim. Bila selisihnya kecil, indeks sederhana yang menang - dan itu pun
    temuan yang jujur untuk disampaikan.
    """

    __tablename__ = "skor_kerentanan"
    __table_args__ = (
        UniqueConstraint(
            "keluarga_id", "gelombang", "versi_model_id", name="uq_skor_keluarga_gelombang_model"
        ),
        Index("ix_skor_gelombang_nilai", "gelombang", "skor"),
        Index("ix_skor_gelombang_kategori", "gelombang", "kategori"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    keluarga_id: Mapped[int] = mapped_column(
        ForeignKey("keluarga.id", ondelete="CASCADE"), nullable=False, index=True
    )
    gelombang: Mapped[int] = mapped_column(Integer, nullable=False)
    versi_model_id: Mapped[int] = mapped_column(
        ForeignKey("versi_model.id", ondelete="RESTRICT"), nullable=False, index=True
    )

    skor: Mapped[float] = mapped_column(Float, nullable=False, doc="Skor 0 sampai 100.")
    probabilitas: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        doc="Peluang terkalibrasi keluarga jatuh atau tetap miskin pada gelombang berikutnya.",
    )
    kategori: Mapped[KategoriRisiko] = mapped_column(TeksEnum(KategoriRisiko, 16), nullable=False)
    skor_baseline: Mapped[float | None] = mapped_column(Float, nullable=True)
    peringkat_kabupaten: Mapped[int | None] = mapped_column(Integer, nullable=True)
    persentil: Mapped[float | None] = mapped_column(Float, nullable=True)

    # --- Penjelasan ---
    kontribusi_fitur: Mapped[list | None] = mapped_column(
        JSONFleksibel,
        nullable=True,
        doc="Nilai TreeSHAP per fitur: nama, nilai, kontribusi, dan faktor risiko terkait.",
    )
    faktor_dominan: Mapped[list | None] = mapped_column(
        JSONFleksibel, nullable=True, doc="Kode faktor risiko yang paling mendorong skor."
    )
    perubahan_dari_sebelumnya: Mapped[float | None] = mapped_column(
        Float, nullable=True, doc="Selisih skor terhadap gelombang sebelumnya."
    )
    penjelasan_singkat: Mapped[str | None] = mapped_column(
        Text, nullable=True, doc="Ringkasan berbahasa Indonesia, dihasilkan templat lokal."
    )

    dihitung_pada: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=sekarang_utc
    )

    keluarga: Mapped["Keluarga"] = relationship("Keluarga")
    versi_model: Mapped["VersiModel"] = relationship("VersiModel")

    @property
    def memburuk(self) -> bool:
        return (self.perubahan_dari_sebelumnya or 0.0) > 0

    def __repr__(self) -> str:  # pragma: no cover
        return f"<SkorKerentanan keluarga={self.keluarga_id} gelombang={self.gelombang} skor={self.skor:.1f}>"


# ---------------------------------------------------------------------------
# Kasus untuk verifikasi
# ---------------------------------------------------------------------------
class Kasus(Base, TimestampMixin):
    """Satu perkara yang ditandai sistem untuk diperiksa manusia.

    Penamaan dipilih dengan sadar. Baris ini bukan "keputusan", bukan pula
    "pelanggaran" - ia adalah **kasus untuk diperiksa**. Perbedaan istilah ini
    menentukan bagaimana petugas memperlakukannya, dan menjaga sistem tetap
    berada pada perannya sebagai pendukung keputusan.
    """

    __tablename__ = "kasus"
    __table_args__ = (
        UniqueConstraint("kode_semu", name="uq_kasus_kode_semu"),
        Index("ix_kasus_status_prioritas", "status", "skor_prioritas"),
        Index("ix_kasus_gelombang_jenis", "gelombang", "jenis"),
        Index("ix_kasus_opd_status", "opd_ditugaskan_id", "status"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    kode_semu: Mapped[str] = mapped_column(String(20), nullable=False)
    keluarga_id: Mapped[int] = mapped_column(
        ForeignKey("keluarga.id", ondelete="CASCADE"), nullable=False, index=True
    )
    gelombang: Mapped[int] = mapped_column(Integer, nullable=False)

    jenis: Mapped[JenisAnomali] = mapped_column(TeksEnum(JenisAnomali, 32), nullable=False)
    skor_prioritas: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        doc="Gabungan tingkat kerentanan dan keyakinan penandaan, bernilai 0 sampai 100.",
    )
    tingkat_prioritas: Mapped[int] = mapped_column(
        Integer, nullable=False, default=3, doc="1 paling mendesak sampai 5 paling longgar."
    )

    alasan: Mapped[list | None] = mapped_column(
        JSONFleksibel,
        nullable=True,
        doc="Daftar alasan penandaan: kode, ringkasan, bukti, dan tingkat keyakinan.",
    )
    sumber_deteksi: Mapped[str] = mapped_column(
        String(24),
        nullable=False,
        default="aturan",
        doc="aturan, statistik, model, atau gabungan.",
    )
    ringkasan: Mapped[str | None] = mapped_column(Text, nullable=True)

    # --- Alur kerja ---
    status: Mapped[StatusKasus] = mapped_column(
        TeksEnum(StatusKasus, 32), nullable=False, default=StatusKasus.BARU
    )
    opd_ditugaskan_id: Mapped[int | None] = mapped_column(
        ForeignKey("opd.id", ondelete="SET NULL"), nullable=True
    )
    pengguna_ditugaskan_id: Mapped[int | None] = mapped_column(
        ForeignKey("pengguna.id", ondelete="SET NULL"), nullable=True
    )
    tenggat: Mapped[date | None] = mapped_column(Date, nullable=True)
    ditutup_pada: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    keluarga: Mapped["Keluarga"] = relationship("Keluarga")
    opd_ditugaskan: Mapped["OPD | None"] = relationship("OPD")
    pengguna_ditugaskan: Mapped["Pengguna | None"] = relationship("Pengguna")
    rekomendasi: Mapped[list["Rekomendasi"]] = relationship(
        "Rekomendasi", back_populates="kasus", cascade="all, delete-orphan"
    )

    @property
    def terbuka(self) -> bool:
        return self.status.terbuka

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Kasus {self.kode_semu} {self.jenis.value} {self.status.value}>"


# ---------------------------------------------------------------------------
# Rekomendasi intervensi
# ---------------------------------------------------------------------------
class Rekomendasi(Base, TimestampMixin):
    """Usulan program bagi satu keluarga, beserta dasar pertimbangannya.

    Kolom :attr:`aturan_tidak_terpenuhi` sama pentingnya dengan
    :attr:`aturan_terpenuhi`. Petugas perlu mengetahui bukan hanya mengapa
    sebuah program disarankan, melainkan juga apa yang masih kurang - sebab
    seringkali yang kurang itu dapat dilengkapi, dan justru itulah tindakan
    paling berguna yang dapat diambil hari itu.
    """

    __tablename__ = "rekomendasi"
    __table_args__ = (
        Index("ix_rekomendasi_keluarga_gelombang", "keluarga_id", "gelombang"),
        Index("ix_rekomendasi_kasus_peringkat", "kasus_id", "peringkat"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    keluarga_id: Mapped[int] = mapped_column(
        ForeignKey("keluarga.id", ondelete="CASCADE"), nullable=False, index=True
    )
    kasus_id: Mapped[int | None] = mapped_column(
        ForeignKey("kasus.id", ondelete="CASCADE"), nullable=True, index=True
    )
    program_id: Mapped[int] = mapped_column(
        ForeignKey("program.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    gelombang: Mapped[int] = mapped_column(Integer, nullable=False)

    skor_kecocokan: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.0, doc="Nilai kecocokan 0 sampai 100."
    )
    peringkat: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    layak: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        doc="Seluruh aturan wajib terpenuhi. Bila salah, rekomendasi tetap "
        "ditampilkan sebagai kandidat bersyarat.",
    )

    faktor_risiko_disasar: Mapped[list | None] = mapped_column(JSONFleksibel, nullable=True)
    aturan_terpenuhi: Mapped[list | None] = mapped_column(JSONFleksibel, nullable=True)
    aturan_tidak_terpenuhi: Mapped[list | None] = mapped_column(JSONFleksibel, nullable=True)
    alasan: Mapped[str | None] = mapped_column(Text, nullable=True)
    perkiraan_manfaat_bulanan: Mapped[float | None] = mapped_column(Float, nullable=True)
    komponen_berlaku: Mapped[list | None] = mapped_column(JSONFleksibel, nullable=True)

    status: Mapped[str] = mapped_column(
        String(24),
        nullable=False,
        default="diusulkan",
        doc="diusulkan, disetujui, ditolak, atau ditindaklanjuti.",
    )
    catatan_petugas: Mapped[str | None] = mapped_column(Text, nullable=True)

    keluarga: Mapped["Keluarga"] = relationship("Keluarga")
    kasus: Mapped["Kasus | None"] = relationship("Kasus", back_populates="rekomendasi")
    program: Mapped["Program"] = relationship("Program")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Rekomendasi keluarga={self.keluarga_id} program={self.program_id} skor={self.skor_kecocokan:.0f}>"


__all__ = ["Kasus", "Rekomendasi", "SkorKerentanan", "VersiModel"]
