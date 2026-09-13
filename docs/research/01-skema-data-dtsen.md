# 01 — Skema Data DTSEN (Data Tunggal Sosial dan Ekonomi Nasional)

> **Tujuan dokumen:** menjadi acuan langsung untuk desain skema database aplikasi NADI.
> **Tanggal riset:** 25 Agustus 2026
> **Status:** riset primer (peraturan resmi + katalog mikrodata resmi) + sumber sekunder yang ditandai eksplisit.

---

## 0. RINGKASAN EKSEKUTIF

| Hal | Temuan |
|---|---|
| Payung hukum tertinggi | **Inpres No. 4 Tahun 2025** tentang DTSEN (ditandatangani 5 Feb 2025) |
| Peraturan teknis | **Peraturan BPS No. 6 Tahun 2025** (ditetapkan 12 Des 2025 oleh Kepala BPS Amalia Adininggar Widyasanti) |
| Wali data | **BPS** — penyusun & pengelola tunggal, penyimpanan terpusat di pusat data BPS |
| Sumber data utama | Regsosek (Bappenas) + DTKS (Kemensos) + P3KE (Kemenko PMK) + Dukcapil (Kemendagri) |
| Sumber data pendukung (versi 1) | **Data pelanggan PLN** + **Data kepesertaan BPJS Kesehatan (khusus PBI)** |
| Unit analisis | **Individu** dan **Keluarga** (bukan "rumah tangga") — kunci: NIK + Nomor KK |
| Metode pemeringkatan | **Proxy Means Test (PMT)** → prediksi pengeluaran per kapita → peringkat → **desil 1–10 (nasional)** |
| Skala (per 10 Juli 2026, DTSEN v3) | **290,13 juta record individu** & **95,98 juta record keluarga** |
| Siklus pemutakhiran | **Triwulanan** (setiap 3 bulan) |
| Jumlah variabel pemeringkatan | **13 variabel individu** + **25 variabel keluarga** + **~19 sub-variabel kepemilikan aset** |
| Sasaran bansos utama | **Desil 1–4** |

**Implikasi paling penting untuk skema DB NADI:** DTSEN adalah model **dua entitas utama** — `individu` (PK: NIK) dan `keluarga` (PK: nomor KK) — dengan relasi many-to-one dan atribut `status_hubungan_keluarga`. Semua variabel kondisi rumah & aset menempel di **keluarga**, bukan individu. **Desil menempel di keluarga.**

---

## 1. PERATURAN BPS NOMOR 6 TAHUN 2025

**Judul lengkap:** Peraturan Badan Pusat Statistik Nomor 6 Tahun 2025 tentang Penyusunan dan Pengelolaan Data Tunggal Sosial dan Ekonomi Nasional
**Ditetapkan:** Jakarta, 12 Desember 2025 · **Kepala BPS: Amalia Adininggar Widyasanti**
**PDF resmi (berhasil diekstrak penuh):** https://peraturan.go.id/files/peraturan-bps-no-6-tahun-2025.pdf
**Halaman detail:** https://peraturan.go.id/id/peraturan-bps-no-6-tahun-2025

### 1.1 Definisi kunci (Pasal 1)

| No | Istilah | Definisi (parafrase dekat teks asli) |
|---|---|---|
| 2 | **DTSEN** | Basis data tunggal **individu dan/atau keluarga** yang mencakup kondisi sosial, ekonomi, dan **peringkat kesejahteraan keluarga**, dibentuk dari penggabungan data registrasi sosial dan ekonomi, data terpadu kesejahteraan sosial, dan data pensasaran percepatan penghapusan kemiskinan ekstrem, serta telah **dipadankan dengan data kependudukan** dan **dimutakhirkan secara berkala**, dikelola oleh lembaga pemerintah bidang statistik. |
| 3 | Data Kependudukan | Data perseorangan dan/atau agregat terstruktur hasil pendaftaran penduduk & pencatatan sipil. |
| 4 | **Pembaruan DTSEN** | Kegiatan sistematis, berkala, berkelanjutan untuk **memperbaiki, menambah, menghapus, dan/atau menyesuaikan data dan variabel** dalam DTSEN berdasarkan perubahan kondisi sosial, ekonomi, dan demografi individu/keluarga; bersumber dari data administrasi, hasil sensus & survei, hasil pemutakhiran, maupun sumber lain dari Instansi Pusat/Daerah. |
| 5 | Data Individu | Data unit observasi yang memuat karakteristik individu, direpresentasikan terperinci pada tingkat terkecil. |
| 6 | Penyedia Sumber Data | Pihak yang menyediakan dan/atau menyampaikan sumber data untuk pengelolaan DTSEN. |
| 7 | Pemrosesan DTSEN | Rangkaian proses sistematis untuk menghasilkan data/informasi DTSEN yang siap digunakan. |
| 8 | **Pemadanan** | Proses pencocokan/penyamaan entitas data dari berbagai sumber agar dapat dikenali sebagai objek yang sama di DTSEN. |
| 9 | **Pemeringkatan Kesejahteraan** | Proses **pengelompokan Data Individu dalam DTSEN berdasarkan tingkat kesejahteraan**. |
| 10 | NIK | Nomor identitas penduduk yang unik/khas, tunggal, dan melekat pada seseorang yang terdaftar sebagai penduduk Indonesia. |
| 11 | Instansi Pusat | K/L, kesekretariatan lembaga negara/nonstruktural, lembaga pemerintah, badan/lembaga. |
| 12 | Instansi Daerah | Perangkat daerah provinsi & kab/kota (setda, setwan DPRD, dinas daerah, lembaga teknis daerah). |
| 13 | **Snapshot DTSEN** | Salinan statis DTSEN — rekaman konsisten & utuh pada titik waktu tertentu. |

### 1.2 Tujuan (Pasal 2) & Ruang Lingkup (Pasal 3)

**Tujuan:** (a) dasar pelaksanaan integrasi data, pemutakhiran, pemeringkatan, dan penyampaian DTSEN oleh BPS; (b) panduan bagi Instansi Pusat & Daerah dalam menyampaikan data untuk memutakhirkan DTSEN; (c) mendorong transparansi & akuntabilitas; (d) mendorong integrasi data lewat penerapan **standar data, metadata, dan interoperabilitas**; (e) menyediakan DTSEN yang akurat, mutakhir, dapat dipertanggungjawabkan.

**Ruang lingkup:** a. penyusunan DTSEN · b. pengelolaan DTSEN · c. penjaminan kualitas · d. penyimpanan DTSEN · e. keamanan data · f. pemantauan dan evaluasi · g. pelaporan · h. pendanaan.

### 1.3 Struktur BAB & Pasal

| BAB | Judul | Pasal |
|---|---|---|
| I | Ketentuan Umum | 1–3 |
| II | Penyusunan DTSEN | 4–7 |
| III | Pengelolaan DTSEN (Umum · Perencanaan Kebutuhan · Penerimaan Data · Pemrosesan · Penyampaian) | 8–24 |
| IV | Penjaminan Kualitas DTSEN | 25 |
| V | Penyimpanan DTSEN | 26–27 |
| VI | Keamanan DTSEN | 28–29 |
| VII | Pemantauan dan Evaluasi DTSEN | 30 |
| VIII | Pelaporan (kepada Presiden, berkala) | 31 |
| IX | Pendanaan (APBN + sumber sah lain) | 32 |
| X | Ketentuan Lain-lain (data pribadi → tunduk UU PDP) | 33 |
| XI | Ketentuan Penutup | 34 |

### 1.4 Sumber data (Pasal 4–6)

**Sumber data utama** (Pasal 5 ayat 2):

| Huruf | Sumber | Pengelola |
|---|---|---|
| a | Data registrasi sosial ekonomi (**Regsosek**) | Kementerian bidang perencanaan pembangunan nasional (**Bappenas**) |
| b | Data terpadu kesejahteraan sosial (**DTKS**) | Kementerian bidang sosial (**Kemensos**) |
| c | Data pensasaran percepatan penghapusan kemiskinan ekstrem (**P3KE**) | Kemenko bidang pembangunan manusia & kebudayaan (**Kemenko PMK**) |
| d | **Data Kependudukan** (Dukcapil) | Kemendagri — untuk verifikasi & sinkronisasi agar setiap individu punya identitas yang jelas, sah, dan unik |

**Sumber data pendukung** (Pasal 6): data administrasi dari Instansi Pusat selain Data Kependudukan, berfungsi memperluas cakupan & meningkatkan validitas informasi.

Pada **DTSEN versi pertama**, dua data pendukung yang dipakai (menurut rancangan Perban):
1. **Data PLN** — pelanggan menurut jenis layanan (prabayar/pascabayar), **ID pelanggan**, dikelompokkan berdasarkan **status subsidi** dan **daya terpasang**.
2. **Data BPJS Kesehatan** — NIK, nama, status kepesertaan, jenis layanan, riwayat pemanfaatan faskes, kategori kepesertaan berdasarkan tingkat kesejahteraan. **Pada integrasi awal, hanya data penerima manfaat PBI (Penerima Bantuan Iuran) yang dipakai.**

### 1.5 Alur Pemrosesan DTSEN (Pasal 12–17)

```
a. PEMADANAN DATA (Pasal 13)
   ├── Pemadanan individu
   ├── Pemadanan keluarga
   └── Pemadanan relasi individu–keluarga
        → hasil: data PADAN / data TIDAK PADAN
        → data tidak padan BERPOTENSI SEBAGAI INDIVIDU BARU (Pasal 13 ayat 4)

b. PEMBARUAN DATA (Pasal 14)
   ├── memperbarui informasi variabel untuk individu/keluarga yang sudah ada di DTSEN
   ├── melengkapi individu/keluarga yang belum punya informasi variabel DTSEN
   └── penambahan variabel untuk pengayaan DTSEN
   (mempertimbangkan periode dan validitas sumber data)

c. VALIDASI NIK DAN NOMOR KARTU KELUARGA (Pasal 15)
   → terhadap Data Kependudukan yang dikelola Kemendagri
   → jika TIDAK VALID: TIDAK diikutsertakan dalam DTSEN dan DIKEMBALIKAN
     kepada Penyedia Sumber Data (Pasal 15 ayat 3)

d. SNAPSHOT DTSEN (Pasal 16)
   → salinan statis berkala; menjamin keutuhan DTSEN

e. PEMERINGKATAN KESEJAHTERAAN (Pasal 17)
   → menentukan peringkat kesejahteraan KELUARGA berdasarkan VARIABEL SOSIAL EKONOMI
   → diterapkan pada hasil SNAPSHOT yang SUDAH divalidasi NIK & nomor KK
```

**Kriteria Data Individu yang diterima BPS (Pasal 10 ayat 4)** — penting untuk desain kontrak/payload API NADI:

| Huruf | Kriteria |
|---|---|
| a | Memuat **variabel NIK dan nama** sebagai dasar Pemadanan |
| b | Memiliki **minimal satu variabel berstandar data yang sama** dengan variabel DTSEN |
| c | **Metadata** |
| d | Memiliki variabel yang dapat **memperkaya informasi** dalam DTSEN |

Tahapan penerimaan data (Pasal 11): (a) penyampaian Data Individu → (b) verifikasi & validasi oleh BPS. Bila ditemukan ketidaksesuaian, **Penyedia Sumber Data melakukan perbaikan dan menyampaikan kembali**.

### 1.6 Pembagian kewenangan pusat–daerah

| Aktor | Kewenangan menurut Perban 6/2025 |
|---|---|
| **BPS (Badan)** | Menyusun, mengintegrasikan, memproses, memadankan, **melakukan Pemeringkatan Kesejahteraan**, membuat Snapshot, menyimpan **terpusat** di pusat data BPS (Pasal 26), menjamin kualitas, memantau & mengevaluasi, melaporkan kepada Presiden (Pasal 31). |
| **Instansi Pusat** | Penyedia Sumber Data (Pasal 10 ayat 2 huruf a); wajib memastikan keamanan sumber daya sistem DTSEN (Pasal 29). |
| **Instansi Daerah** (perangkat daerah prov & kab/kota) | Penyedia Sumber Data (Pasal 10 ayat 2 huruf b); wajib memastikan keamanan (Pasal 29). **TIDAK punya kewenangan menetapkan desil.** |
| Penerima hasil pemrosesan (Pasal 20) | (a) Kemenko bidang pemberdayaan masyarakat; (b) Kementerian PPN/Bappenas; (c) Kemensos — **secara berkala**. |
| Pengawas (Pasal 21) | Badan bidang pengawasan keuangan negara/daerah & pembangunan nasional (**BPKP**). |
| Penyedia Sumber Data (Pasal 22) | Dapat menerima kembali DTSEN hasil pembaruan untuk mendukung program & kebijakan pemerintah. |

> **Penegasan (Ombudsman RI):** peran pemerintah desa dan dinas sosial **terbatas pada penyampaian data, verifikasi, dan validasi** — mereka **tidak** menentukan peringkat kesejahteraan/desil. *(sumber sekunder)*

### 1.7 Penyampaian DTSEN & kewajiban dokumen (Pasal 23–24)

Setiap penyampaian DTSEN **wajib** dilengkapi **Berita Acara Serah Terima (BAST)** + **Perjanjian**.

**BAST minimal memuat:** (a) nama, jenis, dan volume data; (b) metadata; (c) tanggal dan metode penyampaian data; (d) identitas penerima DTSEN; (e) pernyataan kepatuhan terhadap ketentuan pemanfaatan data.

**Perjanjian minimal memuat:** (a) tanggal penandatanganan; (b) identitas penyedia dan penerima DTSEN; (c) peran dan tanggung jawab para pihak.

Perbedaan penting antar-jenis BAST:
- **BAST Pemanfaatan** (ke Kemenko PM/Bappenas/Kemensos): penerima **diperkenankan** membagipakaikan/mempublikasikan data ke pihak lain untuk mendukung program pemerintah, **dan wajib melakukan sinkronisasi periodik balik ke BPS**.
- **BAST Pengawasan** (ke BPKP) & **BAST Pemadanan** (ke K/L tertentu): penerima adalah **pengguna akhir**, **TIDAK diperkenankan** memberikan/membagipakaikan/mempublikasikan data ke pihak lain.

### 1.8 Keamanan (Pasal 28–29)

Keamanan DTSEN mencakup penjaminan: **kerahasiaan, keutuhan, kenirsangkalan, ketersediaan, otentikasi, otorisasi, pencatatan** terhadap data & informasi, infrastruktur, dan aplikasi DTSEN.

Kendali keamanan minimal (Pasal 29 ayat 2):

| Huruf | Kendali |
|---|---|
| a | Pemanfaatan teknologi **kriptografi** |
| b | **Sertifikat elektronik** |
| c | **Pembatasan akses berbasis peran (RBAC)** |
| d | **Pencatatan dan monitoring aktivitas** (manajemen log untuk monitoring, penelusuran insiden, audit) |
| e | Penerapan sistem **pencadangan, replikasi, redundansi** |
| f | Kendali keamanan lain sesuai mitigasi risiko |

### 1.9 Isi Lampiran Perban 6/2025 (final)

