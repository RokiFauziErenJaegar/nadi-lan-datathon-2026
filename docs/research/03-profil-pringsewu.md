# Profil Statistik & Geografi Kabupaten Pringsewu, Provinsi Lampung

> **Dokumen riset untuk proyek NADI (LAN Datathon)**
> Disusun: 25 Agustus 2026 · Kode wilayah: **18.10** · Ibu kota: **Pringsewu**
> Sumber utama: BPS Kabupaten Pringsewu, Kepmendagri No. 300.2.2‑2138/2025, Badan Informasi Geospasial (BIG)

## Legenda status verifikasi

| Tanda | Arti |
|---|---|
| ✅ **VERIFIED** | Diambil langsung dari dokumen/API resmi (BPS, Kemendagri, BIG) dan lolos uji silang (jumlah kolom/baris cocok) |
| 🔢 **DERIVED** | Dihitung sendiri dari angka VERIFIED (rumus ditulis eksplisit) |
| ⚠️ **UNVERIFIED** | Berasal dari media/sekunder, atau hasil rekonstruksi tabel PDF yang tidak bisa diuji silang |
| ❌ **NOT FOUND** | Tidak ditemukan sumber yang dapat dipertanggungjawabkan — **jangan diisi dengan tebakan** |

### Catatan metodologi

PDF publikasi BPS diberi *watermark* teks berulang (`https://pringsewukab.bps.go.id`) yang menyisip ke dalam
aliran teks dan menggeser kolom saat diekstrak. Semua tabel di bawah direkonstruksi kolom‑per‑kolom, lalu
**diuji silang** dengan cara berikut sebelum diberi tanda ✅:

1. Jumlah baris kolom harus sama dengan jumlah kecamatan/tahun.
2. Total baris terakhir harus sama dengan penjumlahan komponen.
3. Rasio turunan (kepadatan = penduduk ÷ luas, persentase = bagian ÷ total) harus mereproduksi angka yang tercetak.

Contoh: peta penduduk per kecamatan dikonfirmasi **dua kali** — lewat kepadatan (Tabel 3.1.1) *dan* lewat
Tabel 4.3.1 (agama), di mana penjumlahan 6 kolom agama untuk setiap kecamatan tepat sama dengan angka penduduknya.
Kolom yang gagal uji silang ditandai ⚠️ dan alasannya ditulis.

---

## 1. Struktur administrasi — 9 kecamatan, 126 pekon, 5 kelurahan

### 1.1 Temuan penting: jumlah pekon adalah **126**, bukan 128

Wikipedia (dan banyak situs turunannya) menyebut *"128 pekon"*, dengan Ambarawa 9 pekon dan Adiluwih 14 pekon.
**Angka itu kedaluwarsa.** Tiga sumber independen sepakat pada **126 pekon + 5 kelurahan = 131 desa/kelurahan**:

| Sumber | Total | Ambarawa | Adiluwih | Status |
|---|---|---|---|---|
| Kepmendagri No. 300.2.2‑2138/2025 (dataset `cahyadsn/wilayah`) | 131 | 8 | 13 | ✅ |
| BPS, *Pringsewu Dalam Angka 2025*, Tabel 2.1.1 (kolom 2024) | 131 | 8 | 13 | ✅ |
| BIG, layer batas desa 1:10K (query `WADMKK='Pringsewu'`) | 131 | 8 | 13 | ✅ |
| Wikipedia id | 133 (128+5) | 9 | 14 | ❌ kedaluwarsa |

**Uji silang penentu:** Tabel 2.1.2 (Indeks Desa Membangun 2024) memuat 15 Desa Berkembang + 75 Desa Maju
+ 36 Desa Mandiri = **126**. IDM hanya menilai *desa/pekon* (kelurahan dikecualikan), dan rinciannya per
kecamatan persis sama dengan jumlah pekon di atas — termasuk Kec. Pringsewu yang muncul sebagai 10
(1+4+5), yaitu 15 desa/kelurahan dikurangi 5 kelurahan. ✅

### 1.2 Rekapitulasi per kecamatan

Semua kolom di tabel ini ✅ VERIFIED kecuali yang ditandai.

| Kode | Kecamatan | Ibu kota | Pekon | Kel. | Total | Luas (km²) | % luas | Penduduk 2024 | Kepadatan (/km²) | Rasio JK | Lat (centroid) | Lon (centroid) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 18.10.01 | Pringsewu | Pringsewu | 10 | 5 | 15 | 45,28 | 7,34 | 88.758 | 1.960 | 103,30 ⚠️ | -5,35643 | 104,96524 |
| 18.10.02 | Gading Rejo | Gading Rejo | 23 | – | 23 | 67,79 | 10,98 | 85.447 | 1.260 | 104,90 ⚠️ | -5,36943 | 105,02848 |
| 18.10.03 | Ambarawa | Ambarawa | 8 | – | 8 | 33,11 | 5,36 | 40.517 | 1.224 | 106,10 ⚠️ | -5,41087 | 104,95014 |
| 18.10.04 | Pardasuka | Pardasuka | 13 | – | 13 | 87,31 | 14,15 | 38.594 | 442 | 106,20 ⚠️ | -5,50645 | 104,92690 |
| 18.10.05 | Pagelaran | Pagelaran | 22 | – | 22 | 48,42 | 7,85 | 56.839 | 1.174 | 105,40 ⚠️ | -5,37236 | 104,90441 |
| 18.10.06 | Banyumas | Banyumas | 11 | – | 11 | 42,71 | 6,92 | 23.610 | 553 | 103,00 ⚠️ | -5,29113 | 104,91433 |
| 18.10.07 | Adiluwih | Adi Luwih | 13 | – | 13 | 68,80 | 11,15 | 39.457 | 574 | 105,50 ⚠️ | -5,24862 | 105,01708 |
| 18.10.08 | Sukoharjo | Sukoharjo | 16 | – | 16 | 65,59 | 10,63 | 54.760 | 835 | 104,00 ⚠️ | -5,30244 | 104,98688 |
| 18.10.09 | Pagelaran Utara | Fajar Mulia | 10 | – | 10 | 158,19 | 25,63 | 16.852 | 107 | 109,00 ⚠️ | -5,25807 | 104,83917 |
| **18.10** | **Kab. Pringsewu** | Pringsewu | **126** | **5** | **131** | **617,19** | 100,00 | **444.834** | **721** | 104,80 | **-5,33636** | **104,93341** |

**Catatan kolom:**

- **Luas** — BPS *Pringsewu Dalam Angka 2025* Tabel 1.1.1 (angka sementara), bersumber pada **Perda Kab. Pringsewu No. 1/2023** dan Kepmendagri No. 100.1.1‑6117/2022. Uji silang: Σ = 617,20 vs total tercetak 617,19 (selisih pembulatan) ✅. **Luas resmi terkini adalah 617,19 km², bukan 625 km²** — angka 625 km² yang beredar luas (Wikipedia) sudah usang.
- **Penduduk 2024** — Tabel 3.1.1, sumber **Data Konsolidasi Bersih (DKB) Semester II 2024 Kemendagri** via Disdukcapil Pringsewu. Σ = 444.834 ✅. Diverifikasi ulang lewat Tabel 4.3.1 (agama) ✅.
- **Kepadatan** — angka tercetak BPS; direproduksi 🔢 dari penduduk ÷ luas untuk semua 9 kecamatan (mis. 88.758 ÷ 45,28 = 1.960) ✅.
- **Rasio jenis kelamin** ⚠️ — nilai kolomnya pasti benar sebagai himpunan (106,20 / 106,10 / 105,40 / 109,00 / 103,30 / 104,90 / 104,00 / 103,00 / 105,50, kabupaten 104,80) tetapi **pemetaan ke kecamatan tidak bisa diuji silang** karena tidak ada total yang menjumlah. Jangan pakai per‑kecamatan tanpa cek ulang ke PDF.
- **Centroid** 🔢 — dihitung dari poligon BIG (rata‑rata centroid tertimbang luas, EPSG:4326).

> ⚠️ **Dua definisi populasi yang berbeda — jangan dicampur.**
> - **Dukcapil/DKB Sem. II 2024 = 444.834 jiwa** (administratif, tersedia sampai level kecamatan).
> - **Proyeksi BPS hasil SP2020 = 424,68 ribu (2024)** dan **429,74 ribu (2025)** (dasar semua indikator makro BPS: kemiskinan, IPM, PDRB per kapita).
> Selisihnya ±20 ribu jiwa (≈4,7%). **Gunakan proyeksi BPS untuk indikator makro, Dukcapil untuk alokasi per kecamatan.**

### 1.3 Daftar lengkap 131 pekon/kelurahan (seed data)

Nama dan kode ✅ dari Kepmendagri No. 300.2.2‑2138/2025; lat/lon 🔢 dihitung dari poligon BIG;
luas (ha) ✅ dari atribut `LUASWH` BIG (luas menurut peraturan).
Semua 131 kode Kemendagri **cocok 100%** dengan 131 kode `KDEPUM` pada layer BIG (0 selisih di kedua arah). ✅

**Aturan kode:** digit ke‑9 pada segmen terakhir menandai status — `1xxx` = kelurahan, `2xxx` = pekon (desa).


#### Pringsewu — `18.10.01` (10 pekon, 5 kelurahan)

