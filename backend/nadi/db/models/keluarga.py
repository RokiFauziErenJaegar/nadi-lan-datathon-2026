"""Keluarga, anggotanya, kondisinya dari waktu ke waktu, dan guncangan.

Inilah Household Digital Twin yang dijanjikan proposal. Rancangannya berpijak
pada satu pemisahan yang menentukan segalanya:

* :class:`Keluarga` menyimpan hal yang **tidak berubah** - pengenal dan lokasi.
* :class:`SnapshotKeluarga` menyimpan **kondisi pada satu titik waktu**.

Tanpa pemisahan ini, "twin" hanyalah baris basis data yang ditimpa setiap kali
data dimutakhirkan, dan seluruh janji tentang deteksi dini menjadi mustahil:
sistem tidak dapat mengenali keluarga yang *memburuk* bila ia tidak menyimpan
keadaan sebelumnya. Riwayat bukan fitur tambahan di sini - ia adalah syarat.

Satu gelombang mewakili satu putaran pemutakhiran data, yang pada praktik
DTSEN berlangsung berkala. Model memakai kondisi pada gelombang ``t`` untuk
memperkirakan keadaan pada gelombang ``t+1``.
"""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Date,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from nadi.db.base import Base, TimestampMixin
from nadi.db.enums import (
    BahanBakarMemasak,
    DayaListrik,
    FasilitasBAB,
    HubunganKK,
    JenisAtap,
    JenisDinding,
    JenisDisabilitas,
    JenisGuncangan,
    JenisKelamin,
    JenisKloset,
    JenisLantai,
    LapanganUsaha,
    PartisipasiSekolah,
    PembuanganTinja,
    PendidikanTertinggi,
    PenyakitKronis,
    StatusGiziBalita,
    StatusKegiatan,
    StatusKepemilikanRumah,
    StatusPekerjaan,
    StatusPerkawinan,
    SumberAirMinum,
    SumberPenerangan,
    TingkatKeparahan,
)
from nadi.db.types import JSONFleksibel, KodeEnum

if TYPE_CHECKING:
    from nadi.db.models.wilayah import Wilayah


class Keluarga(Base, TimestampMixin):
    """Pengenal tetap sebuah keluarga.

    Tabel ini sengaja dibuat ramping. Tidak ada nama, tidak ada NIK, tidak ada
    alamat jalan - bukan karena data itu tidak ada di dunia nyata, melainkan
    karena tak satu pun fungsi NADI memerlukannya. Sistem ini memprioritaskan
    dan menjelaskan; yang mendatangi rumah adalah petugas, memakai sistem
    kependudukan yang memang berwenang menyimpan identitas.
    """

    __tablename__ = "keluarga"
    __table_args__ = (
        UniqueConstraint("kode_semu", name="uq_keluarga_kode_semu"),
        Index("ix_keluarga_wilayah_aktif", "wilayah_id", "aktif"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    kode_semu: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        doc="Kode tampil yang tidak dapat dibalik menjadi identitas, misalnya KLG-7F3A-2B9K.",
    )
    wilayah_id: Mapped[int] = mapped_column(
        ForeignKey("wilayah.id", ondelete="RESTRICT"), nullable=False, index=True
    )

    # Koordinat digeser acak dalam radius kecil sebelum disimpan. Cukup untuk
    # analisis sebaran dan pengelompokan wilayah, tidak cukup untuk menunjuk
    # satu rumah. Lihat nadi.synth.geo untuk besaran pergeserannya.
    lintang: Mapped[float | None] = mapped_column(Float, nullable=True)
    bujur: Mapped[float | None] = mapped_column(Float, nullable=True)

    tanggal_terdaftar: Mapped[date | None] = mapped_column(Date, nullable=True)
    sumber_data: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="dtsen",
        doc="Asal pencatatan: dtsen, usulan_daerah, usulan_mandiri, atau sintetis.",
    )
    aktif: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # --- Relasi ---
    wilayah: Mapped["Wilayah"] = relationship("Wilayah", back_populates="keluarga")
    anggota: Mapped[list["AnggotaKeluarga"]] = relationship(
        "AnggotaKeluarga",
        back_populates="keluarga",
        cascade="all, delete-orphan",
        order_by="AnggotaKeluarga.urutan",
    )
    snapshot: Mapped[list["SnapshotKeluarga"]] = relationship(
        "SnapshotKeluarga",
        back_populates="keluarga",
        cascade="all, delete-orphan",
        order_by="SnapshotKeluarga.gelombang",
    )
    guncangan: Mapped[list["Guncangan"]] = relationship(
        "Guncangan",
        back_populates="keluarga",
        cascade="all, delete-orphan",
        order_by="Guncangan.gelombang",
    )

    def kondisi_pada(self, gelombang: int) -> "SnapshotKeluarga | None":
        """Kondisi keluarga pada satu gelombang tertentu."""
        for s in self.snapshot:
            if s.gelombang == gelombang:
                return s
        return None

    @property
    def kondisi_terkini(self) -> "SnapshotKeluarga | None":
        return self.snapshot[-1] if self.snapshot else None

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Keluarga {self.kode_semu}>"


