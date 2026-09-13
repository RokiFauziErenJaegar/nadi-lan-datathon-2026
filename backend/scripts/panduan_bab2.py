"""Bab 8-10 panduan NADI: penjelasan kepada panitia, celah, dan lampiran.

Bab-bab ini berbeda sifatnya dari bab teknis. Ia bukan menerangkan apa yang
dibangun, melainkan **apa yang harus dikatakan tentangnya** - dan sama
pentingnya, apa yang sebaiknya tidak dikatakan.

Nada seluruh bab ini sengaja berhati-hati. Sebuah karya lomba yang mengaku
lebih daripada yang dapat dibuktikannya akan runtuh pada pertanyaan lanjutan
pertama, dan kerugiannya jauh melampaui keuntungan kalimat yang terdengar
mengesankan. Setiap klaim di bawah dipilih karena ia dapat dipertahankan.
"""

from __future__ import annotations

from dokumen import Panduan
from panduan_bab import rb


# ===========================================================================
# Bab 8 - Apa yang harus dijelaskan kepada panitia
# ===========================================================================
def bab_penjelasan(d: Panduan, f: dict) -> None:
    d.h1("8. Apa yang Harus Dijelaskan kepada Panitia dan Dewan Juri")

    d.p(
        "Bab ini disusun untuk dipakai langsung: dibaca sebelum presentasi, dan dibuka "
        "kembali ketika pertanyaan datang. Susunannya mengikuti urutan yang paling mungkin "
        "muncul, bukan urutan kepentingan teknis."
    )

    d.h2("8.1 Kalimat pembuka yang paling menentukan")
    d.catatan(
        "Empat kalimat pertama",
        "“NADI tidak menetapkan siapa yang berhak menerima bantuan. Ia menyusun antrean "
        "prioritas pemeriksaan ketika jumlah petugas terbatas. Setiap keluarga pada antrean "
        "membawa alasan mengapa ia ada di sana, dinas mana yang berwenang, dan program apa "
        "yang mungkin cocok. Keputusan tetap pada musyawarah pekon dan pejabat berwenang.”",
    )
    d.p(
        "Kalimat itu perlu diucapkan **lebih dahulu**, sebelum satu pun layar ditunjukkan. "
        "Sebagian besar keberatan terhadap sistem penargetan berbasis kecerdasan buatan "
        "berakar pada kekhawatiran bahwa mesin mengambil alih keputusan. Menjawabnya sebelum "
        "ditanya mengubah seluruh nada penilaian selanjutnya."
    )

    d.h2("8.2 Apa yang sudah dikerjakan — urutan yang layak diceritakan")
    d.poin(
        [
            f"**Riset domain lebih dahulu.** {f['riset_berkas']} dokumen, "
            f"{rb(f['riset_kata'])} kata, disusun sebelum satu baris kode ditulis: skema "
            "DTSEN, katalog program, profil Pringsewu, metodologi kerentanan, dan lanskap "
            "sistem yang sudah ada di Indonesia dan mancanegara.",

            "**Keamanan dibangun sebelum fitur.** Berkas pertama yang ditulis adalah "
            "penghalang data pribadi, bukan halaman muka. Janji privasi pada proposal "
            "ditegakkan mesin sejak awal, bukan ditambahkan belakangan.",

            f"**Data sintetis berkalibrasi.** {rb(f['baris']['keluarga'])} keluarga, "
            f"{rb(f['baris']['anggota_keluarga'])} jiwa, enam gelombang pemutakhiran — "
            "dengan angka kemiskinan, sebaran aset, dan jumlah penduduk yang dipaksa sama "
            "dengan angka resmi BPS.",

            f"**Model yang diperiksa, bukan sekadar dilatih.** AUC "
            f"{rb(f['metrik'].get('auc', 0), 3)} setelah tiga kali kebocoran data ditemukan "
            "dan diperbaiki — termasuk sekali ketika AUC sempat mencapai 0,94 dan justru "
            "itulah yang menandakan ada yang salah.",

            "**Lingkar ditutup sampai hasil.** Kasus, verifikasi, penyaluran, penilaian "
            "hasil — dan penilaian itu selalu disandingkan dengan kelompok pembanding.",

            "**Diuji, bukan diasumsikan.** 61 kasus uji otomatis, kesebelas halaman diperiksa "
            "merender, matriks kewenangan diuji lewat permintaan HTTP sungguhan.",
        ]
    )

    d.h2("8.3 Sepuluh pertanyaan tersulit dan jawaban jujurnya")

    tanya_jawab = [
        (
            "Datanya sintetis. Bagaimana membuktikan sistem ini bekerja?",
            "Tidak terbukti bekerja pada keluarga nyata, dan itu memang belum dapat "
            "dibuktikan sekarang. Yang terbukti: alur pengolahannya benar, metriknya "
            "dihitung secara sah, dan kalibrasinya menyerupai kenyataan. Pembuktian "
            "sesungguhnya menuntut penerapan pada data DTSEN dengan izin resmi — dan "
            "itulah langkah berikutnya yang saya usulkan.",
        ),
        (
            "Apa bedanya dengan SEPAKAT milik Bappenas?",
            "SEPAKAT sudah menyediakan analisis, perencanaan, dan penganggaran sejak 2018, "
            "dan saya tidak mengklaim menggantikannya. Yang berbeda: SEPAKAT bekerja pada "
            "tingkat agregat wilayah, NADI bekerja pada tingkat keluarga; SEPAKAT menilai "
            "keadaan yang tercatat, NADI menilai arah perubahannya; dan NADI menutup lingkar "
            "sampai penilaian hasil intervensi. Keduanya dapat saling melengkapi, bukan "
            "saling meniadakan.",
        ),
        (
            "Bukankah ini mirip SyRI di Belanda, yang dilarang pengadilan?",
            "Pertanyaan yang tepat, dan perbedaannya justru menjelaskan seluruh rancangan "
            "NADI. SyRI dipakai untuk **mendeteksi kecurangan** dan menghasilkan keputusan "
            "yang merugikan warga, tanpa transparansi tentang cara kerjanya. NADI dipakai "
            "untuk **menemukan yang terlewat**, keluarannya berupa antrean pemeriksaan "
            "bukan keputusan, setiap skor disertai alasan yang dapat dibaca, dan tidak ada "
            "satu pun jalur di dalamnya yang dapat menghentikan bantuan siapa pun. "
            "Perbedaan arah kerugian itu yang menentukan.",
        ),
        (
            "Siapa yang bertanggung jawab bila sistem salah?",
            "Pejabat yang mengambil keputusan, sama seperti sekarang. Sistem ini tidak "
            "mengambil keputusan apa pun, sehingga tidak memindahkan tanggung jawab. Yang "
            "ditambahkannya justru **jejak audit**: setiap tindakan tercatat beserta "
            "pelakunya, sehingga pertanggungjawaban menjadi lebih mudah ditelusuri "
            "daripada pada proses manual.",
        ),
        (
            "Mengapa AUC hanya 0,86? Sistem lain mengklaim di atas 0,95.",
            "Karena 0,95 pada persoalan ini hampir selalu berarti kebocoran data. Saya "
            "sempat mencapai 0,94, lalu menemukan bahwa desil kesejahteraan dihitung dari "
            "pengeluaran sesungguhnya — sesuatu yang tidak akan tersedia pada saat "
            "peramalan sungguhan. Sesudah diperbaiki, angkanya turun ke kisaran yang wajar "
            "bagi Proxy Means Test di negara berkembang. Saya lebih memilih angka yang "
            "lebih rendah namun jujur.",
        ),
        (
            "Berapa biayanya bila diterapkan?",
            "Seluruh perangkat lunaknya bebas biaya lisensi: Python, PostgreSQL, React, "
            "OpenStreetMap. Biaya nyata ada pada tiga hal: peladen (dapat memakai server "
            "yang sudah dimiliki Diskominfo), layanan model bahasa (dapat diganti model "
            "lokal sehingga nol biaya sekaligus menjaga kedaulatan data), dan waktu "
            "petugas untuk verifikasi lapangan — yang sebenarnya sudah berjalan hari ini, "
            "hanya urutannya yang berubah.",
        ),
        (
            "Mengapa tidak memakai sistem yang sudah ada saja?",
            "Sistem yang ada memang tidak perlu diganti. Yang belum tersedia adalah "
            "penggabungan empat hal sekaligus: penilaian kerentanan yang melihat ke depan, "
            "penjelasan per keluarga, penugasan lintas OPD, dan penilaian hasil terhadap "
            "kelompok pembanding. NADI dirancang untuk mengambil masukan dari DTSEN, bukan "
            "menggantikannya.",
        ),
        (
            "Bagaimana bila petugas hanya menuruti daftar tanpa berpikir?",
            "Risiko itu nyata dan tidak dapat dihilangkan sepenuhnya oleh perangkat lunak. "
            "Yang dapat dilakukan sudah dilakukan: setiap kasus menampilkan alasannya "
            "sehingga petugas dapat menilai apakah alasan itu masuk akal; petugas dapat "
            "mencatat bahwa temuan lapangan **bertentangan** dengan sistem; dan koreksi itu "
            "disimpan sebagai bahan pelatihan ulang. Pada data yang ada, lebih dari "
            "seperlima penandaan ternyata tidak sesuai kenyataan — dan angka itu sengaja "
            "ditampilkan, bukan disembunyikan.",
        ),
        (
            "Apakah ini sudah dipakai petugas sungguhan?",
            "Belum. Ini prototipe yang berfungsi penuh, diuji secara teknis, tetapi belum "
            "pernah diuji oleh petugas di lapangan. Pengujian dengan petugas Dinas Sosial "
            "adalah langkah berikutnya yang paling saya butuhkan, dan saya tidak akan "
            "mengklaim kesiapan operasional sebelum itu dilakukan.",
        ),
        (
            "Apa yang paling Anda ragukan dari karya Anda sendiri?",
            "Tiga hal. Pertama, ketepatan pada data sintetis belum tentu bertahan pada data "
            "DTSEN sesungguhnya yang jauh lebih berantakan. Kedua, saya belum tahu apakah "
            "petugas lapangan menganggap penjelasan yang ditampilkan benar-benar berguna "
            "atau justru mengganggu. Ketiga, sistem ini menuntut pemutakhiran data yang "
            "teratur — dan bila pemutakhiran tidak terjadi, seluruh skornya menjadi usang "
            "tanpa ada yang menyadarinya.",
        ),
    ]
    # Diberi awalan "Pertanyaan" alih-alih nomor telanjang. Tanpa itu, "9." dan
    # "10." di dalam bab ini terbaca seperti nomor bab ketika dokumen dipindai
    # atau dibaca sekilas.
    for i, (t, j) in enumerate(tanya_jawab, 1):
        d.h3(f"Pertanyaan {i} — {t}")
        d.p(j)

    d.h2("8.4 Kalimat yang sebaiknya TIDAK diucapkan")
    d.tabel(
        ["Jangan katakan", "Sebabnya", "Katakan ini"],
        [
            ["“Belum ada yang memprediksi kemiskinan di Indonesia”",
             "Proxy Means Test yang dipakai DTSEN **memang** bersifat prediktif. Juri yang "
             "memahami bidang ini akan langsung mematahkannya.",
             "“Yang belum umum adalah penilaian arah perubahan antarwaktu pada tingkat "
             "keluarga.”"],
            ["“Belum ada koordinasi lintas OPD”",
             "SIMNANGKIS di DIY dan SIPINTER di Purbalingga sudah melakukannya.",
             "“Penugasan lintas OPD sudah ada di beberapa daerah; yang saya tambahkan adalah "
             "kaitannya dengan penilaian hasil.”"],
            ["“Akurasi sistem ini 86 persen”",
             "AUC bukan akurasi, dan menyebutnya begitu akan runtuh pada pertanyaan lanjutan.",
             "“Dari 300 keluarga teratas yang didatangi, 77 persen memang tepat sasaran — "
             "7,35 kali lebih baik daripada memilih acak.”"],
            ["“AI menentukan siapa yang berhak”",
             "Bertentangan dengan seluruh rancangan sistem, dan memancing keberatan etis "
             "yang sebenarnya tidak berlaku.",
             "“Sistem menyusun antrean pemeriksaan; penetapan tetap di musyawarah pekon.”"],
            ["“Sistem ini siap dipakai”",
             "Belum diuji petugas sungguhan dan masih berjalan di atas data sintetis.",
             "“Prototipe berfungsi penuh, siap diuji coba terbatas bersama Dinas Sosial.”"],
        ],
        lebar=[4.2, 5.6, 5.2],
    )


