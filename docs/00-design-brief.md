# NADI — Design Brief
### Navigasi AI Data Intervensi · Sistem Pendukung Keputusan Deteksi Dini Kerentanan Kemiskinan

**Lokus:** Kabupaten Pringsewu, Provinsi Lampung (kode wilayah `18.10`)
**Status dokumen:** fondasi pembangunan — mengikat seluruh keputusan teknis turunan
**Basis:** sintesis lima dokumen riset (`docs/research/01`–`05`)
**Peringatan permanen:** seluruh data yang dipakai aplikasi ini **sintetis**. Tidak ada satu pun keluarga nyata di dalamnya.

---

## 1. Ringkasan Eksekutif

### 1.1 Persoalan yang sebenarnya

Kabupaten Pringsewu tidak kekurangan data kemiskinan. DTSEN Versi 3 (2026) memuat 451.586 jiwa dan 144.262 keluarga untuk kabupaten ini, lengkap dengan desil kesejahteraan nasional. Yang kurang adalah **jembatan antara data dan tindakan**, dan jembatan itu putus di tiga titik yang dapat ditunjuk dengan angka.

| Titik putus | Bukti empiris Pringsewu | Konsekuensi |
|---|---|---|
| **Data tahu siapa miskin hari ini, tidak tahu siapa akan jatuh besok** | Kemiskinan turun 9,14% (2023) ke 8,32% (2024) ke 7,60% (2025), tetapi Gini Ratio **naik** 0,266 ke 0,299 dan melampaui provinsi; akses air layak rumah tangga miskin **turun** 94,27% ke 89,54%; stunting **naik** 15,8% ke 19,5% | Penurunan kemiskinan agregat menyembunyikan pembentukan kantong kerentanan baru |
| **Keputusan tersebar di 30 OPD tanpa antrean bersama** | Backlog RTLH kurang lebih 1.700 unit vs kapasitas APBD 80 unit per tahun (sekitar 21 tahun); kurang lebih 62.000 peserta PBI-JKN dinonaktifkan; tunggakan iuran Pemkab Rp7,94 miliar | Satu keluarga bisa terlewat oleh sembilan dinas sekaligus karena tidak ada yang memegang daftar prioritas lintas-urusan |
| **Kesalahan penargetan tidak pernah terlihat** | Benchmark literatur: exclusion error PMT pada cakupan 20% terbawah rata-rata 81% (Brown, Ravallion & van de Walle 2016); di Indonesia 93% dari 5% termiskin terekslusi dari PKH (Alatas et al. 2016) | Sistem hanya mengaudit kebocoran (orang mampu menerima), tidak pernah mengaudit keterlewatan (orang miskin tidak menerima) |

### 1.2 Apa yang dibangun

NADI adalah **lapisan analitik dan koordinasi di atas DTSEN**, bukan sistem pendataan tandingan. Delapan modul membentuk satu lingkaran tertutup:

```
        +---------- Executive Command Center ----------+
        |                                              |
  GeoAI Poverty Radar --> Household Digital Twin --> Intervention Recommender
        ^                       |                            |
        |                       v                            v
 Outcome Monitoring <-- Mismatch & Anomaly Queue --> Verifikasi Lapangan (manusia)
        ^                                                    |
        +------------ What-if Policy Simulator <-------------+
             AI Policy Copilot (melintasi seluruh modul)
```

Yang membedakan NADI dari dashboard adalah **lima kata kerja yang tidak dilakukan sistem lain secara bersamaan**:

1. **Memprediksi perubahan, bukan level.** Target model bukan "berapa desil keluarga ini" — BPS sudah menjawabnya lewat Proxy Means Test. Target NADI adalah `P(jatuh miskin pada gelombang berikutnya | kondisi gelombang sekarang)`.
2. **Menjelaskan per keluarga.** Setiap skor membawa tiga pendorong dan dua penahan risiko dalam kalimat yang dapat dibacakan pendamping kepada warga di Musyawarah Pekon.
3. **Menugaskan ke OPD spesifik.** Rekomendasi keluar sebagai rantai `faktor risiko -> program -> OPD penanggung jawab -> estimasi biaya`, bukan sekadar label risiko.
4. **Mensimulasikan kebijakan.** Kalkulator anggaran yang jujur: aritmetika cakupan dan biaya, bukan klaim kausal.
5. **Menutup lingkaran.** Hasil verifikasi lapangan dan outcome intervensi kembali menjadi data — untuk mengukur presisi flag, bukan untuk melatih ulang model secara diam-diam.

### 1.3 Mengapa ini bukan sekadar dashboard

Sebuah dashboard menjawab *"berapa"*. NADI menjawab *"siapa berikutnya, mengapa, siapa yang harus bergerak, dan apakah berhasil"*. Perbedaan itu terwujud dalam tiga keputusan arsitektur yang tidak dapat ditambal belakangan.

- **Ada tabel `guncangan` yang tidak ada di DTSEN.** Kematian pencari nafkah, sakit berat, PHK, gagal panen, bencana. Ligon & Schechter (2003) menunjukkan guncangan agregat adalah komponen kerentanan yang lebih besar daripada risiko idiosinkratik — dan DTSEN standar tidak merekam satu pun.
- **Ada tabel `snapshot_keluarga` bergelombang.** Tanpa panel waktu, "deteksi dini" hanyalah kata. Dengan panel, `delta_rasio_kemiskinan` dan `tren_menurun` menjadi fitur nyata.
- **Ada penyimpanan penjelasan yang immutable dan bertanggal.** Ini bukan fitur antarmuka, melainkan artefak kepatuhan UU PDP Pasal 10.

### 1.4 Batas tegas (ditulis di slide dan di setiap layar)

> NADI **tidak** memutus, mengurangi, atau menunda bantuan siapa pun. NADI **tidak** dipakai untuk deteksi kecurangan. Keluaran NADI adalah **antrean prioritas verifikasi**, dan pemutus akhir tetap Musyawarah Pekon/Kelurahan serta Surat Keputusan Bupati. Setiap keluarga berhak mengetahui alasan penilaian dan mengajukan keberatan.

Pembenaran empiris atas kerendahan hati ini: Aiken et al. (*Nature* 2022) menunjukkan targeting berbasis ML **menaikkan** exclusion error 9–35% dibandingkan metode yang memakai social registry komprehensif. Indonesia **punya** registry komprehensif. Maka posisi yang benar secara ilmiah adalah AI melengkapi, bukan menggantikan.

---

## 2. Model Data Kanonik

### 2.1 Enam keputusan fondasional

| # | Keputusan | Alasan |
|---|---|---|
| **D1** | Unit analisis adalah **KELUARGA (nomor KK)**, bukan rumah tangga | Perban BPS 6/2025 Pasal 1 angka 2 mendefinisikan DTSEN sebagai basis data "individu, dan/atau keluarga". Tidak ada nomor rumah tangga nasional. Memakai konsep rumah tangga membuat data NADI tidak dapat dipadankan dengan DTSEN selamanya. |
| **D2** | Nama kolom **persis** seperti Perban DTSEN | Pasal 10 ayat 4 huruf b mensyaratkan "variabel berstandar data yang sama dengan variabel DTSEN". Tulis `jenis_lantai_terluas`, bukan `floor_type`. |
| **D3** | Aset bertipe **integer/decimal**, bukan boolean | DTSEN merekam jumlah (`tabung_gas`, `lemari_es`) dan kuantitas kontinu (`emas_perhiasan` gram, `sawah_kebun` hektar). DTKS lama memakai boolean; menyalinnya akan memutus pemadanan. |
| **D4** | Seluruh kode kategori berada di **satu tabel lookup** `ref_kode_nilai` | Kode numerik resmi DTSEN **belum dipublikasikan** — regulasi hanya memuat nama variabel dan keterangan naratif. Kode yang dipakai NADI berasal dari Susenas via katalog IHSN sebagai proksi. Saat standar resmi terbit, cukup ganti isi tabel tanpa migrasi skema. |
| **D5** | **Versioning wajib** lewat kolom `gelombang` | Pemeringkatan DTSEN dilakukan pada snapshot (Perban Pasal 16–17), siklus triwulanan. Panel waktu adalah prasyarat "deteksi dini", bukan kemewahan. |
| **D6** | **Pseudonimisasi di pangkal**, bukan di ujung | Aplikasi tidak pernah menyimpan NIK/KK asli. Kolom `kode_semu` (misalnya `KLG-0A1B2C3D`) adalah satu-satunya identitas yang beredar di API, antarmuka, dan log. Data sintetis tetap diperlakukan sebagai data pribadi agar disiplin terbawa ke produksi. |

### 2.2 Peta entitas

```
ref_wilayah (SCD-2)                    ref_kode_nilai
     |                                       ^
     +--> konteks_wilayah (per gelombang)    | (semua kolom kategorik merujuk)
     |
     +--> keluarga --+--> anggota_keluarga (individu)
                     +--> snapshot_keluarga (gelombang) --+--> kondisi_hunian
                     |                                    +--> aset_keluarga
                     +--> guncangan
                     +--> kepesertaan_program --> program --> opd
                     +--> skor_kerentanan --> versi_model
                     +--> kasus (flag anomali) --> verifikasi
                     +--> rekomendasi --> intervensi --> hasil_intervensi
```

### 2.3 `ref_wilayah` — tulang punggung geografis

| Kolom | Tipe | Isi | Alasan |
|---|---|---|---|
| `kode` | CHAR(13) PK | `18.10.01.1001` | Kunci utama adalah **kode**, bukan nama. Ejaan berbeda antar sumber: BPS menulis "Gadingrejo", Kepmendagri "Gading Rejo", Tabel 1.1.1 BPS "Adi Luwih". Join berbasis nama akan gagal senyap. |
| `kode_bps` | CHAR(10) | Wilkerstat | BPS dan Kemendagri adalah **dua sistem berbeda** dengan struktur digit sama. Menyimpan keduanya berdampingan mencegah kegagalan join total. |
| `kode_dagri` | CHAR(13) | Kepmendagri 300.2.2-2138/2025 | idem |
| `tingkat` | ENUM | `kabupaten` / `kecamatan` / `desa` | Agregasi cukup lewat prefix string |
| `status` | ENUM | `pekon` / `kelurahan` | **Kritis.** Pringsewu punya 126 pekon dan 5 kelurahan. Dana Desa dan BLT-DD hanya berlaku bagi 126 pekon. Tanpa kolom ini seluruh simulasi anggaran desa salah. |
| `lintang`, `bujur` | DECIMAL(10,7) | Sentroid poligon BIG | 131 dari 131 desa sudah tersedia di `docs/research/pringsewu-seed/seed_desa_pringsewu.csv`. Tidak perlu geocoding saat runtime. |
| `luas_ha` | DECIMAL | Field `LUASWH` BIG | — |
| `status_idm` | ENUM | `berkembang` / `maju` / `mandiri` | Label targeting siap pakai yang sudah divalidasi Kemendes. 15 pekon "Berkembang" terkonsentrasi di Pagelaran Utara (7 dari 10) dan Pardasuka (6 dari 13). |
| `berlaku_mulai`, `berlaku_sampai` | DATE | SCD Type 2 | Kode wilayah berubah tiap pemekaran; Pringsewu akan menjadi 128 pekon. |

**Geometri** disimpan terpisah sebagai GeoJSON tersederhanakan (mapshaper 5–10%) di `data/geo/`, bukan di basis data. Field `KDEPUM` dari layanan BIG cocok **100%** dengan 131 kode Kepmendagri — nol selisih di kedua arah — sehingga dapat langsung dipakai sebagai foreign key. Berkas diunduh sekali dan disimpan lokal; endpoint BIG tidak dipanggil saat runtime karena tidak ada jaminan SLA maupun CORS.

### 2.4 `keluarga` dan `anggota_keluarga`

Tabel `keluarga` sengaja dibuat **tipis**: hanya identitas dan lokasi yang tidak berubah antar gelombang.

| Kolom | Alasan |
|---|---|
| `kode_semu` CHAR(20) UNIQUE | Pengganti nomor KK. Tidak pernah bocor ke antarmuka, LLM, maupun log. |
| `wilayah_id` FK | Menunjuk ke level desa/pekon. |
| `lintang`, `bujur` | Variabel `lokasi` adalah variabel resmi DTSEN. Ini pula **satu-satunya cara membentuk entitas "bangunan"** yang tidak memiliki primary key di DTSEN — lewat hash koordinat dan alamat ternormalisasi. |
| `keluarga_dalam_rumah` SMALLINT | Variabel resmi DTSEN. Menangani kasus lebih dari satu keluarga dalam satu rumah, yang kerap menjadi sumber duplikasi semu. |
| `status_padan_dukcapil` ENUM | Implementasi Perban Pasal 15 ayat 3 sebagai **gerbang masuk**: NIK atau KK tidak valid berarti record tidak masuk tabel utama, melainkan masuk karantina dan dikembalikan kepada penyedia. Bukan pembersihan belakangan. |

Tabel `anggota_keluarga` memuat 13 variabel individu DTSEN. Tiga catatan desain penting:

- **Disabilitas disimpan dalam dua kerangka sekaligus.** Tabel anak `individu_disabilitas_wgss` (6 domain kali 4 tingkat, standar BPS Susenas sejak 2023) **ditambah** kolom `jenis_disabilitas_uu8` (Fisik, Mental, Intelektual, Sensorik, Ganda — dipakai Kemensos untuk ATENSI). Menyimpan salah satu saja memutus salah satu jalur integrasi.
- **Pendidikan memakai dua kolom:** `partisipasi_sekolah` (3 kategori) dan `pendidikan_tertinggi` (ijazah, 8 kategori). Satu kolom tidak cukup — "anak putus sekolah" hanya dapat dideteksi dari kombinasi keduanya dengan usia.
- **`tahun_lahir`, bukan `tanggal_lahir`.** Minimisasi data: presisi hari tidak menambah daya prediksi apa pun, tetapi menambah risiko re-identifikasi.

### 2.5 `snapshot_keluarga` — jantung panel waktu

Satu baris per keluarga per gelombang (triwulan). Inilah tabel yang membedakan NADI dari sebuah registry.

| Kolom | Alasan |
|---|---|
| `gelombang` SMALLINT | 0 sampai N, dipetakan ke triwulan kalender. |
| `tanggal_kondisi` DATE | Tanggal kondisi, bukan tanggal input. |
| `pengeluaran_per_kapita` | Di dunia sintetis, variabel ini dibangkitkan generator dan dipakai menentukan label. Di produksi nyata ini menjadi hasil prediksi PMT. |
| `rasio_garis_kemiskinan` | `pengeluaran_per_kapita / 583.425`. Dinormalisasi terhadap garis kemiskinan Pringsewu 2024 agar sebanding antar gelombang. |
| `desil_kesejahteraan` 1–10 | **Kolom INPUT, bukan target model.** DTSEN sudah memberikan desil; menduplikasinya berarti mereplikasi PMT beserta seluruh label bias-nya. |
| `status_miskin` BOOLEAN | Bernilai benar bila `rasio_garis_kemiskinan < 1`. |
| `jumlah_anggota`, `jumlah_balita`, `jumlah_anak_usia_sekolah`, `jumlah_lansia`, `jumlah_disabilitas`, `jumlah_bekerja` | Agregat yang **dimaterialisasi**, bukan dihitung ad-hoc. Alasannya konsistensi lintas laporan dan kecepatan — komposisi keluarga dipakai di hampir semua fitur. |
| `umur_data_hari` | Turunan yang menjadi **fitur model sekaligus elemen antarmuka**. Aiken, Ohlenburg & Blumenstock membuktikan akurasi prediksi kemiskinan terdegradasi terus-menerus; model harus tahu seberapa basi datanya. |

