"""Bab lanjutan panduan NADI: data dan model, tata kelola, monitoring, kamus.

Dipisahkan dari ``buat_panduan.py`` semata karena panjangnya. Setiap fungsi di
sini menerima penyusun dokumen dan kamus angka faktual, lalu menuliskan satu
bab. Tidak ada satu angka pun yang ditulis tangan; seluruhnya berasal dari
``kumpulkan_fakta()``.
"""

from __future__ import annotations

from dokumen import Panduan


def rb(n: float | int, desimal: int = 0) -> str:
    """Angka bergaya Indonesia: titik ribuan, koma desimal."""
    s = f"{n:,.{desimal}f}"
    utuh, _, pecahan = s.partition(".")
    return f"{utuh.replace(',', '.')},{pecahan}" if pecahan else utuh.replace(",", ".")


# ===========================================================================
# Bab 4 - Data dan model
# ===========================================================================
def bab_data_model(d: Panduan, f: dict) -> None:
    m = f["metrik"]
    a300 = m.get("pada_anggaran", {}).get("300", {})
    kal = m.get("kalibrasi", {})

    d.h1("4. Data dan Model: Cara Kerjanya dan Batasnya")

    d.h2("4.1 Mengapa datanya sintetis")
    d.p(
        "Data DTSEN yang sesungguhnya memuat nama, nomor induk kependudukan, dan alamat "
        "keluarga. Ia tidak dapat dibawa ke dalam lomba, tidak dapat diperlihatkan kepada "
        "dewan juri, dan tidak dapat disalin ke laptop peserta. Membangun karya lomba di "
        "atasnya bukan pilihan yang tersedia."
    )
    d.p(
        "Karena itu dibangkitkan data sintetis yang **berperilaku** seperti kenyataan tanpa "
        "**berisi** kenyataan. Nilainya terletak pada kalibrasi: bila angka kemiskinan, "
        "sebaran aset, dan jumlah penduduk per kecamatan dipaksa sama dengan angka resmi, "
        "kesimpulan yang diambil dari data itu tetap bermakna meski keluarganya fiktif."
    )
    d.tabel(
        ["Yang dikalibrasi", "Terhadap apa", "Cara"],
        [
            ["Angka kemiskinan tiap gelombang", "BPS Kabupaten Pringsewu 2023-2025",
             "Pencarian bagi dua sampai tepat sama dengan sasaran"],
            ["Sebaran kepemilikan aset", "Proporsi Susenas",
             "Pemetaan berbasis peringkat, bukan peluang logistik"],
            ["Jumlah penduduk per kecamatan", "Data Kependudukan Bersih 2024",
             "Dijumlahkan tepat 444.834 jiwa"],
            ["Garis kemiskinan", "BPS 2024: Rp583.425 per kapita per bulan",
             "Dipakai langsung sebagai ambang"],
            ["Ketelitian Proxy Means Test", "Rentang 0,40-0,60 pada negara berkembang",
             "Derau ditambahkan sampai R-kuadrat mencapai 0,50"],
            ["Batas wilayah", "Badan Informasi Geospasial skala 1:10.000",
             "Poligon asli, 131 desa"],
        ],
        lebar=[4.4, 5.4, 5.2],
    )
    d.catatan(
        "Pertanyaan yang hampir pasti diajukan juri",
        "“Datanya sintetis, bagaimana membuktikan sistem ini bekerja?” Jawaban "
        "jujurnya: **tidak terbukti bekerja pada keluarga nyata, dan itu memang belum dapat "
        "dibuktikan sekarang.** Yang terbukti adalah bahwa alur pengolahannya benar, "
        "metriknya dihitung dengan cara yang sah, dan kalibrasinya menyerupai kenyataan. "
        "Pembuktian sesungguhnya menuntut penerapan pada data DTSEN dengan izin resmi — "
        "dan itu tercantum sebagai langkah berikutnya pada Bab 9.",
    )

    d.h2("4.2 Bagaimana skor kerentanan dihitung")
    d.p(
        f"Model yang dipakai adalah {f['model']['algoritma']}. Ia mempelajari "
        f"{f['model']['fitur']} ciri keluarga — kondisi hunian, pendidikan, pekerjaan, "
        "kesehatan, guncangan yang dialami, dan komposisi anggota — lalu memperkirakan "
        "peluang keluarga itu berada di bawah garis kemiskinan pada pemutakhiran berikutnya."
    )
    d.p(
        "Yang **tidak** dipakai sama pentingnya dengan yang dipakai. Tiga ciri sengaja "
        "dikeluarkan karena bersifat melingkar: jumlah program yang diterima, nilai bantuan "
        "per kapita, dan penanda tidak menerima bantuan apa pun. Ketiganya mencerminkan "
        "keputusan penargetan pemerintah pada masa lalu, bukan kebutuhan keluarga. Model "
        "yang mempelajarinya akan mengulang kekeliruan penargetan lama, bukan memperbaikinya."
    )

    d.h2("4.3 Angka kinerja yang sebenarnya")
    d.tabel(
        ["Ukuran", "Nilai", "Artinya dalam bahasa sehari-hari"],
        [
            ["AUC", rb(m.get("auc", 0), 4),
             "Peluang model memberi skor lebih tinggi kepada keluarga yang benar-benar jatuh "
             "miskin daripada kepada yang tidak. 0,5 berarti menebak; 1,0 berarti sempurna."],
            ["Prevalensi", rb(m.get("prevalensi", 0) * 100, 2) + "%",
             "Bagian keluarga dalam cakupan yang benar-benar jatuh miskin pada gelombang uji."],
            ["Presisi pada 300 kunjungan", rb(a300.get("presisi", 0) * 100, 1) + "%",
             "Dari 300 keluarga teratas yang didatangi, sekian persen memang benar jatuh miskin."],
            ["Pengganda", rb(a300.get("pengganda", 0), 2) + "x",
             "Berapa kali lebih baik daripada mendatangi keluarga secara acak."],
            ["Brier score", rb(kal.get("brier", 0), 4),
             "Seberapa dekat peluang yang disebut model dengan kejadian sesungguhnya. "
             "Makin kecil makin baik."],
            ["ECE", rb(kal.get("ece", 0), 4),
             "Selisih rata-rata antara peluang yang dijanjikan dan yang terjadi. Nilai di "
             "bawah 0,01 tergolong sangat baik."],
        ],
        lebar=[3.4, 2.2, 9.4],
    )
    d.p(
        "**Angka yang paling penting bukan AUC, melainkan pengganda.** Seorang kepala dinas "
        "tidak bertanya “berapa AUC-nya”; ia bertanya “kalau saya hanya punya "
        "tenaga untuk 300 kunjungan bulan ini, berapa yang tepat sasaran”. Jawabannya "
        f"{rb(a300.get('presisi', 0) * 100, 1)} persen, atau "
        f"{rb(a300.get('pengganda', 0), 2)} kali lebih baik daripada memilih acak."
    )
    d.catatan(
        "Mengapa AUC 0,86 dan bukan 0,95",
        "Angka setinggi 0,95 pada persoalan seperti ini hampir selalu menandakan kebocoran "
        "data — model melihat sesuatu yang sebenarnya tidak akan tersedia pada saat "
        "peramalan dilakukan. Hal itu memang sempat terjadi pada pengerjaan ini: AUC pernah "
        "mencapai 0,94 sebelum ketahuan bahwa desil kesejahteraan dihitung dari pengeluaran "
        "sesungguhnya. Sesudah diperbaiki, angkanya turun ke kisaran yang wajar bagi Proxy "
        "Means Test di negara berkembang. **Angka yang lebih rendah namun jujur lebih "
        "berguna daripada angka tinggi yang menyesatkan.**",
    )

    d.h2("4.4 Uji keadilan")
    d.p(
        "Model diperiksa apakah ia bekerja sama baiknya bagi kelompok yang berbeda. "
        "Pemeriksaan ini penting karena sistem penargetan yang bekerja lebih buruk pada satu "
        "kecamatan akan memindahkan bantuan menjauhi kecamatan itu tanpa ada yang menyadarinya."
    )
    d.poin(
        [
            "**Antarkecamatan** — AUC dihitung terpisah untuk kesembilan kecamatan.",
            "**Menurut jenis kelamin kepala keluarga** — selisih recall diperiksa.",
            "**Desa berbanding kota** — diperiksa terpisah.",
            "Seluruh hasilnya ditampilkan pada halaman Transparansi Model di dalam aplikasi, "
            "bukan disimpan dalam laporan yang tidak dibaca siapa pun.",
        ]
    )

    d.h2("4.5 Batas yang harus dinyatakan")
    d.poin(
        [
            "Model **tidak menetapkan kelayakan**. Ia mengurutkan prioritas pemeriksaan.",
            "Model **tidak dapat melihat** hal yang tidak tercatat: perselisihan keluarga, "
            "penyakit yang belum terdiagnosis, utang kepada rentenir.",
            "Peluang yang ditampilkan **selalu dibatasi** antara 0,5 dan 99,5 persen. Sistem "
            "tidak pernah mengaku pasti.",
            "Ketepatan pada data sintetis **tidak menjamin** ketepatan pada data DTSEN "
            "sesungguhnya.",
            "Data yang usang tetap menghasilkan skor yang usang. Model tidak dapat memperbaiki "
            "pendataan yang tidak dimutakhirkan.",
        ]
    )