| Kode Kemendagri | Nama | Status | Lat | Lon | Luas (ha, BIG) |
|---|---|---|---|---|---|
| `18.10.01.1001` | Fajaresuk | kelurahan | -5.35398 | 104.95683 | 408.71 |
| `18.10.01.1002` | Pringsewu Utara | kelurahan | -5.35018 | 104.98053 | 150.49 |
| `18.10.01.1003` | Pringsewu Selatan | kelurahan | -5.3612 | 104.97126 | 176.95 |
| `18.10.01.1004` | Pringsewu Barat | kelurahan | -5.34972 | 104.97039 | 158.04 |
| `18.10.01.1005` | Pringsewu Timur | kelurahan | -5.36182 | 104.98109 | 112.77 |
| `18.10.01.2006` | Margakaya | pekon | -5.37782 | 104.97671 | 536.41 |
| `18.10.01.2007` | Waluyojati | pekon | -5.37777 | 104.95677 | 376.14 |
| `18.10.01.2008` | Sidoharjo | pekon | -5.36161 | 104.99303 | 359.44 |
| `18.10.01.2009` | Podomoro | pekon | -5.34306 | 104.9926 | 376.12 |
| `18.10.01.2010` | Bumi Arum | pekon | -5.33889 | 104.94897 | 368.7 |
| `18.10.01.2011` | Fajar Agung | pekon | -5.36911 | 104.94792 | 349.62 |
| `18.10.01.2012` | Rejo Sari | pekon | -5.33784 | 104.9659 | 238.66 |
| `18.10.01.2013` | Bumi Ayu | pekon | -5.34322 | 104.93366 | 414.82 |
| `18.10.01.2014` | Podosari | pekon | -5.33313 | 104.98193 | 219.83 |
| `18.10.01.2015` | Fajar Agung Barat | pekon | -5.37123 | 104.93643 | 155.07 |

#### Gading Rejo — `18.10.02` (23 pekon)

| Kode Kemendagri | Nama | Status | Lat | Lon | Luas (ha, BIG) |
|---|---|---|---|---|---|
| `18.10.02.2001` | Parerejo | pekon | -5.41882 | 104.98782 | 659.61 |
| `18.10.02.2002` | Blitarejo | pekon | -5.39728 | 104.99076 | 386.99 |
| `18.10.02.2003` | Panjerejo | pekon | -5.38319 | 104.99952 | 426.26 |
| `18.10.02.2004` | Bulokarto | pekon | -5.35815 | 105.00318 | 307.58 |
| `18.10.02.2005` | Wates | pekon | -5.37547 | 105.00927 | 213.53 |
| `18.10.02.2006` | Tambahrejo | pekon | -5.37734 | 105.03304 | 304.6 |
| `18.10.02.2007` | Wonodadi | pekon | -5.37647 | 105.05178 | 343.2 |
| `18.10.02.2008` | Gadingrejo | pekon | -5.38292 | 105.06908 | 299.26 |
| `18.10.02.2009` | Tegalsari | pekon | -5.34906 | 105.06203 | 436.93 |
| `18.10.02.2010` | Tulung Agung | pekon | -5.35599 | 105.04572 | 494.48 |
| `18.10.02.2011` | Bulurejo | pekon | -5.35766 | 105.01906 | 364.18 |
| `18.10.02.2012` | Yogyakarta | pekon | -5.33751 | 105.01996 | 357.87 |
| `18.10.02.2013` | Kediri | pekon | -5.34705 | 105.0331 | 241.99 |
| `18.10.02.2014` | Mataram | pekon | -5.33265 | 105.04825 | 620.47 |
| `18.10.02.2015` | Wonosari | pekon | -5.38328 | 105.04604 | 156.33 |
| `18.10.02.2016` | Klaten | pekon | -5.3458 | 105.01369 | 130.99 |
| `18.10.02.2017` | Wates Timur | pekon | -5.3707 | 105.01827 | 200.72 |
| `18.10.02.2018` | Wates Selatan | pekon | -5.392 | 105.01736 | 177.35 |
| `18.10.02.2019` | Gading Rejo Timur | pekon | -5.37121 | 105.0778 | 112.79 |
| `18.10.02.2020` | Gading Rejo Utara | pekon | -5.36745 | 105.06794 | 240.72 |
| `18.10.02.2021` | Tambah Rejo Barat | pekon | -5.384 | 105.02465 | 164.86 |
| `18.10.02.2022` | Wonodadi Utara | pekon | -5.36677 | 105.05594 | 103.76 |
| `18.10.02.2023` | Yogyakarta Selatan | pekon | -5.35494 | 105.02791 | 111.24 |

#### Ambarawa — `18.10.03` (8 pekon)

| Kode Kemendagri | Nama | Status | Lat | Lon | Luas (ha, BIG) |
|---|---|---|---|---|---|
| `18.10.03.2001` | Ambarawa | pekon | -5.42098 | 104.96208 | 511.09 |
| `18.10.03.2002` | Ambarawa Barat | pekon | -5.41485 | 104.95014 | 313.62 |
| `18.10.03.2003` | Kresno Mulyo | pekon | -5.42251 | 104.92308 | 541.25 |
| `18.10.03.2004` | Sumber Agung | pekon | -5.41228 | 104.93275 | 376.14 |
| `18.10.03.2005` | Tanjung Anom | pekon | -5.39709 | 104.93178 | 209.8 |
| `18.10.03.2006` | Jati Agung | pekon | -5.39532 | 104.94673 | 360.04 |
| `18.10.03.2007` | Margodadi | pekon | -5.39488 | 104.96797 | 510.52 |
| `18.10.03.2008` | Ambarawa Timur | pekon | -5.41803 | 104.97349 | 473.73 |

#### Pardasuka — `18.10.04` (13 pekon)

| Kode Kemendagri | Nama | Status | Lat | Lon | Luas (ha, BIG) |
|---|---|---|---|---|---|
| `18.10.04.2001` | Kedaung | pekon | -5.54193 | 104.92138 | 1026.63 |
| `18.10.04.2002` | Pardasuka | pekon | -5.46769 | 104.9316 | 581.96 |
| `18.10.04.2003` | Suka Negeri | pekon | -5.48716 | 104.9231 | 18.96 |
| `18.10.04.2004` | Tanjung Rusia | pekon | -5.47676 | 104.91463 | 595.32 |
| `18.10.04.2005` | Warga Mulyo | pekon | -5.45019 | 104.93802 | 453.58 |
| `18.10.04.2006` | Pujodadi | pekon | -5.43316 | 104.9418 | 484.62 |
| `18.10.04.2007` | Sukorejo | pekon | -5.43668 | 104.90601 | 445.51 |
| `18.10.04.2008` | Selapan | pekon | -5.53681 | 104.90478 | 1378.85 |
| `18.10.04.2009` | Rantau Tijang | pekon | -5.5408 | 104.94376 | 2553.25 |
| `18.10.04.2010` | Sidodadi | pekon | -5.44289 | 104.92895 | 404.86 |
| `18.10.04.2011` | Pardasuka Timur | pekon | -5.4847 | 104.93604 | 108.72 |
| `18.10.04.2012` | Tanjung Rusia Timur | pekon | -5.50149 | 104.91169 | 463.42 |
| `18.10.04.2013` | Pardasuka Selatan | pekon | -5.4929 | 104.92701 | 215.25 |

#### Pagelaran — `18.10.05` (22 pekon)

| Kode Kemendagri | Nama | Status | Lat | Lon | Luas (ha, BIG) |
|---|---|---|---|---|---|
| `18.10.05.2001` | Candi Retno | pekon | -5.39766 | 104.92162 | 249.98 |
| `18.10.05.2002` | Tanjung Dalom | pekon | -5.40197 | 104.90733 | 376.61 |
| `18.10.05.2003` | Way Ngison | pekon | -5.39584 | 104.89669 | 199.69 |
| `18.10.05.2004` | Suka Wangi | pekon | -5.36396 | 104.87053 | 106.39 |
| `18.10.05.2005` | Suka Ratu | pekon | -5.36671 | 104.87593 | 137.71 |
| `18.10.05.2006` | Pagelaran | pekon | -5.3668 | 104.88632 | 295.06 |
| `18.10.05.2007` | Patoman | pekon | -5.37389 | 104.89862 | 261.62 |
| `18.10.05.2008` | Karangsari | pekon | -5.38454 | 104.92406 | 453.99 |
| `18.10.05.2009` | Gumuk Mas | pekon | -5.36735 | 104.91261 | 205.36 |
| `18.10.05.2010` | Bumi Ratu | pekon | -5.34812 | 104.91807 | 406.4 |
| `18.10.05.2011` | Panutan | pekon | -5.36339 | 104.89663 | 175.11 |
| `18.10.05.2012` | Lugusari | pekon | -5.34898 | 104.87867 | 399.13 |
| `18.10.05.2019` | Pamenang | pekon | -5.35177 | 104.9062 | 226.37 |
| `18.10.05.2020` | Gemah Ripah | pekon | -5.38645 | 104.89444 | 152.13 |
| `18.10.05.2023` | Pasir Ukir | pekon | -5.34893 | 104.89604 | 205.02 |
| `18.10.05.2024` | Gumukrejo | pekon | -5.3724 | 104.92388 | 267.92 |
| `18.10.05.2027` | Puji Harjo | pekon | -5.37523 | 104.87394 | 106.17 |
| `18.10.05.2028` | Padang Rejo | pekon | -5.38203 | 104.90556 | 128.92 |
| `18.10.05.2029` | Sidodadi | pekon | -5.38369 | 104.88294 | 104.17 |
| `18.10.05.2030` | Sumber Rejo | pekon | -5.41126 | 104.90888 | 148.89 |
| `18.10.05.2031` | Ganjaran | pekon | -5.36259 | 104.93537 | 118.95 |
| `18.10.05.2032` | Bumi Rejo | pekon | -5.35584 | 104.9292 | 185.62 |

#### Banyumas — `18.10.06` (11 pekon)

