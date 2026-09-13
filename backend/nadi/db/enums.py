"""Kosakata data terkode.

**Nama kategori** mengikuti instrumen pendataan resmi - Susenas, Registrasi
Sosial Ekonomi, dan Data Terpadu Kesejahteraan Sosial. "Marmer/granit",
"Keramik", "Parket/vinil/karpet" adalah kategori sebagaimana tertulis pada
instrumen tersebut, bukan istilah yang dikarang.

**Nomor kodenya bukan.** Nomor pada setiap enumerasi di berkas ini ditetapkan
sendiri oleh NADI. Kode numerik resmi Susenas 2019 ke atas hanya tersedia pada
kuesioner VSEN24.K yang berbayar melalui SiLASTIK BPS, dan tidak diperoleh saat
riset - hal ini dicatat terus terang pada docs/research/01-skema-data-dtsen.md.

Perbedaan itu penting dan tidak boleh dikaburkan. Ketika pipeline kelak
diarahkan ke berkas DTSEN yang sebenarnya, **wajib ada tabel pemetaan** dari
kode NADI ke kode resmi. Tanpa tabel itu kegagalannya bersifat senyap: angka 2
yang berarti "Keramik" di sini akan diterima sebagai angka 2 yang berarti
sesuatu yang lain, tanpa satu pun galat muncul.

Menyusun tabel pemetaan tersebut adalah pekerjaan satu berkas, bukan penulisan
ulang - tetapi ia memang belum ada, dan tidak boleh diklaim sudah ada.

Setiap enumerasi membawa dua hal di luar kodenya:

* ``label`` - kalimat yang dipahami petugas, dipakai apa adanya di antarmuka.
* penilaian kelayakan (``layak``, ``skor_kualitas``, dan sejenisnya) - penilaian
  normatif yang mengubah kategori mentah menjadi sinyal kerentanan. Penilaian
  ini mengikuti definisi resmi: "rumah tangga dengan akses sanitasi layak",
  "hunian layak huni", dan seterusnya. Menempatkannya di sini, bukan tersebar
  di dalam kode model, membuat seluruh asumsi normatif dapat diperiksa dan
  diperdebatkan pada satu tempat.
"""

from __future__ import annotations

import sys
from enum import Enum, IntEnum

if sys.version_info >= (3, 11):  # pragma: no cover - bergantung versi penafsir
    from enum import StrEnum
else:  # pragma: no cover - jalur Python 3.10

    class StrEnum(str, Enum):
        """Padanan ``enum.StrEnum`` untuk Python 3.10.

        Tanpa kelas ini, seluruh modul gagal diimpor pada Python 3.10 karena
        ``enum.StrEnum`` baru diperkenalkan pada Python 3.11.
        """

        def __str__(self) -> str:
            return str(self.value)


class _BerLabel(IntEnum):
    """Dasar enumerasi terkode yang membawa label bahasa Indonesia."""

    @property
    def label(self) -> str:
        return _LABEL[type(self).__name__][self.value]

    @classmethod
    def pilihan(cls) -> list[dict[str, object]]:
        """Daftar pilihan untuk antarmuka dan dokumentasi kamus data."""
        return [{"kode": a.value, "label": a.label, "nama": a.name} for a in cls]


# ---------------------------------------------------------------------------
# Kondisi hunian
# ---------------------------------------------------------------------------
class JenisLantai(_BerLabel):
    MARMER_GRANIT = 1
    KERAMIK = 2
    PARKET_VINIL = 3
    UBIN_TEGEL_TERASO = 4
    KAYU_KUALITAS_TINGGI = 5
    SEMEN_BATA_MERAH = 6
    BAMBU = 7
    KAYU_KUALITAS_RENDAH = 8
    TANAH = 9
    LAINNYA = 10

    @property
    def layak(self) -> bool:
        """Lantai bukan tanah dan bukan bambu dihitung layak.

        Mengikuti indikator "rumah tangga dengan lantai bukan tanah" yang
        dipakai dalam penghitungan rumah tidak layak huni.
        """
        return self not in {JenisLantai.TANAH, JenisLantai.BAMBU, JenisLantai.KAYU_KUALITAS_RENDAH}


class JenisDinding(_BerLabel):
    TEMBOK = 1
    PLESTERAN_ANYAMAN = 2
    KAYU_PAPAN = 3
    ANYAMAN_BAMBU = 4
    BATANG_KAYU = 5
    BAMBU = 6
    LAINNYA = 7

    @property
    def layak(self) -> bool:
        return self in {JenisDinding.TEMBOK, JenisDinding.PLESTERAN_ANYAMAN, JenisDinding.KAYU_PAPAN}


class JenisAtap(_BerLabel):
    BETON = 1
    GENTENG = 2
    SIRAP = 3
    SENG = 4
    ASBES = 5
    IJUK_RUMBIA = 6
    LAINNYA = 7

    @property
    def layak(self) -> bool:
        """Ijuk/rumbia dan bahan lain digolongkan tidak layak.

        Asbes tetap dihitung layak dari sisi ketahanan bangunan walaupun
        bermasalah dari sisi kesehatan - pembedaan ini mengikuti indikator
        perumahan resmi, bukan penilaian kesehatan lingkungan.
        """
        return self not in {JenisAtap.IJUK_RUMBIA, JenisAtap.LAINNYA}


class StatusKepemilikanRumah(_BerLabel):
    MILIK_SENDIRI = 1
    KONTRAK_SEWA = 2
    BEBAS_SEWA = 3
    RUMAH_DINAS = 4
    LAINNYA = 5

    @property
    def rentan(self) -> bool:
        """Hunian tanpa kepastian jangka panjang menambah kerentanan."""
        return self in {StatusKepemilikanRumah.KONTRAK_SEWA, StatusKepemilikanRumah.LAINNYA}