> ⚠️ **PENTING & JUJUR:** Lampiran **Perban 6/2025 versi final TIDAK memuat daftar variabel.** Isinya hanya:
> - **A.** Alur Pemrosesan DTSEN — *"Bagan 1 Pemrosesan DTSEN"* (berupa gambar; teksnya tidak dapat diekstrak dari PDF)
> - **B.** Format BAST untuk **Pemanfaatan** DTSEN
> - **C.** Format BAST untuk **Pengawasan** DTSEN
> - **D.** Format BAST untuk **Pemadanan** DTSEN
> - **E.** Format **Perjanjian Kerahasiaan Data**
>
> Daftar variabel DTSEN (Bagian 2 di bawah) berasal dari **RANCANGAN Peraturan BPS** yang dipublikasikan BPS sendiri di kanal pembentukan peraturan perundang-undangan JDIH BPS. Rancangan ini **jauh lebih rinci** daripada versi final dan memuat metodologi + daftar variabel lengkap.

---

## 2. ⭐ DAFTAR VARIABEL DTSEN — TABEL UTAMA UNTUK SKEMA DATABASE

**Sumber:** *Rancangan Peraturan Badan Pusat Statistik tentang Penyusunan dan Pengelolaan DTSEN*, **Lampiran BAB IV — Pemutakhiran Data, huruf C "Variabel Pemutakhiran Data"**, hal. 26–29.
**URL:** https://jdih.bps.go.id/public/pembentukan-puu/download/eyJpdiI6IkxpVldtUWRWeHJmR29HYkdxSW04ZFE9PSIsInZhbHVlIjoiL0FXWjBCeDNKNys1bTllTEd4am1nZz09IiwibWFjIjoiMjM3NmNjM2ViNzBhOTZhOWIxNzExMTA5NTg1ZDFiNDk3NDQ2YzM4MTA5MWVlZjk1NGNjMTVlMjJmNmM3NTRiYSIsInRhZyI6IiJ9

> Kutipan regulasi: *"Kegiatan pemutakhiran lapangan **minimal** harus mencakup variabel-variabel yang digunakan dalam Pemeringkatan Kesejahteraan keluarga, sebagaimana ditetapkan oleh Badan. Variabel yang digunakan dalam Pemeringkatan Kesejahteraan **dapat bertambah atau berkurang** disesuaikan dengan perkembangan jumlah sumber data pendukung dan validitas sumber data. Variabel pemeringkatan tersebut mencakup variabel individu dan variabel keluarga sebagai berikut."*

### 2.1 TABEL — VARIABEL INDIVIDU DTSEN (13 variabel)

Kolom "Nama Variabel (resmi)" adalah nama **persis** seperti tercantum di rancangan Perban — pakai ini untuk nama kolom DB agar interoperabel.

| # | Nama Variabel (resmi) | Keterangan (resmi, verbatim) | Tipe Data Usulan | Kode Nilai / Kategori | Sumber Kode |
|---|---|---|---|---|---|
| 1 | `nomor_induk_kependudukan` | "nomor induk kependudukan yang tercatat di Dukcapil" | `CHAR(16)` NOT NULL, **PK** | 16 digit numerik (struktur di §10.4) | UU Adminduk / Dukcapil |
| 2 | `nama` | "nama lengkap yang tercatat di Dukcapil" | `VARCHAR(255)` | — | Dukcapil |
| 3 | `nomor_kartu_keluarga` | "nomor kartu keluarga yang tercatat di Dukcapil" | `CHAR(16)` **FK → keluarga** | 16 digit numerik | Dukcapil |
| 4 | `tanggal_lahir` / `usia` | "tanggal lahir yang tercatat di Dukcapil" | `DATE` + kolom turunan `usia SMALLINT` | — | Dukcapil |
| 5 | `jenis_kelamin` | "jenis kelamin individu" | `SMALLINT` | `1`=Laki-laki · `2`=Perempuan | Standar BPS/Dukcapil |
| 6 | `alamat` | "**alamat domisili sesuai kondisi lapangan**" (≠ alamat di KK) | `TEXT` | — | Rancangan Perban |
| 7 | `status_hubungan_keluarga` | "status hubungan individu dengan kepala keluarga" | `SMALLINT` | Lihat **Tabel 6.1** | Susenas/BPS |
| 8 | `status_kawin` | "status perkawinan individu" | `SMALLINT` | `1`=Belum kawin · `2`=Kawin · `3`=Cerai hidup · `4`=Cerai mati | Susenas (IHSN cat.3037 `kwn`/V426) |
| 9 | `pendidikan` | "**partisipasi sekolah** dan **pendidikan terakhir** dari individu" | 2 kolom: `partisipasi_sekolah SMALLINT`, `ijazah_tertinggi SMALLINT` | Lihat **Tabel 6.2** & **Tabel 6.3** | Susenas (`b5r14`/V488, `b5r17`/V491) |
| 10 | `pekerjaan` | "**status** dan **lapangan usaha** pekerjaan utama individu" | 2 kolom: `status_pekerjaan SMALLINT`, `lapangan_usaha SMALLINT` | Lihat **Tabel 6.4** & **Tabel 6.5** | Susenas (`b5r30`/V519) / KBLI |
| 11 | `kepemilikan_usaha` | "jumlah usaha dan lapangan usaha yang dimiliki" | `SMALLINT jumlah_usaha` + tabel anak `usaha(lapangan_usaha)` | jumlah: integer ≥0 | Rancangan Perban |
| 12 | `penyandang_disabilitas` | "status penyandang disabilitas pada individu" | `BOOLEAN` + tabel anak WGSS | Lihat **Tabel 6.6** | Rancangan Perban + WGQ/BPS |
| 13 | `penyakit_kronis` | "keluhan kesehatan **kronis/menahun** pada individu" | `BOOLEAN` (+ `SMALLINT jenis` opsional) | `0`=Tidak · `1`=Ya | Rancangan Perban |

### 2.2 TABEL — VARIABEL KELUARGA DTSEN (25 variabel utama + grup aset)

| # | Nama Variabel (resmi) | Keterangan (resmi, verbatim) | Tipe Data Usulan | Kode Nilai / Kategori | Sumber Kode |
|---|---|---|---|---|---|
| 1 | `kode_provinsi` | "kode provinsi pada DTSEN" | `CHAR(2)` | 2 digit | BPS Wilkerstat |
| 2 | `provinsi` | "nama provinsi" | `VARCHAR(100)` | — | BPS |
| 3 | `kode_kabupaten_kota` | "kode kabupaten/kota pada DTSEN" | `CHAR(4)` | 4 digit (2 pertama = provinsi) | BPS Wilkerstat |
| 4 | `kabupaten_kota` | "nama kabupaten/kota" | `VARCHAR(100)` | — | BPS |
| 5 | `kode_kecamatan` | "kode kecamatan pada DTSEN" | `CHAR(6)` | 6 digit (4 pertama = kab/kota) | BPS Wilkerstat |
| 6 | `kecamatan` | "nama kecamatan" | `VARCHAR(100)` | — | BPS |
| 7 | `kode_kelurahan_desa` | "kode kelurahan/desa pada DTSEN" | `CHAR(10)` | 10 digit (6 pertama = kecamatan) | BPS Wilkerstat |
| 8 | `kelurahan_desa` | "nama kelurahan/desa" | `VARCHAR(100)` | — | BPS |
| 9 | `alamat` | "alamat domisili" | `TEXT` | — | Rancangan Perban |
| 10 | `lokasi` | "**garis lintang (latitude) dan garis bujur (longitude) geotagging**" | `DECIMAL(10,7) lat` + `DECIMAL(10,7) lon` (atau `GEOGRAPHY(POINT,4326)`) | WGS84 | Rancangan Perban |
| 11 | `nomor_kartu_keluarga` | "nomor kartu keluarga yang tercatat di Dukcapil" | `CHAR(16)` **PK** | 16 digit | Dukcapil |
| 12 | `nama_kepala_keluarga` | "nama anggota keluarga yang berstatus sebagai kepala keluarga" | `VARCHAR(255)` | — | Rancangan Perban |
| 13 | `keluarga_dalam_rumah` | "**Jumlah keluarga yang tinggal dalam satu rumah**" | `SMALLINT` | integer ≥1 | Rancangan Perban |
| 14 | `status_kepemilikan_rumah` | "status kepemilikan rumah yang dihuni" | `SMALLINT` | Lihat **Tabel 4.1** | Susenas `b6r3` |
| 15 | `jenis_lantai_terluas` | "jenis lantai terluas dari rumah yang dihuni" | `SMALLINT` | Lihat **Tabel 4.4** | Susenas `b6r7` |
| 16 | `jenis_dinding_terluas` | "jenis dinding terluas dari rumah yang dihuni" | `SMALLINT` | Lihat **Tabel 4.3** | Susenas `b6r6` |
| 17 | `jenis_atap_terluas` | "jenis atap terluas dari rumah yang dihuni" | `SMALLINT` | Lihat **Tabel 4.2** | Susenas `b6r5` |
| 18 | `sumber_air_minum_utama` | "sumber air minum utama dari rumah yang dihuni" | `SMALLINT` | Lihat **Tabel 4.5** | Susenas `b6r9a` |
| 19 | `sumber_penerangan_utama` | "sumber penerangan utama dari rumah yang dihuni" | `SMALLINT` | Lihat **Tabel 4.9** | Susenas `b6r14a` |
| 20 | `daya_terpasang` | "daya listrik terpasang dari rumah yang dihuni" | `SMALLINT` (kode) atau `INT` (VA) | Lihat **Tabel 4.10** | Susenas `b6r14b` / PLN |
| 21 | `id_meteran_PLN` | "**ID pelanggan / nomor meteran PLN** rumah yang dihuni" | `VARCHAR(20)` | 11–12 digit ID pelanggan PLN | Rancangan Perban (data pendukung PLN) |
| 22 | `bahan_bakar_utama_memasak` | "bahan bakar utama memasak dari rumah yang dihuni" | `SMALLINT` | Lihat **Tabel 4.11** | Susenas `b6r15` |
| 23 | `fasilitas_bab` | "fasilitas bab dari rumah yang dihuni" | `SMALLINT` | Lihat **Tabel 4.6** | Susenas `b6r13a` |
| 24 | `jenis_kloset` | "jenis kloset yang digunakan dari rumah yang dihuni" | `SMALLINT` | Lihat **Tabel 4.7** | Susenas `b6r13b` |
| 25 | `pembuangan_akhir_tinja` | "jenis pembuangan akhir tinja dari rumah yang dihuni" | `SMALLINT` | Lihat **Tabel 4.8** | Susenas `b6r13c` |
| 26 | **`Kepemilikan:`** (grup) | 19 sub-variabel aset — lihat **Bagian 5** | — | — | Rancangan Perban |

> ⚠️ **Catatan penting:** Rancangan Perban **tidak** mencantumkan `luas_lantai` maupun `luas lantai per kapita` di daftar variabel keluarga, meskipun "kecukupan luas tempat tinggal **minimal 7,2 m² per kapita**" adalah kriteria rumah layak huni resmi (SDGs/BPS/RPJMN). Untuk NADI, **sediakan kolom `luas_lantai_m2`** karena tersedia di Regsosek/Susenas dan sangat prediktif — tandai sebagai *variabel pengayaan*, bukan variabel wajib DTSEN.

---

## 3. REGISTRASI SOSIAL EKONOMI (REGSOSEK) 2022

| Aspek | Detail |
|---|---|
| Periode pendataan awal | **15 Oktober – 14 November 2022** |
| Tahap lanjutan | **Forum Konsultasi Publik (FKP) 2023** + **Ground Check** |
| Cakupan | **Seluruh penduduk Indonesia** (sensus, bukan sampel) |
| Instrumen | `REGSOSEK22-K` (kuesioner keluarga) · `REGSOSEK22-VK1` (Daftar Verifikasi Keluarga per SLS/non-SLS) |
| Jumlah variabel | ± **90 variabel** |
| Penyelenggara | **BPS**; data dikelola **Bappenas** (per Perban 6/2025 Pasal 5 ayat 3) |
| Output final | **Peringkat kesejahteraan penduduk di setiap kabupaten** |

### 3.1 Struktur blok kuesioner REGSOSEK22-K

| Blok | Judul | Isi |
|---|---|---|
| **I** | **Keterangan Tempat** | Provinsi, kab/kota, kecamatan, desa/kelurahan, SLS/non-SLS, nomor urut bangunan/keluarga, alamat, geotagging. Judul pada VK1: *"BLOK I. IDENTITAS SATUAN LINGKUNGAN SETEMPAT/NON SLS"* |
| **II** | **Keterangan Petugas** | Nama & kode PPL/PML, tanggal pencacahan, tanda tangan |
| **III** | **Keterangan Perumahan** | Status kepemilikan bangunan tempat tinggal, **jenis bukti kepemilikan**, luas bangunan/lantai, jenis lantai, jenis dinding, jenis atap, sumber air minum, fasilitas BAB, jenis kloset, tempat pembuangan akhir tinja, sumber penerangan, daya listrik, bahan bakar memasak |
| **IV** | **Keterangan Sosial Ekonomi Anggota Keluarga** | **IV.A** Keterangan Demografi (nama, NIK, hubungan dgn kepala keluarga, jenis kelamin, umur/tgl lahir, status perkawinan, kepemilikan akta/dokumen kependudukan) · **IV.B** Pendidikan (ART usia 5+) · **IV.C** Ketenagakerjaan (ART usia 5+) · **IV.D** Kepemilikan Usaha (ART usia 5+) · **IV.E** Kesehatan (disabilitas, penyakit kronis/menahun, kondisi ibu hamil, status gizi balita) |
| **V** | **Keikutsertaan Program, Kepemilikan Aset, dan Layanan** | Kepesertaan program perlindungan sosial (PKH, BPNT/Sembako, PBI-JKN, PIP, BLT, KUR, dll.), daftar kepemilikan aset, akses layanan. **6 pertanyaan** pada blok ini menurut deskripsi BPS. |

### 3.2 Cakupan informasi Regsosek (kutipan rancangan Perban BPS)

> *"Data ini memuat hasil pendataan yang paling lengkap, karena cakupannya seluruh penduduk Indonesia. Regsosek juga memiliki variabel yang komprehensif yang meliputi data **perumahan, demografi, pendidikan, ketenagakerjaan, kepemilikan usaha, kesehatan, kepesertaan program perlindungan sosial, kepemilikan aset, serta informasi geospasial**. Kualitas data Regsosek diperkuat dengan partisipasi masyarakat melalui **forum konsultasi publik (FKP)**. Hasil final data Regsosek berupa **peringkat kesejahteraan penduduk di setiap kabupaten**."*

### 3.3 ⚠️ GAP YANG DILAPORKAN JUJUR

**Kuesioner Regsosek 2022 lengkap dengan nomor rincian + kode jawaban verbatim TIDAK BERHASIL DIAMBIL.**

Dokumen aslinya ada di `https://sepakat.bappenas.go.id/layanan/files/dokumen/2024-01-29-807467318.pdf` (judul internal PDF: *"REGISTRASI SOSIAL EKONOMI 2022 — RAHASIA — REPUBLIK INDONESIA"*), tetapi:

| Metode | Hasil |
|---|---|
| WebFetch (https) | **HTTP 403** (Cloudflare) |
| WebFetch via r.jina.ai proxy | **403 Access Denied** |
| curl `--tlsv1.2 / --tls-max 1.2 / --tlsv1.3 / SECLEVEL=0` | **exit 35** — `schannel: SEC_E_ILLEGAL_MESSAGE` (TLS fingerprint ditolak Cloudflare) |
| curl HTTP (port 80) | 301 redirect ke HTTPS |
| Mirror: Scribd, Studocu, PDFCoffee, slideshare | paywall / Cloudflare challenge / sertifikat kedaluwarsa |

**Konsekuensi:** kode kategori pada Bagian 4 & 6 di bawah **bukan** dari kuesioner Regsosek, melainkan dari **standar BPS Susenas** (katalog mikrodata IHSN resmi) yang menjadi induk konsep-definisi Regsosek. Kode ini **sangat mungkin** identik atau sangat mirip, tetapi **harus diverifikasi** sebelum dipakai sebagai kontrak data produksi.

---

## 4. VARIABEL KONDISI RUMAH — KODE KATEGORI

**Sumber kode numerik:** Katalog mikrodata IHSN — *Indonesia National Socio-Economic Survey (SUSENAS) Maret 2011*, datafile `susenas11mar_kr` (Core Household, 71.932 kasus, 90 variabel).
https://catalog.ihsn.org/catalog/3037/data-dictionary/F11?file_name=susenas11mar_kr

**Sumber konsep-definisi & kaidah kelayakan:** *Metadata Indikator Perumahan — Sistem Informasi Perumahan dan Realestat (HREIS), Kementerian PUPR*.
https://hreis.pu.go.id/_lib/file/doc/Metadata/Metadata%20Indikator%20Perumahan(2).pdf

> ⚠️ **Peringatan versi:** Susenas **2019+** memperluas beberapa kategori (mis. atap menambah "Bambu"; dinding dipecah menjadi 7 kategori; lantai memisah "Marmer/granit" dari "Keramik" dan menambah "Parket/vinil/karpet"). Kolom "Kategori Susenas 2019+" berisi **nama kategori terbaru** dari metadata HREIS/BPS, tetapi **nomor kodenya tidak berhasil diperoleh** (kuesioner VSEN24.K hanya tersedia berbayar via SiLASTIK BPS).

### Tabel 4.1 — `status_kepemilikan_rumah` (Susenas `b6r3`, V561)

| Kode | Kategori (ID) |
|---|---|
| 1 | Milik sendiri |
| 2 | Kontrak |
| 3 | Sewa |
| 4 | Bebas sewa milik orang lain |
| 5 | Bebas sewa milik orang tua/sanak/saudara |
| 6 | Dinas |
| 7 | Lainnya (mis. rumah adat) |

Catatan HREIS: bila tidak dapat digolongkan ke salah satu kategori di atas → **Lainnya**, misalnya rumah adat.
**Untuk PMT**, kategori ini pernah dikelompokkan ulang dengan **metode Tukey** dari 7 → **4 kategori**: `milik sendiri` · `bebas sewa/lainnya` · `sewa/kontrak` · `dinas` (Taufiq & Mariyah, BPS/STIS 2021).

### Tabel 4.2 — `jenis_atap_terluas` (Susenas `b6r5`, V563)

| Kode (2011) | Kategori 2011 (EN) | Kategori Susenas 2019+ (ID) | Layak? (HREIS) |
|---|---|---|---|
| 1 | Concrete | **Beton** | ✅ Layak |
| 2 | Roof tile | **Genteng** (termasuk keramik, metal/logam, tanah liat, fiber/polycarbonate) | ✅ Layak |
| 3 | Shingle | **Kayu/Sirap** (biasanya kayu ulin/kayu besi) | ✅ Layak |
| 4 | Iron sheet | **Seng** (seng rata, seng gelombang, decrabond, galvalum) | ✅ Layak |
| 5 | Asbestos | **Asbes** (campuran serat asbes & semen, umumnya bergelombang) | ❌ Tidak layak |
| 6 | Fiber/palm | **Jerami/ijuk/daun-daunan/rumbia** | ❌ Tidak layak |
| 7 | Other | **Lainnya** (mis. kardus, kaca) | ❌ Tidak layak |
| — | *(kategori tambahan 2019+)* | **Bambu** | ❌ Tidak layak |

### Tabel 4.3 — `jenis_dinding_terluas` (Susenas `b6r6`, V564)

| Kode (2011) | Kategori 2011 (EN) | Kategori Susenas 2019+ (ID) | Layak? (HREIS) |
|---|---|---|---|
| 1 | Concrete | **Tembok** (bata merah/batako, umumnya dilapisi plesteran semen; termasuk pasangan batu merah diplester dengan tiang kolom kayu balok berjarak 1–1,5 m) | ✅ Layak |
| 2 | Wood | **Kayu/papan** (termasuk tripleks, GRC, Calciboard) | ✅ Layak |
| 3 | Bamboo | **Bambu** | ❌ Tidak layak |
| 4 | Other | **Lainnya** (mis. seng, kardus) | ❌ Tidak layak |
| — | *(tambahan 2019+)* | **Plesteran anyaman bambu/kawat** (anyaman bambu/kawat ±1 m × 1 m dibingkai balok, diplester semen-pasir) | ✅ Layak |
| — | *(tambahan 2019+)* | **Anyaman bambu** (bambu diiris tipis lalu dirajut) | ❌ Tidak layak |
| — | *(tambahan 2019+)* | **Batang kayu** (batang pohon bulat, tanpa dibelah) | ⚠️ lihat catatan |

⚠️ HREIS §5: dinding **layak** = tembok / plesteran-anyaman bambu-kawat / kayu-papan. Namun kriteria "rumah layak huni" (§1.g HREIS) menyebut dinding layak = *"tembok/ plesteran anyaman bambu/kawat, kayu/papan **dan batang kayu**"*. **Inkonsistensi ini nyata di dokumen sumber** — pastikan mana yang dipakai NADI.

### Tabel 4.4 — `jenis_lantai_terluas` (Susenas `b6r7`, V565)

| Kode (2011) | Kategori 2011 (EN) | Kategori Susenas 2019+ (ID) | Layak? (HREIS) |
|---|---|---|---|
| 1 | Marble/ceramics/granite | **Marmer/granit** · **Keramik** *(2019+ dipisah 2 kategori)* | ✅ Layak |
| 2 | Terrazzo/tiles | **Ubin/tegel/teraso** | ✅ Layak |
| 3 | Cement | **Semen/bata merah** | ✅ Layak |
| 4 | Wood | **Kayu/papan** (termasuk tripleks, GRC, Calciboard) | ✅ Layak |
| 5 | Soil | **Tanah** (langsung permukaan bumi tanpa alas) | ❌ Tidak layak |
| 6 | Other | **Lainnya** | ❌ Tidak layak |
| — | *(tambahan 2019+)* | **Parket/vinil/karpet** | ✅ Layak |
| — | *(tambahan 2019+)* | **Bambu** | ❌ Tidak layak |

### Tabel 4.5 — `sumber_air_minum_utama` (Susenas `b6r9a`, V567)

| Kode | Kategori (ID) | Air minum layak? (SDGs/BPS sejak 2019) |
|---|---|---|
| 1 | Air kemasan bermerk | ✅ **bersyarat** — layak jika sumber air mandi/cuci dari leding/sumur bor-pompa/sumur terlindung/mata air terlindung/air hujan |
| 2 | Air isi ulang | ✅ **bersyarat** (syarat sama seperti kode 1) |
| 3 | Leding meteran | ✅ Layak |
| 4 | Leding eceran | ✅ Layak |
| 5 | Sumur bor/pompa | ✅ jika **jarak ke penampungan limbah > 10 m** · ❌ jika ≤ 10 m |
| 6 | Sumur terlindung | ✅ jika **jarak > 10 m** · ❌ jika ≤ 10 m |
| 7 | Sumur tak terlindung | ❌ Tidak layak |
| 8 | Mata air terlindung | ✅ Layak |
| 9 | Mata air tak terlindung | ❌ Tidak layak |
| 10 | Air sungai / permukaan (sungai, danau/waduk, kolam, irigasi) | ❌ Tidak layak |
| 11 | Air hujan | ✅ Layak |
| 12 | Lainnya | ❌ Tidak layak |

**Variabel pendamping WAJIB:** `jarak_ke_penampungan_limbah` (Susenas `b6r9b`, V568). Tanpa variabel ini, kelayakan air minum **tidak dapat dihitung** untuk kode 5 & 6.
**Variabel pendamping untuk kode 1 & 2:** `sumber_air_mandi_cuci` (Susenas `b6r12a`, V571).

### Tabel 4.6 — `fasilitas_bab` (Susenas `b6r13a`, V573)

| Kode | Kategori (ID) | Definisi (verbatim IHSN) |
|---|---|---|
| 1 | **Sendiri** — ada, digunakan hanya ART sendiri | "the defecation facility is only used by the respondent's household" |
| 2 | **Bersama** — ada, digunakan bersama rumah tangga tertentu | "used by the respondent's household together with several certain households" |
| 3 | **Umum** — ada, digunakan siapa pun | "used by every households, including respondent's household" |
| 4 | **Tidak ada** | "respondent's household does not have defecation facility" |

Susenas terbaru memecah lebih rinci: `Ada, digunakan hanya ART sendiri` · `Ada, digunakan bersama rumah tangga tertentu` · `Ada, di MCK komunal` · `Ada, di MCK umum/siapa pun menggunakan` · `Ada, ART tidak menggunakan` · `Tidak ada fasilitas`.

### Tabel 4.7 — `jenis_kloset` (Susenas `b6r13b`, V574)

| Kode | Kategori (ID) | Layak? |
|---|---|---|
| 1 | **Leher angsa** | ✅ syarat mutlak sanitasi layak |
| 2 | **Plengsengan** | ⚠️ *plengsengan tertutup* dianggap layak untuk fasilitas bersama/MCK komunal (Tabel 3 HREIS) |
| 3 | **Cemplung/cubluk** | ❌ |
| 4 | **Tidak ada / Lainnya** | ❌ |

Catatan: 56.392 kasus valid, 15.540 *invalid/sysmiss* (karena skip pattern dari `b6r13a` = "tidak ada").

### Tabel 4.8 — `pembuangan_akhir_tinja` (Susenas `b6r13c`, V575)

| Kode | Kategori (ID) | Layak? |
|---|---|---|
| 1 | **Tangki septik** (termasuk IPAL/SPAL) | ✅ Layak |
| 2 | Kolam/sawah | ❌ |
| 3 | Sungai/danau/laut | ❌ |
| 4 | **Lubang tanah** | ⚠️ layak **hanya jika wilayah tempat tinggalnya perdesaan** (kaidah SDGs) |
| 5 | Pantai/tanah lapang/kebun | ❌ |
| 6 | Lainnya | ❌ |

**KAIDAH SANITASI LAYAK (BPS/SDGs sejak 2019), verbatim HREIS:**
```
IF   fasilitas_bab ∈ {Ada & hanya ART sendiri, Ada & bersama RT tertentu, Ada & MCK komunal}
AND  jenis_kloset  = Leher Angsa
AND  pembuangan_akhir_tinja ∈ {Tangki septik, IPAL}
THEN Sanitasi Layak
ELSE Sanitasi Tidak Layak
```

### Tabel 4.9 — `sumber_penerangan_utama` (Susenas `b6r14a`, V576)

| Kode | Kategori (ID) |
|---|---|
| 1 | **Listrik PLN** |
| 2 | **Listrik non-PLN** |
| 3 | Petromaks / aladin |
| 4 | Pelita / sentir / obor |
| 5 | Lainnya |

### Tabel 4.10 — `daya_terpasang` (Susenas `b6r14b`, V577) — hanya untuk pengguna listrik PLN

| Kode | Kategori | Watt / VA |
|---|---|---|
| 1 | 450 VA | 450 |
| 2 | 900 VA | 900 |
| 3 | 1.300 VA | 1.300 |
| 4 | 2.200 VA | 2.200 |
| 5 | > 2.200 VA | >2.200 |
| 6 | **Tanpa meteran** | — |

> **Integrasi DTSEN:** diperkaya dengan `id_meteran_PLN` + status subsidi + jenis layanan (prabayar/pascabayar) dari data pelanggan PLN. BPS menyatakan indikator PMT DTSEN mencakup **"daya DAN konsumsi listrik"** — artinya ada potensi variabel `konsumsi_listrik_kwh` yang belum eksplisit di daftar variabel Perban. Sediakan kolomnya.

### Tabel 4.11 — `bahan_bakar_utama_memasak` (Susenas `b6r15`, V578)

| Kode | Kategori (ID) |
|---|---|
| 1 | Listrik |
| 2 | **Gas/LPG (elpiji)** |
| 3 | Gas kota |
| 4 | Minyak tanah |
| 5 | Arang |
| 6 | Briket |
| 7 | **Kayu bakar** |
| 8 | Lainnya |
| 9 | *(label tidak tersedia di katalog — kemungkinan "Tidak memasak di rumah"; **perlu verifikasi**)* |

### Tabel 4.12 — Variabel perumahan Susenas lain yang relevan untuk pengayaan NADI

| Variabel Susenas | ID | Label | Catatan |
|---|---|---|---|
| `b6r1` | V559 | Bangunan tempat tinggal yang disensus | Milik sendiri / bukan |
| `b6r2` | V560 | **Jumlah rumah tangga dalam bangunan sensus** | Setara `keluarga_dalam_rumah` DTSEN |
| `b6r4` | V562 | **Status lahan** bangunan tempat tinggal | ❌ tidak ada di daftar DTSEN |
| `b6r8` | V566 | **Luas lantai (m²)** | Basis `luas_lantai_per_kapita`; ambang layak **7,2 m²/kapita** |
| `b6r9b` | V568 | Jarak ke penampungan limbah terdekat | **Wajib** untuk kaidah air minum layak |
| `b6r10` | V569 | Penggunaan fasilitas air minum | sendiri / bersama / umum |
| `b6r11` | V570 | Cara memperoleh air minum | membeli / tidak membeli |
| `b6r12a` | V571 | **Sumber air mandi/cuci** | **Wajib** untuk kaidah air minum layak kode 1 & 2 |
| `b6r12b` | V572 | Cara memperoleh air mandi/cuci | — |

### Tabel 4.13 — Kriteria RUMAH LAYAK HUNI (4 kriteria, HREIS/BPS sejak 2019)

| # | Kriteria |
|---|---|
| 1 | **Kecukupan luas tempat tinggal** minimal **7,2 m² per kapita** (*sufficient living space*) |
| 2 | Memiliki akses terhadap **air minum layak** |
| 3 | Memiliki akses terhadap **sanitasi layak** |
| 4 | **Ketahanan bangunan** (*durable housing*): atap layak **AND** dinding layak **AND** lantai layak |

> Aturan ketahanan bangunan: *"Jika **salah satu** dari jenis material atap, dinding dan lantai yang digunakan berkategori tidak layak, maka status ketahanan bangunan tersebut berkategori **tidak layak**."*

---

## 5. VARIABEL KEPEMILIKAN ASET DTSEN