| Kode Kemendagri | Nama | Status | Lat | Lon | Luas (ha, BIG) |
|---|---|---|---|---|---|
| `18.10.06.2001` | Banyumas | pekon | -5.28556 | 104.91011 | 286.87 |
| `18.10.06.2002` | Banyuwangi | pekon | -5.26975 | 104.89837 | 502.27 |
| `18.10.06.2003` | Sukamulya | pekon | -5.28632 | 104.929 | 230.91 |
| `18.10.06.2004` | Sriwungu | pekon | -5.30103 | 104.917 | 335.18 |
| `18.10.06.2005` | Banjarejo | pekon | -5.32123 | 104.92018 | 1235.52 |
| `18.10.06.2006` | Waya Krui | pekon | -5.26827 | 104.93618 | 245.64 |
| `18.10.06.2007` | Sri Rahayu | pekon | -5.27283 | 104.92332 | 246.91 |
| `18.10.06.2008` | Nusa Wungu | pekon | -5.2611 | 104.91122 | 253.8 |
| `18.10.06.2009` | Sinar Mulya | pekon | -5.30122 | 104.89993 | 354.08 |
| `18.10.06.2010` | Banyu Urip | pekon | -5.28192 | 104.91782 | 124.61 |
| `18.10.06.2011` | Mulyo Rejo | pekon | -5.25053 | 104.89907 | 289.1 |

#### Adiluwih — `18.10.07` (13 pekon)

| Kode Kemendagri | Nama | Status | Lat | Lon | Luas (ha, BIG) |
|---|---|---|---|---|---|
| `18.10.07.2001` | Adiluwih | pekon | -5.22608 | 105.02762 | 348.37 |
| `18.10.07.2002` | Bandung Baru | pekon | -5.2538 | 104.98091 | 577.52 |
| `18.10.07.2003` | Sinarwayah | pekon | -5.25923 | 104.95878 | 617.96 |
| `18.10.07.2004` | Enggal Rejo | pekon | -5.2433 | 105.0408 | 275.14 |
| `18.10.07.2005` | Sukoharum | pekon | -5.23451 | 105.06973 | 412.23 |
| `18.10.07.2006` | Waringin Sari Timur | pekon | -5.25556 | 105.01936 | 848.77 |
| `18.10.07.2007` | Tri Tunggal Mulya | pekon | -5.26463 | 105.03915 | 573.7 |
| `18.10.07.2008` | Purwodadi | pekon | -5.27614 | 105.02055 | 449.87 |
| `18.10.07.2009` | Srikaton | pekon | -5.22679 | 105.04517 | 543.44 |
| `18.10.07.2010` | Tunggul Pawenang | pekon | -5.22408 | 105.06064 | 463.57 |
| `18.10.07.2011` | Bandung Baru Barat | pekon | -5.27229 | 104.95883 | 250.53 |
| `18.10.07.2012` | Totokarto | pekon | -5.25363 | 104.99751 | 330.62 |
| `18.10.07.2013` | Kuta Waringin | pekon | -5.23836 | 105.00799 | 604.89 |

#### Sukoharjo — `18.10.08` (16 pekon)

| Kode Kemendagri | Nama | Status | Lat | Lon | Luas (ha, BIG) |
|---|---|---|---|---|---|
| `18.10.08.2001` | Sinar Baru | pekon | -5.30231 | 104.94239 | 644.56 |
| `18.10.08.2002` | Sukoharjo I | pekon | -5.31846 | 104.97049 | 707.25 |
| `18.10.08.2003` | Sukoharjo II | pekon | -5.31609 | 104.99151 | 483.05 |
| `18.10.08.2004` | Sukoharjo III | pekon | -5.29857 | 104.98827 | 199.03 |
| `18.10.08.2005` | Sukoharjo IV | pekon | -5.3277 | 105.00779 | 478.2 |
| `18.10.08.2006` | Panggungrejo | pekon | -5.31722 | 105.03483 | 595.32 |
| `18.10.08.2007` | Pandan Sari | pekon | -5.29854 | 105.01754 | 322.32 |
| `18.10.08.2008` | Pandan Surat | pekon | -5.29218 | 105.00497 | 540.1 |
| `18.10.08.2009` | Keputran | pekon | -5.28764 | 104.98121 | 359.83 |
| `18.10.08.2010` | Sukoyoso | pekon | -5.2898 | 104.95867 | 253.39 |
| `18.10.08.2011` | Siliwangi | pekon | -5.28344 | 104.94175 | 264.98 |
| `18.10.08.2012` | Waringinsari Barat | pekon | -5.27509 | 104.9831 | 948.44 |
| `18.10.08.2013` | Pandan Sari Selatan | pekon | -5.31392 | 105.01297 | 372.76 |
| `18.10.08.2014` | Sinar Baru Timur | pekon | -5.31524 | 104.95328 | 576.64 |
| `18.10.08.2015` | Panggung Rejo Utara | pekon | -5.2959 | 105.03245 | 365.03 |
| `18.10.08.2016` | Sukoharjo III Barat | pekon | -5.29837 | 104.97428 | 216.4 |

#### Pagelaran Utara — `18.10.09` (10 pekon)

| Kode Kemendagri | Nama | Status | Lat | Lon | Luas (ha, BIG) |
|---|---|---|---|---|---|
| `18.10.09.2001` | Fajar Baru | pekon | -5.32274 | 104.88402 | 1728.64 |
| `18.10.09.2002` | Kemilin | pekon | -5.32087 | 104.85639 | 695.01 |
| `18.10.09.2003` | Neglasari | pekon | -5.28513 | 104.82931 | 554.01 |
| `18.10.09.2004` | Fajar Mulia | pekon | -5.29301 | 104.87672 | 557.03 |
| `18.10.09.2005` | Margosari | pekon | -5.22578 | 104.82952 | 8499.81 |
| `18.10.09.2006` | Giri Tunggal | pekon | -5.28275 | 104.88664 | 363.52 |
| `18.10.09.2007` | Sumber Bandung | pekon | -5.2798 | 104.83729 | 403.69 |
| `18.10.09.2008` | Madaraya | pekon | -5.2872 | 104.85836 | 280.24 |
| `18.10.09.2009` | Way Kunir | pekon | -5.2668 | 104.81444 | 1832.68 |
| `18.10.09.2010` | Gunung Raya | pekon | -5.30653 | 104.83975 | 879.9 |
> **Catatan penomoran Pagelaran (18.10.05):** urutan melompat (…2012, lalu 2019, 2020, 2023, 2024, 2027–2032).
> Ini normal — nomor yang hilang adalah pekon yang dipindahkan ke Kec. Pagelaran Utara saat kecamatan itu
> dimekarkan (2012). Jangan diperlakukan sebagai data hilang.

> **Catatan ejaan:** BPS menulis `Gadingrejo`/`Adiluwih`, Kepmendagri & BIG menulis `Gading Rejo`/`Adiluwih`,
> Tabel 1.1.1 BPS menulis `Adi Luwih`. Untuk *join* antar sumber **gunakan kode wilayah, jangan nama.**

---

## 2. Kemiskinan — deret waktu 2015–2025

### 2.1 Tabel utama

Sumber: BPS, Susenas Maret. 2015–2025 dari **Potret Kemiskinan Kabupaten Pringsewu 2025** (terbit 17 Nov 2025);
2017–2024 dikonfirmasi ulang oleh *Pringsewu Dalam Angka 2025* Tabel 4.4.1 & 4.4.2; 2024 dikonfirmasi ketiga
kalinya lewat tabel statistik dinamis BPS (`datacontent` = P0 8.32, P1 0.92, P2 0.16, 34.42 ribu, GK 583425). ✅

| Tahun | Penduduk miskin (ribu jiwa) | P0 — % miskin | Garis Kemiskinan (Rp/kap/bln) | P1 (kedalaman) | P2 (keparahan) | Gini Ratio |
|---|---|---|---|---|---|---|
| 2015 | 45,58 | 11,80 | ±305.000 ⚠️ | 1,40 | 0,25 | ±0,35 ⚠️ |
| 2016 | 45,72 | 11,73 | ❌ | 1,78 | 0,42 | ❌ |
| 2017 | 44,41 | 11,30 | 398.830 | 1,71 | 0,39 | ❌ |
| 2018 | 41,64 | 10,50 | 408.174 | 1,44 | 0,31 | ❌ |
| 2019 | 40,55 | 10,15 | 422.691 | 1,13 | 0,21 | ❌ |
| 2020 | 40,12 | 9,97 | 458.627 | 1,20 | 0,21 | ❌ |
| 2021 | 41,04 | 10,11 | 475.983 | 1,38 | 0,26 | ❌ |
| 2022 | 38,18 | 9,34 | 511.679 | 1,07 | 0,19 | ❌ |
| 2023 | 37,60 | 9,14 | 555.787 | 0,99 | 0,19 | ❌ |
| **2024** | **34,42** | **8,32** | **583.425** | **0,92** | **0,16** | **0,266** ✅ |
| **2025** | **31,66** | **7,60** | ±613.000 ⚠️ | **0,58** | **0,10** | **0,299** ✅ |

**Status:** kolom penduduk miskin, P0, P1, P2 untuk **2015–2025 semuanya ✅ VERIFIED** (label data Gambar 2.2
dan 2.3 Potret Kemiskinan 2025; 2017–2024 identik dengan Tabel 4.4.1/4.4.2 PDA 2025 — dua dokumen independen).
Garis Kemiskinan **2017–2024 ✅**; 2015 dan 2025 hanya disebut naratif ("sekitar tiga ratus lima ribu rupiah"
pada 2015, "lebih dari enam ratus tiga belas ribu rupiah" pada 2025) — label numerik Gambar 2.1 tidak
terekstrak, jadi ⚠️.

### 2.2 Gini Ratio — sebagian besar tahun TIDAK ditemukan

- ✅ **2024 = 0,266** (Lampung 0,302; Indonesia 0,379) — tabel dinamis BPS Pringsewu.
- ✅ **2025 = 0,299** (Lampung 0,292) — tabel *Gini Ratio Kabupaten/Kota* BPS Provinsi Lampung.
  Perhatikan: 2025 Pringsewu **naik tajam** dan untuk pertama kalinya **melampaui** rata‑rata provinsi.
