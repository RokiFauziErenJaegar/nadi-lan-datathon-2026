# 05 — Lanskap Sistem Informasi Kemiskinan yang Sudah Ada
### Basis Faktual untuk Klaim Kebaruan NADI (LAN Datathon)

> **Tanggal riset:** 25 Agustus 2026
> **Tujuan dokumen:** memastikan setiap klaim "baru" dalam NADI dapat dipertahankan di depan dewan juri. Dokumen ini sengaja ditulis **melawan** kepentingan tim: mencari sistem yang sudah melakukan apa yang NADI klaim, agar kita tidak mengklaim berlebihan.
> **Aturan main dokumen ini:** tidak ada angka yang dikarang. Jika sesuatu tidak berhasil diverifikasi, ditulis eksplisit sebagai *TIDAK TERVERIFIKASI*.

---

## 0. Ringkasan Eksekutif (baca ini kalau cuma punya 3 menit)

**Temuan paling penting untuk strategi presentasi:**

1. **Pembanding terdekat NADI bukan SIKS-NG, melainkan SEPAKAT (Bappenas).** SEPAKAT sudah punya modul analisis, **perencanaan yang menghasilkan opsi intervensi dengan penargetan sasaran dan lokasi**, penganggaran, pemantauan, dan evaluasi. Jangan klaim "belum ada sistem yang menghubungkan analisis ke perencanaan intervensi" — itu salah dan mudah dipatahkan.
2. **Klaim "prediksi kemiskinan itu baru" juga berbahaya.** Proxy Means Test (PMT) yang menjadi dasar P3KE, DTSEN, Listahanan (Filipina), NSER (Pakistan), dan SISBEN (Kolombia) **adalah model statistik prediktif**. Yang membedakan NADI harus dirumuskan lebih presisi: bukan "prediksi", tapi **prediksi risiko dinamis ke depan (siapa yang akan jatuh/naik), bukan pemeringkatan kesejahteraan saat ini**.
3. **Celah nyata yang tidak ditemukan di sistem eksisting Indonesia (berdasarkan bukti publik):**
   - Penjelasan per-keluarga (*explainability* tingkat individu: "kenapa keluarga ini ditandai berisiko") yang ditampilkan ke operator dan warga.
   - **Loop tertutup**: prediksi → rekomendasi intervensi spesifik → penugasan ke OPD tertentu → pelacakan *outcome* keluarga → umpan balik ke model.
   - Simulasi kebijakan *what-if* pada level keluarga/anggaran.
   - Audit keadilan (*fairness audit*) dan mekanisme keberatan yang sejalan dengan **UU PDP Pasal 10**.
4. **Ada risiko reputasi besar yang harus diantisipasi juri:** SyRI (Belanda) dilarang pengadilan, Robodebt (Australia) berujung Royal Commission dan ganti rugi ratusan juta dolar, Social Card (Serbia) didokumentasikan Amnesty International memperparah kemiskinan Roma. Juri yang paham isu ini akan bertanya: *"Apa bedanya NADI dari SyRI?"* Siapkan jawabannya (lihat Bagian G).
5. **Indonesia baru saja mengganti fondasi datanya.** DTKS sudah digantikan/dilebur ke **DTSEN** berdasarkan **Inpres No. 4 Tahun 2025**, dikelola BPS, per 10 Juli 2026 mencakup **290,13 juta record individu dan 95,98 juta record keluarga**. NADI harus diposisikan sebagai *lapisan analitik di atas DTSEN*, bukan sebagai pesaing pendataan.

---

## 1. Metodologi & Keterbatasan Riset (transparansi)

**Yang dilakukan:** ±20 pencarian web dalam Bahasa Indonesia dan Inggris, plus pengambilan langsung (WebFetch) terhadap sumber primer yang dapat diakses.

**Yang GAGAL diambil (jujur, jangan disembunyikan dari juri jika ditanya):**

| Sumber | Status | Dampak |
|---|---|---|
| `sepakat.bappenas.go.id/wiki/*` | **HTTP 403** untuk semua percobaan | Deskripsi modul SEPAKAT bersandar pada kutipan sekunder (Pemkab Tuban, Kominfo, hasil indeks yang mengutip wiki SEPAKAT). Fitur mutakhir SEPAKAT 2025–2026 **TIDAK TERVERIFIKASI**. |
| `www.bappenas.go.id/berita/...` | **HTTP 403** | idem |
| `bps.go.id` (halaman berita DTSEN) | **HTTP 403** | Angka DTSEN diambil dari pemberitaan yang mengutip BPS (Beritasatu, Media Indonesia), bukan dari halaman BPS langsung. |
| `dtsen.data.go.id` | Gagal parse header | Fitur portal DTSEN **TIDAK TERVERIFIKASI** secara langsung. |
| `kominfo.go.id` / `ekon.go.id` | DNS / sertifikat gagal | |
| Teks lengkap SE Kominfo No. 9/2023 | Hanya metadata yang didapat | Isi pasal per pasal **TIDAK TERVERIFIKASI**; yang terverifikasi adalah struktur tiga kebijakan dan daftar nilai etika. |
| Statistik jumlah pengguna aplikasi Cek Bansos | **Tidak ditemukan** (kuota pencarian habis) | Jangan sebut angka unduhan/pengguna dalam slide. |
| Cakupan SEPAKAT terkini (2025–2026) | **Tidak ditemukan** | Angka 129 kab/kota + 7 provinsi berasal dari sumber era pemulihan COVID; beri label tahun. |

**Prinsip penilaian dalam tabel perbandingan:** kolom diisi "Tidak" hanya bila tidak ditemukan bukti publik atas fitur tersebut. Ini **bukan** bukti absolut ketiadaan. Dalam slide, gunakan frasa *"tidak ditemukan bukti publik"*, bukan *"tidak punya"*.

---

# BAGIAN A — LANSKAP INDONESIA

## A.1 SIKS-NG (Sistem Informasi Kesejahteraan Sosial – Next Generation)

| Aspek | Isi |
|---|---|
| **Pemilik** | Kementerian Sosial RI (dikembangkan ±2017, penerus SIKS berbasis offline) |
| **Fungsi utama** | Tulang punggung pengelolaan data penerima bantuan sosial (dulu DTKS): pendataan, verifikasi & validasi (verivali), pengusulan, finalisasi data penerima |
| **Pengguna** | Operator desa/kelurahan, Dinas Sosial kabupaten/kota & provinsi, pendamping sosial. **Masyarakat umum tidak punya akses login** — hanya lewat portal `cekbansos.kemensos.go.id` / aplikasi Cek Bansos |

**Fitur konkret yang terverifikasi:**
- Modul **verifikasi & validasi (verivali)** — cross-check data terhadap referensi lain.
- Fitur **Usul** dan **Sanggah** (usulan warga baru; sanggahan atas penerima yang dinilai tidak layak).
- **Pengecekan Kelayakan Mandiri** yang terhubung ke data **BPJS Ketenagakerjaan** dan **AHU** (Ditjen Administrasi Hukum Umum) untuk mendeteksi status pekerjaan/kepemilikan badan usaha KPM.
- Siklus operasional: operator wajib melakukan **finalisasi pemutakhiran paling lambat tanggal 25 setiap bulan**.
- Versi mobile Android untuk verifikasi lapangan (dikenal sebagai SIKS Mobile / SIKS-Dataku).

**Alur usulan/sanggah (rantai kelembagaan):**
Usulan warga (mandiri via Cek Bansos, atau lewat perangkat desa) → **Musyawarah Desa/Kelurahan (Musdes/Muskel)** → input operator desa ke SIKS-NG → verifikasi Dinas Sosial → **penetapan melalui SK Bupati/Wali Kota** → pengiriman ke Kemensos → sinkronisasi ke basis data pusat.

**YANG TIDAK DILAKUKAN SIKS-NG (celah untuk NADI):**
- ❌ **Tidak ada prediksi risiko.** SIKS-NG adalah sistem *pencatatan dan verifikasi*, bukan sistem analitik. Tidak ditemukan bukti publik adanya model prediktif di dalamnya.
- ❌ **Tidak ada explainability.** Karena tidak ada model, tidak ada penjelasan skor. Kelayakan ditentukan aturan + verifikasi manusia di lapangan.
- ❌ **Tidak ada rekomendasi intervensi lintas OPD.** Cakupannya program-program Kemensos (PKH, BPNT/Sembako, dsb.), bukan pendidikan (Disdik), kesehatan (Dinkes), perumahan (Perkim), atau ketenagakerjaan (Disnaker).
- ❌ **Tidak ada simulasi kebijakan.**
- ⚠️ **Monitoring: hanya output, bukan outcome.** Yang dipantau adalah status penyaluran bantuan, bukan apakah kondisi kesejahteraan keluarga membaik.

**Kelemahan yang terdokumentasi dalam literatur akademik:** akurasi data, keterlambatan verifikasi, keterbatasan infrastruktur TIK di tingkat desa, dan kesenjangan koordinasi antarinstansi.

**Sumber:**
- https://journal.unismuh.ac.id/index.php/kolaborasi/article/download/16182/7811 (jurnal — alur pengusulan & kendala)
- https://bams.blog/hukum-pemerintahan/siks-ng-cara-kerja-dan-bedanya-dengan-aplikasi-cek-bansos/
- https://ppid.pariamankota.go.id/home/details/724-banner-pengusulan-verifikasi-dan-validasi-data-dtks-melalui-aplikasi-siks-ng.html
- https://www.kapanlagi.com/feeds/cara-menggunakan-aplikasi-siks-ng-untuk-operator-desa-pendamping-sosial-dan-masyarakat-21a155f62b.html
- https://id.scribd.com/presentation/615215709/Verifali-Kelayakan-Data-KPM-Di-SIKS-NG

---

## A.2 Aplikasi Cek Bansos (kanal warga)

| Aspek | Isi |
|---|---|
| **Pemilik** | Kementerian Sosial RI |
| **Kanal** | Aplikasi Android + portal `cekbansos.kemensos.go.id` |
| **Pengguna** | Masyarakat umum |

**Tiga fungsi utama (terverifikasi):**
1. **Cek status** penerima bansos berdasarkan wilayah + nama sesuai KTP.
2. **Usul** — mengusulkan diri/keluarga/tetangga yang layak tapi belum terdaftar (isi NIK, nama sesuai KTP, alamat lengkap, alasan kelayakan).
3. **Sanggah** — menyampaikan keberatan atas penerima yang dinilai tidak layak (pilih ikon, isi alasan, pernyataan, kirim tanggapan).

Laporan usul/sanggah diproses tim verifikator dan ditindaklanjuti dengan pengecekan lapangan; hasil yang valid disinkronkan ke basis data oleh Dinas Sosial.

**YANG TIDAK DILAKUKAN:**
- ❌ Tidak ada prediksi, skor risiko, atau penjelasan mengapa seseorang tidak terdaftar.
- ❌ Tidak ada rekomendasi program lain yang mungkin cocok untuk warga tersebut.
- ❌ Tidak ditemukan bukti publik adanya *tracking* status tindak lanjut usulan bagi pengusul (semacam sistem tiket dengan SLA).
- ❌ Tidak ada monitoring outcome.

**Nilai untuk NADI:** Cek Bansos membuktikan bahwa **partisipasi warga (usul/sanggah) sudah menjadi norma yang diterima secara institusional di Indonesia**. NADI tidak perlu "menemukan" partisipasi warga — NADI harus menghubungkannya ke loop analitik (usulan warga sebagai sinyal untuk model; sanggahan sebagai mekanisme koreksi/keberatan sesuai UU PDP Pasal 10).

**Sumber:**
- https://www.komdigi.go.id/berita/artikel/detail/aplikasi-cek-bansos-inovasi-kementerian-sosial-yang-libatkan-masyarakat-untuk-pengelolaan-bansos-tepat-sasaran
- https://news.detik.com/berita/d-8129874/cara-usul-dan-sanggah-bansos-di-aplikasi-cek-bansos-kemensos
- https://www.detik.com/sumbagsel/berita/d-8581005/aplikasi-cek-bansos-cara-unduh-pantau-penerima-serta-fitur-usul-sanggah
- https://www.detik.com/jatim/berita/d-8608452/aplikasi-cek-bansos-kemensos-untuk-apa-ini-fungsi-dan-caranya

---

## A.3 SEPAKAT (Bappenas) — **PEMBANDING PALING DEKAT, TELITI BAIK-BAIK**

| Aspek | Isi |
|---|---|
| **Nama** | Sistem Perencanaan, Penganggaran, Pemantauan, Analisis dan Evaluasi Kemiskinan Terpadu. (Catatan: penamaan bervariasi antar sumber resmi; situsnya sendiri kini juga memakai frasa *"Sistem Perencanaan Kolaboratif dan Analisis Data Terpadu"*.) |
| **Pemilik** | Kementerian PPN/Bappenas |
| **Mitra pengembang** | Pemerintah Australia melalui program **KOMPAK**, dan **Bank Dunia** |
| **Tahun rilis** | **2018** |
| **Cakupan (sumber sekunder, era pemulihan COVID)** | **129 kabupaten/kota dan 7 provinsi** — *cakupan terkini TIDAK TERVERIFIKASI* |
| **URL** | https://sepakat.bappenas.go.id/ |

**Modul yang terverifikasi (kutipan dari sumber yang mengutip wiki SEPAKAT):**

| Modul | Fungsi (kutipan) |
|---|---|
| **Analisis** | *"menganalisa data untuk kebutuhan diagnosa kemiskinan yang meliputi kemiskinan, ketenagakerjaan, pelayanan dasar, perlindungan sosial, perekonomian daerah dan anggaran daerah"* — memuat informasi ekonomi produktif & ketenagakerjaan (efek **Pertumbuhan**) serta pelayanan dasar & akses (efek **Redistribusi**) |
| **Perencanaan** | *"memberikan analisa perencanaan menggunakan **pohon masalah** dan menghasilkan **opsi intervensi** penanggulangan kemiskinan dengan **penargetan sasaran dan lokasi yang spesifik**"* |
| **Penganggaran** | *"analisa anggaran dan pengalokasian anggaran berdasarkan hasil analisa dari modul analisis dan modul perencanaan"* |
| **Pemantauan** | *"melihat kinerja penanggulangan kemiskinan daerah berdasarkan target daerah dalam dokumen **RPJMD** atau target dalam **SDGs**"* |
| **Evaluasi** | *"menilai kinerja penanggulangan kemiskinan daerah berdasarkan **dekomposisi pertumbuhan dan redistribusi**"* |
| **Pengetahuan / Wiki** | User's guide, panduan umum, *knowledge management* riset kemiskinan |

**Integrasi lintas sistem (SEPAKAT sudah interoperabel):** SIPD (Kemendagri), SIKD (Kemenkeu), InaRisk (BNPB); hasil analisisnya juga dipadukan dengan analisis SIMPEL (Kemendagri–TNP2K) untuk penyusunan dokumen **RPKD** (Rencana Penanggulangan Kemiskinan Daerah). SEPAKAT juga memiliki bagian khusus **REGSOSEK**.