class SumberAirMinum(_BerLabel):
    AIR_KEMASAN = 1
    AIR_ISI_ULANG = 2
    LEDING_METERAN = 3
    LEDING_ECERAN = 4
    SUMUR_BOR_POMPA = 5
    SUMUR_TERLINDUNG = 6
    SUMUR_TAK_TERLINDUNG = 7
    MATA_AIR_TERLINDUNG = 8
    MATA_AIR_TAK_TERLINDUNG = 9
    AIR_SUNGAI = 10
    AIR_HUJAN = 11
    LAINNYA = 12

    @property
    def layak(self) -> bool:
        """Definisi "air minum layak" versi BPS/SDGs.

        Sumber tak terlindung, air permukaan, dan air hujan tidak termasuk.
        """
        return self in {
            SumberAirMinum.AIR_KEMASAN,
            SumberAirMinum.AIR_ISI_ULANG,
            SumberAirMinum.LEDING_METERAN,
            SumberAirMinum.LEDING_ECERAN,
            SumberAirMinum.SUMUR_BOR_POMPA,
            SumberAirMinum.SUMUR_TERLINDUNG,
            SumberAirMinum.MATA_AIR_TERLINDUNG,
        }


class FasilitasBAB(_BerLabel):
    SENDIRI = 1
    BERSAMA = 2
    UMUM = 3
    TIDAK_ADA = 4

    @property
    def layak(self) -> bool:
        return self in {FasilitasBAB.SENDIRI, FasilitasBAB.BERSAMA}


class JenisKloset(_BerLabel):
    LEHER_ANGSA = 1
    PLENGSENGAN = 2
    CEMPLUNG_CUBLUK = 3
    TIDAK_PAKAI = 4

    @property
    def layak(self) -> bool:
        return self is JenisKloset.LEHER_ANGSA


class PembuanganTinja(_BerLabel):
    TANGKI_SEPTIK = 1
    IPAL = 2
    KOLAM_SAWAH_SUNGAI = 3
    LUBANG_TANAH = 4
    PANTAI_TANAH_LAPANG = 5
    LAINNYA = 6

    @property
    def layak(self) -> bool:
        return self in {PembuanganTinja.TANGKI_SEPTIK, PembuanganTinja.IPAL}


class SumberPenerangan(_BerLabel):
    LISTRIK_PLN_METERAN = 1
    LISTRIK_PLN_TANPA_METERAN = 2
    LISTRIK_NON_PLN = 3
    BUKAN_LISTRIK = 4

    @property
    def layak(self) -> bool:
        return self is not SumberPenerangan.BUKAN_LISTRIK


class DayaListrik(_BerLabel):
    TANPA_LISTRIK = 0
    VA_450 = 450
    VA_900 = 900
    VA_1300 = 1300
    VA_2200 = 2200
    VA_LEBIH_2200 = 3500

    @property
    def indikator_ekonomi_rendah(self) -> bool:
        """Daya 450 VA dan 900 VA bersubsidi adalah penanda ekonomi yang kuat.

        Indikator ini dipakai luas dalam penargetan bantuan di Indonesia
        justru karena mudah diverifikasi dan sulit dimanipulasi.
        """
        return self in {DayaListrik.TANPA_LISTRIK, DayaListrik.VA_450, DayaListrik.VA_900}


class BahanBakarMemasak(_BerLabel):
    LISTRIK = 1
    GAS_LEBIH_3KG = 2
    GAS_3KG = 3
    GAS_KOTA = 4
    BIOGAS = 5
    MINYAK_TANAH = 6
    BRIKET = 7
    ARANG = 8
    KAYU_BAKAR = 9
    TIDAK_MEMASAK = 10

    @property
    def layak(self) -> bool:
        return self in {
            BahanBakarMemasak.LISTRIK,
            BahanBakarMemasak.GAS_LEBIH_3KG,
            BahanBakarMemasak.GAS_3KG,
            BahanBakarMemasak.GAS_KOTA,
            BahanBakarMemasak.BIOGAS,
        }


# ---------------------------------------------------------------------------
# Individu
# ---------------------------------------------------------------------------
class HubunganKK(_BerLabel):
    KEPALA_KELUARGA = 1
    ISTRI_SUAMI = 2
    ANAK = 3
    MENANTU = 4
    CUCU = 5
    ORANG_TUA_MERTUA = 6
    FAMILI_LAIN = 7
    LAINNYA = 8


class JenisKelamin(_BerLabel):
    LAKI_LAKI = 1
    PEREMPUAN = 2


class StatusPerkawinan(_BerLabel):
    BELUM_KAWIN = 1
    KAWIN = 2
    CERAI_HIDUP = 3
    CERAI_MATI = 4


class PartisipasiSekolah(_BerLabel):
    TIDAK_PERNAH = 1
    MASIH_SEKOLAH = 2
    TIDAK_BERSEKOLAH_LAGI = 3


class PendidikanTertinggi(_BerLabel):
    TIDAK_SEKOLAH = 1
    TIDAK_TAMAT_SD = 2
    SD = 3
    SMP = 4
    SMA = 5
    DIPLOMA = 6
    SARJANA = 7
    PASCASARJANA = 8

    @property
    def tahun_sekolah(self) -> int:
        """Perkiraan lama sekolah dalam tahun.

        Diperlukan karena model memerlukan besaran berurutan, sementara kode
        aslinya hanyalah label kategori.
        """
        return {1: 0, 2: 3, 3: 6, 4: 9, 5: 12, 6: 15, 7: 16, 8: 18}[self.value]


class StatusKegiatan(_BerLabel):
    BEKERJA = 1
    MENCARI_PEKERJAAN = 2
    SEKOLAH = 3
    MENGURUS_RUMAH_TANGGA = 4
    LAINNYA = 5