### 2.6 `kondisi_hunian` dan `aset_keluarga`

Tabel `kondisi_hunian` memuat 12 variabel perumahan DTSEN **ditambah empat kolom pengayaan yang wajib secara logis**.

| Kolom pengayaan | Mengapa wajib |
|---|---|
| `luas_lantai_m2` | **Tidak ada di daftar variabel DTSEN**, padahal 7,2 m² per kapita adalah kriteria resmi rumah layak huni (RPJMN/SDGs) sekaligus kriteria kelima RTLH Kemensos. Tanpa kolom ini indikator rumah layak huni **tidak dapat dihitung sama sekali**. |
| `jarak_penampungan_limbah_m` | Wajib untuk kaidah air minum layak pada sumber kode 5 dan 6: sumur bor dan sumur terlindung hanya layak bila jarak lebih dari 10 meter. |
| `sumber_air_mandi_cuci` | Melengkapi kaidah air minum layak untuk sumber kode 1 dan 2. |
| `konsumsi_listrik_kwh` | BPS menyebut indikator PMT mencakup "daya **dan konsumsi** listrik", sedangkan daftar Perban hanya memuat `daya_terpasang`. |

Lima kolom **turunan yang dimaterialisasi** (bukan dihitung di dalam query), mengikuti kaidah resmi HREIS/PUPR:

```
air_minum_layak          = sumber IN {kemasan, isi_ulang, leding, hujan, mata_air_terlindung}
                           OR (sumber IN {sumur_bor, sumur_terlindung} AND jarak_limbah > 10)

sanitasi_layak           = fasilitas_bab IN {sendiri, bersama_RT, MCK_komunal}
                           AND jenis_kloset = leher_angsa
                           AND tinja IN {tangki_septik, IPAL}

ketahanan_bangunan_layak = atap_layak AND dinding_layak AND lantai_layak      (konjungsi ketat)

luas_lantai_per_kapita   = luas_lantai_m2 / jumlah_anggota

rumah_layak_huni         = luas_lantai_per_kapita >= 7,2 AND air_minum_layak
                           AND sanitasi_layak AND ketahanan_bangunan_layak
```

Alasan materialisasi: aturannya sudah pasti dan terdokumentasi resmi, dipakai di banyak modul sekaligus (Radar, Digital Twin, Recommender, Simulator), dan perhitungan ad-hoc di query akan menghasilkan angka yang berbeda-beda antar laporan.

Tabel `aset_keluarga` memuat 19 sub-variabel grup "Kepemilikan" DTSEN dengan tipe numerik. Perubahan yang jarang disadari dan wajib diikuti: DTSEN menurunkan ambang tabung gas dari lebih dari 12 kg menjadi minimal 5,5 kg, mengganti "TV kabel" menjadi "TV datar minimal 30 inch", dan **menambah variabel baru `smartphone`**.

### 2.7 `guncangan` — tabel yang tidak ada di DTSEN

Inilah pembeda struktural NADI. DTSEN standar tidak merekam guncangan sama sekali.

| Kolom | Nilai |
|---|---|
| `keluarga_id` FK | — |
| `jenis` ENUM | `kematian_pencari_nafkah`, `sakit_berat`, `kehilangan_pekerjaan`, `gagal_panen`, `bencana`, `kenaikan_harga_pangan`, `perceraian` |
| `gelombang_kejadian` SMALLINT | Menentukan jendela peluruhan pengaruh |
| `tingkat_keparahan` SMALLINT | 1 sampai 3 |
| `sumber_laporan` ENUM | `kader` / `pendamping_pkh` / `tksk` / `mandiri` / `sistem` |
| `terverifikasi` BOOLEAN | Guncangan yang belum terverifikasi tetap masuk model dengan bobot lebih rendah |

Konsekuensi produk: NADI membutuhkan **kanal input kader** berupa modul Rapid Assessment 10 sampai 20 pertanyaan. Ini keputusan besar karena menambah beban lapangan demi kekuatan prediksi. Justifikasinya kuat: guncangan kesehatan katastropik menjatuhkan sekitar 62.685 penduduk Indonesia ke bawah garis kemiskinan **dalam satu bulan**, dan kelompok paling rentan adalah **desil 3 sampai 6** — persis populasi yang tidak tertangkap targeting berbasis desil 1 sampai 4.

### 2.8 `program`, `kepesertaan_program`, `opd`

Tabel `kepesertaan_program` **harus polimorfik**. Sebagian program berbasis keluarga (PKH, Sembako, BLT-DD, subsidi listrik dan LPG), sebagian berbasis individu (PBI-JKN, PIP, KIP Kuliah, MBG, BSU).

```sql
keluarga_id  INT NULL REFERENCES keluarga(id),
anggota_id   INT NULL REFERENCES anggota_keluarga(id),
CHECK (keluarga_id IS NOT NULL OR anggota_id IS NOT NULL)
```

Ditambah `gelombang_mulai` dan `gelombang_selesai` karena kepesertaan berubah tiap triwulan, serta `nilai_manfaat_bulanan` untuk agregasi anggaran.

Setiap nominal di tabel `program_manfaat` **wajib** membawa kolom `keyakinan` ENUM (`pasti`, `cukup_kuat`, `perkiraan`, `tidak_ditemukan`) dan `sumber_url[]`. Riset menemukan konflik nyata: nominal PKH komponen lansia dan disabilitas berat dilaporkan Rp2,4 juta per tahun oleh sumber kuat dan Rp3 juta per tahun oleh blog sekunder. Antarmuka menampilkan badge keyakinan dan **tidak menampilkan angka sama sekali** untuk item berstatus `tidak_ditemukan` — misalnya nominal SANIMAS, PAMSIMAS, dan PMT per porsi.

Tabel `program` juga membawa `tingkat_eksekusi` ENUM: `pusat_disalurkan_di_daerah`, `apbd_daerah`, `dana_desa`, `mandiri_online`. Pembagian ini menentukan apakah pengguna kabupaten dapat **bertindak** atau hanya **memantau**. Catatan operasional yang mudah terlewat: PIP jenjang SD dan SMP adalah kewenangan Dinas Pendidikan kabupaten, sedangkan SMA dan SMK adalah kewenangan provinsi.

### 2.9 `kasus`, `verifikasi`, `rekomendasi`, `intervensi`, `hasil_intervensi`

Rantai kerja yang menutup lingkaran:

| Tabel | Peran | Kolom kunci |
|---|---|---|
| `kasus` | Flag anomali atau prioritas | `jenis`, `skor_prioritas`, `alasan` JSONB, `sumber_deteksi` (`aturan`/`statistik`/`residual`), `status`, `opd_ditugaskan_id`, `tenggat` |
| `verifikasi` | Hasil kunjungan lapangan | `hasil`, `setuju_dengan_sistem` BOOLEAN, `kondisi_terkoreksi` JSONB, `durasi_menit` |
| `rekomendasi` | Program yang cocok | `program_id`, `faktor_risiko_id`, `skor_kecocokan`, `alasan_kelayakan` |
| `intervensi` | Penugasan nyata | `opd_id`, `status`, `nilai_manfaat`, `ditetapkan_oleh_id` |
| `hasil_intervensi` | Outcome | `gelombang_sebelum`, `gelombang_sesudah`, `skor_sebelum`, `skor_sesudah`, `miskin_sebelum`, `miskin_sesudah`, `indikator_berubah` |

Kolom `setuju_dengan_sistem` adalah yang paling bernilai secara metodologis. Alatas et al. (*AER* 2012) membuktikan model statistik dan penilaian komunitas mengukur **konstruk yang berbeda**, dan elite capture bukan penjelasannya — komunitas memakai konsep kemiskinan lain, misalnya kapasitas mencari nafkah alih-alih konsumsi. **Ketidaksepakatan adalah sinyal, bukan gangguan.** Kolom ini memberi umpan balik presisi flag tanpa melatih ulang model secara otomatis.

### 2.10 Tabel sistem

| Tabel | Kewajiban hukum yang dipenuhi |
|---|---|
| `jejak_audit` | Perban Pasal 28 ayat 8: setiap akses, aktivitas, dan pengelolaan tercatat lengkap, akurat, dan terlindungi untuk monitoring, penelusuran insiden, dan audit keamanan. Dirancang hari pertama, bukan retrofit. |
| `pengguna`, `peran`, `hak_akses` | Perban Pasal 29 ayat 2 mewajibkan RBAC, kriptografi, logging, dan backup. |
| `keberatan` | Implementasi konkret UU PDP Pasal 10 (hak keberatan atas keputusan berbasis pemrosesan otomatis). |
| `versi_model` | `metrik`, `metrik_keadilan`, `sidik_jari_dataset`, `dilatih_pada`, `jalur_artefak`. Setiap baris `skor_kerentanan` menyimpan `versi_model_id` sehingga skor lama tetap dapat dipertanggungjawabkan setelah model berganti. |

---

## 3. Desain Fitur Model

### 3.1 Prinsip yang mengikat

| Prinsip | Penegakan teknis |
|---|---|
| **Satu sumber kebenaran fitur** | Seluruh fitur dihitung di satu modul (`nadi/ml/fitur.py`) yang dipanggil sama persis saat pelatihan dan saat penyajian. Ini mencegah *training-serving skew* — model bekerja baik pada data uji lalu meleset di layar pengguna tanpa ada yang tahu sebabnya. |
| **Tidak menengok ke masa depan** | Fungsi pembentuk fitur hanya menerima satu baris kondisi pada gelombang `t` beserta konteks wilayahnya. Secara teknis ia **tidak memiliki akses** ke gelombang `t+1` tempat label berada. Aturan ditegakkan struktur kode, bukan kedisiplinan. |
| **Setiap fitur membawa metadata** | Tiap fitur menyimpan dimensi kerentanan, kode faktor risiko (R01 sampai R20), arah buruk, dan kalimat penjelas berbahasa Indonesia. Metadata inilah yang mengubah keluaran TreeSHAP menjadi alasan yang dapat dibaca petugas, tanpa tabel penerjemah terpisah yang gampang tertinggal. |
| **Pemisahan stok dan aliran** | Fitur **stok** (aset, kondisi rumah) menjelaskan deprivasi saat ini. Fitur **aliran** (status pekerjaan, guncangan, cakupan JKN) menjelaskan risiko ke depan. Keduanya tidak boleh tercampur tanpa sadar. |

### 3.2 Daftar fitur per dimensi

Total 51 fitur. Kolom "Risiko" menunjuk kode faktor risiko pada katalog Bagian 6.

#### A. Ekonomi (5 fitur)

| Fitur | Cara hitung | Alasan teoretis | Risiko |
|---|---|---|---|
| `rasio_garis_kemiskinan` | `pengeluaran_per_kapita / 583.425` | Normalisasi terhadap garis kemiskinan Pringsewu 2024 membuat nilai sebanding antar gelombang dan antar wilayah | R01 |
| `log_pengeluaran_per_kapita` | `ln(pengeluaran_per_kapita)` | Model PMT BPS memakai `ln(y)` sebagai variabel respons; distribusi pengeluaran sangat miring kanan | R01 |
| `desil_kesejahteraan` | Langsung dari DTSEN | **Hanya untuk Skor A (deprivasi).** Dilarang keras sebagai fitur Skor B karena desil adalah keluaran PMT dari fitur yang sama, sehingga menjadi kebocoran melingkar | R01 |
| `indeks_aset` | Skor terbobot 19 aset, dinormalisasi 0 sampai 1 | Aiken et al. (2023) menemukan korelasi indeks aset dengan konsumsi hanya 0,37 — aset mengukur hal berbeda dari konsumsi sehingga menambah informasi, bukan mengulang | R01 |
| `punya_aset_produktif` | Ada sepeda motor, lahan, atau ternak | Aset produktif adalah penyangga guncangan sekaligus modal pemulihan | R14 |

#### B. Pekerjaan (6 fitur)

| Fitur | Cara hitung | Alasan teoretis | Risiko |
|---|---|---|---|
| `rasio_tanggungan` | `(balita + anak sekolah + lansia + disabilitas) / max(jumlah_bekerja, 1)` | Rasio ketergantungan adalah prediktor kerentanan paling stabil lintas negara | R01 |
| `tidak_ada_yang_bekerja` | `jumlah_bekerja == 0` | Kondisi ekstrem yang tidak tertangkap rasio kontinu | R13 |
| `kk_pekerjaan_rentan` | Status pekerjaan KK adalah pekerja bebas, pekerja keluarga tak dibayar, atau berusaha sendiri | Struktur ketenagakerjaan Pringsewu: hanya 30,6% pekerja berstatus relatif formal (69.020 dari 225.631) | R13 |
| `kk_sektor_musiman` | Lapangan usaha KK adalah padi/palawija, hortikultura, perkebunan, atau perikanan | Pertanian menyumbang 22,67% PDRB Pringsewu dengan pendapatan musiman; sekitar 60% kepala rumah tangga rentan miskin berada di sektor primer | R19 |
| `kk_berpenghasilan_tetap` | Buruh/karyawan atau berusaha dibantu buruh tetap | Fitur **penahan** (arah buruk negatif). Penting agar panel penjelasan tidak hanya berisi hal buruk | — |
| `jumlah_usaha_keluarga` | Jumlah usaha yang dimiliki seluruh anggota | Pintu masuk rekomendasi KUR, PENA, dan KUBE | R14 |

#### C. Pendidikan (4 fitur)

| Fitur | Cara hitung | Alasan teoretis | Risiko |
|---|---|---|---|
| `kk_tahun_sekolah` | Konversi ijazah tertinggi KK ke tahun (SD=6, SMP=9, SMA=12, D3=15, S1=16) | Pendidikan kepala keluarga adalah proksi kapasitas pendapatan permanen. Studi Sambas: 68,75% kepala rumah tangga rentan berpendidikan SD ke bawah | R06 |
| `rata_lama_sekolah_dewasa` | Rata-rata tahun sekolah anggota usia 15 tahun ke atas | Menangkap modal manusia keluarga, bukan hanya kepalanya | R06 |
| `ada_anak_putus_sekolah` | Ada anggota usia 7 sampai 18 tahun dengan `partisipasi_sekolah = tidak_bersekolah_lagi` | Mekanisme transmisi kemiskinan antargenerasi paling langsung; pemicu rekomendasi PIP dan Sekolah Rakyat | R05 |
| `beban_anak_sekolah` | `jumlah_anak_usia_sekolah / jumlah_anggota` | Beban biaya pendidikan relatif terhadap ukuran keluarga | R05 |

#### D. Kesehatan (8 fitur)