**Pemanfaatan nyata:** penyusunan RPJMD, RKPD, strategi penanggulangan kemiskinan daerah, dan laporan pelaksanaan. Tersedia varian **SEPAKAT Desa/Kelurahan** sehingga pemda dan desa dapat mengakses data makro tanpa harus menginput dan memverifikasi data sendiri.

**YANG TIDAK DILAKUKAN SEPAKAT (berdasarkan bukti publik yang berhasil dikumpulkan):**
- ❌ **Tidak ada prediksi risiko keluarga.** Analisisnya bersifat **deskriptif dan diagnostik** (statistik makro/mikro, dekomposisi *growth–redistribution*), bukan *forecasting* siapa yang akan jatuh miskin.
- ❌ **Tidak ada explainability model** — karena tidak ada model prediktif per-keluarga yang perlu dijelaskan.
- ⚠️ **Rekomendasi intervensi: ADA, tapi pada level kebijakan/wilayah.** Modul Perencanaan menghasilkan "opsi intervensi" berbasis pohon masalah dengan target sasaran & lokasi — **bukan rekomendasi per-keluarga dan bukan penugasan ke OPD tertentu**. **Jangan klaim NADI yang pertama merekomendasikan intervensi.**
- ⚠️ **Simulasi: parsial.** Modul Penganggaran melakukan pengalokasian anggaran berdasarkan hasil analisis. Bukti publik adanya **simulasi skenario *what-if*** ("kalau anggaran X dipindah ke program Y, berapa perubahan proyeksi kemiskinan?") **TIDAK DITEMUKAN**.
- ✅ **Monitoring outcome: ADA.** Modul Pemantauan melacak capaian terhadap target RPJMD/SDGs; modul Evaluasi menilai kinerja via dekomposisi. **Ini kekuatan SEPAKAT yang harus diakui di slide.** Namun pemantauannya pada level indikator agregat daerah, bukan *outcome* per keluarga penerima.

> **⚠️ PERINGATAN UNTUK TIM NADI:** Jika slide menulis *"belum ada sistem yang menghubungkan data kemiskinan ke perencanaan dan penganggaran"*, juri yang mengenal SEPAKAT akan langsung mematahkannya. Rumuskan ulang menjadi: *"SEPAKAT sudah menjembatani data makro ke perencanaan wilayah; yang belum ada adalah jembatan dari **prediksi risiko per keluarga** ke **penugasan intervensi ke OPD** dengan **pelacakan outcome keluarga**."*

**Sumber:**
- https://sepakat.bappenas.go.id/ (situs resmi; wiki mengembalikan 403 untuk pengambilan otomatis)
- https://tubankab.go.id/entry/slug-34803851b51c026e1075f0f86e2903a9 (kutipan lima fungsi + angka 129 kab/kota, 7 provinsi)
- https://www.bappenas.go.id/berita/sepakat-mempercepat-penanggulangan-kemiskinan-tepat-sasaran-dan-guna
- https://sepakat.bappenas.go.id/wiki/index.php/Mengenal_Sepakat
- https://sepakat.bappenas.go.id/wiki/Pendahuluan_Modul_Evaluasi
- https://sepakat.bappenas.go.id/wiki/Pemanfaatan_Sepakat
- https://sepakat.bappenas.go.id/wiki/Mengenal_Sepakat_Desa_Kelurahan
- https://sepakat.bappenas.go.id/wiki/Alur_Kerja_Penganggaran
- https://sepakat.bappenas.go.id/regsosek/faq/regsosek/registrasi-sosial-ekonomi
- https://bappelitbangda.sumbawakab.go.id/berita/id/51/pemanfaatan-sepakat--sistem-perencanaan--penganggaran--pemantauan--analisis-dan-evaluasi-kemiskinan-terpadu--pemahaman-pemerintah-daerah-terhadap-kebijakan-teknis-did.html
- https://www.kominfo.go.id/content/detail/32195/pemanfaatan-sepakat-untuk-pengentasan-kemiskinan-pemulihan-sosial-ekonomi-daerah-dan-mitigasi-covid-19/0/artikel_gpr

---

## A.4 DTSEN — Data Tunggal Sosial dan Ekonomi Nasional (**fondasi data terbaru, WAJIB dipakai NADI**)

| Aspek | Isi |
|---|---|
| **Dasar hukum** | **Instruksi Presiden No. 4 Tahun 2025** |
| **Pengelola** | **Badan Pusat Statistik (BPS)** menyusun & mengelola; K/L dan pemda berperan sebagai penyedia data dan pemutakhir |
| **Menggantikan/melebur** | **DTKS** (Kemensos), **P3KE** (Kemenko PMK/BKKBN), dan **Regsosek** (BPS) menjadi satu rujukan |
| **Cakupan (per 10 Juli 2026, DTSEN Versi 3 Tahun 2026)** | **290,13 juta record individu** dan **95,98 juta record keluarga** |
| **Portal** | https://dtsen.data.go.id/ (*fitur portal TIDAK TERVERIFIKASI — gagal diambil*) |

**Isi data:** identitas individu & keluarga terpadu yang sudah dipadankan dengan **data Dukcapil**; kondisi ekonomi rumah tangga, kepemilikan aset, sumber pendapatan; kondisi sosial keluarga (akses kesehatan, pendidikan, kesejahteraan sosial); serta **desil kemiskinan / peringkat kesejahteraan keluarga** yang dimutakhirkan berkala.

**Tentang DESIL (penting untuk framing NADI):** desil adalah **peringkat kesejahteraan relatif** — seluruh keluarga diurutkan lalu dibagi 10 kelompok masing-masing ±10%. Desil 1 = 10% terbawah, desil 10 = 10% teratas. BPS menekankan desil **bukan ukuran absolut kemiskinan atau nominal kekayaan tertentu**, dan bukan semata berdasarkan penghasilan.

**Pemutakhiran:** data administrasi, hasil sensus & survei, pemutakhiran K/L dan pemda, **ground check** lapangan, serta pembaruan yang disampaikan masyarakat melalui kanal yang tersedia.

**YANG TIDAK DILAKUKAN DTSEN:**
- ⚠️ **Prediktif? Secara teknis SETENGAH YA — harus jujur disampaikan.** Pendahulunya (P3KE) secara eksplisit memakai **Proxy Means Testing (PMT)** yang mengacu pada Susenas untuk menaksir tingkat kesejahteraan. PMT **adalah model statistik prediktif** (memprediksi konsumsi/kesejahteraan dari variabel proksi). **Jangan klaim "sistem yang ada tidak prediktif sama sekali."** Klaim yang aman: *"yang ada memprediksi **kondisi saat ini**; NADI memprediksi **perubahan risiko ke depan**."*
- ❌ **Tidak ada explainability per keluarga.** Tidak ditemukan mekanisme publik yang menjelaskan ke keluarga/operator: "Anda di desil 4 karena variabel A, B, C."
- ❌ **Tidak ada rekomendasi intervensi lintas OPD** — DTSEN adalah *registry*, bukan sistem perencanaan.
- ❌ **Tidak ada simulasi kebijakan.**
- ❌ **Tidak ada monitoring outcome keluarga.**

**Sumber:**
- https://dtsen.data.go.id/
- https://www.bps.go.id/en/news/2026/08/22/938/dtsen-jadi-rujukan-bersama--bps-jelaskan-arti-desil.html
- https://www.beritasatu.com/nasional/3021260/bps-data-desil-sudah-mencakup-29013-juta-individu
- https://mediaindonesia.com/ekonomi/924777/bps-jelaskan-fungsi-desil-dalam-data-tunggal-sosial-ekonomi-nasional
- https://dinsos.jatimprov.go.id/detail-berita-publik/dtks-dihapus-ganti-dtsen-data-tunggal-sosial-ekonomi-nasional-implementasi-inpres-no-4-tahun-2025
- https://dinsos.bulelengkab.go.id/informasi/detail/berita/60_data-tunggal-sosial-dan-ekonomi-nasional-dtsen

---

## A.5 P3KE & Regsosek (pendahulu DTSEN — bukti PMT sudah dipakai secara nasional)

**P3KE (Pensasaran Percepatan Penghapusan Kemiskinan Ekstrem)**
- Sumber data: **Pendataan Keluarga BKKBN 2021**. Dasar penggunaan: **Inpres No. 4 Tahun 2022**.
- Metode: **Proxy-Means Testing (PMT)** dengan acuan data makro **Susenas**, memperhitungkan perbedaan karakteristik tiap kabupaten/kota.
- Output: pemeringkatan **desil 1–10**; intervensi kemiskinan ekstrem umumnya menyasar **desil 1–4**.
- ❌ Tidak ada explainability, rekomendasi intervensi lintas OPD, simulasi, atau monitoring outcome.
- **Sumber:** https://data.go.id/dataset/dataset/data-p3ke | https://katalog.data.go.id/dataset/data-p3ke | https://data.go.id/dataset/dataset/data-pensasaran-percepatan-penghapusan-kemiskinan-ekstrem-p3ke

**Regsosek (Registrasi Sosial Ekonomi) 2022 — BPS**
- Pendataan awal **15 Oktober – 14 November 2022**, serentak di **514 kabupaten/kota**, mencakup **seluruh keluarga**.
- Cakupan variabel: kondisi sosioekonomi demografis, perumahan & sanitasi/air bersih, kepemilikan aset, kerentanan kelompok penduduk khusus, **informasi geospasial**, tingkat kesejahteraan, dan informasi sosial ekonomi lainnya.
- Prinsip pengelolaan: integritas dan **interoperabilitas**, terhubung dengan data K/L dan pemda hingga desa/kelurahan.
- ❌ Kegiatan pendataan, bukan sistem analitik. Tidak ada prediksi risiko ke depan, XAI, rekomendasi lintas OPD, simulasi, atau monitoring outcome.
- **Sumber:** https://jabar.bps.go.id/en/news/2022/10/15/535/pendataan-awal-registrasi-sosial-ekonomi-dimulai.html | https://sepakat.bappenas.go.id/regsosek/faq/regsosek/registrasi-sosial-ekonomi | https://kapuaskab.bps.go.id/en/news/2022/09/12/54/pendataan-awal-registrasi-sosial-ekonomi--regsosek--2022.html

---

## A.6 Satu Data Indonesia & Portal data.go.id

| Aspek | Isi |
|---|---|
| **Dasar hukum** | **Perpres No. 39 Tahun 2019** tentang Satu Data Indonesia (ditetapkan 17 Juni 2019) |
| **Definisi** | Kebijakan tata kelola data pemerintah untuk menghasilkan data yang **akurat, mutakhir, terpadu, dapat dipertanggungjawabkan**, serta mudah diakses dan dibagipakaikan antar-Instansi Pusat dan Daerah |
| **Empat prinsip** | (1) memenuhi **Standar Data**; (2) memiliki **Metadata**; (3) memenuhi kaidah **Interoperabilitas Data**; (4) menggunakan **Kode Referensi dan/atau Data Induk** |
| **Peran kunci** | **Walidata** — mengumpulkan, memeriksa kesesuaian, mengelola data dari Produsen Data, dan menyebarluaskannya lewat Portal SDI |
| **Portal** | https://data.go.id/ dan https://katalog.data.go.id/ |

**Angka konektivitas yang terverifikasi (kondisi 2022 — WAJIB beri label tahun bila dipakai di slide):** **48 dari 83** portal instansi pemerintah pusat (**58%**) telah terhubung ke portal SDI; **26 dari 38 provinsi** memiliki portal SDI; **95 dari 514 kabupaten/kota**. *Jumlah dataset terkini TIDAK TERVERIFIKASI — portal sedang dalam proses kurasi.*

**YANG TIDAK DILAKUKAN:** Portal katalog data. ❌ Bukan sistem analitik: tidak ada prediksi, XAI, rekomendasi, simulasi, atau monitoring outcome.

**Implikasi untuk NADI:** kepatuhan pada Standar Data + Metadata + Kode Referensi Perpres 39/2019 adalah **syarat kelayakan adopsi**, bukan fitur pembeda. Sebutkan sebagai *compliance*, bukan sebagai inovasi.

**Sumber:**
- https://www.hukumonline.com/klinik/a/dasar-hukum-prinsip-satu-data-indonesia-lt5d19da645ce15/
- https://www.jogloabang.com/teknologi/perpres-39-2019-satu-data-indonesia
- https://data.go.id/ | https://data.go.id/instantion | https://katalog.data.go.id/dataset/

---

## A.7 SIGA (Sistem Informasi Keluarga) — BKKBN / Kemendukbangga

| Aspek | Isi |
|---|---|
| **Pemilik** | Pusat Data dan Teknologi Informasi **Kemendukbangga/BKKBN** (Jl. Permata No. 1, Halim Perdanakusuma, Jakarta Timur) |
| **Portal** | https://siga.kemendukbangga.go.id/ |
| **Fungsi** | Mengubah data keluarga menjadi informasi untuk perencanaan, pelaksanaan, dan evaluasi program Bangga Kencana — "pintu satu data keluarga Indonesia" |

**Subsistem yang terintegrasi:** Pelayanan Kontrasepsi; Pengendalian Lapangan; **Pendataan Keluarga (PK)**; **Keluarga Berisiko Stunting (KRS)**; Manajemen; Pelayanan Publik (**SIGA Mobile**).

**Kategori dataset yang terverifikasi** (rentang **2021–2026**, dapat difilter per provinsi & kabupaten, dan per semester untuk KRS):
1. Cakupan
2. Indikator Kependudukan
3. Indikator Keluarga Berencana
4. Indikator Pembangunan Keluarga
5. **Keluarga Berisiko Stunting**

**Variabel skrining Keluarga Berisiko Stunting (terverifikasi):**
- Akses/kepemilikan **sumber air minum layak** (air kemasan/isi ulang, ledeng/PAM, sumur bor/pompa, sumur terlindung, mata air terlindung)
- **Fasilitas sanitasi/jamban** selain jamban sendiri atau jamban bersama komunal berleher angsa dengan tangki septik/IPAL
- Skrining **"4 Terlalu"** dalam kehamilan/persalinan: terlalu muda, terlalu tua, terlalu dekat jaraknya, terlalu banyak

**Dasar kebijakan:** Perpres No. 72 Tahun 2021 tentang Percepatan Penurunan Stunting — penyediaan data keluarga berisiko stunting adalah salah satu dari **5 kegiatan prioritas RAN PASTI**.

**YANG TIDAK DILAKUKAN / NUANSA PENTING:**
- ⚠️ **SIGA MELAKUKAN "penandaan risiko" — tapi berbasis ATURAN, bukan model prediktif.** Ini contoh Indonesia yang paling dekat dengan *risk flagging*. **Akui ini di slide.** Bedanya: kriteria KRS bersifat deterministik dan sudah ditetapkan; NADI mengusulkan model yang belajar dari data dan memberi probabilitas.
- ✅ **Explainability-nya justru sempurna secara trivial** — karena berbasis aturan eksplisit, siapa pun bisa tahu kenapa suatu keluarga ditandai. **Ini standar yang harus disamai/dikalahkan NADI**, bukan celah. Jika NADI memakai model kompleks, NADI justru *berutang* penjelasan yang setara.
- ❌ Tidak ada rekomendasi intervensi lintas OPD terotomasi, simulasi kebijakan, atau prediksi risiko kemiskinan.
- ⚠️ Ada mekanisme **verifikasi & validasi (verval) KRS** di lapangan — bentuk umpan balik data, tapi bukan monitoring outcome keluarga secara longitudinal.

