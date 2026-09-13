"""Hierarki wilayah administratif.

Struktur mengikuti pembagian nyata Kabupaten Pringsewu: kabupaten membawahi
kecamatan, kecamatan membawahi pekon dan kelurahan. Kode wilayah memakai
format Kementerian Dalam Negeri menurut Kepmendagri Nomor 300.2.2-2138/2025,
ditulis bertitik: 18.10 untuk kabupaten, 18.10.01 untuk kecamatan, dan
18.10.01.1001 untuk pekon.

Perlu dicatat bahwa kode Kemendagri dan kode Badan Pusat Statistik adalah dua
rezim penomoran yang terpisah. Memadankan keduanya MENUNTUT tabel jembatan -
BPS menyediakannya melalui sig.bps.go.id - dan tabel itu belum ada pada sistem
ini. Selama seluruh analitik berjalan di dalam NADI hal tersebut tidak menjadi
persoalan; ia menjadi persoalan pada hari data dipadankan dengan publikasi BPS.

Yang sudah terbukti: kode pekon pada berkas benih cocok seluruhnya dengan layer
batas desa Badan Informasi Geospasial skala 1:10.000 yang dipakai halaman peta.

Kolom :attr:`Wilayah.jalur` menyimpan silsilah lengkap sebagai untai terpisah
garis miring. Kolom ini menduplikasi apa yang sudah tersirat pada
:attr:`Wilayah.induk_id`, dan duplikasi itu disengaja: menanyakan "seluruh
keluarga di Kecamatan Pagelaran" menjadi satu pencocokan awalan, bukan
penelusuran rekursif bertingkat. Pada SQLite yang tidak memiliki ``WITH
RECURSIVE`` yang murah, perbedaannya terasa nyata di layar peta.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from nadi.db.base import Base, TimestampMixin
from nadi.db.enums import JenisWilayah
from nadi.db.types import TeksEnum

if TYPE_CHECKING:
    from nadi.db.models.keluarga import Keluarga


class Wilayah(Base, TimestampMixin):
    """Satu satuan wilayah administratif."""

    __tablename__ = "wilayah"
    __table_args__ = (
        UniqueConstraint("kode", name="uq_wilayah_kode"),
        Index("ix_wilayah_jalur", "jalur"),
        Index("ix_wilayah_jenis_induk", "jenis", "induk_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    kode: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        doc="Kode wilayah versi BPS, misalnya 1810 untuk Kabupaten Pringsewu.",
    )
    nama: Mapped[str] = mapped_column(String(120), nullable=False)
    jenis: Mapped[JenisWilayah] = mapped_column(TeksEnum(JenisWilayah, 16), nullable=False)

    induk_id: Mapped[int | None] = mapped_column(
        ForeignKey("wilayah.id", ondelete="RESTRICT"), nullable=True
    )
    jalur: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        default="",
        doc="Silsilah kode dari kabupaten ke bawah, dipisah garis miring.",
    )
    tingkat: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, doc="0 kabupaten, 1 kecamatan, 2 pekon/kelurahan."
    )

    # --- Geografi ---
    lintang: Mapped[float | None] = mapped_column(Float, nullable=True)
    bujur: Mapped[float | None] = mapped_column(Float, nullable=True)
    luas_km2: Mapped[float | None] = mapped_column(Float, nullable=True)

    # --- Kependudukan (angka acuan, bukan hasil hitung sistem) ---
    jumlah_penduduk: Mapped[int | None] = mapped_column(Integer, nullable=True)
    jumlah_keluarga: Mapped[int | None] = mapped_column(Integer, nullable=True)
    klasifikasi: Mapped[str | None] = mapped_column(
        String(16), nullable=True, doc="perkotaan atau perdesaan"
    )

    # --- Relasi ---
    induk: Mapped["Wilayah | None"] = relationship(
        "Wilayah", remote_side=[id], back_populates="anak"
    )
    anak: Mapped[list["Wilayah"]] = relationship(
        "Wilayah", back_populates="induk", cascade="save-update"
    )
    keluarga: Mapped[list["Keluarga"]] = relationship("Keluarga", back_populates="wilayah")

    # ------------------------------------------------------------------
    def susun_jalur(self) -> str:
        """Bentuk nilai :attr:`jalur` dari silsilah induk."""
        rantai: list[str] = []
        simpul: Wilayah | None = self
        while simpul is not None:
            rantai.append(simpul.kode)
            simpul = simpul.induk
        return "/".join(reversed(rantai))

    @property
    def nama_lengkap(self) -> str:
        """Nama beserta jenisnya, misalnya "Pekon Podomoro"."""
        awalan = {
            JenisWilayah.KABUPATEN: "Kabupaten",
            JenisWilayah.KECAMATAN: "Kecamatan",
            JenisWilayah.PEKON: "Pekon",
            JenisWilayah.KELURAHAN: "Kelurahan",
        }.get(self.jenis, "")
        return f"{awalan} {self.nama}".strip()

    @property
    def perdesaan(self) -> bool:
        return (self.klasifikasi or "perdesaan") == "perdesaan"

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Wilayah {self.kode} {self.nama_lengkap}>"


class StatistikWilayah(Base, TimestampMixin):
    """Rekap terhitung per wilayah per gelombang waktu.

    Tabel ini adalah hasil turunan, bukan sumber kebenaran: seluruh isinya
    dapat dibentuk ulang dari tabel keluarga dan skor. Keberadaannya semata
    demi kecepatan - peta kabupaten dengan seratus tiga puluh satu wilayah
    harus tampil seketika, bukan menunggu agregasi ratusan ribu baris pada
    setiap penggeseran peta.

    Kolom :attr:`jumlah_keluarga` juga berperan sebagai penjaga privasi:
    antarmuka menahan tampilan sel yang jumlahnya di bawah ambang, sebab
    agregat atas segelintir keluarga sama saja dengan menunjuk keluarga itu.
    """

    __tablename__ = "statistik_wilayah"
    __table_args__ = (
        UniqueConstraint("wilayah_id", "gelombang", name="uq_statistik_wilayah_periode"),
        Index("ix_statistik_wilayah_gelombang", "gelombang"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    wilayah_id: Mapped[int] = mapped_column(
        ForeignKey("wilayah.id", ondelete="CASCADE"), nullable=False, index=True
    )
    gelombang: Mapped[int] = mapped_column(Integer, nullable=False)

    jumlah_keluarga: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    jumlah_individu: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # --- Kemiskinan & kerentanan ---
    jumlah_miskin: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    persentase_miskin: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    jumlah_rentan: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, doc="Belum miskin namun di bawah garis kerentanan."
    )
    skor_rata_rata: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    skor_median: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    jumlah_risiko_tinggi: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    jumlah_risiko_sangat_tinggi: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # --- Cakupan layanan dasar ---
    persen_sanitasi_layak: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    persen_air_minum_layak: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    persen_hunian_layak: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    persen_penerima_bantuan: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # --- Beban kerja penanganan ---
    jumlah_kasus_terbuka: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    jumlah_intervensi_berjalan: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    wilayah: Mapped["Wilayah"] = relationship("Wilayah")

    @property
    def aman_ditampilkan(self) -> bool:
        """Apakah sel ini cukup besar untuk ditampilkan tanpa membuka identitas."""
        from nadi.security.rbac import AMBANG_SEL_KECIL

        return self.jumlah_keluarga >= AMBANG_SEL_KECIL

    def __repr__(self) -> str:  # pragma: no cover
        return f"<StatistikWilayah wilayah={self.wilayah_id} gelombang={self.gelombang}>"


__all__ = ["StatistikWilayah", "Wilayah"]