| Fitur | Cara hitung | Alasan teoretis | Risiko |
|---|---|---|---|
| `ada_penyakit_biaya_tinggi` | Ada anggota berpenyakit katastropik | Sekitar 62.685 penduduk Indonesia jatuh miskin dalam sebulan akibat biaya katastropik; rawat inap kanker Rp80 sampai 250 juta | R18 |
| `ada_penyakit_kronis` | Ada anggota berpenyakit menahun | Kriteria eksplisit BLT Dana Desa | R18 |
| `cakupan_jkn` | `jumlah anggota ber-JKN aktif / jumlah_anggota` | Kontinu, bukan boolean — cakupan sebagian adalah kondisi paling umum sekaligus paling berisiko | R07 |
| `tanpa_jkn_sama_sekali` | `cakupan_jkn == 0` | Kondisi ekstrem. Relevansi langsung Pringsewu: sekitar 62.000 peserta PBI dinonaktifkan | R07 |
| `ada_gizi_bermasalah` | Ada balita berstatus gizi kurang atau stunting | Stunting Pringsewu naik 15,8% ke 19,5%, berlawanan arah dengan tren kemiskinan | R03 |
| `jumlah_disabilitas` | Hitungan anggota penyandang disabilitas | Pemicu ATENSI dan komponen PKH disabilitas berat | R12 |
| `ada_ibu_hamil` | Ada anggota sedang hamil | Pemicu PKH komponen ibu hamil dan PMT ibu hamil KEK | R04 |
| `ada_masalah_dokumen` | Ada anggota tanpa NIK padan Dukcapil atau tanpa akta | **Gerbang semua bansos.** Ini penyebab exclusion error yang paling murah diperbaiki: cukup jemput bola Disdukcapil | R16 |

#### E. Hunian (9 fitur)

| Fitur | Cara hitung | Alasan teoretis | Risiko |
|---|---|---|---|
| `luas_lantai_per_kapita` | `luas_lantai_m2 / jumlah_anggota` | Kriteria resmi rumah layak huni | R08 |
| `hunian_padat` | `luas_lantai_per_kapita < 7,2` | Ambang resmi RPJMN dan SDGs | R08 |
| `ketahanan_bangunan_tidak_layak` | Negasi konjungsi atap, dinding, dan lantai layak | Kaidah HREIS/PUPR: bila salah satu tidak layak maka seluruhnya tidak layak | R08 |
| `berbagi_rumah` | `keluarga_dalam_rumah > 1` | Indikator kepadatan tersembunyi yang khas DTSEN | R08 |
| `sanitasi_tidak_layak` | Negasi kaidah sanitasi layak | Sekaligus kriteria RTLH keempat Kemensos | R09 |
| `air_minum_tidak_layak` | Negasi kaidah air minum layak | Perhatian penting: Pringsewu punya air **layak** 95,64% tetapi air **aman** hanya 41,31% — selisih 54 poin adalah ruang intervensi terbesar sektor air | R10 |
| `listrik_daya_rendah` | Daya terpasang 450 atau 900 VA, atau tanpa listrik | Salah satu prediktor terkuat dalam PMT BPS; sekaligus penanda kelayakan subsidi | R01 |
| `memasak_bahan_bakar_tidak_layak` | Kayu bakar, arang, atau briket | Proksi deprivasi energi sekaligus risiko kesehatan pernapasan | R01 |
| `jumlah_kriteria_rtlh` | Hitungan 0 sampai 5 dari lima kriteria RTLH Kemensos | **Fitur produk, bukan sekadar fitur model.** Langsung menjadi skor antrean RTLH pada modul Recommender | R08 |

#### F. Demografi dan tanggungan (5 fitur)

| Fitur | Cara hitung | Alasan teoretis | Risiko |
|---|---|---|---|
| `jumlah_anggota` | Hitungan | Dietrich et al. (2024) membuktikan rumah tangga **kecil** dirugikan sistematis oleh PMT. Fitur ini wajib ada agar bias tersebut dapat diaudit | — |
| `kk_perempuan` | Jenis kelamin KK adalah perempuan | Kriteria eksplisit BLT Dana Desa; PEKKA adalah kelompok rentan terdokumentasi | R17 |
| `kk_lansia` | Usia KK 60 tahun ke atas | Kapasitas pendapatan menurun tanpa penopang | R11 |
| `jumlah_balita` | Hitungan usia 0 sampai 5 tahun | Pemicu PKH, MBG, dan Posyandu | R03 |
| `jumlah_lansia` | Hitungan usia 60 tahun ke atas | Pemicu PKH lansia dan ATENSI | R11 |

#### G. Perlindungan sosial (3 fitur)

| Fitur | Cara hitung | Alasan teoretis | Risiko |
|---|---|---|---|
| `jumlah_program_diterima` | Hitungan program aktif pada gelombang `t` | **Hanya untuk Skor A dan deteksi mismatch.** Dilarang sebagai fitur Skor B karena menciptakan umpan balik melingkar: penerima bantuan tampak kurang rentan, sehingga bantuan justru dicabut | — |
| `nilai_bantuan_per_kapita` | Total manfaat bulanan dibagi jumlah anggota | Dipakai simulator anggaran dan analisis progresivitas | — |
| `tanpa_bantuan_apa_pun` | `jumlah_program_diterima == 0` | Kombinasi dengan skor tinggi adalah **kandidat exclusion error** — skenario demo paling penting | — |

#### H. Guncangan (4 fitur)

| Fitur | Cara hitung | Alasan teoretis | Risiko |
|---|---|---|---|
| `jumlah_guncangan_terkini` | Guncangan dalam 4 gelombang terakhir | Jendela satu tahun; guncangan lebih lama pengaruhnya sudah terserap ke dalam kondisi | R19 |
| `ada_guncangan_pendapatan` | Ada PHK, gagal panen, atau kematian pencari nafkah | Guncangan idiosinkratik pada aliran pendapatan | R19 |
| `ada_guncangan_bencana` | Ada kejadian bencana | Guncangan kovarian; berkorelasi dalam satu pekon | R20 |
| `bobot_guncangan` | Jumlah dari `keparahan × peluruhan(jarak gelombang) × faktor_verifikasi` | Peluruhan eksponensial 0,7 per gelombang. Faktor verifikasi 1,0 bila terverifikasi dan 0,6 bila belum, sehingga laporan yang belum terverifikasi tetap berguna tanpa mendominasi | R19 |

#### I. Dinamika dan konteks wilayah (7 fitur)

| Fitur | Cara hitung | Alasan teoretis | Risiko |
|---|---|---|---|
| `delta_rasio_kemiskinan` | `rasio(t) − rasio(t−1)` | **Inti dari kata "deteksi dini".** Keluarga dengan rasio 1,3 yang menurun cepat lebih berisiko daripada keluarga rasio 1,1 yang stabil | R01 |
| `tren_menurun` | Kemiringan regresi rasio pada 3 gelombang terakhir bernilai negatif | Menangkap arah, bukan hanya perubahan sesaat | R01 |
| `pernah_miskin_sebelumnya` | Pernah `status_miskin` bernilai benar pada gelombang mana pun sebelumnya | Kemiskinan sangat persisten; riwayat adalah prediktor kuat sekaligus pembeda kronis versus transien | R01 |
| `persen_miskin_wilayah` | Angka kemiskinan pekon pada gelombang `t` | Guncangan **agregat** lebih penting daripada idiosinkratik (Ligon & Schechter 2003) | — |
| `wilayah_perdesaan` | Status wilayah adalah pekon | Kemiskinan perdesaan Lampung 10,41% versus perkotaan 7,28%. Base rate memang berbeda secara sah | — |
| `umur_data_bulan` | Selisih tanggal kondisi dengan tanggal skoring | Model dua tahun basi menurunkan akurasi 3 sampai 4 poin persen — sebesar keuntungan targeting berbasis ponsel atas targeting geografis | — |
| `kelengkapan_data` | Proporsi kolom wajib yang terisi | Mencegah keluarga berdata buruk tampak "aman" hanya karena datanya kosong | — |

#### J. Fitur spasial tertinggal (spatial lag)

Untuk setiap fitur kunci `x` dihitung `spatial_lag_x` sebagai rata-rata `x` pada pekon tetangga, memakai matriks kontiguitas dari triangulasi Delaunay atas sentroid desa. Justifikasinya kuat dan spesifik Indonesia: Moran's I pengeluaran rumah tangga Indonesia bernilai 0,411 (p kurang dari 0,01), dan spatial machine learning menurunkan exclusion error dari 28,20% menjadi 20,14% pada data Susenas-DTKS.

Ini adalah **keunggulan struktural NADI**. PMT nasional secara desain tidak dapat memakai efek level desa karena kalibrasinya hanya pada sampel desa, sedangkan NADI beroperasi di satu kabupaten dengan cakupan penuh 131 desa.

### 3.3 Daftar terlarang

Fitur berikut **dilarang** untuk Skor B, masing-masing dengan alasan yang tidak dapat ditawar.

| Fitur terlarang | Alasan |
|---|---|
| `desil_kesejahteraan` | Kebocoran melingkar — desil adalah keluaran PMT dari fitur yang sama |
| `jumlah_program_diterima` dan status penerimaan bansos | Kebocoran target sekaligus umpan balik yang mencabut bantuan dari keluarga yang berhasil ditolong |
| Agama, etnis, suku, bahasa daerah | Pelajaran SyRI: penargetan yang berkorelasi dengan minoritas menjadi fakta memberatkan di pengadilan |
| Afiliasi politik dan data pemilih | Idem, ditambah risiko penyalahgunaan elektoral |
| NIK, nama, dan alamat sebagai nilai numerik | Kebocoran identitas terselubung |
| Foto rumah mentah | Ditunda ke versi kedua; explainability-nya buruk dan risiko biasnya tinggi |

---

## 4. Definisi Label dan Strategi Pemodelan

### 4.1 Dua skor, bukan satu

Kesalahan paling mahal yang dapat dilakukan NADI adalah melatih model untuk memprediksi desil DTSEN. Itu hanya mereplikasi PMT beserta seluruh kesalahannya, dan mudah dipatahkan juri dengan satu kalimat: "BPS sudah melakukannya."

| | **Skor A — Deprivasi** | **Skor B — Kerentanan** |
|---|---|---|
| Pertanyaan | Seberapa buruk kondisi keluarga ini **sekarang**? | Seberapa besar peluang keluarga ini **jatuh miskin** pada gelombang berikutnya? |
| Label | `L_A = 1[rasio_garis_kemiskinan(t) < 1]` | `L_B = 1[status_miskin(t+1) benar DAN status_miskin(t) salah]` |
| Kegunaan | Mengaudit konsistensi NADI dengan DTSEN; mendeteksi mismatch | **Alasan NADI ada.** DTSEN tidak menyediakan ini |
| Fitur terlarang | — | `desil_kesejahteraan`, status bansos |
| Model | LightGBM biner | LightGBM biner ditambah kalibrasi isotonic |

### 4.2 Definisi label utama secara presisi

```
Untuk setiap pasangan (keluarga h, gelombang t) dengan t < T_maks:

  memenuhi_syarat(h, t) = status_miskin(h, t) == FALSE        # berisiko, belum miskin

  L_B(h, t) = 1     bila status_miskin(h, t+1) == TRUE
              0     bila status_miskin(h, t+1) == FALSE
              NULL  bila keluarga hilang pada t+1             # dikeluarkan, bukan diisi 0
```

Tiga keputusan yang menyertainya:

1. **Keluarga yang sudah miskin pada `t` dikeluarkan dari populasi berisiko.** Menyertakan mereka membuat model belajar memprediksi "tetap miskin" — trivial dan tidak berguna untuk pencegahan. Mereka ditangani jalur berbeda: bantuan reguler, bukan pencegahan.
2. **Atrisi tidak diperlakukan sebagai bukan-kejadian.** Keluarga yang hilang pada `t+1` karena pindah, pecah KK, atau meninggal seluruhnya diberi label NULL dan dikeluarkan dari pelatihan maupun evaluasi. Mengisinya dengan 0 adalah bias yang sistematis merugikan keluarga paling tidak stabil.
3. **Label pendamping `L_VEP` sebagai pembanding metodologis**, dihitung dengan metode Chaudhuri, Jalan & Suryahadi (2002) — metode yang justru dikembangkan dengan data Indonesia.

```
Tahap 1 : OLS pada  ln c = X·beta + e   -->  residual e_topi
          regresikan  e_topi^2 = X·theta + eta
Tahap 2 : bagi persamaan varians dengan dirinya sendiri  --> theta_topi efisien asimtotik
Tahap 3 : bagi persamaan utama dengan akar(X·theta_topi) --> beta_topi konsisten dan efisien

V_topi(h) = Phi[ (ln z − X_h·beta_topi) / akar(X_h·theta_topi) ]
Ambang    : V_topi >= 0,50     (Pritchett, Suryahadi & Sumarto 2000)
```

Nilai tambah VEP bukan sekadar angka pembanding melainkan **dekomposisi untuk antarmuka**. Pembilang `(ln z − X·beta)` adalah komponen "rata-rata rendah" yakni kemiskinan struktural; penyebut `akar(X·theta)` adalah komponen "varians tinggi" yakni volatilitas. Keduanya menuntun ke jenis intervensi berbeda — bantuan reguler versus proteksi dan asuransi. Kedua komponen disimpan terpisah pada tabel `skor_kerentanan`.

Uji kewajaran yang dipakai: populasi rentan berkisar 1,5 sampai 2,5 kali populasi miskin. Dengan P0 Pringsewu 7,6%, proporsi rentan yang wajar adalah 11 sampai 19 persen.

### 4.3 Taksonomi keluaran dan pemetaan intervensi

| Kondisi `c` vs garis `z` | Ekspektasi `E[c]` vs `z` | `V` | Kategori | Jalur intervensi |
|---|---|---|---|---|
| `c < z` | `E[c] < z` | — | Miskin kronis | Bantuan reguler dan investasi SDM: PKH, Sembako, PIP |
| `c < z` | `E[c] >= z` | — | Miskin transien | Bantuan sementara dan pemulihan: BLT-DD, BTT Dinsos |
| `c >= z` | — | `>= 0,5` | **Rentan non-miskin** | **Pencegahan**: PBI-JKN, BPJS TK pekerja rentan, dana cadangan pekon |
| `c >= z` | — | `< 0,5` | Aman | Tidak ada |

Baris ketiga adalah wilayah kerja utama NADI, dan justru wilayah yang tidak tertangkap targeting berbasis desil 1 sampai 4.

### 4.4 Panel longitudinal sintetis

Delapan gelombang triwulanan mewakili dua tahun: gelombang 0 pada Triwulan I 2025 sampai gelombang 7 pada Triwulan IV 2026.

| Gelombang | Peran |
|---|---|
| 0–4 | **Latih** (sekitar 60% pasangan keluarga-gelombang) |
| 5 | **Kalibrasi** (20%), terpisah agar isotonic regression tidak melihat data latih |
| 6–7 | **Uji temporal** (20%), meniru kondisi produksi tempat model dilatih pada masa lalu dan dipakai pada masa depan |