# ===========================================================================
# Bab 9 - Apa yang belum dibuat
# ===========================================================================
def bab_celah(d: Panduan, f: dict) -> None:
    d.h1("9. Apa yang Belum Dibuat, dan Mana yang Paling Menentukan")

    d.p(
        "Bab ini ditulis sejujur mungkin, termasuk tentang keterbatasan waktu. Batas akhir "
        "lomba adalah 13 September 2026. Bagi satu orang yang juga menjalankan tugas "
        "kedinasan sehari-hari, sisa waktu itu sangat sedikit — dan daftar di bawah "
        "disusun dengan kesadaran tersebut."
    )

    d.catatan(
        "Kaidah yang dipakai menyusun urutan",
        "Pekerjaan yang **menunjukkan** karya kepada juri selalu didahulukan atas pekerjaan "
        "yang **menambah** kemampuan karya. Aplikasi yang hebat namun tidak pernah terlihat "
        "berjalan akan kalah oleh aplikasi sederhana yang dipresentasikan dengan baik. Pada "
        "titik ini, NADI sudah lebih dari cukup dari sisi kemampuan; yang kurang adalah "
        "cara menyampaikannya.",
    )

    d.h2("9.1 Tiga yang harus dikerjakan lebih dahulu")
    d.tabel(
        ["Prioritas", "Pekerjaan", "Perkiraan waktu", "Mengapa ini yang pertama"],
        [
            ["**1**", "**Video demo**", "4-6 jam",
             "Proposal menjanjikannya. Tanpa video, ada kemungkinan nyata juri tidak pernah "
             "melihat sistem ini berjalan sama sekali — dan seluruh pekerjaan menjadi "
             "tidak terlihat. Ini satu-satunya butir yang bila terlewat dapat menggugurkan "
             "sisanya."],
            ["**2**", "**Bahan presentasi**", "5-8 jam",
             "Alur cerita menentukan penilaian lebih besar daripada kelengkapan fitur. "
             "Susun mengikuti satu keluarga: terdeteksi, diverifikasi, ditangani, dinilai "
             "hasilnya — bukan mengikuti daftar modul."],
            ["**3**", "**Akses daring untuk juri**", "4-8 jam",
             "Proposal menyebut “aplikasi web MVP yang dapat diakses dewan juri”. "
             "Sekarang aplikasi hanya berjalan lokal. Sistem sudah dibangun siap-pindah — "
             "cukup mengganti alamat basis data — tetapi pemindahannya belum dikerjakan."],
        ],
        lebar=[1.6, 3.4, 2.4, 7.6],
    )

    d.h2("9.2 Berikutnya, bila waktu masih ada")
    d.tabel(
        ["Pekerjaan", "Waktu", "Dampak", "Catatan"],
        [
            ["Panduan pengguna bergambar", "3-4 jam", "Sedang",
             "Tangkapan layar tiap modul dengan keterangan. Menunjukkan sistem memang dapat "
             "dipakai orang lain, bukan hanya penyusunnya."],
            ["Ekspor laporan dari aplikasi", "4-6 jam", "Sedang",
             "Kepala dinas membutuhkan berkas yang dapat dilampirkan pada nota dinas. "
             "Fitur kecil dengan nilai praktis besar."],
            ["Menghubungkan empat titik akhir yang menganggur ke layar", "3-5 jam", "Sedang",
             "Penugasan kasus ke OPD yang paling terasa: tanpa itu, alur dari deteksi ke "
             "pelaksana masih terputus di antarmuka meski lengkap di API."],
            ["Perapian tampilan pada layar kecil", "3-5 jam", "Sedang",
             "Juri mungkin membuka dari telepon genggam. Sudah dapat dibuka, belum rapi "
             "sepenuhnya."],
            ["Uji coba dengan petugas Dinas Sosial", "1-2 minggu", "**Tinggi**",
             "Paling menaikkan kredibilitas, tetapi menuntut koordinasi antarinstansi. "
             "Bila hendak dikejar, permohonannya harus dikirim **hari ini juga**."],
            ["Surat dukungan instansi", "1-2 minggu", "**Tinggi**",
             "Menunjukkan karya ini bukan latihan pribadi melainkan menjawab kebutuhan "
             "nyata daerah. Bergantung pada birokrasi, bukan pada pengerjaan."],
        ],
        lebar=[4.2, 1.8, 1.8, 7.2],
    )

    d.h2("9.3 Yang sebaiknya TIDAK dikejar sekarang")
    d.tabel(
        ["Pekerjaan", "Sebabnya"],
        [
            ["Penerapan pada data DTSEN sungguhan",
             "Menuntut izin resmi, perjanjian kerahasiaan, dan penilaian dampak perlindungan "
             "data. Tidak mungkin selesai dalam 18 hari, dan mengerjakannya setengah jalan "
             "justru menimbulkan risiko hukum."],
            ["Integrasi langsung dengan SIKS-NG atau SEPAKAT",
             "Tidak ada akses antarmuka resmi yang tersedia bagi peserta perorangan. Cukup "
             "sampaikan sebagai rencana, bukan sebagai janji."],
            ["Menambah modul baru",
             "Sepuluh modul sudah melampaui delapan yang dijanjikan. Modul kesebelas tidak "
             "menambah nilai sebanyak satu video yang bagus, dan berisiko merusak yang sudah "
             "berjalan."],
            ["Menulis ulang bagian yang sudah berfungsi",
             "Setiap penulisan ulang menjelang batas waktu adalah taruhan yang tidak "
             "sebanding hasilnya."],
        ],
        lebar=[4.6, 10.4],
    )

    d.h2("9.4 Yang perlu dinyatakan sebagai keterbatasan, bukan disembunyikan")
    d.poin(
        [
            "Belum diuji oleh petugas lapangan yang sesungguhnya.",
            "Berjalan di atas data sintetis; ketepatannya pada data DTSEN belum diketahui.",
            "Belum terhubung ke sistem pemerintahan mana pun.",
            "Belum melalui penilaian dampak perlindungan data pribadi secara resmi.",
            "Copilot bergantung pada layanan luar bila ingin berbahasa luwes — meski "
            "seluruh angka tetap dihitung lokal dan model lokal dapat dipakai.",
            "**Empat titik akhir sudah dibangun namun belum terhubung ke antarmuka**: "
            "penugasan kasus ke OPD (`POST /antrean/{kode}/tugaskan`), simulasi dana desa, "
            "riwayat versi model, dan pohon wilayah. Kesepuluh modul berjalan, tetapi "
            "sebagian fungsinya baru dapat dipakai lewat API.",
            "**Empat kewenangan terdaftar namun belum menjaga satu pun rute**: "
            "`baca:jejak_audit`, `jalankan:ekspor`, `admin:program`, `admin:pengguna`. "
            "Kerangkanya sudah ada, layarnya belum.",
        ]
    )
    d.p(
        "Menyebut keterbatasan sendiri di hadapan juri hampir selalu menguatkan, bukan "
        "melemahkan. Ia menandakan penyusunnya mengetahui batas karyanya — dan juri yang "
        "berpengalaman akan menemukan batas itu dengan atau tanpa diberi tahu."
    )