**Sumber:** Rancangan Perban BPS DTSEN, Lampiran, variabel keluarga no. 26 grup `Kepemilikan:` (hal. 28–29).

### Tabel 5.1 — Sub-variabel aset DTSEN (nama & keterangan VERBATIM dari regulasi)

| # | Nama Sub-Variabel (resmi) | Keterangan (verbatim) | Tipe Data | Satuan / Domain |
|---|---|---|---|---|
| 1 | `tabung_gas` | "jumlah tabung gas **minimal 5,5 kg** yang dimiliki" | `SMALLINT` | unit, ≥0 |
| 2 | `lemari_es` | "jumlah lemari es atau kulkas yang dimiliki" | `SMALLINT` | unit, ≥0 |
| 3 | `AC` | "jumlah AC (Air Conditioner) yang dimiliki" | `SMALLINT` | unit, ≥0 |
| 4 | `pemanas_air` | "jumlah pemanas air (WaterHeater) untuk mandi" | `SMALLINT` | unit, ≥0 |
| 5 | `telepon_rumah` | "jumlah telepon rumah atau **PSTN** yang dimiliki" | `SMALLINT` | unit, ≥0 |
| 6 | `tv_datar` | "jumlah televisi datar (**min. 30 inch**) yang dimiliki" | `SMALLINT` | unit, ≥0 |
| 7 | `emas_perhiasan` | "banyaknya perhiasan emas (**gram**)" | `DECIMAL(10,2)` | **gram**, ≥0 |
| 8 | `komputer_laptop_tablet` | "jumlah komputer/PC atau laptop atau tablet" | `SMALLINT` | unit, ≥0 |
| 9 | `sepeda_motor` | "jumlah sepeda motor yang dimiliki" | `SMALLINT` | unit, ≥0 |
| 10 | `sepeda` | "jumlah sepeda yang dimiliki" | `SMALLINT` | unit, ≥0 |
| 11 | `mobil` | "jumlah mobil yang dimiliki" | `SMALLINT` | unit, ≥0 |
| 12 | `perahu` | "jumlah perahu yang dimiliki" | `SMALLINT` | unit, ≥0 |
| 13 | `kapal_perahu_motor` | "jumlah kapal atau perahu motor yang dimiliki" | `SMALLINT` | unit, ≥0 |
| 14 | `smartphone` | "jumlah smartphone yang dimiliki" | `SMALLINT` | unit, ≥0 |
| 15 | `sawah_kebun` | "luas lahan sawah/kebun diusahakan yang dimiliki (**Ha**)" | `DECIMAL(10,4)` | **hektar**, ≥0 |
| 16 | `lahan_lainnya` | "kepemilikan lahan **selain yang dihuni**" | `BOOLEAN` atau `DECIMAL` | ya/tidak atau luas |
| 17 | `rumah_lainnya` | "kepemilikan rumah **selain yang dihuni**" | `BOOLEAN` atau `SMALLINT` | ya/tidak atau jumlah |
| 18 | `ternak_besar` | "jumlah ternak besar (**sapi, kerbau, kuda**) yang dimiliki" | `SMALLINT` | ekor, ≥0 |
| 19 | `ternak_kecil` | "jumlah ternak kecil (**kambing, domba, babi**) yang dimiliki" | `SMALLINT` | ekor, ≥0 |

### 5.2 ⚠️ Pergeseran desain yang KRUSIAL vs DTKS/Susenas lama

Pada Susenas/PPLS/DTKS klasik, aset direkam sebagai **BOOLEAN** (`b7r4a`–`b7r4j`: *"Is the household owned the bicycle?"*).
**DTSEN merekam sebagai JUMLAH (count)** dan bahkan **kuantitas kontinu** (gram emas, hektar lahan).
→ Skema NADI **HARUS** memakai `SMALLINT`/`DECIMAL`, **bukan** `BOOLEAN`, agar kompatibel dengan DTSEN.

### Tabel 5.3 — Perbandingan daftar aset: Susenas 2011 vs DTSEN 2025