- ⚠️ **2015 ≈ 0,35** — hanya dari kalimat naratif Potret Kemiskinan 2025.
- ❌ **2016–2023 NOT FOUND.** Gambar 2.4 memuat grafik dua seri (Pringsewu + Lampung), tapi label datanya
  bercampur dengan label sumbu‑Y saat diekstrak sehingga pemetaan tahun→nilai tidak dapat dipastikan.
  Portal tabel dinamis BPS hanya me‑render tahun terakhir di sisi server (parameter `?year=`, `?th=`,
  `?tahun=` semuanya diabaikan — sudah diuji), sehingga tahun historis tidak bisa diambil tanpa API key.
  **Jangan mengisi sel‑sel ini dengan interpolasi.** Untuk melengkapi: daftar API key di
  <https://webapi.bps.go.id/> lalu query `var=225`, `domain=1810`.

### 2.3 Peringatan konsistensi P0 vs proyeksi penduduk

Membagi "penduduk miskin" dengan "jumlah penduduk" yang tercetak pada Gambar 2.2 **tidak** mereproduksi P0,
dan selisihnya melebar dari tahun ke tahun:

| Tahun | Miskin (ribu) ÷ Penduduk (ribu) | = hasil bagi | P0 terbit | Selisih |
|---|---|---|---|---|
| 2017 | 44,41 ÷ 394,12 | 11,27 | 11,30 | 0,03 |
| 2020 | 40,12 ÷ 404,18 | 9,93 | 9,97 | 0,04 |
| 2023 | 37,60 ÷ 419,59 | 8,96 | 9,14 | 0,18 |
| 2024 | 34,42 ÷ 424,68 | 8,11 | 8,32 | 0,21 |
| 2025 | 31,66 ÷ 429,74 | 7,37 | 7,60 | 0,23 |

Penyebabnya: P0 diestimasi langsung dari Susenas Maret, sedangkan seri "jumlah penduduk" adalah proyeksi
**pertengahan tahun**. **Selalu tampilkan P0 sebagaimana terbit; jangan hitung ulang dari headcount.**

Seri proyeksi penduduk BPS (ribu jiwa) ✅: 2015 387,11 · 2016 390,68 · 2017 394,12 · 2018 397,42 ·
2019 400,58 · 2020 404,18 · 2021 409,33 · 2022 414,47 · 2023 419,59 · 2024 424,68 · **2025 429,74**

### 2.4 Posisi Pringsewu di Provinsi Lampung (Maret 2025) ✅

Dari Gambar 2.12 Potret Kemiskinan 2025 — 15 kabupaten/kota diurutkan menaik menurut P0.
Pringsewu berada di urutan **ke‑6 terendah** dengan **31,66 ribu jiwa / 7,60%**.

Sebaran P0 seluruh Lampung 2025: 5,92 · 6,44 · 6,72 · 6,95 · 7,54 · **7,60 (Pringsewu)** · 9,36 · 9,59 ·
9,93 · 10,10 · 10,93 · 12,05 · 12,13 · 12,15 · 15,78.
(Pemetaan nilai→nama kabupaten tidak terekstrak — ❌.)

### 2.5 Karakteristik rumah tangga miskin ✅

Semua seri di bawah lolos uji silang: tiga komponen tiap tahun berjumlah 100,00.

**Pendidikan penduduk miskin 15+ (%)**

| Tahun | < SD | Tamat SD/SMP | ≥ SMA |
|---|---|---|---|
| 2015 | 31,75 | 58,75 | 9,51 |
| 2016 | 27,22 | 64,23 | 8,55 |
| 2017 | 20,09 | 65,81 | 14,10 |
| 2018 | 27,44 | 63,43 | 9,13 |
| 2019 | 27,00 | 56,90 | 16,10 |
| 2020 | 22,62 | 64,04 | 13,34 |
| 2021 | 27,43 | 55,53 | 17,04 |
| 2022 | 22,92 | 58,34 | 18,75 |
| 2023 | 21,72 | 55,37 | 22,91 |
| 2024 | 23,83 | 61,25 | 14,92 |

**Status pekerjaan penduduk miskin 15+ (%)** — kolom "formal" direkonstruksi lalu diuji:
formal = 100 − informal − tidak bekerja, cocok untuk **10/10 tahun** ✅

| Tahun | Tidak bekerja | Informal | Formal |
|---|---|---|---|
| 2015 | 41,66 | 42,70 | 15,63 |
| 2016 | 46,25 | 38,97 | 14,78 |
| 2017 | 35,79 | 56,52 | 7,69 |
| 2018 | 45,75 | 39,07 | 15,18 |
| 2019 | 36,45 | 38,55 | 25,00 |
| 2020 | 44,36 | 40,49 | 15,15 |
| 2021 | 41,96 | 38,61 | 19,43 |
| 2022 | 42,51 | 41,66 | 15,83 |
| 2023 | 45,58 | 36,97 | 17,46 |
| 2024 | 43,83 | 44,23 | 11,94 |

**Lapangan usaha penduduk miskin 15+ (%)**

| Tahun | Tidak bekerja | Pertanian | Non‑pertanian |
|---|---|---|---|
| 2015 | 41,66 | 25,59 | 32,74 |
| 2016 | 46,25 | 27,71 | 26,04 |
| 2017 | 35,79 | 41,21 | 23,00 |
| 2018 | 45,75 | 8,09 | 46,17 |
| 2019 | 36,45 | 32,78 | 30,77 |
| 2020 | 44,36 | 33,98 | 21,66 |
| 2021 | 41,96 | 22,15 | 35,89 |
| 2022 | 42,51 | 30,12 | 27,37 |
| 2023 | 45,58 | 29,29 | 25,14 |
| 2024 | 43,83 | 28,41 | 27,77 |

**Akses fasilitas dasar RUMAH TANGGA MISKIN (%)** ✅ — dikonfirmasi oleh narasi teks publikasi

| Tahun | Air layak | Jamban sendiri/bersama |
|---|---|---|
| 2016 | 61,67 | 68,73 |
| 2017 | 66,57 | 76,51 |
| 2018 | 66,40 | 85,37 |
| 2019 | 67,76 | 88,57 |
| 2020 | 69,75 | 95,32 |
| 2021 | 92,38 | 91,49 |
| 2022 | 94,27 | 87,65 |
| 2023 | 94,24 | 97,79 |
| 2024 | **89,54** | **97,18** |

> **Sinyal kebijakan:** akses air layak RT miskin **turun** dari puncak 94,27% (2022) ke 89,54% (2024).
> BPS menyebut kemungkinan kekeringan, kerusakan sarana air bersih, atau keterbatasan biaya pemeliharaan.

**Pengeluaran makanan (% dari total)** — RT miskin selalu di atas RT tidak miskin:
2016: miskin 61,70 vs tidak miskin 57,24 · puncak 2020: 66,94 · terendah 2023: 59,24 (tidak miskin 51,97)
· 2024: **61,87** vs **55,61**. ✅

**Angka Partisipasi Sekolah penduduk miskin** ⚠️: usia 13–15 tahun tercatat 90,09% (2015), sempat 100%
(2017–2018), turun ke titik terendah **83,63% (2023)**, naik tipis ke **85,73% (2024)**. Usia SD disebut
mendekati universal (91,20% disebut untuk satu jenjang, konteks tidak sepenuhnya terekstrak).

---

## 3. Indikator pembangunan (Statistik Kunci BPS) ✅

Dari halaman *Statistik Kunci* PDA 2025. Diuji silang tiga arah: TPT dan TPAK direproduksi dari Tabel 3.2.1,
PDRB per kapita direproduksi dari PDRB ÷ penduduk, kemiskinan cocok dengan Tabel 4.4.1.

| Indikator | Satuan | 2022 | 2023 | 2024 |
|---|---|---|---|---|
| Penduduk (proyeksi SP2020, pertengahan tahun) | ribu jiwa | 414,47 | 419,59 | 424,68 |
| Laju pertumbuhan penduduk | % | 1,25 | 1,24 | 1,21 |
| Usia Harapan Hidup (UHH/e₀) | tahun | 74,15 | 74,33 | **74,56** |
| Angka Melek Aksara 15+ | % | … | 97,51 | **97,13** |
| TPAK | % | 73,17 | 73,29 | **73,55** |
| TPT | % | 4,77 | 4,66 | **4,39** |
| Penduduk miskin | ribu jiwa | 38,18 | 37,60 | 34,42 |
| Persentase penduduk miskin | % | 9,34 | 9,14 | 8,32 |
| **IPM** | poin | 72,57 | 73,11 | **73,84** |
| PDRB harga berlaku | miliar Rp | 12.841,95 | 14.009,71* | 15.098,16** |
| Laju pertumbuhan ekonomi | % | 4,37 | 4,78* | 4,58** |
| **PDRB per kapita harga berlaku** | ribu Rp | 30.984,40 | 33.389,85 | **35.551,94** |

`*` angka sementara · `**` angka sangat sementara · Angka Kelahiran Total (TFR) dan AKB: dicetak `...` (tidak tersedia) di sumber

**Verifikasi turunan 🔢:**
- TPAK 2024 = 235.992 ÷ 320.868 = **73,55%** ✅ cocok persis
- TPT 2024 = 10.361 ÷ 235.992 = **4,39%** ✅ cocok persis
- PDRB/kapita 2024 = 15.098,16 miliar ÷ 424,68 ribu = **35.550 ribu Rp** ✅ cocok (selisih pembulatan)

### 3.1 IPM — perbandingan dengan Lampung ✅

IPM 2024 **73,84**, di atas Provinsi Lampung (**73,13**). Peringkat **ke‑4 tertinggi** di Lampung, setelah
Kota Bandar Lampung (80,46), Kota Metro (80,41), dan Lampung Tengah (74,16).

IPM 2024 seluruh Lampung: Lampung Barat 72,41 · Tanggamus 70,54 · Lampung Selatan 72,15 · Lampung Timur 73,05
· Lampung Tengah 74,16 · Lampung Utara 71,42 · Way Kanan 71,17 · Tulangbawang 72,24 · Pesawaran 70,24 ·
**Pringsewu 73,84** · Mesuji 68,59 · Tulang Bawang Barat 70,04 · Pesisir Barat 71,04 ·
Bandar Lampung 80,46 · Metro 80,41 · **LAMPUNG 73,13**. ✅