class LapanganUsaha(_BerLabel):
    PADI_PALAWIJA = 1
    HORTIKULTURA = 2
    PERKEBUNAN = 3
    PERIKANAN = 4
    PETERNAKAN = 5
    KEHUTANAN = 6
    PERTAMBANGAN = 7
    INDUSTRI_PENGOLAHAN = 8
    LISTRIK_GAS_AIR = 9
    KONSTRUKSI = 10
    PERDAGANGAN = 11
    HOTEL_RUMAH_MAKAN = 12
    TRANSPORTASI = 13
    INFORMASI_KOMUNIKASI = 14
    KEUANGAN_ASURANSI = 15
    JASA_PENDIDIKAN = 16
    JASA_KESEHATAN = 17
    JASA_PEMERINTAHAN = 18
    JASA_LAINNYA = 19
    TIDAK_BEKERJA = 20

    @property
    def sektor_pertanian(self) -> bool:
        return self.value in {1, 2, 3, 4, 5, 6}

    @property
    def rentan_musiman(self) -> bool:
        """Sektor yang penghasilannya berayun mengikuti musim atau cuaca.

        Keluarga di sektor ini menghadapi risiko guncangan pendapatan yang
        berbeda sifatnya dari pekerja bergaji tetap - perbedaan yang penting
        bagi model kerentanan.
        """
        return self.value in {1, 2, 3, 4, 6, 10}


class StatusPekerjaan(_BerLabel):
    BERUSAHA_SENDIRI = 1
    BERUSAHA_DIBANTU_BURUH_TIDAK_TETAP = 2
    BERUSAHA_DIBANTU_BURUH_TETAP = 3
    BURUH_KARYAWAN_PEGAWAI = 4
    PEKERJA_BEBAS_PERTANIAN = 5
    PEKERJA_BEBAS_NON_PERTANIAN = 6
    PEKERJA_KELUARGA_TAK_DIBAYAR = 7
    TIDAK_BEKERJA = 8

    @property
    def pekerjaan_rentan(self) -> bool:
        """Definisi "pekerjaan rentan" versi Organisasi Buruh Internasional.

        Mencakup pekerja berusaha sendiri dan pekerja keluarga tak dibayar,
        ditambah pekerja bebas yang tidak memiliki kepastian penghasilan.
        """
        return self.value in {1, 2, 5, 6, 7}

    @property
    def berpenghasilan_tetap(self) -> bool:
        return self in {StatusPekerjaan.BURUH_KARYAWAN_PEGAWAI, StatusPekerjaan.BERUSAHA_DIBANTU_BURUH_TETAP}


class JenisDisabilitas(_BerLabel):
    TIDAK_ADA = 1
    TUNANETRA = 2
    TUNARUNGU = 3
    TUNAWICARA = 4
    TUNADAKSA = 5
    TUNAGRAHITA = 6
    TUNALARAS = 7
    DISABILITAS_GANDA = 8
    EKS_GANGGUAN_JIWA = 9

    @property
    def ada(self) -> bool:
        return self is not JenisDisabilitas.TIDAK_ADA

    @property
    def berat(self) -> bool:
        """Disabilitas berat menjadi syarat komponen tertentu pada PKH."""
        return self in {JenisDisabilitas.DISABILITAS_GANDA, JenisDisabilitas.TUNAGRAHITA}


class PenyakitKronis(_BerLabel):
    TIDAK_ADA = 1
    HIPERTENSI = 2
    DIABETES = 3
    JANTUNG = 4
    STROKE = 5
    TBC = 6
    KANKER = 7
    GAGAL_GINJAL = 8
    LAINNYA = 9

    @property
    def ada(self) -> bool:
        return self is not PenyakitKronis.TIDAK_ADA

    @property
    def biaya_tinggi(self) -> bool:
        """Penyakit dengan biaya berobat yang mampu menjatuhkan ekonomi keluarga.

        Pengeluaran kesehatan katastrofik adalah salah satu jalur tercepat
        sebuah keluarga jatuh miskin.
        """
        return self in {
            PenyakitKronis.JANTUNG,
            PenyakitKronis.STROKE,
            PenyakitKronis.KANKER,
            PenyakitKronis.GAGAL_GINJAL,
        }


class StatusGiziBalita(_BerLabel):
    TIDAK_BERLAKU = 0
    GIZI_BAIK = 1
    GIZI_KURANG = 2
    GIZI_BURUK = 3
    STUNTING = 4
    OBESITAS = 5

    @property
    def bermasalah(self) -> bool:
        return self in {
            StatusGiziBalita.GIZI_KURANG,
            StatusGiziBalita.GIZI_BURUK,
            StatusGiziBalita.STUNTING,
        }


# ---------------------------------------------------------------------------
# Guncangan
# ---------------------------------------------------------------------------
class JenisGuncangan(_BerLabel):
    SAKIT_BERAT = 1
    KEHILANGAN_PEKERJAAN = 2
    GAGAL_PANEN = 3
    KEMATIAN_PENCARI_NAFKAH = 4
    BENCANA_ALAM = 5
    KELAHIRAN_ANGGOTA_BARU = 6
    PERCERAIAN = 7
    KENAIKAN_HARGA_PANGAN = 8
    KERUSAKAN_RUMAH = 9
    ANAK_MASUK_JENJANG_BARU = 10

    @property
    def sifat(self) -> str:
        """Guncangan pendapatan menurunkan pemasukan; guncangan pengeluaran menaikkan beban."""
        if self.value in {1, 2, 3, 4, 5}:
            return "pendapatan"
        return "pengeluaran"


class TingkatKeparahan(_BerLabel):
    RINGAN = 1
    SEDANG = 2
    BERAT = 3