Pemisahan dilakukan **di level keluarga (kode semu)**, bukan di level baris, agar keluarga yang sama tidak tersebar antara latih dan uji. Ditambah **leave-one-kecamatan-out cross-validation** sebagai uji generalisasi spasial wajib: model yang bagus secara agregat dapat gagal total di satu kecamatan, dan Pagelaran Utara adalah outlier di hampir semua dimensi.

### 4.5 Variabel laten yang disembunyikan dari model

Inilah yang membuat metrik realistis. Lima variabel dibangkitkan, disimpan untuk audit generator, dan **tidak pernah** diberikan kepada model.

| Laten | Peran dalam proses pembangkitan |
|---|---|
| `L1_kapasitas_pendapatan` | Penentu utama pengeluaran. Fitur teramati (aset, luas lantai, daya listrik) adalah fungsi **berderau** dari L1 |
| `L2_jaringan_sosial` | Menentukan kemampuan pulih setelah guncangan dan peluang menerima bantuan informal |
| `L3_kerentanan_kesehatan` | Menentukan laju kejadian guncangan sakit berat |
| `L4_kualitas_enumerasi_pekon` | Menentukan tingkat derau pencatatan dan probabilitas label terbalik pada pekon tersebut |
| `L5_akses_kredit_informal` | Penyangga guncangan yang tidak terlihat pada aset formal |

Kalibrasi derau diatur sehingga `R kuadrat` regresi fitur teramati terhadap `ln(pengeluaran)` berada pada **0,45 sampai 0,55** — kisaran yang dilaporkan literatur: rata-rata 0,53 pada sembilan negara Afrika (Brown, Ravallion & van de Walle 2016) dan 0,40 sampai 0,60 pada mayoritas PMT negara berkembang (Kidd & Wylde 2017).

**Label dibangkitkan dari laten, bukan dari fitur teramati.** Ini pembalikan yang menentukan:

```
ln(pengeluaran) = beta·L1 + gamma·L2 − delta·L3 + efek_guncangan + eta
status_miskin   = 1[pengeluaran < garis_kemiskinan]
```

Bila label dibangkitkan dari fitur teramati, model akan menemukan hubungan yang nyaris deterministik dan AUC melonjak ke 0,97 — angka yang cantik di slide dan tidak berarti apa pun.

### 4.6 Derau label yang tidak acak

Sebanyak 3 sampai 5 persen label dibalik, dan pembalikan itu **sengaja tidak seragam**: lebih sering pada rumah tangga **kecil** (mereplikasi temuan Dietrich et al. 2024 bahwa PMT merugikan rumah tangga kecil secara sistematis) dan pada pekon dengan `L4` rendah.

Tanpa ini, dashboard keadilan akan menampilkan kesenjangan nol di semua kelompok dan uji keadilan menjadi hiasan belaka. Dengan ini, kesenjangan terdeteksi pada kisaran 8 sampai 15 poin persen — cukup untuk mendemonstrasikan bahwa alat auditnya memang bekerja.

### 4.7 Metrik yang dilaporkan

Metrik utama adalah **recall@k pada kapasitas verifikasi nyata**, bukan akurasi. Empat alasan independen:

1. **Anggaran.** Kapasitas verifikasi lapangan bersifat tetap; ini masalah alokasi sumber daya, bukan klasifikasi bebas.
2. **Prevalensi.** Bila 12% layak, model yang menjawab "semua tidak layak" mencapai akurasi 88% dengan recall 0%.
3. **Asimetri biaya.** Inclusion error membebani anggaran; exclusion error membebani orang miskin. Ketika tujuan kebijakan adalah menurunkan kemiskinan, exclusion error harus mendapat bobot lebih besar.
4. **Bentuk keluaran.** NADI menghasilkan antrean, dan antrean diukur dengan metrik pemeringkatan.

| Kelompok metrik | Isi |
|---|---|
| Diskriminasi | AUC (target **0,72 sampai 0,85**), Spearman rho |
| Anggaran nyata | `recall@100`, `recall@300`, `recall@500`, `precision@300`, `lift@300`, `exclusion_error@300` |
| Kalibrasi | Brier score, Expected Calibration Error 10 bin, reliability diagram per kecamatan |
| Keadilan | `EqualOpportunityGap` = selisih recall@k tertinggi dan terendah antar kelompok |
| Baseline | M1 targeting geografis, M0 logistic sepuluh fitur gaya PPI |
| Meta | versi model, tanggal latih, sidik jari dataset, prevalensi label, median umur data |

Rumus yang dipakai secara konsisten:

```
Exclusion Error (EE) = FN / (TP + FN) = 1 − Recall        # keterlewatan
Inclusion Error (IE) = FP / (TP + FP) = 1 − Precision     # kebocoran
Targeting Differential = TPR − FPR
Indeks CGH = pangsa transfer ke kelompok sasaran / pangsa populasi kelompok sasaran
```

Sifat penting yang harus disebut di dokumen metodologi: ketika kuota sama dengan prevalensi, **precision sama dengan recall secara konstruksi**, dan setiap exclusion error menghasilkan tepat satu inclusion error.

**AUC di atas 0,90 adalah alarm kebocoran, bukan prestasi.** Pipeline generator memperlakukannya sebagai kegagalan dan menaikkan derau. Angka rujukan: targeting geografis 0,59 sampai 0,68; indeks aset 0,55 sampai 0,75; PPI sepuluh pertanyaan 0,81; PMT terkalibrasi sempurna 0,85.

**Metrik keadilan yang dipilih adalah equal opportunity (paritas recall), bukan demographic parity.** Demographic parity keliru di sini karena base rate memang berbeda secara sah: memaksa proporsi penargetan yang sama antara desa (10,41%) dan kota (7,28%) berarti sengaja mengeksklusi keluarga miskin desa. Kelompok yang wajib diaudit: kecamatan, perdesaan versus perkotaan, jenis kelamin kepala keluarga, **kuintil ukuran keluarga** (wajib karena biasnya terdokumentasi), keberadaan anggota disabilitas, dan keberadaan lansia. Ambang alarm 10 poin persen.

Dua baseline **wajib dilaporkan berdampingan** dengan model utama. Bila LightGBM hanya sedikit mengungguli logistic sepuluh fitur, itu adalah informasi penting yang harus disampaikan, bukan kegagalan yang disembunyikan.

---

## 5. Desain Generator Data Sintetis

Bagian ini menanggung beban terbesar. Bila generator keliru, seluruh demo menjadi teater: angka evaluasi tampak hebat tetapi tidak mengukur apa pun.

### 5.1 Pipa enam tahap

```
Tahap 1  Kerangka wilayah nyata      131 desa Pringsewu, kode dan koordinat asli
Tahap 2  Variabel laten              L1..L5, disimpan tetapi tidak diberikan ke model
Tahap 3  Gaussian copula             struktur dependensi antar variabel teramati
Tahap 4  IPF / raking                paksa marginal cocok dengan angka BPS
Tahap 5  Dinamika panel              8 gelombang, guncangan, pemulihan, atrisi
Tahap 6  Penargetan program          dengan inclusion dan exclusion error yang disengaja
Tahap 7  Injeksi anomali             dengan kolom kebenaran dasar yang tidak diekspos
Tahap 8  Gerbang mutu                AUC 0,72-0,85, jika gagal ulangi dengan derau naik
```

### 5.2 Tahap 1 — kerangka wilayah nyata

Tidak ada wilayah fiktif. Seluruh 131 desa berasal dari `seed_desa_pringsewu.csv` dengan kode Kepmendagri, nama, status pekon/kelurahan, sentroid, dan luas dari BIG.

| Parameter | Nilai | Sumber |
|---|---|---|
| Jumlah keluarga dibangkitkan | 73.879 (desil 1 sampai 5) | DTSEN 2026 |
| Basis penduduk untuk kemiskinan | 416.579 jiwa (proyeksi BPS SP2020) | Diturunkan dari 31,66 ribu setara 7,60% |
| Garis kemiskinan | Rp583.425 per kapita per bulan | BPS 2024 |
| Rata-rata anggota keluarga | 4,62 | BPS Maret 2026 |

**Peringatan yang harus dipatuhi generator:** tiga angka penduduk beredar untuk Pringsewu dan ketiganya benar menurut definisinya. DTSEN 451.586, Dukcapil 444.834, proyeksi BPS 416.579. Angka kemiskinan BPS dihitung terhadap **proyeksi**, bukan terhadap DTSEN maupun Dukcapil. Memakai basis yang keliru menggeser seluruh sasaran kalibrasi sekitar satu setengah poin persen.

Keputusan cakupan: NADI hanya membangkitkan **desil 1 sampai 5** (73.879 keluarga), bukan seluruh 144.262 keluarga. Alasannya sistem penargetan kemiskinan tidak perlu memuat seluruh penduduk, cukup mereka yang berpeluang menjadi sasaran program. Ini sekaligus menurunkan kebutuhan komputasi tanpa mengurangi realisme.

Alokasi keluarga ke desa mengikuti bobot penduduk Dukcapil per kecamatan, kemudian dipecah ke desa dengan bobot proporsional luas dan status IDM. Pekon berstatus "Berkembang" diberi bobot kemiskinan lebih tinggi, sehingga 7 dari 10 pekon Pagelaran Utara dan 6 dari 13 pekon Pardasuka menjadi kantong kerentanan — persis seperti data IDM 2024 yang sesungguhnya.

### 5.3 Tahap 2 dan 3 — laten dan dependensi

Fitur teramati adalah fungsi berderau dari laten:

```
luas_lantai      = g(L1) + derau_1
indeks_aset      = h(L1, L5) + derau_2
daya_listrik     = diskretisasi(k(L1)) + kesalahan_pencatatan(L4)
pendidikan_kk    = m(L1) + derau_3
```

Struktur dependensi antar variabel teramati dibentuk dengan Gaussian copula. Korelasi yang dipakai — satu di antaranya empiris, sisanya asumsi yang didokumentasikan:

| Pasangan | rho | Status |
|---|---|---|
| indeks aset dengan konsumsi | **+0,37** | **Empiris** (Aiken et al. 2023, Afghanistan) |
| pendidikan KK dengan kapasitas pendapatan | +0,45 | Asumsi berdokumentasi |
| lantai tanah dengan tanpa jamban | +0,55 | Asumsi berdokumentasi |
| sektor pertanian dengan perdesaan | +0,60 | Asumsi berdokumentasi |

Korelasi 0,37 antara aset dan konsumsi adalah angka yang paling penting untuk dipertahankan. Bila terlalu tinggi, model berbasis aset akan tampak jauh lebih baik daripada di dunia nyata; kesimpulan desain yang ditarik dari demo menjadi salah.

### 5.4 Tahap 4 — raking ke marginal BPS

Iterative Proportional Fitting terhadap lima dimensi, dengan prioritas sumber Kabupaten lebih dulu, lalu Provinsi, lalu Nasional. Tahun jangkar 2024 dipakai konsisten agar tidak mencampur tahun.

| Dimensi | Target |
|---|---|
| Kecamatan (9) kali perdesaan/perkotaan | Distribusi penduduk Dukcapil per kecamatan |
| Ukuran keluarga 1 sampai 6+ | Rata-rata 4,62 jiwa |
| Jenis kelamin kepala keluarga | Pangsa KK perempuan |
| Kelas ekonomi (5 pita Bank Dunia) | 8,57 / 24,42 / 49,29 / 17,25 / 0,46 persen |
| Kelompok umur kepala keluarga | Piramida penduduk |

Sasaran verifikasi setelah raking: P0 gelombang 0 sama dengan **8,32%** (2024) dan menurun ke **7,60%** pada gelombang akhir, dengan Gini naik dari 0,266 ke 0,299. Reproduksi kedua tren yang berlawanan arah ini adalah uji paling ketat bahwa generator menangkap dinamika Pringsewu yang sesungguhnya, bukan sekadar rata-ratanya.

Garis kerentanan turunan yang dipakai, seluruhnya ditandai `is_derived`:

```
z      (garis kemiskinan)   = Rp   583.425   [BPS, terverifikasi]
1,5z   (garis kerentanan)   = Rp   875.138   [turunan]
3,5z   (batas aspiring MC)  = Rp 2.041.988   [turunan]
```

### 5.5 Tahap 5 — dinamika panel dan proses guncangan

Setiap gelombang, tiga hal terjadi berurutan.

**(a) Guncangan.** Laju kejadian tidak seragam:

| Jenis guncangan | Laju dasar per gelombang | Pengubah |
|---|---|---|
| `sakit_berat` | 1,2% | Naik dengan `L3`, dengan jumlah lansia, dan bila `cakupan_jkn` rendah |
| `kehilangan_pekerjaan` | 2,0% | Naik bila `kk_pekerjaan_rentan` |
| `gagal_panen` | 3,5% pada gelombang musim | Hanya untuk `kk_sektor_musiman`; **kovarian per kecamatan** |
| `kematian_pencari_nafkah` | 0,4% | Naik dengan usia KK |
| `bencana` | 0,8% | **Kovarian penuh per pekon** dari zona rawan |
| `kenaikan_harga_pangan` | Kejadian pada dua gelombang tertentu | **Kovarian seluruh kabupaten** |

Pembedaan kovarian versus idiosinkratik adalah inti desain, bukan detail. Ligon & Schechter menemukan guncangan agregat lebih penting daripada risiko idiosinkratik. Bila seluruh guncangan dibangkitkan independen antar keluarga, fitur `persen_miskin_wilayah` dan spatial lag menjadi tidak berdaya prediksi, dan salah satu keunggulan utama NADI hilang tanpa disadari.

Justifikasi bobot komponen makanan: makanan menyusun **74,70%** garis kemiskinan nasional Maret 2026, sehingga elastisitas terhadap harga pangan sangat tinggi. Guncangan harga pangan dimodelkan sebagai penurunan langsung `pengeluaran riil`, bukan sebagai kejadian probabilistik pada keluarga individual.

**(b) Dampak dan pemulihan.** Guncangan menurunkan pengeluaran sesuai keparahan, lalu pulih secara eksponensial dengan laju yang bergantung pada `L2_jaringan_sosial` dan `L5_akses_kredit_informal`. Keluarga dengan jaringan lemah pulih lebih lambat, sehingga guncangan sedang pun dapat menjatuhkan mereka melewati garis. Inilah mekanisme yang menciptakan **kemiskinan transien** — kategori yang mustahil muncul pada data cross-sectional.

**(c) Evolusi struktural.** Kondisi hunian membaik perlahan sesuai pertumbuhan `L1` dan intervensi yang diterima; komposisi keluarga berubah (kelahiran, anak tumbuh ke jenjang berikutnya, lansia meninggal); sebagian keluarga pecah atau pindah, menghasilkan atrisi realistis 1 sampai 2 persen per gelombang.

Desil dihitung ulang setiap gelombang dengan **derau PMT yang sengaja ditambahkan** ke pengeluaran sebelum pemeringkatan. Alasannya: desil DTSEN adalah hasil prediksi PMT, bukan pengeluaran sebenarnya. Tanpa derau ini, `desil_kesejahteraan` akan menjadi fungsi sempurna dari `pengeluaran_per_kapita`, dan seluruh analisis mismatch — yang justru bertumpu pada selisih antara keduanya — menjadi mustahil.