| Aset | Susenas 2011 (`b7r4x`, boolean) | DTSEN 2025 | Perubahan |
|---|---|---|---|
| Sepeda | ✅ `b7r4a` (V592) | ✅ `sepeda` | boolean → **count** |
| Sepeda motor | ✅ `b7r4b` (V593) | ✅ `sepeda_motor` | boolean → count |
| Perahu | ✅ `b7r4c` (V594) | ✅ `perahu` | boolean → count |
| TV kabel | ✅ `b7r4d` (V595) | ❌ diganti `tv_datar` (min. 30") | **GANTI DEFINISI** |
| AC | ✅ `b7r4e` (V596) | ✅ `AC` | boolean → count |
| Pemanas air | ✅ `b7r4f` (V597) | ✅ `pemanas_air` | boolean → count |
| Tabung gas | ✅ `b7r4g` (V598) — **> 12 kg** | ✅ `tabung_gas` — **≥ 5,5 kg** | **AMBANG TURUN** |
| Lemari es | ✅ `b7r4h` (V599) | ✅ `lemari_es` | boolean → count |
| Perahu motor | ✅ `b7r4i` (V600) | ✅ `kapal_perahu_motor` | boolean → count |
| Mobil | ✅ `b7r4j` (V601) | ✅ `mobil` | boolean → count |
| Emas/perhiasan | (di PPLS/BDT) | ✅ `emas_perhiasan` (**gram**) | → kuantitatif |
| Komputer/laptop/tablet | (di PPLS/BDT) | ✅ `komputer_laptop_tablet` | → count |
| Telepon rumah/PSTN | (di PPLS/BDT) | ✅ `telepon_rumah` | → count |
| **Smartphone** | ❌ tidak ada | ✅ `smartphone` | **VARIABEL BARU** |
| Ternak | (di PPLS/BDT, gabungan) | ✅ `ternak_besar` + `ternak_kecil` | **dipecah 2** |
| Lahan sawah/kebun | (di PPLS/BDT) | ✅ `sawah_kebun` (Ha) | → kuantitatif |
| Lahan/rumah lain | (di PPLS/BDT) | ✅ `lahan_lainnya`, `rumah_lainnya` | — |

---

## 6. VARIABEL INDIVIDU — KODE KATEGORI

**Sumber kode:** IHSN catalog 3037 (Susenas Maret 2011), datafile `susenas11mar_ki` (Household Member Information, 284.539 kasus).
https://catalog.ihsn.org/catalog/3037/data-dictionary/F10?file_name=susenas11mar_ki

### Tabel 6.1 — `status_hubungan_keluarga` (Susenas `hb`, V423)

| Kode | Kategori (ID) |
|---|---|
| 1 | **Kepala keluarga / kepala rumah tangga** |
| 2 | Istri / suami |
| 3 | Anak |
| 4 | Menantu |
| 5 | Cucu |
| 6 | Orang tua / mertua |
| 7 | Famili lain |
| 8 | Pembantu rumah tangga |
| 9 | Lainnya |

> Susenas terbaru dapat menambah kode `10` (sopir/tukang kebun) atau memisah kategori 8 & 9 — **perlu verifikasi**.

### Tabel 6.2 — `partisipasi_sekolah` (Susenas `b5r14`, V488) — ART usia 5 tahun ke atas

| Kode | Kategori (ID) |
|---|---|
| 1 | **Tidak/belum pernah sekolah** |
| 2 | **Masih sekolah** |
| 3 | **Tidak bersekolah lagi** |

### Tabel 6.3 — `ijazah_tertinggi` (Susenas `b5r17`, V491) — 15 kategori

| Kode | Kategori (ID) |
|---|---|
| 1 | Tidak punya ijazah SD |
| 2 | SD |
| 3 | Madrasah Ibtidaiyah |
| 4 | Paket A |
| 5 | SMP |
| 6 | Madrasah Tsanawiyah |
| 7 | Paket B |
| 8 | SMA |
| 9 | Madrasah Aliyah |
| 10 | SMK (sekolah kejuruan) |
| 11 | Paket C |
| 12 | Diploma 1 / Diploma 2 |
| 13 | Diploma 3 |
| 14 | Diploma 4 / S1 |
| 15 | S2 / S3 |

### Tabel 6.4 — `lapangan_usaha` pekerjaan utama (Susenas `b5r30`, V519) — 19 kategori

| Kode | Kategori (ID) |
|---|---|
| 1 | Pertanian tanaman padi & palawija |
| 2 | Hortikultura |
| 3 | Perkebunan |
| 4 | Perikanan |
| 5 | Peternakan |
| 6 | Kehutanan & pertanian lainnya |
| 7 | Pertambangan & penggalian |
| 8 | Industri pengolahan |
| 9 | Listrik dan gas |
| 10 | Konstruksi / bangunan |
| 11 | Perdagangan |
| 12 | Hotel dan rumah makan |
| 13 | Transportasi & pergudangan |
| 14 | Informasi dan komunikasi |
| 15 | Keuangan dan asuransi |
| 16 | Jasa pendidikan |
| 17 | Jasa kesehatan |
| 18 | Jasa kemasyarakatan, pemerintahan & perorangan |
| 19 | Lainnya |

> **Rekomendasi:** untuk sistem baru, pakai **KBLI 2020 kategori A–U** (1 huruf) sebagai penyimpanan kanonik dan simpan mapping ke 19 kode di atas untuk interoperabilitas DTSEN.

### Tabel 6.5 — `status_pekerjaan` / kedudukan dalam pekerjaan utama

> ⚠️ **LOW CONFIDENCE.** Kode berikut dari **standar BPS umum (Sakernas/Susenas)**, **BUKAN** diambil dari katalog resmi dalam riset ini. Variabel ini tidak terekspos di data dictionary IHSN yang diakses. **Verifikasi sebelum produksi.**

| Kode | Kategori (ID) |
|---|---|
| 1 | Berusaha sendiri |
| 2 | Berusaha dibantu buruh tidak tetap / buruh tak dibayar |
| 3 | Berusaha dibantu buruh tetap / buruh dibayar |
| 4 | Buruh / karyawan / pegawai |
| 5 | Pekerja bebas di pertanian |
| 6 | Pekerja bebas di non-pertanian |
| 7 | Pekerja keluarga / pekerja tak dibayar |

### Tabel 6.6 — `penyandang_disabilitas` — DUA kerangka yang berbeda

DTSEN mencatat *"status penyandang disabilitas pada individu"* tanpa merinci kerangka. Ada **dua kerangka** yang harus dipilih secara sadar:

**(A) Kerangka fungsional — Washington Group Short Set (WGSS)**
Dipakai BPS di Susenas **sejak 2023**, sesuai UU No. 8 Tahun 2016. Enam domain, masing-masing dengan 4 tingkat kesulitan.

| Domain | Pertanyaan |
|---|---|
| 1 | **Penglihatan** — melihat, walau memakai kacamata |
| 2 | **Pendengaran** — mendengar, walau memakai alat bantu dengar |
| 3 | **Berjalan / naik tangga** |
| 4 | **Mengingat / berkonsentrasi** |
| 5 | **Mengurus diri sendiri** (mandi, berpakaian) |
| 6 | **Berkomunikasi** (memahami / dipahami orang lain) |

| Kode jawaban | Kategori |
|---|---|
| 1 | Tidak ada kesulitan |
| 2 | Ada sedikit kesulitan |
| 3 | Ada banyak kesulitan |
| 4 | Tidak dapat melakukan sama sekali |

Klasifikasi turunan BPS (Susenas 2020): **disabilitas ringan / sedang / berat**.

**(B) Kerangka jenis disabilitas UU No. 8 Tahun 2016**
Dipakai Kemensos & tercatat di metadata SIRuSa BPS (https://sirusa.web.bps.go.id/metadata/variabel/73550):

| Kode | Kategori |
|---|---|
| 1 | Penyandang Disabilitas **Fisik** |
| 2 | Penyandang Disabilitas **Mental** |
| 3 | Penyandang Disabilitas **Intelektual** |
| 4 | Penyandang Disabilitas **Sensorik** |
| 5 | Penyandang Disabilitas **Ganda** |

**REKOMENDASI NADI:** simpan **KEDUANYA** — WGSS 6 domain (konsistensi dengan Susenas/DTSEN & input pemeringkatan) + 5 jenis UU 8/2016 (interoperabilitas dengan program Kemensos/ATENSI).

### Tabel 6.7 — Variabel individu Blok IV Regsosek yang BELUM masuk daftar wajib DTSEN

| Variabel | Keterangan | Status di DTSEN |
|---|---|---|
| `punya_akta_lahir` | Kepemilikan akta kelahiran | ❌ tidak di daftar Perban (ada di Regsosek Blok IV.A) |
| `status_rekam_ktp_el` | Sudah rekam KTP-el? | ❌ — bisa diturunkan dari hasil validasi Dukcapil |
| `ibu_hamil` | Status kehamilan ART perempuan | ❌ di daftar Perban; ✅ ada di Regsosek Blok IV.E; **komponen PKH** |
| `status_gizi_balita` | BB/U, TB/U, BB/TB balita | ❌ di daftar Perban; ✅ ada di Regsosek Blok IV.E; **komponen PKH & program stunting** |
| `penyakit_kronis` | Keluhan kesehatan kronis/menahun | ✅ **ADA** di daftar DTSEN (jenis penyakitnya tidak dirinci di Perban) |

---

## 7. DTKS, PBDT 2015, SIKS-NG & CEK BANSOS

### 7.1 Garis waktu basis data kemiskinan Indonesia

| Tahun | Nama | Penyelenggara | Cakupan |
|---|---|---|---|
| 2005 | **PSE05** — Pendataan Sosial Ekonomi | BPS | RT miskin |
| 2008 | **PPLS08** | BPS | RT miskin |
| 2011 | **PPLS11** → **Basis Data Terpadu (BDT)** | BPS → TNP2K | **25 juta RT** (40% terbawah) |
| 2015 | **PBDT 2015** — Pemutakhiran BDT | BPS + TNP2K | **25,7 juta RT** (proses sensus) |
| 2019– | **DTKS** | Kemensos (Pusdatin Kesos) | PPKS + penerima bansos + PSKS |
| 2021 | **P3KE** (dari Pendataan Keluarga BKKBN 2021) | BKKBN → Kemenko PMK | keluarga berisiko miskin ekstrem |
| 2022 | **Regsosek** | BPS → Bappenas | **seluruh penduduk Indonesia** |
| **2025–** | **DTSEN** | **BPS** | **290,13 juta individu / 95,98 juta keluarga** (v3, 10 Juli 2026) |

**PBDT 2015 terdiri atas 3 bagian besar:** (1) **Forum Konsultasi Publik**, (2) **Pendataan Rumah Tangga**, (3) **Pemeringkatan serta pengelompokan status kesejahteraan rumah tangga**.
PBDT 2015 = kegiatan nasional memperbaiki data karakteristik rumah tangga BDT yang dikumpulkan 2011 dan dianggap sudah berubah.

**Kuesioner PPLS 2011/2015** dirancang ringkas (**2 halaman**), fokus pada variabel yang merupakan **prediktor terkuat konsumsi/kemiskinan**, dengan konsultasi K/L pelaksana program agar informasinya memenuhi kebutuhan mereka.

### 7.2 DTKS — Permensos No. 3 Tahun 2021

**Judul:** Peraturan Menteri Sosial No. 3 Tahun 2021 tentang **Pengelolaan Data Terpadu Kesejahteraan Sosial**
**Ditetapkan:** 27 Mei 2021 (Menteri Sosial **Tri Rismaharini**) · Diundangkan 31 Mei 2021 · **BN 2021 No. 578**
**PDF (berhasil diekstrak penuh):** https://peraturan.go.id/files/bn578-2021.pdf
Menggantikan **Permensos No. 5 Tahun 2019** & **Permensos No. 11 Tahun 2019**.

**Definisi DTKS (Pasal 1 angka 1), verbatim:**
> *"Data Terpadu Kesejahteraan Sosial adalah **data induk** yang berisi data **pemerlu pelayanan kesejahteraan sosial**, **penerima bantuan dan pemberdayaan sosial**, serta **potensi dan sumber kesejahteraan sosial**."*

**Definisi Pengelolaan Data (Pasal 1 angka 2), verbatim:**
> *"kegiatan sistematis dalam pengaturan, penyimpanan, dan pemeliharaan data yang mencakup **proses usulan data, verifikasi dan validasi, penetapan, dan penggunaan data**..."*

**Cakupan DTKS (Pasal 2 ayat 2–3):** (a) **PPKS** — Pemerlu Pelayanan Kesejahteraan Sosial; (b) penerima bantuan & pemberdayaan sosial; (c) **PSKS** — Potensi dan Sumber Kesejahteraan Sosial. Masing-masing berupa **perseorangan, keluarga, kelompok, dan masyarakat**.

**Tahapan Pengelolaan Data (Pasal 2 ayat 1):**
```
a. Proses Usulan Data serta Verifikasi dan Validasi
b. Pengendalian/Penjaminan Kualitas
c. Penetapan
d. Penggunaan
```

**Kriteria DTKS (Pasal 3 ayat 2)** — ditetapkan Menteri:

| Huruf | Kriteria |
|---|---|
| a | Kemiskinan |
| b | Ketelantaran |
| c | Kecacatan |
| d | Keterpencilan |
| e | Ketunaan sosial dan penyimpangan perilaku |
| f | Korban bencana |
| g | Korban tindak kekerasan, eksploitasi, dan diskriminasi |
| h | Kriteria lainnya yang ditetapkan Menteri |

**Jalur Proses Usulan Data (Pasal 4):**

| Huruf | Jalur |
|---|---|
| a | **Musyawarah desa atau kelurahan** (atau nama lain) |
| b | **Usulan Kementerian Sosial** — hanya dalam kondisi kedaruratan bencana, PPKS ditemukan tidak tertangani/belum terdata, atau kondisi lain yang mengancam keselamatan (Pasal 9 ayat 2) |
| c | **Pendaftaran mandiri** menggunakan aplikasi **SIKS-NG** |

**Asal usulan via musdes/muskel (Pasal 5):** a. RT/RW · b. kepala dusun · c. lurah/kepala desa · d. **PSKS** · e. pendaftaran mandiri kepada perangkat desa/kelurahan.

**Alur berjenjang (Pasal 6–8, 12):**
```
Musdes/Muskel
  → Bupati/Walikota c.q. DINAS SOSIAL kab/kota  [WAJIB melakukan Verifikasi & Validasi]
  → hasil verval dikirim melalui aplikasi SIKS-NG
  → Pemerintah Daerah PROVINSI (diteruskan)
  → MENTERI SOSIAL
  → Penilaian oleh satker pengelola data Kemensos (kriteria integritas data)
     └─ jika tidak memenuhi: DIKEMBALIKAN ke Pemda kab/kota untuk diperbaiki
     └─ jika masih bermasalah: diserahkan ke PERGURUAN TINGGI untuk Penjaminan Kualitas
  → PENETAPAN oleh Menteri (Pasal 12)
```

**Kriteria integritas data (Pasal 8 ayat 3)** — sangat relevan sebagai aturan validasi NADI:

| Huruf | Kriteria |
|---|---|
| a | Data perorangan bersifat **individual dan tunggal** |
| b | Data perorangan mempunyai **NIK, nama, alamat** sesuai data kependudukan Dukcapil |
| c | Data keluarga/kelompok/masyarakat merupakan **himpunan data perorangan** |
| d | Data anggota keluarga **tidak tumpang tindih** dengan anggota keluarga lain |
| e | **Kelengkapan atribut data** |

**Pengendalian/Penjaminan Kualitas (Pasal 11):** dilakukan oleh **perguruan tinggi yang ditetapkan Menteri**, dipicu bila ada ketidaksepahaman/ketidaksesuaian/perbedaan data antara: (a) Pemda kab/kota ↔ desa/kelurahan; (b) Pemda provinsi ↔ Pemda kab/kota; (c) perbedaan data lainnya.

**Frekuensi (perbandingan antar-regulasi):**

| Aspek | UU 13/2011 | Permensos 5/2019 | **Permensos 3/2021** |
|---|---|---|---|
| Verval rumah tangga miskin | min. **2 tahun** sekali (Pasal 8 ayat 5) | min. **1 tahun** sekali (Pasal 8) | **tidak lagi disebut** |
| Penetapan DTKS oleh Menteri | — | min. 1× per **6 bulan** (Pasal 9) | **1× setiap BULAN** (Pasal 12 ayat 3) |

### 7.3 "44 indikator kemiskinan" DTKS

Studi SMERU (2022) menyebut komponen data yang dimutakhirkan dalam DTKS mengacu pada **"44 indikator kemiskinan yang ditetapkan oleh Pemerintah Pusat"**.

> ⚠️ **DAFTAR LENGKAP 44 INDIKATOR TERSEBUT TIDAK DITEMUKAN** dalam riset ini. Tidak dipublikasikan sebagai lampiran Permensos 3/2021 maupun di JDIH Kemensos yang dapat diakses. **Jangan mengarang isinya.**
> Temuan lapangan SMERU: banyak daerah **tidak** memutakhirkan seluruh 44 komponen — hanya mencocokkan NIK dan data administrasi, sementara data kondisi kesejahteraan rumah tangga hanya sebagian atau tidak dimutakhirkan sama sekali. Daerah yang sudah pakai **SIKS-Droid** (DKI Jakarta, Kab. Maros) cenderung memutakhirkan seluruh komponen. **DKI Jakarta** punya *negative list* sendiri sebagai penyaring awal calon RT DTKS.

Sumber: SMERU Research Institute, *Mendorong Pemutakhiran Berkelanjutan terhadap Data Terpadu Kesejahteraan Sosial* — https://smeru.or.id/id/file/3891/download?token=wk_MwoCK

### 7.4 SIKS-NG (Sistem Informasi Kesejahteraan Sosial — Next Generation)

| Aspek | Detail |
|---|---|
| Definisi resmi | *"sistem informasi yang mendukung proses pengelolaan Data Terpadu Kesejahteraan Sosial"* (Permensos 3/2021 Pasal 1 angka 14) |
| Mode | **Luring/offline** (berbasis desktop) & **daring/online** (berbasis web) |
| Varian mobile | **SIKS-Droid** — petugas tidak perlu mencetak *prelist*, input langsung di gawai saat kunjungan rumah (CAPI) |
| Aplikasi pemantau | **SIKS-Dataku** (rilis 2019, Play Store) → berganti nama **SIKSMobile** (2021) |
| Aktor | Koordinator verval kab/kota (**BPS kab/kota**), supervisor, operator DTKS kab/kota, operator DTKS desa/kelurahan, Dinsos kab/kota, Bappeda, **Pusdatin Kesos** |

**Alur verval DTKS via SIKS-NG (temuan lapangan SMERU, 10 tahap):**
```
Tahap 1  : Unduh PRELIST AWAL via SIKS-NG (dirinci berdasarkan lokasi tempat tinggal)
           → jika manual: dicetak oleh operator kab/kota
           → jika SIKS-Droid: prelist dikirim ke gawai petugas terdaftar
Tahap 2  : Bimbingan teknis (bimtek) petugas
Tahap 3  : MUSYAWARAH DESA/KELURAHAN
           → difasilitasi petugas pengumpul data
           → melibatkan kepala desa/lurah, aparat, Dinsos kab/kota
           → hasil didokumentasikan dalam BERITA ACARA forum musyawarah,
             ditandatangani pemerintah desa/kelurahan
Tahap 4–8: Kunjungan rumah / wawancara (kertas atau CAPI)
Tahap 9  : Input hasil verval ke SIKS-NG oleh operator (luring/daring)
Tahap 10 : Pengiriman data ke PUSDATIN KESOS
```
Sumber data usulan baru umumnya: pendataan ketua RT, pendamping program, **Puskesos** (Pusat Kesejahteraan Sosial), dan pendaftaran mandiri.

### 7.5 Cek Bansos & Cek DTSEN — mekanisme usul/sanggah era DTSEN

| Kanal | URL / Aplikasi | Fungsi |
|---|---|---|
| **Cek Bansos** (Kemensos) | https://cekbansos.kemensos.go.id/ + aplikasi Android/iOS (**versi ≥ 5.0**) | Cek status penerima; menu **"Usul/Sanggah"**; daftar akun dengan **NIK + Nomor KK** |
| **Cek DTSEN** (BPS) | `dtsen-form.bps.go.id` (disebut juga `cekdtsen.bps.go.id`) | Penelusuran mandiri posisi **desil** dengan input **NIK 16 digit**; kanal pemutakhiran mandiri |
| **SIKS-NG** | operator desa/kelurahan & Dinsos | Jalur resmi usulan/perbaikan berjenjang |
| Luring | Kantor desa/kelurahan → Dinas Sosial kab/kota | Petugas kesejahteraan sosial |

**Dokumen yang lazim disiapkan untuk USUL** *(sumber sekunder — praktik lapangan, bukan regulasi):* foto rumah tampak depan (jelas, tidak blur), foto KTP-el, foto KK, dan bila ada Surat Keterangan Tidak Mampu (SKTM) dari RT/RW.

**Prinsip penting yang dinyatakan BPS:** perubahan desil **TIDAK INSTAN**. Data yang diperbarui tetap melalui verifikasi faktual, pemadanan, snapshot, dan **pemeringkatan ulang berkala (triwulanan)** sebelum status desil baru ditetapkan resmi.

---

## 8. KEPESERTAAN PROGRAM

### Tabel 8.1 — Program yang menjadi variabel kepesertaan (Regsosek Blok V + praktik DTSEN)

| Kode usulan | Program | Singkatan | Penyelenggara | Unit penerima |
|---|---|---|---|---|
| `PKH` | Program Keluarga Harapan | PKH | Kemensos | **Keluarga (KPM)** |
| `SEMBAKO` | Program Sembako / Bantuan Pangan Non-Tunai | BPNT | Kemensos | Keluarga (KPM) |
| `PBI_JKN` | Penerima Bantuan Iuran — Jaminan Kesehatan Nasional | PBI-JKN / PBI-JK | Kemenkes / BPJS Kesehatan | **Individu** |
| `PIP` | Program Indonesia Pintar (Kartu Indonesia Pintar) | PIP / KIP | Kemendikdasmen | Individu (siswa) |
| `KIP_KULIAH` | KIP Kuliah | — | Kemendikti | Individu (mahasiswa) |
| `BLT` | Bantuan Langsung Tunai (termasuk BLT Dana Desa, BLT-BBM) | BLT | Kemensos / Kemendes / Pemda | Keluarga |
| `BST` | Bantuan Sosial Tunai (era COVID-19) | BST | Kemensos | Keluarga |
| `RASTRA` | Beras Sejahtera (pendahulu BPNT; historis: Raskin) | Rastra | Bulog / Kemensos | Keluarga |
| `BANPANG` | Bantuan Pangan Beras | — | Bapanas / Bulog | Keluarga |
| `KUR` | Kredit Usaha Rakyat | KUR | Kemenkeu / bank penyalur | Individu / usaha |
| `ATENSI` | Asistensi Rehabilitasi Sosial | ATENSI | Kemensos | Individu |
| `PENA` | Pahlawan Ekonomi Nusantara (program graduasi) | PENA | Kemensos | Keluarga |
| `MBG` | Makan Bergizi Gratis | MBG | BGN | Individu |
| `BSU` | Bantuan Subsidi Upah | BSU | Kemnaker | Individu |
| `SUBSIDI_LISTRIK` | Subsidi listrik daya 450/900 VA | — | PLN / ESDM | Keluarga (via ID meteran) |
| `SUBSIDI_LPG3KG` | Subsidi LPG 3 kg | — | Pertamina / ESDM | Keluarga |

### Tabel 8.2 — Sasaran berdasarkan desil (kondisi 2026)

| Desil | Kelompok | Program utama |
|---|---|---|
| **1–4** | Miskin ekstrem → rentan miskin | **PKH · BPNT/Sembako · PBI-JKN · ATENSI · PIP** |
| 5 | Rentan | Masih berpeluang untuk **PBI-JK** dan program tertentu |
| 6–10 | Bukan prioritas | Umumnya bukan sasaran bansos reguler |

Catatan: BPNT/Sembako sebelumnya menjangkau hingga desil 5, kini **difokuskan ke desil 1–4**.
**Terdaftar di DTSEN ≠ otomatis menerima bantuan.** Status tidak layak bisa terjadi karena verifikasi lapangan menunjukkan perbaikan kondisi ekonomi, atau karena **keterbatasan kuota wilayah** pada periode berjalan.

### Tabel 8.3 — Besaran bantuan PKH 2026 ⚠️ SUMBER SEKUNDER, LOW CONFIDENCE

| Komponen | Per tahap (triwulanan) | Per tahun |
|---|---|---|
| Ibu hamil | Rp750.000 | Rp3.000.000 |
| Balita (usia 0–6 tahun) | Rp750.000 | Rp3.000.000 |
| Anak SD | Rp225.000 | Rp900.000 |
| Anak SMP | Rp375.000 | Rp1.500.000 |
| Anak SMA | Rp500.000 | Rp2.000.000 |
| Lansia ≥ 70 tahun | Rp750.000 | Rp3.000.000 |
| Penyandang disabilitas berat | Rp750.000 | Rp3.000.000 |

⚠️ Angka ini dari media/blog, **BUKAN** dari Permensos/Kepmensos. **Verifikasi ke Kemensos sebelum dipakai.**

---

## 9. DESIL KESEJAHTERAAN & PROXY MEANS TEST (PMT)

### 9.1 Definisi desil — kutipan VERBATIM dari rancangan Perban BPS

> *"Desil merupakan kelompok yang membagi data yang sudah diurutkan ke dalam sepuluh bagian yang sama besar. Masing-masing bagian disebut desil satu, desil dua, hingga desil kesepuluh. **Desil yang digunakan adalah desil nasional**, sehingga data diurutkan berdasarkan **peringkat nasional** untuk dapat menentukan posisi desil dari setiap data."*

| Desil | Arti |
|---|---|
| **1** | ~10% keluarga dengan tingkat kesejahteraan **relatif paling rendah** |
| 2 | 10–20% terbawah |
| 3–9 | … |
| **10** | ~10% keluarga dengan tingkat kesejahteraan **relatif paling tinggi** |

**Penegasan resmi BPS (Kepala BPS Amalia Adininggar Widyasanti, Agustus 2026):**
- Desil menunjukkan **posisi RELATIF** suatu keluarga dibandingkan keluarga lainnya.
- Desil **BUKAN** ukuran langsung pendapatan atau kekayaan.
- Desil **BUKAN** penentu mutlak kemiskinan.
- Keluarga dalam desil yang sama **tidak** selalu punya pendapatan/pengeluaran/kondisi sosial ekonomi yang identik.

### 9.2 Indikator yang dipakai dalam pemeringkatan (pernyataan resmi BPS)

| # | Indikator |
|---|---|
| 1 | Kondisi tempat tinggal |
| 2 | Sumber air minum |
| 3 | Bahan bakar dan energi untuk memasak |
| 4 | Kepemilikan aset |
| 5 | **Daya dan konsumsi listrik** |
| 6 | Komposisi keluarga |
| 7 | Pendidikan |
| 8 | Pekerjaan |
| 9 | Kesehatan |
| 10 | Kondisi disabilitas |

Rancangan Perban menyebut kelompok variabel PMT: **demografi, pendidikan, ketenagakerjaan, kondisi perumahan, dan kepemilikan aset**.

### 9.3 Metode PMT — tahapan menurut rancangan Perban BPS (verbatim)

> *"Pemeringkatan Kesejahteraan dilakukan pada keluarga hasil pembaruan yang telah divalidasi dengan Data Kependudukan menggunakan **Proxy Means Test (PMT)**. PMT merupakan metode untuk memprediksi tingkat konsumsi (**pengeluaran perkapita**) berdasarkan variabel individu dan keluarga yang terdiri dari: variabel demografi, pendidikan, ketenagakerjaan, kondisi perumahan, dan kepemilikan aset. **Model PMT dibangun dengan data Susenas** karena memiliki seluruh informasi tersebut."*

```
a. Mengembangkan model PMT dengan data terkini (basis: Susenas)
b. Menghitung prediksi pengeluaran perkapita dengan model PMT
c. Mendapatkan peringkat kesejahteraan keluarga dari urutan prediksi pengeluaran perkapita
d. Menentukan DESIL dengan membentuk kelompok berdasarkan peringkat kesejahteraan
```
Ditambah: *"pemeringkatan juga dapat memanfaatkan **informasi tambahan dari data administrasi dan/atau data hasil kegiatan yang diselenggarakan oleh kementerian/lembaga lainnya** yang relevan dan berkaitan dengan kesejahteraan."*

### 9.4 Model matematis PMT (Taufiq & Mariyah, BPS + Politeknik Statistika STIS, 2021)

```
ln(y_i) = α + β·X_i + ε_i          … (1)
ŷ_i     = exp(α + β·X_i)           … (2)

y  = pengeluaran per kapita rumah tangga (variabel respon)
X  = variabel penjelas (karakteristik RT & ART)
β  = koefisien regresi
ε  = error
```

**Spesifikasi model (praktik TNP2K/BPS pada PBDT 2015):**

| Aspek | Detail |
|---|---|
| Teknik | **Regresi forward-stepwise** |
| Transformasi respon | **Log** (distribusi pengeluaran sangat *skewed*) |
| Level model | **Per kabupaten/kota** — **514 kab/kota**, bukan satu model nasional |
| Data latih | **Pooling Susenas Maret 2016–2020**, total **1.533.746 rumah tangga** |
| Sampel | **Seluruh** rumah tangga Susenas (bukan hanya 40% terbawah) — jika hanya kelompok bawah, akurasi menurun karena model sulit menemukan variabel pembeda |
| Faktor koreksi wilayah | **Indeks Kesulitan Geografis (IKG)** dari **Podes 2018** |

**Perlakuan variabel (penting untuk feature engineering NADI):**
| Jenis | Perlakuan |
|---|---|
| Karakteristik **rumah tangga/keluarga** | Dijadikan **dummy variable** |
| Karakteristik **anggota rumah tangga** | Dijadikan **jumlah ART dengan karakteristik tersebut** (count) |
| Kategori bertingkat | **Pengelompokan ulang dengan metode Tukey** — kategori yang tidak berbeda signifikan digabung. Contoh: status kepemilikan bangunan **7 kategori → 4 kategori** |

### Tabel 9.1 — Klasifikasi variabel penjelas PMT menurut kelompok (Taufiq & Mariyah 2021, Tabel 1 — VERBATIM)

| Kelompok Variabel | Variabel |
|---|---|
| **Demografi** | Jumlah ART dengan rentang usia tertentu |
| **Pendidikan** | Persentase ART dalam ruta yang menamatkan jenjang pendidikan tertentu |
| **Pekerjaan** | Sektor Pekerjaan, Status dalam Pekerjaan |
| **Karakteristik Perumahan** | Jenis Lantai, Jenis Atap, Jenis Dinding, Penerangan Utama, Sumber Air Minum, Sanitasi, Status Kepemilikan Rumah |
| **Kepemilikan Aset** | Mobil, Komputer/Laptop, Kulkas, Emas, Perahu Motor, Sepeda Motor, Perahu, Telefon Rumah |
| **Kewilayahan** | Indeks Kesulitan Geografis (IKG) |

### Tabel 9.2 — Kinerja model

| Model | Rata-rata Inclusion Error | Rata-rata Exclusion Error |
|---|---|---|
| **PMT** (regresi forward-stepwise) | **0,29** | **0,29** |
| **Machine Learning** (MARS, KNN, Decision Tree, Bagging) | **0,21** | lebih tinggi dari IE — *"belum cukup sensitif dalam mengurangi exclusion error"* |

**Definisi error:**
- **Inclusion error (IE):** rumah tangga yang sebenarnya tergolong **sejahtera** masuk ke kategori penerima manfaat program.
- **Exclusion error (EE):** rumah tangga yang sebenarnya tergolong **tidak sejahtera** justru **tidak** ada di daftar penerima manfaat.
- Cut-off evaluasi lazim: **40% terbawah**.

Sumber: https://prosiding.stis.ac.id/index.php/semnasoffstat/article/download/1018/328/

### 9.5 Pemeringkatan DTSEN VERSI PERTAMA (prosedur khusus, hanya untuk data awal hasil integrasi)

Karena 3 sumber utama berbeda **sumber, waktu, cakupan, dan kelengkapan**, BPS memakai prosedur khusus:

```
1. EKSPLORASI DATA
   a. Pengecekan cakupan & ketersediaan variabel pada data hasil integrasi
   b. Identifikasi seluruh target yang akan diperingkatkan
      (memperhatikan jumlah keluarga yang PADAN dari ketiga sumber utama)
   c. Tabulasi kondisi data hasil integrasi & penyiapan data pendukung

2. PROSES PEMERINGKATAN — 3 tahap utama
   a. Pemeringkatan ANTAR KELOMPOK sumber data
      Ukuran peringkat yang digunakan:
        • persentil REGSOSEK
        • status bantuan & SKOR DTKS
        • persentil P3KE
      → ketiganya digabung menggunakan BOBOT yang ditentukan berdasarkan data pendukung

   b. Ukuran pengurutan DALAM setiap kelompok (harus sebanding):
        • Regsosek → PREDIKSI pengeluaran per kapita
        • DTKS     → NILAI SKOR
        • P3KE     → IMPUTASI pengeluaran per kapita

   c. Peringkat kesejahteraan keluarga tingkat KABUPATEN/KOTA
      → dari peringkat gabungan (antar kelompok + urutan dalam kelompok)
      → lalu disusun ke level PROVINSI dan NASIONAL dengan memanfaatkan
        distribusi pengeluaran per kapita SUSENAS atau angka kemiskinan MAKRO

   d. PEMBENTUKAN DESIL → desil NASIONAL

3. EVALUASI PEMERINGKATAN
   a. Penghitungan Inclusion Error & Exclusion Error
      1) Memadankan data DTSEN dengan data SUSENAS
      2) Menentukan cut-off IE & EE (misalnya 40 persen) dan membagi data
      3) Menghitung IE & EE per kelompok data berdasarkan hasil prediksi vs nilai sebenarnya
   b. VALIDASI LAPANGAN (ground check) — verifikasi langsung untuk menangkap
      fenomena yang tidak dapat ditangkap oleh model
```

---

## 10. STRUKTUR IDENTITAS & KODE WILAYAH

### 10.1 Keluarga vs Rumah Tangga vs Individu

| Konsep | Definisi | Basis identitas | Dipakai di |
|---|---|---|---|
| **Individu** | Satu orang penduduk | **NIK** (16 digit, unik & tunggal) | DTSEN · Dukcapil · semua |
| **Keluarga** | Himpunan individu dalam satu **Kartu Keluarga** | **Nomor KK** (16 digit) | **DTSEN** · P3KE · BKKBN |
| **Rumah Tangga** | Seorang/sekelompok orang yang mendiami sebagian/seluruh bangunan fisik dan biasanya makan dari satu dapur | Nomor urut RT dalam blok sensus (**bukan** nomor nasional) | Susenas · DTKS/PPLS/PBDT |

> **KUNCI DESAIN:** DTSEN memakai unit **KELUARGA (berbasis Nomor KK)**, **bukan** rumah tangga. Perban 6/2025 Pasal 12 huruf c secara eksplisit mewajibkan *"validasi NIK **dan nomor kartu keluarga**"*.
> Karena beberapa keluarga bisa tinggal di satu rumah, DTSEN menyediakan `keluarga_dalam_rumah` = jumlah keluarga yang tinggal dalam satu rumah.
> **Konsekuensi:** konsep "rumah/bangunan fisik" **tidak punya primary key sendiri** di DTSEN. Jika NADI butuh entitas bangunan, harus dibuat sendiri (mis. hash dari `lokasi` geotagging + alamat ternormalisasi).

### 10.2 Pemadanan (Pasal 13)

```
Pemadanan mencakup 3 level:
  a. Pemadanan INDIVIDU              (kunci: NIK + nama)
  b. Pemadanan KELUARGA              (kunci: nomor KK)
  c. Pemadanan RELASI individu–keluarga

Hasil:
  • data PADAN
  • data TIDAK PADAN  →  berpotensi sebagai INDIVIDU BARU
```
DTSEN disusun dengan pemadanan berbasis **nama dan alamat — By-Name-By-Address (BNBA)**.

### 10.3 Kode wilayah — BPS (Wilkerstat) vs Kemendagri

| Level | Digit | Contoh struktur | Keterangan |
|---|---|---|---|
| Provinsi | **2** | `32` | — |
| Kabupaten/Kota | **4** | `32` + `73` = `3273` | 2 digit pertama = kode provinsi |
| Kecamatan | **6** | `3273` + `10` = `327310` | 4 digit pertama = kode kab/kota |
| Desa/Kelurahan | **10** | `327310` + `1001` = `3273101001` | 6 digit pertama = kode kecamatan |

**Aturan digit khusus (versi Kemendagri):**

| Aturan | Nilai |
|---|---|
| Digit 3–4 kabupaten/kota | **01–69 = Kabupaten** · **71–99 = Kota** |
| Digit pertama dari 4 digit desa | **1 = Kelurahan** · **2 = Desa** · **3 = Desa adat** |
| Format penulisan | "serangkaian angka dan titik" (mis. `32.73.10.1001`), tapi di database umumnya tanpa titik |

**Dua sistem kode yang berbeda dan HARUS di-bridging:**

| Sistem | Nama resmi | Pengelola | Dasar hukum terbaru |
|---|---|---|---|
| **BPS** | **Kode Wilayah Kerja Statistik (Wilkerstat)** | BPS | Diterbitkan BPS; punya level tambahan di bawah desa: **Blok Sensus** & **SLS (Satuan Lingkungan Setempat)** |
| **Kemendagri** | **Kode Wilayah Administrasi Pemerintahan** | Ditjen Bina Adwil Kemendagri | **Kepmendagri No. 300.2.2-2430 Tahun 2025** (23 Juni 2025), menggantikan **Kepmendagri No. 100.1.1-6117 Tahun 2022** |

**Portal bridging resmi BPS:** https://sig.bps.go.id/bridging-kode/index
Struktur tabel relasi: `kode_bps` · `nama_bps` · `kode_dagri` · `nama_dagri` — tersedia untuk level **provinsi, kab/kota, kecamatan** (level **desa hanya tersedia pada periode non-sensus**).

> **IMPLIKASI UNTUK NADI:** rancang tabel `ref_wilayah` dengan **dua kolom kode** (`kode_bps`, `kode_dagri`) + `berlaku_mulai`/`berlaku_sampai` (**SCD Type 2**), karena kode berubah setiap pemekaran/penggabungan wilayah. DTSEN sendiri memakai istilah *"kode provinsi **pada DTSEN**"* — artinya BPS menetapkan kode kanoniknya sendiri, kemungkinan besar **Wilkerstat**. Ini **harus dikonfirmasi ke BPS**.

### 10.4 Struktur NIK (16 digit)

| Posisi | Panjang | Isi |
|---|---|---|
| 1–2 | 2 | Kode provinsi |
| 3–4 | 2 | Kode kabupaten/kota |
| 5–6 | 2 | Kode kecamatan |
| 7–8 | 2 | **Tanggal lahir (+40 untuk perempuan)** |
| 9–10 | 2 | Bulan lahir |
| 11–12 | 2 | Tahun lahir (2 digit terakhir) |
| 13–16 | 4 | Nomor urut komputerisasi |

> ⚠️ Kode wilayah pada NIK adalah kode **tempat perekaman**, **BUKAN** domisili saat ini. DTSEN memisahkan ini secara eksplisit: variabel `alamat` individu didefinisikan sebagai *"alamat domisili **sesuai kondisi lapangan**"*.

---

## 11. USULAN SKEMA DATABASE UNTUK NADI

```sql
-- ============================ REFERENSI ============================
CREATE TABLE ref_wilayah (
  id                 BIGSERIAL PRIMARY KEY,
  level              SMALLINT NOT NULL,        -- 1=prov 2=kab/kota 3=kec 4=desa
  kode_bps           VARCHAR(10) NOT NULL,
  nama_bps           VARCHAR(100),
  kode_dagri         VARCHAR(13),
  nama_dagri         VARCHAR(100),
  parent_kode_bps    VARCHAR(10),
  tipe_desa          SMALLINT,                 -- 1=kelurahan 2=desa 3=desa adat
  berlaku_mulai      DATE NOT NULL,
  berlaku_sampai     DATE,
  UNIQUE (kode_bps, berlaku_mulai)
);

CREATE TABLE ref_kode_nilai (       -- lookup terpusat semua kode kategori
  variabel     VARCHAR(60)  NOT NULL,
  kode         SMALLINT     NOT NULL,
  label_id     VARCHAR(200) NOT NULL,
  label_en     VARCHAR(200),
  sumber       VARCHAR(120),        -- 'Susenas 2011' | 'Perban BPS 6/2025' | ...
  layak        BOOLEAN,             -- utk atap/dinding/lantai/air/sanitasi
  aktif        BOOLEAN DEFAULT TRUE,
  PRIMARY KEY (variabel, kode)
);

-- ============================ ENTITAS INTI ============================
CREATE TABLE keluarga (
  nomor_kartu_keluarga        CHAR(16) PRIMARY KEY,
  nama_kepala_keluarga        VARCHAR(255),
  nik_kepala_keluarga         CHAR(16),
  -- wilayah (var. keluarga #1-#8)
  kode_provinsi               CHAR(2),
  kode_kabupaten_kota         CHAR(4),
  kode_kecamatan              CHAR(6),
  kode_kelurahan_desa         CHAR(10),
  alamat                      TEXT,             -- #9
  latitude                    DECIMAL(10,7),    -- #10 lokasi
  longitude                   DECIMAL(10,7),
  -- perumahan (var. keluarga #13-#25)
  keluarga_dalam_rumah        SMALLINT,
  status_kepemilikan_rumah    SMALLINT,
  jenis_lantai_terluas        SMALLINT,
  jenis_dinding_terluas       SMALLINT,
  jenis_atap_terluas          SMALLINT,
  sumber_air_minum_utama      SMALLINT,
  sumber_penerangan_utama     SMALLINT,
  daya_terpasang              SMALLINT,
  id_meteran_pln              VARCHAR(20),
  bahan_bakar_utama_memasak   SMALLINT,
  fasilitas_bab               SMALLINT,
  jenis_kloset                SMALLINT,
  pembuangan_akhir_tinja      SMALLINT,
  -- PENGAYAAN (tidak wajib DTSEN, tapi ada di Regsosek/Susenas)
  luas_lantai_m2              DECIMAL(8,2),
  jarak_penampungan_limbah    SMALLINT,   -- wajib utk kaidah air minum layak
  sumber_air_mandi_cuci       SMALLINT,   -- wajib utk kaidah air minum layak (kode 1&2)
  status_lahan_bangunan       SMALLINT,
  konsumsi_listrik_kwh        DECIMAL(10,2),
  -- indikator turunan (materialized)
  air_minum_layak             BOOLEAN,
  sanitasi_layak              BOOLEAN,
  ketahanan_bangunan_layak    BOOLEAN,
  rumah_layak_huni            BOOLEAN,
  luas_lantai_per_kapita      DECIMAL(8,2),
  -- pemeringkatan
  desil                       SMALLINT CHECK (desil BETWEEN 1 AND 10),
  peringkat_nasional          BIGINT,
  peringkat_provinsi          BIGINT,
  peringkat_kabkota           BIGINT,
  prediksi_pengeluaran_kapita DECIMAL(14,2),
  -- metadata & lineage
  snapshot_versi              VARCHAR(20),  -- 'DTSEN-2026-TW3'
  sumber_asal                 VARCHAR(20),  -- 'REGSOSEK'|'DTKS'|'P3KE'|'BARU'
  status_padan_dukcapil       SMALLINT,     -- 1=padan 2=tidak padan 3=belum dicek
  updated_at                  TIMESTAMPTZ
);

CREATE TABLE keluarga_aset (          -- semua COUNT, bukan boolean (lihat §5.2)
  nomor_kartu_keluarga    CHAR(16) PRIMARY KEY REFERENCES keluarga,
  tabung_gas              SMALLINT      DEFAULT 0,  -- min 5,5 kg
  lemari_es               SMALLINT      DEFAULT 0,
  ac                      SMALLINT      DEFAULT 0,
  pemanas_air             SMALLINT      DEFAULT 0,
  telepon_rumah           SMALLINT      DEFAULT 0,  -- PSTN
  tv_datar                SMALLINT      DEFAULT 0,  -- min 30 inch
  emas_perhiasan_gram     DECIMAL(10,2) DEFAULT 0,
  komputer_laptop_tablet  SMALLINT      DEFAULT 0,
  sepeda_motor            SMALLINT      DEFAULT 0,
  sepeda                  SMALLINT      DEFAULT 0,
  mobil                   SMALLINT      DEFAULT 0,
  perahu                  SMALLINT      DEFAULT 0,
  kapal_perahu_motor      SMALLINT      DEFAULT 0,
  smartphone              SMALLINT      DEFAULT 0,
  sawah_kebun_ha          DECIMAL(10,4) DEFAULT 0,
  lahan_lainnya           BOOLEAN       DEFAULT FALSE,
  rumah_lainnya           BOOLEAN       DEFAULT FALSE,
  ternak_besar            SMALLINT      DEFAULT 0,  -- sapi, kerbau, kuda
  ternak_kecil            SMALLINT      DEFAULT 0   -- kambing, domba, babi
);

CREATE TABLE individu (
  nomor_induk_kependudukan  CHAR(16) PRIMARY KEY,
  nomor_kartu_keluarga      CHAR(16) REFERENCES keluarga,
  nama                      VARCHAR(255),
  tanggal_lahir             DATE,
  usia                      SMALLINT,
  jenis_kelamin             SMALLINT,           -- 1=L 2=P
  alamat_domisili           TEXT,               -- sesuai kondisi lapangan
  status_hubungan_keluarga  SMALLINT,
  status_kawin              SMALLINT,
  partisipasi_sekolah       SMALLINT,
  ijazah_tertinggi          SMALLINT,
  status_pekerjaan          SMALLINT,
  lapangan_usaha            SMALLINT,
  jumlah_usaha              SMALLINT DEFAULT 0,
  penyandang_disabilitas    BOOLEAN,
  jenis_disabilitas_uu8     SMALLINT,           -- 1..5 (UU 8/2016)
  penyakit_kronis           BOOLEAN,
  -- PENGAYAAN (Regsosek Blok IV.A & IV.E)
  ibu_hamil                 BOOLEAN,
  status_gizi_balita        SMALLINT,
  punya_akta_lahir          BOOLEAN,
  -- lineage
  status_padan_dukcapil     SMALLINT,
  sumber_asal               VARCHAR(20),
  updated_at                TIMESTAMPTZ
);

CREATE TABLE individu_disabilitas_wgss (   -- Washington Group Short Set
  nomor_induk_kependudukan  CHAR(16) REFERENCES individu,
  domain                    SMALLINT,   -- 1..6 (lihat Tabel 6.6)
  tingkat_kesulitan         SMALLINT,   -- 1..4
  PRIMARY KEY (nomor_induk_kependudukan, domain)
);

CREATE TABLE individu_usaha (
  id                        BIGSERIAL PRIMARY KEY,
  nomor_induk_kependudukan  CHAR(16) REFERENCES individu,
  lapangan_usaha            SMALLINT
);

CREATE TABLE kepesertaan_program (
  id                       BIGSERIAL PRIMARY KEY,
  kode_program             VARCHAR(20),   -- 'PKH','SEMBAKO','PBI_JKN','PIP',...
  nomor_induk_kependudukan CHAR(16),      -- diisi untuk program berbasis individu
  nomor_kartu_keluarga     CHAR(16),      -- diisi untuk program berbasis keluarga
  status                   SMALLINT,      -- 1=aktif 2=nonaktif 3=graduasi
  periode_mulai            DATE,
  periode_selesai          DATE,
  nominal                  DECIMAL(14,2),
  sumber_data              VARCHAR(40),
  CHECK (nomor_induk_kependudukan IS NOT NULL OR nomor_kartu_keluarga IS NOT NULL)
);

-- ============================ TATA KELOLA ============================
CREATE TABLE dtsen_snapshot (       -- audit versi (Perban 6/2025 Pasal 16)
  id              BIGSERIAL PRIMARY KEY,
  versi           VARCHAR(20) UNIQUE,   -- 'v1','v2','v3'
  tanggal_kondisi DATE,
  jumlah_individu BIGINT,
  jumlah_keluarga BIGINT,
  catatan         TEXT
);

CREATE TABLE usul_sanggah (         -- alur pemutakhiran mandiri
  id                       BIGSERIAL PRIMARY KEY,
  jenis                    SMALLINT,    -- 1=usul baru 2=sanggah 3=perbaikan atribut
  kanal                    VARCHAR(20), -- 'CEK_BANSOS'|'CEK_DTSEN'|'SIKS_NG'|'DESA'
  nomor_induk_kependudukan CHAR(16),
  nomor_kartu_keluarga     CHAR(16),
  payload                  JSONB,       -- variabel yang diusulkan berubah
  lampiran                 JSONB,       -- foto rumah, KTP, KK, SKTM
  status                   SMALLINT,    -- 1=diajukan 2=verval desa 3=verval dinsos
                                        -- 4=diteruskan BPS 5=diterima 6=ditolak
  diajukan_pada            TIMESTAMPTZ,
  diproses_pada            TIMESTAMPTZ,
  snapshot_target          VARCHAR(20)  -- snapshot mana yang akan memuat perubahan
);

CREATE TABLE audit_log (            -- Perban 6/2025 Pasal 28 ayat 8 (kenirsangkalan)
  id           BIGSERIAL PRIMARY KEY,
  actor_id     VARCHAR(64),
  actor_role   VARCHAR(40),
  aksi         VARCHAR(40),         -- READ|CREATE|UPDATE|DELETE|EXPORT
  entitas      VARCHAR(40),
  entitas_id   VARCHAR(32),
  ip_address   INET,
  payload_hash CHAR(64),
  waktu        TIMESTAMPTZ DEFAULT now()
);
```

### Tabel 11.1 — Aturan bisnis WAJIB (turunan langsung regulasi)

| # | Aturan | Dasar hukum |
|---|---|---|
| 1 | Setiap record wajib punya **NIK + nama** — jika tidak, **tolak** | Perban 6/2025 Pasal 10 ayat 4 huruf a |
| 2 | NIK & Nomor KK **tidak valid di Dukcapil → TIDAK masuk DTSEN**, dikembalikan ke penyedia | Perban 6/2025 Pasal 15 ayat 3 |
| 3 | Data perorangan harus **individual & tunggal**; anggota keluarga **tidak boleh tumpang tindih** antar KK | Permensos 3/2021 Pasal 8 ayat 3 huruf a & d |
| 4 | Pemeringkatan **hanya** dilakukan pada hasil **Snapshot** yang sudah tervalidasi NIK & KK | Perban 6/2025 Pasal 17 ayat 2 |
| 5 | Desil = **desil NASIONAL** (bukan desil provinsi/kabupaten) | Rancangan Perban, Lampiran BAB II.D.2.d |
| 6 | Setiap penyerahan data ke pihak lain wajib disertai **BAST + Perjanjian Kerahasiaan** | Perban 6/2025 Pasal 23–24 |
| 7 | Data pribadi tunduk pada **UU No. 27 Tahun 2022 (PDP)** | Perban 6/2025 Pasal 33 |
| 8 | Wajib **log/pencatatan lengkap** setiap akses & aktivitas (kenirsangkalan, penelusuran insiden, audit) | Perban 6/2025 Pasal 28 ayat 8 |
| 9 | Kendali keamanan minimal: kriptografi · sertifikat elektronik · **RBAC** · logging & monitoring · backup/replikasi/redundansi | Perban 6/2025 Pasal 29 ayat 2 |
| 10 | Aplikasi pengumpulan data wajib punya **aturan validasi built-in** + pedoman konsep-definisi + pelatihan petugas | Rancangan Perban, Lampiran BAB V.A.3 |
| 11 | Penerima kategori "pemanfaat" wajib melakukan **sinkronisasi periodik balik ke BPS**; penerima kategori "pengguna akhir" **dilarang** membagipakaikan data | Lampiran Perban 6/2025 huruf B & C |
| 12 | Wajib **deduplikasi & validasi otomatis** sebelum data masuk sistem utama | Rancangan Perban, BAB V.A.1.a.1)c) |