# ---------------------------------------------------------------------------
# Vokabuler proses
# ---------------------------------------------------------------------------
class KategoriRisiko(StrEnum):
    """Pengelompokan skor kerentanan untuk penyajian dan penetapan prioritas."""

    RENDAH = "rendah"
    SEDANG = "sedang"
    TINGGI = "tinggi"
    SANGAT_TINGGI = "sangat_tinggi"

    @property
    def label(self) -> str:
        return {
            KategoriRisiko.RENDAH: "Risiko Rendah",
            KategoriRisiko.SEDANG: "Risiko Sedang",
            KategoriRisiko.TINGGI: "Risiko Tinggi",
            KategoriRisiko.SANGAT_TINGGI: "Risiko Sangat Tinggi",
        }[self]

    @property
    def warna(self) -> str:
        """Warna aksen antarmuka, ditetapkan di satu tempat agar konsisten.

        Nilai berikut berasal dari palet status yang telah diuji keterbacaannya
        bagi pembaca dengan buta warna. Pilihan pertama - hijau, kuning tua,
        jingga, merah tua - gugur pada dua pemeriksaan: hijaunya terlalu pucat
        sehingga terbaca abu-abu, dan pasangan jingga dengan merah tua terlalu
        berdekatan bahkan bagi pembaca berpenglihatan normal.

        Perlu ditegaskan: kategori risiko adalah keadaan berjenjang, bukan
        identitas. Warnanya karena itu WAJIB selalu disertai ikon dan tulisan.
        Dua di antaranya - sedang dan tinggi - memang berkontras rendah pada
        latar terang, dan justru itulah sebabnya warna tidak pernah boleh
        menjadi satu-satunya penanda.
        """
        return {
            KategoriRisiko.RENDAH: "#0ca30c",
            KategoriRisiko.SEDANG: "#fab219",
            KategoriRisiko.TINGGI: "#ec835a",
            KategoriRisiko.SANGAT_TINGGI: "#d03b3b",
        }[self]

    @property
    def ikon(self) -> str:
        """Nama ikon Lucide yang menyertai warna.

        Wajib ditampilkan bersama warna dan tulisan - warna sendirian tidak
        pernah cukup menyampaikan tingkat risiko.
        """
        return {
            KategoriRisiko.RENDAH: "circle-check",
            KategoriRisiko.SEDANG: "circle-alert",
            KategoriRisiko.TINGGI: "triangle-alert",
            KategoriRisiko.SANGAT_TINGGI: "octagon-alert",
        }[self]

    @classmethod
    def dari_skor(cls, skor: float) -> "KategoriRisiko":
        """Petakan skor 0-100 ke kategori.

        Ambang ditetapkan pada 40, 60, dan 80. Nilainya bukan hasil teori,
        melainkan pilihan operasional yang dikalibrasi terhadap kapasitas
        verifikasi: lihat :mod:`nadi.ml.kalibrasi` untuk cara ambang ini
        disesuaikan dengan jumlah petugas yang tersedia.
        """
        if skor >= 80:
            return cls.SANGAT_TINGGI
        if skor >= 60:
            return cls.TINGGI
        if skor >= 40:
            return cls.SEDANG
        return cls.RENDAH


class JenisAnomali(StrEnum):
    """Jenis ketidaklaziman yang ditandai untuk diverifikasi manusia."""

    EXCLUSION_MISMATCH = "exclusion_mismatch"
    INCLUSION_MISMATCH = "inclusion_mismatch"
    DUPLIKASI_BANTUAN = "duplikasi_bantuan"
    INKONSISTENSI_DATA = "inkonsistensi_data"
    PERUBAHAN_BELUM_DITINDAK = "perubahan_belum_ditindak"
    POLA_TIDAK_LAZIM = "pola_tidak_lazim"
    DATA_KEDALUWARSA = "data_kedaluwarsa"

    @property
    def label(self) -> str:
        return {
            JenisAnomali.EXCLUSION_MISMATCH: "Sangat rentan namun belum tersentuh program relevan",
            JenisAnomali.INCLUSION_MISMATCH: "Menerima program yang kriterianya tidak lagi terpenuhi",
            JenisAnomali.DUPLIKASI_BANTUAN: "Menerima beberapa program dengan manfaat bertumpuk",
            JenisAnomali.INKONSISTENSI_DATA: "Isian data saling bertentangan",
            JenisAnomali.PERUBAHAN_BELUM_DITINDAK: "Kondisi memburuk namun penanganan belum berubah",
            JenisAnomali.POLA_TIDAK_LAZIM: "Pola data menyimpang dari keluarga sebanding",
            JenisAnomali.DATA_KEDALUWARSA: "Data belum dimutakhirkan melewati batas kewajaran",
        }[self]


class StatusKasus(StrEnum):
    BARU = "baru"
    DITUGASKAN = "ditugaskan"
    SEDANG_DIVERIFIKASI = "sedang_diverifikasi"
    TERVERIFIKASI_SESUAI = "terverifikasi_sesuai"
    TERVERIFIKASI_TIDAK_SESUAI = "terverifikasi_tidak_sesuai"
    PERLU_DATA_TAMBAHAN = "perlu_data_tambahan"
    DITINDAKLANJUTI = "ditindaklanjuti"
    SELESAI = "selesai"
    DITUTUP_TANPA_TINDAKAN = "ditutup_tanpa_tindakan"

    @property
    def label(self) -> str:
        return self.value.replace("_", " ").capitalize()

    @property
    def terbuka(self) -> bool:
        return self not in {
            StatusKasus.SELESAI,
            StatusKasus.DITUTUP_TANPA_TINDAKAN,
            StatusKasus.TERVERIFIKASI_TIDAK_SESUAI,
        }


class StatusIntervensi(StrEnum):
    DIRENCANAKAN = "direncanakan"
    DISETUJUI = "disetujui"
    BERJALAN = "berjalan"
    SELESAI = "selesai"
    DIBATALKAN = "dibatalkan"

    @property
    def label(self) -> str:
        return self.value.capitalize()