**Sumber:**
- https://siga.kemendukbangga.go.id/dataset
- https://kalteng.kemendukbangga.go.id/posts/03897a4c-e899-401b-9400-47bd0890f088-siga-sistem-informasi-keluarga-sebagai-pintu-satu-data-keluarga-indonesia
- https://siga-api-gateway.bkkbn.go.id/landing-page-be-v2/downloadFile/METADATA_KEGIATAN_PK21_final.pdf (Buku Metadata Pendataan Keluarga 2021)
- https://siga-api-gateway.bkkbn.go.id/landing-page-be-v2/downloadFile/STANDAR%20DATA%20VERVAL%20KRS%202022.pdf
- https://docu.bkkbndiy.id/wp-content/uploads/2024/05/BUKU-SAKU-KATALOG-DATA-RUTIN-SISTEM-INFORMASI-KELUARGA-PROGRAM-BANGGA-KENCANA_FINAL-1.pdf

---

## A.8 SIM-PKH / e-PKH (Program Keluarga Harapan)

| Aspek | Isi |
|---|---|
| **Pemilik** | Kementerian Sosial RI |
| **Sejarah** | Pedoman Operasional SIM-PKH terbit **2012**; **e-PKH** diluncurkan **September 2019** |
| **Pengguna** | Pendamping PKH, operator, KPM (via SIMPKH Mobile — login NIK + password dari pendamping saat validasi awal) |

**Fungsi terverifikasi e-PKH:** validasi, pemutakhiran data, **verifikasi komitmen**, **FDS (Family Development Session)**, manajemen SDM, penyaluran, dan rekonsiliasi. Sejak 2019 pemutakhiran data dilakukan langsung oleh pendamping di aplikasi untuk mempercepat proses.

**YANG TIDAK DILAKUKAN:**
- ❌ Tidak ada prediksi risiko, XAI, rekomendasi lintas OPD, atau simulasi kebijakan.
- ✅ **Monitoring outcome: ADA SEBAGIAN — pengecualian penting.** **"Verifikasi komitmen"** memeriksa apakah anak KPM benar bersekolah dan ibu hamil/balita benar mengakses layanan kesehatan. Ini **pemantauan perilaku/outcome antara pada level keluarga**, bukan sekadar output penyaluran. **Jangan klaim NADI yang pertama memantau outcome per keluarga di Indonesia.**
- ⚠️ Konsep **graduasi** (keluar dari program) sudah ada dan telah dikaji Bank Dunia — "melacak perubahan status keluarga" bukan gagasan baru.

**Sumber:**
- https://kms.kemenkopm.go.id/index.php?p=show_detail&id=1348 (Pedoman Operasional SIM-PKH 2012)
- https://kms.kemenkopm.go.id/index.php?p=show_detail&id=2198 (Web Portal & Dashboard SIM-PKH)
- https://documents1.worldbank.org/curated/en/099600012222121722/pdf/P1605900731f410730af2306a8be9ddde3b.pdf (Graduasi dari Program Bantuan Tunai Bersyarat di Indonesia — Bank Dunia)

---

## A.9 Sistem Daerah — Studi Kasus Konkret

### A.9.1 SIMNANGKIS DIY — Sistem Informasi Penanggulangan Kemiskinan, Provinsi D.I. Yogyakarta
- **Pengelola:** Badan Perencanaan Pembangunan, Riset, dan Inovasi Daerah DIY (Jl. Malioboro No. 8, Yogyakarta).
- **URL:** https://simnangkis.jogjaprov.go.id/
- **Empat modul terverifikasi:**
  1. **Pronangkis** — *"Sinergi Program Penanggulangan Kemiskinan lintas Provinsi dan Kabupaten/Kota"*
  2. **CSR** — usulan CSR dunia usaha, diorganisir per lokasi, output, dan keselarasan SDGs
  3. **SDGs** — pemantauan indikator kemiskinan terhadap target SDGs
  4. **Publikasi & Berita**
- **Data yang ditampilkan:** anggaran dan **realisasi triwulanan** per kabupaten/kota, sumber pendanaan, tujuan program, OPD penanggung jawab dan kontribusinya terhadap penanggulangan kemiskinan.
- ✅ **BUKTI KUAT bahwa "sinkronisasi program lintas OPD + pelibatan CSR + pelacakan SDGs" SUDAH ADA di Indonesia pada level provinsi.**
- ❌ Yang **tidak** ditemukan pada antarmuka publik: analitik prediktif, mesin rekomendasi intervensi, alat simulasi kebijakan, atau modul monitoring outcome keluarga (yang dilacak adalah **realisasi anggaran/output program**, bukan perubahan kondisi keluarga).

### A.9.2 SIPINTER — Kabupaten Purbalingga, Jawa Tengah
- **Nama lengkap:** Sistem Informasi Pelaporan Intervensi Penanggulangan Kemiskinan Terpadu.
- **Diluncurkan:** ***soft launching* 21 Juli 2026**, bersama program "Purbalingga Gotong Royong".
- **Moto:** *"Satu Data, Satu Gerak, Tepat Sasaran"*.
- **Fungsi:** mengintegrasikan data lintas instansi dan melacak **siapa yang membutuhkan bantuan, bantuan apa yang diberikan, organisasi mana yang membantu, kapan, dan hasilnya**.
- **Pelibatan pentahelix:** pemerintah, dunia usaha, perguruan tinggi, ormas keagamaan, BAZNAS, PMI, media, komunitas, masyarakat.
- ⚠️ **Ini pesaing konseptual paling dekat untuk klaim "loop intervensi lintas OPD".** Konsepnya sudah mencakup pelacakan hasil intervensi.
- ❌ Tidak ada penyebutan analitik prediktif, AI, atau *forecasting* dalam dokumentasi publik yang ditemukan. Spesifikasi teknis, model data, dan antarmuka **TIDAK TERVERIFIKASI**.
- **Sumber:** https://setda.purbalinggakab.go.id/soft-launching-purbalingga-gotong-royong-pemkab-satukan-kekuatan-lintas-sektor-percepat-penanggulangan-kemiskinan/

