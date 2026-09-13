"""Pengguna, jejak audit, dan catatan pemanggilan layanan AI.

Undang-Undang Nomor 27 Tahun 2022 mewajibkan pengendali data pribadi mampu
menunjukkan siapa mengakses apa dan kapan. :class:`JejakAudit` memenuhi
kewajiban itu.

:class:`CatatanPermintaanAI` melangkah lebih jauh dari yang diwajibkan.
Proposal NADI menyatakan data mentah keluarga tidak dikirim ke layanan AI
eksternal. Pernyataan semacam itu mudah diucapkan dan sulit dibuktikan. Tabel
ini mencatat setiap pemanggilan beserta hasil pemindaian pengenal pribadinya,
sehingga pernyataan tersebut berubah menjadi sesuatu yang dapat diaudit -
termasuk oleh pihak di luar tim pengembang.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
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
from nadi.db.types import JSONFleksibel, TeksEnum
from nadi.security.rbac import Peran

if TYPE_CHECKING:
    from nadi.db.models.program import OPD


class Pengguna(Base, TimestampMixin):
    """Akun pengguna sistem."""

    __tablename__ = "pengguna"
    __table_args__ = (
        UniqueConstraint("nama_pengguna", name="uq_pengguna_nama_pengguna"),
        Index("ix_pengguna_peran_aktif", "peran", "aktif"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nama_pengguna: Mapped[str] = mapped_column(String(64), nullable=False)
    nama_lengkap: Mapped[str] = mapped_column(String(160), nullable=False)
    cernaan_sandi: Mapped[str] = mapped_column(String(120), nullable=False)

    peran: Mapped[Peran] = mapped_column(TeksEnum(Peran, 24), nullable=False)
    jabatan: Mapped[str | None] = mapped_column(String(160), nullable=True)
    opd_id: Mapped[int | None] = mapped_column(
        ForeignKey("opd.id", ondelete="SET NULL"), nullable=True
    )
    wilayah_akses: Mapped[list | None] = mapped_column(
        JSONFleksibel,
        nullable=True,
        doc="Daftar kode wilayah yang boleh diakses. Kosong berarti seluruh kabupaten.",
    )

    aktif: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    harus_ganti_sandi: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    terakhir_masuk: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    jumlah_gagal_masuk: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    terkunci_sampai: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    opd: Mapped["OPD | None"] = relationship("OPD")

    @property
    def terkunci(self) -> bool:
        if self.terkunci_sampai is None:
            return False
        return self.terkunci_sampai > sekarang_utc()

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Pengguna {self.nama_pengguna} ({self.peran})>"


class JejakAudit(Base):
    """Satu baris jejak audit.

    Tabel ini hanya bertambah. Tidak ada jalur pada aplikasi yang memperbarui
    atau menghapus barisnya - jejak audit yang dapat disunting bukanlah jejak
    audit. Karena itu pula :class:`TimestampMixin` tidak dipakai di sini:
    kolom "diperbarui pada" akan menyiratkan sesuatu yang tidak boleh terjadi.
    """

    __tablename__ = "jejak_audit"
    __table_args__ = (
        Index("ix_jejak_waktu", "waktu"),
        Index("ix_jejak_pengguna_waktu", "pengguna_id", "waktu"),
        Index("ix_jejak_entitas", "entitas", "entitas_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    waktu: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=sekarang_utc
    )

    pengguna_id: Mapped[int | None] = mapped_column(
        ForeignKey("pengguna.id", ondelete="SET NULL"), nullable=True
    )
    # Nama dan peran disalin, tidak sekadar dirujuk. Bila akun kelak dihapus
    # atau perannya berubah, jejak tetap menunjukkan keadaan pada saat kejadian.
    nama_pengguna: Mapped[str | None] = mapped_column(String(64), nullable=True)
    peran: Mapped[str | None] = mapped_column(String(24), nullable=True)

    aksi: Mapped[str] = mapped_column(
        String(64), nullable=False, doc="Misalnya buka_keluarga atau verifikasi_kasus."
    )
    entitas: Mapped[str | None] = mapped_column(String(48), nullable=True)
    entitas_id: Mapped[str | None] = mapped_column(String(48), nullable=True)
    ringkasan: Mapped[str | None] = mapped_column(Text, nullable=True)

    alamat_ip: Mapped[str | None] = mapped_column(String(64), nullable=True)
    agen_pengguna: Mapped[str | None] = mapped_column(String(300), nullable=True)
    berhasil: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    rincian: Mapped[dict | None] = mapped_column(JSONFleksibel, nullable=True)

    pengguna: Mapped["Pengguna | None"] = relationship("Pengguna")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<JejakAudit {self.aksi} oleh {self.nama_pengguna}>"


class CatatanPermintaanAI(Base):
    """Catatan satu pemanggilan layanan model bahasa.

    Isi percakapan **tidak** disimpan. Yang dicatat adalah bentuknya: berapa
    besar muatannya, apakah lolos pemindaian pengenal pribadi, model apa yang
    menjawab, dan berapa lama. Menyimpan isi percakapan justru akan menciptakan
    tempat penampungan data baru - persis yang hendak dihindari.
    """

    __tablename__ = "catatan_permintaan_ai"
    __table_args__ = (Index("ix_catatan_ai_waktu", "waktu"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    waktu: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=sekarang_utc
    )

    pengguna_id: Mapped[int | None] = mapped_column(
        ForeignKey("pengguna.id", ondelete="SET NULL"), nullable=True
    )
    keperluan: Mapped[str] = mapped_column(
        String(48), nullable=False, doc="copilot, penjelasan_skor, ringkasan_wilayah, dan sejenisnya."
    )

    penyedia: Mapped[str | None] = mapped_column(String(48), nullable=True)
    model: Mapped[str | None] = mapped_column(String(96), nullable=True)
    dari_cadangan: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    ukuran_muatan_bita: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    hasil_pindai_pii: Mapped[str] = mapped_column(
        String(200), nullable=False, default="bersih", doc="Ringkasan pemindaian, bukan isinya."
    )
    diblokir: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        doc="Benar bila permintaan dibatalkan karena terdeteksi pengenal pribadi.",
    )

    token_masukan: Mapped[int | None] = mapped_column(Integer, nullable=True)
    token_keluaran: Mapped[int | None] = mapped_column(Integer, nullable=True)
    durasi_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    berhasil: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    galat: Mapped[str | None] = mapped_column(String(300), nullable=True)

    pengguna: Mapped["Pengguna | None"] = relationship("Pengguna")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<CatatanPermintaanAI {self.keperluan} diblokir={self.diblokir}>"


class PengaturanSistem(Base, TimestampMixin):
    """Pengaturan yang dapat diubah pengguna tanpa menyentuh berkas konfigurasi.

    Dipakai untuk nilai yang memang wajar berubah sepanjang sistem berjalan -
    garis kemiskinan yang berlaku, gelombang aktif, ambang antrean verifikasi -
    dan yang perubahannya perlu tercatat siapa dan kapan.
    """

    __tablename__ = "pengaturan_sistem"
    __table_args__ = (UniqueConstraint("kunci", name="uq_pengaturan_kunci"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    kunci: Mapped[str] = mapped_column(String(64), nullable=False)
    nilai: Mapped[dict | list | str | float | None] = mapped_column(JSONFleksibel, nullable=True)
    keterangan: Mapped[str | None] = mapped_column(Text, nullable=True)
    diubah_oleh_id: Mapped[int | None] = mapped_column(
        ForeignKey("pengguna.id", ondelete="SET NULL"), nullable=True
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<PengaturanSistem {self.kunci}>"


__all__ = ["CatatanPermintaanAI", "JejakAudit", "PengaturanSistem", "Pengguna"]