class AnggotaKeluarga(Base, TimestampMixin):
    """Satu anggota keluarga, beserta rentang waktu keanggotaannya.

    Kolom :attr:`gelombang_masuk` dan :attr:`gelombang_keluar` membuat kelahiran,
    kematian, dan perpindahan dapat direkam tanpa menghapus baris. Menghapus
    anggota yang meninggal akan menghilangkan penjelasan mengapa kerentanan
    keluarga melonjak pada gelombang itu - padahal justru penjelasan itulah
    yang dicari pengguna.
    """

    __tablename__ = "anggota_keluarga"
    __table_args__ = (
        UniqueConstraint("keluarga_id", "urutan", name="uq_anggota_keluarga_urutan"),
        Index("ix_anggota_rentang", "keluarga_id", "gelombang_masuk", "gelombang_keluar"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    keluarga_id: Mapped[int] = mapped_column(
        ForeignKey("keluarga.id", ondelete="CASCADE"), nullable=False, index=True
    )
    urutan: Mapped[int] = mapped_column(Integer, nullable=False)
    kode_semu: Mapped[str] = mapped_column(String(20), nullable=False)

    # --- Demografi ---
    hubungan_kk: Mapped[HubunganKK] = mapped_column(KodeEnum(HubunganKK), nullable=False)
    jenis_kelamin: Mapped[JenisKelamin] = mapped_column(KodeEnum(JenisKelamin), nullable=False)
    tahun_lahir: Mapped[int] = mapped_column(
        Integer, nullable=False, doc="Hanya tahun; tanggal lahir lengkap tidak diperlukan."
    )
    status_perkawinan: Mapped[StatusPerkawinan] = mapped_column(
        KodeEnum(StatusPerkawinan), nullable=False, default=StatusPerkawinan.BELUM_KAWIN
    )

    # --- Pendidikan ---
    partisipasi_sekolah: Mapped[PartisipasiSekolah] = mapped_column(
        KodeEnum(PartisipasiSekolah), nullable=False, default=PartisipasiSekolah.TIDAK_PERNAH
    )
    pendidikan_tertinggi: Mapped[PendidikanTertinggi] = mapped_column(
        KodeEnum(PendidikanTertinggi), nullable=False, default=PendidikanTertinggi.TIDAK_SEKOLAH
    )

    # --- Ketenagakerjaan ---
    status_kegiatan: Mapped[StatusKegiatan] = mapped_column(
        KodeEnum(StatusKegiatan), nullable=False, default=StatusKegiatan.LAINNYA
    )
    lapangan_usaha: Mapped[LapanganUsaha] = mapped_column(
        KodeEnum(LapanganUsaha), nullable=False, default=LapanganUsaha.TIDAK_BEKERJA
    )
    status_pekerjaan: Mapped[StatusPekerjaan] = mapped_column(
        KodeEnum(StatusPekerjaan), nullable=False, default=StatusPekerjaan.TIDAK_BEKERJA
    )
    jumlah_usaha: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Jumlah usaha yang dimiliki. Variabel DTSEN 'kepemilikan_usaha'. "
        "Penting bagi pencocokan program pemberdayaan ekonomi seperti KUR dan PENA.",
    )

    # --- Kesehatan ---
    jenis_disabilitas: Mapped[JenisDisabilitas] = mapped_column(
        KodeEnum(JenisDisabilitas), nullable=False, default=JenisDisabilitas.TIDAK_ADA
    )
    penyakit_kronis: Mapped[PenyakitKronis] = mapped_column(
        KodeEnum(PenyakitKronis), nullable=False, default=PenyakitKronis.TIDAK_ADA
    )
    status_gizi_balita: Mapped[StatusGiziBalita] = mapped_column(
        KodeEnum(StatusGiziBalita), nullable=False, default=StatusGiziBalita.TIDAK_BERLAKU
    )
    sedang_hamil: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    punya_jaminan_kesehatan: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # --- Rentang keanggotaan ---
    gelombang_masuk: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    gelombang_keluar: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sebab_keluar: Mapped[str | None] = mapped_column(
        String(32), nullable=True, doc="meninggal, pindah, menikah_keluar, atau lainnya."
    )

    keluarga: Mapped["Keluarga"] = relationship("Keluarga", back_populates="anggota")

    def umur_pada(self, tahun: int) -> int:
        return max(0, tahun - self.tahun_lahir)

    def aktif_pada(self, gelombang: int) -> bool:
        if gelombang < self.gelombang_masuk:
            return False
        return self.gelombang_keluar is None or gelombang < self.gelombang_keluar

    def __repr__(self) -> str:  # pragma: no cover
        return f"<AnggotaKeluarga {self.kode_semu} hub={self.hubungan_kk.name}>"


class SnapshotKeluarga(Base, TimestampMixin):
    """Kondisi lengkap satu keluarga pada satu gelombang.

    Seluruh keadaan disatukan pada satu baris lebar dan sengaja tidak
    dinormalisasi lebih jauh. Alasannya praktis: satu baris di sini adalah satu
    contoh latih bagi model. Menyebarnya ke banyak tabel akan memaksa setiap
    pelatihan melakukan penggabungan berlipat, dan setiap penggabungan adalah
    kesempatan bagi kebocoran data masa depan menyelinap masuk.
    """

    __tablename__ = "snapshot_keluarga"
    __table_args__ = (
        UniqueConstraint("keluarga_id", "gelombang", name="uq_snapshot_keluarga_gelombang"),
        Index("ix_snapshot_gelombang_miskin", "gelombang", "status_miskin"),
        Index("ix_snapshot_gelombang_desil", "gelombang", "desil_kesejahteraan"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    keluarga_id: Mapped[int] = mapped_column(
        ForeignKey("keluarga.id", ondelete="CASCADE"), nullable=False, index=True
    )
    gelombang: Mapped[int] = mapped_column(Integer, nullable=False)
    tanggal_kondisi: Mapped[date] = mapped_column(Date, nullable=False)

    # ------------------------------------------------------------------
    # Ekonomi
    # ------------------------------------------------------------------
    pengeluaran_per_kapita: Mapped[float] = mapped_column(
        Float, nullable=False, doc="Rupiah per kapita per bulan - ukuran resmi kemiskinan."
    )
    pendapatan_bulanan: Mapped[float | None] = mapped_column(
        Float, nullable=True, doc="Perkiraan pendapatan keluarga per bulan."
    )
    desil_kesejahteraan: Mapped[int] = mapped_column(
        Integer, nullable=False, doc="Desil 1 sampai 10; desil 1 adalah yang paling miskin."
    )
    peringkat_kesejahteraan: Mapped[float | None] = mapped_column(
        Float, nullable=True, doc="Peringkat relatif 0 sampai 1 dalam kabupaten."
    )
    status_miskin: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        doc="Pengeluaran per kapita di bawah garis kemiskinan yang berlaku.",
    )
    rasio_garis_kemiskinan: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=1.0,
        doc="Pengeluaran per kapita dibagi garis kemiskinan. Di bawah 1 berarti miskin.",
    )

    # ------------------------------------------------------------------
    # Susunan keluarga
    # ------------------------------------------------------------------
    jumlah_anggota: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    jumlah_balita: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    jumlah_anak_usia_sekolah: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    jumlah_lansia: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    jumlah_disabilitas: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    jumlah_bekerja: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    rasio_tanggungan: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        doc="Anggota yang tidak bekerja dibagi anggota yang bekerja.",
    )

    # ------------------------------------------------------------------
    # Kepala keluarga
    # ------------------------------------------------------------------
    kk_umur: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    kk_jenis_kelamin: Mapped[JenisKelamin] = mapped_column(
        KodeEnum(JenisKelamin), nullable=False, default=JenisKelamin.LAKI_LAKI
    )
    kk_pendidikan: Mapped[PendidikanTertinggi] = mapped_column(
        KodeEnum(PendidikanTertinggi), nullable=False, default=PendidikanTertinggi.SD
    )
    kk_status_kegiatan: Mapped[StatusKegiatan] = mapped_column(
        KodeEnum(StatusKegiatan), nullable=False, default=StatusKegiatan.BEKERJA
    )
    kk_lapangan_usaha: Mapped[LapanganUsaha] = mapped_column(
        KodeEnum(LapanganUsaha), nullable=False, default=LapanganUsaha.TIDAK_BEKERJA
    )
    kk_status_pekerjaan: Mapped[StatusPekerjaan] = mapped_column(
        KodeEnum(StatusPekerjaan), nullable=False, default=StatusPekerjaan.TIDAK_BEKERJA
    )

    # ------------------------------------------------------------------
    # Hunian
    # ------------------------------------------------------------------
    # Nama kolom di bawah mengikuti penamaan resmi variabel keluarga DTSEN
    # (jenis_lantai_terluas, sumber_air_minum_utama, dan seterusnya). Menyalin
    # penamaan resmi membuat pemuatan data DTSEN yang sebenarnya kelak menjadi
    # pemetaan satu-lawan-satu, bukan penulisan ulang adaptor.
    status_kepemilikan_rumah: Mapped[StatusKepemilikanRumah] = mapped_column(
        KodeEnum(StatusKepemilikanRumah), nullable=False, default=StatusKepemilikanRumah.MILIK_SENDIRI
    )
    keluarga_dalam_rumah: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        doc="Jumlah keluarga yang tinggal dalam satu rumah. Lebih dari satu "
        "menandakan kepadatan hunian yang tidak terlihat dari luas lantai saja.",
    )
    luas_lantai_m2: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=36.0,
        doc="Variabel pengayaan dari Regsosek/Susenas, bukan variabel wajib DTSEN, "
        "namun diperlukan karena kecukupan luas 7,2 m2 per kapita adalah salah "
        "satu kriteria resmi rumah layak huni.",
    )
    jenis_lantai_terluas: Mapped[JenisLantai] = mapped_column(
        KodeEnum(JenisLantai), nullable=False, default=JenisLantai.SEMEN_BATA_MERAH
    )
    jenis_dinding_terluas: Mapped[JenisDinding] = mapped_column(
        KodeEnum(JenisDinding), nullable=False, default=JenisDinding.TEMBOK
    )
    jenis_atap_terluas: Mapped[JenisAtap] = mapped_column(
        KodeEnum(JenisAtap), nullable=False, default=JenisAtap.GENTENG
    )

    # ------------------------------------------------------------------
    # Air dan sanitasi
    # ------------------------------------------------------------------
    sumber_air_minum_utama: Mapped[SumberAirMinum] = mapped_column(
        KodeEnum(SumberAirMinum), nullable=False, default=SumberAirMinum.SUMUR_TERLINDUNG
    )
    fasilitas_bab: Mapped[FasilitasBAB] = mapped_column(
        KodeEnum(FasilitasBAB), nullable=False, default=FasilitasBAB.SENDIRI
    )
    jenis_kloset: Mapped[JenisKloset] = mapped_column(
        KodeEnum(JenisKloset), nullable=False, default=JenisKloset.LEHER_ANGSA
    )
    pembuangan_akhir_tinja: Mapped[PembuanganTinja] = mapped_column(
        KodeEnum(PembuanganTinja), nullable=False, default=PembuanganTinja.TANGKI_SEPTIK
    )

    # ------------------------------------------------------------------
    # Energi
    # ------------------------------------------------------------------
    sumber_penerangan_utama: Mapped[SumberPenerangan] = mapped_column(
        KodeEnum(SumberPenerangan), nullable=False, default=SumberPenerangan.LISTRIK_PLN_METERAN
    )
    daya_terpasang: Mapped[DayaListrik] = mapped_column(
        KodeEnum(DayaListrik), nullable=False, default=DayaListrik.VA_900
    )
    bahan_bakar_utama_memasak: Mapped[BahanBakarMemasak] = mapped_column(
        KodeEnum(BahanBakarMemasak), nullable=False, default=BahanBakarMemasak.GAS_3KG
    )

    # ------------------------------------------------------------------
    # Aset - mengikuti grup "Kepemilikan" pada variabel keluarga DTSEN
    # ------------------------------------------------------------------
    # Perhatikan bentuk datanya. Susenas, PPLS, dan DTKS lama mencatat aset
    # sebagai ya/tidak. DTSEN mengubahnya menjadi **jumlah unit**, bahkan
    # kuantitas kontinu untuk emas (gram) dan lahan (hektar).
    #
    # Perbedaan ini tampak sepele namun berkonsekuensi besar. Keluarga dengan
    # satu sepeda motor tua dan keluarga dengan tiga sepeda motor sama-sama
    # bernilai "ya" pada skema lama - padahal keduanya berada di dunia ekonomi
    # yang berbeda. Menyimpan jumlah mempertahankan informasi itu, sekaligus
    # memastikan data DTSEN yang sebenarnya dapat dimuat kelak tanpa kehilangan
    # apa pun dan tanpa mengubah skema.
    jumlah_tabung_gas: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, doc="Tabung gas berukuran minimal 5,5 kg."
    )
    jumlah_lemari_es: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    jumlah_ac: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    jumlah_pemanas_air: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    jumlah_telepon_rumah: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    jumlah_tv_datar: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, doc="Televisi datar berukuran minimal 30 inci."
    )
    jumlah_komputer: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, doc="Komputer, laptop, atau tablet."
    )
    jumlah_smartphone: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, doc="Variabel baru pada DTSEN, tidak ada pada DTKS."
    )
    jumlah_sepeda: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    jumlah_sepeda_motor: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    jumlah_mobil: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    jumlah_perahu: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    jumlah_kapal_perahu_motor: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    gram_emas_perhiasan: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.0, doc="Berat perhiasan emas dalam gram."
    )
    luas_sawah_kebun_ha: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.0, doc="Luas lahan sawah atau kebun yang diusahakan, hektar."
    )
    punya_lahan_lainnya: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, doc="Lahan selain yang dihuni."
    )
    jumlah_rumah_lainnya: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, doc="Rumah selain yang dihuni."
    )
    jumlah_ternak_besar: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, doc="Sapi, kerbau, atau kuda."
    )
    jumlah_ternak_kecil: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, doc="Kambing, domba, atau babi."
    )

    # ------------------------------------------------------------------
    # Kesehatan dan pendidikan tingkat keluarga
    # ------------------------------------------------------------------
    ada_penyakit_kronis: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    ada_penyakit_biaya_tinggi: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    ada_gizi_bermasalah: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    jumlah_ber_jkn: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    jumlah_ibu_hamil: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Anggota yang sedang hamil atau dalam masa nifas. Menentukan "
        "kelayakan komponen ibu hamil pada PKH dan pemberian makanan tambahan.",
    )
    jumlah_tanpa_dokumen: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Anggota tanpa nomor induk kependudukan yang sah atau tanpa akta "
        "kelahiran. Merupakan penghambat paling mendasar: tanpa dokumen, "
        "keluarga tidak dapat ditetapkan sebagai penerima program apa pun.",
    )
    ada_anak_putus_sekolah: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    rata_lama_sekolah_dewasa: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    jumlah_usaha_keluarga: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Jumlah usaha seluruh anggota keluarga, dijumlahkan dari variabel "
        "DTSEN 'kepemilikan_usaha' pada tingkat individu.",
    )

    # ------------------------------------------------------------------
    # Perlindungan sosial yang sedang diterima
    # ------------------------------------------------------------------
    jumlah_program_diterima: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    nilai_bantuan_bulanan: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # ------------------------------------------------------------------
    # Kualitas data
    # ------------------------------------------------------------------
    kelengkapan_data: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=1.0,
        doc="Bagian bidang wajib yang terisi, bernilai 0 sampai 1.",
    )
    umur_data_bulan: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Berapa bulan sejak pemutakhiran terakhir. Data usang adalah risiko tersendiri.",
    )

    keluarga: Mapped["Keluarga"] = relationship("Keluarga", back_populates="snapshot")

    # ------------------------------------------------------------------
    # Sifat turunan
    # ------------------------------------------------------------------
    #: Luas lantai minimum per orang agar hunian dinilai cukup, dalam meter
    #: persegi. Angka ini adalah kriteria resmi rumah layak huni.
    LUAS_LANTAI_MINIMUM_PER_KAPITA: float = 7.2

    @property
    def sanitasi_layak(self) -> bool:
        """Sanitasi layak menuntut fasilitas, kloset, dan pembuangan sekaligus."""
        return (
            bool(self.fasilitas_bab.layak)
            and bool(self.jenis_kloset.layak)
            and bool(self.pembuangan_akhir_tinja.layak)
        )

    @property
    def air_minum_layak(self) -> bool:
        return bool(self.sumber_air_minum_utama.layak)

    @property
    def luas_lantai_per_kapita(self) -> float:
        return self.luas_lantai_m2 / self.jumlah_anggota if self.jumlah_anggota else 0.0

    @property
    def luas_cukup(self) -> bool:
        return self.luas_lantai_per_kapita >= self.LUAS_LANTAI_MINIMUM_PER_KAPITA

    @property
    def ketahanan_bangunan_layak(self) -> bool:
        """Atap, dinding, dan lantai harus ketiganya layak.

        Aturan resminya tegas: bila **salah satu** dari ketiga bahan berkategori
        tidak layak, ketahanan bangunan dinilai tidak layak. Tidak ada
        pembobotan, tidak ada dua dari tiga.
        """
        return (
            bool(self.jenis_lantai_terluas.layak)
            and bool(self.jenis_dinding_terluas.layak)
            and bool(self.jenis_atap_terluas.layak)
        )

    @property
    def hunian_layak(self) -> bool:
        """Rumah layak huni menurut definisi resmi - keempat kriteria wajib terpenuhi.

        Kriteria tersebut adalah kecukupan luas tempat tinggal, akses air minum
        layak, akses sanitasi layak, dan ketahanan bangunan.

        Perlu ditegaskan karena mudah keliru: rumah berdinding tembok dengan
        lantai keramik tetap dinilai **tidak** layak huni bila keluarganya buang
        air besar sembarangan. Menyederhanakan definisi ini menjadi sekadar
        kondisi fisik bangunan akan melaporkan angka rumah layak huni yang lebih
        tinggi daripada kenyataan - dan angka itulah yang dipakai menyusun
        anggaran perbaikan rumah tahun berikutnya.
        """
        return (
            self.luas_cukup
            and self.air_minum_layak
            and self.sanitasi_layak
            and self.ketahanan_bangunan_layak
        )

    @property
    def kriteria_hunian_tidak_terpenuhi(self) -> list[str]:
        """Kriteria rumah layak huni mana saja yang belum terpenuhi.

        Dipakai antarmuka dan mesin rekomendasi: mengetahui bahwa yang kurang
        adalah sanitasi, bukan atap, menentukan program mana yang tepat.
        """
        kurang: list[str] = []
        if not self.luas_cukup:
            kurang.append("kecukupan_luas")
        if not self.air_minum_layak:
            kurang.append("air_minum_layak")
        if not self.sanitasi_layak:
            kurang.append("sanitasi_layak")
        if not self.ketahanan_bangunan_layak:
            kurang.append("ketahanan_bangunan")
        return kurang

    @property
    def cakupan_jkn(self) -> float:
        return self.jumlah_ber_jkn / self.jumlah_anggota if self.jumlah_anggota else 0.0

    @property
    def rentan_tapi_belum_miskin(self) -> bool:
        """Berada di atas garis kemiskinan namun di bawah 1,5 kali garis tersebut.

        Kelompok inilah yang paling sering luput: belum tercatat miskin,
        sehingga tidak masuk daftar penerima, namun satu guncangan saja cukup
        untuk menjatuhkannya.
        """
        return 1.0 <= self.rasio_garis_kemiskinan < 1.5

    def __repr__(self) -> str:  # pragma: no cover
        return f"<SnapshotKeluarga keluarga={self.keluarga_id} gelombang={self.gelombang}>"