class JenisIntervensi(StrEnum):
    """Golongan besar tindakan, dipakai memetakan faktor risiko ke program."""

    BANTUAN_TUNAI = "bantuan_tunai"
    BANTUAN_PANGAN = "bantuan_pangan"
    JAMINAN_KESEHATAN = "jaminan_kesehatan"
    BANTUAN_PENDIDIKAN = "bantuan_pendidikan"
    PERBAIKAN_HUNIAN = "perbaikan_hunian"
    SANITASI_AIR_BERSIH = "sanitasi_air_bersih"
    PEMBERDAYAAN_EKONOMI = "pemberdayaan_ekonomi"
    PELATIHAN_KERJA = "pelatihan_kerja"
    GIZI_DAN_STUNTING = "gizi_dan_stunting"
    LAYANAN_DISABILITAS = "layanan_disabilitas"
    LAYANAN_LANSIA = "layanan_lansia"
    ADMINISTRASI_KEPENDUDUKAN = "administrasi_kependudukan"

    @property
    def label(self) -> str:
        return self.value.replace("_", " ").title()


class SumberDana(StrEnum):
    APBN = "apbn"
    APBD_PROVINSI = "apbd_provinsi"
    APBD_KABUPATEN = "apbd_kabupaten"
    DANA_DESA = "dana_desa"
    CSR = "csr"
    LAINNYA = "lainnya"

    @property
    def label(self) -> str:
        return {
            SumberDana.APBN: "APBN",
            SumberDana.APBD_PROVINSI: "APBD Provinsi",
            SumberDana.APBD_KABUPATEN: "APBD Kabupaten",
            SumberDana.DANA_DESA: "Dana Desa",
            SumberDana.CSR: "CSR / Kemitraan",
            SumberDana.LAINNYA: "Lainnya",
        }[self]


class TingkatKeyakinan(StrEnum):
    """Seberapa kuat dasar sebuah angka atau ketentuan program.

    Katalog program disusun dari peraturan, publikasi resmi, dan pemberitaan.
    Ketiganya tidak setara. Menandai tingkat keyakinan pada setiap butir
    memungkinkan antarmuka bersikap jujur: nominal bantuan yang bersumber dari
    peraturan ditampilkan tegas, sedangkan yang bersumber dari pemberitaan
    ditampilkan dengan peringatan agar diverifikasi lebih dulu.

    Tanpa penandaan ini, sistem akan terdengar sama yakinnya untuk semua hal -
    dan justru itulah yang membuat pengguna berhenti mempercayainya setelah
    menemukan satu angka yang keliru.
    """

    PASTI = "pasti"
    CUKUP_KUAT = "cukup_kuat"
    PERKIRAAN = "perkiraan"
    TIDAK_DITEMUKAN = "tidak_ditemukan"

    @property
    def label(self) -> str:
        return {
            TingkatKeyakinan.PASTI: "Bersumber dari peraturan atau dokumen resmi",
            TingkatKeyakinan.CUKUP_KUAT: "Bersumber dari publikasi resmi tidak langsung",
            TingkatKeyakinan.PERKIRAAN: "Perkiraan - perlu diverifikasi sebelum dipakai",
            TingkatKeyakinan.TIDAK_DITEMUKAN: "Belum ditemukan sumbernya",
        }[self]

    @property
    def perlu_verifikasi(self) -> bool:
        return self in {TingkatKeyakinan.PERKIRAAN, TingkatKeyakinan.TIDAK_DITEMUKAN}


class TingkatEksekusi(StrEnum):
    """Di tingkat mana sebuah program benar-benar dijalankan.

    Penting bagi orkestrasi lintas OPD: program yang ditetapkan pusat tidak
    dapat "diberikan" oleh dinas daerah, yang bisa dilakukan hanyalah
    mengusulkan dan memverifikasi. Menyamakan keduanya akan menghasilkan
    rekomendasi yang tidak dapat ditindaklanjuti siapa pun.
    """

    PUSAT_DISALURKAN_DI_DAERAH = "pusat_disalurkan_di_daerah"
    DAERAH = "daerah"
    DESA = "desa"
    MANDIRI_ONLINE = "mandiri_online"

    @property
    def label(self) -> str:
        return {
            TingkatEksekusi.PUSAT_DISALURKAN_DI_DAERAH: "Ditetapkan pusat, disalurkan di daerah",
            TingkatEksekusi.DAERAH: "Ditetapkan dan dijalankan daerah",
            TingkatEksekusi.DESA: "Dijalankan pemerintah pekon melalui APBDes",
            TingkatEksekusi.MANDIRI_ONLINE: "Pendaftaran mandiri secara daring",
        }[self]

    @property
    def tindakan_daerah(self) -> str:
        """Tindakan nyata yang dapat dilakukan OPD kabupaten atas program ini."""
        return {
            TingkatEksekusi.PUSAT_DISALURKAN_DI_DAERAH: "Usulkan dan verifikasi",
            TingkatEksekusi.DAERAH: "Tetapkan dan salurkan",
            TingkatEksekusi.DESA: "Koordinasikan dengan pemerintah pekon",
            TingkatEksekusi.MANDIRI_ONLINE: "Dampingi pendaftaran",
        }[self]


class BasisDataProgram(StrEnum):
    """Pangkalan data yang menjadi gerbang kelayakan sebuah program."""

    DTSEN = "dtsen"
    DAPODIK = "dapodik"
    DTSEN_DAN_DAPODIK = "dtsen_dan_dapodik"
    MANDIRI = "mandiri"
    LOKASI = "lokasi"
    LAINNYA = "lainnya"

    @property
    def label(self) -> str:
        return {
            BasisDataProgram.DTSEN: "DTSEN",
            BasisDataProgram.DAPODIK: "Dapodik",
            BasisDataProgram.DTSEN_DAN_DAPODIK: "DTSEN dipadankan dengan Dapodik",
            BasisDataProgram.MANDIRI: "Pendaftaran mandiri",
            BasisDataProgram.LOKASI: "Berbasis lokasi, bukan per keluarga",
            BasisDataProgram.LAINNYA: "Lainnya",
        }[self]