> ⚠️ Sejak 2021 IPM dihitung memakai UHH hasil **Long Form SP2020**; seri lama (berbasis SP2010) tidak
> sebanding. Angka **73,11** yang beredar di media adalah nilai **2023**, bukan angka terbaru.
> Kolom IPM 2021–2023 per kabupaten di Tabel 13.4 tidak dapat direkonstruksi (kolom teracak) — ❌,
> kecuali Pringsewu yang diketahui dari Statistik Kunci: 2022 = 72,57 · 2023 = 73,11 ✅.

### 3.2 Komponen IPM yang BELUM lengkap

| Komponen | Status |
|---|---|
| Angka Harapan Hidup (UHH) | ✅ 74,56 tahun (2024) |
| **Harapan Lama Sekolah (HLS)** | ❌ **NOT FOUND** — tidak ada di PDA 2025 maupun tabel dinamis yang dapat diakses |
| **Rata‑rata Lama Sekolah (RLS)** | ❌ **NOT FOUND** — idem |
| **Pengeluaran per kapita disesuaikan (PPP)** | ❌ **NOT FOUND** — jangan dikacaukan dengan pengeluaran nominal Susenas di §3.5 |

Untuk melengkapi: BPS *Berita Resmi Statistik IPM* atau publikasi *Indeks Pembangunan Manusia Kabupaten/Kota*,
atau WebAPI BPS dengan API key.

### 3.3 Ketenagakerjaan 2024 (Sakernas Agustus) ✅

Seluruh sel lolos uji: L+P = total di tiap baris, dan komponen menjumlah ke totalnya.

| Kegiatan utama | Laki‑laki | Perempuan | Total |
|---|---|---|---|
| **I. Angkatan Kerja** | 147.165 | 88.827 | **235.992** |
| — Bekerja | 142.323 | 83.308 | 225.631 |
| — Pengangguran | 4.842 | 5.519 | 10.361 |
| **II. Bukan Angkatan Kerja** | 17.384 | 67.492 | **84.876** |
| — Sekolah | 9.564 | 12.819 | 22.383 |
| — Mengurus rumah tangga | 4.265 | 51.399 | 55.664 |
| — Lainnya | 3.555 | 3.274 | 6.829 |
| **Total penduduk 15+** | **164.549** | **156.319** | **320.868** |

**Status pekerjaan utama (2024)** — Σ = 225.631 ✅

| Status | Jumlah |
|---|---|
| Buruh/karyawan/pegawai | 62.411 |
| Berusaha sendiri | 62.086 |
| Pekerja keluarga/tak dibayar | 35.351 |
| Berusaha dibantu buruh tidak tetap/tidak dibayar | 34.302 |
| Pekerja bebas | 24.872 |
| Berusaha dibantu buruh tetap/dibayar | 6.609 |

> **Struktur kerentanan** 🔢: hanya **69.020** dari 225.631 pekerja (**30,6%**) berstatus relatif formal
> (buruh/karyawan + berusaha dibantu buruh tetap). Sisanya 69,4% informal — konsisten dengan temuan
> Potret Kemiskinan bahwa 44,2% penduduk miskin bekerja di sektor informal.

### 3.4 Pendidikan penduduk usia kerja & indikator "ijazah SMA+" ✅

Tabel 3.2.2 PDA 2025. Persentase tercetak direproduksi untuk **6/6 baris** (bekerja ÷ usia kerja) ✅,
dan kedua kolom menjumlah tepat ke totalnya ✅.

| Pendidikan tertinggi | Bekerja | Penduduk usia kerja (15+) | % bekerja |
|---|---|---|---|
| ≤ SD | 80.612 | 113.182 | 71,22 |
| SMP | 52.528 | 85.918 | 61,14 |
| SMA | 30.113 | 45.962 | 65,52 |
| SMK | 43.557 | 51.026 | 85,36 |
| Diploma I/II/III | 4.684 | 5.884 | 79,61 |
| Universitas | 14.137 | 18.896 | 74,81 |
| **Total** | **225.631** | **320.868** | **70,32** |

**Persentase penduduk 15+ berijazah SMA ke atas** 🔢 **DERIVED**:
(45.962 + 51.026 + 5.884 + 18.896) ÷ 320.868 = 121.768 ÷ 320.868 = **37,95%**

> Ini **bukan** angka resmi BPS berlabel "penduduk dengan ijazah SMA+" — ini turunan dari tabel
> ketenagakerjaan dengan basis penduduk **15 tahun ke atas**. Bila NADI perlu angka yang bisa dikutip
> resmi, tandai sebagai perhitungan internal, bukan statistik terbitan.

### 3.5 Pengeluaran per kapita sebulan (Susenas Maret) ✅

Σ komponen makanan = 580.590 vs tercetak 580.589 ✅ · Σ non‑makanan = 459.243 ✅ · total = 1.039.832 ✅

| Kelompok | 2023 (Rp) | 2024 (Rp) |
|---|---|---|
| **Makanan** | **542.281** | **580.589** |
| — Makanan & minuman jadi | 144.868 | 135.415 |
| — Padi‑padian | 74.168 | 91.875 |
| — Rokok | 78.888 | 85.535 |
| — Sayur‑sayuran | 55.753 | 59.662 |
| — Buah‑buahan | 27.346 | 38.653 |
| — Ikan/udang/cumi/kerang | 33.804 | 36.491 |
| — Telur dan susu | 27.266 | 28.785 |
| — Bahan minuman | 20.405 | 22.610 |
| — Minyak dan kelapa | 19.932 | 21.395 |
| — Kacang‑kacangan | 15.738 | 17.340 |
| — Daging | 17.487 | 16.431 |
| — Bumbu‑bumbuan | 13.045 | 12.577 |
| — Konsumsi lainnya | 8.896 | 10.969 |
| — Umbi‑umbian | 4.685 | 2.852 |
| **Bukan makanan** | **495.835** | **459.243** |
| — Perumahan & fasilitas RT | 235.074 | 230.516 |
| — Aneka barang dan jasa | 118.518 | 117.159 |
| — Pajak, pungutan, asuransi | 41.104 | 41.150 |
| — Pakaian, alas kaki, tutup kepala | 27.823 | 28.486 |
| — Barang tahan lama | 45.414 | 26.519 |
| — Keperluan pesta/upacara | 27.902 | 15.413 |
| **TOTAL** | **1.038.116** | **1.039.832** |

> 🔢 Total nyaris stagnan (+0,17% nominal) padahal inflasi positif → **daya beli riil turun pada 2024**.
> Belanja rokok (85.535/bulan) melampaui gabungan pakaian + barang tahan lama + pesta (70.418).

---

## 4. Indikator sosial

### 4.1 Ringkasan status

| Indikator | Nilai | Tahun | Sumber | Status |
|---|---|---|---|---|
| Prevalensi stunting | 19,0% | 2021 | SSGI/media | ⚠️ |
| Prevalensi stunting | 16,2% | 2022 | SSGI/media | ⚠️ |
| Prevalensi stunting | 15,8% | 2023 | SKI 2023/media | ⚠️ |
| Prevalensi stunting | **19,5%** | 2024 | SSGI 2024/media (naik 3,7 poin) | ⚠️ |
| Balita stunting (ePPGBM) | 1.405 anak | 2024 | media | ⚠️ |
| AKI | 194 per 100.000 KH | 2024 | Profil Kesehatan Dinkes Pringsewu | ⚠️ |
| AKB | 9 per 1.000 KH | 2024 | Profil Kesehatan Dinkes Pringsewu | ⚠️ |
| Cakupan JKN | 98,29% | 1 Agu 2024 | BPJS Kesehatan/media | ⚠️ |
| Air minum **layak** (semua RT) | **95,64%** | 2023 | BPS, Indikator SDGs 6.1.1(a) | ✅ |
| Air minum **aman** (semua RT) | **41,31%** | 2024 | BPS, tabel dinamis | ✅ |
| Kecukupan air minum | **99,85%** | 2023 | BPS, tabel dinamis | ✅ |
| Air layak (RT **miskin**) | 89,54% | 2024 | BPS Potret Kemiskinan 2025 | ✅ |
| Jamban sendiri/bersama (RT **miskin**) | 97,18% | 2024 | BPS Potret Kemiskinan 2025 | ✅ |
| **Sanitasi layak (semua RT)** | — | — | — | ❌ **NOT FOUND** |
| **Akses listrik (% RT)** | — | — | — | ❌ **NOT FOUND** |
| **RTLH (rumah tidak layak huni)** | — | — | — | ❌ **NOT FOUND** |
| **Jumlah rumah tangga / KK** | — | — | — | ❌ **NOT FOUND** |

### 4.2 Air minum — rincian menurut kelompok pengeluaran ✅

Indikator SDGs 6.1.1(a), *Persentase RT yang menggunakan sumber air minum layak*, Kab. Pringsewu **2023**:

| Kelompok | % |
|---|---|
| 40% terbawah | 94,36 |
| 40% tengah | 95,53 |
| 20% teratas | 99,04 |
| **Total** | **95,64** |

> **Kesenjangan air layak antar kelompok kecil (4,7 poin)** — masalahnya bukan pemerataan air *layak*.
> Yang menganga adalah **air *aman*: hanya 41,31% (2024)** sementara air *layak* 95,64%. Selisih ~54 poin
> ini adalah ruang intervensi paling besar di sektor air.

### 4.3 Kelahiran hidup menurut kecamatan, 2024 ✅

Tabel 4.2.5 PDA 2025 (Dinkes Pringsewu). Uji: L+P = total ✅ dan Σ kecamatan = 5.684 ✅ (2.926 L + 2.758 P).