### 5.6 Tahap 6 — penargetan program dengan kesalahan yang disengaja

Ini bagian yang paling sering dilewatkan generator lain, dan justru bagian yang membuat modul Mismatch punya sesuatu untuk ditemukan. Empat sumber kesalahan ditirukan, keempatnya berasal dari cara kerja nyata:

| Sumber kesalahan | Mekanisme dalam generator | Besaran |
|---|---|---|
| **Kesalahan PMT** | Penargetan memakai desil berderau, bukan pengeluaran sebenarnya | Menghasilkan EE dan IE alami |
| **Data usang** | Sebagian keluarga ditargetkan berdasarkan kondisi 2 sampai 4 gelombang lalu | 25% populasi |
| **Hambatan administratif** | `ada_masalah_dokumen` memblokir kepesertaan meski layak | Sesuai prevalensi masalah dokumen |
| **Kuota dan inersia** | Kuota program terbatas; penerima lama bertahan meski kondisinya membaik | Rotasi hanya 10% per gelombang |

Sasaran kalibrasi: exclusion error pada cakupan 40% berada di kisaran **24 sampai 36 persen**, sesuai rentang yang dilaporkan Brown et al. untuk cut-off 0,4. Bila generator menghasilkan EE 5%, penargetannya terlalu sempurna dan modul Mismatch tidak akan punya kasus nyata untuk ditampilkan.

Sumber kesalahan keempat adalah yang paling instruktif untuk demo: keluarga yang **berhasil ditolong** tetap menerima bantuan sementara keluarga yang baru jatuh belum masuk. Ini bukan kecurangan siapa pun — ini konsekuensi struktural siklus data triwulanan, dan persis yang ingin ditunjukkan NADI kepada pengambil keputusan.

### 5.7 Tahap 7 — injeksi anomali dengan kebenaran dasar

Setiap anomali yang disisipkan menyimpan kolom `is_planted_anomaly` dan `anomaly_type` yang **tidak pernah diekspos** ke aplikasi. Kolom ini hanya dipakai untuk mengukur presisi dan recall detektor.

| Tipe anomali | Proporsi | Rujukan skala nyata |
|---|---|---|
| **Keluarga sangat rentan tanpa program apa pun** | **3,0%** | Skenario demo paling penting — kandidat exclusion error |
| Anggota meninggal masih aktif menerima | 1,2% | BPK menemukan 5.702 anggota bernama kosong di DTKS |
| Geotag di luar batas pekon | 2,0% | Kesalahan enumerasi lapangan |
| NIK duplikat lintas KK | 0,8% | BPKP 2020: 41.985 KPM duplikat |
| Desil 1 sampai 4 dengan listrik 2.200 VA ke atas | 0,5% | Kontradiksi kondisi |
| Koordinat duplikat persis pada lebih dari 3 KK | 0,4% | Penyalinan koordinat oleh petugas |
| Penerima berprofesi ASN atau BUMN | 0,3% | Kemensos 2025-2026 menemukan lebih dari 100.000 penerima anomali |

Angka rujukan nasional dicantumkan bukan sebagai hiasan melainkan sebagai pembenaran proporsi: bila proporsi anomali dikarang, juri berhak menanyakan dari mana angkanya.

### 5.8 Tahap 8 — gerbang mutu otomatis

Pipeline **membatalkan sendiri** hasilnya bila kriteria berikut tidak terpenuhi:

| Kriteria | Ambang | Tindakan bila gagal |
|---|---|---|
| AUC model utama pada set uji | 0,72 sampai 0,85 | Di atas 0,90 naikkan derau laten; di bawah 0,65 turunkan derau |
| R kuadrat fitur terhadap ln pengeluaran | 0,45 sampai 0,55 | Sesuaikan sigma derau observasi |
| P0 gelombang 0 | 8,32% plus minus 0,3 pp | Ulangi raking |
| Gini gelombang akhir | 0,299 plus minus 0,01 | Sesuaikan sebaran L1 |
| Exclusion error penargetan cakupan 40% | 24 sampai 36% | Sesuaikan derau PMT dan laju rotasi |
| Kesenjangan keadilan terdeteksi | 8 sampai 15 pp | Sesuaikan pola derau label |
| KSComplement per variabel | di atas 0,90 | Periksa marginal |
| CorrelationSimilarity | di atas 0,85 | Periksa copula |

**Urutan yang tidak boleh dibalik:** bangkitkan populasi penuh lebih dulu, baru lakukan pemisahan latih-uji. Oversampling atau SMOTE **selalu setelah** pemisahan; melakukannya sebelum pemisahan membuat sampel sintetis nyaris identik dengan titik uji dan menghasilkan akurasi yang menggelembung.

### 5.9 Reproduktibilitas

Seluruh generator dikendalikan satu `seed` yang disimpan bersama `sidik_jari_dataset` (hash SHA-256 atas parameter dan keluaran). Setiap angka acuan berada di satu berkas parameter dengan sumbernya tercantum per baris — sehingga ketika juri bertanya "dari mana angka ini", jawabannya dapat ditunjuk pada satu baris, bukan dicari di antara ribuan baris kode.

Label **"DATA SINTETIS — BUKAN DATA RIIL"** ditempelkan permanen dan mencolok di seluruh antarmuka, serta disisipkan sebagai kolom konstanta pada setiap ekspor data.

---

## 6. Katalog Program dan Aturan Pencocokan

### 6.1 Struktur basis pengetahuan

Empat tabel yang saling terkait, seluruhnya di-seed dari `docs/research/02-katalog-program-intervensi.md`:

```
opd (30 baris)  <--  program (28 baris)  -->  program_manfaat (komponen dan nominal)
                          ^
                          |  banyak-ke-banyak
                     faktor_risiko (20 baris, R01-R20)
```

Kolom kritis pada `program`:

| Kolom | Isi | Kegunaan |
|---|---|---|
| `desil_min`, `desil_max` | Rentang kelayakan | Pencocokan otomatis dalam satu query |
| `tingkat_eksekusi` | `pusat_disalurkan_di_daerah` / `apbd_daerah` / `dana_desa` / `mandiri_online` | Menentukan apakah pengguna kabupaten dapat bertindak atau hanya memantau |
| `basis_penerima` | `keluarga` / `individu` / `lokasi` | Menentukan tabel kepesertaan yang dipakai |
| `status_aktif` | `aktif` / `tidak_pasti` / `berhenti` | BLT Kesra 2026 berstatus `tidak_pasti`; antarmuka tidak menampilkan jadwal maupun nominalnya |
| `syarat` | JSONB berisi ekspresi aturan | Dieksekusi mesin, lihat 6.2 |

### 6.2 Skema aturan kelayakan yang dieksekusi mesin

Aturan disimpan sebagai JSON, bukan kode. Alasannya tiga: dapat diubah operator tanpa deploy ulang, dapat diaudit oleh non-programmer, dan dapat diterjemahkan otomatis menjadi kalimat penjelasan.

```json
{
  "semua": [
    { "fitur": "desil_kesejahteraan", "operator": "antara", "nilai": [1, 2] },
    { "salah_satu": [
        { "fitur": "ada_ibu_hamil",          "operator": "adalah", "nilai": true },
        { "fitur": "jumlah_balita",          "operator": ">=",     "nilai": 1 },
        { "fitur": "jumlah_anak_usia_sekolah","operator": ">=",    "nilai": 1 },
        { "fitur": "jumlah_lansia",          "operator": ">=",     "nilai": 1 },
        { "fitur": "jumlah_disabilitas",     "operator": ">=",     "nilai": 1 }
    ]},
    { "tidak": { "fitur": "ada_masalah_dokumen", "operator": "adalah", "nilai": true } }
  ]
}
```

Operator yang didukung: `==`, `!=`, `<`, `<=`, `>`, `>=`, `antara`, `termasuk`, `adalah`. Penggabung: `semua` (AND), `salah_satu` (OR), `tidak` (NOT). Evaluator bersifat vektorisasi terhadap DataFrame sehingga 73.879 keluarga dinilai untuk 28 program dalam satu operasi.

Setiap butir aturan membawa fungsi `jelaskan_syarat` yang menghasilkan kalimat Indonesia, sehingga hasil evaluasi tampil sebagai daftar terperiksa:

> **PKH — memenuhi syarat**
> ✓ Desil kesejahteraan 2 (syarat: 1 sampai 2)
> ✓ Terdapat 1 anak usia sekolah
> ✓ Tidak ada masalah dokumen kependudukan

> **Sekolah Rakyat — belum memenuhi syarat**
> ✗ Desil kesejahteraan 3 (syarat: 1 sampai 2; desil 3 hanya bila kuota tersisa)

### 6.3 Matriks faktor risiko

Dua puluh faktor risiko R01 sampai R20 menghubungkan fitur model dengan program dan OPD. Kolom `ekspresi_deteksi` berisi JSON aturan dengan skema yang sama seperti 6.2, sehingga faktor risiko dinilai dengan evaluator yang sama.

| Kode | Faktor risiko | Fitur pemicu utama | Program | OPD Pringsewu |
|---|---|---|---|---|
| R01 | Miskin ekstrem | `rasio_garis_kemiskinan < 1` dan `desil = 1` | PKH, Sembako, BLT-DD, Bantuan Pangan Beras | Dinsos, DPMP |
| R02 | Rawan pangan | `pengeluaran pangan tinggi`, `tanpa_bantuan_apa_pun` | Sembako, MBG, ketahanan pangan Dana Desa (min 20%) | Dinsos, DKP, DPMP |
| R03 | Balita gizi bermasalah | `ada_gizi_bermasalah` | PMT pangan lokal, MBG, Posyandu ILP | Dinkes, DPMP |
| R04 | Ibu hamil risiko tinggi | `ada_ibu_hamil` dan `tanpa_jkn_sama_sekali` | PMT ibu hamil, PKH ibu hamil, PBI-JKN | Dinkes, Dinsos |
| R05 | Anak putus sekolah | `ada_anak_putus_sekolah` | PIP, PKH pendidikan, **Sekolah Rakyat** | Disdikbud, Dinsos |
| R06 | Tidak lanjut pendidikan tinggi | Lulusan SMA desil 1 sampai 3 | KIP Kuliah | Disdikbud |
| R07 | Tanpa jaminan kesehatan | `tanpa_jkn_sama_sekali` atau `cakupan_jkn < 1` | PBI-JKN Pusat (desil 1 sampai 4), PBI Daerah APBD | Dinsos, Dinkes |
| R08 | Rumah tidak layak huni | `jumlah_kriteria_rtlh >= 1` | BSPS Rp20 juta, RST Rp20 juta, Rutilahu APBD, Dana Desa | PUPR, Dinsos, DPMP |
| R09 | Tanpa sanitasi layak | `sanitasi_tidak_layak` | SANIMAS DAK, STBM, jambanisasi Dana Desa | PUPR, Dinkes, DPMP |
| R10 | Tanpa air minum layak | `air_minum_tidak_layak` | PAMSIMAS, DAK Air Minum | PUPR, DPMP |
| R11 | Lansia telantar | `kk_lansia` dan `tidak_ada_yang_bekerja` | PKH lansia, ATENSI, Posyandu ILP lansia | Dinsos, Dinkes |
| R12 | Penyandang disabilitas | `jumlah_disabilitas >= 1` | PKH disabilitas berat, ATENSI (kursi roda, alat bantu dengar, motor roda tiga) | Dinsos, Disnakertrans |
| R13 | Pengangguran | `tidak_ada_yang_bekerja` atau `kk_pekerjaan_rentan` | Prakerja, BLK/BPVP, Padat Karya Tunai Desa | Disnakertrans, DPMP |
| R14 | Usaha mikro tanpa modal | `jumlah_usaha_keluarga >= 1` dan desil rendah | KUR Super Mikro, PENA Rp4,9 juta, PPSE, KUBE | Diskoperindag, Dinsos |
| R15 | Pekerja informal tanpa perlindungan | `kk_pekerjaan_rentan` dan tanpa BPJS TK | **BPJS TK Pekerja Rentan Rp16.800 per bulan** | Disnakertrans, Dinsos |
| R16 | Tanpa dokumen kependudukan | `ada_masalah_dokumen` | Jemput bola Dukcapil — **prasyarat semua bansos** | Disdukcapil |
| R17 | Perempuan kepala keluarga | `kk_perempuan` | BLT-DD (kriteria eksplisit), PKH, PENA, KUBE | Dinsos, DPMP |
| R18 | Anggota sakit kronis | `ada_penyakit_kronis` atau `ada_penyakit_biaya_tinggi` | BLT-DD (kriteria eksplisit), PBI-JKN, ATENSI | DPMP, Dinsos |
| R19 | Kehilangan mata pencaharian | `ada_guncangan_pendapatan` | BLT-DD (kriteria eksplisit), Prakerja, BTT Dinsos, PKTD | DPMP, Dinsos, Disnakertrans |
| R20 | Terdampak bencana | `ada_guncangan_bencana` | Penanganan korban bencana, ATENSI | Dinsos, BPBD |

Catatan penting soal nomenklatur OPD: Pringsewu **tidak** memiliki Dinas Perumahan dan Kawasan Permukiman terpisah — urusan perumahan melekat di Dinas PUPR. Nomenklaturnya juga khas: "Diskoperindag" bukan Dinas Koperasi UKM, dan "DPMP" memakai kata **Pekon**, bukan Desa. Memakai template OPD generik akan langsung terlihat sebagai kelemahan riset.

### 6.4 Cara rekomendasi disusun

Urutan yang mengikat:

```
1. Hitung skor kerentanan (Skor B)                     -> mengurutkan antrean
2. Deteksi faktor risiko aktif lewat ekspresi_deteksi   -> menjelaskan mengapa
3. Ambil program yang terhubung ke faktor risiko aktif  -> menyarankan apa
4. Saring dengan aturan kelayakan (6.2)                 -> memastikan sah
5. Kurangi program yang sudah diterima                  -> mencegah usulan ganda
6. Urutkan berdasarkan (dampak x kelayakan) / biaya     -> memprioritaskan
7. Lampirkan OPD penanggung jawab dan estimasi biaya    -> menugaskan
```

**Rekomendasi program datang dari aturan kelayakan, bukan dari SHAP.** SHAP menjelaskan mengapa skor tinggi; aturan kelayakan menentukan program apa yang sah. Mencampurnya akan menghasilkan rekomendasi yang tampak canggih tetapi melanggar juknis.

---

## 7. Desain Deteksi Mismatch dan Anomali

### 7.1 Tiga lapis, dengan urutan yang mengikat

| Lapis | Metode | Sifat keluaran | Prioritas |
|---|---|---|---|
| **1. Berbasis aturan** | Deterministik | **Flag bernama** dengan tingkat keparahan | Tertinggi |
| **2. Statistik tanpa penyelia** | Isolation Forest, Local Outlier Factor | Skor keanehan | Menengah |
| **3. Analisis residual** | Selisih skor model dengan implikasi desil | Kandidat EE dan IE | **Paling bernilai** |

Lapis pertama menghasilkan flag **bernama**, bukan skor buram, karena harus dapat dibacakan di Musyawarah Pekon. Kalimat "sistem menandai keluarga ini dengan skor keanehan 0,87" tidak dapat dipertanggungjawabkan di hadapan warga; kalimat "tercatat satu anggota telah meninggal namun masih terdaftar aktif" dapat.