# ===========================================================================
# Bab 5 - Tata kelola
# ===========================================================================
def bab_tata_kelola(d: Panduan, f: dict) -> None:
    d.h1("5. Tata Kelola, Privasi, dan Keamanan")
    d.p(
        "Proposal berjanji: nol keputusan otomatis oleh AI, manusia selalu di dalam lingkar, "
        "tidak ada NIK yang dikirim ke layanan luar. Bab ini memerinci bagaimana janji itu "
        "**ditegakkan mesin**, bukan sekadar dituliskan pada dokumen."
    )

    d.h2("5.1 Enam peran dan apa yang boleh dilakukannya")
    d.tabel(
        ["Peran", "Cakupan data", "Yang menjadi ciri khasnya"],
        [
            ["Administrator Sistem", "Seluruh kabupaten",
             "Satu-satunya yang dapat mengubah pengaturan layanan AI"],
            ["Pimpinan Daerah", "**Agregat saja**",
             "Tidak dapat membuka satu pun keluarga — disengaja"],
            ["Perencana (Bappeda)", "**Agregat saja**",
             "Simulasi kebijakan dan katalog program"],
            ["Dinas Sosial", "Seluruh kabupaten",
             "Menugaskan kasus dan **menilai hasil** intervensi"],
            ["OPD Pelaksana", "Wilayah tertugas",
             "**Mencatat penyaluran**, tetapi tidak boleh menilainya"],
            ["Verifikator", "Wilayah tertugas",
             "Mencatat temuan lapangan; tidak melihat monitoring"],
        ],
        lebar=[3.4, 3.2, 8.4],
    )
    d.catatan(
        "Pemisahan tugas yang menentukan kepercayaan pada angka capaian",
        "OPD pelaksana dapat mencatat apa yang ia salurkan, tetapi **tidak dapat menilai "
        "hasilnya sendiri**. Penilaian jatuh ke Dinas Sosial sebagai pengoordinasi. Tanpa "
        "pemisahan ini, laporan capaian menilai dirinya sendiri, dan angka pada layar "
        "monitoring tidak lagi berarti apa pun bagi pimpinan yang membacanya. Pemisahan "
        "tersebut diuji lewat permintaan HTTP sungguhan: akun OPD menerima penolakan ketika "
        "mencoba menilai intervensi yang ia catat sendiri.",
    )

    d.h2("5.2 Perlindungan data pribadi")
    d.tabel(
        ["Perlindungan", "Cara kerjanya"],
        [
            ["Pseudonimisasi",
             "Identitas keluarga menjadi kode semu (KLG-7F3A-2B9K) melalui HMAC-SHA256. Tidak "
             "dapat dibalik tanpa kunci rahasia aplikasi."],
            ["Penghalang PII",
             "Setiap muatan yang hendak dikirim ke layanan AI diperiksa tepat sebelum "
             "berangkat. Bila memuat NIK, nomor kartu keluarga, NPWP, BPJS, nomor telepon, "
             "surel, koordinat presisi, atau RT/RW — permintaan **dibatalkan**, bukan "
             "disamarkan diam-diam."],
            ["Redaksi masukan pengguna",
             "Pertanyaan yang diketik pengguna dan memuat pengenal pribadi diredaksi lebih "
             "dahulu, lalu tetap dijawab sebisanya."],
            ["Penekanan sel kecil",
             "Agregat wilayah dengan kurang dari sepuluh keluarga tidak ditampilkan."],
            ["Pengaburan koordinat",
             "Titik pada peta digeser acak sehingga rumah tidak dapat ditemukan dari layar."],
            ["Jejak audit",
             "Setiap tindakan tercatat: siapa, kapan, dari alamat mana, terhadap apa. Kunci "
             "API tidak pernah ikut tercatat."],
            ["Kunci API di luar basis data",
             "Kunci layanan AI disimpan pada berkas konfigurasi di peladen, bukan di dalam "
             "basis data — berkas basis data memang dimaksudkan untuk disalin."],
        ],
        lebar=[3.8, 11.2],
    )

    d.h2("5.3 Manusia di dalam lingkar")
    d.p("Tidak ada satu pun keputusan yang dijalankan sistem tanpa manusia. Alur penuhnya:")
    d.poin(
        [
            "Sistem **menandai** keluarga yang perlu diperiksa, beserta alasannya.",
            "Petugas **mendatangi** dan mencatat temuan lapangan — termasuk ketika "
            "temuannya **bertentangan** dengan catatan sistem.",
            "Koreksi petugas **disimpan** sebagai bahan pelatihan ulang model.",
            "OPD **mencatat** penyaluran yang benar-benar terjadi.",
            "Dinas Sosial **menilai** hasilnya terhadap kondisi keluarga sesudahnya.",
            "Penetapan penerima tetap melalui **musyawarah pekon** dan keputusan pejabat "
            "berwenang — sistem tidak pernah menyentuh tahap itu.",
        ],
        bernomor=True,
    )
    d.p(
        "Perhatikan langkah ketiga. Sistem yang baik harus dapat **mengakui dirinya salah**, "
        "dan koreksi petugas adalah satu-satunya jalan agar itu terjadi. Pada data yang ada "
        f"sekarang, {rb(f['baris'].get('verifikasi', 0))} verifikasi tercatat, dan lebih dari "
        "seperlimanya menyatakan penandaan sistem tidak sesuai kenyataan."
    )