| Kecamatan | Laki‑laki | Perempuan | Total | CBR kasar 🔢 (/1.000 pddk) |
|---|---|---|---|---|
| Pardasuka | 201 | 197 | 398 | 10,3 |
| Ambarawa | 321 | 288 | 609 | 15,0 |
| Pagelaran | 338 | 301 | 639 | 11,2 |
| Pagelaran Utara | 112 | 138 | 250 | 14,8 |
| Pringsewu | 670 | 626 | 1.296 | 14,6 |
| Gading Rejo | 505 | 470 | 975 | 11,4 |
| Sukoharjo | 378 | 364 | 742 | 13,6 |
| Banyumas | 138 | 139 | 277 | 11,7 |
| Adiluwih | 263 | 235 | 498 | 12,6 |
| **Kabupaten** | **2.926** | **2.758** | **5.684** | **12,8** |

### 4.4 Komposisi agama menurut kecamatan, 2024 ✅

Tabel 4.3.1 PDA 2025 (DKB Sem. II 2024). **Uji silang paling kuat dalam dokumen ini**: penjumlahan 6 kolom
untuk setiap kecamatan menghasilkan tepat angka penduduk kecamatan itu di Tabel 3.1.1 — 9/9 cocok.

| Kecamatan | Islam | Protestan | Katolik | Hindu | Buddha | Lainnya | Σ = penduduk |
|---|---|---|---|---|---|---|---|
| Pardasuka | 38.492 | 23 | 69 | – | 8 | 2 | 38.594 ✅ |
| Ambarawa | 39.190 | 336 | 654 | 335 | – | 2 | 40.517 ✅ |
| Pagelaran | 54.898 | 249 | 1.316 | 351 | 16 | 9 | 56.839 ✅ |
| Pagelaran Utara | 16.558 | 8 | 47 | 105 | 112 | 22 | 16.852 ✅ |
| Pringsewu | 83.756 | 1.300 | 3.391 | 108 | 198 | 5 | 88.758 ✅ |
| Gading Rejo | 84.159 | 393 | 408 | 466 | 21 | – | 85.447 ✅ |
| Sukoharjo | 52.224 | 720 | 1.128 | 686 | – | 2 | 54.760 ✅ |
| Banyumas | 23.236 | 16 | 172 | 63 | 9 | 114 | 23.610 ✅ |
| Adiluwih | 37.469 | 487 | 1.080 | 230 | 178 | 13 | 39.457 ✅ |
| **Kabupaten** | **429.982** | **3.532** | **8.265** | **2.344** | **542** | **169** | **444.834** ✅ |

### 4.5 Indeks Desa Membangun 2024 ✅

Kementerian Desa PDTT. Σ tiap kolom cocok, dan Σ baris tiap kecamatan = jumlah pekonnya.
**Tidak ada Desa Tertinggal atau Sangat Tertinggal di Pringsewu.**

| Kecamatan | Berkembang | Maju | Mandiri | Σ pekon |
|---|---|---|---|---|
| Pardasuka | 6 | 7 | – | 13 ✅ |
| Ambarawa | – | 3 | 5 | 8 ✅ |
| Pagelaran | 1 | 14 | 7 | 22 ✅ |
| Pagelaran Utara | 7 | 3 | – | 10 ✅ |
| Pringsewu | 1 | 4 | 5 | 10 ✅ |
| Gading Rejo | – | 10 | 13 | 23 ✅ |
| Sukoharjo | – | 14 | 2 | 16 ✅ |
| Banyumas | – | 11 | – | 11 ✅ |
| Adiluwih | – | 9 | 4 | 13 ✅ |
| **Total** | **15** | **75** | **36** | **126** ✅ |

> **Sangat berguna untuk targeting NADI.** 15 pekon berstatus "Berkembang" (paling tertinggal secara relatif)
> terkonsentrasi di **Pagelaran Utara (7)** dan **Pardasuka (6)** — dua kecamatan dengan kepadatan terendah
> (107 dan 442 jiwa/km²) dan, untuk Pagelaran Utara, luas terbesar (25,63% wilayah kabupaten).
> Ini konsisten: **wilayah perbukitan barat‑laut adalah kantong ketertinggalan**.

---

## 5. Struktur ekonomi

### 5.1 PDRB menurut lapangan usaha (ADHB, % distribusi) ✅

Tabel 12.3 PDA 2025. Σ kolom 2024 = 99,99 ≈ 100,00 ✅ (selisih pembulatan).

| Kode | Lapangan usaha | 2020 | 2021 | 2022 | 2023* | **2024**\*\* |
|---|---|---|---|---|---|---|
| A | **Pertanian, Kehutanan, dan Perikanan** | 25,12 | 24,07 | 23,88 | 23,10 | **22,67** |
| G | Perdagangan Besar & Eceran; Reparasi Mobil/Motor | 13,75 | 14,11 | 15,72 | 16,56 | **16,90** |
| C | Industri Pengolahan | 14,94 | 15,32 | 14,49 | 13,96 | 14,24 |
| F | Konstruksi | 11,76 | 12,39 | 12,31 | 12,35 | 11,86 |
| H | Transportasi dan Pergudangan | 4,51 | 4,48 | 5,22 | 6,27 | 6,48 |
| J | Informasi dan Komunikasi | 6,05 | 6,01 | 5,53 | 5,46 | 5,42 |
| P | Jasa Pendidikan | 5,68 | 5,60 | 5,38 | 5,22 | 5,25 |
| O | Administrasi Pemerintahan, Pertahanan, Jamsos Wajib | 4,41 | 4,38 | 4,02 | 3,75 | 3,80 |
| K | Jasa Keuangan dan Asuransi | 4,01 | 4,15 | 3,94 | 3,80 | 3,72 |
| L | Real Estat | 3,94 | 3,84 | 3,69 | 3,49 | 3,52 |
| I | Penyediaan Akomodasi dan Makan Minum | 2,63 | 2,51 | 2,59 | 2,74 | 2,75 |
| Q | Jasa Kesehatan dan Kegiatan Sosial | 1,58 | 1,59 | 1,47 | 1,44 | 1,46 |
| R,S,T,U | Jasa Lainnya | 1,15 | 1,08 | 1,27 | 1,39 | 1,45 |
| M,N | Jasa Perusahaan | 0,25 | 0,24 | 0,26 | 0,26 | 0,27 |
| B | Pertambangan dan Penggalian | 0,11 | 0,10 | 0,10 | 0,10 | 0,09 |
| D | Pengadaan Listrik dan Gas | 0,07 | 0,07 | 0,07 | 0,07 | 0,06 |
| E | Pengadaan Air, Sampah, Limbah, Daur Ulang | 0,06 | 0,06 | 0,06 | 0,05 | 0,05 |
| | **PDRB** | 100,00 | 100,00 | 100,00 | 100,00 | **100,00** |

> **Jawaban atas "sektor dominan?"** — Ya, **pertanian tetap sektor terbesar (22,67% pada 2024)**, tapi
> pangsanya **turun terus** (25,12% → 22,67% dalam 5 tahun, −2,45 poin) sementara **perdagangan naik tajam**
> (13,75% → 16,90%, +3,15 poin). Jika tren berlanjut, perdagangan akan menyalip pertanian sekitar 2029–2030.
> Untuk NADI: penerima manfaat berbasis pertanian adalah mayoritas hari ini, tetapi desain harus mengakomodasi
> pergeseran ke perdagangan/jasa informal.

### 5.2 Padi — komoditas utama ✅

Luas panen padi 2024 **26.589 ha** (Σ 9 kecamatan cocok persis dengan total tercetak ✅).
Padi mendominasi total: jagung 8.176 ha, kedelai 90 ha, ubi kayu 71 ha, ubi jalar 6,25 ha, kacang tanah 4 ha.

| Kecamatan | Padi (ha) | Jagung (ha) | Ubi kayu (ha) | Kedelai (ha) |
|---|---|---|---|---|
| Pardasuka | 4.357 | 5 | 14 | 42 |
| Ambarawa | 4.109 | – | – | 12 |
| Pagelaran | 2.815 | 168 | 9 | – |
| Pagelaran Utara | 1.008 | 565 | 15 | 21 |
| Pringsewu | 2.860 | 25 | 2 | – |
| Gading Rejo | 6.180 | 102 | – | 15 |
| Sukoharjo | 2.379 | 1.798 | 20 | – |
| Banyumas | 1.335 | 569 | 2 | – |
| Adiluwih | 1.546 | 4.944 | 9 | – |
| **Kabupaten** | **26.589** | **8.176** | **71** | **90** |

⚠️ **Peringatan pemetaan:** total tiap kolom ✅ terverifikasi, tetapi **penugasan nilai ke kecamatan
⚠️ UNVERIFIED** — kolom nama pada PDF teracak oleh watermark dan tidak ada uji silang independen per baris.
Pola yang muncul masuk akal (Gading Rejo tertinggi untuk padi di dataran irigasi; Adiluwih & Sukoharjo
dominan jagung; Pagelaran Utara yang berbukit paling rendah padinya), tetapi **verifikasi ulang ke PDF
halaman 238–239 sebelum dipakai untuk alokasi anggaran per kecamatan.**

### 5.3 UMKM dan koperasi

| Indikator | Nilai | Sumber | Status |
|---|---|---|---|
| Jumlah UMKM | **45.683** | Pemkab Pringsewu via Radar Lampung | ⚠️ UNVERIFIED (media, tahun tidak pasti) |
| Koperasi aktif 2024 | **100** | PDA 2025 Tabel 9.1 (Σ cocok ✅) | ✅ |

**Koperasi aktif menurut kecamatan** ✅ (Σ = 100)

| Kecamatan | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|
| Pardasuka | 3 | 2 | 2 | 3 |
| Ambarawa | 10 | 10 | 10 | 10 |
| Pagelaran | 10 | 10 | 10 | 10 |
| Pagelaran Utara | 1 | 1 | 1 | 1 |
| Pringsewu | 30 | 33 | 34 | 33 |
| Gading Rejo | 8 | 14 | 13 | 14 |
| Sukoharjo | 16 | 14 | 14 | 14 |
| Banyumas | 7 | 7 | 7 | 7 |
| Adiluwih | 6 | 7 | 8 | 8 |
| **Total** | **91** | **98** | **99** | **100** |