### 7.2 Lapis 1 — aturan deterministik

**Kelompok A: Identitas** (keparahan `blocking`)

| Kode | Aturan |
|---|---|
| A01 | NIK bukan 16 digit atau gagal uji struktur |
| A02 | NIK duplikat lintas kartu keluarga |
| A03 | NIK sama dengan nama berbeda |
| A04 | Nama kosong atau satu karakter |
| A05 | `status_padan_dukcapil` bernilai tidak padan |
| A06 | Usia lebih dari 120 tahun atau tahun lahir di masa depan |
| A07 | Individu terdaftar pada lebih dari satu KK aktif |

**Kelompok B: Kontradiksi kondisi** (keparahan `review`)

| Kode | Aturan | Alasan |
|---|---|---|
| B01 | Desil 1 sampai 4 dengan daya listrik 2.200 VA ke atas | Daya adalah prediktor kesejahteraan terkuat dalam PMT |
| B02 | Desil 1 sampai 4 dengan mobil atau lahan lebih dari 2 hektar | Kontradiksi aset |
| B03 | Pekerjaan ASN, TNI, Polri, atau BUMN dengan desil 1 sampai 4 | Kemensos menemukan lebih dari 100.000 kasus serupa |
| B04 | Menerima 3 program atau lebih sekaligus | Perlu diperiksa, bukan otomatis salah |
| B05 | `jumlah_anggota` bernilai 0 atau lebih dari 20 | Kesalahan pencatatan |
| B06 | Kepala keluarga berusia di bawah 15 tahun | Kesalahan relasi |
| B07 | `luas_lantai_per_kapita` di atas 100 m2 dengan desil rendah | Kontradiksi hunian |

**Kelompok C: Kelayakan berjalan** (keparahan `review`)

C01 anggota berstatus meninggal masih aktif menerima; C02 pindah keluar kabupaten; C03 tanpa penyaluran lebih dari dua siklus; C04 rekening atau KKS tidak aktif.

**Kelompok D: Spasial** (keparahan `info`)

D01 geotag di luar poligon pekon terdaftar; D02 koordinat duplikat persis pada lebih dari 3 KK; D03 koordinat bernilai nol atau kosong.

### 7.3 Lapis 2 — statistik tanpa penyelia

**Isolation Forest** pada ruang fitur ternormalisasi, dengan parameter `contamination` sebagai parameter paling kritis — disetel ke 0,05 dan diekspos di panel administrator. **Local Outlier Factor** dijalankan **di dalam grup pekon**, bukan pada seluruh kabupaten, karena yang dicari adalah anomali **kontekstual**: keluarga yang aneh dibandingkan tetangganya, bukan dibandingkan seluruh kabupaten. Sebuah keluarga berlantai tanah di Pagelaran Utara adalah hal biasa; keluarga yang sama di Pringsewu kota adalah sinyal.

**Autoencoder tidak dipakai pada versi pertama.** Kemampuan menjelaskannya buruk, dan flag yang tidak dapat dijelaskan tidak dapat diverifikasi manusia.

### 7.4 Lapis 3 — analisis residual (yang paling bernilai)

```
implied_kerentanan = f(desil_kesejahteraan)        # implikasi desil DTSEN
r = skor_kerentanan_model − implied_kerentanan

r >> 0  -->  KANDIDAT EXCLUSION ERROR  -->  antrean verifikasi prioritas
r << 0  -->  KANDIDAT INCLUSION ERROR  -->  antrean audit
```

Tiga penyempurnaan yang membuat lapis ini bekerja:

1. **Isolation Forest dijalankan pada vektor residual**, bukan pada fitur mentah. Yang dicari bukan keluarga yang aneh, melainkan keluarga yang **penilaiannya** aneh.
2. **Agregasi level pekon.** Rata-rata `|r|` yang tinggi pada satu pekon menandakan masalah **sistemik** — kualitas enumerasi buruk atau data usang — bukan masalah per keluarga. Ini menghasilkan rekomendasi yang berbeda sama sekali: bukan verifikasi 30 keluarga, melainkan pemutakhiran data satu pekon.
3. **Flag selisih model versus musyawarah.** Kolom `peringkat_musdes` dibandingkan dengan peringkat model. Ketidaksepakatan ditampilkan sebagai item yang layak ditinjau, bukan sebagai kesalahan salah satu pihak. Dasarnya temuan Alatas et al. bahwa keduanya mengukur konstruk berbeda.

### 7.5 Deteksi perubahan kondisi yang belum ditindaklanjuti

Kelas kasus tersendiri yang hanya mungkin karena ada panel waktu:

| Pemicu | Tindakan yang diusulkan |
|---|---|
| `delta_rasio_kemiskinan` turun lebih dari 15% selama dua gelombang berturut-turut tanpa perubahan kepesertaan | Verifikasi ulang; kandidat program baru |
| Guncangan tercatat lebih dari satu gelombang lalu tanpa intervensi apa pun | Eskalasi ke OPD sesuai jenis guncangan |
| `umur_data_bulan` lebih dari 12 pada keluarga skor tinggi | Prioritas pemutakhiran data |
| Kondisi membaik melewati ambang graduasi selama tiga gelombang | Kandidat graduasi; usul rotasi kuota |
| Anak mencapai usia sekolah tanpa terdaftar PIP | Rujuk Disdikbud |
| PBI-JKN nonaktif pada keluarga desil 1 sampai 4 | Usul reaktivasi — masalah nyata Pringsewu dengan sekitar 62.000 peserta terdampak |

### 7.6 Tata kelola flag

Empat aturan yang tidak dapat ditawar:

1. **Tidak ada penghapusan otomatis.** Setiap flag adalah hipotesis untuk diverifikasi manusia, bukan keputusan.
2. **Audit dua sisi.** Sistem yang hanya mencari kebocoran akan memperburuk exclusion error. Rasio kasus EE terhadap IE dipantau; bila kasus IE mendominasi antrean, ambang disesuaikan.
3. **Presisi flag dilacak berkala** lewat kolom `setuju_dengan_sistem` pada tabel verifikasi. Bila presisi satu jenis flag turun di bawah 30 persen, aturannya diperketat atau dinonaktifkan.
4. **Prioritas antrean bukan skor tunggal.** `skor_prioritas` menggabungkan keparahan flag, skor kerentanan, dan umur kasus, sehingga kasus lama tidak tenggelam selamanya di bawah kasus baru berskor tinggi.

---

## 8. Desain What-if Policy Simulator

### 8.1 Garis batas kejujuran

Simulator ini **bukan model kausal**. Ia tidak dapat menjawab "berapa penurunan kemiskinan bila PKH dinaikkan", karena data sintetis tidak memuat efek kausal yang teridentifikasi — dan bahkan data nyata pun membutuhkan desain evaluasi tersendiri.

Yang **boleh** dijawab simulator:

| Pertanyaan | Sifat |
|---|---|
| Berapa keluarga tercakup bila ambang desil digeser dari 2 ke 3? | Aritmetika penghitungan |
| Berapa biaya menaikkan cakupan PBI-JKN Daerah sebesar 5.000 jiwa? | Aritmetika biaya |
| Bila kapasitas verifikasi naik dari 300 ke 500 per triwulan, berapa recall bertambah? | Kurva metrik terukur |
| Bila pagu Dana Desa satu pekon dialokasikan dengan komposisi tertentu, berapa KPM tercakup BLT-DD? | Aritmetika terbatas pagu |
| Berapa tahun backlog RTLH selesai pada laju A, B, atau C? | Proyeksi aritmetika |

Yang **tidak boleh** dijawab: prediksi angka kemiskinan sebagai akibat kebijakan, klaim efektivitas relatif antar program, dan proyeksi perubahan perilaku penerima.

### 8.2 Empat mesin perhitungan

**(a) Kalkulator cakupan dan biaya.** Diberi aturan kelayakan dan pagu, hasilkan `jumlah_layak`, `jumlah_tercakup`, `biaya_total`, `sisa_pagu`, dan **daftar keluarga yang layak namun tidak tercakup**. Keluaran terakhir itu yang paling berharga: ia mengubah keterbatasan anggaran dari angka abstrak menjadi daftar nyata.

**(b) Simulator Dana Desa per pekon.** Dana Desa 2026 memiliki pagu terikat: BLT maksimal 15 persen, ketahanan pangan minimal 20 persen, dengan delapan fokus penggunaan. Kalkulator menerima pagu satu pekon lalu menghasilkan komposisi alokasi, jumlah KPM tercakup BLT-DD dengan batas Rp300.000 per bulan selama maksimal tiga bulan, dan sisa untuk PKTD, stunting, serta KDMP. Ini instrumen paling fleksibel yang benar-benar dapat diarahkan pemerintah kabupaten.

**(c) Simulator blending RTLH.** Empat sumber dana dengan nominal berbeda: BSPS APBN Rp20 juta, RST Kemensos Rp20 juta, Rutilahu APBD sekitar Rp15 juta, dan Dana Desa. Diberi backlog 1.700 unit dan kapasitas per sumber, hitung berapa tahun backlog selesai per skenario. Skenario dasar 80 unit per tahun menghasilkan 21 tahun — angka yang membuat pertanyaan kebijakan menjadi konkret.

**(d) Kurva kapasitas verifikasi.** Plot `recall@k` terhadap `k` untuk seluruh rentang kapasitas. Kurva ini menjawab pertanyaan yang paling sering diajukan pimpinan — "kalau saya tambah petugas, apa untungnya?" — dan menjawabnya dengan kurva yang melandai, bukan janji linear.

### 8.3 Penyajian ketidakpastian

| Mekanisme | Wujud |
|---|---|
| **Rentang, bukan titik** | "Antara 4.200 dan 5.100 keluarga", diperoleh dari bootstrap 500 replikasi |
| **Badge keyakinan pada setiap nominal** | Hijau `pasti`, kuning `cukup_kuat`, jingga `perkiraan`; item `tidak_ditemukan` tidak ditampilkan sama sekali |
| **Daftar asumsi eksplisit** | Setiap hasil membawa panel "Asumsi yang dipakai" yang dapat dibuka |
| **Analisis sensitivitas satu klik** | Tombol "Bagaimana bila asumsi ini meleset 20 persen?" |

### 8.4 Yang selalu ditampilkan di bawah setiap hasil

> Simulasi ini adalah **perhitungan aritmetika cakupan dan biaya** berdasarkan aturan kelayakan program dan pagu yang dimasukkan. Simulasi ini **bukan** prediksi dampak kebijakan dan tidak mengandung klaim sebab-akibat. Angka nominal program mengikuti sumber yang tercantum, dengan tingkat keyakinan yang ditandai pada setiap angka.

---

## 9. Desain AI Copilot dan RAG

### 9.1 Peran yang sempit dan tegas

AI Policy Copilot adalah **antarmuka bahasa alami untuk data dan regulasi yang sudah ada di dalam sistem**, bukan penasihat kebijakan otonom. Ia menjawab pertanyaan tentang isi basis data dan basis pengetahuan; ia **tidak** menghasilkan penilaian baru tentang keluarga mana pun.

### 9.2 Sumber pengetahuan

| Korpus | Isi | Sifat |
|---|---|---|
| **K1 Regulasi** | Perban BPS 6/2025, Permensos 3/2021 dan 5/2021, Permendes 16/2026, Permendagri 53/2020, UU PDP 27/2022, Permen PKP 10/2025 | Publik, statis |
| **K2 Katalog program** | 28 program, nominal, syarat, OPD, dasar hukum | Publik, terstruktur |
| **K3 Statistik daerah** | Profil Pringsewu, 131 desa, IDM, kemiskinan, ketenagakerjaan | Publik, terstruktur |
| **K4 Metodologi NADI** | Definisi fitur, label, metrik, keterbatasan model | Internal, aman untuk publik |
| **K5 Agregat sistem** | Statistik hasil kueri terparameter — jumlah, rata-rata, distribusi | Dihitung saat itu juga, **tanpa identitas** |

**K5 tidak pernah berupa baris data mentah.** Ketika pengguna bertanya "berapa keluarga berisiko tinggi di Pagelaran Utara", sistem menjalankan kueri terparameter yang sudah ditetapkan sebelumnya dan mengirim **hasil agregatnya** ke LLM, bukan data yang mendasarinya.

### 9.3 Strategi retrieval

Hibrida BM25 dengan penyaringan metadata — bukan embedding vektor, dan ini keputusan sadar.

| Alasan | Penjelasan |
|---|---|
| Korpus kecil dan terstruktur | Kurang dari 2.000 potongan; keunggulan pencarian semantik tipis |
| Istilah regulasi bersifat leksikal | "Pasal 15 ayat 3", "desil 1 sampai 4", "Rp20.000.000" — pencocokan tepat lebih penting daripada kemiripan makna |
| Tanpa ketergantungan eksternal | Tidak ada layanan embedding, sehingga tidak ada data yang keluar untuk indeksasi |
| Dapat dijelaskan | Sistem dapat menunjukkan kata mana yang memicu pengambilan |

Alur kerja: normalisasi pertanyaan dan ekstraksi entitas (wilayah, program, tahun) sebagai filter metadata; BM25 mengambil 20 kandidat; pemeringkatan ulang berdasarkan otoritas sumber (regulasi mengungguli berita) dan kesegaran; ambil lima potongan teratas; **wajib menyertakan sitasi** berupa nama dokumen, pasal atau tabel, dan URL.

### 9.4 Guardrail

**Yang BOLEH dijawab:**

- Isi regulasi dan program, disertai sitasi
- Statistik agregat wilayah dari K5
- Penjelasan metodologi NADI beserta keterbatasannya
- Penerjemahan hasil model menjadi kalimat awam
- Penyusunan draf dokumen TKPKD — RPKD, Rencana Aksi Tahunan, bahan rapat koordinasi — dari data agregat

**Yang TIDAK BOLEH dijawab**, dengan penolakan berpola tetap:

| Larangan | Alasan |
|---|---|
| Menyebut identitas keluarga atau individu | UU PDP; prinsip minimisasi data |
| Menilai kelayakan satu keluarga | Itu tugas mesin aturan yang dapat diaudit, bukan LLM |
| Merekomendasikan pencabutan bantuan | Batas tegas NADI |
| Memberi nominal berstatus `tidak_ditemukan` | Mencegah halusinasi angka bansos — area yang penuh konten spam dan hoaks |
| Memprediksi kebijakan pemerintah pusat | Di luar cakupan bukti |
| Klaim kausal atas efektivitas program | Tidak ada desain evaluasi yang mendukungnya |
| Menjawab pertanyaan faktual tanpa sumber | Setiap klaim faktual wajib bersitasi |

### 9.5 Jaminan tidak ada data pribadi keluar

Lima lapis, berurutan:

```
Lapis 1  Pseudonimisasi di pangkal : NIK dan KK asli tidak pernah masuk basis data
Lapis 2  Daftar-putih kueri        : hanya kueri agregat terparameter yang boleh
                                     memberi konteks; tidak ada SQL bebas
Lapis 3  Penyaring keluar          : regex NIK 16 digit, nomor KK, nomor telepon,
                                     nama diri, dan koordinat presisi tinggi diperiksa
                                     pada payload SEBELUM dikirim
Lapis 4  Ambang k-anonimitas       : agregat dengan n kurang dari 10 ditolak dan
                                     diganti "jumlah terlalu kecil untuk ditampilkan"
Lapis 5  Pencatatan penuh          : seluruh prompt dan respons masuk jejak_audit
                                     dengan hash, tanpa isi sensitif
```

Lapis 3 adalah jaring pengaman terakhir dan diuji dengan kasus uji khusus: bila regex menemukan pola identitas pada payload, permintaan **dibatalkan** dan dicatat sebagai insiden — bukan sekadar disunting diam-diam.

Arsitektur penyedia LLM sudah berlapis: penyedia kompatibel OpenAI sebagai utama, **penyedia templat sebagai cadangan** yang menghasilkan jawaban dari templat deterministik tanpa jaringan sama sekali, dengan pemutus arus di antaranya. Konsekuensi desain yang penting: **seluruh fitur inti NADI tetap berfungsi tanpa LLM.** Copilot adalah lapisan kenyamanan, bukan ketergantungan. Bila layanan LLM mati saat demo, skor, rekomendasi, deteksi mismatch, dan simulator tetap berjalan.

### 9.6 Penanganan penjelasan skor

Copilot **tidak menghitung** penjelasan. Ia menerima keluaran TreeSHAP yang sudah dikelompokkan per dimensi fitur, lalu menyusunnya menjadi kalimat Indonesia yang wajar. Dua kaidah mengikat:

1. **SHAP dilaporkan pada level kelompok fitur** (hunian, aset, pekerjaan, pendidikan, kesehatan), bukan fitur individual. Alasannya masalah korelasi fitur dan *path dependency* pada TreeSHAP: perhitungan probabilitas jalur mengandaikan variabel pemisah saling bebas, sedangkan variabel DTSEN sangat berkorelasi.
2. **Disclaimer non-kausal wajib menyertai setiap tampilan SHAP:** "Menjelaskan cara model menghitung skor, bukan sebab-akibat."

Counterfactual **dibalik arahnya**. Framing yang dilarang: "agar layak, keluarga ini perlu ...". Framing itu menyalahkan keluarga miskin dan memicu gaming — merusak lantai rumah agar tampak miskin adalah masalah nyata yang terdokumentasi dalam literatur PMT. Framing yang dipakai:

> "Bila keluarga ini terdaftar PBI-JKN, skor risiko turun dari 74 ke 61."
> "Data yang bila diperbarui paling mengubah skor: status pekerjaan kepala keluarga, terakhir diperbarui 14 bulan lalu."

Dengan pembalikan ini counterfactual menjadi **alat prioritisasi verifikasi data dan alat penilaian program**, bukan tuntutan kepada warga.

---

## 10. Perbandingan Jujur NADI dan Sistem Eksisting

### 10.1 Versi ringkas untuk satu slide

| Kelompok sistem | Prediktif risiko KE DEPAN | Penjelasan PER KELUARGA | Rekomendasi ke OPD SPESIFIK | Simulasi WHAT-IF | Monitoring OUTCOME KELUARGA |
|---|:--:|:--:|:--:|:--:|:--:|
| DTSEN / SIKS-NG (data dan penyaluran) | Tidak | Tidak | Tidak | Tidak | Tidak |
| SEPAKAT (perencanaan wilayah) | Tidak | Tidak | Sebagian (level wilayah) | Sebagian (alokasi anggaran) | Ya (level agregat) |
| SIMNANGKIS DIY / SIPINTER Purbalingga | Tidak | Tidak | **Ya** | Tidak | Sebagian (output dan anggaran) |
| SIGA-KRS / e-PKH (skrining dan kepatuhan) | Sebagian (berbasis aturan) | Ya (aturan) | Tidak | Tidak | Ya (terbatas domain) |
| **NADI (usulan)** | **Ya** | **Ya** | **Ya** | **Ya** | **Ya** |

**Catatan wajib di bawah slide:**

> Penilaian berdasarkan bukti yang tersedia publik per Agustus 2026. Tanda "Tidak" berarti tidak ditemukan bukti publik, bukan bukti ketiadaan. Sistem yang dibandingkan memiliki mandat berbeda — ini bukan penilaian mutu.

### 10.2 Klaim yang HARUS DIHINDARI dan pematahnya

Bagian ini ada karena setiap klaim di bawah dapat dipatahkan juri dalam satu kalimat.

| Klaim berbahaya | Pematah |
|---|---|
| "Belum ada AI/ML untuk kemiskinan di Indonesia" | arXiv 2503.04300 (spatial ML pada Susenas-DTKS); Wobcke & Mariyah 2023 di *Statistical Journal of the IAOS* |
| "Belum ada yang memprediksi kemiskinan" | PMT **adalah** model prediktif — dipakai P3KE, DTSEN, Listahanan, NSER Pakistan, SISBEN Kolombia |
| "Belum ada yang menghubungkan data ke perencanaan dan anggaran" | SEPAKAT Bappenas sejak 2018, dengan modul Perencanaan, Penganggaran, Pemantauan, dan Evaluasi |
| "Belum ada koordinasi intervensi lintas OPD berbasis sistem" | SIMNANGKIS DIY; SIPINTER Purbalingga sejak 21 Juli 2026 |
| "Belum ada data by-name-by-address dengan geolokasi" | Smart Kampung Banyuwangi melakukan geokoding GPS rumah keluarga miskin |
| "Belum ada monitoring keluarga penerima" | e-PKH verifikasi komitmen; kondisionalitas Bolsa Familia |
| "Warga belum bisa tahu skornya" | Pakistan BISP membuka pengecekan skor PMT lewat CNIC |
| "NADI mematuhi regulasi AI Indonesia" | Belum ada Perpres AI yang terbit; SE Kominfo 9/2023 tidak bersanksi. Yang mengikat hanya **UU PDP** |
| "Belum ada skor kesejahteraan per keluarga" | Carik Jakarta memiliki Indeks Ekonomi/Kemiskinan dan Indeks Pembangunan Keluarga |

### 10.3 Rumusan kebaruan yang aman

> Kami tidak mengklaim NADI adalah sistem data kemiskinan pertama di Indonesia. Kami memetakan 13 sistem Indonesia dan 11 sistem internasional. Semuanya berhenti sebelum satu langkah yang sama: **menjelaskan risiko per keluarga dan menutup lingkaran menuju tindakan.**

Kebaruan diletakkan pada **kombinasi**, bukan pada komponen tunggal. Tiga celah yang tidak ditemukan pada satu pun dari 24 sistem yang diteliti:

1. **Explainability per keluarga yang disajikan kepada operator dan warga.** Pakistan menampilkan skor tetapi bukan alasannya; SyRI menyembunyikannya dan justru karena itu dilarang pengadilan.
2. **Lingkaran tertutup prediksi ke intervensi ke outcome ke umpan balik.** Tidak satu pun sistem mencatat intervensi kembali sebagai data evaluasi.
3. **Simulasi what-if.** Hanya ditemukan sebagai kemampuan parsial pada modul Penganggaran SEPAKAT, tanpa bukti publik adanya perbandingan skenario.

---

## 11. Kepatuhan dan Etika

### 11.1 UU PDP 27/2022 — kewajiban, bukan pilihan

| Pasal | Kewajiban | Implementasi NADI |
|---|---|---|
| **Pasal 10** | Hak mengajukan keberatan atas keputusan yang **hanya** didasarkan pemrosesan otomatis, termasuk pemrofilan | Tombol "Saya tidak setuju" pada setiap kartu keluarga yang membuat entri di tabel `keberatan`; manusia selalu menjadi pemutus |
| **Pasal 20 ayat 2 huruf c dan e** | Basis legal pemrosesan | Kewajiban hukum dan pelaksanaan tugas kepentingan publik — **bukan** persetujuan, karena persetujuan tidak bermakna dalam relasi kuasa penerima bantuan |
| **Pasal 34** | Penilaian dampak wajib bila pemrosesan berisiko tinggi | NADI memicu hampir seluruh kriteria: skala besar, pemrofilan sistematis dan berkelanjutan, data anak, keputusan berdampak signifikan. **Kerangka DPIA menjadi deliverable, bukan lampiran opsional** |
| Perekaman kegiatan | Seluruh kegiatan pemrosesan wajib terekam | Tabel `jejak_audit` |

Catatan status regulasi yang harus akurat di slide: **belum ada Perpres AI yang terbit** per Agustus 2026. SE Kominfo 9/2023 tentang Etika Kecerdasan Artifisial berbentuk pedoman tanpa sanksi. Menyebut nomor Perpres AI yang belum ada adalah kesalahan yang mudah dideteksi juri.

### 11.2 Perban BPS 6/2025 dan Permendagri 53/2020

| Kewajiban | Implementasi |
|---|---|
| Pasal 28 ayat 8: log lengkap untuk audit | `jejak_audit` dengan aktor, aksi, entitas, waktu, dan alamat IP |
| Pasal 29 ayat 2: kriptografi, RBAC, logging, backup | Lihat 11.3 |
| Pasal 23 sampai 24: BAST dan perjanjian kerahasiaan | Templat tersedia; setiap ekspor data mencatat tujuan dan penerima |
| Permendagri 53/2020: tiga produk TKPKD | Modul yang menghasilkan draf RPKD, Rencana Aksi Tahunan, dan laporan, ditambah paket bahan rapat koordinasi |

Modul TKPKD inilah yang mengubah NADI dari "aplikasi data" menjadi "aplikasi yang dipakai rutin oleh Bappeda" — rapat koordinasi wajib minimal tiga kali setahun, dan setiap rapat membutuhkan bahan.

### 11.3 RBAC — lima peran

| Peran | Melihat identitas | Melihat lokasi presisi | Cakupan wilayah | Dapat menugaskan |
|---|:--:|:--:|---|:--:|
| Kader / pendamping pekon | Ya | Ya | **Hanya pekonnya** | Tidak |
| Operator Dinsos kabupaten | Ya | Ya | Kabupaten | Ya |
| Kepala OPD | Terbatas | Tidak | Kabupaten, urusannya saja | Ya |
| Bappeda / TKPKD | **Tidak** | Tidak | Kabupaten, agregat | Tidak |
| Auditor | Pseudonim | Tidak | Kabupaten | Tidak |

Pembatasan lokasi presisi hanya untuk petugas wilayah bersangkutan adalah penerapan langsung prinsip minimisasi data — yang merupakan alasan kedua pelarangan SyRI oleh Pengadilan Distrik Den Haag.

### 11.4 Pelajaran dari tiga kegagalan

| Sistem | Sebab kegagalan | Mitigasi NADI |
|---|---|---|
| **SyRI** (Belanda, dilarang 5 Februari 2020) | Terlalu buram; mengumpulkan terlalu banyak data; tujuan tidak cukup spesifik; menyasar lingkungan berpenghasilan rendah dan minoritas | Explainability wajib per keluarga; minimisasi data; tujuan tunggal yang tertulis; larangan variabel proksi etnis dan agama; **NADI tidak dipakai untuk deteksi kecurangan** |
| **Robodebt** (Australia, AUD 1,76 miliar dari 526.000 orang) | Asumsi statistik sederhana berupa income averaging dipakai untuk keputusan individual **tanpa verifikasi manusia** | Skor tidak pernah menjadi dasar tunggal keputusan merugikan; tidak ada penghapusan otomatis; banner "Rekomendasi, bukan keputusan" di setiap layar |
| **Social Card** (Serbia, digugat konstitusional) | Otomasi **memperbesar** bias yang sudah ada dalam aturan kelayakan; Roma dan penyandang disabilitas paling dirugikan | Panel Audit Keadilan **di dalam aplikasi** yang menampilkan exclusion error per kelompok rentan: disabilitas, lansia, perempuan kepala keluarga, ukuran keluarga kecil, dan wilayah tertinggal |

### 11.5 Sepuluh guardrail yang masuk ke antarmuka

| # | Guardrail |
|---|---|
| 1 | Model tidak pernah memutuskan; keluarannya antrean prioritas verifikasi |
| 2 | Tidak ada penghapusan otomatis dari daftar penerima |
| 3 | Setiap skor punya penjelasan bahasa manusia yang dapat dibacakan di Musyawarah Pekon |
| 4 | Disclaimer non-kausal wajib pada setiap tampilan SHAP |
| 5 | Angka ditampilkan sebagai **pita** ("Risiko tinggi, 60 sampai 80 persen"), bukan desimal ("72,4 persen") — presisi palsu memicu kepercayaan berlebih |
| 6 | Bobot fitur eksak tidak dipublikasikan; **daftar dimensi dipublikasikan** — menyeimbangkan transparansi prosedural dengan risiko gaming |
| 7 | Audit dua sisi: mencari exclusion error seintensif inclusion error |
| 8 | Dashboard keadilan terlihat pengguna, bukan hanya pengembang |
| 9 | Umur data ditampilkan di setiap kartu keluarga |
| 10 | Label "DATA SINTETIS — BUKAN DATA RIIL" permanen dan mencolok |

Satu tambahan yang absen di **seluruh** sistem yang diteliti dan murah untuk diadakan: **versi model dan tanggal data tercantum di footer setiap halaman.**

### 11.6 Kaidah komunikasi desil

BPS secara eksplisit menyatakan desil DTSEN adalah **pemeringkatan relatif** tingkat kesejahteraan keluarga, bukan ukuran absolut kemiskinan, pendapatan, atau kekayaan. Miskonsepsi ini sudah menjadi polemik publik sampai Ombudsman turun tangan meluruskan.

| Dilarang ditulis | Yang dipakai |
|---|---|
| "Desil 3 sama dengan miskin" | "Desil 3 berarti berada pada 30 persen terbawah secara relatif di antara keluarga terdata secara nasional" |
| "Desil Anda akan berubah setelah pengajuan" | "Perubahan desil menunggu snapshot dan pemeringkatan ulang triwulan berikutnya oleh BPS" |
| "Pemerintah desa menetapkan desil" | "Pemerintah desa dan dinas sosial melakukan verifikasi dan validasi; pemeringkatan adalah kewenangan BPS" |

---

## 12. Risiko Teknis Terbesar dan Mitigasi

Diurutkan berdasarkan hasil kali probabilitas dan dampak.