### 11.2 Dimensi kualitas statistik & Quality Gates

Rancangan Perban mewajibkan **Quality Gates (QG)** — *"titik pengambilan keputusan (checkpoint) dalam penyelenggaraan statistik untuk menentukan kelayakan suatu proses berlanjut ke tahapan berikutnya."*

**9 dimensi kualitas statistik:**

| # | Dimensi | Makna |
|---|---|---|
| 1 | Kerahasiaan dan keamanan | Perlindungan informasi pribadi dari akses/penggunaan/pengungkapan tidak sah |
| 2 | Keandalan metodologi dan prosedur | Metodologi & prosedur statistik yang tepat dan andal sesuai standar ilmiah |
| 3 | Efektivitas dan efisiensi sumber daya | Kecukupan anggaran, SDM, sarana-prasarana |
| 4 | Relevansi | Kemampuan keluaran memenuhi kebutuhan pengguna (cakupan & konten) |
| 5 | Akurasi | Kedekatan statistik dengan kenyataan/populasi |
| 6 | Aktualitas dan ketepatan waktu | Penyajian aktual & tepat jadwal |
| 7 | Koherensi dan keterbandingan | Dapat digabungkan konsisten & dibandingkan antarwaktu/antarwilayah |
| 8 | Aksesibilitas | Kemudahan akses + metadata memadai |
| 9 | Interpretabilitas | Kejelasan penyajian sehingga mudah ditafsirkan |

