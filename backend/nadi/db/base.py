"""Fondasi lapisan basis data.

NADI harus berjalan di dua tempat tanpa perubahan kode: SQLite pada laptop
petugas (nol instalasi, mudah dibawa saat demo) dan PostgreSQL pada peladen
daerah. Modul ini menyiapkan kelas dasar dan konvensi yang membuat kedua
sasaran itu berperilaku sama.

Konvensi penamaan batasan (constraint) ditetapkan secara eksplisit. Tanpa itu,
SQLite memberi nama otomatis pada indeks dan kunci asing, sehingga migrasi
Alembic yang dibuat di satu mesin gagal diterapkan di mesin lain.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, MetaData, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Konvensi penamaan yang membuat nama batasan bersifat deterministik
# di seluruh mesin dan seluruh mesin basis data.
KONVENSI_PENAMAAN = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """Kelas dasar seluruh model NADI."""

    metadata = MetaData(naming_convention=KONVENSI_PENAMAAN)

    def __repr__(self) -> str:  # pragma: no cover - bantuan saat penelusuran
        pk = getattr(self, "id", None)
        return f"<{type(self).__name__} id={pk}>"


def sekarang_utc() -> datetime:
    """Waktu saat ini dalam UTC dengan zona waktu yang eksplisit.

    Seluruh cap waktu disimpan dalam UTC dan diubah ke Waktu Indonesia Barat
    hanya di lapisan penyajian. Jejak audit yang bercampur zona waktu adalah
    jejak audit yang tidak dapat dipertanggungjawabkan.
    """
    return datetime.now(timezone.utc)


class TimestampMixin:
    """Menambahkan kolom waktu pembuatan dan pemutakhiran.

    Nilai diisi di sisi basis data agar tetap benar walaupun baris disisipkan
    lewat jalur lain, misalnya skrip pemuatan data massal.
    """

    dibuat_pada: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="Waktu baris pertama kali dibuat (UTC).",
    )
    diperbarui_pada: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        doc="Waktu baris terakhir diubah (UTC).",
    )


__all__ = ["Base", "KONVENSI_PENAMAAN", "TimestampMixin", "sekarang_utc"]