> 🔢 Rasio UMKM per penduduk: 45.683 ÷ 444.834 ≈ **1 UMKM per 9,7 jiwa** — sangat tinggi; angka ini
> kemungkinan mencakup usaha mikro non‑formal. Perlakukan sebagai indikatif sampai dikonfirmasi ke
> Dinas Koperasi, UKM, Perdagangan dan Perindustrian Kab. Pringsewu.

### 5.4 Listrik ⚠️

Pelanggan listrik ULP Pringsewu 2024: **122.487** (Σ 9 kecamatan cocok persis dengan total ✅).

⚠️ **Tetapi tabel ini tidak konsisten lintas tahun**: untuk 2021–2023, Σ kecamatan (119.964 pada 2021)
**tidak** sama dengan total tercetak (155.647). Sumbernya juga berubah (PT PLN UP3 Metro untuk 2021–2023,
ULP Pringsewu untuk 2024) dan wilayah layanan PLN tidak berimpit dengan batas kecamatan.
**Jangan pakai tabel ini sebagai proksi elektrifikasi.** Persentase RT dengan akses listrik ❌ NOT FOUND.

---

## 6. Sumber batas administrasi (GeoJSON / Shapefile) — TERUJI

### 6.1 REKOMENDASI UTAMA: BIG ArcGIS REST — resmi, gratis, tanpa login, langsung GeoJSON ✅

Badan Informasi Geospasial menyediakan layanan ArcGIS REST publik yang **sudah saya uji dan berhasil**
mengembalikan tepat 131 desa dan 9 kecamatan Pringsewu.

**Level desa/kelurahan** — layer `Administrasi_AR_KelDesa_10K` (skala 1:10.000, edisi Okt 2020, EPSG:4326):

```
https://geoservices.big.go.id/rbi/rest/services/BATASWILAYAH/Administrasi_AR_KelDesa_10K/MapServer/0/query?where=WADMKK%3D%27Pringsewu%27&outFields=NAMOBJ,KDEPUM,WADMKC,WADMKD,LUASWH&returnGeometry=true&outSR=4326&f=geojson
```

- **Hasil uji:** HTTP 200, ~1,75 MB, `FeatureCollection` dengan **131 feature** ✅
- **Kode wilayah:** field `KDEPUM` berformat `18.10.xx.xxxx` — **cocok 100%** dengan 131 kode Kepmendagri 2025
  (0 selisih di kedua arah) ✅ → bisa langsung dipakai sebagai *foreign key*
- `maxRecordCount` = 4000, jadi 131 feature aman dalam satu request
- Ganti `f=geojson` → `f=json` untuk Esri JSON; `returnGeometry=false` untuk tabel atribut saja

**Level kecamatan** — layer `Administrasi_AR_Kecamatan_10K`:

```
https://geoservices.big.go.id/rbi/rest/services/BATASWILAYAH/Administrasi_AR_Kecamatan_10K/MapServer/0/query?where=WADMKK%3D%27Pringsewu%27&outFields=NAMOBJ,KDCPUM,WADMKC,WADMKK&returnGeometry=true&outSR=4326&f=geojson
```

- **Hasil uji:** HTTP 200, **9 feature**, `KDCPUM` = `18.10.01`…`18.10.09` ✅

**Untuk seluruh Provinsi Lampung**, ganti klausa `where`:
`where=WADMPR%3D%27Lampung%27`

**Field yang tersedia** (layer desa): `NAMOBJ`, `KDEPUM`, `KDEBPS`, `KDCPUM`, `KDCBPS`, `KDBBPS`, `KDPBPS`,
`WADMKD`, `WADMKC`, `WADMKK`, `WADMPR`, `LUASWH` (luas menurut peraturan, hektar), `TIPADM`, `UUPP`, `LUAS`.

> ⚠️ `KDEBPS` dan `KDCBPS` (kode BPS) **kosong/`null`** pada layer ini — hanya kode PUM (Kemendagri) yang
> terisi. Gunakan `KDEPUM`/`KDCPUM`.
> ⚠️ Geometri berbasis edisi **Oktober 2020** (referensi Permendagri 72/2019). Karena jumlah dan kode desa
> Pringsewu tidak berubah antara 2020 dan Kepmendagri 2025, ini tidak jadi masalah untuk Pringsewu —
> tetapi cek ulang bila memperluas ke kabupaten lain yang mengalami pemekaran.

### 6.2 Alternatif GitHub (gratis, tapi ada catatan)