**Komponen QG:** (1) penempatan QG berdasarkan penilaian risiko · (2) penentuan ukuran kualitas · (3) penentuan peran · (4) penentuan toleransi (ambang batas kualitas yang dapat diterima) · (5) penentuan aksi preventif & korektif · (6) *(komponen ke-6 terpotong di PDF sumber)*.

**Penjaminan kualitas pada Pemutakhiran Data (rancangan Perban BAB V.A.3):**
a. pemeriksaan pemenuhan variabel kesejahteraan sesuai ketentuan BPS dalam kuesioner · b. **penerapan aturan validasi data pada aplikasi/sistem pengumpulan data** · c. ketersediaan pedoman pengumpulan data (konsep & definisi + mekanisme) · d. pelatihan petugas lapangan · e. pengumpulan sesuai prosedur · f. **pengecekan kelengkapan data, duplikasi data, data tidak wajar, konsistensi data** · g. ketersediaan metadata · h. penerapan standar data DTSEN · i. penerapan format data sesuai kebutuhan DTSEN.

---

## 12. DAFTAR SUMBER (URL)

### 12.1 Sumber PRIMER — berhasil diekstrak PENUH

| Dokumen | URL | Status |
|---|---|---|
| **Peraturan BPS No. 6 Tahun 2025 tentang DTSEN** (PDF lengkap, 68 KB teks) | https://peraturan.go.id/files/peraturan-bps-no-6-tahun-2025.pdf | ✅ Penuh |
| Halaman detail Perban BPS 6/2025 | https://peraturan.go.id/id/peraturan-bps-no-6-tahun-2025 | ✅ |
| **RANCANGAN Peraturan BPS tentang DTSEN** — ⭐ **memuat DAFTAR VARIABEL & metodologi pemeringkatan** (103 KB teks) | https://jdih.bps.go.id/public/pembentukan-puu/download/eyJpdiI6IkxpVldtUWRWeHJmR29HYkdxSW04ZFE9PSIsInZhbHVlIjoiL0FXWjBCeDNKNys1bTllTEd4am1nZz09IiwibWFjIjoiMjM3NmNjM2ViNzBhOTZhOWIxNzExMTA5NTg1ZDFiNDk3NDQ2YzM4MTA5MWVlZjk1NGNjMTVlMjJmNmM3NTRiYSIsInRhZyI6IiJ9 | ✅ Penuh |
| **Permensos No. 3 Tahun 2021 tentang Pengelolaan DTKS** (PDF, BN 2021/578) | https://peraturan.go.id/files/bn578-2021.pdf | ✅ Penuh |
| Halaman detail Permensos 3/2021 | https://peraturan.go.id/id/permensos-no-3-tahun-2021 | ✅ |
| Daftar Peraturan BPS 2025 | https://www.peraturan.go.id/perlpnk?pemrakarsa=16&tahun=2025 | ✅ |
| IHSN — Susenas Maret 2011, datafile Core Household (`susenas11mar_kr`) | https://catalog.ihsn.org/catalog/3037/data-dictionary/F11?file_name=susenas11mar_kr | ✅ |
| IHSN — Susenas Maret 2011, datafile Household Member (`susenas11mar_ki`) | https://catalog.ihsn.org/catalog/3037/data-dictionary/F10?file_name=susenas11mar_ki | ✅ |
| IHSN — katalog induk Susenas 2011 | https://catalog.ihsn.org/index.php/catalog/3037 | ✅ |
| BPS SIG — Portal bridging kode BPS ↔ Kemendagri | https://sig.bps.go.id/bridging-kode/index | ✅ |
| BPS SIRuSa — metadata variabel "Jenis Disabilitas" | https://sirusa.web.bps.go.id/metadata/variabel/73550 | ✅ |
| BPS SIRuSa — daftar metadata variabel statistik | https://sirusa.bps.go.id/metadata/variabel | ✅ |
| World Bank Microdata — SUSETI BPS 2008 (contoh penamaan variabel aset/perumahan) | https://microdata.worldbank.org/index.php/catalog/1832/data-dictionary | ✅ |

