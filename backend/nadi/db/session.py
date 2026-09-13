"""Mesin basis data, sesi, dan penyetelan khusus per mesin.

SQLite memerlukan beberapa penyesuaian yang mudah terlewat namun berakibat
serius:

* Penegakan kunci asing **mati secara bawaan**. Tanpa ``PRAGMA foreign_keys=ON``
  basis data akan menerima baris yatim tanpa keluhan, dan integritas relasi
  yang kita rancang dengan hati-hati menjadi sekadar dokumentasi.
* Mode jurnal bawaan mengunci seluruh berkas saat menulis. Dengan ``WAL``,
  pembacaan tetap berjalan selagi penulisan berlangsung - penting ketika
  antarmuka menampilkan peta sementara skrip penilaian sedang memperbarui skor.
* Koneksi terikat pada utas pembuatnya. FastAPI menjalankan permintaan pada
  kumpulan utas, sehingga ikatan tersebut harus dilonggarkan.
"""

from __future__ import annotations

import logging
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from sqlalchemy import Engine, create_engine, event, text
from sqlalchemy.orm import Session, sessionmaker

from nadi.config import settings
from nadi.db.base import Base

logger = logging.getLogger("nadi.db")


def _url_sqlite(url: str) -> bool:
    return url.startswith("sqlite")


def normalisasi_url_sqlite(url: str) -> str:
    """Ubah lintasan SQLite relatif menjadi mutlak, berpatokan pada akar proyek.

    SQLite menafsirkan lintasan relatif terhadap **direktori kerja saat itu**.
    Akibatnya, ``sqlite:///./data/nadi.db`` menunjuk berkas yang berbeda ketika
    aplikasi dijalankan dari akar proyek, dari dalam folder ``backend``, atau
    dari pintasan di layar. Bagi peluncur satu-klik yang dipakai saat demo,
    perbedaan itu berarti basis data kosong tepat di depan dewan juri.

    Fungsi ini menambatkan lintasan pada akar proyek sehingga berkas yang
    dituju selalu sama, dari mana pun aplikasi dinyalakan.
    """
    if not _url_sqlite(url) or ":memory:" in url:
        return url

    bagian = url.split("///", 1)
    if len(bagian) != 2 or not bagian[1]:
        return url

    skema, sisa = bagian
    jalur = Path(sisa)
    if not jalur.is_absolute():
        jalur = (settings.project_root / jalur).resolve()

    jalur.parent.mkdir(parents=True, exist_ok=True)
    return f"{skema}///{jalur.as_posix()}"


def buat_mesin(url: str | None = None) -> Engine:
    """Bangun mesin SQLAlchemy dengan penyetelan sesuai jenis basis data."""
    url = normalisasi_url_sqlite(url or settings.database_url)
    opsi: dict[str, Any] = {
        "echo": settings.db_echo,
        "future": True,
        "pool_pre_ping": True,
    }

    if _url_sqlite(url):
        # Longgarkan ikatan utas; keamanan tetap terjaga karena setiap
        # permintaan memakai sesinya sendiri dan tidak berbagi koneksi.
        opsi["connect_args"] = {"check_same_thread": False}
    else:
        # PostgreSQL: kumpulan koneksi berukuran wajar untuk satu kabupaten.
        opsi.update(pool_size=10, max_overflow=20, pool_recycle=1800)

    mesin = create_engine(url, **opsi)

    if _url_sqlite(url):
        _pasang_pragma_sqlite(mesin)

    return mesin


def _pasang_pragma_sqlite(mesin: Engine) -> None:
    """Terapkan penyetelan SQLite pada setiap koneksi baru."""

    @event.listens_for(mesin, "connect")
    def _atur_pragma(dbapi_connection, connection_record):  # noqa: ANN001, ARG001
        kursor = dbapi_connection.cursor()
        try:
            # Tanpa baris ini, kunci asing tidak ditegakkan sama sekali.
            kursor.execute("PRAGMA foreign_keys=ON")
            # Pembacaan tidak terhalang penulisan.
            kursor.execute("PRAGMA journal_mode=WAL")
            # Keseimbangan wajar antara ketahanan dan kecepatan tulis massal.
            kursor.execute("PRAGMA synchronous=NORMAL")
            # Ruang sementara di memori mempercepat ORDER BY pada tabel besar.
            kursor.execute("PRAGMA temp_store=MEMORY")
            # Cache 64 MB; dataset satu kabupaten muat hampir seluruhnya.
            kursor.execute("PRAGMA cache_size=-64000")
        finally:
            kursor.close()


# Mesin dan pabrik sesi tunggal untuk seluruh proses.
mesin = buat_mesin()
SesiLokal = sessionmaker(bind=mesin, autocommit=False, autoflush=False, expire_on_commit=False)


def dapatkan_sesi() -> Iterator[Session]:
    """Dependensi FastAPI: satu sesi per permintaan, selalu ditutup."""
    sesi = SesiLokal()
    try:
        yield sesi
    finally:
        sesi.close()


@contextmanager
def sesi_transaksi() -> Iterator[Session]:
    """Sesi untuk skrip: melakukan commit bila berhasil, rollback bila gagal."""
    sesi = SesiLokal()
    try:
        yield sesi
        sesi.commit()
    except Exception:
        sesi.rollback()
        raise
    finally:
        sesi.close()


def buat_seluruh_tabel() -> None:
    """Bentuk seluruh tabel yang belum ada.

    Dipakai untuk penyiapan cepat di laptop. Untuk peladen produksi, gunakan
    migrasi Alembic agar perubahan skema dapat ditelusuri dan dibalik.
    """
    # Impor di dalam fungsi agar seluruh model terdaftar pada metadata
    # sebelum tabel dibentuk, tanpa menimbulkan impor melingkar.
    from nadi.db import models  # noqa: F401

    Base.metadata.create_all(bind=mesin)
    logger.info("Skema basis data siap: %d tabel.", len(Base.metadata.tables))


def periksa_koneksi() -> dict[str, Any]:
    """Uji koneksi basis data untuk titik akhir kesehatan."""
    try:
        with mesin.connect() as koneksi:
            koneksi.execute(text("SELECT 1"))
        return {
            "tersedia": True,
            "jenis": mesin.dialect.name,
            "jumlah_tabel": len(Base.metadata.tables),
        }
    except Exception as exc:  # noqa: BLE001 - dilaporkan apa adanya ke pemantauan
        return {"tersedia": False, "jenis": mesin.dialect.name, "alasan": str(exc)}


__all__ = [
    "SesiLokal",
    "buat_mesin",
    "buat_seluruh_tabel",
    "dapatkan_sesi",
    "mesin",
    "periksa_koneksi",
    "sesi_transaksi",
]