class FrekuensiProgram(StrEnum):
    HARIAN = "harian"
    BULANAN = "bulanan"
    TRIWULANAN = "triwulanan"
    SEMESTERAN = "semesteran"
    TAHUNAN = "tahunan"
    SEKALI = "sekali"
    BERKELANJUTAN = "berkelanjutan"
    AD_HOC = "ad_hoc"

    @property
    def label(self) -> str:
        return {
            FrekuensiProgram.HARIAN: "Harian",
            FrekuensiProgram.BULANAN: "Bulanan",
            FrekuensiProgram.TRIWULANAN: "Triwulanan",
            FrekuensiProgram.SEMESTERAN: "Semesteran",
            FrekuensiProgram.TAHUNAN: "Tahunan",
            FrekuensiProgram.SEKALI: "Sekali (tidak berulang)",
            FrekuensiProgram.BERKELANJUTAN: "Berkelanjutan",
            FrekuensiProgram.AD_HOC: "Sewaktu-waktu",
        }[self]

    @property
    def kali_per_tahun(self) -> float:
        """Berapa kali manfaat diterima dalam setahun, untuk penyetaraan nilai."""
        return {
            FrekuensiProgram.HARIAN: 220.0,  # perkiraan hari sekolah efektif
            FrekuensiProgram.BULANAN: 12.0,
            FrekuensiProgram.TRIWULANAN: 4.0,
            FrekuensiProgram.SEMESTERAN: 2.0,
            FrekuensiProgram.TAHUNAN: 1.0,
            FrekuensiProgram.SEKALI: 1.0,
            FrekuensiProgram.BERKELANJUTAN: 12.0,
            FrekuensiProgram.AD_HOC: 1.0,
        }[self]


class StatusProgram(StrEnum):
    AKTIF = "aktif"
    TIDAK_PASTI = "tidak_pasti"
    DIHENTIKAN = "dihentikan"

    @property
    def label(self) -> str:
        return {
            StatusProgram.AKTIF: "Aktif",
            StatusProgram.TIDAK_PASTI: "Status belum pasti",
            StatusProgram.DIHENTIKAN: "Dihentikan",
        }[self]


class SatuanManfaat(StrEnum):
    RUPIAH = "rupiah"
    KILOGRAM = "kilogram"
    PORSI = "porsi"
    UNIT = "unit"
    LAYANAN = "layanan"

    @property
    def label(self) -> str:
        return {
            SatuanManfaat.RUPIAH: "Rupiah",
            SatuanManfaat.KILOGRAM: "Kilogram",
            SatuanManfaat.PORSI: "Porsi",
            SatuanManfaat.UNIT: "Unit",
            SatuanManfaat.LAYANAN: "Layanan",
        }[self]


class DimensiRisiko(StrEnum):
    """Pengelompokan faktor risiko menurut dimensi kemiskinan.

    Mengikuti pandangan bahwa kemiskinan bersifat multidimensi, sebagaimana
    dinyatakan pada bagian pembuka proposal. Pengelompokan ini dipakai untuk
    menyusun tampilan penjelasan risiko agar terbaca sebagai cerita yang utuh,
    bukan sebagai daftar angka yang berserakan.
    """

    EKONOMI = "ekonomi"
    PANGAN_GIZI = "pangan_gizi"
    KESEHATAN = "kesehatan"
    PENDIDIKAN = "pendidikan"
    HUNIAN = "hunian"
    AIR_SANITASI = "air_sanitasi"
    PEKERJAAN = "pekerjaan"
    DEMOGRAFI = "demografi"
    ADMINISTRASI = "administrasi"
    GUNCANGAN = "guncangan"

    @property
    def label(self) -> str:
        return {
            DimensiRisiko.EKONOMI: "Ekonomi & Pendapatan",
            DimensiRisiko.PANGAN_GIZI: "Pangan & Gizi",
            DimensiRisiko.KESEHATAN: "Kesehatan",
            DimensiRisiko.PENDIDIKAN: "Pendidikan",
            DimensiRisiko.HUNIAN: "Hunian",
            DimensiRisiko.AIR_SANITASI: "Air Bersih & Sanitasi",
            DimensiRisiko.PEKERJAAN: "Pekerjaan & Keterampilan",
            DimensiRisiko.DEMOGRAFI: "Susunan Keluarga & Tanggungan",
            DimensiRisiko.ADMINISTRASI: "Administrasi Kependudukan",
            DimensiRisiko.GUNCANGAN: "Guncangan & Kejadian Mendadak",
        }[self]

    @property
    def ikon(self) -> str:
        """Nama ikon Lucide yang dipakai antarmuka."""
        return {
            DimensiRisiko.EKONOMI: "wallet",
            DimensiRisiko.PANGAN_GIZI: "utensils",
            DimensiRisiko.KESEHATAN: "heart-pulse",
            DimensiRisiko.PENDIDIKAN: "graduation-cap",
            DimensiRisiko.HUNIAN: "home",
            DimensiRisiko.AIR_SANITASI: "droplets",
            DimensiRisiko.PEKERJAAN: "briefcase",
            DimensiRisiko.DEMOGRAFI: "users",
            DimensiRisiko.ADMINISTRASI: "id-card",
            DimensiRisiko.GUNCANGAN: "zap",
        }[self]


class TipeAturan(StrEnum):
    """Ranah yang diperiksa sebuah aturan kelayakan."""

    DESIL = "desil"
    USIA = "usia"
    KOMPOSISI = "komposisi"
    STATUS = "status"
    DOKUMEN = "dokumen"
    KONDISI_RUMAH = "kondisi_rumah"
    AIR_SANITASI = "air_sanitasi"
    PEKERJAAN = "pekerjaan"
    KESEHATAN = "kesehatan"
    PENDIDIKAN = "pendidikan"
    LOKASI = "lokasi"
    KEPESERTAAN = "kepesertaan"