# ===========================================================================
# Bab 10 - Lampiran
# ===========================================================================
def bab_lampiran(d: Panduan, f: dict) -> None:
    d.h1("10. Lampiran")

    d.h2("10.1 Cara menjalankan aplikasi")
    d.p(
        "Klik dua kali berkas **JALANKAN-NADI.bat** pada folder proyek. Skrip itu memeriksa "
        "setiap prasyarat lebih dahulu, hanya mengerjakan yang belum ada, lalu membuka "
        "peramban. Menjalankannya untuk kedua kali langsung membuka aplikasi dalam hitungan "
        "detik."
    )
    d.kode(
        "JALANKAN-NADI.bat            # sekali klik, semua otomatis\n"
        "\n"
        "# atau, bila ingin melangkah satu per satu:\n"
        "python backend/scripts/siapkan_data.py      # bangun basis data sintetis\n"
        "python backend/scripts/latih_model.py       # latih dan nilai model\n"
        "python backend/scripts/deteksi_kasus.py     # bentuk antrean kasus\n"
        "python backend/scripts/seed_intervensi.py   # isi riwayat intervensi\n"
        "cd backend && python -m uvicorn nadi.main:app --port 8000"
    )

    d.h2("10.2 Akun untuk mencoba")
    d.tabel(
        ["Nama pengguna", "Sandi", "Peran", "Yang menarik untuk dicoba"],
        [
            ["admin", "NadiAdmin#2026", "Administrator", "Halaman Pengaturan AI"],
            ["bupati", "NadiPimpinan#2026", "Pimpinan Daerah",
             "Coba buka satu keluarga — sistem akan menolak"],
            ["bappeda", "NadiPerencana#2026", "Perencana", "Simulasi kebijakan"],
            ["dinsos", "NadiDinsos#2026", "Dinas Sosial", "Antrean kasus dan monitoring"],
            ["pupr", "NadiPupr#2026", "OPD Pelaksana",
             "Coba nilai hasil intervensi — sistem akan menolak"],
            ["verifikator", "NadiVerif#2026", "Verifikator",
             "Hanya melihat wilayah tugasnya sendiri"],
        ],
        lebar=[3.0, 3.4, 3.0, 5.6],
    )
    d.catatan(
        "Dua percobaan yang paling meyakinkan untuk ditunjukkan kepada juri",
        "Masuk sebagai **bupati**, lalu coba buka profil satu keluarga — sistem menolak, "
        "karena pimpinan daerah sengaja hanya diberi akses agregat. Lalu masuk sebagai "
        "**pupr**, catat sebuah penyaluran, dan coba nilai hasilnya sendiri — sistem juga "
        "menolak. Dua penolakan itu memperlihatkan tata kelola bekerja, jauh lebih "
        "meyakinkan daripada menjelaskannya dengan kata-kata.",
    )

    d.h2("10.3 Perintah pengujian")
    d.kode(
        "python -m pytest backend/tests -q        # 61 uji backend\n"
        "cd frontend && npm run uji               # 11 halaman antarmuka\n"
        "cd frontend && npm run lint              # pemeriksaan tipe TypeScript\n"
        "python backend/scripts/siapkan_ai.py --daftar    # daftar model AI tersedia"
    )

    d.h2("10.4 Susunan berkas")
    d.kode(
        "NADI - LAN DATATHON/\n"
        "  backend/\n"
        "    nadi/\n"
        "      api/routes/      titik akhir API menurut modul\n"
        "      security/        penghalang PII, kewenangan, kode semu\n"
        "      db/              model tabel dan kosakata terkode\n"
        "      ml/              fitur, pelatihan, evaluasi, penjelasan\n"
        "      services/        deteksi anomali, rekomendasi, simulator\n"
        "      synth/           pembangkit data sintetis berkalibrasi\n"
        "      ai/              penyedia LLM agnostik dan Policy Copilot\n"
        "    scripts/           penyiapan data, pelatihan, dokumen\n"
        "    tests/             uji otomatis\n"
        "  frontend/\n"
        "    src/pages/         sebelas halaman antarmuka\n"
        "    src/components/    komponen bersama\n"
        "    uji/               uji asap antarmuka\n"
        "  data/                basis data, benih, batas wilayah\n"
        "  docs/                enam dokumen riset domain\n"
        "  dokumen/             panduan ini\n"
        "  JALANKAN-NADI.bat    peluncur satu klik"
    )

    d.h2("10.5 Rekapitulasi angka")
    baris = [
        ["Berkas Python", f"{f['py_berkas']}"],
        ["Baris Python", rb(f["py_baris"])],
        ["Berkas TypeScript", f"{f['ts_berkas']}"],
        ["Baris TypeScript", rb(f["ts_baris"])],
        ["Dokumen riset", f"{f['riset_berkas']} berkas, {rb(f['riset_kata'])} kata"],
        ["Tabel basis data", f"{f['tabel']} tabel, {rb(f['kolom'])} kolom"],
        ["Ukuran basis data", f"{rb(f['db_mb'], 1)} MB"],
        ["Keluarga", rb(f["baris"]["keluarga"])],
        ["Individu", rb(f["baris"]["anggota_keluarga"])],
        ["Potret kondisi", rb(f["baris"]["snapshot_keluarga"])],
        ["Skor kerentanan", rb(f["baris"]["skor_kerentanan"])],
        ["Guncangan tercatat", rb(f["baris"]["guncangan"])],
        ["Kasus terdeteksi", rb(f["baris"]["kasus"])],
        ["Verifikasi lapangan", rb(f["baris"]["verifikasi"])],
        ["Intervensi tercatat", rb(f["baris"]["intervensi"])],
        ["Hasil dinilai", rb(f["baris"]["hasil_intervensi"])],
        ["Program dalam katalog", rb(f["baris"]["program"])],
        ["Faktor risiko", rb(f["baris"]["faktor_risiko"])],
        ["OPD", rb(f["baris"]["opd"])],
        ["Wilayah", rb(f["baris"]["wilayah"])],
        ["Titik akhir API", "45 titik akhir pada 43 jalur"],
        ["Uji otomatis", "29 fungsi, 61 kasus uji"],
    ]
    d.tabel(["Butir", "Jumlah"], baris, lebar=[7.0, 8.0])

    d.h2("10.6 Sumber data dan acuan")
    d.poin(
        [
            "BPS Kabupaten Pringsewu — Potret Kemiskinan 2025, Pringsewu Dalam Angka 2025",
            "Peraturan BPS Nomor 6 Tahun 2025 tentang DTSEN",
            "Instruksi Presiden Nomor 4 Tahun 2025",
            "Kepmendagri Nomor 300.2.2-2138/2025 — daftar dan kode wilayah",
            "Badan Informasi Geospasial — batas desa skala 1:10.000",
            "Kementerian Desa PDTT — Indeks Desa Membangun 2024",
        ]
    )

    d.h2("10.7 Cara memperbarui dokumen ini")
    d.p(
        "Seluruh angka pada panduan ini dibaca langsung dari basis data dan berkas proyek "
        "saat dokumen disusun. Bila sistemnya berubah, jalankan ulang perintah berikut dan "
        "dokumennya ikut berubah."
    )
    d.kode("python backend/scripts/buat_panduan.py")


__all__ = ["bab_celah", "bab_lampiran", "bab_penjelasan"]