class Guncangan(Base, TimestampMixin):
    """Kejadian yang mengubah keadaan keluarga secara mendadak.

    Kemiskinan jarang datang perlahan. Ia datang lewat kejadian: pencari nafkah
    jatuh sakit, panen gagal, pabrik menutup lini produksi. Merekam kejadian
    ini secara terpisah membuat sistem dapat menjawab pertanyaan yang paling
    sering diajukan pengguna - *mengapa* keluarga ini tiba-tiba memburuk.
    """

    __tablename__ = "guncangan"
    __table_args__ = (
        Index("ix_guncangan_keluarga_gelombang", "keluarga_id", "gelombang"),
        Index("ix_guncangan_jenis_gelombang", "jenis", "gelombang"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    keluarga_id: Mapped[int] = mapped_column(
        ForeignKey("keluarga.id", ondelete="CASCADE"), nullable=False, index=True
    )
    gelombang: Mapped[int] = mapped_column(Integer, nullable=False)
    tanggal_kejadian: Mapped[date | None] = mapped_column(Date, nullable=True)

    jenis: Mapped[JenisGuncangan] = mapped_column(KodeEnum(JenisGuncangan), nullable=False)
    keparahan: Mapped[TingkatKeparahan] = mapped_column(
        KodeEnum(TingkatKeparahan), nullable=False, default=TingkatKeparahan.SEDANG
    )
    dampak_pendapatan_persen: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        doc="Perkiraan perubahan pendapatan akibat kejadian, dalam persen. Negatif berarti turun.",
    )
    keterangan: Mapped[str | None] = mapped_column(Text, nullable=True)
    rincian: Mapped[dict | None] = mapped_column(JSONFleksibel, nullable=True)

    keluarga: Mapped["Keluarga"] = relationship("Keluarga", back_populates="guncangan")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Guncangan {self.jenis.name} keluarga={self.keluarga_id} gelombang={self.gelombang}>"


__all__ = ["AnggotaKeluarga", "Guncangan", "Keluarga", "SnapshotKeluarga"]