class OperatorAturan(StrEnum):
    """Pembanding yang dipakai mesin aturan kelayakan.

    Daftar ini sengaja pendek. Setiap operator tambahan memperluas apa yang
    dapat dinyatakan sebuah aturan, sekaligus memperluas apa yang dapat keliru
    tanpa disadari. Kebutuhan yang tidak terwakili di sini sebaiknya ditulis
    sebagai fitur turunan yang bernama jelas, bukan sebagai operator baru.
    """

    SAMA_DENGAN = "eq"
    TIDAK_SAMA = "ne"
    LEBIH_DARI = "gt"
    LEBIH_ATAU_SAMA = "gte"
    KURANG_DARI = "lt"
    KURANG_ATAU_SAMA = "lte"
    TERMASUK = "in"
    TIDAK_TERMASUK = "not_in"
    ANTARA = "between"
    BENAR = "is_true"
    SALAH = "is_false"
    TERISI = "exists"

    @property
    def label(self) -> str:
        return {
            OperatorAturan.SAMA_DENGAN: "sama dengan",
            OperatorAturan.TIDAK_SAMA: "tidak sama dengan",
            OperatorAturan.LEBIH_DARI: "lebih dari",
            OperatorAturan.LEBIH_ATAU_SAMA: "minimal",
            OperatorAturan.KURANG_DARI: "kurang dari",
            OperatorAturan.KURANG_ATAU_SAMA: "maksimal",
            OperatorAturan.TERMASUK: "termasuk salah satu dari",
            OperatorAturan.TIDAK_TERMASUK: "bukan salah satu dari",
            OperatorAturan.ANTARA: "berada di antara",
            OperatorAturan.BENAR: "bernilai benar",
            OperatorAturan.SALAH: "bernilai salah",
            OperatorAturan.TERISI: "terisi",
        }[self]


class StatusKepesertaan(StrEnum):
    AKTIF = "aktif"
    DIUSULKAN = "diusulkan"
    DITANGGUHKAN = "ditangguhkan"
    GRADUASI = "graduasi"
    DIHENTIKAN = "dihentikan"

    @property
    def label(self) -> str:
        return {
            StatusKepesertaan.AKTIF: "Aktif menerima",
            StatusKepesertaan.DIUSULKAN: "Diusulkan, belum ditetapkan",
            StatusKepesertaan.DITANGGUHKAN: "Ditangguhkan sementara",
            StatusKepesertaan.GRADUASI: "Graduasi mandiri",
            StatusKepesertaan.DIHENTIKAN: "Dihentikan",
        }[self]

    @property
    def sedang_menerima(self) -> bool:
        return self is StatusKepesertaan.AKTIF


class JenisWilayah(StrEnum):
    KABUPATEN = "kabupaten"
    KECAMATAN = "kecamatan"
    PEKON = "pekon"
    KELURAHAN = "kelurahan"

    @property
    def label(self) -> str:
        return self.value.capitalize()


class HasilVerifikasi(StrEnum):
    SESUAI = "sesuai"
    TIDAK_SESUAI = "tidak_sesuai"
    PERLU_DATA_TAMBAHAN = "perlu_data_tambahan"
    TIDAK_DITEMUKAN = "tidak_ditemukan"

    @property
    def label(self) -> str:
        return {
            HasilVerifikasi.SESUAI: "Kondisi sesuai dengan data sistem",
            HasilVerifikasi.TIDAK_SESUAI: "Kondisi berbeda dari data sistem",
            HasilVerifikasi.PERLU_DATA_TAMBAHAN: "Perlu data tambahan",
            HasilVerifikasi.TIDAK_DITEMUKAN: "Keluarga tidak ditemukan di alamat",
        }[self]