| Repo | Isi | Format | Catatan |
|---|---|---|---|
| [`Alf-Anas/batas-administrasi-indonesia`](https://github.com/Alf-Anas/batas-administrasi-indonesia) | Provinsi, Kab/Kota, Kecamatan, Kel/Desa | SHP, KML, GeoJSON, GPKG | ✅ terverifikasi ada. Level desa & kecamatan dipecah jadi **arsip 7z multi‑part** (`Kel_Desa.7z.001`…`.007`, `Kecamatan SHP.7z.001`…`.004`) — harus diunduh semua part lalu digabung. Folder `2020/` juga punya `Batas Kecamatan SHP.zip` dan `batas_desa_shp`/`batas_desa_gpkg` yang lebih mudah dipakai. |
| [`pararawendy/border-desa-indonesia-geojson`](https://github.com/pararawendy/border-desa-indonesia-geojson) | 83.332 desa se‑Indonesia | GeoJSON (zip) | ✅ file tunggal `indonesia_villages_border.geojson.zip` — paling praktis kalau butuh nasional sekaligus |
| [`ardian28/GeoJson-Indonesia-38-Provinsi`](https://github.com/ardian28/GeoJson-Indonesia-38-Provinsi) | Provinsi + Kabupaten saja | GeoJSON | ⚠️ **hanya sampai level kabupaten** (`Kabupaten/38 Provinsi Indonesia - Kabupaten.json`) — tidak cukup untuk NADI |
| [`cahyadsn/wilayah`](https://github.com/cahyadsn/wilayah) | Kode & nama wilayah (bukan geometri) | SQL | ✅ **sumber kode wilayah yang saya pakai di dokumen ini** — Kepmendagri No. 300.2.2‑2138/2025. File: `db/wilayah.sql` |
| [`batas-admin.geoit.dev`](https://batas-admin.geoit.dev/) | Portal unduh interaktif | beragam | ⚠️ belum diuji |

**Perintah unduh langsung untuk kode wilayah** (teruji ✅):

```bash
curl -sL -o wilayah.sql https://raw.githubusercontent.com/cahyadsn/wilayah/master/db/wilayah.sql
grep -o "('18\.10[^)]*)" wilayah.sql    # → 141 baris: 1 kabupaten + 9 kecamatan + 131 desa/kelurahan
```

### 6.3 Yang TIDAK berhasil

| Sumber | Masalah |
|---|---|
| `tanahair.indonesia.go.id` / Ina‑Geoportal | ❌ tidak diuji berhasil dalam sesi ini; secara umum butuh registrasi akun untuk unduh massal |
| `kodewilayah.id` | ❌ domain tidak resolve (`ENOTFOUND`) |
| `pekon.id` | ❌ HTTP 500 |
| `emsifa.github.io/api-wilayah-indonesia` | ⚠️ redirect ke `emsifa.com`; data berbasis Permendagri 2019 (kedaluwarsa) |
| Halaman tabel BPS via WebFetch | ❌ HTTP 403 — **harus** pakai `curl` dengan `User-Agent` browser |

---

## 7. Koordinat

### 7.1 Titik pusat kabupaten dan kecamatan 🔢

Centroid dihitung dari poligon BIG (rata‑rata centroid tertimbang luas, EPSG:4326 WGS84).

| Wilayah | Kode | Latitude | Longitude |
|---|---|---|---|
| **Kabupaten Pringsewu** | 18.10 | **-5,33636** | **104,93341** |
| Pringsewu | 18.10.01 | -5,35643 | 104,96524 |
| Gading Rejo | 18.10.02 | -5,36943 | 105,02848 |
| Ambarawa | 18.10.03 | -5,41087 | 104,95014 |
| Pardasuka | 18.10.04 | -5,50645 | 104,92690 |
| Pagelaran | 18.10.05 | -5,37236 | 104,90441 |
| Banyumas | 18.10.06 | -5,29113 | 104,91433 |
| Adiluwih | 18.10.07 | -5,24862 | 105,01708 |
| Sukoharjo | 18.10.08 | -5,30244 | 104,98688 |
| Pagelaran Utara | 18.10.09 | -5,25807 | 104,83917 |

**Bounding box kabupaten** (perkiraan dari sebaran centroid desa): lat −5,51…−5,24 · lon 104,81…105,08.
Untuk peta web, `center = [-5.336, 104.933]`, `zoom ≈ 11`.

### 7.2 Centroid tiap desa/kelurahan

Tersedia lengkap untuk **131/131** wilayah di kolom `lat`/`lon` pada tabel §1.3 dan pada berkas seed
(`seed_desa_pringsewu.json` / `.csv`).

---

## 8. Implikasi untuk desain NADI

### 8.1 Skema database

1. **Kunci utama wilayah = kode Kemendagri (string, format `18.10.xx.xxxx`), bukan nama.** Ejaan berbeda di
   tiap sumber (`Gadingrejo`/`Gading Rejo`, `Adiluwih`/`Adi Luwih`, `Fajaresuk`/`Fajar Esuk`). Simpan
   `kode_desa` (13 char), `kode_kecamatan` (8 char), `kode_kabupaten` (5 char) sebagai kolom terpisah agar
   agregasi cukup lewat prefix.
2. **Simpan `status` sebagai enum `pekon` | `kelurahan`.** Bisa diturunkan dari digit pertama segmen
   terakhir (`1`=kelurahan, `2`=pekon), tapi simpan eksplisit — Pringsewu adalah satu‑satunya kecamatan
   dengan kelurahan, dan dana desa (ADP/Dana Desa) hanya berlaku untuk 126 pekon, bukan 5 kelurahan.
3. **Dua kolom populasi, bukan satu:** `penduduk_dukcapil` (444.834, ada sampai level kecamatan) dan
   `penduduk_proyeksi_bps` (429,74 ribu untuk 2025, hanya level kabupaten). Beri constraint/anotasi agar
   tidak tercampur di satu grafik.
4. **Kolom `lat`/`lon` sudah siap** untuk 131 desa + 9 kecamatan — tidak perlu geocoding eksternal.
5. **Tabel indikator harus punya kolom `status_verifikasi`** (`verified`/`derived`/`unverified`) dan
   `sumber` + `tahun`. Sekitar 30% indikator yang diminta berstatus ⚠️ atau ❌; UI harus bisa
   menampilkannya sebagai "data belum tersedia" alih‑alih 0 atau null diam‑diam.

### 8.2 Fitur model / analitik

6. **Gunakan IDM sebagai label targeting siap pakai.** 15 pekon "Berkembang" adalah daftar prioritas yang
   sudah divalidasi Kemendes, terkonsentrasi di Pagelaran Utara (7) dan Pardasuka (6).
7. **Fitur geografis yang terbukti diskriminatif:** kepadatan penduduk membentang 107 → 1.960 jiwa/km²
   (rasio 18×). Pagelaran Utara adalah *outlier* di hampir semua dimensi (25,63% luas wilayah tapi hanya
   3,79% penduduk, padi terendah, koperasi 1 unit, 7 dari 10 pekonnya "Berkembang").
8. **Kemiskinan hanya tersedia di level kabupaten, bukan desa.** Untuk peta kemiskinan per desa, NADI harus
   melakukan *small‑area estimation* memakai proksi yang tersedia per kecamatan/desa: status IDM, kepadatan,
   luas panen padi, jumlah koperasi, kelahiran hidup, komposisi agama. **Jangan mengklaim P0 per desa
   sebagai data resmi.**
9. **Sinyal deteriorasi yang layak diangkat:** (a) Gini naik 0,266 → 0,299 (2024→2025) melewati provinsi;
   (b) air layak RT miskin turun 94,27% → 89,54%; (c) stunting naik 15,8% → 19,5%; (d) pengeluaran riil
   stagnan. Kemiskinan turun, tapi kualitas penurunannya memburuk — ini narasi utama yang datanya kuat.
10. **Rantai formalitas kerja** dapat jadi fitur: 69,4% pekerja informal (kabupaten) vs 44,2% penduduk
    miskin di sektor informal — informalitas bukan penyebab tunggal kemiskinan, jadi hindari model yang
    terlalu mengandalkan variabel ini.

### 8.3 UI aplikasi

11. **Choropleth desa langsung bisa dibuat**: 131 poligon dari BIG + join `KDEPUM` ↔ `kode_desa`.
    Simpan GeoJSON hasil unduh secara lokal (~1,75 MB) — jangan panggil BIG saat runtime (tanpa SLA/CORS
    yang dijamin). Sederhanakan geometri (mis. mapshaper 5–10%) agar payload web ringan.
12. **Sediakan pemilih level: kabupaten → kecamatan → pekon.** Karena data indikator makin jarang makin
    ke bawah, UI harus otomatis menurunkan set indikator yang ditampilkan per level.
13. **Beri label sumber + tahun di setiap kartu angka.** Dokumen ini mencampur 2023, 2024, dan 2025 —
    menampilkannya berdampingan tanpa label akan menyesatkan.
14. **Tampilkan air *layak* dan air *aman* berdampingan** (95,64% vs 41,31%). Ini satu‑satunya indikator di
    mana selisih definisi mengubah kesimpulan kebijakan secara total.

---

## 9. Daftar sumber

**Dokumen resmi yang berhasil diunduh dan diekstrak penuh:**

1. BPS Kabupaten Pringsewu, **Kabupaten Pringsewu Dalam Angka 2025** (Vol. 14, Katalog 1102001.1810,
   ISSN 2654‑6736, 428 hlm, terbit 28 Feb 2025) —
   <https://pringsewukab.bps.go.id/id/publication/2025/02/28/92289dcccc7d51700b126fc9/kabupaten-pringsewu-dalam-angka-2025.html>
2. BPS Kabupaten Pringsewu, **Potret Kemiskinan Kabupaten Pringsewu 2025** (Vol. 1, terbit 17 Nov 2025) —
   <https://pringsewukab.bps.go.id/id/publication/2025/11/17/303bdc8bbabe449d666ded91/potret-kemiskinan-kabupaten-pringsewu-2025.html>
3. **Kepmendagri No. 300.2.2‑2138 Tahun 2025** tentang Kode dan Data Wilayah, via
   <https://github.com/cahyadsn/wilayah> (`db/wilayah.sql`)
4. **Badan Informasi Geospasial**, layanan ArcGIS REST BATASWILAYAH —
   <https://geoservices.big.go.id/rbi/rest/services/BATASWILAYAH>

**Tabel statistik dinamis BPS (diakses via curl + User‑Agent browser):**

5. Angka Kemiskinan Kab. Pringsewu — <https://pringsewukab.bps.go.id/id/statistics-table/2/MjA5IzI=/angka-kemiskinan-kabupaten-pringsewu.html>
6. Koefisien Gini Kab. Pringsewu — <https://pringsewukab.bps.go.id/id/statistics-table/2/MjI1IzI=/koefisien-gini-gini-ratio.html>
7. Gini Ratio Kabupaten/Kota, BPS Prov. Lampung — <https://lampung.bps.go.id/id/statistics-table/2/NjMyIzI=/gini-ratio-kabupaten-kota.html>
8. Indikator SDGs 6.1.1(a) air minum layak — <https://pringsewukab.bps.go.id/id/statistics-table/2/NjYzIzI=/-indikator-6-1-1-a-persentase-rumah-tangga-yang-menggunakan-sumber-air-minum-layak.html>
9. RT dengan akses air minum aman — <https://pringsewukab.bps.go.id/id/statistics-table/2/NzkzIzI=/persentase-rumah-tangga-yang-memiliki-akses-terhadap-air-minum-aman-di-kabupaten-pringsewu.html>
10. RT dengan akses kecukupan air minum — <https://pringsewukab.bps.go.id/id/statistics-table/2/Nzg5IzI=/persentase-rumah-tangga-yang-memiliki-akses-terhadap-kecukupan-air-minum-di-kabupaten-pringsewu.html>

**Sumber sekunder (⚠️ perlu konfirmasi):** Radar Lampung (UMKM 45.683), inilampung.com & lampungcorner.com
(stunting), Profil Kesehatan Dinkes Pringsewu 2024 via pencarian (AKI/AKB), Lampungpro/BPJS (JKN 98,29%).

---

## 10. Ringkasan kesenjangan data (untuk tindak lanjut)

| # | Yang belum ada | Cara mendapatkan |
|---|---|---|
| 1 | Gini Ratio 2016–2023 | WebAPI BPS (`var=225`, `domain=1810`) dengan API key dari webapi.bps.go.id |
| 2 | HLS, RLS, pengeluaran per kapita disesuaikan | BRS IPM BPS / publikasi IPM Kabupaten/Kota |
| 3 | Jumlah rumah tangga / KK | Disdukcapil Pringsewu, atau Susenas/Long Form SP2020 |
| 4 | Sanitasi layak (semua RT) | Indikator SDGs 6.2.1(b) — slug tabel BPS Pringsewu belum ditemukan |
| 5 | Akses listrik (% RT) | Susenas / Indikator SDGs 7.1.1 |
| 6 | RTLH | Dinas Perumahan & Permukiman Kab. Pringsewu; data.go.id belum memuat Pringsewu |
| 7 | Stunting resmi per kecamatan | Dinkes Pringsewu (ePPGBM); angka SSGI hanya level kabupaten |
| 8 | Garis kemiskinan 2015, 2016, 2025 | Potret Kemiskinan (Gambar 2.1) versi teks, atau WebAPI BPS |
| 9 | Nama kabupaten untuk sebaran P0 Lampung 2025 | BPS *Data dan Informasi Kemiskinan Kabupaten/Kota 2025* (terbit 28 Nov 2025) |
| 10 | Padi per kecamatan — konfirmasi pemetaan baris | PDA 2025 hlm. 238–239 (cek visual PDF) |

---

## Lampiran — berkas seed yang dihasilkan

Berkas siap impor tersimpan di `docs/research/pringsewu-seed/`:

| Berkas | Isi | Ukuran |
|---|---|---|
| `seed_desa_pringsewu.csv` | 131 baris — kolom `kode`, `kode_kec`, `kecamatan`, `nama`, `status`, `lat`, `lon`, `luas_ha_big` | 10 KB |
| `seed_desa_pringsewu.json` | sama, format JSON array | 27 KB |
| `pringsewu_desa.geojson` | 131 poligon batas desa dari BIG, EPSG:4326 | 1,75 MB |

Verifikasi isi seed: 131 baris · 126 pekon + 5 kelurahan · Gading Rejo 23, Pagelaran 22, Sukoharjo 16,
Pringsewu 15, Pardasuka 13, Adiluwih 13, Banyumas 11, Pagelaran Utara 10, Ambarawa 8 ✅

Contoh 3 baris pertama:

```csv
kode,kode_kec,kecamatan,nama,status,lat,lon,luas_ha_big
18.10.01.1001,18.10.01,Pringsewu,Fajaresuk,kelurahan,-5.35398,104.95683,408.71
18.10.01.1002,18.10.01,Pringsewu,Pringsewu Utara,kelurahan,-5.35018,104.98053,150.49
18.10.01.1003,18.10.01,Pringsewu,Pringsewu Selatan,kelurahan,-5.3612,104.97126,176.95
```

> Sebelum dipakai di peta web, sederhanakan `pringsewu_desa.geojson` (mis. `mapshaper -simplify 8%`)
> agar payload turun dari ~1,75 MB ke ratusan KB.
