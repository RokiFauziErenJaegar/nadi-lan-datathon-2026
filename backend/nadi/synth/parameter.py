"""Parameter kalibrasi generator data sintetis.

Seluruh angka acuan berkumpul di satu berkas ini, masing-masing disertai
sumbernya. Alasannya bukan kerapian melainkan pertanggungjawaban: ketika dewan
juri atau pejabat bertanya "dari mana angka ini", jawabannya harus dapat
ditunjuk pada satu baris, bukan dicari di antara ribuan baris kode.

Data yang dihasilkan bersifat **sintetis sepenuhnya**. Tidak ada satu pun
keluarga nyata di dalamnya. Yang ditiru adalah *bentuk statistik* penduduk
Kabupaten Pringsewu - berapa persen yang miskin, seperti apa sebaran
pengeluarannya, seberapa sering rumah berlantai tanah - sehingga sistem dapat
diuji pada data yang berperilaku seperti aslinya tanpa menyentuh data pribadi
siapa pun.

Satu gagasan menaungi seluruh rancangan: **model tidak boleh dapat menebak
dengan sempurna.** Proses pembangkitan sengaja memuat variabel laten yang tidak
pernah dilihat model - kemampuan berusaha, kekuatan jejaring sosial, ketahanan
menghadapi penyakit, dan keberuntungan. Tanpa itu, model akan mencapai AUC
mendekati satu dan seluruh angka evaluasi menjadi tidak berarti. Dengan itu,
angka evaluasi berada pada kisaran yang wajar bagi persoalan penargetan
kemiskinan sebagaimana dilaporkan literatur.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# ===========================================================================
# ACUAN RESMI KABUPATEN PRINGSEWU
# ===========================================================================


@dataclass(frozen=True)
class AcuanPringsewu:
    """Angka resmi yang menjadi sasaran kalibrasi.

    Sumber tercantum pada setiap kolom. Angka yang belum terverifikasi ditandai
    pada :attr:`catatan_keyakinan`.
    """

    # --- Kependudukan ---
    #
    # PERINGATAN: tiga angka penduduk beredar untuk Kabupaten Pringsewu dan
    # ketiganya benar menurut definisinya masing-masing. Mencampurnya adalah
    # kekeliruan yang mudah terjadi dan berakibat pada seluruh angka turunan.
    #
    #   DTSEN 2026            451.586 jiwa  - basis penargetan bantuan
    #   Dukcapil DKB 2024     444.834 jiwa  - satu-satunya yang tersedia per kecamatan
    #   Proyeksi BPS SP2020  ~416.000 jiwa  - basis SELURUH indikator makro,
    #                                         termasuk angka kemiskinan
    #
    # Angka kemiskinan BPS dihitung terhadap proyeksi, bukan terhadap DTSEN
    # maupun Dukcapil. Memakai basis yang keliru menggeser seluruh sasaran
    # kalibrasi sekitar satu setengah poin persen.
    jumlah_penduduk_dtsen: int = 451_586
    """Jiwa menurut DTSEN 2026. Dipakai untuk penargetan, BUKAN untuk
    menghitung angka kemiskinan."""

    jumlah_penduduk_dukcapil: int = 444_834
    """Jiwa menurut Data Konsolidasi Bersih Semester II 2024 Kemendagri.
    Satu-satunya sumber yang tersedia sampai tingkat kecamatan."""

    jumlah_penduduk_proyeksi_bps: int = 416_579
    """Jiwa menurut proyeksi BPS hasil Sensus Penduduk 2020, tahun 2025.

    Diturunkan dari angka resmi yang saling bersesuaian: 31,66 ribu penduduk
    miskin setara 7,60 persen, sehingga basisnya 416.579 jiwa. Uji silang
    dengan angka 2024 memberi hasil serupa: 34,42 ribu setara 8,32 persen,
    yakni 413.702 jiwa. INILAH basis yang benar untuk seluruh angka kemiskinan.
    """

    jumlah_keluarga: int = 144_262
    """Kartu keluarga. Sumber: DTSEN 2026."""

    jumlah_keluarga_desil_1_5: int = 73_879
    """Keluarga pada desil kesejahteraan 1 sampai 5, sekitar 51,2 persen dari
    seluruh keluarga. Sumber: DTSEN 2026. Inilah cakupan yang menjadi ruang
    kerja NADI - sistem penargetan kemiskinan tidak perlu memuat seluruh
    penduduk, cukup mereka yang berpeluang menjadi sasaran program."""

    jumlah_penduduk_desil_1_5: int = 241_740
    """Jiwa. Sumber: DTSEN 2026."""

    # --- Kemiskinan ---
    garis_kemiskinan: float = 583_425.0
    """Rupiah per kapita per bulan. Sumber: BPS 2024.

    Ini satu-satunya garis kemiskinan tingkat kabupaten yang terverifikasi
    silang pada dua dokumen. Angka 2025 beredar sekitar Rp613.000 namun hanya
    dalam bentuk naratif, sehingga tidak dipakai.
    """

    pengali_garis_kerentanan: float = 1.5
    """Pengali garis kemiskinan untuk menetapkan garis kerentanan.

    Mengikuti klasifikasi Bank Dunia: penduduk dengan pengeluaran antara satu
    sampai satu setengah kali garis kemiskinan tergolong rentan miskin -
    kelompok yang belum tercatat miskin namun cukup satu guncangan untuk
    jatuh. Secara nasional kelompok ini berjumlah 68,5 juta jiwa, jauh
    melampaui 24,06 juta penduduk yang tercatat miskin.
    """

    persen_miskin_2023: float = 9.14
    persen_miskin_2024: float = 8.32
    persen_miskin_2025: float = 7.60
    """Persentase penduduk miskin. Sumber: BPS. Angka 2025 dikutip Pemkab."""

    jumlah_penduduk_miskin_2024: int = 34_420
    jumlah_penduduk_miskin_2025: int = 31_660
    """Jiwa. Sumber: BPS. Angka 2025 sesuai yang dikutip pada proposal NADI."""

    @property
    def garis_kerentanan(self) -> float:
        """Garis kerentanan dalam rupiah per kapita per bulan.

        Nilai TURUNAN, bukan angka resmi BPS. Antarmuka wajib menandainya
        demikian agar tidak dikutip sebagai statistik resmi.
        """
        return self.garis_kemiskinan * self.pengali_garis_kerentanan

    # --- Wilayah ---
    jumlah_kecamatan: int = 9
    jumlah_pekon: int = 126
    jumlah_kelurahan: int = 5

    # --- Kondisi khusus yang tercatat ---
    backlog_rtlh: int = 1_700
    """Perkiraan unit rumah tidak layak huni yang belum tertangani.
    Sumber: Dinas Sosial Kabupaten Pringsewu, 2025."""

    kuota_rutilahu_apbd_tahunan: int = 80
    """Penerima bantuan rumah tidak layak huni dari APBD per tahun.
    Sumber: realisasi tahun anggaran 2025, Rp1,2 miliar untuk 80 keluarga.
    Perbandingan antara kuota 80 dan kebutuhan 1.700 inilah persoalan
    penetapan prioritas yang sesungguhnya."""

    catatan_keyakinan: str = (
        "Persentase penduduk miskin 2025 sebesar 7,60 persen dikutip dari "
        "pernyataan Pemkab, bukan dari publikasi BPS langsung. Garis "
        "kemiskinan memakai angka 2024 karena angka 2025 belum ditemukan."
    )


ACUAN = AcuanPringsewu()


# ===========================================================================
# PARAMETER PEMBANGKITAN
# ===========================================================================


@dataclass(frozen=True)
class ParameterGenerator:
    """Parameter proses pembangkitan data sintetis."""

    # -----------------------------------------------------------------
    # Ukuran dan waktu
    # -----------------------------------------------------------------
    jumlah_keluarga: int = 40_000
    """Banyaknya keluarga yang dibangkitkan.

    Nilai bawaan ini sekitar 54 persen dari 73.879 keluarga desil 1 sampai 5
    yang sebenarnya. Dipilih agar demo berjalan ringan di laptop tanpa
    kehilangan keragaman. Untuk mendekati keadaan sesungguhnya, setel nilai ini
    ke 73.879.
    """

    jumlah_gelombang: int = 6
    """Banyaknya putaran pemutakhiran data.

    Enam gelombang memberi cukup ruang untuk mempelajari perpindahan keadaan:
    gelombang nol sampai empat menjadi bahan pelatihan, gelombang lima menjadi
    penguji yang belum pernah dilihat model.
    """

    bulan_per_gelombang: int = 6
    """Jarak waktu antar-gelombang, mengikuti kelaziman pemutakhiran berkala."""

    tahun_awal: int = 2023
    bulan_awal: int = 3
    """Gelombang nol ditetapkan pada Maret, mengikuti waktu pencacahan Susenas."""

    benih_acak: int = 20260913
    """Benih pembangkit bilangan acak. Ditetapkan agar seluruh hasil dapat
    diulang persis - syarat agar angka evaluasi dapat diperiksa ulang oleh
    pihak lain."""

    # -----------------------------------------------------------------
    # Struktur pendapatan laten
    # -----------------------------------------------------------------
    # Pengeluaran per kapita dibentuk sebagai:
    #     log c = log(kemampuan permanen) + pengaruh sementara + guncangan
    # Kemampuan permanen sendiri terbagi dua: bagian yang dapat diterangkan
    # ciri-ciri teramati, dan bagian yang tidak.
    sd_kemampuan_tak_teramati: float = 0.34
    """Simpangan baku bagian kemampuan permanen yang TIDAK teramati model.

    Inilah pengatur utama seberapa sulit persoalan ini. Nilai nol berarti
    seluruh nasib keluarga dapat dibaca dari berkas data, dan model akan
    mencapai ketepatan yang mustahil di dunia nyata. Nilai 0,34 menempatkan
    kinerja model pada kisaran yang dilaporkan literatur penargetan kemiskinan.
    """

    sd_guncangan_sementara: float = 0.22
    """Simpangan baku ragam pengeluaran antar-periode yang murni acak.

    Mewakili panen yang kebetulan baik, pesanan dagangan yang kebetulan ramai,
    atau bulan yang kebetulan banyak pengeluaran. Tidak dapat diramalkan siapa
    pun, dan keberadaannya membuat sebagian perpindahan keadaan memang tidak
    mungkin diprediksi.
    """

    korelasi_antar_gelombang: float = 0.72
    """Seberapa kuat keadaan sebuah keluarga bertahan dari satu gelombang ke
    gelombang berikutnya. Nilai tinggi berarti kemiskinan bersifat menetap;
    nilai rendah berarti banyak keluarga keluar-masuk kemiskinan. Angka 0,72
    menghasilkan perpindahan sekitar sepuluh sampai lima belas persen per
    gelombang, sejalan dengan temuan kajian dinamika kemiskinan di Indonesia."""

    # -----------------------------------------------------------------
    # Guncangan
    # -----------------------------------------------------------------
    peluang_dasar_guncangan: float = 0.11
    """Peluang sebuah keluarga mengalami setidaknya satu guncangan per
    gelombang, sebelum disesuaikan menurut ciri keluarga."""

    pengali_guncangan_sektor_musiman: float = 1.7
    """Keluarga yang bergantung pada pertanian dan sektor musiman lebih sering
    terkena guncangan pendapatan."""

    pengali_guncangan_penyakit_kronis: float = 1.5
    pengali_guncangan_lansia: float = 1.3

    dampak_guncangan_ringan: float = -0.08
    dampak_guncangan_sedang: float = -0.20
    dampak_guncangan_berat: float = -0.42
    """Perubahan logaritma pengeluaran akibat guncangan menurut keparahannya.
    Guncangan berat memangkas pengeluaran sekitar sepertiga."""

    pemulihan_guncangan: float = 0.55
    """Bagian dampak guncangan yang pulih pada gelombang berikutnya. Sisanya
    menetap - inilah sebabnya satu peristiwa buruk dapat mengubah lintasan
    sebuah keluarga secara permanen."""

    # -----------------------------------------------------------------
    # Penargetan program dan kesalahannya
    # -----------------------------------------------------------------
    # Bagian ini sengaja dibuat TIDAK sempurna. Sistem yang dibangun untuk
    # menemukan ketidaksesuaian sasaran tidak dapat diuji pada data yang tidak
    # memiliki ketidaksesuaian. Besaran kesalahan di bawah mengikuti kisaran
    # yang dilaporkan kajian evaluasi penargetan bantuan sosial di Indonesia.
    galat_eksklusi: float = 0.22
    """Bagian keluarga yang layak namun tidak menerima program. Kesalahan jenis
    ini paling merugikan dan paling sulit terlihat, sebab yang terdampak tidak
    muncul di daftar mana pun."""

    galat_inklusi: float = 0.18
    """Bagian penerima yang sebenarnya tidak lagi memenuhi kriteria, umumnya
    karena keadaannya sudah membaik namun data belum dimutakhirkan."""

    kelambanan_kepesertaan: float = 0.88
    """Peluang keluarga yang menerima program pada satu gelombang tetap
    menerima pada gelombang berikutnya, terlepas dari perubahan keadaan.
    Kelambanan inilah sumber utama ketidaksesuaian sasaran di lapangan."""

    keterlambatan_desil_gelombang: int = 1
    """Berapa gelombang tertinggal desil kesejahteraan yang dipakai menetapkan
    sasaran. Menirukan kenyataan bahwa penetapan penerima selalu memakai
    potret keadaan yang sudah lewat."""

    sasaran_r2_pmt: float = 0.50
    """Daya jelas proxy means test terhadap pengeluaran sesungguhnya.

    Angka ini menentukan seberapa sulit persoalan yang dihadapi model, dan
    berpijak pada temuan lintas negara: sebagian besar proxy means test di
    negara berkembang memiliki daya jelas antara 0,40 dan 0,60. Dengan kata
    lain, sekitar separuh keragaman kesejahteraan antar-keluarga tetap tidak
    terjelaskan oleh penanda tak langsung.

    Menaikkan nilai ini akan membuat angka evaluasi tampak jauh lebih baik
    sekaligus membuatnya tidak berarti, sebab desil pada data sintetis lalu
    menjadi lebih tajam daripada desil DTSEN yang sesungguhnya.
    """

    peluang_salah_catat_desil: float = 0.08
    """Bagian keluarga yang desil tercatatnya keliru secara MENETAP.

    Ini sumber kesalahan sasaran yang paling penting sekaligus paling sering
    terlewat. Kuota yang terbatas dan data yang tertinggal menghasilkan
    kesalahan yang berpindah-pindah - keluarga terlewat pada satu periode lalu
    terjangkau pada periode berikutnya. Sebaliknya, kekeliruan pencatatan
    bersifat menetap: keluarga yang tercatat pada desil yang keliru akan
    terlewat pada setiap penetapan, tahun demi tahun, tanpa pernah muncul di
    daftar mana pun untuk diperiksa.

    Penyebabnya beragam dan semuanya nyata: pencacah tidak menemui keluarga
    tersebut lalu memakai perkiraan tetangga, keluarga menolak didata,
    pendataan dilakukan ketika keadaan sedang membaik sesaat, atau data
    tertukar. Menemukan keluarga semacam inilah alasan utama sistem penilaian
    risiko dibangun - sebab merekalah yang tidak akan pernah ditemukan dengan
    cara memeriksa daftar penerima.
    """

    bias_desil_ke_atas: float = 0.68
    """Bagian kekeliruan pencatatan yang mengarah ke atas, yakni keluarga
    tercatat lebih sejahtera daripada keadaan sesungguhnya sehingga terlewat
    dari program. Sisanya mengarah ke bawah dan menghasilkan penerima yang
    sebenarnya tidak berhak.

    Arah ke atas dibuat lebih sering karena memang begitu kecenderungannya:
    keluarga yang merasa dirugikan penetapan akan mengajukan sanggahan, dan
    sanggahan itu memperbaiki catatan. Keluarga yang diuntungkan tidak
    mengajukan apa-apa, sehingga kekeliruannya bertahan lebih lama.
    """

    # -----------------------------------------------------------------
    # Kualitas data
    # -----------------------------------------------------------------
    peluang_data_kedaluwarsa: float = 0.16
    """Bagian keluarga yang datanya tidak dimutakhirkan pada satu gelombang."""

    peluang_data_tidak_lengkap: float = 0.09

    peluang_masalah_dokumen: float = 0.010
    """Peluang seorang ANGGOTA tidak memiliki dokumen kependudukan yang sah.

    Perhatikan satuannya: peluang ini berlaku per orang, bukan per keluarga.
    Dengan rata-rata 3,3 anggota, peluang sebuah keluarga memiliki setidaknya
    satu anggota bermasalah menjadi sekitar tiga persen, lalu naik menjadi
    sekitar empat persen setelah ditambah bayi yang belum berakta kelahiran.
    Angka per keluarga inilah yang sebanding dengan laporan lapangan.
    """

    peluang_inkonsistensi_data: float = 0.02
    """Bagian keluarga dengan isian yang saling bertentangan, misalnya
    memiliki mobil namun berdaya listrik 450 VA. Sengaja disisipkan agar
    penandaan inkonsistensi memiliki sasaran nyata untuk ditemukan."""

    # -----------------------------------------------------------------
    # Privasi
    # -----------------------------------------------------------------
    pergeseran_koordinat_meter: float = 250.0
    """Radius pergeseran acak koordinat sebelum disimpan.

    Cukup untuk analisis sebaran dan pengelompokan wilayah, tidak cukup untuk
    menunjuk satu rumah. Diterapkan walaupun data ini sintetis, sebab kode yang
    sama kelak berjalan pada data sesungguhnya - kebiasaan yang dibangun sejak
    awal jauh lebih dapat diandalkan daripada penyesuaian yang ditambahkan
    belakangan."""


PARAMETER = ParameterGenerator()


# ===========================================================================
# SEBARAN CIRI KELUARGA
# ===========================================================================


@dataclass(frozen=True)
class SebaranKeluarga:
    """Sebaran ciri keluarga, dicondongkan sesuai keadaan desil bawah.

    Perlu ditegaskan: angka-angka ini menggambarkan keluarga desil 1 sampai 5,
    bukan seluruh penduduk Pringsewu. Kelompok inilah ruang kerja sistem ini,
    dan keadaannya memang berbeda dari rata-rata kabupaten.
    """

    # --- Susunan keluarga ---
    peluang_jumlah_anggota: tuple[float, ...] = (
        0.10,  # 1 orang
        0.21,  # 2 orang
        0.26,  # 3 orang
        0.23,  # 4 orang
        0.12,  # 5 orang
        0.05,  # 6 orang
        0.02,  # 7 orang
        0.01,  # 8 orang
    )
    """Sebaran jumlah anggota keluarga, menghasilkan rata-rata sekitar 3,34 jiwa.

    Acuannya adalah 451.586 jiwa berbanding 144.262 kartu keluarga menurut
    DTSEN 2026, yakni 3,13 jiwa per keluarga untuk seluruh penduduk. Nilai di
    sini sedikit lebih tinggi karena keluarga desil bawah cenderung beranggota
    lebih banyak - salah satu sebab pengeluaran per kapitanya rendah.
    """

    peluang_kk_perempuan: float = 0.155
    """Bagian keluarga dengan kepala keluarga perempuan. Cenderung lebih tinggi
    pada desil bawah dibanding rata-rata penduduk."""

    umur_kk_rerata: float = 47.0
    umur_kk_sd: float = 13.5

    # --- Pendidikan kepala keluarga ---
    # Urutan mengikuti kode PendidikanTertinggi 1 sampai 8.
    peluang_pendidikan_kk: tuple[float, ...] = (
        0.05,  # tidak sekolah
        0.11,  # tidak tamat SD
        0.36,  # SD
        0.26,  # SMP
        0.18,  # SMA
        0.02,  # diploma
        0.02,  # sarjana
        0.00,  # pascasarjana
    )

    # --- Sektor pekerjaan kepala keluarga ---
    # Pringsewu bercorak pertanian; singkong menjadi komoditas utama yang
    # sedang didorong menjadi tepung mocaf.
    peluang_sektor_kk: dict[int, float] = field(
        default_factory=lambda: {
            1: 0.29,  # padi dan palawija termasuk singkong
            2: 0.05,  # hortikultura
            3: 0.06,  # perkebunan
            4: 0.02,  # perikanan
            5: 0.04,  # peternakan
            8: 0.06,  # industri pengolahan
            10: 0.10,  # konstruksi
            11: 0.16,  # perdagangan
            12: 0.03,  # rumah makan
            13: 0.06,  # transportasi
            18: 0.02,  # jasa pemerintahan
            19: 0.06,  # jasa lainnya
            20: 0.05,  # tidak bekerja
        }
    )

    # --- Kesehatan ---
    peluang_penyakit_kronis_per_dewasa: float = 0.075
    peluang_disabilitas_per_orang: float = 0.021
    peluang_gizi_bermasalah_per_balita: float = 0.17
    """Sejalan dengan prevalensi masalah gizi balita pada kelompok
    berpenghasilan rendah."""

    peluang_hamil_per_perempuan_usia_subur: float = 0.055

    # --- Jaminan kesehatan ---
    peluang_jkn_desil_bawah: float = 0.78
    peluang_jkn_desil_atas: float = 0.62
    """Cakupan jaminan kesehatan justru lebih tinggi pada desil terbawah karena
    iurannya ditanggung pemerintah. Kelompok tepat di atas garis kemiskinan
    sering terlewat - terlalu mampu untuk ditanggung, terlalu tidak mampu untuk
    membayar sendiri. Celah inilah yang penting ditemukan sistem ini."""


SEBARAN = SebaranKeluarga()


__all__ = [
    "ACUAN",
    "PARAMETER",
    "SEBARAN",
    "AcuanPringsewu",
    "ParameterGenerator",
    "SebaranKeluarga",
]