### A.9.3 Carik Jakarta — DKI Jakarta
- **Pengelola:** Dinas Pemberdayaan, Perlindungan Anak dan Pengendalian Penduduk (DPPAPP) Provinsi DKI Jakarta.
- **Pendata:** **Kader PKK / Kader Dasawisma** ("Carik" = juru tulis dalam bahasa Jawa).
- **4 tema pendataan:** Sosial Ekonomi; Keluarga Berencana (KB); Pembangunan Keluarga (PK); PKK & **Kondisi Fungsional Anak (CFM)**.
- **Dashboard publik** (https://carik.jakarta.go.id/dashboard/) — **12 seksi tematik**: Kependudukan, Kesehatan, Lingkungan, Pendidikan, Pembangunan Keluarga, Teknologi Informasi, Fertilitas/KB, Perumahan, Sosial Ekonomi, Potensi Bencana, Transportasi, Ketenagakerjaan. Unit ukur: Kelompok, Bangunan, Rumah Tangga, Keluarga, Individu. Indikator contoh: kepemilikan jaminan kesehatan, status gizi balita, ASI eksklusif.
- **Indeks turunan yang dihasilkan:** Indeks Pembangunan Keluarga (IPK), Indeks Rumah Sehat, **Indeks Ekonomi/Kemiskinan**, Indeks Kependudukan & KB, Indeks Tahapan Kesejahteraan Keluarga, plus **analisis kros-tabulasi**.
- **Kaitan DTKS:** digunakan Dinas Sosial DKI sebagai media pendataan warga pra-sejahtera untuk masuk DTKS.
- ✅ Composite index per keluarga sudah ada — "menghitung skor kesejahteraan keluarga" **bukan hal baru** di Jakarta.
- ❌ Tidak ditemukan fitur prediksi, rekomendasi intervensi, atau simulasi pada halaman publik. *Angka cakupan riil TIDAK TERVERIFIKASI (dashboard menampilkan 0 saat diambil otomatis).*
- **Sumber:** https://carik.jakarta.go.id/dashboard/ | https://www.jakarta.go.id/carik-jakarta | https://greennetwork.id/kabar/carik-jakarta-data-komprehensif-untuk-dukung-kebijakan-yang-lebih-tepat/ | https://dtks.jakarta.go.id/ | https://pusdatinkeluarga.jakarta.go.id/ | https://datawarga-dukcapil.jakarta.go.id/

### A.9.4 Smart Kampung — Kabupaten Banyuwangi
- Program integrasi layanan publik hingga level desa berbasis serat optik; memadukan TIK, ekonomi produktif, ekonomi kreatif, peningkatan pendidikan-kesehatan, dan **upaya pengentasan kemiskinan**.
- **Fitur paling relevan:** aparat desa mendata ulang dan mencocokkan data kemiskinan dengan data kependudukan sehingga penduduk miskin diketahui berdasarkan **nama, NIK, alamat, posisi rumah (geokoding koordinat GPS), dan jenis kemiskinannya** — dengan tujuan eksplisit **memudahkan intervensi program yang sesuai dengan kondisi keluarga miskin tersebut**.
- ✅ **"By name by address" + geospasial + pencocokan jenis kemiskinan ke jenis intervensi SUDAH ADA di Banyuwangi.** Jangan klaim ini sebagai kebaruan NADI.
- ❌ Tidak ditemukan bukti prediksi, XAI, simulasi, atau monitoring outcome longitudinal.
- **Sumber:** https://smartkampung.id/ | https://smartkampung.id/spbedesa/dtks | https://sipp.banyuwangikab.go.id/layanan/dinas-komunikasi-informatika-dan-persandian/smart-kampung | https://majadigi.jatimprov.go.id/layanan/smart-kampung-banyuwangi

### A.9.5 Inisiatif daerah lain (bukti bahwa "dashboard kemiskinan daerah" sudah ramai)
- **Kabupaten Blitar:** Rencana Aksi Tahunan (RAT), **dashboard kemiskinan**, aplikasi **Sidaksos**, gerakan gotong royong, kolaborasi pentahelix — dilaporkan sebagai inovasi kelembagaan untuk mengatasi masalah koordinasi.
- **Kabupaten Rote Ndao (NTT), inovasi "Tulu Fali":** integrasi data keluarga, individu, kependudukan, dan berbagai program bantuan lintas OPD untuk perencanaan lebih akurat, **menghindari tumpang tindih bantuan**, serta meningkatkan transparansi dan akuntabilitas.
- **Dinas Sosial Provinsi Jawa Tengah:** inovasi **"ATRI-BUT" (Akurasi Terbaik dengan Data Terpadu)**.
- **Kabupaten Rokan Hulu:** portal **E-Bangkit — Penanggulangan Kemiskinan Terpadu**.
- **Jawa Barat:** **Sapawarga** (super-app layanan publik oleh Jabar Digital Service), **Jabar X-Road** (data exchange), **Portal Data Desa** dengan dashboard IDM (Pendidikan, Kesehatan, Kependudukan, Infrastruktur Internet, Bencana, Ekonomi, Lingkungan, Program Desa). *Dashboard khusus kemiskinan ekstrem Jabar: TIDAK DITEMUKAN dalam riset ini.*
- **DKI Jakarta:** Dinas Sosial rutin melakukan verifikasi & validasi DTKS untuk memastikan kelayakan penerima.
- **Sumber:** https://rotendaokab.go.id/inovasi-tulu-fali-perkuat-komitmen-bupati-dan-wakil-bupati-rote-ndao-dalam-percepatan-penanggulangan-kemiskinan.php | https://dinsos.jatengprov.go.id/detail_berita/rapat-koordinasi-percepatan-penuntasan-kemiskinan-ekstrem-dan-launching-inovasi-dinas-sosial-provinsi-jawa-tengah | https://e-bangkit.rokanhulukab.go.id/index.php?page=detailinfo&id=8 | https://digitalservice.jabarprov.go.id/program/ | https://portaldatadesa.jabarprov.go.id/ | https://jurnal.unpad.ac.id/jmpp/article/download/66013/pdf | https://m.beritajakarta.id/read/129944/dinsos-dki-terus-lakukan-verifikasi-validasi-dtks-untuk-pastikan-kelayakan-penerima-bansos

---

## A.10 Riset akademik Indonesia — bukti bahwa ML untuk targeting kemiskinan sudah dikerjakan

**⚠️ Ini bagian yang paling berbahaya bagi klaim kebaruan NADI. Baca sebelum menulis slide "state of the art".**

**Studi paling relevan: "Enhancing Poverty Targeting with Spatial Machine Learning: An application to Indonesia"** (arXiv:2503.04300)
- **Data:** SUSENAS dalam konteks **DTKS Indonesia**, dua periode:
  - 2016–2020: **1.533.746 observasi, 134 variabel**
  - 2016–2021: **1.512.887 observasi, 255 variabel**
  - Target: pengeluaran per kapita rumah tangga, dibinerkan pada ambang kemiskinan 40%.
- **Metode:** *spatial contiguity matrix* (Delaunay Triangulation) + *spatial hierarchical clustering* (4 / 6 / 12 klaster) + model ML terpisah per klaster (Naive Bayes, Random Forest, Gradient Boosting) + integrasi *spatial lag features*.
- **Hasil konkret:** exclusion error turun **28% → 20%** (data 2016–2020) dan **27% → 24%** (data 2016–2021). Moran's I = **0,411 (p<0,01)** membuktikan pola spasial signifikan pada distribusi pengeluaran.
- **Kelemahan PMT konvensional yang disorot:** mengabaikan autokorelasi spasial; **exclusion error tinggi (28% rumah tangga miskin terekslusi)**; heterogenitas regional; generalisasi buruk pada pendekatan regresi linear tradisional.
- **Sumber:** https://arxiv.org/html/2503.04300 | https://ideas.repec.org/p/arx/papers/2503.04300.html

**Bukti lain:**
- **Wobcke & Mariyah (2023), "Machine learning and data augmentation in the proxy means test for poverty targeting"**, *Statistical Journal of the IAOS* — https://journals.sagepub.com/doi/abs/10.3233/SJI-230033 (Mariyah berafiliasi dengan Politeknik Statistika STIS / ekosistem BPS).
- **BPS/STIS:** studi *geospatial big data* + ML/deep learning untuk estimasi distribusi kemiskinan granular di Jawa Timur — https://proceedings.stis.ac.id/icdsos/article/view/359
- **BPS:** internalisasi **Small Area Estimation (SAE)** untuk data kualitas tinggi tingkat kecamatan/desa (workshop 2023 & 2024) — https://pesawarankab.bps.go.id/en/news/2023/11/27/63/workshop-implementasi-small-area-estimation--sae-.html | https://bengkulu.bps.go.id/en/news/2024/09/06/723/internalization-of-small-area-estimation--sae--for-quality-data.html
- **Perbandingan metode prediksi kemiskinan Indonesia:** https://ejournal.uin-suska.ac.id/index.php/JSMS/article/download/9259/5439
- **Studi ML kemiskinan Pulau Jawa (interaksi IPM × bantuan sosial):** https://bds-sby.telkomuniversity.ac.id/mengurai-kemiskinan-lewat-statistik-dan-machine-learning-studi-kasus-pulau-jawa/

**Kesimpulan jujur:** **ML untuk targeting kemiskinan di Indonesia sudah ada pada level riset, bahkan dari dalam ekosistem BPS sendiri.** Kebaruan NADI **bukan** pada "memakai ML untuk kemiskinan". Kebaruan harus dicari pada **operasionalisasi** — menjadikannya alat kerja harian OPD dengan penjelasan, rekomendasi, dan akuntabilitas.

---

# BAGIAN B — LANSKAP INTERNASIONAL

## B.1 SISBEN IV — Kolombia

| Aspek | Isi |
|---|---|
| **Nama** | Sistema de Identificación de Potenciales Beneficiarios de Programas Sociales |
| **Pemilik** | Departamento Nacional de Planeación (DNP), Kolombia |
| **Sejak** | **1994** |
| **Metode** | **Proxy Means Test** — indeks kesejahteraan komposit dari variabel konsumsi barang tahan lama, *human capital endowment*, dan pendapatan berjalan. Algoritma: **Optimal Scaling & Alternating Least Squares** |
| **Output** | Skor **0–100**, **6 level**; sebagian besar program nasional membatasi kelayakan pada level 1–2 (beberapa hingga level 3) |

**Fitur baru pada SISBEN IV:** mulai menggunakan **teknologi data analytics untuk mencari inkonsistensi dalam basis data**, menghukum orang yang diduga berbohong, dan mengurangi jumlah orang yang bisa mengakses manfaat.

**KRITIK TERDOKUMENTASI:**
- **Exclusion error** signifikan pada populasi migran/pengungsi Venezuela; mekanisme yang diidentifikasi adalah *occupational downgrading*.
- Kritik akademik: algoritmanya disebut *"apparently ad-hoc"*.
- Kritik kebijakan: pergeseran dari alat inklusi menjadi alat **deteksi kecurangan** — pelajaran penting untuk NADI (jangan sampai model risiko berubah fungsi jadi alat penghukuman).

**YANG TIDAK DILAKUKAN:** ❌ prediksi risiko dinamis ke depan; ❌ explainability yang disajikan ke warga; ❌ rekomendasi intervensi lintas sektor; ❌ simulasi kebijakan; ❌ monitoring outcome.

**Sumber:**
- https://documents1.worldbank.org/curated/en/364521468019731045/pdf/32759.pdf (World Bank SP Discussion Paper No. 0529)
- https://jpia.princeton.edu/news/accuracy-proxy-means-tests-immigrant-populations-case-study-colombia
- https://www.researchgate.net/publication/351699844_Experimenting_with_poverty_The_SISBEN_and_data_analytics_projects_in_Colombia
- https://econpapers.repec.org/paper/wbkhdnspu/32759.htm

---

## B.2 Cadastro Único + Bolsa Família — Brasil

| Aspek | Isi |
|---|---|
| **Pemilik** | Ministério do Desenvolvimento Social (MDS); dioperasikan **Caixa Econômica Federal** |
| **Cakupan** | Hampir sensus terhadap populasi termiskin; pendataan & entri data oleh **5.570 pemerintah kota (municípios)** |
| **Titik layanan** | **CRAS** (Centro de Referência de Assistência Social) |
| **Alur** | Warga daftar ke CadÚnico → pemerintah **otomatis menganalisis data untuk mengidentifikasi keluarga yang layak Bolsa Família** — **tidak ada formulir aplikasi terpisah** |

**Fitur mutakhir yang relevan:**
- **Averiguação Cadastral** — pemeriksaan silang otomatis data CadÚnico terhadap catatan administratif federal lain (remunerasi kerja, manfaat INSS). Keluarga dengan divergensi pendapatan dipanggil untuk pemutakhiran.
- Sejak **2023**, averiguação difokuskan mengidentifikasi manfaat yang dibayarkan secara tidak semestinya.
- Sistem kini dapat melakukan **pemutakhiran otomatis lewat integrasi data** — status ditampilkan sebagai *"Atualizado por integração de dados"*, sehingga keluarga **tidak perlu datang** untuk memutakhirkan hal yang sudah diketahui pemerintah.

**Nilai untuk NADI:** ✅ **Pemutakhiran otomatis berbasis integrasi data administratif SUDAH DILAKUKAN Brasil.** Jika NADI menawarkan "data selalu mutakhir lewat integrasi", akui ini sebagai adopsi praktik terbaik internasional, bukan penemuan.

**YANG TIDAK DILAKUKAN:** ❌ prediksi risiko ke depan; ❌ explainability per keluarga; ❌ rekomendasi lintas sektor otomatis; ❌ simulasi kebijakan. ⚠️ Ada **kondisionalitas** (kehadiran sekolah, imunisasi) yang dipantau — bentuk monitoring outcome antara, mirip verifikasi komitmen PKH.

**Sumber:**
- https://www.ilo.org/sites/default/files/wcmsp5/groups/public/@ed_protect/@soc_sec/documents/publication/wcms_311694.pdf
- https://www.worldbank.org/content/dam/Worldbank/Event/social-protection/Claudia%20Curralero%20-%20SSN%20Course%20Cadastro%20%C3%9Anico.pdf
- https://globalallianceagainsthungerandpoverty.org/country-example/brazil-single-registry-cadunico/
- https://globalallianceagainsthungerandpoverty.org/country-example/brazil-bolsa-familia/
- https://mds.gov.br/webarquivos/MDS/2_Acoes_e_Programas/Bolsa_Familia/Gestao_de_Beneficios/Guia_Rapido_de_Gestao_de_Beneficios_Bloqueio_Averiguacao_Unipessoal.pdf
- https://centreforpublicimpact.org/public-impact-fundamentals/bolsa-familia-in-brazil/

---

## B.3 Listahanan / NHTS-PR — Filipina

| Aspek | Isi |
|---|---|
| **Pemilik** | Department of Social Welfare and Development (DSWD) |
| **Metode** | **Proxy Means Test** — menaksir pendapatan keluarga dari variabel proksi (komposisi keluarga, pendidikan anggota, kondisi keluarga, akses layanan dasar); taksiran dibandingkan dengan **ambang kemiskinan per provinsi** |
| **Instrumen** | **Family Assessment Form (FAF)** — kuesioner **4 halaman dengan 46 variabel**, dikumpulkan lewat kunjungan rumah |

**Empat fase:** (1) *Preparatory*; (2) *Data Collection & Analysis*; (3) **Validation & Finalization — memakai umpan balik komunitas**; (4) *Report Generation*.

**Angka putaran (⚠️ ada inkonsistensi antar sumber — JANGAN pakai di slide tanpa verifikasi ulang):**
- Putaran 1 (selesai 2011): **5,2 juta keluarga miskin** dari 10,9 juta rumah tangga yang dinilai.
- Putaran 3 (2016): **5,6 juta keluarga miskin**.
- Listahanan 3 diumumkan hasilnya **Agustus 2022**; satu sumber menyebut DSWD menyelesaikan penilaian **14,4 juta keluarga miskin** — angka ini **bertentangan** dengan 5,6 juta di atas, kemungkinan karena beda definisi/cakupan.

**Fitur akuntabilitas:** tersedia mekanisme **banding/appeal** publik untuk masuk ke daftar Listahanan 3.

**YANG TIDAK DILAKUKAN:** ❌ prediksi risiko dinamis; ❌ explainability skor PMT ke keluarga; ❌ rekomendasi intervensi lintas agensi; ❌ simulasi; ❌ monitoring outcome. ⚠️ Registry statis dengan siklus multi-tahun — kelemahan yang sama dengan pendekatan Indonesia sebelum DTSEN.

**Sumber:**
- https://fo8.dswd.gov.ph/national-household-targeting-system-for-poverty-reduction-nhts-pr-or-listahan/
- https://documents1.worldbank.org/curated/en/830621542293177821/pdf/132110-PN-P162701-SPL-Policy-Note-16-Listahanan.pdf
- https://mirror.pia.gov.ph/press-releases/2022/08/01/dswd-launches-listahanan-3-result
- https://www.pna.gov.ph/articles/1119180
- https://www.pna.gov.ph/articles/1112815 (mekanisme appeal)
- https://coe-psp.dap.edu.ph/compendium-innovation/listahanan-national-household-targeting-system-for-poverty-reduction-nhts-pr-2/

---

## B.4 NSER / BISP — Pakistan (**contoh terbaik "dynamic registry"**)

| Aspek | Isi |
|---|---|
| **Nama** | Benazir National Socio-Economic Registry (NSER), dikelola Benazir Income Support Programme (BISP) |
| **Pemutakhiran besar** | **2019–2021** menggunakan **CAPI (Computer Assisted Personal Interviewing)**, data dikumpulkan dari **hampir 35 juta rumah tangga**; basis data diluncurkan resmi **Januari 2022** |
| **Metode** | **PMT** menghasilkan skor kesejahteraan **skala 0–100** |
| **Ambang batas** | **PMT cut-off 32** (disetujui BISP Board rapat ke-52, **23 September 2021**); **cut-off 37** untuk keluarga dengan anggota penyandang disabilitas |

**Fitur "dynamic registry" (paling relevan untuk NADI):** berbeda dengan registry statis yang hanya diperbarui setiap beberapa tahun, **NSER ditransformasi menjadi *dynamic registry*** agar rumah tangga dapat mendaftar dan memutakhirkan informasi lebih sering. Sejak pilot 2017 di **15 distrik**: **desk pendaftaran mandiri** + survei *door-to-door*.

**Transparansi:** warga dapat **mengecek skor PMT-nya sendiri secara online lewat CNIC** (nomor identitas nasional).

✅ **PENTING: Pakistan sudah memberi warga akses ke skor PMT pribadinya.** Jika NADI mengklaim "warga bisa tahu skornya", akui bahwa Pakistan sudah melakukannya — bedakan pada **penjelasan mengapa**, bukan sekadar angka.

**YANG TIDAK DILAKUKAN:** ❌ prediksi risiko ke depan; ❌ explainability variabel per keluarga (skor ditampilkan, alasannya tidak); ❌ rekomendasi lintas sektor; ❌ simulasi; ❌ monitoring outcome kesejahteraan.

**Sumber:**
- https://bisp.gov.pk/Detail/NzI5YTMyYTMtYjE1My00NGUwLTgwYTItZWUwYTZkYWZjYmNj (halaman resmi NSER)
- https://bisp.gov.pk/Detail/YTgzNjkxM2YtN2ViMC00MjA5LWI0MDMtNzM4ZWJmMGVlNzc5
- https://www.bisp.gov.pk/SiteImage/Downloads/Data%20Sharing%20protocols_online_2022.pdf (protokol berbagi data — rujukan bagus untuk tata kelola NADI)
- https://pitb.gov.pk/bisp

---

## B.5 Enhanced Single Registry (ESR) — Kenya

| Aspek | Isi |
|---|---|
| **Pemilik** | National Social Protection Secretariat, Ministry of Labour and Social Protection |
| **Waktu** | Diperkenalkan **2020**, *go-live* **Juli 2021** |
| **Mitra** | Development Pathways, WFP, beberapa departemen kementerian |
| **Arsitektur** | Modul web + mobile; mengotomatiskan komponen **social registry** DAN **integrated beneficiary registry** |

**Fitur konkret:**
- Platform tunggal tempat informasi lintas program perlindungan sosial disimpan, dianalisis, dan dilaporkan.
- **Pemeriksaan duplikasi manfaat** — mencegah satu penerima mendapat manfaat ganda di dalam dan antar program.
- Menghubungkan data program: **CT-OVC** (anak yatim & rentan), **HSNP** (Hunger Safety Net Programme), **OPCT** (lansia), **PwSD-CT** (disabilitas berat).

✅ **"Deteksi tumpang tindih bantuan lintas program" SUDAH ADA dan operasional di Kenya sejak 2021.** Ini fitur yang sering diklaim baru oleh proposal dashboard kemiskinan — jangan.

**YANG TIDAK DILAKUKAN:** ❌ prediksi risiko; ❌ XAI; ❌ rekomendasi intervensi otomatis lintas kementerian; ❌ simulasi; ❌ monitoring outcome kesejahteraan longitudinal.

**Sumber:**
- https://www.nsps.socialprotection.go.ke/enhanced-single-registry
- https://www.jointsdgfund.org/article/enhanced-single-registry-social-protection-kenya
- https://kms.nsps.socialprotection.go.ke/index.php/knowledge-repository/28-enhanced-single-registry/59-strategy-for-the-enhancement-of-the-single-registry-esr
- https://socialprotection.org/sites/default/files/publications_files/GIZ_DFID_IIMS%20in%20social%20protection_long_02-2020.pdf
- https://includeplatform.net/wp-content/uploads/2022/08/Two-pager-Single-and-ready_2022-08.pdf

---

## B.6 Ubudehe — Rwanda (**contoh "community-based targeting", antitesis pendekatan algoritmik**)

| Aspek | Isi |
|---|---|
| **Pemilik** | Local Administrative Entities Development Agency (**LODA**), Rwanda |
| **Sejak** | Diluncurkan **2001**, berakar pada praktik tradisional gotong royong |
| **Metode** | **Kategorisasi berbasis komunitas** — warga mengklasifikasikan rumah tangga sendiri dalam musyawarah; direklasifikasi tiap ~3 tahun |
| **Revisi 2020** | Restrukturisasi menjadi **5 kategori (A–E)** berbasis pendapatan keluarga per bulan. **Kategori A:** > **Rwf 600.000/bulan**. **Kategori B:** **Rwf 65.000 – 600.000/bulan**. **Kategori C & D:** kelompok termiskin. **Kategori E:** lansia dan lemah |

**KRITIK TERDOKUMENTASI:** Kritikus mempertanyakan bagaimana rumah tangga bisa berada di kategori yang sama padahal pendapatan satu **hampir sepuluh kali lipat** yang lain (rentang Kategori B terlalu lebar). Warga menuntut peninjauan oleh legislator dan lebih banyak masukan publik. Tujuan strategis revisi sendiri secara eksplisit menyebut **"mengurangi ketidakpuasan warga"** terhadap kategorisasi sebelumnya, dan **menyelaraskan kategorisasi komunitas dengan informasi berbasis bukti tentang penghidupan rumah tangga**.

**Pelajaran untuk NADI:**
- ✅ Ubudehe menunjukkan **legitimasi sosial** dari penilaian berbasis musyawarah — paralel dengan **Musdes/Muskel** dalam alur SIKS-NG. **Argumen kuat untuk NADI: model AI tidak menggantikan musyawarah, tapi menyiapkan bahan musyawarah yang lebih baik.**
- ❌ Namun Ubudehe juga menunjukkan bahwa kategorisasi kasar tanpa penjelasan yang jelas memicu ketidakpuasan — persis risiko yang harus dimitigasi NADI.

**Sumber:**
- https://www.loda.gov.rw/updates/news-detail/citizens-start-classifying-their-households-into-new-ubudehe-categories
- https://www.ktpress.rw/2020/10/revised-ubudehe-categories-draw-mixed-reactions/
- https://loda.prod.risa.rw/updates/news-detail/cabinet-approves-review-and-classification-of-households-into-ubudehe-categories
- http://www.xinhuanet.com/english/2020-12/05/c_139565857.htm
- https://www.researchgate.net/publication/370589439_The_Challenges_and_Examination_of_New_Programme_Ubudehe_2020_in_Rwanda

---

## B.7 India — DBT & Social Registries negara bagian

| Aspek | Isi |
|---|---|
| **Nasional** | **Direct Benefit Transfer (DBT)** — https://dbtbharat.gov.in/ |
| **Peran Aadhaar** | Berfungsi ganda: **verifikator identitas** dan **alamat finansial** via **Aadhaar Payments Bridge (APB)**. Aadhaar **tidak wajib** untuk skema DBT, tetapi dipreferensikan |
| **Social registries negara bagian** | **Samagra** (Madhya Pradesh), **Kutumba** (Karnataka), **Parivaar Pehchaan Patra** (Haryana), **Jan Aadhaar** (Rajasthan), **Social Protection Delivery Platform / SPDP** (Odisha) |

**KRITIK TERDOKUMENTASI (penting untuk bagian Responsible AI NADI):**
- **Exclusion errors** — orang yang layak ditolak karena daftar penerima usang, dokumen hilang, atau ketidakcocokan data Aadhaar/bank.
- **Kegagalan autentikasi sidik jari** menyebabkan penolakan manfaat, terutama menimpa lansia dan pekerja kasar (sidik jari aus).
- **Hambatan digital & perbankan** di daerah pedesaan, suku, dan terpencil.
- Kritik struktural: DBT *"sering memaksakan hambatan baru bagi kaum miskin, lansia, perempuan, dan kelompok terpinggirkan"* — efisiensi sistem tidak otomatis berarti inklusi.

**Pelajaran untuk NADI:** kegagalan bukan hanya di model, tapi di **lapisan verifikasi identitas dan penyaluran**. Desain NADI wajib punya **jalur luring / manual override** yang jelas.

**Sumber:**
- https://dbtbharat.gov.in/static-page-content/spagecont?id=1
- https://www.ideasforindia.in/topics/governance/aadhaar-bill-and-government-benefits-risk-of-increasing-exclusion
- https://link.springer.com/chapter/10.1007/978-3-032-20821-7_17 ("Digital States, Analog Lives")
- https://globalallianceagainsthungerandpoverty.org/country-example/india-direct-benefit-transfer-dbt/
- https://arxiv.org/pdf/2006.04654 (arsitektur *privacy-by-design* untuk layanan publik India)
- https://www.impriindia.com/insights/dbt-2-0-transforming-welfare-delivery/

---

## B.8 Togo — Novissi (**contoh positif AI untuk bansos, dengan kejujuran soal batasnya**)

- **Konteks:** program transfer tunai darurat COVID-19 pemerintah Togo, menyalurkan jutaan dolar AS bantuan.
- **Metode:** data survei tradisional dipakai melatih algoritma ML untuk mengenali pola kemiskinan dalam **metadata telepon seluler** (jumlah panggilan, jumlah menara BTS unik yang dikunjungi, penggunaan data seluler) + **citra satelit**.
- **Hasil terverifikasi (Nature 603, 2022, hlm. 864–870):**
  - Targeting berbasis telepon: **AUC = 0,70**, mengungguli *geographic blanket targeting* (**AUC = 0,59–0,64**).
  - Pendekatan ML **mengurangi exclusion error 4–21%** dibanding opsi *geographic targeting*.
  - **NAMUN — dan ini harus disampaikan jujur:** dibandingkan metode yang membutuhkan **social registry komprehensif**, pendekatan ML justru **MENAIKKAN exclusion error 9–35%**.
- **Kesimpulan penulis sendiri:** pendekatan ML cepat dan hemat biaya **jika tidak ada data mutakhir**, tetapi ***"tidak seharusnya menggantikan metode targeting tradisional bila data dan waktu memungkinkan."***

> **💡 Ini kutipan terkuat untuk membenarkan posisi NADI yang rendah hati:** Indonesia **punya** social registry komprehensif (DTSEN, 290,13 juta individu). Maka posisi NADI yang benar dan jujur bukan *"AI menggantikan DTSEN"*, melainkan **"AI melengkapi DTSEN dengan dimensi waktu, penjelasan, dan tindak lanjut."**

**Sumber:**
- https://www.nature.com/articles/s41586-022-04484-9
- https://www.povertyactionlab.org/project/using-mobile-phone-and-satellite-data-target-togos-emergency-cash-transfer-program
- https://cega.berkeley.edu/collection/ai-assisted-cash-transfers-togo/
- https://www.nber.org/system/files/working_papers/w29070/w29070.pdf
- https://voxdev.org/topic/methods-measurement/measuring-poverty-using-mobile-phone-data-implications-targeting-and
- https://arxiv.org/pdf/2408.13424 (*targeted differential privacy* untuk aplikasi kemanusiaan)

---

## B.9 Bukti akademik lintas negara tentang ML dalam PMT

- **McBride & Nichols, "Improved poverty targeting through machine learning: An application to the USAID Poverty Assessment Tools":** penerapan algoritma ML pada pengembangan PMT dapat meningkatkan kinerja *out-of-sample* secara substansial; metode *stochastic ensemble* memperbaiki kinerja **2%–18%** dibanding metode saat ini. — https://www.semanticscholar.org/paper/Improved-poverty-targeting-through-machine-learning-McBridea-Nicholsb/6ad8406eb8d2c809810e0485639bb41d237352bd
- **Bank Dunia, "Estimating Changes to the Predictive Performance of Proxy Means Test":** https://documents1.worldbank.org/curated/en/099060523221086697/txt/P1749430f9ac8e020a0f601ead6b1d0bdc.txt
- **Brown, Ravallion & van de Walle, "A poor means test? Econometric targeting in Africa"** (*Journal of Development Economics*) — kritik mendasar terhadap akurasi PMT di Afrika: https://www.sciencedirect.com/science/article/abs/pii/S0304387818305819
- **Bloomberg/akademik, "Algorithmic Fairness and Efficiency in Targeting Social Welfare Programs":** https://data.bloomberglp.com/company/sites/2/2018/09/algorithm-fairness-efficiency_.pdf

---

# BAGIAN C — KASUS KONTROVERSI: AI/ALGORITMA DALAM BANSOS
### (Bahan wajib untuk bagian Responsible AI & Mitigasi Risiko NADI)

## C.1 SyRI (Systeem Risico Indicatie) — Belanda, **DILARANG PENGADILAN**

| Aspek | Isi |
|---|---|
| **Apa** | Sistem algoritmik pemerintah Belanda untuk *"mencegah dan memberantas kecurangan di bidang jaminan sosial dan skema terkait pendapatan, pajak, kontribusi asuransi sosial, dan hukum ketenagakerjaan"* |
| **Cara kerja** | Menautkan dan menganalisis data dari berbagai instansi pemerintah/publik, lalu menghasilkan **laporan risiko** bila seseorang dicurigai melakukan kecurangan |
| **Putusan** | **5 Februari 2020** — Pengadilan Distrik Den Haag: SyRI **melanggar Pasal 8 ECHR** (hak atas penghormatan kehidupan pribadi dan keluarga) |

**Tiga alasan utama pengadilan (HAFALKAN — ini checklist mitigasi NADI):**
1. **Terlalu buram (*too opaque*)** — model risiko algoritmiknya disembunyikan.
2. **Mengumpulkan terlalu banyak data.**
3. **Tujuan pengumpulan data tidak cukup jelas dan spesifik.**

Pengadilan menyimpulkan SyRI **tidak mencapai keseimbangan yang adil (*fair balance*)** antara deteksi kecurangan dan privasi.

**Fakta memberatkan tambahan:** SyRI **secara eksklusif ditargetkan ke lingkungan yang mayoritas dihuni penduduk berpenghasilan rendah dan minoritas** — bentuk diskriminasi geografis/sosial.

**Signifikansi:** salah satu kali pertama pengadilan di dunia membatalkan sistem deteksi kecurangan kesejahteraan atas dasar hak asasi manusia. Pelapor Khusus PBB menyebutnya *"putusan penting yang menghentikan upaya pemerintah memata-matai kaum miskin."*

**Sumber:**
- https://www.loc.gov/item/global-legal-monitor/2020-03-13/netherlands-court-prohibits-governments-use-of-ai-software-to-detect-welfare-fraud/
- https://algorithmwatch.org/en/syri-netherlands-algorithm/
- https://www.ohchr.org/en/press-releases/2020/02/landmark-ruling-dutch-court-stops-government-attempts-spy-poor-un-expert
- https://journals.sagepub.com/doi/10.1177/13882627211031257 (van Bekkum & Zuiderveen Borgesius, 2021)
- https://arxiv.org/abs/2509.23843
- https://techcrunch.com/2020/02/06/blackbox-welfare-fraud-detection-system-breaches-human-rights-dutch-court-rules
- https://iapp.org/news/a/digital-welfare-fraud-detection-and-the-dutch-syri-judgment

---

## C.2 Robodebt — Australia, **ROYAL COMMISSION & GANTI RUGI**

| Aspek | Isi |
|---|---|
| **Periode** | **2015–2019** |
| **Cara kerja** | Penilaian otomatis membandingkan data kantor pajak dengan data pembayaran kesejahteraan, menggunakan **income averaging** untuk menghitung rata-rata pendapatan, lalu menerbitkan surat tagihan utang ke penerima bansos |
| **Skala** | Menagih **AUD 1,76 miliar** dari sekitar **526.000 penerima** melalui ±**794.000 transaksi penagihan** |
| **Cacat fatal** | Penggunaan *income averaging* **tidak konsisten dengan undang-undang jaminan sosial**; *"pada dasarnya tidak adil, memperlakukan banyak orang seolah-olah mereka telah menerima pendapatan pada saat mereka sebenarnya tidak"* |

**Hasil Royal Commission (laporan final 7 Juli 2023):** lebih dari **900 halaman, 3 volume, 57 rekomendasi**. Skema disebut *"crude and cruel mechanism"* yang *"neither fair nor legal"* dan *"membuat banyak orang merasa seperti kriminal."* Individu dirujuk untuk penuntutan pidana.

**Penyelesaian finansial:**
- *Class action* awal diselesaikan 2020: pemerintah federal setuju mengembalikan utang yang ditagih keliru plus bunga — total **AUD 1,8 miliar**.
- Pengadilan Federal Australia mengesahkan penyelesaian *class action* **AUD 548,5 juta** — disebut yang terbesar dalam sejarah Australia.

**Pelajaran untuk NADI (paling tajam):** kegagalan Robodebt **bukan kegagalan AI canggih** — melainkan kegagalan **asumsi statistik sederhana (rata-rata) yang diterapkan pada keputusan individual, tanpa verifikasi manusia, dengan beban pembuktian dibalik ke warga.** NADI harus eksplisit: **skor model tidak boleh menjadi dasar tunggal keputusan yang merugikan.**

**Sumber:**
- https://www.abc.net.au/news/2023-07-07/robodebt-royal-commission-findings-revealed/102531450
- https://lsj.com.au/articles/crude-cruel-and-unlawful-robodebt-royal-commission-findings/
- https://clcs.org.au/robodebt-royal-commission-report-unravels-systemic-injustice-and-recommends-urgent-reform/
- https://en.wikipedia.org/wiki/Royal_Commission_into_the_Robodebt_Scheme
- https://www.sbs.com.au/news/article/robodebt-class-action-compensation-whats-next-for-victims/yturl57q3
- https://www.auspublaw.org/blog/2024/8/government-debt-collection-after-robodebt

---

## C.3 Social Card (Socijalna Karta) — Serbia

| Aspek | Isi |
|---|---|
| **Dasar** | Social Card Law, berlaku **1 Maret 2022** |
| **Cara kerja** | Basis data terpusat yang memproses **130 kategori data pribadi** dari pemohon bantuan sosial untuk menilai kelayakan |
| **Pendanaan** | **Dibiayai Bank Dunia** |

**Temuan Amnesty International** (laporan ***"Trapped by Automation: Poverty and Discrimination in Serbia's Welfare State"***, Desember 2023):
- Registry **mengoperasionalkan kondisi kelayakan restriktif yang sudah ada dan memperparah eksklusi**, terutama menimpa **Roma dan penyandang disabilitas**.
- Orang-orang tidak mampu membayar tagihan dan menyediakan makanan setelah dikeluarkan dari bantuan sosial akibat sistem ini.
- Amnesty menyebutnya *"intrusive surveillance system"*.
- **28 November 2022:** Amnesty International bersama ESCR-Net menyerahkan opini hukum ke A11 Initiative sebagai bukti untuk **gugatan konstitusional** terhadap Social Card Law.

**Pelajaran untuk NADI:** **otomasi memperbesar bias yang sudah ada dalam aturan kelayakan.** Jika aturan dasarnya eksklusif, sistem yang lebih efisien hanya membuat eksklusi lebih cepat dan lebih luas. NADI wajib melakukan **audit dampak diferensial per kelompok rentan** (disabilitas, lansia, masyarakat adat, perempuan kepala keluarga, wilayah 3T).

**Sumber:**
- https://www.amnesty.org/en/latest/research/2023/12/trapped-by-automation-poverty-and-discrimination-in-serbias-welfare-state/
- https://www.amnesty.org/en/documents/eur70/7443/2023/en/
- https://www.amnesty.org/en/latest/news/2023/12/serbia-world-bank-funded-digital-welfare-system-exacerbating-poverty-especially-for-roma-and-people-with-disabilities/
- https://www.amnesty.org/en/latest/news/2022/11/serbia-social-card-law-could-harm-marginalized-members-of-society-legal-opinion/
- https://balkaninsight.com/2023/07/25/doomed-by-algorithm-serbias-social-card-leaves-societys-weakest-exposed/
- https://www.rferl.org/a/serbia-social-assistance-roma-amnesty-world-bank/32712625.html
- https://www.context.news/digital-rights/as-serbia-adopts-digital-welfare-system-the-poorest-miss-out

---

## C.4 Sintesis Risiko — Brookings, *"AI for Social Protection: Mind the People"*

Empat tantangan kritis yang diidentifikasi:
1. **Akuntabilitas & transparansi** — banyak keputusan AI *"bersifat tidak transparan dan tidak sepenuhnya dapat dijelaskan karena menggabungkan banyak faktor dalam proses algoritmik bertahap."*
2. **Kualitas data** — data administratif yang buruk menghasilkan kesalahan serius (contoh: penempatan anak asuh yang tidak optimal).
3. **Penyalahgunaan data terintegrasi (*function creep*)** — data yang dikumpulkan untuk tujuan kesejahteraan dipakai untuk keperluan lain, misalnya identifikasi remaja berisiko menjadi pelaku kejahatan.
4. **Respons petugas publik** — pejabat mungkin **mengabaikan atau menyalahgunakan** rekomendasi algoritma dengan cara yang merusak kinerja sistem.

**Kasus penghentian yang dikutip:** **Illinois** dan **Los Angeles** (AS) menghentikan proyek AI karena kualitas data buruk dan sifat *black box*; **Denmark** menghentikan proyek identifikasi anak rentan dalam **kurang dari setahun**.

**Rekomendasi tata kelola:** **sistem hibrida** — AI digunakan **bersama** sistem tradisional, bukan menggantikannya, untuk mengurangi risiko dan mendorong adopsi. Organisasi pembangunan internasional harus membantu negara mengatasi *"tantangan yang berpusat pada manusia"* dalam adopsi teknologi baru.

**Sumber:** https://www.brookings.edu/articles/ai-for-social-protection-mind-the-people/

---

# BAGIAN D — REGULASI INDONESIA YANG MENGIKAT NADI

## D.1 UU No. 27 Tahun 2022 tentang Pelindungan Data Pribadi (UU PDP)

| Aspek | Isi |
|---|---|
| **Disahkan** | **17 Oktober 2022** |
| **Struktur** | **16 bab, 76 pasal** — kerangka hukum PDP menyeluruh pertama di Indonesia |
| **Masa transisi** | 2 tahun (berlaku penuh sejak Oktober 2024) |

### 🔴 Pasal 10 — Hak Keberatan atas Keputusan Otomatis (**PASAL PALING KRITIS UNTUK NADI**)
> *"Subjek Data Pribadi berhak untuk mengajukan keberatan atas tindakan pengambilan keputusan yang **hanya didasarkan pada pemrosesan secara otomatis, termasuk pemrofilan**, yang menimbulkan akibat hukum atau berdampak signifikan pada Subjek Data Pribadi."*
> Ketentuan lebih lanjut mengenai pengajuan keberatan atas pemrosesan secara otomatis diatur dalam Peraturan Pemerintah.

**Implikasi langsung:** NADI **secara hukum tidak boleh** membuat keputusan kelayakan bansos **semata-mata** berdasarkan output model. Wajib ada **human-in-the-loop** dan **mekanisme keberatan yang dapat diakses warga**. Ini bukan pilihan desain — ini kewajiban hukum. **Ini juga kunci pembeda NADI vs SyRI.**

### 🔴 Pasal 34 — Penilaian Dampak Pelindungan Data Pribadi (DPIA)
Pengendali Data wajib melakukan DPIA bila pemrosesan **berpotensi risiko tinggi** terhadap Subjek Data. Kondisi pemicu (Pasal 34 + praktik internasional):
- Memproses **data spesifik** (biometrik, kesehatan, genetika, **data anak**, keuangan) dalam skala besar;
- Menggunakan **teknologi baru** yang belum diuji risikonya;
- **Pemantauan atau profiling sistematis dan berkelanjutan** terhadap individu;
- Memproses data pribadi untuk **pengambilan keputusan otomatis yang berdampak signifikan** pada subjek data.

**Implikasi:** NADI memenuhi hampir **semua** pemicu → **DPIA WAJIB**. Sertakan ringkasan DPIA dalam deliverable datathon — ini akan sangat menonjol di mata juri.

### Dasar sah pemrosesan (6 basis legal)
(1) persetujuan Subjek Data; (2) pemenuhan kewajiban perjanjian; (3) pemenuhan kewajiban hukum Pengendali; (4) pelindungan kepentingan vital Subjek Data; (5) **pelaksanaan tugas kepentingan publik, pelayanan publik, atau kewenangan Pengendali**; (6) pemenuhan kepentingan sah lainnya.

→ Untuk NADI, basis paling tepat adalah **(3)** dan **(5)**, bukan *consent* — tetapi memilih basis non-consent **menambah** kewajiban transparansi dan hak keberatan, bukan mengurangi.

### Kewajiban Pengendali Data lain yang relevan
- Wajib **bertanggung jawab** atas pemrosesan dan **menunjukkan pertanggungjawaban** atas pemenuhan prinsip PDP (akuntabilitas).
- Wajib melakukan **perekaman terhadap seluruh kegiatan pemrosesan Data Pribadi** (*record of processing activities*) dan menyimpan bukti pemrosesan serta persetujuan — untuk keperluan **audit** dan penyelesaian sengketa hukum.
- Hak subjek data mencakup: memberi/menarik persetujuan, mengakses, memperbaiki, dan **meminta penghapusan** data yang tidak relevan atau dikumpulkan secara ilegal.

**Sumber:**
- https://peraturan.bpk.go.id/Details/229798/uu-no-27-tahun-2022
- https://jdih.komdigi.go.id/produk_hukum/view/id/832/t/undangundang+nomor+27+tahun+2022
- https://uupdp-info.id/pasal-10/
- https://learning.hukumonline.com/wp-content/uploads/2023/07/Undang-Undang-No.27-Tahun-2022-Hukumonline.pdf
- https://www.hukumku.id/post/dpia-dalam-uu-pdp
- https://www.hukumku.id/post/menunggu-rpp-pdp-langkah-menyiapkan-dpia-dari-sekarang

---

## D.2 Perpres No. 95 Tahun 2018 — Sistem Pemerintahan Berbasis Elektronik (SPBE)

- **Ditandatangani 2 Oktober 2018, diundangkan 5 Oktober 2018.**
- **Definisi SPBE:** penyelenggaraan pemerintahan yang memanfaatkan TIK untuk memberikan layanan kepada Pengguna SPBE.
- **Mengatur:** tata kelola, manajemen, **arsitektur**, dan peta rencana SPBE secara nasional, serta prinsip-prinsip pelaksanaan SPBE.
- **Arsitektur SPBE** = kerangka dasar yang mendeskripsikan integrasi **proses bisnis, data dan informasi, infrastruktur SPBE, aplikasi SPBE, dan keamanan SPBE** untuk menghasilkan layanan SPBE yang terintegrasi.

**Implikasi untuk NADI:** NADI harus dipetakan ke **Arsitektur SPBE daerah** (domain proses bisnis, domain data, domain aplikasi, domain keamanan). Menyebut ini menunjukkan kesiapan implementasi, bukan sekadar prototipe.

**Sumber:** https://peraturan.bpk.go.id/Details/96913/perpres-no-95-tahun-2018 | https://www.jogloabang.com/teknologi/perpres-95-2018-sistem-pemerintahan-berbasis-elektronik | https://kaltara.bpk.go.id/wp-content/uploads/2019/01/Tulisan-Hukum-Kaltara_Perpres-No-95_2018_SPBE-edit.pdf | https://www.menpan.go.id/site/berita-terkini/babak-baru-sistem-pemerintahan-berbasis-elektronik

---

## D.3 Perpres No. 39 Tahun 2019 — Satu Data Indonesia
Lihat **A.6**. Inti kewajiban untuk NADI: **Standar Data, Metadata, Interoperabilitas Data, Kode Referensi/Data Induk**, serta menghormati peran **Walidata** daerah.
**Sumber:** https://www.hukumonline.com/klinik/a/dasar-hukum-prinsip-satu-data-indonesia-lt5d19da645ce15/ | https://www.jogloabang.com/teknologi/perpres-39-2019-satu-data-indonesia

---

## D.4 Perpres No. 82 Tahun 2023 — Percepatan Transformasi Digital dan Keterpaduan Layanan Digital Nasional

- Mengatur percepatan transformasi digital melalui penyelenggaraan **Aplikasi SPBE Prioritas** dengan **mengutamakan integrasi dan interoperabilitas**.
- Dasar penugasan **PERURI sebagai GovTech Indonesia** → **INA Digital**, diresmikan Presiden **27 Mei 2024**.
- Fondasi yang dibangun: **Portal Administrasi Pemerintahan, Portal Pelayanan Publik, dan Identitas Digital Nasional**.

**Implikasi untuk NADI:** hindari membangun silo baru. Posisikan NADI sebagai **modul analitik yang interoperabel** dengan ekosistem INA Digital / SPBE Prioritas, bukan aplikasi berdiri sendiri.

**Sumber:** https://peraturan.bpk.go.id/Details/273981/perpres-no-82-tahun-2023 | https://peraturan.go.id/id/perpres-no-82-tahun-2023 | https://menpan.go.id/site/berita-terkini/presiden-keluarkan-perpres-percepatan-govtech-dan-interoperabilitas-layanan-digital-nasional | https://setkab.go.id/presiden-buka-spbe-summit-2024-dan-luncurkan-govtech-indonesia/ | https://jdih.menpan.go.id/dokumen-hukum/peraturan-presiden-republik-indonesia-nomor-82-tahun-2023-tentang-percepatan-transformasi-digital-da-1801

---

## D.5 SE Menkominfo No. 9 Tahun 2023 tentang Etika Kecerdasan Artifisial

| Aspek | Isi |
|---|---|
| **Ditandatangani** | **19 Desember 2023** |
| **Ditujukan kepada** | Pelaku usaha aktivitas pemrograman berbasis kecerdasan artifisial pada **Penyelenggara Sistem Elektronik (PSE) lingkup publik DAN privat** |
| **Tiga kebijakan** | (1) **nilai etika**; (2) **pelaksanaan nilai etika**; (3) **tanggung jawab** dalam pemanfaatan dan pengembangan AI |

**Nilai-nilai etika yang disebut (terverifikasi):** **inklusivitas, aksesibilitas, keamanan, kemanusiaan, kredibilitas dan akuntabilitas** (serta penekanan pada privasi & pelindungan data).

**Pendekatan pelaksanaan (terverifikasi sebagian):**
- AI diselenggarakan sebagai **pendukung aktivitas manusia**, khususnya meningkatkan kreativitas pengguna dalam menyelesaikan permasalahan dan pekerjaan.
- Penyelenggaraan yang **menjaga privasi dan data sehingga tidak ada individu yang dirugikan**.

⚠️ **Sifat hukum:** Surat Edaran = **pedoman/imbauan, bukan norma bersanksi**. Jangan mengklaim NADI "mematuhi regulasi AI yang mengikat" — yang mengikat adalah **UU PDP**. *Isi lengkap pasal per pasal SE ini TIDAK TERVERIFIKASI dalam riset ini.*

**Sumber:**
- https://jdih.komdigi.go.id/produk_hukum/view/id/883/t/surat+edaran+menteri+komunikasi+dan+informatika+nomor+9+tahun+2023
- https://jdih.kominfo.go.id/produk_hukum/view/id/883/t/surat+edaran+menteri+komunikasi+dan+informatika+nomor+9+tahun+2023
- https://www.kominfo.go.id/content/detail/53722/siaran-pers-no-582hmkominfo122023-tentang-resmi-terbitkan-se-menkominfo-jadi-pedoman-bagi-pse-publik-dan-privat/0/siaran_pers
- https://www.kompas.id/baca/ekonomi/2023/12/22/surat-edaran-panduan-etika-kecerdasan-artifisial-berlaku-bagi-penyelenggara-sistem-elektronik-publik-dan-privat
- https://www.hukumonline.com/pusatdata/detail/lt65855ded55dc2/surat-edaran-menteri-komunikasi-dan-informatika-nomor-9-tahun-2023/analysis/
- https://greennetwork.id/gna-knowledge-hub/kominfo-terbitkan-surat-edaran-terkait-etika-penggunaan-ai/

---

## D.6 Kebijakan AI sektor publik: Stranas KA & Perpres AI (status per Agustus 2026)

**Strategi Nasional Kecerdasan Artifisial (Stranas KA) 2020–2045**
- Disusun **BPPT (2020)**, diperkenalkan publik pada Hakteknas Agustus 2020.
- **8 bab:** pendahuluan; visi & misi; **etika dan kebijakan**; pengembangan talenta; **infrastruktur dan data**; riset dan inovasi industri; bidang prioritas; *quick wins* dan peta jalan.
- **5 klaster sektor prioritas:** kesehatan, **reformasi birokrasi**, pendidikan & riset, ketahanan pangan, mobilitas & kota cerdas.
- 📌 **NADI masuk klaster "reformasi birokrasi"** — sebutkan untuk menunjukkan keselarasan dengan kebijakan nasional.
- **Sumber:** https://korika.id/wp-content/uploads/2024/07/stranas-ka-2045.pdf | https://karya.brin.go.id/id/eprint/13918/ | https://oecd.ai/en/dashboards/policy-initiatives/national-ai-strategy-4627 | https://regulations.ai/regulations/RAI-ID-NA-SNKAIXX-2020

**Peta Jalan Kecerdasan Artifisial Nasional 2025–2029** (dipimpin Kementerian Komunikasi dan Digital) — mengoperasionalkan Stranas KA: etika & tata kelola, talenta, infrastruktur & data, riset & inovasi, investasi, *use case* prioritas, serta mekanisme monitoring & evaluasi.

**Status Perpres AI (⚠️ PERIKSA ULANG SEBELUM PRESENTASI — isu ini bergerak cepat):**
- Pemerintah memilih **pendekatan bertahap**: Perpres dulu, baru UU AI.
- **Dua rancangan Perpres:** (1) tentang **peta jalan** AI; (2) tentang **etika** AI. (Termasuk dalam Keppres No. 38/2025 tentang program penyusunan Perpres.)
- Target awal rampung September 2025; per siaran pers Komdigi **No. 138/HM-KKD/7/2026 (28 Juli 2026)**, kedua rancangan telah rampung dan **ditargetkan terbit pada 2026**.
- Karakter yang dilaporkan: mengatur **tiga tingkatan risiko** dan mitigasi kerugian; dilaporkan **tanpa sanksi**, memprioritaskan tata kelola dan kepercayaan publik.
- **Status per 25 Agustus 2026: BELUM TERKONFIRMASI TERBIT dengan nomor resmi.** ⛔ **Jangan menyebut nomor Perpres AI di slide.**
- **Sumber:** https://www.komdigi.go.id/berita/siaran-pers/detail/kemkomdigi-jadikan-perpres-ai-sebagai-langkah-awal-menuju-undang-undang-ai | https://katadata.co.id/digital/teknologi/69df0e8039515/dua-perpres-ai-segera-terbit-atur-tiga-tingkatan-risiko-dan-mitigasi-kerugian | https://www.hukumonline.com/berita/a/pemerintah-siapkan-perpres-ai-tanpa-sanksi--prioritaskan-tata-kelola-dan-kepercayaan-publik-lt69b8f1b63acd9/ | https://news.detik.com/berita/d-8433227/komdigi-ajukan-2-rancangan-perpres-tentang-ai-target-segera-terbit | https://jdih.banyuwangikab.go.id/berita/detail/pemerintah-siapkan-perpres-ai-tanpa-sanksi-prioritaskan-tata-kelola-dan-kepercayaan-publik

---

# BAGIAN E — TABEL PERBANDINGAN (SIAP PAKAI UNTUK SLIDE)

## E.1 Tabel Utama — Sistem Indonesia

**Legenda:** ✅ Ya (ada bukti publik) · 🟡 Sebagian / dengan syarat · ❌ Tidak ditemukan bukti publik · ❔ Tidak terverifikasi

| Sistem | Pemilik | Prediktif? | Explainable? | Rekomendasi lintas OPD? | Simulasi kebijakan? | Monitoring outcome? |
|---|---|---|---|---|---|---|
| **SIKS-NG** | Kemensos | ❌ | ❌ (tidak ada model) | ❌ (hanya program Kemensos) | ❌ | 🟡 output penyaluran saja |
| **Cek Bansos** (warga) | Kemensos | ❌ | ❌ | ❌ | ❌ | ❌ |
| **DTSEN** | BPS (Inpres 4/2025) | 🟡 PMT = prediksi kondisi **saat ini**, bukan risiko ke depan | ❌ | ❌ (registry, bukan perencana) | ❌ | ❌ |
| **P3KE** | Kemenko PMK / BKKBN | 🟡 PMT desil 1–10 | ❌ | ❌ | ❌ | ❌ |
| **Regsosek 2022** | BPS | ❌ (pendataan) | ❌ | ❌ | ❌ | ❌ |
| **SEPAKAT** | Bappenas | ❌ (deskriptif/diagnostik) | ❌ | ✅ **level wilayah/kebijakan** (pohon masalah → opsi intervensi + target lokasi) | 🟡 alokasi anggaran; *what-if* ❔ | ✅ **RPJMD/SDGs + dekomposisi**, level agregat |
| **Satu Data / data.go.id** | Kemenkomdigi & Bappenas | ❌ | ❌ | ❌ | ❌ | ❌ |
| **SIGA / PK / KRS** | Kemendukbangga (BKKBN) | 🟡 **skrining risiko berbasis ATURAN** (air, sanitasi, 4 Terlalu) | ✅ **trivially explainable** (aturan eksplisit) | ❌ | ❌ | 🟡 verval KRS berkala |
| **SIM-PKH / e-PKH** | Kemensos | ❌ | ❌ | ❌ | ❌ | ✅ **verifikasi komitmen sekolah & kesehatan per keluarga** |
| **SIMNANGKIS DIY** | Bappeda DIY | ❌ | ❌ | ✅ **sinergi program lintas OPD + CSR** | ❌ | 🟡 realisasi anggaran/output + tracking SDGs |
| **SIPINTER Purbalingga** | Pemkab Purbalingga | ❌ | ❌ | ✅ pelaporan intervensi lintas sektor (pentahelix) | ❌ | 🟡 konsep melacak "hasil" ❔ detail teknis |
| **Carik Jakarta** | DPPAPP DKI | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Smart Kampung Banyuwangi** | Pemkab Banyuwangi | ❌ | ❌ | 🟡 pencocokan *jenis kemiskinan → jenis intervensi* | ❌ | ❌ |

## E.2 Tabel Pembanding Internasional

| Sistem | Negara / Pemilik | Prediktif? | Explainable? | Rekomendasi lintas sektor? | Simulasi kebijakan? | Monitoring outcome? |
|---|---|---|---|---|---|---|
| **SISBEN IV** | Kolombia / DNP | 🟡 PMT + data analytics deteksi inkonsistensi | ❌ (algoritma dikritik *ad-hoc*) | ❌ | ❌ | ❌ |
| **Cadastro Único + Bolsa Família** | Brasil / MDS–Caixa | 🟡 seleksi otomatis berbasis aturan pendapatan | ❌ | ❌ | ❌ | 🟡 kondisionalitas sekolah & imunisasi |
| **Listahanan / NHTS-PR** | Filipina / DSWD | 🟡 PMT (FAF 46 variabel) | ❌ (tapi ada **mekanisme appeal**) | ❌ | ❌ | ❌ |
| **NSER / BISP** | Pakistan | 🟡 PMT 0–100, **dynamic registry** | 🟡 **skor bisa dicek warga via CNIC**, alasannya tidak | ❌ | ❌ | ❌ |
| **Enhanced Single Registry** | Kenya / NSPS | ❌ | ❌ | 🟡 **deteksi duplikasi manfaat lintas 4 program** | ❌ | ❌ |
| **Ubudehe** | Rwanda / LODA | ❌ (kategorisasi komunitas) | ✅ **musyawarah = transparan secara sosial** (meski kriteria dikritik) | ❌ | ❌ | ❌ |
| **DBT + registry negara bagian** | India | ❌ | ❌ | 🟡 satu identitas untuk banyak skema | ❌ | ❌ |
| **Novissi (Togo)** | Togo + akademisi | ✅ **ML asli (AUC 0,70)** | ❌ | ❌ | ❌ | ❌ |
| **SyRI** ⛔ | Belanda | ✅ skor risiko kecurangan | ❌ **DILARANG PENGADILAN karena buram** | ❌ | ❌ | ❌ |
| **Robodebt** ⛔ | Australia | 🟡 *income averaging* otomatis | ❌ | ❌ | ❌ | ❌ |
| **Social Card** ⛔ | Serbia | 🟡 otomasi 130 kategori data | ❌ | ❌ | ❌ | ❌ |

## E.3 Versi Ringkas untuk Satu Slide (5 baris, paling jujur & paling kuat)

| Sistem | Prediktif risiko **ke depan** | Penjelasan **per keluarga** | Rekomendasi ke **OPD spesifik** | Simulasi **what-if** | Monitoring **outcome keluarga** |
|---|:--:|:--:|:--:|:--:|:--:|
| **DTSEN / SIKS-NG** (data & penyaluran) | ❌ | ❌ | ❌ | ❌ | ❌ |
| **SEPAKAT** (perencanaan wilayah) | ❌ | ❌ | 🟡 level wilayah | 🟡 alokasi anggaran | ✅ level agregat |
| **SIMNANGKIS / SIPINTER** (koordinasi daerah) | ❌ | ❌ | ✅ | ❌ | 🟡 output/anggaran |
| **SIGA-KRS / e-PKH** (skrining & kepatuhan) | 🟡 aturan | ✅ aturan | ❌ | ❌ | ✅ terbatas domain |
| **NADI (usulan)** | ✅ | ✅ | ✅ | ✅ | ✅ |

> **Catatan wajib di bawah slide:** *"Penilaian berdasarkan bukti yang tersedia publik per Agustus 2026. Tanda ❌ berarti tidak ditemukan bukti publik, bukan bukti ketiadaan. Sistem yang dibandingkan memiliki mandat berbeda-beda — perbandingan ini bukan penilaian mutu."*

---

# BAGIAN F — RUMUSAN KLAIM KEBARUAN NADI (aman vs berbahaya)

## F.1 ⛔ KLAIM YANG HARUS DIHINDARI (mudah dipatahkan)

| Klaim berbahaya | Kenapa dipatahkan | Pematah |
|---|---|---|
| "Belum ada sistem yang memakai AI/ML untuk kemiskinan di Indonesia" | Riset ML untuk PMT Indonesia sudah dipublikasikan, sebagian dari ekosistem BPS/STIS | arXiv 2503.04300; Wobcke & Mariyah (2023) |
| "Belum ada yang memprediksi kemiskinan" | PMT **adalah** model prediktif; dipakai P3KE/DTSEN, Listahanan, NSER, SISBEN | P3KE (data.go.id), BISP, DSWD |
| "Belum ada yang menghubungkan data ke perencanaan & anggaran" | SEPAKAT sudah punya modul perencanaan + penganggaran + evaluasi sejak 2018 | SEPAKAT (Bappenas) |
| "Belum ada koordinasi intervensi lintas OPD berbasis sistem" | SIMNANGKIS DIY & SIPINTER Purbalingga sudah melakukannya | simnangkis.jogjaprov.go.id; Pemkab Purbalingga |
| "Belum ada data by-name-by-address dengan geolokasi" | Smart Kampung Banyuwangi sudah geokoding rumah keluarga miskin | smartkampung.id |
| "Belum ada monitoring keluarga penerima" | e-PKH verifikasi komitmen sekolah & kesehatan; Bolsa Família kondisionalitas | Kemensos; MDS Brasil |
| "Warga belum bisa tahu skornya" | Pakistan memungkinkan cek skor PMT via CNIC | bisp.gov.pk |
| "NADI mematuhi regulasi AI Indonesia" | Belum ada Perpres AI yang terbit; SE 9/2023 tidak bersanksi | Komdigi, Agustus 2026 |

## F.2 ✅ KLAIM YANG AMAN & TAHAN UJI

Rumuskan kebaruan NADI pada **kombinasi**, bukan pada komponen tunggal:

1. **"Dari peringkat statis ke risiko dinamis."**
   *"DTSEN memberi tahu siapa yang miskin **hari ini** (desil, PMT). Yang belum ada: siapa yang **akan** jatuh ke desil bawah dalam 6–12 bulan ke depan, dan karena tekanan apa. NADI menambahkan dimensi waktu pada data yang sudah ada."*

2. **"Dari skor tanpa alasan ke skor dengan alasan."**
   *"Pakistan menampilkan skor PMT ke warga; SyRI justru dilarang pengadilan Belanda karena menyembunyikan modelnya. NADI menampilkan **alasan per keluarga** — variabel apa yang mendorong risiko naik — sehingga pendamping bisa memverifikasi dan warga bisa membantah. Ini bukan fitur estetik; ini pemenuhan UU PDP Pasal 10."*

3. **"Dari koordinasi program ke penugasan intervensi."**
   *"SIMNANGKIS mensinkronkan program lintas OPD pada level anggaran. SEPAKAT menghasilkan opsi intervensi pada level wilayah. NADI menurunkannya satu tingkat: **keluarga X → butuh intervensi Y → OPD Z → tenggat W → status hasil**."*

4. **"Loop tertutup dengan umpan balik ke model."**
   *"Yang tidak ditemukan di sistem manapun yang kami teliti — Indonesia maupun internasional: intervensi yang tercatat kembali menjadi data latih. NADI belajar dari apa yang berhasil, bukan hanya memprediksi sekali."*

5. **"Responsible AI sebagai fitur, bukan disclaimer."**
   *"NADI dirancang dengan tiga alasan pelarangan SyRI sebagai checklist terbalik: (a) tidak buram — setiap skor bisa dijelaskan; (b) minimisasi data — hanya variabel yang dibenarkan; (c) tujuan spesifik — hanya untuk perluasan layanan, tidak pernah untuk pemutusan bantuan atau deteksi kecurangan."*

6. **"Skor bukan keputusan."**
   *"Belajar dari Robodebt: model NADI tidak pernah menjadi dasar tunggal keputusan yang merugikan warga. Output NADI adalah **daftar prioritas kunjungan**, bukan keputusan pemutusan bantuan. Keputusan tetap di Musdes/Muskel dan SK kepala daerah."*

## F.3 Kalimat pembuka slide "Kebaruan" (siap salin)

> **"Kami tidak mengklaim NADI adalah sistem data kemiskinan pertama di Indonesia — sudah ada DTSEN, SIKS-NG, SEPAKAT, SIMNANGKIS, dan puluhan dashboard daerah. Kami memetakan 13 sistem Indonesia dan 11 sistem internasional. Yang kami temukan: semuanya berhenti sebelum satu langkah yang sama — menjelaskan risiko per keluarga dan menutup loop ke tindakan. Di situlah NADI berdiri."**

---

# BAGIAN G — ANTISIPASI PERTANYAAN JURI (dengan jawaban)

**Q1. "Ini kan sudah ada SEPAKAT. Apa bedanya?"**
> SEPAKAT bekerja pada level **wilayah dan dokumen perencanaan** — diagnosis kemiskinan daerah, pohon masalah, opsi intervensi dengan target lokasi, lalu evaluasi lewat dekomposisi pertumbuhan-redistribusi. NADI bekerja pada level **keluarga dan tindakan** — siapa yang berisiko, kenapa, siapa yang harus datang, dan apa hasilnya. Keduanya komplementer: SEPAKAT menjawab "program apa untuk kecamatan mana", NADI menjawab "keluarga mana dulu di kecamatan itu, dan oleh OPD mana".

**Q2. "Bukankah PMT/desil DTSEN sudah prediksi?"**
> Betul, dan kami sebutkan itu secara eksplisit di dokumen riset kami. PMT memprediksi **kesejahteraan saat ini** dari variabel proksi. Yang tidak dilakukan PMT adalah memprediksi **perubahan** — keluarga desil 5 yang kepala keluarganya kehilangan pekerjaan dan punya anak SMP terancam putus sekolah tidak berubah desilnya sampai pendataan berikutnya. Itu jendela waktu yang hilang.

**Q3. "Apa bedanya NADI dengan SyRI yang dilarang pengadilan Belanda?"** ← **PERTANYAAN PALING MEMATIKAN**
> Tiga alasan pengadilan Den Haag melarang SyRI kami pakai sebagai checklist desain terbalik:
> 1. **SyRI buram** → NADI menampilkan kontribusi variabel per keluarga ke operator dan menyediakan penjelasan yang dapat disampaikan ke warga.
> 2. **SyRI mengumpulkan terlalu banyak data** → NADI hanya memakai variabel dari DTSEN dan sumber administratif yang sudah sah dikumpulkan untuk tujuan kesejahteraan; kami tidak menambah pengumpulan data baru.
> 3. **Tujuan SyRI tidak spesifik** → tujuan NADI dibatasi secara tertulis: **memprioritaskan kunjungan dan perluasan layanan.** NADI **dilarang** dipakai untuk deteksi kecurangan atau pemutusan bantuan. Dan berbeda dari SyRI yang menyasar kecurangan, NADI menyasar **inklusi** — kesalahan yang kami minimalkan adalah *exclusion error*, bukan *inclusion error*.

**Q4. "Kalau modelnya salah dan orang tidak dapat bantuan, siapa yang tanggung jawab?"**
> Model NADI tidak pernah memutus bantuan. Output NADI adalah daftar prioritas kunjungan — **hanya bisa menambah**, tidak bisa mengurangi. Keputusan kelayakan tetap melalui Musdes/Muskel dan SK kepala daerah, sesuai alur SIKS-NG yang berlaku. Ini juga kewajiban hukum: **UU PDP Pasal 10** melarang keputusan yang **hanya** didasarkan pemrosesan otomatis bila berdampak signifikan.

**Q5. "Sudah ada DPIA?"**
> NADI memicu hampir semua kriteria kewajiban DPIA di **UU PDP Pasal 34**: skala besar, profiling sistematis, data anak, dan keputusan otomatis berdampak signifikan. Kami menyertakan kerangka DPIA sebagai bagian dari deliverable, bukan sebagai lampiran opsional.

**Q6. "Bagaimana kalau modelnya bias terhadap kelompok tertentu?"**
> Ini persis yang terjadi di Serbia — Amnesty International mendokumentasikan Social Card memperparah eksklusi Roma dan penyandang disabilitas. Mitigasi kami: **audit dampak diferensial** yang wajib dijalankan per rilis model, memecah metrik *exclusion error* per kelompok rentan (disabilitas, lansia, perempuan kepala keluarga, wilayah 3T), dengan ambang yang menghentikan rilis bila kesenjangan melewati batas.

**Q7. "Apakah ini menggantikan pendataan lapangan / musyawarah desa?"**
> Tidak, dan itu justru posisi yang didukung bukti. Studi Togo di *Nature* (2022) menemukan pendekatan ML **menaikkan** exclusion error 9–35% dibanding metode yang punya social registry komprehensif. Indonesia **punya** registry itu (DTSEN, 290,13 juta individu). Jadi peran AI di sini bukan menggantikan, tapi **memprioritaskan** — menentukan rumah mana yang dikunjungi pendamping lebih dulu ketika jumlah pendamping terbatas. Musdes tetap pemutus.

**Q8. "Data DTSEN kan sudah dipadankan Dukcapil dan dimutakhirkan BPS. Buat apa NADI?"**
> DTSEN menjawab pertanyaan "siapa dan seberapa". NADI menjawab "siapa dulu, kenapa, oleh siapa, dan apakah berhasil". Kami tidak membangun registry tandingan — kami membangun lapisan analitik dan alur kerja di atasnya.

**Q9. "Apa dasar hukum NADI memproses data pribadi?"**
> Bukan *consent*, melainkan **UU PDP Pasal 20 ayat (2) huruf c dan e** — pemenuhan kewajiban hukum Pengendali dan pelaksanaan tugas kepentingan publik/pelayanan publik. Konsekuensinya: kewajiban transparansi dan hak keberatan justru **lebih berat**, dan itu kami penuhi lewat explainability + kanal sanggah.

**Q10. "Kalau bagus, kenapa belum ada yang buat?"** *(jawab dengan jujur, jangan defensif)*
> Sebagian sudah ada, terpisah-pisah: SIGA menandai risiko (berbasis aturan), e-PKH memantau outcome keluarga, SIMNANGKIS mengoordinasi lintas OPD, SEPAKAT merencanakan intervensi, BPS meneliti ML untuk PMT. Yang belum ada adalah **satu alur kerja yang menyambungkan kelimanya**. Hambatannya bukan teknologi — hambatannya kelembagaan (data lintas OPD) dan regulasi (UU PDP baru berlaku penuh Oktober 2024). Justru sekarang momennya: DTSEN sudah tunggal, Perpres 82/2023 mewajibkan interoperabilitas, dan kerangka etika AI sedang dibentuk.

---

# BAGIAN H — IMPLIKASI KONKRET UNTUK PEMBANGUNAN NADI

## H.1 Skema Database
1. **Gunakan struktur DTSEN sebagai kanonik**: entitas `individu` + `keluarga` (bukan hanya rumah tangga), kunci `NIK` yang sudah dipadankan Dukcapil, atribut `desil` (1–10) sebagai kolom, bukan sebagai target model.
2. **Tabel `desil_history`** dengan stempel waktu per versi DTSEN — inilah bahan mentah untuk prediksi *perubahan*, sesuatu yang tidak dilakukan sistem manapun. DTSEN sendiri sudah berversi (Versi 3 Tahun 2026), jadi *time series* tersedia secara struktural.
3. **Tabel `intervensi`** dengan kolom `opd_penanggung_jawab`, `program`, `tanggal_penugasan`, `tanggal_realisasi`, `status_outcome` — meniru struktur SIPINTER ("siapa butuh, bantuan apa, organisasi mana, kapan, hasilnya") dan realisasi triwulanan SIMNANGKIS.
4. **Tabel `penjelasan_skor`** menyimpan kontribusi fitur per keluarga per versi model — ini artefak kepatuhan UU PDP Pasal 10, bukan sekadar fitur UI. Harus **immutable dan bertanggal**.
5. **Tabel `audit_pemrosesan`** — UU PDP mewajibkan **perekaman seluruh kegiatan pemrosesan Data Pribadi** untuk audit. Bangun dari awal, jangan ditambal belakangan.
6. **Tabel `keberatan`** (mengikuti pola usul/sanggah SIKS-NG dan appeal Listahanan) dengan status, penanggung jawab, dan tenggat.
7. **Variabel yang terbukti dipakai secara internasional** (untuk fitur model): akses air minum layak & sanitasi (SIGA/KRS), kepemilikan aset & sumber pendapatan (DTSEN, Regsosek), komposisi keluarga & pendidikan anggota (Listahanan FAF), status pekerjaan dari BPJS Ketenagakerjaan (sudah diintegrasikan SIKS-NG), **informasi geospasial** (Regsosek, Smart Kampung).
8. **Metadata wajib Perpres 39/2019**: setiap tabel harus punya standar data, metadata, dan kode referensi wilayah (kode BPS/Kemendagri) agar bisa diadopsi Walidata daerah.

## H.2 Fitur Model
1. **Target = perubahan, bukan level.** Prediksi `P(turun desil dalam periode berikutnya)` atau `P(masuk desil 1–4)`, bukan memprediksi desil itu sendiri — karena desil sudah disediakan BPS.
2. **Sertakan fitur spasial.** Bukti Indonesia sangat kuat: Moran's I = 0,411 (p<0,01); *spatial clustering* menurunkan exclusion error 28% → 20%. Ini justifikasi metodologis yang bisa dikutip langsung.
3. **Metrik utama = exclusion error, dipecah per kelompok.** Bukan akurasi. Pelajaran Serbia & India: eksklusi kelompok rentan adalah kegagalan utama sistem semacam ini.
4. **Explainability wajib, bukan opsional.** Kontribusi fitur per keluarga, diterjemahkan ke bahasa yang bisa dibacakan pendamping ke warga ("keluarga ini diprioritaskan karena: anak usia sekolah tanpa status sekolah aktif; sumber air tidak layak; kepala keluarga tidak tercatat aktif di BPJS Ketenagakerjaan").
5. **Baseline wajib dilaporkan**: bandingkan dengan (a) desil DTSEN apa adanya, (b) PMT/regresi linear. Bila NADI tidak mengalahkan desil DTSEN, katakan jujur — juri lebih menghargai itu daripada klaim kosong.
6. **Jangan gunakan variabel proksi etnis/agama/asal daerah** — pelajaran SyRI (target lingkungan minoritas) dan Serbia (Roma).

## H.3 UI/UX Aplikasi
1. **Tiga persona, tiga tampilan:** (a) **Pendamping/operator desa** — daftar prioritas kunjungan hari ini + alasan per keluarga; (b) **Kepala OPD** — antrean penugasan + SLA + status outcome; (c) **Bappeda/TKPK** — agregat, simulasi anggaran, capaian RPJMD/SDGs (sambungkan konsep ke SEPAKAT, jangan duplikasi).
2. **Setiap skor WAJIB ditemani tombol "Kenapa?"** — tidak boleh ada angka telanjang di layar manapun. Ini pembeda visual paling kuat di demo, sekaligus bukti kepatuhan Pasal 10.
3. **Tombol "Saya tidak setuju"** pada setiap kartu keluarga → membuat entri di tabel `keberatan`. Ini implementasi visual UU PDP Pasal 10 yang bisa langsung ditunjukkan ke juri dalam 5 detik.
4. **Banner permanen: "Rekomendasi, bukan keputusan."** Antisipasi Robodebt, terlihat di setiap layar.
5. **Panel "Audit Keadilan"** yang menampilkan exclusion error per kelompok rentan — letakkan di dalam aplikasi, bukan hanya di dokumen. Ini yang membedakan NADI dari Social Card Serbia secara visual.
6. **Peta by-name-by-address** dengan geokoding (Smart Kampung sudah membuktikan kelayakannya di level desa) — tapi batasi akses lokasi presisi hanya untuk pendamping wilayah tersebut (minimisasi data).
7. **Jangan buat kanal usul/sanggah tandingan.** Tautkan ke Cek Bansos/SIKS-NG yang sudah dipakai warga; NADI cukup menampilkan status dan mempercepat verifikasi.
8. **Tampilkan versi model & tanggal data** di footer setiap halaman — praktik akuntabilitas yang absen di semua sistem yang diteliti.

## H.4 Batas Tegas yang Harus Ditulis di Dokumen & Slide
- NADI **tidak** memutus, mengurangi, atau menunda bantuan siapa pun.
- NADI **tidak** dipakai untuk deteksi kecurangan.
- NADI **tidak** mengumpulkan data baru di luar yang sudah sah dikumpulkan untuk tujuan kesejahteraan.
- Output NADI **tidak** menjadi dasar tunggal keputusan apa pun; Musdes/Muskel dan SK kepala daerah tetap pemutus.
- Setiap keluarga berhak mengetahui alasan penilaian dan mengajukan keberatan.

---

# BAGIAN I — PERTANYAAN TERBUKA (belum terjawab riset ini)

1. **Fitur SEPAKAT terkini (2025–2026)** — apakah sudah ada modul prediktif/simulasi baru? Situs 403; perlu akses langsung atau kontak Bappenas.
2. **Cakupan SEPAKAT terkini** — apakah masih 129 kab/kota + 7 provinsi, atau sudah berkembang/berkurang?
3. **Fitur portal DTSEN (dtsen.data.go.id)** — apakah menyediakan API? Layanan usul/sanggah? Level akses pemda?
4. **Bagaimana persisnya desil DTSEN dihitung** — apakah masih PMT seperti P3KE, model apa, variabel apa? Metodologi resmi belum ditemukan.
5. **Isi lengkap SE Kominfo 9/2023** pasal per pasal.
6. **Status Perpres AI per hari presentasi** — sudah terbit atau belum, dengan nomor berapa.
7. **Apakah sudah ada RPP UU PDP** yang mengatur tata cara pengajuan keberatan atas pemrosesan otomatis (diamanatkan Pasal 10)? Ini menentukan bentuk konkret fitur keberatan NADI.
8. **Spesifikasi teknis SIPINTER Purbalingga** — apakah sudah melacak outcome keluarga secara longitudinal?
9. **Angka pengguna aplikasi Cek Bansos** dan volume usul/sanggah per tahun — berguna untuk mengukur potensi partisipasi.
10. **Apakah ada pemda yang sudah menjalankan model prediktif kemiskinan dalam produksi** (bukan riset)? Belum ditemukan, tapi absennya bukti bukan bukti absennya.

---

## Daftar Sumber Utama (rekap)

**Indonesia — sistem**
1. https://journal.unismuh.ac.id/index.php/kolaborasi/article/download/16182/7811 — SIKS-NG (jurnal)
2. https://www.komdigi.go.id/berita/artikel/detail/aplikasi-cek-bansos-inovasi-kementerian-sosial-yang-libatkan-masyarakat-untuk-pengelolaan-bansos-tepat-sasaran — Cek Bansos
3. https://sepakat.bappenas.go.id/ — SEPAKAT
4. https://tubankab.go.id/entry/slug-34803851b51c026e1075f0f86e2903a9 — modul & cakupan SEPAKAT
5. https://dtsen.data.go.id/ — DTSEN
6. https://www.beritasatu.com/nasional/3021260/bps-data-desil-sudah-mencakup-29013-juta-individu — angka DTSEN
7. https://data.go.id/dataset/dataset/data-p3ke — P3KE
8. https://data.go.id/ — Satu Data Indonesia
9. https://siga.kemendukbangga.go.id/dataset — SIGA
10. https://simnangkis.jogjaprov.go.id/ — SIMNANGKIS DIY
11. https://setda.purbalinggakab.go.id/soft-launching-purbalingga-gotong-royong-pemkab-satukan-kekuatan-lintas-sektor-percepat-penanggulangan-kemiskinan/ — SIPINTER
12. https://carik.jakarta.go.id/dashboard/ — Carik Jakarta
13. https://smartkampung.id/spbedesa/dtks — Smart Kampung Banyuwangi

**Indonesia — regulasi**
14. https://peraturan.bpk.go.id/Details/229798/uu-no-27-tahun-2022 — UU PDP
15. https://uupdp-info.id/pasal-10/ — Pasal 10 UU PDP
16. https://peraturan.bpk.go.id/Details/96913/perpres-no-95-tahun-2018 — SPBE
17. https://peraturan.bpk.go.id/Details/273981/perpres-no-82-tahun-2023 — Transformasi Digital
18. https://jdih.komdigi.go.id/produk_hukum/view/id/883/t/surat+edaran+menteri+komunikasi+dan+informatika+nomor+9+tahun+2023 — SE Etika AI
19. https://korika.id/wp-content/uploads/2024/07/stranas-ka-2045.pdf — Stranas KA

**Internasional — sistem**
20. https://documents1.worldbank.org/curated/en/364521468019731045/pdf/32759.pdf — SISBEN
21. https://globalallianceagainsthungerandpoverty.org/country-example/brazil-single-registry-cadunico/ — CadÚnico
22. https://documents1.worldbank.org/curated/en/830621542293177821/pdf/132110-PN-P162701-SPL-Policy-Note-16-Listahanan.pdf — Listahanan
23. https://bisp.gov.pk/Detail/NzI5YTMyYTMtYjE1My00NGUwLTgwYTItZWUwYTZkYWZjYmNj — NSER Pakistan
24. https://www.nsps.socialprotection.go.ke/enhanced-single-registry — ESR Kenya
25. https://www.loda.gov.rw/updates/news-detail/citizens-start-classifying-their-households-into-new-ubudehe-categories — Ubudehe
26. https://dbtbharat.gov.in/static-page-content/spagecont?id=1 — DBT India

**Responsible AI / kontroversi**
27. https://www.loc.gov/item/global-legal-monitor/2020-03-13/netherlands-court-prohibits-governments-use-of-ai-software-to-detect-welfare-fraud/ — SyRI
28. https://algorithmwatch.org/en/syri-netherlands-algorithm/ — SyRI
29. https://www.abc.net.au/news/2023-07-07/robodebt-royal-commission-findings-revealed/102531450 — Robodebt
30. https://www.amnesty.org/en/latest/research/2023/12/trapped-by-automation-poverty-and-discrimination-in-serbias-welfare-state/ — Serbia
31. https://www.brookings.edu/articles/ai-for-social-protection-mind-the-people/ — sintesis risiko

**Bukti metodologis ML**
32. https://arxiv.org/html/2503.04300 — Spatial ML untuk targeting kemiskinan Indonesia
33. https://www.nature.com/articles/s41586-022-04484-9 — Togo Novissi (Nature 2022)
34. https://journals.sagepub.com/doi/abs/10.3233/SJI-230033 — ML + augmentasi data dalam PMT
35. https://www.sciencedirect.com/science/article/abs/pii/S0304387818305819 — kritik akurasi PMT

---

*Dokumen ini adalah hasil riset desk per 25 Agustus 2026. Setiap penilaian "tidak ada fitur X" berarti "tidak ditemukan bukti publik", bukan bukti ketiadaan. Verifikasi ulang butir-butir di Bagian I sebelum presentasi.*