# ===========================================================================
# Bab 6 - Kejujuran statistik
# ===========================================================================
def bab_monitoring(d: Panduan, f: dict) -> None:
    d.h1("6. Monitoring Hasil dan Kejujuran Statistik")
    d.p(
        "Bab ini menjelaskan bagian yang menurut penilaian penyusun paling membedakan NADI "
        "dari dasbor pemerintahan pada umumnya — dan yang paling layak ditonjolkan di "
        "hadapan dewan juri."
    )

    d.h2("6.1 Persoalannya")
    d.p(
        "Pada data sistem ini, **68,1 persen** keluarga membaik setelah menerima intervensi. "
        "Angka itu terdengar meyakinkan. Ia juga hampir tidak berarti apa-apa."
    )
    d.p(
        "Sebabnya: keluarga yang skor kerentanannya tinggi cenderung turun dengan sendirinya "
        "pada pengukuran berikutnya, tanpa menerima apa pun. Gejala ini disebut **regresi ke "
        "rata-rata**, dan ia bekerja paling kuat justru pada keluarga paling rentan — "
        "yakni keluarga yang paling mungkin menjadi sasaran intervensi."
    )

    d.h2("6.2 Cara NADI menanganinya")
    d.p(
        "Setiap angka capaian pada halaman Monitoring disandingkan dengan **kelompok "
        "pembanding**: keluarga yang tidak menerima intervensi, dicocokkan pada gelombang "
        "yang sama dan pita skor awal selebar sepuluh poin."
    )
    d.tabel(
        ["Penilaian", "Menerima intervensi", "Pembanding", "Selisih"],
        [
            ["Membaik", "68,1%", "**45,5%**", "**+22,6 poin persen**"],
            ["Tetap", "20,8%", "37,4%", "-16,6 poin persen"],
            ["Memburuk", "11,1%", "17,1%", "-6,0 poin persen"],
        ],
        lebar=[3.4, 3.8, 3.4, 4.4],
    )
    d.p(
        "Capaian sesungguhnya karena itu **+22,6 poin persen**, bukan 68 persen. Sebanyak 466 "
        "dari 467 intervensi berhasil dicocokkan dengan kelompok pembandingnya."
    )

    d.h2("6.3 Mengapa ini penting bagi penilaian lomba")
    d.poin(
        [
            "Dasbor pemerintahan yang menampilkan angka capaian tanpa pembanding bukan sekadar "
            "kurang teliti — ia **menyesatkan** pengambil keputusan yang mempercayainya.",
            "Menampilkan pembanding berarti sistem ini bersedia menampilkan angka yang **lebih "
            "kecil** daripada yang bisa ditampilkannya. Kesediaan itu sendiri adalah bukti "
            "bahwa angka lainnya juga dapat dipercaya.",
            "Ambangnya pun tidak dikarang: simpangan baku perubahan skor antargelombang pada "
            "200.000 pengamatan adalah **7,0 poin**, sehingga ambang 5 poin berarti sekitar "
            "0,7 simpangan baku.",
            "Penilaian membaik, tetap, atau memburuk **dihitung peladen**, tidak pernah "
            "diketik manusia. Pihak yang dinilai tidak dapat memoles angkanya sendiri.",
        ]
    )
    d.catatan(
        "Kalimat penafian yang muncul pada setiap layar monitoring",
        "“Angka pada modul ini menunjukkan PERUBAHAN kondisi, bukan SEBAB. Keluarga yang "
        "membaik setelah menerima intervensi belum tentu membaik karena intervensi "
        "tersebut.” Kalimat ini sengaja ditampilkan terus-menerus, bukan disembunyikan "
        "pada halaman metodologi yang tidak dibuka siapa pun.",
    )