# ---------------------------------------------------------------------------
# Tabel label
# ---------------------------------------------------------------------------
# Label disimpan terpisah dari definisi enumerasi agar daftar anggota tetap
# mudah dibaca sekilas, dan agar penerjemahan ke bahasa lain kelak cukup
# mengganti satu tabel ini.
_LABEL: dict[str, dict[int, str]] = {
    "JenisLantai": {
        1: "Marmer/granit",
        2: "Keramik",
        3: "Parket/vinil/permadani",
        4: "Ubin/tegel/teraso",
        5: "Kayu kualitas tinggi",
        6: "Semen/bata merah",
        7: "Bambu",
        8: "Kayu kualitas rendah",
        9: "Tanah",
        10: "Lainnya",
    },
    "JenisDinding": {
        1: "Tembok",
        2: "Plesteran anyaman bambu/kawat",
        3: "Kayu/papan",
        4: "Anyaman bambu",
        5: "Batang kayu",
        6: "Bambu",
        7: "Lainnya",
    },
    "JenisAtap": {
        1: "Beton",
        2: "Genteng",
        3: "Sirap",
        4: "Seng",
        5: "Asbes",
        6: "Ijuk/rumbia",
        7: "Lainnya",
    },
    "StatusKepemilikanRumah": {
        1: "Milik sendiri",
        2: "Kontrak/sewa",
        3: "Bebas sewa",
        4: "Rumah dinas",
        5: "Lainnya",
    },
    "SumberAirMinum": {
        1: "Air kemasan bermerek",
        2: "Air isi ulang",
        3: "Leding meteran",
        4: "Leding eceran",
        5: "Sumur bor/pompa",
        6: "Sumur terlindung",
        7: "Sumur tak terlindung",
        8: "Mata air terlindung",
        9: "Mata air tak terlindung",
        10: "Air sungai",
        11: "Air hujan",
        12: "Lainnya",
    },
    "FasilitasBAB": {1: "Sendiri", 2: "Bersama", 3: "Umum", 4: "Tidak ada"},
    "JenisKloset": {
        1: "Leher angsa",
        2: "Plengsengan",
        3: "Cemplung/cubluk",
        4: "Tidak pakai",
    },
    "PembuanganTinja": {
        1: "Tangki septik",
        2: "IPAL",
        3: "Kolam/sawah/sungai/danau/laut",
        4: "Lubang tanah",
        5: "Pantai/tanah lapang/kebun",
        6: "Lainnya",
    },
    "SumberPenerangan": {
        1: "Listrik PLN dengan meteran",
        2: "Listrik PLN tanpa meteran",
        3: "Listrik non-PLN",
        4: "Bukan listrik",
    },
    "DayaListrik": {
        0: "Tanpa listrik",
        450: "450 VA",
        900: "900 VA",
        1300: "1.300 VA",
        2200: "2.200 VA",
        3500: "Di atas 2.200 VA",
    },
    "BahanBakarMemasak": {
        1: "Listrik",
        2: "Gas di atas 3 kg",
        3: "Gas 3 kg",
        4: "Gas kota",
        5: "Biogas",
        6: "Minyak tanah",
        7: "Briket",
        8: "Arang",
        9: "Kayu bakar",
        10: "Tidak memasak di rumah",
    },
    "HubunganKK": {
        1: "Kepala keluarga",
        2: "Istri/suami",
        3: "Anak",
        4: "Menantu",
        5: "Cucu",
        6: "Orang tua/mertua",
        7: "Famili lain",
        8: "Lainnya",
    },
    "JenisKelamin": {1: "Laki-laki", 2: "Perempuan"},
    "StatusPerkawinan": {
        1: "Belum kawin",
        2: "Kawin",
        3: "Cerai hidup",
        4: "Cerai mati",
    },
    "PartisipasiSekolah": {
        1: "Tidak/belum pernah sekolah",
        2: "Masih sekolah",
        3: "Tidak bersekolah lagi",
    },
    "PendidikanTertinggi": {
        1: "Tidak/belum pernah sekolah",
        2: "Tidak tamat SD",
        3: "SD/sederajat",
        4: "SMP/sederajat",
        5: "SMA/sederajat",
        6: "Diploma I/II/III",
        7: "Diploma IV/S1",
        8: "S2/S3",
    },
    "StatusKegiatan": {
        1: "Bekerja",
        2: "Mencari pekerjaan",
        3: "Sekolah",
        4: "Mengurus rumah tangga",
        5: "Lainnya",
    },
    "LapanganUsaha": {
        1: "Pertanian padi/palawija",
        2: "Hortikultura",
        3: "Perkebunan",
        4: "Perikanan",
        5: "Peternakan",
        6: "Kehutanan",
        7: "Pertambangan",
        8: "Industri pengolahan",
        9: "Listrik/gas/air",
        10: "Konstruksi",
        11: "Perdagangan",
        12: "Hotel/rumah makan",
        13: "Transportasi/pergudangan",
        14: "Informasi/komunikasi",
        15: "Keuangan/asuransi",
        16: "Jasa pendidikan",
        17: "Jasa kesehatan",
        18: "Jasa pemerintahan",
        19: "Jasa lainnya",
        20: "Tidak bekerja",
    },
    "StatusPekerjaan": {
        1: "Berusaha sendiri",
        2: "Berusaha dibantu buruh tidak tetap",
        3: "Berusaha dibantu buruh tetap",
        4: "Buruh/karyawan/pegawai",
        5: "Pekerja bebas pertanian",
        6: "Pekerja bebas non-pertanian",
        7: "Pekerja keluarga tak dibayar",
        8: "Tidak bekerja",
    },
    "JenisDisabilitas": {
        1: "Tidak ada",
        2: "Tunanetra",
        3: "Tunarungu",
        4: "Tunawicara",
        5: "Tunadaksa",
        6: "Tunagrahita",
        7: "Tunalaras",
        8: "Disabilitas ganda",
        9: "Eks gangguan jiwa",
    },
    "PenyakitKronis": {
        1: "Tidak ada",
        2: "Hipertensi",
        3: "Diabetes",
        4: "Jantung",
        5: "Stroke",
        6: "Tuberkulosis",
        7: "Kanker",
        8: "Gagal ginjal",
        9: "Lainnya",
    },
    "StatusGiziBalita": {
        0: "Tidak ada balita",
        1: "Gizi baik",
        2: "Gizi kurang",
        3: "Gizi buruk",
        4: "Stunting",
        5: "Obesitas",
    },
    "JenisGuncangan": {
        1: "Sakit berat anggota keluarga",
        2: "Kehilangan pekerjaan",
        3: "Gagal panen",
        4: "Kematian pencari nafkah",
        5: "Bencana alam",
        6: "Kelahiran anggota baru",
        7: "Perceraian",
        8: "Kenaikan harga pangan",
        9: "Kerusakan rumah",
        10: "Anak masuk jenjang pendidikan baru",
    },
    "TingkatKeparahan": {1: "Ringan", 2: "Sedang", 3: "Berat"},
}


__all__ = [
    "BahanBakarMemasak",
    "BasisDataProgram",
    "DayaListrik",
    "DimensiRisiko",
    "FasilitasBAB",
    "FrekuensiProgram",
    "HasilVerifikasi",
    "HubunganKK",
    "JenisAnomali",
    "JenisAtap",
    "JenisDinding",
    "JenisDisabilitas",
    "JenisGuncangan",
    "JenisIntervensi",
    "JenisKelamin",
    "JenisKloset",
    "JenisLantai",
    "JenisWilayah",
    "KategoriRisiko",
    "LapanganUsaha",
    "OperatorAturan",
    "PartisipasiSekolah",
    "PembuanganTinja",
    "PendidikanTertinggi",
    "PenyakitKronis",
    "SatuanManfaat",
    "StatusGiziBalita",
    "StatusIntervensi",
    "StatusKasus",
    "StatusKegiatan",
    "StatusKepemilikanRumah",
    "StatusKepesertaan",
    "StatusPekerjaan",
    "StatusPerkawinan",
    "StatusProgram",
    "SumberAirMinum",
    "SumberDana",
    "SumberPenerangan",
    "TingkatEksekusi",
    "TingkatKeparahan",
    "TingkatKeyakinan",
    "TipeAturan",
]
