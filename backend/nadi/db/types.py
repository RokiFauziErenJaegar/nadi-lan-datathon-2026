"""Tipe kolom khusus.

Dua kebutuhan yang tampak bertentangan diselesaikan di sini.

Lapisan analitik membaca tabel langsung dengan pandas untuk melatih model.
Bagi keperluan itu, nilai kategorik paling baik tersimpan sebagai **angka
mentah** - siap dipakai tanpa penerjemahan, dan ukurannya kecil.

Lapisan aplikasi memerlukan **tipe yang kuat** supaya kekeliruan seperti
membandingkan kode lantai dengan kode dinding tertangkap saat penulisan kode,
bukan saat demo.

:class:`KodeEnum` dan :class:`TeksEnum` memenuhi keduanya: basis data menyimpan
angka atau untai polos, sementara Python menerima dan mengembalikan objek
enumerasi yang bertipe.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Generic, TypeVar

from sqlalchemy import Dialect, Integer, String
from sqlalchemy.dialects import postgresql
from sqlalchemy.types import JSON, TypeDecorator

E = TypeVar("E", bound=Enum)


class KodeEnum(TypeDecorator, Generic[E]):
    """Simpan :class:`enum.IntEnum` sebagai bilangan bulat.

    Nilai yang tidak dikenali dibiarkan lewat apa adanya, bukan diangkat
    sebagai galat. Data pemerintahan yang nyata selalu memuat kode di luar
    daftar resmi; menolak membaca seluruh baris karena satu kode asing akan
    membuat sistem tidak dapat dipakai justru pada data yang paling perlu
    diperiksa. Kode asing tersebut akan muncul sebagai anomali data, yang
    memang tempatnya.
    """

    impl = Integer
    cache_ok = True

    def __init__(self, kelas_enum: type[E], *args: Any, **kwargs: Any) -> None:
        self.kelas_enum = kelas_enum
        super().__init__(*args, **kwargs)

    def process_bind_param(self, value: E | int | None, dialect: Dialect) -> int | None:
        if value is None:
            return None
        if isinstance(value, Enum):
            return int(value.value)
        return int(value)

    def process_result_value(self, value: int | None, dialect: Dialect) -> E | int | None:
        if value is None:
            return None
        try:
            return self.kelas_enum(value)
        except ValueError:
            return value


class TeksEnum(TypeDecorator, Generic[E]):
    """Simpan enumerasi berbasis untai sebagai VARCHAR.

    Untai dipilih ketimbang tipe ENUM asli basis data karena menambah anggota
    baru pada ENUM PostgreSQL memerlukan migrasi skema, sedangkan menambah
    jenis anomali atau status kasus baru adalah perubahan yang wajar terjadi
    berulang kali selama sistem dipakai.
    """

    impl = String
    cache_ok = True

    def __init__(self, kelas_enum: type[E], panjang: int = 48, *args: Any, **kwargs: Any) -> None:
        self.kelas_enum = kelas_enum
        super().__init__(panjang, *args, **kwargs)

    def process_bind_param(self, value: E | str | None, dialect: Dialect) -> str | None:
        if value is None:
            return None
        if isinstance(value, Enum):
            return str(value.value)
        return str(value)

    def process_result_value(self, value: str | None, dialect: Dialect) -> E | str | None:
        if value is None:
            return None
        try:
            return self.kelas_enum(value)
        except ValueError:
            return value


#: Kolom JSON yang berperilaku baik di kedua mesin basis data.
#: PostgreSQL memakai JSONB agar dapat diindeks dan dikueri isinya;
#: SQLite menyimpannya sebagai teks.
JSONFleksibel = JSON().with_variant(postgresql.JSONB, "postgresql")


__all__ = ["JSONFleksibel", "KodeEnum", "TeksEnum"]