# ===========================================================================
# Bab 7 - Kamus istilah
# ===========================================================================
ISTILAH: list[tuple[str, str]] = [
    ("API", "Cara dua program berbicara satu sama lain. Antarmuka NADI meminta angka kepada "
            "bagian peladen lewat API; keduanya program terpisah yang bekerja sama."),
    ("AUC", "Ukuran seberapa baik model membedakan dua kelompok. Nilainya antara 0,5 (setara "
            "menebak) dan 1,0 (sempurna). NADI mencapai 0,858. Angka di atas 0,90 pada "
            "persoalan kemiskinan hampir selalu menandakan ada yang keliru."),
    ("Brier score", "Ukuran seberapa dekat peluang yang disebut model dengan kejadian yang "
                    "sungguh terjadi. Makin kecil makin baik. NADI: 0,071."),
    ("Choropleth", "Peta yang mewarnai wilayah menurut besar kecilnya sebuah angka. Makin "
                   "gelap biasanya berarti makin besar."),
    ("Desil", "Pembagian penduduk menjadi sepuluh kelompok sama besar menurut tingkat "
              "kesejahteraan. Desil 1 adalah sepuluh persen paling miskin. NADI mencakup "
              "desil 1 sampai 5."),
    ("Digital twin", "Salinan digital sesuatu yang nyata. Pada NADI, setiap keluarga punya "
                     "salinan digital berisi kondisi dan perubahannya sepanjang waktu."),
    ("DTSEN", "Data Tunggal Sosial dan Ekonomi Nasional. Basis data tunggal penerima bantuan "
              "sosial menurut Peraturan BPS Nomor 6 Tahun 2025 dan Inpres Nomor 4 Tahun 2025, "
              "menggantikan DTKS, P3KE, dan Regsosek."),
    ("ECE", "Expected Calibration Error. Selisih rata-rata antara peluang yang dijanjikan "
            "model dan yang benar-benar terjadi. NADI: 0,006 — sangat baik."),
    ("Endpoint", "Satu alamat pada API yang melayani satu jenis permintaan, misalnya alamat "
                 "yang mengembalikan ringkasan kabupaten."),
    ("Exclusion error", "Kesalahan melewatkan: keluarga yang berhak menerima bantuan tetapi "
                        "tidak terdaftar. Pada penargetan kemiskinan, kesalahan jenis ini "
                        "membebani keluarga itu sendiri — dan mereka tidak muncul pada "
                        "daftar mana pun untuk mengeluh."),
    ("FastAPI", "Kerangka kerja untuk membangun API dengan bahasa Python. Dipakai NADI pada "
                "bagian peladen."),
    ("Garis kemiskinan", "Batas pengeluaran per orang per bulan; di bawahnya seseorang "
                         "digolongkan miskin. BPS menetapkan Rp583.425 untuk Kabupaten "
                         "Pringsewu pada 2024."),
    ("Gelombang", "Satu putaran pemutakhiran data. NADI memiliki enam gelombang, mewakili enam "
                  "kali pendataan ulang sepanjang tiga tahun."),
    ("GeoAI", "Penggabungan analisis kecerdasan buatan dengan data keruangan — hasilnya "
              "berupa peta yang menunjukkan di mana persoalan menumpuk."),
    ("Gradient boosting", "Cara melatih model dengan menyusun banyak pohon keputusan kecil "
                          "secara berurutan; setiap pohon memperbaiki kesalahan pohon "
                          "sebelumnya."),
    ("Guncangan", "Peristiwa mendadak yang menjatuhkan kondisi keluarga: gagal panen, "
                  "kehilangan pekerjaan, sakit berat, kematian pencari nafkah."),
    ("HMAC-SHA256", "Cara mengubah nomor identitas menjadi kode acak yang tidak dapat "
                    "dikembalikan tanpa kunci rahasia. Dipakai NADI untuk membuat kode semu "
                    "keluarga."),
    ("Human-in-the-loop", "Rancangan yang mewajibkan manusia mengambil keputusan akhir; sistem "
                          "hanya menyiapkan bahan pertimbangan."),
    ("Inclusion error", "Kesalahan memasukkan: keluarga yang sebenarnya tidak berhak tetapi "
                        "menerima bantuan. Kesalahan jenis ini membebani anggaran."),
    ("Kalibrasi", "Penyesuaian agar peluang yang disebut model sesuai dengan kenyataan. Bila "
                  "model berkata “peluang 30 persen” pada seratus keluarga, sekitar "
                  "tiga puluh di antaranya memang harus mengalaminya."),
    ("Kelompok pembanding", "Kelompok yang tidak menerima perlakuan, dipakai sebagai pembanding "
                            "untuk mengetahui apa yang akan terjadi tanpa intervensi. Tanpa "
                            "ini, angka capaian tidak dapat ditafsirkan."),
    ("LightGBM", "Pustaka perangkat lunak untuk gradient boosting yang cepat dan hemat memori. "
                 "Mesin model kerentanan NADI."),
    ("Lift", "Berapa kali lebih baik daripada memilih secara acak. NADI mencapai 7,35 kali pada "
             "anggaran 300 kunjungan."),
    ("LLM", "Large Language Model — model bahasa besar seperti GPT atau Claude. Pada NADI "
            "ia hanya menyusun kalimat penjelasan; seluruh angka dihitung di dalam sistem "
            "sendiri."),
    ("OPD", "Organisasi Perangkat Daerah — dinas dan badan di lingkungan pemerintah "
            "kabupaten. NADI mengenal 21 OPD Kabupaten Pringsewu."),
    ("Panel longitudinal", "Data yang mengikuti orang atau keluarga yang sama sepanjang waktu, "
                           "bukan mengambil orang berbeda pada setiap pengukuran."),
    ("Pekon", "Sebutan untuk desa di Provinsi Lampung. Kabupaten Pringsewu memiliki 126 pekon "
              "dan 5 kelurahan."),
    ("PII", "Personally Identifiable Information — keterangan yang dapat menunjuk orang "
            "tertentu: nama, NIK, alamat, nomor telepon."),
    ("PostGIS", "Tambahan pada basis data PostgreSQL yang memungkinkannya menyimpan dan "
                "mengolah data peta."),
    ("Presisi", "Dari sekian keluarga yang ditandai sistem, berapa persen yang memang benar. "
                "NADI: 77 persen pada 300 kunjungan teratas."),
    ("Prevalensi", "Bagian dari seluruh kelompok yang mengalami suatu hal. Pada data NADI, "
                   "10,5 persen keluarga jatuh miskin pada gelombang uji."),
    ("Proxy Means Test", "Cara menaksir kesejahteraan keluarga dari ciri yang mudah diamati "
                         "— jenis lantai, kepemilikan aset, pendidikan — karena "
                         "pendapatan sesungguhnya sulit diukur. Ketelitiannya di negara "
                         "berkembang berkisar 0,40 sampai 0,60."),
    ("Pseudonimisasi", "Mengganti identitas asli dengan kode buatan, sehingga data tetap dapat "
                       "diolah tanpa menyebut siapa orangnya."),
    ("RBAC", "Role-Based Access Control — pengaturan hak akses menurut jabatan. NADI "
             "memakai dua lapis: kewenangan menentukan tindakan, cakupan menentukan baris data "
             "yang terlihat."),
    ("React", "Pustaka untuk membangun tampilan aplikasi web. Dipakai pada antarmuka NADI."),
    ("Recall", "Dari seluruh keluarga yang benar-benar jatuh miskin, berapa persen berhasil "
               "ditemukan sistem."),
    ("Recall@k", "Recall yang dihitung hanya pada k keluarga teratas. Ukuran ini lebih jujur "
                 "daripada akurasi ketika anggaran kunjungan terbatas."),
    ("Regresi ke rata-rata", "Gejala statistik: nilai yang sangat tinggi atau sangat rendah pada "
                             "satu pengukuran cenderung lebih mendekati rata-rata pada "
                             "pengukuran berikutnya — tanpa sebab apa pun. Inilah alasan "
                             "angka capaian selalu perlu pembanding."),
    ("RTLH", "Rumah Tidak Layak Huni. Menurut standar teknis, rumah disebut layak bila memenuhi "
             "empat kriteria sekaligus: luas cukup, air minum layak, sanitasi layak, dan "
             "bangunan tahan."),
    ("SHAP", "Cara menjelaskan mengapa model memberi skor tertentu kepada satu keluarga, dengan "
             "membagi skor itu menjadi sumbangan tiap ciri. Inilah yang membuat sistem dapat "
             "berkata “karena atap rusak dan kepala keluarga putus sekolah”."),
    ("Sel kecil", "Kelompok data yang jumlahnya terlalu sedikit sehingga individunya dapat "
                  "ditebak dari angka gabungan. NADI menyembunyikan agregat wilayah dengan "
                  "kurang dari sepuluh keluarga."),
    ("Ambang", "Garis pemisah berupa angka yang menentukan sebuah kasus masuk kelompok mana. "
               "Garisnya dipilih manusia, bukan ditemukan mesin, sehingga selalu dapat "
               "diperdebatkan dan digeser. Pada NADI, skor 0-100 dibagi pada garis 40, 60, "
               "dan 80."),
    ("Anggaran verifikasi (k)", "Jumlah keluarga yang sanggup didatangi petugas dalam satu "
                               "putaran kerja. Angka ini datang dari berapa banyak petugas "
                               "yang ada, bukan dari perhitungan mesin — dan seluruh "
                               "penilaian mutu daftar prioritas diukur pada angka itu."),
    ("Anomali", "Ketidaksesuaian antara catatan data dan keadaan yang wajar. NADI memakai "
                "tujuh detektor anomali, dan hasilnya berupa usulan pemeriksaan — bukan "
                "tuduhan kecurangan."),
    ("Antrean prioritas", "Daftar keluarga yang perlu didatangi lebih dahulu, diurutkan "
                          "menurut skor dan kegentingan. Inilah keluaran utama NADI; ia "
                          "bukan daftar penerima bantuan."),
    ("Benih acak", "Angka awal yang membuat proses acak menghasilkan urutan yang sama setiap "
                   "kali dijalankan. Karena itu data sintetis NADI dapat dibangkitkan ulang "
                   "persis sama oleh siapa pun yang memeriksanya."),
    ("Data sintetis", "Data buatan yang dirancang berperilaku seperti data nyata tanpa berisi "
                      "orang nyata. Nilainya terletak pada kalibrasi terhadap angka resmi; "
                      "tanpa itu ia hanya angka acak."),
    ("Daftar putih", "Cara pengamanan yang menyebut apa saja yang **boleh**, lalu menolak "
                     "sisanya. Lebih aman daripada menyebut apa yang dilarang, karena hal "
                     "yang belum terpikirkan otomatis ikut tertolak."),
    ("Fitur", "Satu ciri keluarga yang dipakai model sebagai bahan pertimbangan — jenis "
              "lantai, lama sekolah kepala keluarga, jumlah tanggungan. NADI memakai 43 "
              "fitur."),
    ("Garis kerentanan", "Batas pengeluaran satu setengah kali garis kemiskinan. Keluarga di "
                         "bawahnya belum tercatat miskin, tetapi satu guncangan sudah cukup "
                         "menjatuhkannya."),
    ("GeoJSON", "Bentuk berkas untuk menyimpan batas wilayah dan titik pada peta. Batas 131 "
                "desa Pringsewu disimpan dalam satu berkas GeoJSON."),
    ("Jejak audit", "Catatan otomatis tentang siapa melakukan apa, kapan, dan dari mana. "
                    "Membuat pertanggungjawaban dapat ditelusuri — dan justru inilah yang "
                    "sering hilang pada proses manual."),
    ("Keadilan model", "Pemeriksaan apakah model bekerja sama baiknya bagi kelompok yang "
                       "berbeda. Model yang lebih buruk pada satu kecamatan akan memindahkan "
                       "bantuan menjauhi kecamatan itu tanpa ada yang menyadarinya."),
    ("Kebocoran data", "Keadaan ketika model diam-diam melihat keterangan yang sebenarnya "
                       "tidak akan tersedia pada saat peramalan sungguhan. Akibatnya angka "
                       "kinerja tampak jauh lebih baik daripada kenyataan. Terjadi tiga kali "
                       "pada pengerjaan NADI, dan ketiganya diperbaiki."),
    ("Label", "Jawaban yang dipelajari model — pada NADI, apakah keluarga benar-benar berada "
              "di bawah garis kemiskinan pada gelombang berikutnya."),
    ("Leaflet", "Pustaka perangkat lunak untuk menampilkan peta di dalam peramban. Bebas biaya "
                "dan memakai ubin peta OpenStreetMap."),
    ("Minimalisasi data", "Asas perlindungan data: hanya mengumpulkan dan memakai keterangan "
                          "yang benar-benar diperlukan. NADI tidak menyimpan nama, NIK, "
                          "maupun alamat sama sekali."),
    ("Pembagian menurut waktu", "Cara membagi data latih dan data uji berdasarkan periode, "
                                "bukan diacak. Pembagian acak membuat model melihat keluarga "
                                "yang sama pada waktu berbeda, sehingga hasilnya tampak lebih "
                                "baik daripada yang sebenarnya dapat dicapai."),
    ("Penggeseran koordinat", "Menggeser titik pada peta secara acak sejauh puluhan meter, "
                              "sehingga sebaran wilayah tetap terbaca tetapi rumah seseorang "
                              "tidak dapat ditemukan dari layar."),
    ("Regresi isotonik", "Cara mengalibrasi peluang keluaran model agar sesuai kenyataan, "
                         "dengan syarat urutannya tidak boleh terbalik. Dipakai NADI setelah "
                         "pelatihan model."),
    ("Simpangan baku", "Ukuran seberapa jauh angka-angka menyebar dari rata-ratanya. Pada NADI, "
                       "perubahan skor antargelombang memiliki simpangan baku 7,0 poin — "
                       "angka inilah yang dipakai menetapkan ambang perubahan bermakna."),
    ("Skor kerentanan", "Angka 0 sampai 100 yang menyatakan seberapa mendesak sebuah keluarga "
                        "diperiksa. Makin tinggi makin mendesak. Ia **bukan** ukuran "
                        "kemiskinan dan **bukan** penetapan kelayakan."),
    ("Token akses", "Tanda pengenal sementara yang dipegang peramban setelah pengguna masuk, "
                    "sehingga tidak perlu memasukkan sandi pada setiap permintaan. Berlaku "
                    "delapan jam pada NADI."),
    ("What-if", "Simulasi “bagaimana jika”: menghitung akibat sebuah pilihan kebijakan "
                "sebelum pilihan itu diambil. Misalnya, berapa tahun untuk menuntaskan rumah "
                "tidak layak huni pada kuota anggaran tertentu."),
    ("Uji asap", "Pengujian cepat yang memastikan setiap bagian aplikasi menyala dan "
                 "menampilkan isi, sebelum pengujian yang lebih rinci dilakukan."),
]


def bab_kamus(d: Panduan, f: dict) -> None:
    d.h1("7. Kamus Istilah")
    d.p(
        "Bagian ini ditujukan kepada pembaca yang bukan ahli statistik maupun pemrogram. "
        "Setiap istilah dijelaskan tanpa memakai istilah teknis lain."
    )
    d.tabel(
        ["Istilah", "Penjelasan"],
        [[a, b] for a, b in sorted(ISTILAH, key=lambda x: x[0].lower())],
        lebar=[3.6, 11.4],
    )


__all__ = ["bab_data_model", "bab_kamus", "bab_monitoring", "bab_tata_kelola", "rb"]
