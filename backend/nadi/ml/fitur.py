"""Rekayasa fitur: dari kondisi mentah menjadi sinyal kerentanan.

Modul ini adalah satu-satunya tempat di mana data mentah berubah menjadi
masukan model. Pemusatan itu disengaja dan menyelesaikan dua persoalan yang
melumpuhkan banyak sistem serupa.

**Kebocoran latih-sajikan** (*training-serving skew*). Bila fitur dihitung
dengan kode berbeda saat melatih dan saat melayani permintaan, model bekerja
baik pada catatan pengujian lalu meleset pada layar pengguna, dan tidak ada
yang tahu sebabnya. Di sini keduanya memanggil fungsi yang sama persis.

**Kebocoran masa depan** (*target leakage*). Setiap fitur di sini dihitung
hanya dari keadaan pada gelombang ``t``. Tidak ada satu pun yang menengok ke
gelombang ``t+1``, tempat label berada. Aturan ini ditegakkan oleh struktur
kode, bukan oleh kedisiplinan: fungsi pembentuk fitur hanya menerima satu
baris kondisi dan konteks wilayahnya, sehingga secara teknis tidak memiliki
akses ke masa depan.

Setiap fitur juga membawa metadata - dimensi kerentanan, faktor risiko yang
diwakilinya, dan kalimat penjelas berbahasa Indonesia. Metadata inilah yang
memungkinkan keluaran TreeSHAP diterjemahkan langsung menjadi alasan yang
dibaca petugas, tanpa tabel penerjemah terpisah yang gampang tertinggal saat
daftar fitur berubah.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Iterable

import numpy as np
import pandas as pd

from nadi.db.enums import DimensiRisiko

# ---------------------------------------------------------------------------
# Deskripsi fitur
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Fitur:
    """Satu fitur model beserta seluruh keterangannya.

    Atribut :attr:`kode_risiko` adalah penghubung menuju katalog faktor risiko.
    Ketika TreeSHAP menyatakan fitur ini mendorong skor naik, kode tersebut
    menuntun sistem langsung ke program yang menangani persoalannya.
    """

    nama: str
    label: str
    dimensi: DimensiRisiko
    keterangan: str
    kode_risiko: str | None = None
    arah_buruk: int = 1
    """Arah yang menandakan kerentanan lebih tinggi: 1 bila nilai besar berarti
    lebih rentan, -1 bila sebaliknya. Dipakai untuk menyusun kalimat penjelasan
    yang benar tanpa menuliskannya satu per satu."""

    satuan: str | None = None
    biner: bool = False

    melingkar: bool = False
    """Apakah fitur ini mencerminkan KEPUTUSAN pemerintah, bukan KEADAAN keluarga.

    Kepesertaan program adalah contohnya. Sekilas ia penduga yang baik - dan
    memang demikian, sebab bantuan disalurkan kepada yang miskin. Justru di
    situlah persoalannya: yang dipelajari model bukanlah siapa yang
    membutuhkan, melainkan siapa yang selama ini sudah ditetapkan sebagai
    penerima.

    Pengukuran pada data ini menunjukkan arahnya secara gamblang: penanda
    "tidak menerima bantuan apa pun" berkorelasi NEGATIF dengan kemiskinan
    pada gelombang berikutnya (-0,12). Model yang memakainya akan menempatkan
    keluarga yang belum tersentuh bantuan lebih rendah pada antrean - padahal
    merekalah yang paling perlu ditemukan.

    Fitur bertanda ini dikeluarkan dari model dan dipakai di tempat yang tepat:
    pada detektor ketidaksesuaian, tempat aturan "sangat rentan namun belum
    menerima apa pun" memang seharusnya berada.

    Pengujian menunjukkan biaya mengeluarkannya hampir nol - AUC turun dari
    0,859 menjadi 0,858. Pilihan yang benar ternyata tidak menuntut pengorbanan.
    """

    sumber: str = "dtsen"
    """Dari mana fitur ini benar-benar dapat diperoleh pemerintah daerah.

    Tiga nilai yang dipakai, dan pembedaannya menentukan kejujuran seluruh
    angka evaluasi:

    ``dtsen``
        Ada langsung pada Data Tunggal Sosial dan Ekonomi Nasional. Tersedia
        hari ini, tanpa syarat apa pun.

    ``lintas_opd``
        Menuntut pemaduan data antar-dinas - catatan kematian dari Dukcapil,
        pemutusan hubungan kerja dari BPJS Ketenagakerjaan, gagal panen dari
        Dinas Pertanian, kejadian bencana dari BPBD, hasil kunjungan lapangan
        dari Dinas Sosial. Tidak ada satu pun di DTSEN. Justru pemaduan inilah
        yang menjadi nilai tambah NADI, dan biayanya berupa kerja koordinasi
        yang nyata - bukan sekadar tambahan kolom.

    ``survei_konsumsi``
        Menuntut pencacahan pengeluaran rumah tangga gaya Susenas, yang mahal,
        jarang, dan tidak mencakup seluruh keluarga. Fitur bertanda ini TIDAK
        dipakai model yang dijalankan, dan hanya disertakan sebagai pembanding
        untuk menunjukkan berapa nilai tambahnya bila kelak dipadankan.
    """

    tersedia_dtsen: bool = True
    """Apakah fitur ini benar-benar ada pada data yang dimiliki pemerintah daerah.

    Pembedaan ini menentukan kejujuran seluruh angka evaluasi, dan mudah
    terlewat sampai hasilnya terlalu bagus untuk dipercaya.

    DTSEN **tidak memuat pengeluaran per kapita yang terukur.** Justru karena
    mengukur konsumsi rumah tangga menuntut pencacahan Susenas yang mahal dan
    jarang, pemerintah memakai penduga tak langsung - kondisi rumah, aset,
    pendidikan, pekerjaan - untuk memperkirakannya. Itulah seluruh alasan
    keberadaan proxy means test.

    Memberi model angka pengeluaran terukur berarti memberinya jawaban yang
    seharusnya ia perkirakan. Hasilnya tampak mengesankan pada kertas dan
    mustahil dijalankan di lapangan, sebab angka itu tidak akan tersedia saat
    sistem benar-benar dipakai.

    Fitur bertanda ``False`` tetap dihitung dan disimpan, namun tidak dipakai
    model utama. Keduanya diadu berdampingan, dan selisihnya justru menjadi
    keterangan yang berguna bagi pengambil kebijakan: sebesar itulah nilai
    tambah bila data Susenas kelak dipadankan dengan DTSEN.
    """

    def kalimat(self, nilai: Any) -> str:
        """Susun kalimat penjelasan untuk satu nilai fitur."""
        if self.biner:
            return self.label if nilai else f"Tidak {self.label.lower()}"
        if self.satuan:
            return f"{self.label}: {_format_angka(nilai)} {self.satuan}"
        return f"{self.label}: {_format_angka(nilai)}"


def _format_angka(nilai: Any) -> str:
    """Format angka mengikuti kelaziman Indonesia - koma sebagai desimal."""
    if nilai is None:
        return "-"
    if isinstance(nilai, (bool, np.bool_)):
        return "ya" if nilai else "tidak"
    if isinstance(nilai, (int, np.integer)):
        return f"{int(nilai):,}".replace(",", ".")
    if isinstance(nilai, (float, np.floating)):
        if float(nilai).is_integer():
            return f"{int(nilai):,}".replace(",", ".")
        return f"{nilai:,.2f}".replace(",", "~").replace(".", ",").replace("~", ".")
    return str(nilai)


# ---------------------------------------------------------------------------
# Daftar fitur
# ---------------------------------------------------------------------------
D = DimensiRisiko

DAFTAR_FITUR: tuple[Fitur, ...] = (
    # ----- Ekonomi -----
    Fitur(
        "rasio_garis_kemiskinan",
        "Rasio pengeluaran terhadap garis kemiskinan",
        D.EKONOMI,
        "Pengeluaran per kapita dibagi garis kemiskinan yang berlaku. Nilai di "
        "bawah 1 berarti sudah miskin; antara 1 dan 1,5 berarti rentan.",
        kode_risiko="R01",
        arah_buruk=-1,
        tersedia_dtsen=False,
        sumber="survei_konsumsi",
    ),
    Fitur(
        "log_pengeluaran_per_kapita",
        "Pengeluaran per kapita (skala logaritmik)",
        D.EKONOMI,
        "Logaritma pengeluaran per kapita. Skala logaritmik dipakai karena "
        "selisih seratus ribu rupiah jauh lebih berarti bagi keluarga miskin "
        "daripada bagi keluarga mampu.",
        kode_risiko="R01",
        arah_buruk=-1,
        tersedia_dtsen=False,
        sumber="survei_konsumsi",
    ),
    Fitur(
        "desil_kesejahteraan",
        "Desil kesejahteraan DTSEN",
        D.EKONOMI,
        "Peringkat kesejahteraan 1 sampai 10 hasil pemeringkatan DTSEN. "
        "Desil 1 adalah sepuluh persen termiskin.",
        kode_risiko="R01",
        arah_buruk=-1,
    ),
    Fitur(
        "indeks_aset",
        "Indeks kepemilikan aset",
        D.EKONOMI,
        "Gabungan berbobot seluruh aset yang dimiliki. Aset menahan keluarga "
        "dari kejatuhan karena dapat dijual saat terdesak - fungsinya sebagai "
        "penyangga tidak terlihat pada angka pengeluaran.",
        kode_risiko="R01",
        arah_buruk=-1,
    ),
    Fitur(
        "punya_aset_produktif",
        "Memiliki aset produktif",
        D.EKONOMI,
        "Lahan, ternak, atau perahu motor - aset yang menghasilkan pemasukan, "
        "bukan sekadar menyimpan nilai.",
        kode_risiko="R14",
        arah_buruk=-1,
        biner=True,
    ),
    # ----- Pekerjaan -----
    Fitur(
        "rasio_tanggungan",
        "Rasio tanggungan",
        D.DEMOGRAFI,
        "Jumlah anggota yang tidak bekerja dibagi jumlah yang bekerja. Semakin "
        "tinggi, semakin berat beban satu penghasilan.",
        kode_risiko="R01",
    ),
    Fitur(
        "tidak_ada_yang_bekerja",
        "Tidak ada anggota yang bekerja",
        D.PEKERJAAN,
        "Tidak seorang pun anggota keluarga berstatus bekerja.",
        kode_risiko="R13",
        biner=True,
    ),
    Fitur(
        "kk_pekerjaan_rentan",
        "Kepala keluarga berstatus pekerjaan rentan",
        D.PEKERJAAN,
        "Berusaha sendiri, pekerja bebas, atau pekerja keluarga tak dibayar - "
        "golongan yang penghasilannya tidak pasti dan tanpa perlindungan.",
        kode_risiko="R15",
        biner=True,
    ),
    Fitur(
        "kk_sektor_musiman",
        "Kepala keluarga bekerja di sektor musiman",
        D.PEKERJAAN,
        "Pertanian, perikanan, kehutanan, atau konstruksi - sektor yang "
        "penghasilannya berayun mengikuti musim dan cuaca.",
        kode_risiko="R19",
        biner=True,
    ),
    Fitur(
        "kk_berpenghasilan_tetap",
        "Kepala keluarga berpenghasilan tetap",
        D.PEKERJAAN,
        "Buruh, karyawan, atau pegawai - penghasilan lebih dapat diperkirakan.",
        kode_risiko="R13",
        arah_buruk=-1,
        biner=True,
    ),
    Fitur(
        "jumlah_usaha_keluarga",
        "Jumlah usaha yang dimiliki keluarga",
        D.PEKERJAAN,
        "Usaha mikro yang dijalankan anggota keluarga.",
        kode_risiko="R14",
        arah_buruk=-1,
    ),
    # ----- Pendidikan -----
    Fitur(
        "kk_tahun_sekolah",
        "Lama sekolah kepala keluarga",
        D.PENDIDIKAN,
        "Perkiraan tahun sekolah kepala keluarga. Pendidikan kepala keluarga "
        "adalah salah satu penduga kesejahteraan yang paling konsisten.",
        # Dipetakan ke keterbatasan keterampilan, BUKAN ke anak putus sekolah.
        # Pemetaan sebelumnya menempatkannya pada R05, dan akibatnya keluarga
        # tanpa satu pun anak usia sekolah tetap menerima penjelasan "anak
        # putus sekolah" - penjelasan yang keliru dan langsung terlihat keliru
        # oleh petugas yang mengenal keluarganya. Pendidikan orang dewasa
        # menuntun ke pelatihan kerja, bukan ke bantuan pendidikan anak.
        kode_risiko="R13",
        arah_buruk=-1,
        satuan="tahun",
    ),
    Fitur(
        "rata_lama_sekolah_dewasa",
        "Rata-rata lama sekolah anggota dewasa",
        D.PENDIDIKAN,
        "Rata-rata tahun sekolah seluruh anggota berusia dewasa.",
        kode_risiko="R13",
        arah_buruk=-1,
        satuan="tahun",
    ),
    Fitur(
        "ada_anak_putus_sekolah",
        "Ada anak putus sekolah",
        D.PENDIDIKAN,
        "Anak usia sekolah yang tidak lagi bersekolah - penanda paling awal "
        "bahwa kemiskinan sedang berpindah ke generasi berikutnya.",
        kode_risiko="R05",
        biner=True,
    ),
    Fitur(
        "beban_anak_sekolah",
        "Jumlah anak usia sekolah",
        D.PENDIDIKAN,
        "Banyaknya anak usia sekolah yang biaya pendidikannya ditanggung.",
        kode_risiko="R05",
    ),
    # ----- Kesehatan -----
    Fitur(
        "ada_penyakit_biaya_tinggi",
        "Ada anggota berpenyakit berbiaya tinggi",
        D.KESEHATAN,
        "Jantung, stroke, kanker, atau gagal ginjal. Pengeluaran kesehatan "
        "katastrofik adalah jalur tercepat sebuah keluarga jatuh miskin.",
        kode_risiko="R18",
        biner=True,
    ),
    Fitur(
        "ada_penyakit_kronis",
        "Ada anggota berpenyakit kronis",
        D.KESEHATAN,
        "Penyakit menahun yang menuntut pengobatan berkelanjutan.",
        kode_risiko="R18",
        biner=True,
    ),
    Fitur(
        "cakupan_jkn",
        "Cakupan jaminan kesehatan",
        D.KESEHATAN,
        "Bagian anggota keluarga yang memiliki jaminan kesehatan. Tanpa "
        "jaminan, satu kali rawat inap dapat menghabiskan tabungan bertahun-tahun.",
        kode_risiko="R07",
        arah_buruk=-1,
    ),
    Fitur(
        "tanpa_jkn_sama_sekali",
        "Tidak ada anggota yang memiliki jaminan kesehatan",
        D.KESEHATAN,
        "Seluruh anggota keluarga berada di luar perlindungan jaminan kesehatan.",
        kode_risiko="R07",
        biner=True,
    ),
    Fitur(
        "ada_gizi_bermasalah",
        "Ada balita bermasalah gizi",
        D.PANGAN_GIZI,
        "Balita dengan gizi kurang, gizi buruk, atau stunting.",
        kode_risiko="R03",
        biner=True,
    ),
    Fitur(
        "jumlah_disabilitas",
        "Jumlah anggota penyandang disabilitas",
        D.KESEHATAN,
        "Anggota keluarga penyandang disabilitas yang memerlukan dukungan.",
        kode_risiko="R12",
    ),
    Fitur(
        "ada_ibu_hamil",
        "Ada ibu hamil atau dalam masa nifas",
        D.KESEHATAN,
        "Kehamilan menuntut tambahan gizi dan biaya persalinan pada saat "
        "kemampuan bekerja justru berkurang.",
        kode_risiko="R04",
        biner=True,
    ),
    # ----- Administrasi kependudukan -----
    Fitur(
        "ada_masalah_dokumen",
        "Ada anggota tanpa dokumen kependudukan",
        D.ADMINISTRASI,
        "Tanpa nomor induk kependudukan yang sah, keluarga tidak dapat "
        "ditetapkan sebagai penerima program mana pun. Ini hambatan paling "
        "mendasar dan seringkali paling mudah diselesaikan.",
        kode_risiko="R16",
        biner=True,
    ),
    # ----- Hunian, air, sanitasi -----
    Fitur(
        "luas_lantai_per_kapita",
        "Luas lantai per orang",
        D.HUNIAN,
        "Luas lantai dibagi jumlah anggota. Di bawah 7,2 meter persegi "
        "dinilai tidak memenuhi kecukupan ruang.",
        kode_risiko="R08",
        arah_buruk=-1,
        satuan="m2",
    ),
    Fitur(
        "hunian_padat",
        "Hunian padat",
        D.HUNIAN,
        "Luas lantai per orang di bawah ambang kelayakan.",
        kode_risiko="R08",
        biner=True,
    ),
    Fitur(
        "ketahanan_bangunan_tidak_layak",
        "Ketahanan bangunan tidak layak",
        D.HUNIAN,
        "Salah satu dari atap, dinding, atau lantai berbahan tidak layak.",
        kode_risiko="R08",
        biner=True,
    ),
    Fitur(
        "berbagi_rumah",
        "Berbagi rumah dengan keluarga lain",
        D.HUNIAN,
        "Lebih dari satu keluarga tinggal dalam satu rumah - kepadatan yang "
        "tidak tampak dari angka luas lantai.",
        kode_risiko="R08",
        biner=True,
    ),
    Fitur(
        "sanitasi_tidak_layak",
        "Sanitasi tidak layak",
        D.AIR_SANITASI,
        "Fasilitas buang air, jenis kloset, atau pembuangan tinja belum "
        "memenuhi kriteria layak.",
        kode_risiko="R09",
        biner=True,
    ),
    Fitur(
        "air_minum_tidak_layak",
        "Air minum tidak layak",
        D.AIR_SANITASI,
        "Sumber air minum berasal dari sumber tak terlindung atau air permukaan.",
        kode_risiko="R10",
        biner=True,
    ),
    Fitur(
        "listrik_daya_rendah",
        "Daya listrik rendah atau tanpa listrik",
        D.HUNIAN,
        "Daya terpasang 450 atau 900 VA, atau tidak berlistrik sama sekali. "
        "Penanda ekonomi yang mudah diverifikasi dan sulit dimanipulasi.",
        kode_risiko="R01",
        biner=True,
    ),
    Fitur(
        "memasak_bahan_bakar_tidak_layak",
        "Memasak dengan bahan bakar tidak layak",
        D.HUNIAN,
        "Kayu bakar, arang, briket, atau minyak tanah.",
        kode_risiko="R08",
        biner=True,
    ),
    Fitur(
        "jumlah_kriteria_rtlh",
        "Jumlah kriteria rumah layak huni yang tidak terpenuhi",
        D.HUNIAN,
        "Berapa dari empat kriteria rumah layak huni yang belum terpenuhi.",
        kode_risiko="R08",
    ),
    # ----- Demografi -----
    Fitur(
        "jumlah_anggota",
        "Jumlah anggota keluarga",
        D.DEMOGRAFI,
        "Banyaknya orang yang ditanggung oleh keluarga.",
        kode_risiko="R01",
    ),
    Fitur(
        "kk_perempuan",
        "Kepala keluarga perempuan",
        D.DEMOGRAFI,
        "Keluarga dengan kepala keluarga perempuan menghadapi hambatan "
        "ekonomi yang berbeda dan menjadi kriteria eksplisit beberapa program.",
        kode_risiko="R17",
        biner=True,
    ),
    Fitur(
        "kk_lansia",
        "Kepala keluarga berusia lanjut",
        D.DEMOGRAFI,
        "Kepala keluarga berusia enam puluh tahun ke atas.",
        kode_risiko="R11",
        biner=True,
    ),
    Fitur(
        "jumlah_balita",
        "Jumlah balita",
        D.DEMOGRAFI,
        "Anak berusia di bawah lima tahun yang memerlukan perhatian gizi.",
        kode_risiko="R03",
    ),
    Fitur(
        "jumlah_lansia",
        "Jumlah anggota lanjut usia",
        D.DEMOGRAFI,
        "Anggota berusia enam puluh tahun ke atas.",
        kode_risiko="R11",
    ),
    # ----- Perlindungan sosial -----
    Fitur(
        "jumlah_program_diterima",
        "Jumlah program yang diterima",
        D.EKONOMI,
        "Banyaknya program bantuan yang sedang diterima keluarga.",
        kode_risiko="R01",
        arah_buruk=-1,
        melingkar=True
    ),
    Fitur(
        "nilai_bantuan_per_kapita",
        "Nilai bantuan per orang per bulan",
        D.EKONOMI,
        "Total manfaat bantuan dibagi jumlah anggota keluarga.",
        kode_risiko="R01",
        arah_buruk=-1,
        satuan="rupiah",
        melingkar=True
    ),
    Fitur(
        "tanpa_bantuan_apa_pun",
        "Tidak menerima bantuan apa pun",
        D.EKONOMI,
        "Belum tersentuh satu pun program perlindungan sosial.",
        kode_risiko="R01",
        biner=True,
        melingkar=True
    ),
    # ----- Guncangan -----
    Fitur(
        "jumlah_guncangan_terkini",
        "Jumlah guncangan pada periode ini",
        D.GUNCANGAN,
        "Kejadian mendadak yang menimpa keluarga pada gelombang ini.",
        kode_risiko="R19",
        sumber="lintas_opd"
    ),
    Fitur(
        "ada_guncangan_pendapatan",
        "Mengalami guncangan pendapatan",
        D.GUNCANGAN,
        "Kehilangan pekerjaan, gagal panen, sakit berat, kematian pencari "
        "nafkah, atau bencana.",
        kode_risiko="R19",
        biner=True,
        sumber="lintas_opd"
    ),
    Fitur(
        "ada_guncangan_bencana",
        "Terdampak bencana",
        D.GUNCANGAN,
        "Keluarga terdampak bencana alam pada periode ini. Dibedakan dari "
        "guncangan lain karena penanganannya melibatkan jalur kelembagaan "
        "tersendiri dan bersifat mendesak.",
        kode_risiko="R20",
        biner=True,
        sumber="lintas_opd"
    ),
    Fitur(
        "bobot_guncangan",
        "Bobot guncangan tertimbang keparahan",
        D.GUNCANGAN,
        "Gabungan jumlah dan tingkat keparahan guncangan yang dialami.",
        kode_risiko="R19",
        sumber="lintas_opd"
    ),
    # ----- Dinamika -----
    Fitur(
        "delta_rasio_kemiskinan",
        "Perubahan rasio kemiskinan dari periode sebelumnya",
        D.EKONOMI,
        "Selisih rasio terhadap garis kemiskinan dibanding gelombang lalu. "
        "Nilai negatif berarti keadaan sedang memburuk.",
        kode_risiko="R19",
        arah_buruk=-1,
        tersedia_dtsen=False,
        sumber="survei_konsumsi",
    ),
    Fitur(
        "tren_menurun",
        "Kondisi ekonomi sedang menurun",
        D.EKONOMI,
        "Pengeluaran per kapita menurun dibanding gelombang sebelumnya.",
        kode_risiko="R19",
        biner=True,
        tersedia_dtsen=False,
        sumber="survei_konsumsi",
    ),
    Fitur(
        "pernah_miskin_sebelumnya",
        "Pernah berstatus miskin sebelumnya",
        D.EKONOMI,
        "Keluarga pernah berada di bawah garis kemiskinan pada gelombang "
        "sebelumnya. Riwayat kemiskinan sangat menentukan peluang terulangnya.",
        kode_risiko="R01",
        biner=True,
        tersedia_dtsen=False,
        sumber="survei_konsumsi",
    ),
    # ----- Konteks wilayah -----
    Fitur(
        "persen_miskin_wilayah",
        "Tingkat kemiskinan di wilayahnya",
        D.EKONOMI,
        "Persentase keluarga miskin di pekon atau kelurahan tempat tinggal. "
        "Kemiskinan mengelompok secara geografis; lingkungan sekitar membawa "
        "keterangan yang tidak dimiliki data keluarga itu sendiri.",
        kode_risiko="R01",
    ),
    Fitur(
        "wilayah_perdesaan",
        "Bertempat tinggal di wilayah perdesaan",
        D.EKONOMI,
        "Akses terhadap layanan dan peluang kerja berbeda antara desa dan kota.",
        kode_risiko="R01",
        biner=True,
    ),
    # ----- Kualitas data -----
    Fitur(
        "umur_data_bulan",
        "Umur data dalam bulan",
        D.ADMINISTRASI,
        "Lama sejak pemutakhiran terakhir. Data usang menyembunyikan "
        "perubahan - ketidaktahuan itu sendiri adalah risiko.",
        kode_risiko="R16",
        satuan="bulan",
    ),
    Fitur(
        "kelengkapan_data",
        "Kelengkapan data",
        D.ADMINISTRASI,
        "Bagian bidang wajib yang terisi.",
        kode_risiko="R16",
        arah_buruk=-1,
    ),
)

#: Tiga lapis himpunan fitur, menurut apa yang benar-benar dapat diperoleh.
#:
#: Menyandingkan ketiganya menjawab pertanyaan yang benar-benar berguna bagi
#: pengambil kebijakan: seberapa jauh kemampuan menargetkan dapat ditingkatkan
#: dengan memadukan data antar-dinas, dan seberapa jauh lagi bila pencacahan
#: konsumsi ikut dipadankan. Selisih antar-lapis adalah nilai tambah pemaduan
#: data, dinyatakan sebagai angka alih-alih sebagai gagasan.
NAMA_FITUR_DTSEN: tuple[str, ...] = tuple(
    f.nama for f in DAFTAR_FITUR if f.sumber == "dtsen" and not f.melingkar
)

#: Himpunan yang dipakai model NADI yang dijalankan: DTSEN ditambah sinyal
#: lintas dinas. Inilah keadaan yang dapat dicapai pemerintah daerah hari ini
#: dengan koordinasi, tanpa menunggu pencacahan baru.
NAMA_FITUR_OPERASIONAL: tuple[str, ...] = tuple(
    f.nama
    for f in DAFTAR_FITUR
    if f.sumber in {"dtsen", "lintas_opd"} and not f.melingkar
)

#: Seluruh fitur, termasuk yang menuntut pencacahan konsumsi. HANYA dipakai
#: sebagai pembanding batas atas, tidak pernah untuk model yang dijalankan.
NAMA_FITUR_LENGKAP: tuple[str, ...] = tuple(
    f.nama for f in DAFTAR_FITUR if not f.melingkar
)

#: Fitur yang mencerminkan keputusan penargetan pemerintah, bukan keadaan
#: keluarga. TIDAK dipakai model mana pun; disediakan bagi detektor
#: ketidaksesuaian dan bagi tampilan profil keluarga.
NAMA_FITUR_MELINGKAR: tuple[str, ...] = tuple(
    f.nama for f in DAFTAR_FITUR if f.melingkar
)


#: Peta cepat dari nama fitur ke keterangannya.
PETA_FITUR: dict[str, Fitur] = {f.nama: f for f in DAFTAR_FITUR}

#: Urutan kolom yang dipakai model. Dibekukan agar model yang dilatih hari ini
#: tetap dapat dipakai bulan depan meski daftar fitur bertambah di bawahnya.
NAMA_FITUR: tuple[str, ...] = tuple(f.nama for f in DAFTAR_FITUR)


def fitur_per_dimensi() -> dict[DimensiRisiko, list[Fitur]]:
    """Kelompokkan fitur menurut dimensi kerentanan."""
    hasil: dict[DimensiRisiko, list[Fitur]] = {}
    for f in DAFTAR_FITUR:
        hasil.setdefault(f.dimensi, []).append(f)
    return hasil


def fitur_untuk_risiko(kode_risiko: str) -> list[Fitur]:
    """Seluruh fitur yang memetakan ke satu kode faktor risiko."""
    return [f for f in DAFTAR_FITUR if f.kode_risiko == kode_risiko]


__all__ = [
    "DAFTAR_FITUR",
    "Fitur",
    "NAMA_FITUR",
    "NAMA_FITUR_DTSEN",
    "NAMA_FITUR_LENGKAP",
    "NAMA_FITUR_MELINGKAR",
    "NAMA_FITUR_OPERASIONAL",
    "PETA_FITUR",
    "fitur_per_dimensi",
    "fitur_untuk_risiko",
]