**Halaman variabel IHSN yang diambil satu per satu (untuk kode kategori):**
`b6r3` V561 · `b6r5` V563 · `b6r6` V564 · `b6r7` V565 · `b6r9a` V567 · `b6r13a` V573 · `b6r13b` V574 · `b6r13c` V575 · `b6r14a` V576 · `b6r14b` V577 · `b6r15` V578 · `hb` V423 · `kwn` V426 · `b5r14` V488 · `b5r17` V491 · `b5r30` V519
Pola URL: `https://catalog.ihsn.org/catalog/3037/variable/F11/V563?name=b6r5`

### 12.2 Sumber PRIMER akademik/teknis

| Dokumen | URL | Status |
|---|---|---|
| **Taufiq N. & Mariyah S. (2021)** — *Pendekatan Model Machine Learning dalam Pemeringkatan Status Sosial Ekonomi Rumah Tangga di Indonesia*, Seminar Nasional Official Statistics 2021 (BPS RI + Politeknik Statistika STIS). ⭐ **Berisi Tabel 1: variabel penjelas PMT** | https://prosiding.stis.ac.id/index.php/semnasoffstat/article/download/1018/328/ | ✅ Penuh |
| **SMERU (2022)** — *Mendorong Pemutakhiran Berkelanjutan terhadap Data Terpadu Kesejahteraan Sosial* — alur verval SIKS-NG, "44 indikator", regulasi DTKS | https://smeru.or.id/id/file/3891/download?token=wk_MwoCK | ✅ Penuh |
| **Kementerian PUPR / HREIS** — *Metadata Indikator Perumahan* — definisi & kaidah kelayakan atap/dinding/lantai/air minum/sanitasi/rumah layak huni | https://hreis.pu.go.id/_lib/file/doc/Metadata/Metadata%20Indikator%20Perumahan(2).pdf | ✅ Penuh |
| **SMERU** — *Penetapan Kriteria dan Variabel Pendataan Penduduk Miskin* (23 indikator BKKBN, PSE05, PPLS08) | https://smeru.or.id/sites/default/files/publication/cbms_criteria_ind.pdf | ✅ Terekstrak |
| MIT — *Using Administrative Data to Improve Social Protection in Indonesia* (PPLS11 → 25 juta RT) | https://admindatahandbook.mit.edu/book/latest/indonesia.html | Referensi |
| TNP2K — *Indonesia's Unified Database for Social Protection Programmes* | https://www.tnp2k.go.id/images/uploads/downloads/Book%20%20Indonesias%20Unified%20Database%20for%20Social%20Protection%20Programmes%20Final.pdf | ❌ ECONNREFUSED |

### 12.3 Sumber SEKUNDER (berita/rilis — untuk angka & konteks terkini)

| Dokumen | URL |
|---|---|
| **BPS** — *DTSEN Jadi Rujukan Bersama, BPS Jelaskan Arti Desil* (22 Ags 2026) | https://www.bps.go.id/en/news/2026/08/22/938/dtsen-jadi-rujukan-bersama--bps-jelaskan-arti-desil.html |
| CNBC Indonesia — liputan rilis BPS di atas (**290,13 jt individu / 95,98 jt keluarga; update tiap 3 bulan**) | https://www.cnbcindonesia.com/news/20260823101026-4-761576/dtsen-jadi-rujukan-bersama-bps-jelaskan-arti-desil |
| CNN Indonesia — *BPS Jelaskan Arti Desil dalam DTSEN: Bukan Penentu Mutlak Kemiskinan* | https://www.cnnindonesia.com/ekonomi/20260822131626-532-1395277/bps-jelaskan-arti-desil-dalam-dtsen-bukan-penentu-mutlak-kemiskinan |
| Kompas — *Siapa yang Menentukan Desil? Begini Penjelasan BPS* | https://money.kompas.com/read/2026/08/19/132546926/siapa-yang-menentukan-desil-begini-penjelasan-bps |
| **Ombudsman RI** — *Luruskan Informasi Keliru soal Penentu Desil DTSEN, Bukan Desa atau Dinas Sosial* | https://ombudsman.go.id/perwakilan/news/r/pwkmedia--ombudsman-babel-luruskan-informasi-keliru-soal-penentu-desil-dtsen-bukan-desa-atau-dinas-sosial |
| ANTARA — *Kemensos dan BPS siap luncurkan DTSEN versi 3* | https://www.antaranews.com/berita/5640885/kemensos-dan-bps-siap-luncurkan-dtsen-versi-3 |
| Kemensos — *Inpres DTSEN Sudah Ditandatangani Presiden* | https://kemensos.go.id/berita-terkini/menteri-sosial/Inpres-DTSEN-Sudah-Ditandatangani-Presiden,-Kemensos-Akan-Lakukan-Uji-Petik-dan-Pendalaman-Data |
| Cek Bansos Kemensos | https://cekbansos.kemensos.go.id/ |
| Inpres No. 4/2025 di JDIH Kemensos | https://jdih.kemensos.go.id/detail/instruksi-presiden-republik-indonesia-nomor-4-tahun-2025-ten-XAK410qR3x |
| Inpres No. 4/2025 di JDIH BPK | https://peraturan.bpk.go.id/Details/314649/inpres-no-4-tahun-2025 |
| BPS Jatim — Regsosek 2022 untuk Satu Data Program Perlindungan Sosial | https://jatim.bps.go.id/en/news/2022/10/10/192/pendataan-awal-registrasi-sosial-ekonomi--regsosek--2022-untuk-satu-data-program-perlindungan-sosial.html |
| Kominfo — Pendataan Awal Registrasi Sosial Ekonomi Dimulai | https://www.kominfo.go.id/content/detail/45002/pendataan-awal-registrasi-sosial-ekonomi-dimulai/0/artikel_gpr |
| Kemenko Perekonomian — Pemerintah Gunakan Basis Data Regsosek | https://www.ekon.go.id/publikasi/detail/5443/pemerintah-gunakan-basis-data-regsosek-untuk-penyaluran-program-pemerintah-yang-lebih-tepat-sasaran |
| UNICEF Indonesia — Integrated socio-economic registration system for Indonesia | https://www.unicef.org/indonesia/reports/integrated-socio-economic-registration-system-indonesia |
| Dinsos Jatim — *DTKS Dihapus Ganti DTSEN, Implementasi Inpres No. 4 Tahun 2025* | https://dinsos.jatimprov.go.id/detail-berita-publik/dtks-dihapus-ganti-dtsen-data-tunggal-sosial-ekonomi-nasional-implementasi-inpres-no-4-tahun-2025 |
| Portal Satu Data — Dataset P3KE | https://katalog.data.go.id/dataset/data-p3ke |
| GitHub `cahyadsn/wilayah` — struktur kode Kepmendagri 300.2.2-2430/2025 | https://github.com/cahyadsn/wilayah |
| GitHub `zakiego/...` — relasi kode BPS ↔ Kemendagri | https://github.com/zakiego/Kode-Wilayah-Administrasi-Indonesia-Relasi-BPS-Kemendagri |
| Kemendagri Ditjen Bina Adwil — pemutakhiran kode wilayah | https://ditjenbinaadwil.kemendagri.go.id/berita/detail/kemendagri-mutakhirkan--kode-data-wilayah-administrasi-pemerintahan--dan-pulau-di-seluruh-indonesia |

---

## 13. ⚠️ YANG TIDAK BERHASIL DITEMUKAN (dilaporkan jujur — jangan diarang)

| # | Yang dicari | Penyebab kegagalan | Dampak & mitigasi |
|---|---|---|---|
| 1 | **Kuesioner Regsosek 2022 lengkap (REGSOSEK22-K) dengan nomor rincian & kode jawaban verbatim** | `sepakat.bappenas.go.id` di belakang Cloudflare: WebFetch 403; curl gagal TLS handshake (`SEC_E_ILLEGAL_MESSAGE`, exit 35) di semua kombinasi TLS. Mirror Scribd/Studocu/PDFCoffee/Slideshare semuanya paywall/Cloudflare/sertifikat kedaluwarsa | **Kode kategori di Bagian 4 & 6 memakai standar Susenas (IHSN) sebagai proxy — WAJIB diverifikasi.** Struktur blok I–V berhasil dikonfirmasi dari beberapa sumber independen |
| 2 | **Buku 1/2/3 Pedoman Regsosek 2022** (konsep-definisi resmi + skip pattern) | Sama seperti #1 | Definisi operasional diambil dari metadata HREIS/PUPR yang mengacu konsep Susenas BPS |
| 3 | **Daftar lengkap "44 indikator kemiskinan" DTKS** | Tidak dipublikasikan sebagai lampiran Permensos 3/2021; hanya angkanya yang disebut di studi SMERU | **Tidak bisa direkonstruksi.** Perlu permintaan resmi ke Pusdatin Kesos Kemensos |
| 4 | **Teks lengkap Inpres No. 4 Tahun 2025** (seluruh diktum + daftar pejabat yang diinstruksikan) | `peraturan.bpk.go.id` → 403; `jdih.kemensos.go.id` tidak terjangkau | Hanya ringkasan dari sumber sekunder. Isi pokoknya terkonfirmasi dari daftar "Mengingat" di Lampiran Perban 6/2025 |
| 5 | **Bagan 1 "Alur Pemrosesan DTSEN"** (Lampiran A Perban 6/2025) | Berupa gambar/diagram di PDF; tidak ada layer teks | Alur direkonstruksi dari **Pasal 12–17** yang isinya setara |
| 6 | **Kode numerik RESMI variabel DTSEN** (mis. `jenis_lantai_terluas` = kode berapa untuk "keramik") | Perban & rancangannya hanya memuat **nama variabel + keterangan**, tidak ada tabel kode | **Ini gap paling kritis.** Wajib minta spesifikasi standar data DTSEN ke BPS |
| 7 | **Kode `status_pekerjaan`** dari katalog resmi | Variabel tidak terekspos di data dictionary IHSN yang diakses | Tabel 6.5 dari standar BPS umum — **ditandai LOW CONFIDENCE** |
| 8 | **Buku TNP2K "Indonesia's Unified Database"** (variabel PPLS 2011 lengkap) | `tnp2k.go.id` menolak koneksi (ECONNREFUSED 150.107.142.248:443) | Variabel PPLS/BDT direkonstruksi dari paper STIS + katalog IHSN |
| 9 | **Kamus data / DDI resmi P3KE** | `katalog.data.go.id` tidak resolve DNS; `tnp2k.go.id` down | Hanya deskripsi umum (bersumber dari Pendataan Keluarga BKKBN 2021; variabel pemeringkatan: status wilayah, jumlah ART, jumlah ART kuadrat, jenis kelamin, umur, tingkat pendidikan) |
| 10 | **Besaran bantuan PKH 2026 dari sumber resmi Kemensos** | Hanya ditemukan di media/blog | Tabel 8.3 **ditandai LOW CONFIDENCE** |
| 11 | **Distribusi jumlah keluarga per desil DTSEN** | Tidak dipublikasikan BPS secara terbuka | — |
| 12 | **Kode NUMERIK kategori Susenas versi 2019+** (bukan sekadar nama kategori) | Kuesioner VSEN24.K hanya via SiLASTIK BPS berbayar (perlu SPPD + PNBP); arsip RAND 403 | Kolom "Kategori Susenas 2019+" hanya berisi **nama** kategori, **tanpa nomor kode** |
| 13 | **Lampiran BAST yang merinci "jumlah record, variabel, dan metadata"** DTSEN yang diserahterimakan | Format BAST menyebut ada Lampiran, tapi isinya kosong/template di PDF | Bisa jadi dokumen inilah yang memuat kamus data DTSEN operasional — minta ke BPS |

---

## 14. LANGKAH VERIFIKASI YANG DIREKOMENDASIKAN

| # | Langkah | Target |
|---|---|---|
| 1 | **Ajukan permintaan resmi spesifikasi variabel & kode standar DTSEN ke BPS** (Direktorat Sistem Informasi Statistik / Pusdatin BPS). Perban 6/2025 Pasal 10 ayat 4 huruf b mewajibkan *"variabel berstandar data yang sama dengan variabel DTSEN"* — standar itu **pasti ada** dalam bentuk dokumen | Kode numerik kanonik semua variabel |
| 2 | **Ambil kuesioner + pedoman Regsosek 2022** langsung dari BPS kab/kota atau portal SEPAKAT Bappenas dengan akun terdaftar | Verifikasi kode kategori Bagian 4 & 6 |
| 3 | **Unduh dataset bridging kode wilayah** dari https://sig.bps.go.id/bridging-kode/index | Seed tabel `ref_wilayah` |
| 4 | **Ambil Kepmendagri No. 300.2.2-2430 Tahun 2025** beserta lampirannya | Daftar kode wilayah administrasi terbaru + tipe desa |
| 5 | **Konfirmasi ke Pusdatin Kesos Kemensos**: daftar "44 indikator" & spesifikasi payload/API SIKS-NG | Jika NADI perlu integrasi DTKS/usul-sanggah |
| 6 | **Beli/ajukan mikrodata Susenas KOR terbaru** via SiLASTIK BPS (https://silastik.bps.go.id) | Kode kategori Susenas 2019+ dengan nomor |
| 7 | **Konfirmasi apakah `kode_provinsi` "pada DTSEN"** = kode BPS Wilkerstat atau kode Kemendagri | Menentukan kolom kode kanonik `ref_wilayah` |
| 8 | **Konfirmasi keberadaan variabel `konsumsi_listrik_kwh`** dan `luas_lantai` di DTSEN operasional | BPS menyebut "daya **dan konsumsi** listrik" sebagai indikator PMT |
