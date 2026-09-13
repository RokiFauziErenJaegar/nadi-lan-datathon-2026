"""Alur kerja: verifikasi lapangan, pelaksanaan intervensi, dan hasilnya.

Tiga tabel ini menutup lingkaran yang dijanjikan proposal - dari penandaan,
menuju pemeriksaan, menuju tindakan, kembali menjadi data.

:class:`Verifikasi` memuat satu kolom yang paling menentukan nasib sistem ini
dalam jangka panjang: :attr:`Verifikasi.kondisi_terkoreksi`. Ketika petugas
mendapati keadaan di lapangan berbeda dari catatan sistem, koreksinya tidak
sekadar menutup kasus - ia menjadi data pelatihan. Setiap kunjungan lapangan
memperbaiki model, dan model yang membaik mengirim petugas ke tempat yang lebih
tepat pada putaran berikutnya. Inilah feedback loop pada proposal, dinyatakan
sebagai kolom basis data alih-alih sebagai diagram.
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
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from nadi.db.base import Base, TimestampMixin, sekarang_utc
from nadi.db.enums import HasilVerifikasi, StatusIntervensi
from nadi.db.types import JSONFleksibel, TeksEnum

if TYPE_CHECKING:
    from nadi.db.models.analitik import Kasus, Rekomendasi
    from nadi.db.models.keluarga import Keluarga
    from nadi.db.models.program import OPD, Program
    from nadi.db.models.sistem import Pengguna


class Verifikasi(Base, TimestampMixin):
    """Hasil pemeriksaan manusia atas sebuah kasus.

    Keberadaan tabel ini adalah wujud teknis dari janji "0 keputusan otomatis"
    pada tabel dampak proposal: tidak ada jalur pada aplikasi yang mengubah
    status kasus menjadi tuntas tanpa melewati satu baris di sini, dan setiap
    baris di sini selalu membawa pengenal petugas yang bertanggung jawab.
    """

    __tablename__ = "verifikasi"
    __table_args__ = (
        Index("ix_verifikasi_kasus_waktu", "kasus_id", "waktu"),
        Index("ix_verifikasi_petugas", "pengguna_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    kasus_id: Mapped[int] = mapped_column(
        ForeignKey("kasus.id", ondelete="CASCADE"), nullable=False, index=True
    )
    pengguna_id: Mapped[int] = mapped_column(
        ForeignKey("pengguna.id", ondelete="RESTRICT"), nullable=False
    )
    waktu: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=sekarang_utc
    )

    hasil: Mapped[HasilVerifikasi] = mapped_column(TeksEnum(HasilVerifikasi, 24), nullable=False)
    catatan: Mapped[str | None] = mapped_column(Text, nullable=True)
    metode: Mapped[str] = mapped_column(
        String(24),
        nullable=False,
        default="kunjungan_lapangan",
        doc="kunjungan_lapangan, telepon, musyawarah_pekon, atau pemeriksaan_dokumen.",
    )

    kondisi_terkoreksi: Mapped[dict | None] = mapped_column(
        JSONFleksibel,
        nullable=True,
        doc="Bidang yang dikoreksi petugas beserta nilai lama dan barunya. "
        "Menjadi bahan pelatihan ulang model.",
    )
    setuju_dengan_sistem: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
        doc="Apakah temuan lapangan sejalan dengan penandaan sistem. "
        "Agregatnya menjadi ukuran ketepatan penandaan yang sesungguhnya.",
    )
    durasi_menit: Mapped[int | None] = mapped_column(
        Integer, nullable=True, doc="Lama pemeriksaan, dipakai mengukur beban kerja."
    )

    kasus: Mapped["Kasus"] = relationship("Kasus")
    pengguna: Mapped["Pengguna"] = relationship("Pengguna")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Verifikasi kasus={self.kasus_id} hasil={self.hasil}>"


class Intervensi(Base, TimestampMixin):
    """Satu tindakan yang benar-benar dijalankan bagi sebuah keluarga."""

    __tablename__ = "intervensi"
    __table_args__ = (
        Index("ix_intervensi_keluarga_status", "keluarga_id", "status"),
        Index("ix_intervensi_opd_status", "opd_id", "status"),
        Index("ix_intervensi_gelombang", "gelombang_mulai"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    kode_semu: Mapped[str] = mapped_column(String(20), nullable=False)

    keluarga_id: Mapped[int] = mapped_column(
        ForeignKey("keluarga.id", ondelete="CASCADE"), nullable=False, index=True
    )
    program_id: Mapped[int] = mapped_column(
        ForeignKey("program.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    opd_id: Mapped[int | None] = mapped_column(
        ForeignKey("opd.id", ondelete="SET NULL"), nullable=True
    )

    # Penelusuran balik: intervensi ini berasal dari kasus dan rekomendasi mana.
    # Tanpa tautan ini, mustahil menjawab apakah rekomendasi sistem benar-benar
    # ditindaklanjuti - dan tanpa jawaban itu, tidak ada dasar memperbaikinya.
    kasus_id: Mapped[int | None] = mapped_column(
        ForeignKey("kasus.id", ondelete="SET NULL"), nullable=True
    )
    rekomendasi_id: Mapped[int | None] = mapped_column(
        ForeignKey("rekomendasi.id", ondelete="SET NULL"), nullable=True
    )

    gelombang_mulai: Mapped[int] = mapped_column(Integer, nullable=False)
    tanggal_mulai: Mapped[date | None] = mapped_column(Date, nullable=True)
    tanggal_selesai: Mapped[date | None] = mapped_column(Date, nullable=True)

    status: Mapped[StatusIntervensi] = mapped_column(
        TeksEnum(StatusIntervensi, 24), nullable=False, default=StatusIntervensi.DIRENCANAKAN
    )
    nilai_manfaat_bulanan: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    nilai_manfaat_total: Mapped[float | None] = mapped_column(Float, nullable=True)
    komponen: Mapped[list | None] = mapped_column(JSONFleksibel, nullable=True)

    ditetapkan_oleh_id: Mapped[int | None] = mapped_column(
        ForeignKey("pengguna.id", ondelete="SET NULL"), nullable=True
    )
    catatan: Mapped[str | None] = mapped_column(Text, nullable=True)

    keluarga: Mapped["Keluarga"] = relationship("Keluarga")
    program: Mapped["Program"] = relationship("Program")
    opd: Mapped["OPD | None"] = relationship("OPD")
    kasus: Mapped["Kasus | None"] = relationship("Kasus")
    rekomendasi: Mapped["Rekomendasi | None"] = relationship("Rekomendasi")
    ditetapkan_oleh: Mapped["Pengguna | None"] = relationship("Pengguna")
    hasil: Mapped[list["HasilIntervensi"]] = relationship(
        "HasilIntervensi", back_populates="intervensi", cascade="all, delete-orphan"
    )

    @property
    def berasal_dari_rekomendasi(self) -> bool:
        return self.rekomendasi_id is not None

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Intervensi {self.kode_semu} program={self.program_id} {self.status}>"


class HasilIntervensi(Base, TimestampMixin):
    """Perbandingan keadaan sebelum dan sesudah sebuah intervensi.

    Perlu diperhatikan saat menyajikannya: tabel ini menunjukkan **perubahan**,
    bukan **sebab**. Keluarga yang membaik setelah menerima bantuan mungkin
    membaik karena bantuan itu, atau karena panen membaik, atau karena anaknya
    mulai bekerja. Antarmuka wajib menyatakan perbedaan ini secara terbuka -
    menyebut perubahan sebagai dampak adalah kekeliruan yang akan mengarahkan
    anggaran ke tempat yang salah pada tahun berikutnya.
    """

    __tablename__ = "hasil_intervensi"
    __table_args__ = (
        Index("ix_hasil_intervensi_intervensi", "intervensi_id"),
        Index("ix_hasil_intervensi_penilaian", "penilaian"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    intervensi_id: Mapped[int] = mapped_column(
        ForeignKey("intervensi.id", ondelete="CASCADE"), nullable=False, index=True
    )
    keluarga_id: Mapped[int] = mapped_column(
        ForeignKey("keluarga.id", ondelete="CASCADE"), nullable=False, index=True
    )

    gelombang_sebelum: Mapped[int] = mapped_column(Integer, nullable=False)
    gelombang_sesudah: Mapped[int] = mapped_column(Integer, nullable=False)

    skor_sebelum: Mapped[float | None] = mapped_column(Float, nullable=True)
    skor_sesudah: Mapped[float | None] = mapped_column(Float, nullable=True)
    selisih_skor: Mapped[float | None] = mapped_column(Float, nullable=True)

    miskin_sebelum: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    miskin_sesudah: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    pengeluaran_sebelum: Mapped[float | None] = mapped_column(Float, nullable=True)
    pengeluaran_sesudah: Mapped[float | None] = mapped_column(Float, nullable=True)

    indikator_berubah: Mapped[list | None] = mapped_column(
        JSONFleksibel,
        nullable=True,
        doc="Indikator yang berubah beserta nilai sebelum dan sesudahnya.",
    )
    penilaian: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default="tetap",
        doc="membaik, tetap, atau memburuk.",
    )
    catatan: Mapped[str | None] = mapped_column(Text, nullable=True)
    dinilai_pada: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=sekarang_utc
    )

    intervensi: Mapped["Intervensi"] = relationship("Intervensi", back_populates="hasil")
    keluarga: Mapped["Keluarga"] = relationship("Keluarga")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<HasilIntervensi intervensi={self.intervensi_id} {self.penilaian}>"


__all__ = ["HasilIntervensi", "Intervensi", "Verifikasi"]