| # | Risiko | Gejala | Mitigasi | Pemilik |
|---|---|---|---|---|
| **T1** | **Generator terlalu mudah ditebak** — AUC melonjak ke 0,95 dan seluruh evaluasi menjadi tak bermakna | AUC di atas 0,90; R kuadrat fitur terhadap ln pengeluaran di atas 0,7 | Label dibangkitkan dari **laten**, bukan dari fitur teramati; gerbang mutu otomatis membatalkan generasi; lima laten disembunyikan permanen | Tim data |
| **T2** | **Kebocoran fitur** — `desil_kesejahteraan` atau status bansos masuk Skor B | AUC tinggi hanya pada Skor B; SHAP didominasi satu fitur | Daftar terlarang ditegakkan **di kode**, bukan di dokumen: fungsi pembangun fitur Skor B menolak nama terlarang dan menggagalkan pipeline | Tim ML |
| **T3** | **Kebocoran temporal** — fitur menengok ke gelombang `t+1` | Metrik uji temporal jauh lebih baik daripada yang wajar | Fungsi fitur secara struktural hanya menerima satu baris pada `t`; uji unit memastikan tidak ada akses `t+1` | Tim ML |
| **T4** | **Basis penduduk tercampur** — DTSEN 451.586 versus Dukcapil 444.834 versus proyeksi BPS 416.579 | Angka kemiskinan hasil generator meleset satu setengah poin persen | Ketiganya menjadi konstanta bernama terpisah dengan komentar tegas; hanya proyeksi BPS dipakai untuk angka kemiskinan | Tim data |
| **T5** | **Nominal program salah tampil** — konflik sumber pada PKH lansia dan disabilitas | Angka di antarmuka berbeda dengan juknis resmi | Kolom `keyakinan` wajib; item `tidak_ditemukan` tidak ditampilkan sama sekali; setiap angka dapat diklik untuk melihat sumbernya | Tim produk |
| **T6** | **Kode kategori DTSEN resmi berbeda dengan proksi Susenas** | Pemadanan gagal saat integrasi nyata | Seluruh kode di `ref_kode_nilai` dengan kolom `sumber`; pergantian cukup mengubah isi tabel tanpa migrasi skema | Tim data |
| **T7** | **Model gagal di satu kecamatan** — Pagelaran Utara adalah outlier di hampir semua dimensi | Recall jatuh drastis pada satu kecamatan | Leave-one-kecamatan-out CV wajib; reliability diagram per kecamatan; ambang tidak dipaksakan seragam bila kalibrasi berbeda nyata | Tim ML |
| **T8** | **Guncangan dibangkitkan independen** sehingga fitur spasial kehilangan daya prediksi | Spatial lag dan `persen_miskin_wilayah` tidak muncul pada kepentingan fitur | Guncangan bencana kovarian penuh per pekon; gagal panen kovarian per kecamatan; harga pangan kovarian kabupaten | Tim data |
| **T9** | **Ketergantungan pada LLM eksternal** saat demo | Copilot mati, presentasi terganggu | Penyedia berlapis dengan cadangan templat deterministik **tanpa jaringan**; seluruh fitur inti berfungsi tanpa LLM | Tim backend |
| **T10** | **Data pribadi bocor ke LLM** | Payload memuat pola identitas | Lima lapis penyaring; regex keluar sebagai jaring terakhir; pelanggaran **membatalkan** permintaan dan dicatat sebagai insiden | Tim keamanan |
| **T11** | **Antrean anomali didominasi inclusion error** sehingga NADI menjadi alat berburu kebocoran | Rasio kasus IE terhadap EE melebihi 2 banding 1 | Rasio dipantau di dashboard; ambang residual disetel agar kandidat EE mendapat porsi setara | Tim produk |
| **T12** | **Presisi flag rendah** sehingga petugas kehilangan kepercayaan | `setuju_dengan_sistem` di bawah 30 persen untuk satu jenis flag | Presisi per jenis flag dipantau; aturan berpresisi rendah diperketat atau dinonaktifkan | Tim produk |
| **T13** | **Geometri 1,75 MB memberatkan peramban** | Peta lambat pada perangkat lapangan | Penyederhanaan mapshaper 5 sampai 10 persen; disimpan lokal; tidak memanggil endpoint BIG saat runtime | Tim frontend |
| **T14** | **Klaim kebaruan dipatahkan juri** | Pertanyaan "bukankah SEPAKAT sudah melakukannya" | Tabel 10.1 dan 10.2 masuk ke slide sebagai bagian presentasi, bukan disembunyikan; kebaruan dirumuskan pada kombinasi | Tim presentasi |
| **T15** | **Ruang lingkup melebar** — delapan modul dalam waktu terbatas menuju 13 September 2026 | Modul setengah jadi di semua lini | Urutan prioritas mengikat: (1) generator dan basis data, (2) model dan explainability, (3) Digital Twin dan Radar, (4) Recommender dan Mismatch, (5) Simulator dan Outcome, (6) Copilot. Copilot terakhir karena paling mudah didemokan secara sederhana | Pimpinan tim |

### 12.1 Urutan pembangunan yang disarankan

```
Minggu 1-2   Skema basis data + seed wilayah 131 desa + katalog 28 program + 30 OPD
Minggu 3-4   Generator: laten, copula, raking, panel 8 gelombang        <-- GERBANG MUTU
Minggu 5     Fitur (51) + label + LightGBM + kalibrasi + evaluasi lengkap
Minggu 6     TreeSHAP per kelompok fitur + kalimat penjelasan Indonesia
Minggu 7     Household Digital Twin + GeoAI Poverty Radar
Minggu 8     Intervention Recommender + Mismatch Queue (3 lapis)
Minggu 9     What-if Simulator + Outcome Monitoring
Minggu 10    AI Policy Copilot + RAG BM25 + guardrail
Minggu 11    Executive Command Center + dashboard keadilan + audit
Minggu 12    Kerangka DPIA, dokumentasi metodologi, bahan presentasi
```

Gerbang mutu pada akhir minggu 4 bersifat mengikat: **bila AUC berada di luar 0,72 sampai 0,85, pembangunan modul berikutnya ditunda** sampai generator diperbaiki. Membangun antarmuka di atas data yang cacat berarti membangun demo yang tampak bekerja tetapi tidak mengukur apa pun.

---

## 13. Daftar Sumber

### 13.1 Regulasi

| Regulasi | Isi relevan |
|---|---|
| Peraturan BPS No. 6 Tahun 2025 tentang DTSEN | Definisi, pemadanan, pemeringkatan, keamanan, audit |
| Rancangan Peraturan BPS tentang DTSEN (JDIH BPS) | **Satu-satunya sumber daftar variabel lengkap**: 13 individu, 25 keluarga, 19 sub-variabel aset |
| Inpres No. 4 Tahun 2025 | DTSEN sebagai rujukan tunggal; DTKS dilebur |
| UU No. 27 Tahun 2022 (PDP) | Pasal 10 keberatan; Pasal 20 basis legal; Pasal 34 DPIA |
| Permensos No. 3 Tahun 2021 | Pengelolaan DTKS, verval, penjaminan kualitas |
| Permensos No. 5 Tahun 2021 | Program Sembako |
| Permensos No. 1 Tahun 2018 | Program Keluarga Harapan |
| Permensos No. 7 Tahun 2021 jo. 7 Tahun 2022 | ATENSI |
| Permendes No. 16 Tahun 2026 | Fokus Dana Desa 2026, BLT maksimal 15 persen |
| Permendagri No. 53 Tahun 2020 | TKPK kabupaten/kota, tiga produk kerja |
| Permen PKP No. 10 Tahun 2025 jo. 6 Tahun 2026 | BSPS Rp20 juta per unit |
| Permenkes No. 3 Tahun 2014 | Lima pilar STBM |
| Inpres No. 9 Tahun 2025 | Koperasi Desa/Kelurahan Merah Putih |
| Perpres No. 39 Tahun 2019, No. 95 Tahun 2018, No. 82 Tahun 2023 | Satu Data Indonesia dan SPBE |
| Kepmendagri No. 300.2.2-2138/2025 dan 300.2.2-2430/2025 | Kode wilayah administrasi |
| SE Menkominfo No. 9 Tahun 2023 | Etika AI — pedoman, **tanpa sanksi** |

### 13.2 Metodologi

| Rujukan | Kontribusi |
|---|---|
| Brown, Ravallion & van de Walle (NBER WP 22919, 2016) | R kuadrat PMT 0,53; exclusion error 81 persen pada cakupan 20 persen; bias OLS terhadap yang termiskin |
| Kidd & Wylde (ILO, 2017) | Design exclusion error PMT; kerusakan sosial PMT di Indonesia; mekanisme banding yang tidak dapat berfungsi |
| Aiken, Bellue, Karlan, Udry & Blumenstock (*Nature* 603, 2022) | AUC 0,70 targeting ML; ML menaikkan EE 9 sampai 35 persen dibanding registry komprehensif; dekomposisi enam sumber eksklusi |
| Aiken, Bedoya, Blumenstock & Coville (*JDE*, 2023) | Korelasi aset dengan konsumsi 0,37; kombinasi sumber mengungguli sumber tunggal |
| Chaudhuri, Jalan & Suryahadi (Columbia DP 0102-52, 2002) | Metode VEP dengan FGLS tiga tahap |
| Pritchett, Suryahadi & Sumarto (SMERU, 2000) | Ambang kerentanan 0,5; rasio rentan terhadap miskin |
| Ligon & Schechter (*Economic Journal*, 2003) | Dekomposisi kerentanan; guncangan agregat lebih penting |
| Alatas, Banerjee, Hanna, Olken & Tobias (*AER*, 2012) | Model dan komunitas mengukur konstruk berbeda; elite capture bukan penjelasannya |
| Dietrich, Malerba & Gassmann (*Data & Policy* 6:e3, 2024) | Akurasi lebih tinggi dapat menurunkan kesejahteraan; rumah tangga kecil dirugikan sistematis |
| Gonzales Martinez & Cooray (arXiv:2503.04300, 2025) | Spatial ML Indonesia; Moran's I 0,411; EE 28,20 ke 20,14 persen |
| Kumar, Venkatasubramanian, Scheidegger & Friedler (ICML, 2020) | Batas SHAP sebagai penjelasan; kebutuhan penalaran kausal |
| Chen, Janizek, Lundberg & Lee (arXiv:2006.16234, 2020) | Interventional versus observational SHAP |
| Kshirsagar, Wieczorek, Ramanathan & Wells (NIPS, 2017) | PPI sepuluh pertanyaan; AUC 0,81 sebagai benchmark |
| Aiken, Ohlenburg & Blumenstock (COMPASS, 2023) | Degradasi akurasi model prediksi kemiskinan lintas waktu |
| Taufiq & Mariyah (Prosiding STIS, 2021) | Variabel PMT PBDT 2015; forward-stepwise per kabupaten |

### 13.3 Data Pringsewu dan geospasial

| Sumber | Isi |
|---|---|
| BPS, *Kabupaten Pringsewu Dalam Angka 2025* | Struktur wilayah, ketenagakerjaan, PDRB, IDM, kemiskinan |
| BPS, *Potret Kemiskinan Kabupaten Pringsewu 2025* | Deret P0, P1, P2, garis kemiskinan, indikator RT miskin |
| Tabel dinamis BPS Pringsewu | Gini Ratio, air minum layak dan aman |
| Badan Informasi Geospasial, layanan ArcGIS REST BATASWILAYAH | Poligon 131 desa dan 9 kecamatan, kode KDEPUM |
| `cahyadsn/wilayah` (Kepmendagri 2025) | 141 baris kode wilayah 18.10 |
| Portal resmi Kabupaten Pringsewu | 30 OPD dan subdomainnya |
| Dinas Sosial Pringsewu | 12 standar layanan |
| HREIS/PUPR, Metadata Indikator Perumahan | Kaidah air minum layak, sanitasi layak, rumah layak huni |
| Katalog IHSN, Susenas Maret 2011 (katalog 3037) | Kode kategori 16 variabel kunci — **proksi**, wajib diverifikasi |

### 13.4 Lanskap sistem

SEPAKAT Bappenas; SIKS-NG Kemensos; portal DTSEN BPS; SIGA Kemendukbangga; e-PKH; SIMNANGKIS DIY; SIPINTER Purbalingga; Carik Jakarta; Smart Kampung Banyuwangi; SISBEN Kolombia; CadUnico Brasil; Listahanan Filipina; NSER/BISP Pakistan; Enhanced Single Registry Kenya; Novissi Togo; SyRI Belanda (putusan 5 Februari 2020); Robodebt Australia (Royal Commission 7 Juli 2023); Social Card Serbia (Amnesty International, Desember 2023).

---

## Lampiran A — Data yang tidak ditemukan dan diasumsikan

Bagian ini ada agar tidak ada angka yang dikarang diam-diam. Setiap item di bawah **wajib** ditandai di antarmuka sebagai asumsi atau tidak ditampilkan sama sekali.

| # | Data yang tidak ditemukan | Perlakuan di NADI |
|---|---|---|
| 1 | Kode kategori numerik resmi DTSEN | Memakai proksi Susenas; kolom `sumber` pada `ref_kode_nilai` menandainya |
| 2 | Bobot PMT eksak DTSEN | Tidak direplikasi; NADI memakai desil sebagai masukan apa adanya |
| 3 | Jumlah KPM PKH, Sembako, PBI-JKN spesifik Pringsewu | Dibangkitkan sintetis dengan cakupan yang dikalibrasi ke pagu nasional |
| 4 | Gini Ratio Pringsewu 2016 sampai 2023 | Hanya 2024 dan 2025 ditampilkan |
| 5 | HLS, RLS, pengeluaran disesuaikan (komponen IPM) | Tidak ditampilkan |
| 6 | Jumlah rumah tangga/KK versi BPS | Memakai angka DTSEN dengan label sumber |
| 7 | Persentase sanitasi layak seluruh rumah tangga | Hanya angka RT miskin ditampilkan, dengan label |
| 8 | Jumlah RTLH resmi Pringsewu | Memakai backlog 1.700 unit dari Dinsos, ditandai `perkiraan` |
| 9 | Nominal PMT, SANIMAS, PAMSIMAS per unit | **Tidak ditampilkan** — berstatus `tidak_ditemukan` |
| 10 | Nominal PKH lansia dan disabilitas berat | Rp2,4 juta per tahun dengan badge `cukup_kuat` dan catatan konflik sumber |
| 11 | Rincian nominal per paket ATENSI | Hanya total Pringsewu 2026 ditampilkan |
| 12 | Kelanjutan resmi BLT Kesra 2026 | Program berstatus `tidak_pasti`; jadwal dan nominal tidak ditampilkan |
| 13 | Variabel guncangan di DTSEN | **Diasumsikan tidak ada**; NADI mengumpulkannya sendiri lewat kanal kader |
| 14 | Kapasitas verifikasi lapangan nyata per triwulan | Diasumsikan 300 kasus per triwulan; menjadi parameter yang dapat diubah pengguna |
| 15 | Stunting, ODF, dan SPPG MBG per pekon | Tidak ditampilkan per pekon; hanya agregat kabupaten dengan label `unverified` |
| 16 | Prevalensi kemiskinan per pekon | **Tidak ada data resmi.** Hasil estimasi NADI ditandai sebagai estimasi, bukan angka BPS |
| 17 | Bobot penggabungan Regsosek, DTKS, dan P3KE | Tidak direplikasi |
| 18 | API resmi DTSEN untuk pemda | Diasumsikan belum tersedia; integrasi dirancang sebagai impor berkas |

---

*Dokumen ini adalah fondasi. Setiap perubahan pada keputusan D1 sampai D6 (Bagian 2.1), daftar terlarang fitur (Bagian 3.3), definisi label (Bagian 4.2), gerbang mutu generator (Bagian 5.8), atau batas tegas (Bagian 1.4) memerlukan catatan keputusan arsitektur tersendiri di `docs/adr/`.*
