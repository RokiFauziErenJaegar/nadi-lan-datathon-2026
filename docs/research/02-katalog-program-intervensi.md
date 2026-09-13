# Katalog Program Perlindungan Sosial & Pengentasan Kemiskinan Indonesia (2025–2026)
### Dokumen Riset untuk Seed Data Knowledge Base Aplikasi NADI — Kabupaten Pringsewu, Lampung

| Meta | Isi |
|---|---|
| Versi dokumen | 1.0 |
| Tanggal riset | 25 Agustus 2026 |
| Cakupan | Program nasional (APBN), provinsi (Lampung), kabupaten (Pringsewu), dan Dana Desa/Pekon |
| Fokus | Program yang **dapat dieksekusi atau dikoordinasikan di tingkat kabupaten** |
| Metode | 20+ pencarian web (Bahasa Indonesia & Inggris) + WebFetch ke sumber resmi/regulasi |
| Status | **Riset sekunder.** Belum diverifikasi silang dengan dokumen APBD Pringsewu, DPA OPD, atau Perbup. |

---

## 0. CARA MEMBACA DOKUMEN INI

### 0.1 Legenda Tingkat Keyakinan Angka

| Tanda | Arti | Aksi untuk tim build |
|---|---|---|
| 🟢 **PASTI** | Angka dikonfirmasi minimal 2 sumber independen, atau 1 sumber resmi pemerintah (kementerian/BPS/JDIH). | Boleh langsung jadi seed data produksi. |
| 🟡 **CUKUP KUAT** | Angka konsisten di banyak sumber media/pemda, tapi belum ditemukan dokumen regulasi aslinya. | Boleh jadi seed data, beri flag `needs_verification: true`. |
| 🟠 **PERKIRAAN** | Angka bervariasi antar sumber, atau merupakan hasil turunan/pembagian. | Jangan tampilkan sebagai angka pasti di UI. Tampilkan sebagai rentang atau "sekitar". |
| 🔴 **TIDAK DITEMUKAN** | Tidak berhasil dikonfirmasi dalam riset ini. | **JANGAN diisi angka.** Kosongkan field, tandai untuk riset lanjutan. |

### 0.2 Peringatan Penting

> ⚠️ **Banyak nominal bansos beredar di blog/portal berita non-resmi dengan angka yang saling bertentangan.**
> Contoh nyata yang ditemukan dalam riset ini: komponen **lansia PKH** disebut Rp3.000.000/tahun oleh beberapa blog, padahal sumber yang lebih kredibel (Detik, Liputan6, Nova/Grid) konsisten menyebut **Rp2.400.000/tahun**. Dokumen ini memakai angka yang paling banyak dikonfirmasi dan menandai perbedaannya secara eksplisit.

> ⚠️ **DTKS sudah tidak berlaku sebagai basis penyaluran.** Sejak Inpres 4/2025, basis data tunggal adalah **DTSEN**. Namun banyak juknis program (mis. PIP) masih menuliskan "DTKS" di dokumen lamanya. Aplikasi NADI harus memakai **DTSEN + desil** sebagai kunci utama.

---

## 1. FONDASI TARGETING: DTSEN & DESIL KESEJAHTERAAN

Ini adalah **komponen paling penting** untuk arsitektur data NADI. Hampir semua program di bawah memakai DTSEN sebagai gerbang kelayakan.

| Atribut | Isi | Keyakinan |
|---|---|---|
| Nama resmi | Data Tunggal Sosial dan Ekonomi Nasional | 🟢 |
| Singkatan | DTSEN | 🟢 |
| Dasar hukum | **Instruksi Presiden (Inpres) Nomor 4 Tahun 2025**, ditandatangani Presiden Prabowo Subianto pada 5 Februari 2025 | 🟢 |
| Penyusun & pengelola | **Badan Pusat Statistik (BPS)** menyusun & mengelola; **Kemensos** melakukan pemutakhiran/ground check | 🟢 |
| Menggantikan | DTKS (Kemensos), P3KE (BKKBN), Regsosek (BPS) — ketiganya diintegrasikan | 🟢 |
| Portal resmi | https://dtsen.data.go.id/ | 🟢 |
| Mulai ground check | Maret 2025 | 🟡 |
| Struktur klasifikasi | **Desil 1–10.** Seluruh keluarga diperingkat berdasarkan tingkat kesejahteraan relatif, dibagi 10 kelompok, masing-masing ±10% populasi. Desil 1 = 10% termiskin. Desil 10 = 10% terkaya. | 🟢 |
| Mekanisme perbaikan data | Usul & Sanggah via aplikasi **Cek Bansos** (fitur "Daftar Usulan"); verifikasi lapangan oleh Pendamping PKH, TKSK, operator Dinsos; **Musyawarah Desa/Kelurahan (Muskel)** bersama perangkat pekon, BPD/LHP, RT/RW | 🟡 |

### 1.1 Peta Desil → Kelayakan Program (KRUSIAL untuk rule engine NADI)

| Desil | Label umum | Program yang umumnya menjangkau | Keyakinan |
|---|---|---|---|
| Desil 1 | Sangat miskin / miskin ekstrem | PKH, Sembako, PBI-JKN, Sekolah Rakyat (prioritas), BLT Dana Desa (prioritas), RST/Rutilahu, ATENSI | 🟢 |
| Desil 2 | Miskin | PKH, Sembako, PBI-JKN, Sekolah Rakyat, PIP | 🟢 |
| Desil 3 | Rentan miskin | Sembako, PBI-JKN, PIP, Sekolah Rakyat (jika kuota belum penuh) | 🟡 |
| Desil 4 | Rentan miskin | **PBI-JKN Pusat masih menjangkau desil 1–4** (Peraturan Kemensos No. 3/2025); BLT Kesra 2025 menjangkau desil 1–4 | 🟡 |
| Desil 5 | Menengah bawah | Umumnya di luar bansos reguler; sasaran program pemberdayaan/KUR/Prakerja | 🟠 |
| Desil 6–10 | Menengah ke atas | Bukan sasaran bansos | 🟢 |

> **Catatan desain NADI:** simpan `desil` sebagai integer 1–10 pada entitas keluarga, dan simpan `desil_min`/`desil_max` pada entitas program. Ini memungkinkan matching otomatis.

---

## 2. TABEL MASTER KATALOG PROGRAM

Tabel ringkas untuk seed awal. Detail lengkap tiap program ada di Bagian 3.

| # | Kode | Program | Kementerian Pengampu | OPD Pelaksana Kabupaten | Sumber Dana | Manfaat Utama | Frekuensi | Faktor Risiko Ditangani |
|---|---|---|---|---|---|---|---|---|
| 1 | PKH | Program Keluarga Harapan | Kemensos (Ditjen Linjamsos) | Dinas Sosial | APBN | Rp900rb–Rp3jt/komponen/tahun | Triwulanan (4x/thn) | Pendapatan, gizi, putus sekolah, lansia telantar, disabilitas |
| 2 | SEMBAKO | Program Sembako / BPNT | Kemensos | Dinas Sosial | APBN | Rp200.000/bulan | Bulanan (sering dirapel) | Rawan pangan, gizi |
| 3 | PBI-JKN | Penerima Bantuan Iuran JKN | Kemensos + Kemenkes / BPJS Kes | Dinas Sosial + Dinas Kesehatan | APBN (PBI Pusat) / APBD (PBI Daerah) | Iuran Rp42.000/jiwa/bulan | Bulanan (ke BPJS) | Beban biaya kesehatan katastropik |
| 4 | PIP | Program Indonesia Pintar | Kemendikdasmen (Puslapdik) | Dinas Pendidikan & Kebudayaan | APBN | Rp450rb–Rp1,8jt/tahun | Tahunan/bertahap | Putus sekolah, biaya personal pendidikan |
| 5 | KIPK | KIP Kuliah | Kemendiktisaintek | — (langsung ke PT) | APBN | UKT penuh + Rp800rb–1,4jt/bln | Semesteran | Putus jenjang pendidikan tinggi |
| 6 | BLT-DD | BLT Dana Desa | Kemendes PDT | DPMP (Dinas PMD/Pekon) | Dana Desa (APBN → APBDesa) | Maks Rp300.000/bulan | Bulanan, maks 3 bulan | Kemiskinan ekstrem, kehilangan mata pencaharian |
| 7 | BLT-KESRA | BLT Kesejahteraan Rakyat | Kemensos / Kemenko Perekonomian | Dinas Sosial | APBN | Rp300.000/bulan (dirapel Rp900rb) | Ad-hoc | Guncangan daya beli |
| 8 | BAPANG | Bantuan Pangan Beras | Bapanas + Perum BULOG | Dinas Ketahanan Pangan + Dinas Sosial | APBN (CPP) | 10 kg beras/bulan | Per tahap (sering 3 bln sekaligus) | Rawan pangan |
| 9 | BSPS | Bantuan Stimulan Perumahan Swadaya (Bedah Rumah) | Kementerian PKP | Dinas PUPR / bidang Perkim | APBN | Rp20.000.000/unit | Sekali (one-off) | Rumah tidak layak huni |
| 10 | RST | Rumah Sejahtera Terpadu (eks RS-RUTILAHU) | Kemensos (Ditjen Linjamsos) | Dinas Sosial | APBN | Rp20.000.000/unit | Sekali | RTLH pada keluarga miskin |
| 11 | RUTILAHU-D | Rutilahu APBD Kabupaten | — (daerah) | Dinas Sosial Pringsewu | APBD Kabupaten | ±Rp15.000.000/unit (Pringsewu 2025) | Sekali | RTLH |
| 12 | SANIMAS | Sanitasi Berbasis Masyarakat (DAK) | Kementerian PU | Dinas PUPR | DAK Fisik (APBN→APBD) | IPAL komunal / tangki septik individual | Sekali per lokasi | Sanitasi buruk, stunting |
| 13 | PAMSIMAS | Penyediaan Air Minum & Sanitasi Berbasis Masyarakat | Kementerian PU | Dinas PUPR | APBN/DAK + kontribusi masyarakat | Sarana air minum perdesaan | Sekali per desa | Akses air bersih |
| 14 | STBM | Sanitasi Total Berbasis Masyarakat | Kemenkes | Dinas Kesehatan (Puskesmas) | APBN/APBD/DAK Non-Fisik (BOK) | Pemicuan perilaku, target ODF | Berkelanjutan | BAB sembarangan, diare, stunting |
| 15 | KUR | Kredit Usaha Rakyat | Kemenko Perekonomian | Diskoperindag | Kredit perbankan + subsidi bunga APBN | Plafon s/d Rp500jt, bunga 6%/thn | Sesuai akad | Modal usaha, pendapatan |
| 16 | PENA | Pahlawan Ekonomi Nusantara | Kemensos (Ditjen Dayasos) | Dinas Sosial | APBN | ±Rp4.900.000/KPM modal usaha + pendampingan | Sekali | Ketergantungan bansos, pendapatan |
| 17 | PPSE | Program Pemberdayaan Sosial Ekonomi | Kemensos | Dinas Sosial | APBN | ±Rp5.000.000 modal usaha | Sekali | Pendapatan |
| 18 | KUBE | Kelompok Usaha Bersama | Kemensos | Dinas Sosial | APBN | Rp10jt (5 KK) / Rp20jt (10 KK) per kelompok | Sekali | Pendapatan kolektif |
| 19 | PRAKERJA | Kartu Prakerja | Kemenko Perekonomian (MPPKP) | — (mandiri online) | APBN | Total ±Rp4.200.000 (pelatihan + insentif) | Sekali per peserta | Pengangguran, keterampilan rendah |
| 20 | MBG | Makan Bergizi Gratis | Badan Gizi Nasional (BGN) | Koordinasi Dinkes/Disdikbud + SPPG | APBN | Rp8.000–10.000/porsi/hari | Harian sekolah | Gizi anak, ibu hamil, ibu menyusui |
| 21 | PMT | Pemberian Makanan Tambahan Pangan Lokal | Kemenkes | Dinas Kesehatan (Puskesmas/Posyandu) | DAK Non-Fisik (BOK) / APBD / Dana Desa | Makanan tambahan harian | Harian, siklus ±90 hari | Stunting, gizi kurang, ibu hamil KEK |
| 22 | POSYANDU-ILP | Posyandu Integrasi Layanan Primer | Kemenkes | Dinas Kesehatan | APBD/BOK/Dana Desa | Layanan siklus hidup 0–lansia | Bulanan | Akses layanan kesehatan primer |
| 23 | ATENSI | Asistensi Rehabilitasi Sosial | Kemensos (Ditjen Rehsos, via Sentra/Balai) | Dinas Sosial | APBN | Alat bantu, kebutuhan dasar, modal usaha, terapi | Sesuai kasus | Disabilitas, lansia telantar, anak telantar |
| 24 | SEKOLAH-RAKYAT | Sekolah Rakyat | Kemensos | Dinas Sosial (penjangkauan) + Disdikbud | APBN | Sekolah berasrama gratis penuh | Berkelanjutan | Putus sekolah pada miskin ekstrem |
| 25 | PKT | Padat Karya Tunai Desa | Kemendes PDT / Kementerian PU | DPMP / Dinas PUPR | Dana Desa / APBN | Upah harian ke pekerja lokal | Musiman/proyek | Pengangguran musiman, daya beli |
| 26 | BLK | Pelatihan Vokasi BLK/BPVP | Kemnaker | Dinas Ketenagakerjaan & Transmigrasi | APBN/APBD | Pelatihan gratis + sertifikasi | Per angkatan | Keterampilan rendah, pengangguran |
| 27 | KDMP | Koperasi Desa/Kelurahan Merah Putih | Kementerian Koperasi | Diskoperindag + DPMP | Pinjaman Himbara (dijamin pemerintah) | Plafon s/d Rp3 miliar/koperasi | Sekali (kredit) | Akses pasar, harga sembako, akses kredit |
| 28 | BPJSTK-RENTAN | BPJS Ketenagakerjaan Pekerja Rentan | Kemnaker / BPJS TK | Dinas Ketenagakerjaan + Dinas Sosial | APBD / CSR / Baznas | Iuran Rp16.800/bulan (JKK+JKM) | Bulanan | Guncangan kecelakaan kerja & kematian pencari nafkah |

---

## 3. RINCIAN LENGKAP PER PROGRAM

---

### 3.1 PKH — PROGRAM KELUARGA HARAPAN

| Atribut | Isi | Keyakinan |
|---|---|---|
| Nama resmi | Program Keluarga Harapan | 🟢 |
| Singkatan | PKH | 🟢 |
| Jenis | Conditional Cash Transfer (bantuan tunai bersyarat) | 🟢 |
| Dasar hukum utama | **Permensos No. 1 Tahun 2018** tentang Program Keluarga Harapan (ditetapkan 8 Januari 2018). Payung: UU No. 11/2009 Kesejahteraan Sosial, UU No. 13/2011 Penanganan Fakir Miskin | 🟢 |
| Kementerian pengampu | Kementerian Sosial RI — Ditjen Perlindungan & Jaminan Sosial | 🟢 |
| OPD pelaksana kabupaten | **Dinas Sosial** (koordinator), dibantu **Koordinator Kabupaten PKH**, **Pendamping Sosial PKH**, dan **TKSK** di tiap kecamatan | 🟢 |
| Basis data | DTSEN (sebelumnya DTKS) | 🟢 |
| Frekuensi penyaluran | **4 tahap/tahun (triwulanan)**: Tahap 1 Jan–Mar, Tahap 2 Apr–Jun, Tahap 3 Jul–Sep, Tahap 4 Okt–Des | 🟢 |
| Mekanisme penyaluran | Transfer ke rekening **Bank Himbara** (BRI, BNI, Mandiri, BTN, BSI) melalui **KKS**; untuk daerah sulit dijangkau via **PT Pos Indonesia** | 🟢 |
| Batas komponen | **Maksimal 4 komponen per Kartu Keluarga.** Sistem memilih komponen dengan nominal tertinggi bila anggota keluarga melebihi 4. | 🟡 |
| Kewajiban penerima | Komitmen kesehatan (periksa kehamilan, imunisasi, timbang balita) & pendidikan (kehadiran sekolah ≥85%); wajib ikut **Pertemuan Peningkatan Kemampuan Keluarga (P2K2)** bulanan | 🟡 |
| Cakupan nasional 2026 | Alokasi RAPBN 2026: **Rp28,7 triliun untuk 10 juta KPM**. Realisasi penyaluran Triwulan III 2026 dilaporkan **7 juta KPM** — angka realisasi lebih rendah dari pagu | 🟡 |

#### 3.1.1 Nominal PKH per Komponen (angka 2025 & 2026 — identik)

| Komponen | Kriteria detail | Rp/tahap (triwulan) | **Rp/tahun** | Keyakinan |
|---|---|---|---|---|
| Ibu hamil / masa nifas | Ibu hamil atau dalam masa nifas dalam KPM PKH | Rp750.000 | **Rp3.000.000** | 🟢 |
| Anak usia dini (0–6 tahun) | Balita/apras dalam KPM PKH | Rp750.000 | **Rp3.000.000** | 🟢 |
| Anak SD / MI / sederajat | Terdaftar & aktif bersekolah | Rp225.000 | **Rp900.000** | 🟢 |
| Anak SMP / MTs / sederajat | Terdaftar & aktif bersekolah | Rp375.000 | **Rp1.500.000** | 🟢 |
| Anak SMA / SMK / MA / sederajat | Terdaftar & aktif bersekolah | Rp500.000 | **Rp2.000.000** | 🟢 |
| **Lanjut usia** | Permensos 1/2018 menyebut **≥60 tahun**; praktik penyaluran umum menargetkan **≥70 tahun** | Rp600.000 | **Rp2.400.000** | 🟡 (lihat catatan) |
| **Penyandang disabilitas berat** | Disabilitas berat yang tidak dapat mengurus diri sendiri | Rp600.000 | **Rp2.400.000** | 🟡 (lihat catatan) |
| Korban pelanggaran HAM berat masa lalu | Kategori khusus Kemensos | Rp2.700.000 | **Rp10.800.000** | 🟠 |

> ⚠️ **KONFLIK SUMBER — WAJIB DIVERIFIKASI:**
> - Beberapa portal (fahum.umsu.ac.id, itera.ac.id blog) menyebut lansia & disabilitas berat = **Rp3.000.000/tahun**.
> - Sumber lain yang lebih konsisten (Detik, Liputan6, Nova/Grid, Sultra Media) menyebut **Rp2.400.000/tahun (Rp600.000/triwulan)**.
> - Angka **Rp2.400.000** adalah angka historis resmi Kemensos sejak 2019 dan lebih banyak dikonfirmasi. **Dokumen ini memakai Rp2.400.000.**
> - **Aksi:** verifikasi ke Dinas Sosial Pringsewu / Koordinator Kabupaten PKH sebelum masuk produksi.

> ⚠️ **KONFLIK USIA LANSIA:** Permensos 1/2018 pasal komponen kesejahteraan sosial menyebut "lanjut usia mulai dari 60 tahun". Namun praktik penyaluran yang banyak dilaporkan menargetkan **70 tahun ke atas**. Kemungkinan besar 60+ adalah batas regulasi, 70+ adalah prioritas operasional karena keterbatasan kuota. **Simpan sebagai dua field terpisah di NADI: `usia_regulasi_min = 60`, `usia_prioritas_operasional = 70`.**

> 🔴 **Tidak ditemukan:** angka pasti jumlah KPM PKH di Kabupaten Pringsewu.

---

### 3.2 PROGRAM SEMBAKO / BPNT

| Atribut | Isi | Keyakinan |
|---|---|---|
| Nama resmi | Program Sembako (dahulu Bantuan Pangan Non-Tunai / BPNT) | 🟢 |
| Singkatan | Sembako / BPNT | 🟢 |
| Dasar hukum | **Permensos No. 5 Tahun 2021** tentang Program Sembako | 🟢 |
| Kementerian pengampu | Kementerian Sosial RI | 🟢 |
| OPD pelaksana kabupaten | Dinas Sosial (verifikasi & validasi penerima, pembinaan e-warong) | 🟢 |
| **Nominal** | **Rp200.000 per KPM per bulan** (naik dari Rp150.000 sejak Maret 2020) | 🟢 |
| Frekuensi | Bulanan; dalam praktik sering **dirapel 2–3 bulan sekaligus** | 🟢 |
| Sumber dana | APBN. Alokasi RAPBN 2026: **Rp43,8 triliun untuk 18,3 juta KPM** | 🟡 |
| Mekanisme penyaluran | Saldo masuk ke rekening/**Kartu Keluarga Sejahtera (KKS)**, dibelanjakan di **e-warong** (Elektronik Warung Gotong Royong) memakai mesin EDC dengan PIN. Bukan uang tunai. | 🟢 |
| Komoditas yang boleh dibeli | 4 golongan gizi: **karbohidrat** (beras, jagung), **protein hewani** (telur, daging ayam, daging sapi, ikan), **protein nabati** (tempe, tahu, kacang-kacangan), **vitamin & mineral** (sayur, buah) | 🟢 |
| Larangan | Tidak boleh dibelanjakan untuk rokok, minuman beralkohol, pulsa, dan barang non-pangan. (Larangan disebut umum di banyak juknis; teks pasti tidak berhasil diambil) | 🟠 |
| Kriteria penerima | Terdaftar DTSEN; keluarga miskin/rentan miskin; memiliki NIK & KK valid; memiliki KKS atau rekening Himbara | 🟢 |
| Catatan kombinasi | Beberapa sumber menyebut penerima Sembako "tidak boleh menerima PKH bersamaan". **Ini KELIRU secara umum** — praktik nasional membolehkan KPM PKH juga menerima Sembako. | 🟠 |

---

### 3.3 PBI-JKN — PENERIMA BANTUAN IURAN JAMINAN KESEHATAN NASIONAL

| Atribut | Isi | Keyakinan |
|---|---|---|
| Nama resmi | Penerima Bantuan Iuran Jaminan Kesehatan | 🟢 |
| Singkatan | PBI-JK / PBI-JKN | 🟢 |
| Dasar hukum | UU No. 40/2004 SJSN; UU No. 24/2011 BPJS; **Perpres No. 82/2018 tentang Jaminan Kesehatan** beserta perubahannya termasuk **Perpres No. 59 Tahun 2024**; **Peraturan Kemensos No. 3 Tahun 2025** (kriteria desil PBI Pusat) | 🟡 |
| Kementerian pengampu | Kemensos (penetapan sasaran) + Kemenkes (kebijakan) + BPJS Kesehatan (operator) | 🟢 |
| OPD pelaksana kabupaten | **Dinas Sosial** (usul/hapus data PBI), **Dinas Kesehatan** (koordinasi UHC & fasyankes), **Dukcapil** (validasi NIK) | 🟢 |
| **Besaran iuran ditanggung** | **Rp42.000 per jiwa per bulan**, hak kelas rawat inap kelas 3 | 🟢 |
| Bentuk manfaat | **Bukan uang tunai.** Pemerintah membayar langsung ke BPJS Kesehatan. Peserta mendapat layanan JKN penuh. | 🟢 |
| Frekuensi | Bulanan (pembayaran iuran) | 🟢 |
| Sumber dana | **PBI Pusat = APBN** (kuota nasional dijaga ±96,8 juta jiwa). **PBI Daerah = APBD Provinsi / APBD Kabupaten** (mekanisme mencapai UHC) | 🟡 |
| Kriteria penerima | Fakir miskin & orang tidak mampu. **PBI Pusat: desil 1–4 DTSEN** (per Peraturan Kemensos 3/2025). WNI, NIK valid & terdaftar di Dukcapil, terdaftar DTSEN. | 🟡 |
| Definisi fakir miskin | Tidak memiliki sumber penghasilan sama sekali, ATAU memiliki penghasilan tetapi tidak mampu memenuhi kebutuhan dasar yang layak untuk diri/keluarganya | 🟢 |
| Definisi tidak mampu | Memiliki penghasilan yang hanya cukup untuk kebutuhan dasar, tidak mampu membayar iuran jaminan kesehatan | 🟢 |
| Target nasional | RPJMN 2025–2029 (Perpres 12/2025): cakupan kepesertaan JKN **98% pada 2025**, **99% pada 2029** | 🟡 |
| Risiko operasional kabupaten | **Penonaktifan massal PBI** akibat pembersihan data. Di Kabupaten Pringsewu, ±**62.000 peserta terdampak penonaktifan kepesertaan PBI**. Tunggakan iuran JKN Pemkab Pringsewu **Rp7,94 miliar**. | 🟡 |
| Konteks Lampung | Capaian UHC wilayah kerja BPJS Kesehatan Cabang Bandarlampung (mencakup Bandarlampung, Lampung Selatan, Pesawaran, **Pringsewu**, Tanggamus) = **96,52% per Mei 2026**. Tunggakan iuran JKN Pemda se-wilayah = Rp134,2 miliar. | 🟡 |

> **Implikasi NADI:** ini adalah *pain point* nyata di Pringsewu. Fitur "deteksi keluarga miskin yang PBI-nya nonaktif" akan sangat bernilai.

---

### 3.4 PIP — PROGRAM INDONESIA PINTAR

| Atribut | Isi | Keyakinan |
|---|---|---|
| Nama resmi | Program Indonesia Pintar | 🟢 |
| Singkatan | PIP (kartunya: **KIP** — Kartu Indonesia Pintar) | 🟢 |
| Dasar hukum | **Persesjen Kemendikbudristek No. 19 Tahun 2024** (Juknis PIP Dikdasmen); **Peraturan Sekjen Kemendikdasmen No. 10 Tahun 2025** (Juknis PIP jenjang SD, SMP, SMA, SMK, SKB, PKBM, SLB) | 🟡 |
| Kementerian pengampu | Kementerian Pendidikan Dasar & Menengah — **Puslapdik** (Pusat Layanan Pembiayaan Pendidikan) | 🟢 |
| OPD pelaksana kabupaten | **Dinas Pendidikan dan Kebudayaan** (SD & SMP); SMA/SMK adalah kewenangan **Dinas Pendidikan Provinsi** — penting untuk pembagian tugas di NADI | 🟢 |
| Kriteria penerima | (a) Terdaftar DTKS/DTSEN Kemensos **ATAU** pemegang KIP; (b) status **"Layak PIP"** di **Dapodik** sekolah; (c) pertimbangan khusus: yatim/piatu, korban bencana, dari keluarga terdampak PHK, disabilitas | 🟢 |
| Mekanisme penyaluran | Transfer ke **rekening tabungan siswa** di bank penyalur (SimPel BRI/BNI). Siswa ≥17 tahun dengan ATM aktif bisa tarik mandiri; di bawah itu harus didampingi orang tua di teller. Cek status di **pip.kemendikdasmen.go.id** (input NISN, NIK, nama). | 🟢 |
| Peruntukan dana | Biaya personal pendidikan: transportasi, perlengkapan sekolah, kebutuhan lain selama bersekolah | 🟢 |

#### 3.4.1 Nominal PIP 2025 per Jenjang

| Jenjang | Kelas | **Nominal per tahun** | Keyakinan |
|---|---|---|---|
| SD / SDLB / Paket A | Kelas 1–5 | **Rp450.000** | 🟢 |
| SD / SDLB / Paket A | Kelas 6 (akhir) | **Rp225.000** | 🟢 |
| SMP / SMPLB / Paket B | Kelas 7–8 | **Rp750.000** | 🟢 |
| SMP / SMPLB / Paket B | Kelas 9 (akhir) | **Rp375.000** | 🟢 |
| SMA / SMK / SMALB / Paket C | Kelas 10–11 | **Rp1.800.000** | 🟢 |
| SMA / SMK / SMALB / Paket C | Kelas 12 (akhir) | **Rp900.000** | 🟢 |

> Catatan: Puslapdik menerbitkan klarifikasi resmi bahwa nominal SMA/SMK adalah **Rp1.800.000** (bukan angka lain yang beredar). Nominal 2025 **sama dengan 2024** — tidak ada kenaikan.
> Satu sumber menyebut siswa **baru** kelas 10 semester pertama juga menerima setengah (Rp900.000). 🟠
> Realisasi nasional 2024: Rp6,524 triliun untuk 4,168 juta siswa jenjang menengah.

---

### 3.5 KIP KULIAH

| Atribut | Isi | Keyakinan |
|---|---|---|
| Nama resmi | Kartu Indonesia Pintar Kuliah | 🟢 |
| Singkatan | KIP Kuliah / KIP-K | 🟢 |
| Kementerian pengampu | Kementerian Pendidikan Tinggi, Sains & Teknologi (Puslapdik) | 🟡 |
| OPD pelaksana kabupaten | **Tidak ada** — pendaftaran mandiri online oleh siswa. Dinas Pendidikan/Dinsos hanya dapat berperan sosialisasi & penerbitan SKTM. | 🟢 |
| Manfaat 1: biaya pendidikan | **Pembebasan UKT penuh**, ditransfer pemerintah langsung ke perguruan tinggi tiap semester | 🟢 |
| Manfaat 2: biaya hidup | **5 klaster wilayah**: Rp800.000 / Rp950.000 / Rp1.100.000 / Rp1.250.000 / **Rp1.400.000** per bulan. Disalurkan per semester ke rekening mahasiswa. | 🟢 |
| Kriteria penerima | Lulusan SMA/SMK/MA tahun berjalan atau 2 tahun sebelumnya; NISN, NPSN, NIK valid; **memiliki KIP ATAU terdaftar DTKS/DTSEN**; bila tidak terdaftar, wajib melampirkan **SKTM** | 🟢 |
| Perubahan skema 2026 | Kuota per kampus dihapus | 🟠 |
| Jadwal 2026 | Pendaftaran akun dibuka 3 Februari 2026, ditutup 31 Oktober 2026 | 🟡 |

---

### 3.6 BLT DANA DESA

| Atribut | Isi | Keyakinan |
|---|---|---|
| Nama resmi | Bantuan Langsung Tunai Dana Desa | 🟢 |
| Singkatan | BLT-DD / BLT Desa | 🟢 |
| Dasar hukum | **Permendes No. 16 Tahun 2025** (dilanjutkan **Permendes No. 16 Tahun 2026** tentang Petunjuk Operasional Fokus Penggunaan Dana Desa TA 2026); **PMK No. 7 Tahun 2026** (pengelolaan Dana Desa) | 🟡 |
| Kementerian pengampu | Kementerian Desa & Pembangunan Daerah Tertinggal | 🟢 |
| OPD pelaksana kabupaten | **Dinas Pemberdayaan Masyarakat dan Pekon (DPMP)** — di Pringsewu istilah desa = **pekon**. Pelaksana teknis: Pemerintah Pekon + Musyawarah Pekon. | 🟢 |
| **Nominal** | **Maksimal Rp300.000 per KPM per bulan** — "sesuai kemampuan desa", jadi bisa lebih rendah | 🟢 |
| **Durasi** | **Paling lama 3 bulan** (perubahan besar dari skema sebelumnya yang 12 bulan) | 🟡 |
| **Pagu maksimal** | **Maksimal 15% dari pagu Dana Desa** per desa | 🟡 |
| Frekuensi | Bulanan, atau dirapel 3 bulan sekaligus | 🟢 |
| Sumber dana | **Dana Desa** (APBN → transfer ke APBDesa/APBPekon) | 🟢 |
| Kriteria penerima (prioritas) | **Keluarga miskin ekstrem berdomisili di desa setempat sesuai DTSEN** | 🟢 |
| Kriteria alternatif (bila data pusat tidak tersedia) | (a) kehilangan mata pencaharian; (b) memiliki anggota keluarga rentan sakit menahun/kronis/disabilitas; (c) **tidak menerima PKH**; (d) rumah tangga dengan anggota tunggal lanjut usia; (e) perempuan kepala keluarga dari keluarga miskin | 🟢 |
| Mekanisme penetapan | **Musyawarah Desa/Pekon Khusus** → ditetapkan dengan **Peraturan Kepala Desa/Peraturan Pekon** | 🟡 |
| Temuan lapangan | Ditemukan kasus penyaluran hanya **Rp150.000/KPM** karena keterbatasan pagu desa — konfirmasi bahwa Rp300.000 adalah **plafon**, bukan nominal pasti | 🟡 |

#### 3.6.1 Fokus Penggunaan Dana Desa 2026 (relevan untuk NADI)

| # | Fokus | Ketentuan/pagu | Keyakinan |
|---|---|---|---|
| a | Penanganan kemiskinan ekstrem via BLT Desa | **Maks 15%** pagu | 🟡 |
| b | Program ketahanan pangan / lumbung pangan | **Minimal 20%** pagu | 🟡 |
| c | Penguatan desa berketahanan iklim & tangguh bencana | — | 🟡 |
| d | Peningkatan promosi & layanan dasar kesehatan skala desa (termasuk **pencegahan stunting**: intervensi gizi, PMT pangan lokal, edukasi gizi ibu hamil & balita, sanitasi & air bersih) | — | 🟡 |
| e | Dukungan implementasi **Koperasi Desa Merah Putih** | — | 🟡 |
| f | Pembangunan & pemeliharaan infrastruktur desa via **Padat Karya Tunai Desa** | — | 🟡 |
| g | Pembangunan infrastruktur digital & teknologi desa | — | 🟡 |

> **Implikasi NADI:** Dana Desa adalah instrumen kabupaten yang paling *fleksibel* dan bisa direkomendasikan mesin NADI untuk mengisi celah yang tidak ditutup program APBN.

---

### 3.7 BLT KESRA

| Atribut | Isi | Keyakinan |
|---|---|---|
| Nama | Bantuan Langsung Tunai Kesejahteraan Rakyat | 🟡 |
| Singkatan | BLT Kesra / BLTS Kesra | 🟡 |
| Inisiator | Instruksi Presiden Prabowo Subianto via Kemenko Perekonomian; disalurkan Kemensos | 🟡 |
| Nominal 2025 | **Rp300.000/bulan × 3 bulan (Okt–Des 2025) = Rp900.000 dirapel sekali** | 🟡 |
| Kriteria | Keluarga **desil 1–4 DTSEN** | 🟡 |
| Status 2026 | **Belum ada keputusan resmi kelanjutan** per Juli 2026. Banyak berita hoaks/spekulasi beredar. | 🟡 |

> ⚠️ **Peringatan integritas data:** topik "BLT Kesra 2026" adalah magnet konten spam/clickbait. Jangan seed angka 2026 sebelum ada pengumuman resmi. Tandai `status: uncertain`.

---

### 3.8 BANTUAN PANGAN BERAS (BAPANAS–BULOG)

| Atribut | Isi | Keyakinan |
|---|---|---|
| Nama resmi | Bantuan Pangan Beras (Cadangan Pangan Pemerintah) | 🟢 |
| Pengampu | **Badan Pangan Nasional (Bapanas)** memberi penugasan ke **Perum BULOG** | 🟢 |
| OPD kabupaten | **Dinas Ketahanan Pangan** (koordinasi), **Dinas Sosial** (data penerima), Pemerintah Pekon/Kelurahan (titik bagi) | 🟡 |
| **Nominal** | **10 kg beras per KPM per bulan**; sering disalurkan 3 bulan sekaligus = **30 kg** | 🟢 |
| Tambahan | Pada beberapa tahap disertai **minyak goreng (MinyaKita)** | 🟡 |
| Sumber dana | APBN (Cadangan Beras Pemerintah / CPP) | 🟢 |
| Kriteria penerima | KPM sesuai desil kemiskinan DTSEN; **KPM PKH murni otomatis masuk alokasi** | 🟡 |
| Titik penyaluran | Kantor balai desa/pekon, kantor kelurahan, atau unit **Koperasi Desa Merah Putih** terdekat; penerima mendapat surat undangan | 🟡 |
| Skala 2026 | Sasaran diperluas menjadi **33,2 juta KPM**; tahap Jul–Sep 2026 mulai 17 Agustus 2026 | 🟡 |

---

### 3.9 BSPS — BANTUAN STIMULAN PERUMAHAN SWADAYA (BEDAH RUMAH)

| Atribut | Isi | Keyakinan |
|---|---|---|
| Nama resmi | Bantuan Stimulan Perumahan Swadaya | 🟢 |
| Singkatan | BSPS (populer: "Bedah Rumah") | 🟢 |
| Dasar hukum | **Permen PKP No. 10 Tahun 2025** tentang Pelaksanaan Bantuan Pembangunan Perumahan dan Penyediaan Rumah Khusus; diperbarui **Permen PKP No. 6 Tahun 2026** tentang Bedah Rumah | 🟡 |
| Kementerian pengampu | **Kementerian Perumahan dan Kawasan Permukiman (PKP)** — sebelumnya di bawah Kementerian PUPR. Operasional lewat **BP3KP / BP2P** wilayah. | 🟢 |
| OPD pelaksana kabupaten | **Dinas PUPR** (di Pringsewu urusan perumahan & permukiman berada di Dinas PUPR — tidak ada Dinas Perkim terpisah) | 🟡 |
| **Nominal total** | **Rp20.000.000 per unit rumah** | 🟢 |
| **Rincian nominal** | **Rp17.500.000** untuk pembelian bahan bangunan (disalurkan langsung ke toko bahan bangunan) + **Rp2.500.000** untuk upah tukang | 🟢 |
| Frekuensi | Sekali (one-off) per rumah tangga | 🟢 |
| Sumber dana | APBN | 🟢 |
| Kriteria penerima | (a) WNI sudah berkeluarga; (b) memiliki/menguasai tanah secara legal, tidak sengketa, sesuai tata ruang; (c) belum memiliki rumah **ATAU** memiliki & menempati satu-satunya rumah dalam kondisi tidak layak huni; (d) belum pernah menerima BSPS/bantuan perumahan sejenis; (e) berpenghasilan rendah (MBR); (f) bersedia berswadaya & membentuk kelompok penerima bantuan (KPB) | 🟢 |
| Mekanisme | Usulan dari pemda → verifikasi lapangan oleh fasilitator → penetapan SK → transfer ke rekening penerima (dana bahan bangunan langsung ke toko) → pembangunan swakelola/gotong royong → pelaporan | 🟡 |
| Isu 2026 | Nominal Rp20 juta **tidak naik selama 5 tahun** dan mulai dikritik tidak realistis terhadap harga bahan bangunan | 🟢 |
| Alokasi Provinsi Lampung | Pusat mengalokasikan **11.000 unit BSPS untuk Provinsi Lampung**. Kota Bandar Lampung menerima 300 unit. | 🟡 |
| Alokasi Pringsewu | 🔴 **Tidak ditemukan** angka spesifik alokasi BSPS untuk Kabupaten Pringsewu. |

---

### 3.10 RST / RS-RUTILAHU — KEMENSOS

| Atribut | Isi | Keyakinan |
|---|---|---|
| Nama resmi saat ini | **Rumah Sejahtera Terpadu (RST)** — sebelumnya **Rehabilitasi Sosial Rumah Tidak Layak Huni (RS-Rutilahu)** | 🟢 |
| Kementerian pengampu | Kemensos — **Ditjen Perlindungan & Jaminan Sosial** | 🟢 |
| OPD pelaksana kabupaten | **Dinas Sosial** | 🟢 |
| **Nominal** | **Rp20.000.000 per rumah** | 🟢 |
| Batasan penggunaan dana | **Wajib untuk bahan bangunan/material saja.** Dilaksanakan **gotong royong**, **tidak boleh dipihakketigakan**, **tidak boleh untuk membayar jasa/upah tukang** | 🟢 |
| Sumber dana | APBN | 🟢 |
| Kriteria RTLH (detail — penting untuk NADI) | (a) **dinding dan/atau atap rusak & membahayakan keselamatan penghuni**; (b) **dinding/atap dari bahan yang mudah rusak atau lapuk**; (c) **lantai dari tanah, papan, bambu, atau semen/keramik dalam kondisi rusak**; (d) **tidak memiliki fasilitas MCK, atau memiliki tetapi tidak layak**; (e) **luas lantai < 7,2 m² per orang** | 🟢 |
| Kriteria penerima | Terdaftar DTKS/DTSEN atau termasuk kategori kemiskinan ekstrem; terdaftar dalam sistem **SI Langkarr** Kemensos | 🟡 |
| Mekanisme verifikasi | Identifikasi & verifikasi lapangan langsung oleh **fasilitator sosial** dan **TKSK (Tenaga Kesejahteraan Sosial Kecamatan)** | 🟢 |

> **Implikasi NADI:** kriteria RTLH di atas adalah **checklist survei rumah yang siap pakai**. Jadikan form input terstruktur (5 boolean + 1 numeric luas lantai per kapita).

---

### 3.11 RUTILAHU APBD KABUPATEN PRINGSEWU (DATA NYATA)

| Atribut | Isi | Keyakinan |
|---|---|---|
| Nama program | Bantuan Sosial Rutilahu (Rumah Tinggal Layak Huni) Kabupaten Pringsewu | 🟢 |
| Tahun | 2025 (penyerahan 5 Mei 2025 oleh Bupati) | 🟢 |
| OPD pelaksana | **Dinas Sosial Kabupaten Pringsewu** (Kadis: Debi Hardian) | 🟢 |
| Sumber dana | **APBD Kabupaten Pringsewu TA 2025** | 🟢 |
| Jumlah penerima | **80 KPM** | 🟢 |
| Total anggaran | **Rp1.200.000.000** | 🟢 |
| **Nominal per unit** | **Rp15.000.000** (hasil pembagian Rp1,2 M ÷ 80 KPM) | 🟠 (turunan, bukan angka yang dinyatakan langsung) |
| Dasar hukum yang dirujuk | **UU No. 11 Tahun 2009** tentang Kesejahteraan Sosial (Pasal 21: penanggulangan kemiskinan mencakup penyediaan akses pelayanan perumahan dan permukiman) dan **UU No. 13 Tahun 2011** tentang Penanganan Fakir Miskin | 🟢 |
| **Backlog** | **±1.700 unit RTLH masih tersisa di Kabupaten Pringsewu** | 🟢 |

#### 3.11.1 Distribusi Penerima Rutilahu Pringsewu 2025 per Kecamatan

| Kecamatan | Jumlah KPM |
|---|---|
| Gadingrejo | 17 |
| Pringsewu | 14 |
| Pagelaran | 13 |
| Sukoharjo | 10 |
| Pagelaran Utara ("Pantura") | 9 |
| Adiluwih | 6 |
| Ambarawa | 4 |
| Pardasuka | 4 |
| Banyumas | 3 |
| **TOTAL** | **80** |

> 🟢 Semua angka di atas dari sumber berita lokal yang mengutip acara resmi Pemkab. **Ini data seed terbaik yang ditemukan untuk konteks lokal Pringsewu.**
> **Insight kuat untuk NADI:** dengan laju 80 unit/tahun dari APBD, backlog 1.700 unit membutuhkan **±21 tahun**. Ini argumen kuat untuk fitur *prioritisasi berbasis skor risiko* dan *blending* APBD + BSPS APBN + RST Kemensos + Dana Desa.

---

### 3.12 PROGRAM SANITASI & AIR MINUM

| Program | Pengampu | OPD Kabupaten | Sumber Dana | Isi | Keyakinan |
|---|---|---|---|---|---|
| **SANIMAS** (Sanitasi Berbasis Masyarakat) | Kementerian PU | Dinas PUPR | **DAK Fisik Bidang Sanitasi** | Pembangunan **IPAL skala permukiman** dan **tangki septik individual** di kawasan padat/kumuh. Berbasis partisipasi masyarakat (KSM). | 🟢 |
| **PAMSIMAS** (Penyediaan Air Minum & Sanitasi Berbasis Masyarakat) | Kementerian PU | Dinas PUPR | APBN/DAK + kontribusi masyarakat (in-cash & in-kind) | Infrastruktur air minum perdesaan; masyarakat mengadakan, mengelola, & memelihara sendiri melalui **KPSPAMS**. Diperkenalkan Indonesia di World Water Forum ke-10. | 🟢 |
| **STBM** (Sanitasi Total Berbasis Masyarakat) | Kemenkes | Dinas Kesehatan (Puskesmas & sanitarian) | APBN/APBD/**DAK Non-Fisik (BOK)** | Perubahan perilaku via metode **pemicuan**. Target output: **ODF (Open Defecation Free)**. | 🟢 |
| **Jambanisasi** | — (bukan program nasional tunggal) | Dinas Kesehatan / Dinas PUPR / Dana Desa / Baznas | APBD Kabupaten, Dana Desa, CSR, Baznas | Bantuan pembangunan jamban sehat individual. **Tidak ada nomenklatur & nominal nasional yang seragam.** | 🟠 |

#### 3.12.1 Lima Pilar STBM (Permenkes No. 3 Tahun 2014) 🟢

| Pilar | Nama | Singkatan |
|---|---|---|
| 1 | Stop Buang Air Besar Sembarangan | SBABS |
| 2 | Cuci Tangan Pakai Sabun | CTPS |
| 3 | Pengelolaan Air Minum & Makanan Rumah Tangga | PAMMRT |
| 4 | Pengamanan Sampah Rumah Tangga | PSRT |
| 5 | Pengamanan Limbah Cair Rumah Tangga | PLCRT |

> 🔴 **Tidak ditemukan:** nominal rupiah standar per unit untuk SANIMAS, PAMSIMAS, maupun jambanisasi. Besaran ditentukan per DAK/per lokasi. **Jangan mengarang angka.**

---

### 3.13 PROGRAM EKONOMI PRODUKTIF

#### 3.13.1 KUR — Kredit Usaha Rakyat

| Atribut | Isi | Keyakinan |
|---|---|---|
| Nama resmi | Kredit Usaha Rakyat | 🟢 |
| Pengampu kebijakan | **Kemenko Perekonomian** — Komite Kebijakan Pembiayaan bagi UMKM | 🟢 |
| Dasar hukum | **Permenko No. 8/2019** jo. **Permenko No. 2/2021** tentang Pedoman Pelaksanaan KUR (portal resmi kur.ekon.go.id masih menampilkan versi 2021). Ada perubahan Permenko untuk pelaksanaan 2025 — **nomor pastinya tidak berhasil dikonfirmasi**. | 🟡 |
| OPD pelaksana kabupaten | **Diskoperindag** (Dinas Koperasi, Perindustrian & Perdagangan) — fasilitasi, pendampingan, NIB/IUMK. Penyaluran oleh bank (BRI, BNI, Mandiri, BSI, BPD). | 🟢 |
| Target nasional 2025 | **Rp300 triliun**, harapan menjangkau >2 juta debitur baru + 1 juta debitur graduasi | 🟢 |
| Sumber dana | Dana perbankan; pemerintah menanggung **subsidi bunga/marjin** dari APBN | 🟢 |

**Skema KUR (per Permenko 2/2021 + update 2026):**

| Skema | Plafon | Suku bunga efektif/tahun | Agunan tambahan | Keyakinan |
|---|---|---|---|---|
| KUR Super Mikro | s/d **Rp10 juta** | **3%** (BRI 2026) / 6% (kebijakan umum) | Tidak diwajibkan | 🟡 |
| KUR Mikro | **>Rp10 juta – Rp100 juta** (per Permenko 2021: Rp10–50 juta) | **6%** untuk pinjaman pertama | Tidak diwajibkan | 🟡 |
| KUR Kecil | **>Rp100 juta – Rp500 juta** | **6–9%** | Tidak wajib s/d Rp100 juta | 🟡 |
| KUR Khusus | s/d Rp500 juta | 6% | Kelompok/klaster (pertanian, peternakan, perikanan, UMKM pengolahan) | 🟠 |
| KUR Penempatan PMI/TKI | s/d **Rp25 juta** | 6% | — | 🟠 |
| KUR Perumahan | — | — | Mulai disalurkan Oktober 2025 | 🟠 |

> ⚠️ **Batas plafon KUR Mikro berbeda antar sumber** (Rp50 juta vs Rp100 juta). Portal resmi menampilkan versi 2021 (Rp50 juta); sumber 2026 menyebut Rp100 juta. **Verifikasi ke Permenko terbaru sebelum seed.**

**Syarat umum:** WNI ≥21 tahun atau sudah menikah; punya KTP & izin usaha (NIB/IUMK); usaha produktif & layak (*feasible*); usaha telah berjalan **minimal 6 bulan** (KUR Super Mikro <6 bulan wajib ikut pelatihan). 🟡

#### 3.13.2 PENA — Pahlawan Ekonomi Nusantara

| Atribut | Isi | Keyakinan |
|---|---|---|
| Nama resmi | Pahlawan Ekonomi Nusantara | 🟢 |
| Pengampu | Kemensos — **Ditjen Pemberdayaan Sosial (Dayasos)** | 🟢 |
| OPD kabupaten | Dinas Sosial | 🟢 |
| **Nominal** | **Rp4.900.000 per KPM** (modal usaha) | 🟡 |
| **Kriteria penerima** | **KPM PKH berusia produktif 20–45 tahun**, memiliki atau berkomitmen memulai usaha mandiri | 🟡 |
| Tujuan eksplisit | **Graduasi mandiri** — memutus ketergantungan pada bansos | 🟢 |
| Manfaat non-tunai | Pendampingan usaha, pelatihan **pengemasan/packaging**, pemasaran, **literasi keuangan** | 🟢 |
| Capaian | Kemensos melaporkan **25.360 wirausahawan** lahir lewat PENA | 🟢 |
| Program penerus | **PPSE (Program Pemberdayaan Sosial Ekonomi)** resmi dijalankan 2025 dengan cakupan lebih luas, modal usaha **±Rp5.000.000** | 🟡 |

> ⚠️ Hubungan PENA vs PPSE belum sepenuhnya jelas dari sumber terbuka: apakah PPSE menggantikan PENA atau berjalan paralel. **Tandai untuk klarifikasi ke Dinsos.**

#### 3.13.3 KUBE — Kelompok Usaha Bersama

| Atribut | Isi | Keyakinan |
|---|---|---|
| Definisi | Himpunan **5–10 Kepala Keluarga** miskin yang dibentuk atas prakarsa sendiri, saling berinteraksi, tinggal dalam satu wilayah | 🟢 |
| Pengampu | Kemensos | 🟢 |
| OPD kabupaten | Dinas Sosial | 🟢 |
| **Nominal** | **Rp10.000.000 per KUBE beranggotakan 5 KK**; **Rp20.000.000 per KUBE beranggotakan 10 KK** (= **Rp2.000.000 per KK**) | 🟡 |
| Skema | **Bantuan Langsung Pemberdayaan Sosial (BLPS)** untuk mengelola **Usaha Ekonomi Produktif (UEP)** | 🟢 |
| Contoh usaha | Warung, es jus, cilok, gorengan, ternak, dan usaha mikro sejenis | 🟢 |
| Konteks Lampung | Kemensos pernah menggelar Bimtek untuk **50 kelompok penerima KUBE** di Provinsi Lampung | 🟡 |

#### 3.13.4 Kartu Prakerja

| Atribut | Isi | Keyakinan |
|---|---|---|
| Pengampu | Kemenko Perekonomian — Manajemen Pelaksana Program Kartu Prakerja (MPPKP) | 🟢 |
| OPD kabupaten | **Tidak ada** — pendaftaran mandiri di www.prakerja.go.id. Dinas Tenaga Kerja hanya bisa sosialisasi. | 🟢 |
| Skema berjalan | **Skema Normal** (bukan semi-bansos) — dana pelatihan wajib dibelanjakan di platform mitra resmi | 🟢 |
| **Total manfaat** | **Rp4.200.000** = saldo pelatihan **Rp3.500.000** + insentif biaya mencari kerja **Rp600.000** + insentif survei evaluasi **Rp100.000** | 🟡 |
| Kriteria | WNI **18–64 tahun**; **tidak sedang menempuh pendidikan formal**; bukan ASN/TNI/Polri/Kepala Desa/Perangkat Desa/anggota DPRD/direksi BUMN-BUMD; **maksimal 2 NIK per KK** | 🟡 |
| Sasaran | Pencari kerja, korban PHK, buruh yang butuh peningkatan kompetensi, pelaku UMKM | 🟢 |
| Validasi | Terintegrasi Dukcapil nasional | 🟢 |

> ⚠️ Angka Rp3.550.000 yang sering beredar **bukan** total manfaat — total saat ini Rp4.200.000. 🟡

#### 3.13.5 Koperasi Desa/Kelurahan Merah Putih (KDMP)

| Atribut | Isi | Keyakinan |
|---|---|---|
| Dasar hukum | **Inpres No. 9 Tahun 2025** tentang Percepatan Pembentukan Koperasi Desa/Kelurahan Merah Putih, ditandatangani 27 Maret 2025 | 🟢 |
| Target | **80.000 KDMP** se-Indonesia; **80.081 unit sudah diresmikan** per 21 Juli 2025 | 🟢 |
| OPD kabupaten | **Diskoperindag** + **DPMP** (Dinas Pemberdayaan Masyarakat & Pekon) | 🟡 |
| **7 gerai wajib** | (1) kantor koperasi, (2) **gerai sembako**, (3) unit simpan pinjam, (4) **klinik desa**, (5) **apotek desa**, (6) gudang berpendingin / cold storage, (7) sarana logistik | 🟢 |
| **Plafon pinjaman** | **Rp3 miliar per koperasi**: **Rp2,5 miliar capex** (fisik & operasional) + **Rp500 juta opex** | 🟢 |
| Bunga & tenor | **6% per tahun**, tenor maksimal **72 bulan** | 🟢 |
| Relevansi kemiskinan | Titik distribusi Bantuan Pangan Beras; akses sembako murah; akses kredit non-rentenir; klinik & apotek desa | 🟡 |

---

### 3.14 PROGRAM KESEHATAN & GIZI

#### 3.14.1 MBG — Makan Bergizi Gratis

| Atribut | Isi | Keyakinan |
|---|---|---|
| Nama resmi | Makan Bergizi Gratis | 🟢 |
| Pengampu | **Badan Gizi Nasional (BGN)** | 🟢 |
| Unit pelaksana | **SPPG (Satuan Pelayanan Pemenuhan Gizi)** — dapur MBG. **24.000 SPPG** terbentuk hingga akhir 2025. | 🟢 |
| OPD kabupaten | Tidak ada OPD pelaksana langsung; **koordinasi** dengan Dinas Pendidikan (sekolah), Dinas Kesehatan (ibu hamil/menyusui/balita), Dinas Ketahanan Pangan & Dinas Pertanian (pasokan bahan lokal) | 🟠 |
| **Biaya bahan makanan** | **Rp8.000–Rp10.000 per porsi** (BGN menegaskan **bukan Rp15.000**). Disesuaikan untuk daerah dengan indeks kemahalan tinggi. | 🟢 |
| Anggaran APBN 2025 | **Rp71 triliun**, target **19,47 juta penerima manfaat** | 🟢 |
| Anggaran 2026 | **Rp355 triliun** (naik ±400%), target **minimal 60 juta penerima**, biaya operasional **±Rp900 miliar/hari** | 🟢 |
| Sasaran | Peserta didik **PAUD hingga SMA/sederajat**, **balita**, **ibu hamil**, **ibu menyusui** | 🟢 |
| Frekuensi | Harian pada hari sekolah | 🟢 |
| Faktor risiko ditangani | Gizi buruk/kurang, stunting, absensi sekolah, beban pengeluaran pangan rumah tangga | 🟡 |

> **Implikasi NADI:** MBG bersifat *universal berbasis lokasi* (semua siswa di sekolah yang dilayani SPPG), bukan berbasis desil. Ini penting: MBG **tidak** perlu matching DTSEN, tapi **penempatan SPPG** perlu diprioritaskan ke wilayah dengan prevalensi stunting/kemiskinan tinggi.

#### 3.14.2 PMT — Pemberian Makanan Tambahan Pangan Lokal

| Atribut | Isi | Keyakinan |
|---|---|---|
| Pengampu | Kemenkes — Direktorat Gizi & KIA | 🟢 |
| OPD kabupaten | **Dinas Kesehatan** → Puskesmas → Posyandu/kader | 🟢 |
| Dasar/panduan | **Juknis PMT Berbahan Pangan Lokal (2024)**, Buku Saku Kader PMT, Buku Resep Makanan Lokal (2023) | 🟡 |
| Sasaran | (a) **Balita gizi kurang / berisiko stunting**; (b) **Ibu hamil KEK (Kekurangan Energi Kronis)** | 🟢 |
| Sumber dana | **DAK Non-Fisik (BOK)**, APBD Kabupaten, dan/atau **Dana Desa** | 🟡 |
| Frekuensi | Harian dalam satu siklus intervensi (umumnya sekitar 90 hari) | 🟠 |
| Konteks nasional | Prevalensi stunting Indonesia disebut **21,7%** | 🟡 |
| Konteks Pringsewu | Terdapat studi akademik "Pengaruh PMT Lokal terhadap Status Gizi Balita Stunting di **Pekon Wonosari, Kecamatan Gadingrejo, Kabupaten Pringsewu**, Tahun 2025" — bukti PMT berjalan di Pringsewu. | 🟢 |

> 🔴 **Tidak ditemukan:** nominal rupiah standar per anak per hari untuk PMT 2025/2026. **Jangan diisi.**

#### 3.14.3 Posyandu ILP — Integrasi Layanan Primer

| Atribut | Isi | Keyakinan |
|---|---|---|
| Nama | Posyandu Integrasi Layanan Primer | 🟢 |
| Pengampu | Kemenkes (Transformasi Layanan Primer) | 🟢 |
| OPD kabupaten | **Dinas Kesehatan** → Puskesmas → **Pustu** → **Posyandu** | 🟢 |
| Perubahan mendasar | Posyandu yang dulu hanya melayani balita & ibu hamil kini melayani **seluruh siklus hidup: usia 0 hingga lansia** | 🟢 |
| Layanan tambahan | Skrining PTM (tekanan darah, lingkar perut, gula darah), penyuluhan kesehatan, edukasi kesehatan | 🟢 |
| Frekuensi | Bulanan | 🟢 |
| Sumber dana | APBD, BOK, Dana Desa (operasional & insentif kader) | 🟠 |

---

### 3.15 PROGRAM DISABILITAS & LANSIA

#### 3.15.1 ATENSI — Asistensi Rehabilitasi Sosial

| Atribut | Isi | Keyakinan |
|---|---|---|
| Nama resmi | Asistensi Rehabilitasi Sosial | 🟢 |
| Singkatan | ATENSI | 🟢 |
| Dasar hukum | **Permensos No. 7 Tahun 2021** tentang Asistensi Rehabilitasi Sosial, diubah dengan **Permensos No. 7 Tahun 2022** | 🟢 |
| Kementerian pengampu | Kemensos — **Ditjen Rehabilitasi Sosial**, dilaksanakan melalui **Sentra/Balai** Kemensos di daerah | 🟢 |
| OPD pelaksana kabupaten | **Dinas Sosial** (pengusulan, verifikasi, pendampingan, penyerahan) | 🟢 |
| Pendekatan | **Berbasis keluarga**, **berbasis komunitas**, dan/atau **residensial** | 🟢 |
| **Sasaran (kriteria)** | Individu/keluarga/kelompok/komunitas dengan kriteria: **kemiskinan, ketelantaran, disabilitas, keterpencilan, ketunaan sosial & penyimpangan perilaku, korban bencana, korban tindak kekerasan/eksploitasi/diskriminasi** | 🟢 |
| **Komponen layanan** | (1) dukungan pemenuhan kebutuhan hidup layak; (2) perawatan sosial dan/atau pengasuhan anak; (3) dukungan keluarga; (4) terapi fisik; (5) terapi psikososial; (6) terapi mental spiritual; (7) pelatihan vokasional & pembinaan kewirausahaan; (8) bantuan sosial & asistensi sosial; (9) dukungan aksesibilitas | 🟢 |
| Bentuk bantuan konkret | **Alat bantu disabilitas** (kursi roda, kursi roda adaptif, alat bantu dengar, kaki/tangan palsu), **motor roda tiga / kendaraan roda tiga** sebagai sarana usaha, **modal usaha**, kebutuhan dasar | 🟢 |
| Nominal | 🔴 **Tidak ada nominal tunggal** — bantuan berbasis paket/kasus. Angka "Rp2.400.000" yang beredar untuk "bansos disabilitas" kemungkinan besar merujuk komponen disabilitas berat PKH, bukan ATENSI. | 🟠 |

**Data ATENSI di Kabupaten Pringsewu (2026) — 🟢 sumber berita resmi acara Wamensos:**

| Item | Nilai |
|---|---|
| Nilai bantuan ATENSI Pringsewu 2026 | **Rp1.036.411.418** (±Rp1 miliar) |
| Jumlah penerima | ±**1.000 penerima manfaat** |
| Rata-rata per penerima | ±**Rp1.036.411** 🟠 (turunan) |
| Bentuk bantuan | Kebutuhan dasar + pemberdayaan: **kendaraan roda tiga bagi penyandang disabilitas**, modal usaha |
| Pejabat | Wamensos **Agus Jabo Priyono**; Bupati Pringsewu **H. Riyanto Pamungkas** |
| Total bansos APBN diterima Pringsewu s/d Triwulan I 2026 | **> Rp50,5 miliar** |

#### 3.15.2 Home Care Lansia

| Atribut | Isi | Keyakinan |
|---|---|---|
| Status | **Program dalam pengembangan**, dikoordinasikan **Kemenko PMK** | 🟡 |
| Konsep | Perawatan sosial di rumah bagi lansia — lansia tetap tinggal di keluarga & lingkungannya | 🟢 |
| Arah kebijakan | Peningkatan layanan home care bagi lansia & disabilitas **berbasis bantuan sosial dan asuransi** | 🟡 |
| Pelaksana saat ini | Sebagian besar layanan home care lansia komersial/swasta. Layanan pemerintah berjalan lewat komponen **perawatan sosial** dalam ATENSI. | 🟠 |
| Nominal | 🔴 **Tidak ditemukan** — belum ada skema nominal nasional. |

---

### 3.16 SEKOLAH RAKYAT

| Atribut | Isi | Keyakinan |
|---|---|---|
| Nama | Sekolah Rakyat | 🟢 |
| Pengampu | **Kemensos** | 🟢 |
| OPD kabupaten | **Dinas Sosial** (penjangkauan & seleksi berbasis DTSEN) + Disdikbud (koordinasi); Pemkab menyediakan **hibah lahan** | 🟢 |
| Model | **Boarding school gratis penuh** — siswa tinggal di asrama dengan pengasuhan & pengawasan | 🟢 |
| **Kriteria siswa** | **Desil 1 atau desil 2 DTSEN**. Miskin ekstrem diprioritaskan. **Desil 3 berpeluang bila kuota belum terpenuhi.** | 🟢 |
| Manfaat | Sekolah gratis, **makan bergizi**, seragam, asrama, alat tulis — **tanpa pungutan biaya apa pun** | 🟢 |
| Mekanisme pendaftaran | **Tidak ada pendaftaran terbuka seperti SPMB.** Penerimaan melalui **penjangkauan aktif** berbasis data DTSEN oleh Dinas Sosial, pendamping PKH, atau pihak terkait. | 🟢 |
| Skala 2025 | ±**166 titik rintisan**, ±**15.000–16.000 siswa** | 🟡 |
| Skala 2026/2027 | ±**182 titik**, target **43.000–45.000 siswa** | 🟡 |
| Status Pringsewu | **Pemkab Pringsewu sedang membidik/mengincar hibah lahan untuk Sekolah Rakyat.** Dinilai cocok untuk memutus rantai kemiskinan ekstrem. | 🟢 |

> **Implikasi NADI:** karena penerimaan **berbasis penjangkauan aktif (bukan pendaftaran)**, aplikasi NADI dapat memberi nilai tinggi dengan fitur "daftar anak usia sekolah dari keluarga desil 1–2 yang belum/putus sekolah" sebagai *feed* penjangkauan.

---

### 3.17 PROGRAM KETENAGAKERJAAN

#### 3.17.1 Padat Karya Tunai (PKT / Cash for Work)

| Atribut | Isi | Keyakinan |
|---|---|---|
| Nama | Padat Karya Tunai Desa (PKTD) / Padat Karya Tunai infrastruktur | 🟢 |
| Pengampu | Kemendes PDT (PKT Desa) & Kementerian PU (padat karya infrastruktur) | 🟢 |
| OPD kabupaten | **DPMP** (untuk PKTD via Dana Desa), **Dinas PUPR** (padat karya infrastruktur) | 🟡 |
| Sumber dana | **Dana Desa** (fokus penggunaan 2026 huruf f) dan APBN Kementerian PU | 🟢 |
| Mekanisme | Proyek desa dikerjakan **swakelola**; pekerja lokal dibayar **upah harian atau mingguan langsung tunai** | 🟢 |
| Sasaran | **Kelompok miskin dan marginal**, penganggur/setengah penganggur, keluarga berisiko stunting | 🟢 |
| Tujuan ganda | (1) Infrastruktur desa terbangun; (2) daya beli & pendapatan masyarakat naik; juga **mendukung penurunan stunting** | 🟢 |
| Prinsip | Mengutamakan **sumber daya, tenaga kerja, dan teknologi lokal** | 🟢 |
| Capaian nasional | 2020–2024 padat karya Kementerian PU menyerap **4,12 juta tenaga kerja** (sumber daya air, jalan, jembatan, permukiman, perumahan) | 🟢 |
| Nominal upah | 🔴 **Tidak ada standar nasional** — mengikuti standar upah harian setempat/HSPK daerah. |

#### 3.17.2 Pelatihan Vokasi BLK / BPVP

| Atribut | Isi | Keyakinan |
|---|---|---|
| Pengampu | **Kemnaker** — **BPVP** (Balai Pelatihan Vokasi & Produktivitas, dulu BLK) pusat; **UPTD BLK** milik pemda | 🟢 |
| OPD kabupaten | **Dinas Ketenagakerjaan dan Transmigrasi** (di Pringsewu: **Disnakertrans**) | 🟢 |
| Biaya | **GRATIS** dibiayai pemerintah | 🟢 |
| Jaringan | **21 UPT BPVP** se-Indonesia + UPTD BLK milik pemda | 🟢 |
| Pendaftaran | Online via **skillhub.kemnaker.go.id**; juga **e-training.kemnaker.go.id** | 🟢 |
| Kriteria | Lulusan SMA/SMK/MA atau sederajat, **tanpa batasan tahun kelulusan** (dilonggarkan dari sebelumnya khusus lulusan 2023–2025) | 🟡 |
| Skala | Target **60.000 peserta** pada Bulan Pelatihan Vokasi Nasional | 🟡 |
| Job matching / bursa kerja | Fungsi melekat pada Disnaker kabupaten (**AKAD/AKL, bursa kerja, job fair, pengantar kerja**) | 🟠 |

> 🔴 **Tidak ditemukan:** apakah Kabupaten Pringsewu memiliki UPTD BLK sendiri. Terdapat entri "Kab. Pringsewu" di Direktori Online Disnaker se-Indonesia, tetapi keberadaan BLK tidak terkonfirmasi.

#### 3.17.3 BPJS Ketenagakerjaan Pekerja Rentan

| Atribut | Isi | Keyakinan |
|---|---|---|
| Nama | Perlindungan Jamsostek bagi Pekerja Rentan / BPU (Bukan Penerima Upah) | 🟢 |
| Pengampu | BPJS Ketenagakerjaan (BPJAMSOSTEK) | 🟢 |
| OPD kabupaten | **Dinas Ketenagakerjaan** + **Dinas Sosial** (identifikasi pekerja rentan) | 🟠 |
| **Iuran** | **Rp16.800 per bulan** untuk 2 program: **JKK (Jaminan Kecelakaan Kerja)** + **JKM (Jaminan Kematian)** | 🟢 |
| Manfaat | Perawatan akibat kecelakaan kerja, santunan, hingga **beasiswa bagi anak pekerja** | 🟢 |
| Sumber pembiayaan (skema pemda) | **APBD Kabupaten/Provinsi**, CSR perusahaan, Baznas, atau mandiri | 🟡 |
| Sasaran | Pekerja informal: petani, nelayan, pedagang, ojol, buruh harian, pekerja rentan | 🟢 |
| Contoh implementasi | Pemprov Jawa Barat mendorong kepesertaan pekerja formal & informal dengan iuran Rp16.800/bulan; 320.000 pengemudi ojol terdaftar sejak Mei 2025 | 🟢 |

> **Implikasi NADI:** ini adalah **intervensi APBD berbiaya sangat rendah** (Rp16.800 × 12 = **Rp201.600/orang/tahun**) yang melindungi keluarga miskin dari guncangan kehilangan pencari nafkah. Kandidat kuat rekomendasi program daerah.

---

## 4. STRUKTUR OPD KABUPATEN & TUPOKSI TERKAIT KEMISKINAN

### 4.1 Dasar Hukum Kelembagaan

| Regulasi | Isi relevan | Keyakinan |
|---|---|---|
| **UU No. 23 Tahun 2014** tentang Pemerintahan Daerah | Pembagian urusan pemerintahan konkuren: urusan wajib pelayanan dasar & non-pelayanan dasar | 🟢 |
| **PP No. 18 Tahun 2016** tentang Perangkat Daerah | Pedoman pembentukan & tipologi Perangkat Daerah (tipe A/B/C). Urusan wajib pelayanan dasar tetap dibentuk minimal sebagai **dinas tipe C**. | 🟢 |
| **UU No. 11 Tahun 2009** tentang Kesejahteraan Sosial | Pasal 21: penanggulangan kemiskinan mencakup penyediaan akses pelayanan perumahan & permukiman | 🟢 |
| **UU No. 13 Tahun 2011** tentang Penanganan Fakir Miskin | Pemda kabupaten/kota berwenang **menetapkan kebijakan, strategi, dan program penanganan fakir miskin tingkat kabupaten/kota** dalam bentuk **rencana penanganan fakir miskin di daerah**, berdasarkan kebijakan nasional | 🟢 |
| **PP No. 2 Tahun 2018** tentang SPM | Menetapkan **6 bidang SPM**: pendidikan, kesehatan, pekerjaan umum & penataan ruang, perumahan rakyat & kawasan permukiman, ketenteraman/ketertiban umum & perlindungan masyarakat, **sosial** | 🟢 |
| **Permendagri No. 59 Tahun 2021** tentang Penerapan SPM | Mekanisme penerapan SPM oleh pemda, indikator & target layanan terukur | 🟢 |
| **Permendagri No. 53 Tahun 2020** | Tata kerja & penyelarasan kerja serta pembinaan kelembagaan & SDM **TKPK Provinsi dan TKPK Kabupaten/Kota** | 🟢 |
| **Inpres No. 4 Tahun 2025** | DTSEN sebagai rujukan tunggal | 🟢 |
| **Inpres No. 9 Tahun 2025** | Percepatan pembentukan Koperasi Desa/Kelurahan Merah Putih | 🟢 |
| **Perpres No. 12 Tahun 2025** | RPJMN 2025–2029 (target JKN 98% 2025, 99% 2029) | 🟡 |

### 4.2 TKPKD — Tim Koordinasi Penanggulangan Kemiskinan Daerah

| Atribut | Isi | Keyakinan |
|---|---|---|
| Nama | Tim Koordinasi Penanggulangan Kemiskinan (TKPK) Kabupaten/Kota — populer disebut **TKPKD** | 🟢 |
| Dasar hukum | **Permendagri No. 53 Tahun 2020** | 🟢 |
| Kewajiban | **Setiap provinsi dan kabupaten/kota wajib membentuk TKPK** | 🟢 |
| Tugas | **Koordinasi perumusan kebijakan, perencanaan, pelaksanaan, dan pemantauan** pelaksanaan penanggulangan kemiskinan di wilayahnya | 🟢 |
| Keanggotaan | Unsur **pemerintah daerah, masyarakat, dunia usaha**, dan pemangku kepentingan lain | 🟢 |
| Ketua (praktik umum) | **Wakil Bupati/Wakil Wali Kota**; Sekretaris: **Kepala Bappeda** | 🟠 |
| Sekretariat | Dibentuk melalui **Keputusan Bupati/Wali Kota**; umumnya melekat di **Bappeda** | 🟡 |
| Produk kerja | (1) **RPKD (Rencana Penanggulangan Kemiskinan Daerah)**; (2) **Rencana Aksi Tahunan**; (3) **Laporan pelaksanaan penanggulangan kemiskinan** | 🟢 |
| Ritme kerja | Rapat koordinasi **minimal 3 kali dalam 1 tahun** atau sesuai kebutuhan; disusun berdasarkan **agenda kerja tahunan** | 🟢 |
| Pembina nasional | **Ditjen Bina Pembangunan Daerah (Bangda) Kemendagri** | 🟢 |

> **Implikasi NADI:** TKPKD adalah **"pengguna institusional" alami** aplikasi NADI. Alur RPKD → Rencana Aksi Tahunan → Laporan adalah *product surface* yang jelas: NADI bisa jadi tulang punggung data untuk ketiganya, plus penyiapan bahan 3 rakor/tahun.

### 4.3 Peta OPD Tipikal Kabupaten × Tupoksi Kemiskinan

| OPD | Urusan | Peran dalam penanggulangan kemiskinan | Program yang dipegang | Keyakinan |
|---|---|---|---|---|
| **Bappeda** (Badan Perencanaan Pembangunan Daerah) | Perencanaan | **Sekretariat TKPKD**; penyusun RPKD & Rencana Aksi; sinkronisasi RPJMD–RKPD; koordinasi lintas OPD; pengelola data kemiskinan daerah | RPKD, Rencana Aksi, Musrenbang | 🟡 |
| **Dinas Sosial** | Sosial (wajib pelayanan dasar) | **Leading sector.** Verifikasi & validasi DTSEN; penyaluran & pendampingan bansos pusat; rehabilitasi sosial; bansos daerah | PKH (koordinasi), Sembako, PBI-JKN (usulan), RST/Rutilahu, ATENSI, KUBE, PENA/PPSE, Sekolah Rakyat (penjangkauan), BTT | 🟢 |
| **Dinas Kesehatan** | Kesehatan (wajib pelayanan dasar) | Layanan primer bagi warga miskin; penurunan stunting; STBM/ODF; PMT; Posyandu ILP; koordinasi UHC/JKN | PMT, STBM, Posyandu ILP, PIS-PK, penurunan stunting | 🟢 |
| **Dinas Pendidikan & Kebudayaan** | Pendidikan (wajib pelayanan dasar) | PIP SD & SMP; penanganan **Anak Tidak Sekolah (ATS)**; BOS/BOSDA; bantuan seragam/perlengkapan | PIP (SD/SMP), BOS, program ATS | 🟢 |
| **Dinas PUPR** (di Pringsewu juga mengampu perumahan & permukiman) | PU & Penataan Ruang; Perumahan Rakyat & Kawasan Permukiman | Penanganan RTLH; air minum & sanitasi; jalan lingkungan; penanganan kawasan kumuh | BSPS, SANIMAS, PAMSIMAS, DAK Air Minum, padat karya infrastruktur | 🟡 |
| **Diskoperindag** (Koperasi, Perindustrian & Perdagangan) | Koperasi & UKM; Perdagangan; Perindustrian | Fasilitasi KUR; pembinaan UMKM; legalitas usaha (NIB/IUMK); pembinaan KDMP; stabilitas harga pangan | KUR (fasilitasi), pelatihan UMKM, KDMP | 🟡 |
| **Dinas Ketenagakerjaan & Transmigrasi** (Disnakertrans) | Tenaga Kerja | Pelatihan vokasi; job matching & bursa kerja; hubungan industrial; perlindungan pekerja rentan | BLK/BPVP, bursa kerja, BPJS TK pekerja rentan | 🟡 |
| **DPMP** (Dinas Pemberdayaan Masyarakat dan Pekon) | Pemberdayaan Masyarakat & Desa | Pembinaan penggunaan Dana Desa; BLT Desa; PKTD; pendampingan pekon; **Musyawarah Pekon** | BLT-DD, PKTD, ketahanan pangan desa, KDMP (bersama Diskoperindag) | 🟢 |
| **Dinas Ketahanan Pangan** | Pangan | Ketersediaan, keterjangkauan & konsumsi pangan; koordinasi Bantuan Pangan Beras; kawasan rumah pangan lestari; SKPG | Bantuan Pangan Beras (koordinasi), diversifikasi pangan | 🟡 |
| **Dinas Kependudukan & Pencatatan Sipil (Disdukcapil)** | Administrasi Kependudukan | **Gerbang semua bansos**: NIK valid, KK, akta kelahiran. Padan-data DTSEN ↔ Dukcapil. Jemput bola dokumen kependudukan bagi warga miskin. | Perekaman KTP-el, akta kelahiran, KIA | 🟢 |
| **Dinas P3AP2KB** | PPPA, Pengendalian Penduduk & KB | Keluarga berisiko stunting (eks P3KE/BKKBN); perlindungan perempuan & anak; kampung KB | Data keluarga berisiko stunting, PPA | 🟠 |
| **Dinas Pertanian / Dinas Perikanan** | Pertanian; Kelautan & Perikanan | Bantuan sarana produksi bagi petani/nelayan miskin; korporasi petani; hilirisasi (mis. **MOCAF** di Pringsewu) | Bantuan alsintan, benih, hilirisasi | 🟠 |
| **BPKAD / Bapenda** | Keuangan Daerah | Penganggaran belanja bansos & hibah; verifikasi kemampuan fiskal daerah | Alokasi APBD | 🟠 |
| **Bagian Kesra Setda** | Kesejahteraan Rakyat | Hibah/bansos keagamaan & kemasyarakatan; koordinasi program kesra | Hibah/bansos non-OPD | 🟠 |

---

## 5. KONTEKS KABUPATEN PRINGSEWU

### 5.1 Profil Wilayah & Kemiskinan

| Indikator | Nilai | Sumber/Tahun | Keyakinan |
|---|---|---|---|
| Jumlah kecamatan | **9** | Sejak 2013 | 🟢 |
| Nama kecamatan | Pardasuka, Ambarawa, Pagelaran, **Pagelaran Utara**, Pringsewu, Gadingrejo, Sukoharjo, Banyumas, Adiluwih | — | 🟢 |
| Jumlah pekon (desa) | **126** (akan menjadi **128** dengan 2 pekon baru) | 2025 | 🟢 |
| Jumlah kelurahan | **5** | — | 🟢 |
| Istilah lokal desa | **Pekon** (istilah Lampung); kepala desa = **Kepala Pekon** | — | 🟡 |
| Jumlah penduduk (DTSEN 2026) | **451.586 jiwa / 144.262 KK** | DTSEN 2026 | 🟢 |
| Jumlah penduduk (BPS 2024) | **442.049 jiwa** | BPS 2024 | 🟢 |
| **Penduduk desil 1–5 (rentan)** | **241.740 jiwa / 73.879 KK** (≈51,2% KK) | DTSEN 2026 | 🟢 |
| Persentase penduduk miskin 2023 | **9,14%** | BPS | 🟡 |
| **Persentase penduduk miskin 2024** | **8,32%** | BPS | 🟢 |
| **Persentase penduduk miskin akhir 2025** | **7,6%** | BPS (dikutip Pemkab) | 🟡 |
| Jumlah penduduk miskin 2024 | **34.420 jiwa** (±34,42 ribu) | BPS | 🟢 |
| **Garis kemiskinan** | **Rp583.425 per kapita per bulan** | BPS 2024 | 🟢 |
| Peringkat nasional penurunan kemiskinan | ke-**295** dari seluruh kabupaten/kota | 2024 | 🟠 |
| Backlog RTLH | **±1.700 unit** | Dinsos Pringsewu 2025 | 🟢 |
| Kepesertaan PBI dinonaktifkan | **±62.000 peserta** | 2026 | 🟡 |
| Tunggakan iuran JKN Pemkab | **Rp7,94 miliar** | 2026 | 🟡 |
| Capaian UHC wilayah (Cabang Bandarlampung) | **96,52%** per Mei 2026 | BPJS Kesehatan | 🟡 |
| Total bansos APBN diterima s/d TW I 2026 | **> Rp50,5 miliar** | Pemkab | 🟢 |
| Bupati | **H. Riyanto Pamungkas** | 2026 | 🟢 |

### 5.2 Daftar Lengkap OPD Kabupaten Pringsewu (dari situs resmi pringsewukab.go.id) 🟢

| # | Nama OPD | Situs | Relevansi kemiskinan |
|---|---|---|---|
| 1 | Sekretariat Daerah | setda.pringsewukab.go.id | Sedang (Bagian Kesra) |
| 2 | Sekretariat DPRD | sekretariatdprd.pringsewukab.go.id | Rendah |
| 3 | Inspektorat | inspektorat.pringsewukab.go.id | Rendah (pengawasan) |
| 4 | **Badan Perencanaan Pembangunan Daerah (Bappeda)** | bappeda.pringsewukab.go.id | **TINGGI — Sekretariat TKPKD** |
| 5 | Badan Pengelola Keuangan dan Aset Daerah (BPKAD) | bpkad.pringsewukab.go.id | Sedang |
| 6 | Badan Pendapatan Daerah (Bapenda) | bapenda.pringsewukab.go.id | Rendah |
| 7 | BKPSDM | bkpsdm.pringsewukab.go.id | Rendah |
| 8 | Badan Penanggulangan Bencana Daerah (BPBD) | bpbd.pringsewukab.go.id | Sedang (kerentanan bencana) |
| 9 | **Dinas Sosial** | dinsos.pringsewukab.go.id | **TINGGI — leading sector** |
| 10 | **Dinas Kesehatan** | dinkes.pringsewukab.go.id | **TINGGI** |
| 11 | RSUD Pringsewu | rsud.pringsewukab.go.id | Sedang (rujukan JKN) |
| 12 | **Dinas Pendidikan dan Kebudayaan** | disdikbud.pringsewukab.go.id | **TINGGI** |
| 13 | **Dinas PUPR** | pupr.pringsewukab.go.id | **TINGGI — RTLH, air, sanitasi** |
| 14 | **Dinas Pemberdayaan Masyarakat dan Pekon (DPMP)** | dpmp.pringsewukab.go.id | **TINGGI — Dana Desa, BLT-DD** |
| 15 | **Dinas Ketenagakerjaan dan Transmigrasi** | disnakertrans.pringsewukab.go.id | **TINGGI** |
| 16 | **Diskoperindag** (Koperasi, Perindustrian, Perdagangan) | diskoperindag.pringsewukab.go.id | **TINGGI — UMKM, KUR, KDMP** |
| 17 | **Dinas Ketahanan Pangan (DKP)** | dkp.pringsewukab.go.id | **TINGGI — pangan** |
| 18 | **Dinas Kependudukan dan Pencatatan Sipil** | disdukcapil.pringsewukab.go.id | **TINGGI — gerbang NIK** |
| 19 | Dinas P3AP2KB | kb.pringsewukab.go.id | Sedang–Tinggi (stunting, PPA) |
| 20 | Dinas Pertanian | distan.pringsewukab.go.id | Sedang (MOCAF, petani miskin) |
| 21 | Dinas Perikanan | perikanan.pringsewukab.go.id | Sedang |
| 22 | Dinas Lingkungan Hidup | dlh.pringsewukab.go.id | Rendah–Sedang |
| 23 | Dinas Perhubungan | dishub.pringsewukab.go.id | Rendah |
| 24 | Dinas Komunikasi dan Informatika | diskominfo.pringsewukab.go.id | **Sedang — mitra teknis aplikasi** |
| 25 | Dinas Perizinan (DPMPTSP) | dpmptsp.pringsewukab.go.id | Sedang (NIB UMKM) |
| 26 | Dinas Kepemudaan, Olahraga dan Pariwisata | disporpar.pringsewukab.go.id | Rendah |
| 27 | Dinas Perpustakaan Daerah | perpusda.pringsewukab.go.id | Rendah |
| 28 | Satuan Polisi Pamong Praja | polpp.pringsewukab.go.id | Rendah |
| 29 | Kantor Kesatuan Bangsa dan Politik | kesbangpol.pringsewukab.go.id | Rendah |
| 30 | Sekretariat Korpri | korpri.pringsewukab.go.id | Rendah |

> ⚠️ **Catatan penting:** Pringsewu **tidak memiliki Dinas Perumahan & Kawasan Permukiman terpisah** — urusan perumahan melekat di **Dinas PUPR**. Ini berbeda dari banyak kabupaten lain dan harus dicerminkan dalam mapping OPD di NADI.

### 5.3 Standar Layanan Dinas Sosial Kabupaten Pringsewu 🟢

Dari situs resmi dinsos.pringsewukab.go.id:

| # | Layanan |
|---|---|
| 1 | Surat Tanda Daftar dan Rekomendasi Izin Operasional Lembaga Kesejahteraan Sosial (LKS) |
| 2 | **Surat Keterangan Terdaftar DTKS** (kini seharusnya DTSEN) |
| 3 | Rekomendasi Izin Pengumpulan Uang dan Barang (PUB) |
| 4 | **Rehabilitasi Sosial bagi Penyandang Disabilitas** |
| 5 | **Rehabilitasi Sosial bagi Lanjut Usia Telantar** |
| 6 | Perlindungan Sosial bagi Korban Tindak Kekerasan dan Perdagangan Orang |
| 7 | Penanganan Korban Bencana Alam dan Bencana Sosial |
| 8 | Penanganan Orang Telantar dan Kehabisan Bekal |
| 9 | Komunikasi, Informasi, dan Edukasi (KIE) |
| 10 | Calon Orang Tua Asuh (COTA) |
| 11 | **Bantuan Sosial Tak Terduga (BTT)** bagi warga kurang mampu |
| 12 | Lembaga Konsultasi Kesejahteraan Keluarga (LK3) |

### 5.4 Program Unggulan / Khas Kabupaten Pringsewu

| Program | Deskripsi | Status | Keyakinan |
|---|---|---|---|
| **Hilirisasi Singkong → MOCAF** | Pengolahan singkong menjadi Modified Cassava Flour. Digunakan KPM sebagai bahan baku usaha produktif (kue, mi, olahan). Punya portal khusus: **mocaf.pringsewukab.go.id**. Didorong juga oleh Gubernur Lampung Rahmat Mirzani Djausal sebagai penggerak ekonomi inklusif. | Berjalan | 🟢 |
| **Rutilahu APBD** | 80 KPM, Rp1,2 miliar, TA 2025 | Berjalan | 🟢 |
| **ATENSI (kolaborasi Kemensos)** | Rp1.036.411.418 untuk ±1.000 penerima, 2026 | Berjalan | 🟢 |
| **Sekolah Rakyat** | Pemkab membidik hibah lahan untuk lokasi Sekolah Rakyat | Rencana | 🟢 |
| **Penguatan KMP** | Kunjungan Tim Kemendagri membahas penguatan KMP (kemungkinan Koperasi Merah Putih) | Berjalan | 🟠 |

> 🔴 **Tidak ditemukan:** dokumen RPJMD Kabupaten Pringsewu 2025–2029, RPKD Pringsewu, Perbup tentang penanggulangan kemiskinan, daftar lengkap program unggulan Bupati Riyanto Pamungkas, dan besaran APBD Pringsewu untuk bansos. **Ini gap paling kritis untuk NADI — perlu diambil langsung dari Bappeda/BPKAD Pringsewu.**

### 5.5 Konteks Provinsi Lampung

| Item | Isi | Keyakinan |
|---|---|---|
| Alokasi BSPS Provinsi Lampung | **11.000 unit** dari pemerintah pusat | 🟡 |
| Gubernur Lampung | **Rahmat Mirzani Djausal** | 🟢 |
| Dinas Sosial Provinsi Lampung | Menyelenggarakan Rapat Evaluasi Program Bantuan Sosial dalam rangka Penanggulangan Kemiskinan tingkat provinsi | 🟢 |
| Beasiswa Pemprov Lampung | Dilaporkan **tidak dianggarkan** oleh Pemprov Lampung (kritik media 2026) | 🟠 |
| KUBE di Lampung | Kemensos menggelar Bimtek untuk 50 kelompok penerima KUBE | 🟡 |
| Tunggakan iuran JKN Pemda se-wilayah Bandarlampung | **Rp134,2 miliar** | 🟡 |

---

## 6. MATRIKS PEMETAAN: FAKTOR RISIKO KEMISKINAN → PROGRAM INTERVENSI

Ini adalah **inti mesin rekomendasi NADI**. Setiap baris adalah aturan yang bisa dikodekan.

| Kode Risiko | Faktor risiko kemiskinan | Indikator terukur (input NADI) | Program yang cocok | OPD |
|---|---|---|---|---|
| R01 | Pendapatan sangat rendah / miskin ekstrem | Desil DTSEN = 1; pengeluaran < garis kemiskinan (Rp583.425/kapita/bln) | PKH, Sembako, BLT-DD, Bantuan Pangan Beras, BLT Kesra | Dinsos, DPMP |
| R02 | Rawan pangan rumah tangga | Frekuensi makan < 3x; skor keragaman pangan rendah | Sembako, Bantuan Pangan Beras, MBG, ketahanan pangan Dana Desa, KDMP gerai sembako | Dinsos, DKP, DPMP |
| R03 | Anak balita stunting / gizi kurang | TB/U < -2 SD; BB/U kurang | PMT pangan lokal, MBG, Posyandu ILP, PKH komponen anak usia dini, sanitasi | Dinkes, DPMP |
| R04 | Ibu hamil KEK / risiko tinggi | LILA < 23,5 cm; ANC tidak lengkap | PMT ibu hamil, MBG, PKH komponen ibu hamil, PBI-JKN | Dinkes, Dinsos |
| R05 | Anak usia sekolah putus/terancam putus sekolah | Anak 7–18 th tidak terdaftar Dapodik; kehadiran <85% | PIP, PKH komponen pendidikan, **Sekolah Rakyat** (desil 1–2), program ATS | Disdikbud, Dinsos |
| R06 | Tidak lanjut ke pendidikan tinggi | Lulusan SMA/SMK dari desil 1–3 tidak kuliah | KIP Kuliah, beasiswa daerah | Disdikbud |
| R07 | Tidak punya jaminan kesehatan | Tidak terdaftar/nonaktif di JKN | PBI-JKN Pusat (desil 1–4), PBI Daerah APBD | Dinsos, Dinkes |
| R08 | Rumah tidak layak huni | Salah satu dari 5 kriteria RTLH; luas lantai <7,2 m²/orang | BSPS (Rp20jt), RST Kemensos (Rp20jt), Rutilahu APBD (±Rp15jt), Dana Desa | PUPR, Dinsos, DPMP |
| R09 | Tidak punya akses sanitasi layak | Tidak punya jamban/jamban tidak layak; BABS | SANIMAS DAK, STBM, jambanisasi Dana Desa/Baznas | PUPR, Dinkes, DPMP |
| R10 | Tidak punya akses air minum layak | Sumber air tidak terlindungi | PAMSIMAS, DAK Air Minum, Dana Desa | PUPR, DPMP |
| R11 | Lansia telantar | Usia ≥60 (prioritas ≥70), tanpa penopang ekonomi | PKH komponen lansia (Rp2,4jt/thn), ATENSI, Posyandu ILP lansia, home care | Dinsos, Dinkes |
| R12 | Penyandang disabilitas | Disabilitas berat / butuh alat bantu | PKH komponen disabilitas berat (Rp2,4jt/thn), ATENSI (kursi roda, alat bantu dengar, motor roda tiga), pelatihan vokasi inklusif | Dinsos, Disnakertrans |
| R13 | Pengangguran / setengah pengangguran | Usia kerja tidak bekerja / jam kerja <35 jam/mgg | Prakerja, BLK/BPVP, PKTD, bursa kerja/job matching | Disnakertrans, DPMP |
| R14 | Usaha mikro tanpa modal | Punya usaha <6 bln atau tanpa akses kredit formal | KUR Super Mikro/Mikro, PENA/PPSE, KUBE, KDMP simpan pinjam | Diskoperindag, Dinsos |
| R15 | Pekerja informal tanpa perlindungan | Petani/nelayan/pedagang/ojol tanpa BPJS TK | BPJS TK Pekerja Rentan (Rp16.800/bln) via APBD/CSR/Baznas | Disnakertrans, Dinsos |
| R16 | Tidak punya dokumen kependudukan | Tanpa NIK valid / KK / akta kelahiran | Jemput bola Dukcapil — **prasyarat semua bansos** | Disdukcapil |
| R17 | Perempuan kepala keluarga | PEKKA dari keluarga miskin | BLT-DD (kriteria eksplisit), PKH, PENA/PPSE, KUBE | Dinsos, DPMP |
| R18 | Anggota keluarga sakit kronis/menahun | Penyakit kronis dalam keluarga | BLT-DD (kriteria eksplisit), PBI-JKN, ATENSI | DPMP, Dinsos |
| R19 | Kehilangan mata pencaharian mendadak | PHK / gagal panen / bencana | BLT-DD (kriteria eksplisit), Prakerja, BTT Dinsos, PKTD | DPMP, Dinsos, Disnakertrans |
| R20 | Terdampak bencana | Korban bencana alam/sosial | Penanganan korban bencana (Dinsos/BPBD), ATENSI | Dinsos, BPBD |

---

## 7. USULAN SKEMA SEED DATA UNTUK APLIKASI NADI

Struktur yang disarankan agar tabel di atas bisa langsung menjadi database.

### 7.1 Tabel `programs`

| Kolom | Tipe | Contoh |
|---|---|---|
| `id` | string (slug) | `pkh` |
| `nama_resmi` | text | `Program Keluarga Harapan` |
| `singkatan` | text | `PKH` |
| `jenis` | enum | `cash_transfer` / `in_kind` / `insurance_subsidy` / `infrastructure` / `service` / `credit` / `training` |
| `dasar_hukum` | text[] | `["Permensos No. 1 Tahun 2018"]` |
| `kementerian_pengampu` | text | `Kementerian Sosial RI` |
| `opd_pelaksana_kabupaten` | text[] | `["dinas_sosial"]` |
| `sumber_dana` | enum[] | `["APBN"]` |
| `tingkat_eksekusi` | enum | `pusat_disalurkan_di_daerah` / `daerah` / `desa` / `mandiri_online` |
| `desil_min` / `desil_max` | int | `1` / `4` |
| `basis_data` | enum | `DTSEN` / `Dapodik` / `mandiri` / `lokasi` |
| `frekuensi` | enum | `bulanan` / `triwulanan` / `tahunan` / `sekali` / `harian` / `ad_hoc` |
| `mekanisme_penyaluran` | text | `Transfer rekening Himbara via KKS / PT Pos` |
| `faktor_risiko` | text[] | `["R01","R03","R05","R11","R12"]` |
| `status_aktif` | enum | `aktif` / `tidak_pasti` / `dihentikan` |
| `confidence` | enum | `pasti` / `cukup_kuat` / `perkiraan` / `tidak_ditemukan` |
| `sumber_url` | text[] | — |

### 7.2 Tabel `program_benefits` (relasi 1-ke-banyak dengan `programs`)

| Kolom | Tipe | Contoh |
|---|---|---|
| `program_id` | fk | `pkh` |
| `komponen` | text | `anak_sma` |
| `label` | text | `Anak SMA/SMK/MA sederajat` |
| `nominal_per_periode` | int | `500000` |
| `periode` | enum | `triwulan` |
| `nominal_per_tahun` | int | `2000000` |
| `satuan` | enum | `rupiah` / `kg` / `porsi` / `unit` |
| `confidence` | enum | `pasti` |
| `catatan_konflik` | text | null |

### 7.3 Tabel `eligibility_rules`

| Kolom | Tipe | Contoh |
|---|---|---|
| `program_id` | fk | `sekolah_rakyat` |
| `tipe` | enum | `desil` / `usia` / `status` / `dokumen` / `kondisi_rumah` / `lokasi` |
| `operator` | enum | `in` / `gte` / `lte` / `eq` / `exists` |
| `nilai` | json | `[1,2]` |
| `wajib` | bool | `true` |
| `prioritas` | int | `1` |

### 7.4 Tabel `opd` (khusus Pringsewu)

Gunakan daftar 30 OPD di Bagian 5.2, dengan kolom `relevansi_kemiskinan` (tinggi/sedang/rendah), `situs`, dan relasi many-to-many ke `programs`.

### 7.5 Tabel `wilayah` (Pringsewu)

9 kecamatan × 126 pekon + 5 kelurahan. Gunakan kode wilayah BPS/Kemendagri sebagai primary key agar bisa join dengan data DTSEN & BPS.

---

## 8. HAL YANG TIDAK BERHASIL DITEMUKAN (JANGAN DIISI/DIKARANG)

| # | Item | Catatan |
|---|---|---|
| 1 | Jumlah KPM PKH, Sembako, PBI-JKN spesifik Kabupaten Pringsewu | Perlu data dari Dinsos Pringsewu / SIKS-NG |
| 2 | RPJMD Kabupaten Pringsewu 2025–2029 | Perlu dari Bappeda Pringsewu |
| 3 | RPKD (Rencana Penanggulangan Kemiskinan Daerah) Pringsewu | Perlu dari Bappeda/TKPKD |
| 4 | Perbup Pringsewu tentang penanggulangan kemiskinan / SOTK terbaru | Perlu dari JDIH Pringsewu |
| 5 | Besaran APBD Pringsewu untuk belanja bansos 2025/2026 | Perlu dari BPKAD |
| 6 | Nominal PMT per anak/ibu hamil per hari (2025/2026) | Juknis Kemenkes tidak berhasil diambil |
| 7 | Nominal standar SANIMAS/PAMSIMAS/jambanisasi per unit | Ditentukan per DAK/lokasi |
| 8 | Nominal ATENSI per jenis bantuan (rincian paket) | Bersifat kasuistis |
| 9 | Nomor Permenko KUR terbaru untuk 2025/2026 | Portal resmi kur.ekon.go.id masih menampilkan Permenko 2/2021 |
| 10 | Struktur SK TKPKD Kabupaten Pringsewu (ketua, anggota) | Perlu dari Bappeda |
| 11 | Keberadaan UPTD BLK Kabupaten Pringsewu | Tidak terkonfirmasi |
| 12 | Alokasi unit BSPS untuk Kabupaten Pringsewu | Hanya ditemukan angka provinsi (11.000 unit Lampung) |
| 13 | Program beasiswa daerah Kabupaten Pringsewu | Tidak ditemukan; Pemprov Lampung dilaporkan tidak menganggarkan beasiswa |
| 14 | Kelanjutan resmi BLT Kesra 2026 | Belum ada pengumuman resmi per Juli 2026 |
| 15 | Rincian nominal per komponen ATENSI dalam Permensos 7/2021 | Teks lampiran tidak berhasil diambil |
| 16 | Status hukum PENA vs PPSE (menggantikan atau paralel) | Ambigu di sumber terbuka |
| 17 | Daftar lengkap larangan komoditas Program Sembako | Tidak eksplisit di sumber yang diambil |
| 18 | Data stunting & ODF tingkat pekon di Pringsewu | Perlu dari Dinkes Pringsewu |

---

## 9. REKOMENDASI LANGKAH VERIFIKASI BERIKUTNYA

| Prioritas | Aksi | Sumber target |
|---|---|---|
| 1 | Ambil **Juknis PKH terbaru** & konfirmasi nominal lansia/disabilitas (Rp2,4jt vs Rp3jt) | Dinas Sosial Pringsewu / Koordinator Kabupaten PKH |
| 2 | Ambil **RPJMD & RPKD Pringsewu** | Bappeda Pringsewu, JDIH Pringsewu |
| 3 | Ambil **rekap SIKS-NG/DTSEN Pringsewu** per pekon & desil | Dinas Sosial Pringsewu |
| 4 | Ambil **daftar penerima & pagu bansos APBD 2026** | BPKAD Pringsewu |
| 5 | Konfirmasi **struktur & agenda TKPKD Pringsewu** | Bappeda Pringsewu |
| 6 | Ambil **Permendes 16/2026** teks penuh untuk validasi 15% BLT & 20% ketahanan pangan | JDIH Kemendes / peraturan.go.id |
| 7 | Ambil **Permen PKP 6/2026** untuk validasi nominal & kriteria BSPS terbaru | JDIH Kementerian PKP |
| 8 | Ambil **data stunting & ODF per pekon** | Dinas Kesehatan Pringsewu |

---

## 10. DAFTAR SUMBER

### Regulasi & Portal Resmi
- [Inpres No. 4 Tahun 2025 tentang DTSEN — Dinsos Kab. Dairi](https://dinsos.dairikab.go.id/detail/postingan/inpres-nomor-4-tahun-2025-tentang-data-tunggal-sosial-dan-ekonomi-nasional-dtsen-resmi-diterbitkan)
- [Portal DTSEN — dtsen.data.go.id](https://dtsen.data.go.id/)
- [BPS — DTSEN Jadi Rujukan Bersama, BPS Jelaskan Arti Desil](https://www.bps.go.id/en/news/2026/08/22/938/dtsen-jadi-rujukan-bersama--bps-jelaskan-arti-desil.html)
- [DTKS Dihapus Ganti DTSEN — Dinsos Prov. Jatim](https://dinsos.jatimprov.go.id/detail-berita-publik/dtks-dihapus-ganti-dtsen-data-tunggal-sosial-ekonomi-nasional-implementasi-inpres-no-4-tahun-2025)
- [Permensos No. 1 Tahun 2018 tentang PKH — Jogloabang](https://www.jogloabang.com/komunitas/permensos-no-1-tahun-2018-tentang-program-keluarga-harapan)
- [Lampiran Permensos No. 1 Tahun 2018 — UIN Antasari](https://idr.uin-antasari.ac.id/22887/10/LAMPIRAN.pdf)
- [Permensos No. 5 Tahun 2021 tentang Sembako (PDF)](https://sidetapa-buleleng.desa.id/assets/files/dokumen/PERMENSOS%20NOMOR%205%20TAHUN%202021%20TENTANG%20SEMBAKO.pdf)
- [Permensos No. 7 Tahun 2021 tentang ATENSI — JDIH BPK](https://peraturan.bpk.go.id/Details/217211/permensos-no-7-tahun-2021)
- [Permensos No. 7 Tahun 2022 (perubahan ATENSI) — peraturan.go.id](https://peraturan.go.id/id/permensos-no-7-tahun-2022)
- [Permendagri No. 53 Tahun 2020 tentang TKPK — JDIH BPK](https://peraturan.bpk.go.id/Details/163101/permendagri-no-53-tahun-2020)
- [PP No. 18 Tahun 2016 tentang Perangkat Daerah (PDF, BKN)](https://www.bkn.go.id/storage/2016/10/PP-NOMOR-18-TAHUN-2016-PERANGKAT-DAERAH.pdf)
- [PP No. 2 Tahun 2018 tentang SPM (PDF)](https://www.kemhan.go.id/itjen/wp-content/uploads/2018/10/pp2-2018bt.pdf)
- [Permendagri No. 59 Tahun 2021 tentang Penerapan SPM (PDF)](https://localisesdgs-indonesia.org/asset/file/Pengetahuan%20TPB/Peraturan%20Menteri%20Dalam%20Negeri%20Nomor%2059%20Tahun%202021%20Tentang%20Penerapan%20Standar%20Pelayanan%20Minimal.pdf)
- [UU No. 13 Tahun 2011 tentang Penanganan Fakir Miskin — JDIH BPK](https://peraturan.bpk.go.id/Details/39223/uu-no-13-tahun-2011)
- [Permenkes No. 3 Tahun 2014 tentang STBM — JDIH BPK](https://peraturan.bpk.go.id/Home/Details/116706/permenkes-no-3-tahun-2014)
- [Inpres No. 9 Tahun 2025 tentang Kopdes Merah Putih — Wantimpres RI](https://wantimpres.go.id/id/2025/04/presiden-ri-menerbitkan-inpres-nomor-9-tahun-2025-tentang-percepatan-pembentukan-koperasi-desa-kelurahan-merah-putih/)
- [Kebijakan KUR — kur.ekon.go.id](https://kur.ekon.go.id/kebijakan-kur)
- [Target KUR 2025 Rp300 Triliun — Kemenko Perekonomian](https://ekon.go.id/publikasi/detail/6114/resmi-target-kur-2025-naik-menjadi-rp300-triliun)
- [Indeks Manfaat Program Sembako — DJPb Kemenkeu](https://djpb.kemenkeu.go.id/kanwil/kaltim/id/data-publikasi/pub/pengumuman/2916-indeks-manfaat-program-sembako.html)
- [Tata Cara Pinjaman Kopdes Merah Putih — DJPb Kemenkeu](https://djpb.kemenkeu.go.id/kppn/manna/id/data-publikasi/artikel/3249-tata-cara-pinjaman-dalam-rangka-pendanaan-koperasi-desa-kelurahan-merah-putih.html)
- [BGN — Anggaran Bahan Makan MBG Rp8.000–Rp10.000](https://www.bgn.go.id/news/siaran-pers/bgn-ingatkan-anggaran-bahan-makan-mbg-rp8000-rp10000-bukan-rp15000)
- [Klarifikasi Puslapdik: Nominal PIP SMA/SMK Rp1.800.000](https://puslapdik.kemendikdasmen.go.id/klarifikasi-puslapdik-nominal-dana-pip-jenjang-sma-dan-smk-sebesar-rp1-800-000/)
- [Bapanas — Bantuan Pangan Beras & Minyak Goreng 33,2 Juta KPM](https://badanpangan.go.id/blog/post/meningkat-jadi-332-juta-keluarga-penerima-manfaat-pemerintah-siapkan-bantuan-pangan-beras-dan-minyak-goreng)
- [Buku Saku BSPS — Kementerian PKP (PDF)](https://pkp.go.id/s3/website-perumahan/prod-storage/bp3kp-sumatera-v/produk/buku-saku-bsps-bp3kp-sumatera-v/01kbc34v48xtxtb5ap0za2fw5t.pdf)
- [Kemensos — Bansos RS Rutilahu](https://kemensos.go.id/melalui-bansos-rs-rutilahu-penerima-bantuan-mendapatkan-rumah-layak-huni)
- [Kemensos — 25.360 Wirausahawan lewat PENA](https://kemensos.go.id/kementerian-sosial-ri-lahirkan-25360-wirausahawan-lewat-pahlawan-ekonomi-nusantara-pena)
- [BPJS Ketenagakerjaan — Iuran Rp16.800 Pekerja Informal](https://www.bpjsketenagakerjaan.go.id/berita/28039/Bayar-Iuran-Rp16.800-per-Bulan,-Pekerja-Informal-Terlindungi-BPJAMSOSTEK)
- [Kemendagri Bangda — Optimalisasi Peran TKPK](https://bangda.kemendagri.go.id/berita/baca_kontent/1465/percepat_penurunan_angka_kemiskinan_ekstrem_pemda_optimalkan_peran_tkpk)
- [Pokja AMPL — PAMSIMAS](https://www.ampl.or.id/program/program-nasional-penyediaan-air-minum-dan-sanitasi-berbasis-masyarakat-pamsimas-/2)
- [Pokja AMPL — SANIMAS](https://www.ampl.or.id/program/sanitasi-berbasis-masyarakat-sanimas-/3)
- [TNP2K — Padat Karya Tunai / Cash for Work](https://www.tnp2k.go.id/news/cash-for-work-encourages-the-improvement-of-community-welfare)
- [Kemenko PMK — Padat Karya Tunai di Desa](https://arsip.kemenkopmk.go.id/artikel/pemerintah-siap-laksanakan-program-padat-karya-tunai-di-desacash-work)
- [Kemenko PMK — Home Care Berkelanjutan untuk Lansia](https://www.kemenkopmk.go.id/pemerintah-akan-tingkatkan-pelayanan-home-care-bagi-lansia)

### Sumber Pringsewu & Lampung
- [Portal Resmi Kabupaten Pringsewu](https://www.pringsewukab.go.id/)
- [Tentang Pringsewu — pringsewukab.go.id](https://www.pringsewukab.go.id/portal/berita/profil/tentang-pringsewu)
- [Dinas Sosial Kabupaten Pringsewu](https://dinsos.pringsewukab.go.id/)
- [MOCAF Pringsewu — mocaf.pringsewukab.go.id](https://mocaf.pringsewukab.go.id/tentang-kami/)
- [BPS Kabupaten Pringsewu — Angka Kemiskinan](https://pringsewukab.bps.go.id/en/statistics-table/2/MjA5IzI=/angka-kemiskinan-kabupaten-pringsewu.html)
- [BPS Pringsewu — Profil Kemiskinan Maret 2024](https://pringsewukab.bps.go.id/en/pressrelease/2024/08/07/1472/profil-kemiskinan-kabupaten-pringsewu-maret-2024.html)
- [Databoks — Jumlah Penduduk & Persentase Kemiskinan Pringsewu 2010–2024](https://databoks.katadata.co.id/demografi/statistik/ac90936ba340044/jumlah-penduduk-dan-persentase-kemiskinan-di-kabupaten-pringsewu-2010-2024)
- [Lampung Monitor — 34,42 Ribu Penduduk Pringsewu Masih Miskin](https://lampungmonitor.com/daerah/3442-ribu-penduduk-pringsewu-masih-hidup-dalam-kemiskinan/)
- [Bupati Pringsewu Serahkan Bantuan Rutilahu kepada 80 KPM — Lampung Corner](https://lampungcorner.com/bupati-pringsewu-serahkan-bantuan-sosial-rutiahu-kepada-80-kpm/)
- [Pemkab Pringsewu & Kemensos Salurkan ATENSI 2026 — Media Nusantara News](https://www.medianusantaranews.com/2026/06/11/pemkab-pringsewu-dan-kemensos-ri-salurkan-bantuan-atensi-tahun-2026-untuk-tingkatkan-kesejahteraan-masyarakat/)
- [Wamensos Serahkan Bantuan ATENSI di Pringsewu — Sir Lampung](https://www.sirlampung.com/kunjungi-pringsewu-wakil-menteri-sosial-ri-serahkan-bantuan-atensi/)
- [Pemkab Pringsewu Bidik Hibah Lahan Sekolah Rakyat — RRI](https://rri.co.id/bandar-lampung/nasional/2485503/pemkab-pringsewu-bidik-hibah-lahan-bakal-sekolah-rakyat)
- [Pringsewu Dorong Hilirisasi Singkong Jadi MOCAF — Tribun Lampung](https://lampung.tribunnews.com/lampung/1211379/pringsewu-dorong-hilirisasi-singkong-jadi-mocaf-untuk-perkuat-ekonomi-warga)
- [Gubernur Lampung Dorong Produksi Mocaf di Pringsewu — Biro Adpim Lampung](https://biroadpim.lampungprov.go.id/detail-post/gubernur-rahmat-mirzani-djausal-dorong-produksi-mocaf-sebagai-penggerak-ekonomi-inklusif-di-kabupaten-pringsewu-hilirisasi-singkong-dinilai-mampu-memperkuat-ketahanan-pangan-dan-ekonomi-daerah)
- [Pemprov Lampung & Kementerian PKP — Percepatan Bedah Rumah (11.000 unit)](https://biroadpim.lampungprov.go.id/detail-post/pemprov-lampung-perkuat-sinergi-dengan-kementerian-pkp-dorong-percepatan-calon-penerima-bantuan-program-bedah-rumah-di-lampung)
- [Dinas Sosial Provinsi Lampung](https://dinsos.lampungprov.go.id/)
- [Kemensos Bimtek 50 Kelompok KUBE di Lampung — Pemprov Lampung](https://lampungprov.go.id/detail-post/kemensos-gelar-bimtek-untuk-50-kelompok-penerima-bantuan-kube)
- [Tunggakan Iuran JKN Pemda Lampung Rp134,2 Miliar — VoxLampung](https://voxlampung.com/2026/07/09/tunggakan-iuran-jkn-pemda-capai-rp1342-miliar-bpjs-tekankan-hak-kesehatan-masyarakat/)
- [BPJS Kesehatan Bandarlampung Kejar UHC 99% — Antara Lampung](https://lampung.antaranews.com/berita/825781/bpjs-kesehatan-bandarlampung-kejar-target-uhc-99-persen)
- [Jumlah Pekon Pringsewu Bertambah Jadi 128 — Prioritastv](https://prioritastv.com/2025/05/14/jumlah-desa-di-kabupaten-pringsewu-bakal-bertambah-jadi-128-ini-nama-pekonnya/)
- [Pengaruh PMT Lokal terhadap Balita Stunting di Pekon Wonosari, Gadingrejo, Pringsewu 2025 — Jurnal LITERA](https://litera-academica.com/ojs/litera/article/view/312)

### Sumber Media / Sekunder (nominal & operasional)
- [8 Kategori Penerima PKH 2026 dan Besarannya — Detik](https://www.detik.com/jabar/jabar-gaskeun/d-8448192/8-kategori-penerima-pkh-2026-dan-besaran-uangnya)
- [Besaran Bantuan PKH 2026 per Komponen — Liputan6](https://www.liputan6.com/hot/read/8273080/besaran-bantuan-pkh-2026)
- [Bansos Lansia & Disabilitas Rp600 Ribu/Bulan — Nova Grid](https://nova.grid.id/read/054342025/bansos-untuk-lansia-dan-disabilitas-cair-hingga-rp600-ribu-per-bulan?page=all)
- [Besaran PIP 2025 untuk SD, SMP, SMA — CNN Indonesia](https://www.cnnindonesia.com/edukasi/20250714164134-569-1250580/berapa-besaran-pip-2025-untuk-siswa-sd-smp-sma)
- [Kriteria Penerima PIP SD, SMP, SMA 2025 — Detik](https://www.detik.com/sumbagsel/berita/d-8019442/kriteria-penerima-pip-sd-smp-dan-sma-2025-lengkap-cara-ceknya)
- [5 Klaster Biaya Hidup KIP Kuliah 2026](https://bansoskemensosgo.id/5-klaster-biaya-hidup-kip-kuliah-2026/)
- [Besaran Bantuan KIP Kuliah 2026 Berdasarkan Klaster — ITERA](https://www.itera.ac.id/blog/besaran-bantuan-kip-kuliah-2026-berdasarkan-akreditasi-dan-klaster-wilayah/)
- [Apa Itu BLT Dana Desa 2026 — Detik](https://www.detik.com/jogja/bisnis/d-8463219/apa-itu-blt-dana-desa-2026-ini-pengertian-kriteria-penerima-serta-aturannya)
- [Permendes 16/2025: BLT Dana Desa Paling Lama 3 Bulan — Desa Balaan](https://www.balaan.my.id/artikel/2025/12/31/permendes-162025-blt-dana-desa-hanya-paling-lama-3-bulan)
- [8 Prioritas Dana Desa 2026, BLT Maks Rp300 Ribu — Portal Pantura](https://www.portalpantura.com/news/bangun-desa/pemerintah-tetapkan-8-prioritas-dana-desa-2026-blt-maksimal-rp300-ribu-per-bulan-28030/)
- [8 Prioritas Dana Desa 2026 — DPMG Banda Aceh](https://dpmg.bandaacehkota.go.id/2026/01/01/8-prioritas-dana-desa-2026/)
- [Cara Mendapatkan BSPS, Bantuan Bedah Rumah Tak Layak Huni — Kompas](https://www.kompas.com/properti/read/2025/10/23/151043821/cara-mendapatkan-bsps-bantuan-bedah-rumah-tak-layak-huni)
- [Bantuan Bedah Rumah Rp20 Juta Tak Naik 5 Tahun — Kompas](https://www.kompas.com/properti/read/2026/08/15/214116521/tak-naik-selama-5-tahun-bantuan-bedah-rumah-rp-20-juta-disebut-tak)
- [Bansos RST Bantu Kebutuhan Perumahan Fakir Miskin — DJPb Kemenkeu](https://djpb.kemenkeu.go.id/portal/id/berita/lainnya/opini/4029-bansos-rumah-sejahtera-terpadu-rst-bantu-penuhi-kebutuhan-perumahan-untuk-fakir-miskin.html)
- [Dinsos Tabalong Verifikasi Rutilahu Rp20 Juta per Rumah](https://portal.tabalongkab.go.id/post/dinsos-tabalong-verifikasi-39-usulan-penerima-bantuan-rs-rutilahu-targetkan-bantuan-rp-20-juta-per-rumah)
- [Modal Usaha Rp5 Juta dari Kemensos: Beda PPSE dan PENA — UMSU](https://ic2lc.umsu.ac.id/kini/modal-usaha-rp5-juta-dari-kemensos-apa-bedanya-ppse-dan-pena/)
- [Prosedur Pengusulan KUBE — Dinsos Kalbar](https://dinsos.kalbarprov.go.id/blog/2019/09/12/syarat-pengajuan-kelompok-usaha-bersama-kube/)
- [KUBE — Dinsos Buleleng](https://dinsos.bulelengkab.go.id/informasi/detail/artikel/kelompok-usaha-bersama-kube-23)
- [Anggaran Perlindungan Sosial Rp508,2 Triliun RAPBN 2026 — SWA](https://swa.co.id/read/462793/anggaran-perlindungan-sosial-rp5082-triliun-di-rapbn-2026)
- [Kemensos Salurkan Bansos Triwulan III 2026: PKH 7 Juta KPM, Sembako 12 Juta — Antara](https://kupang.antaranews.com/berita/196192/kemensos-menyalurkan-bansos-triwulan-iii-2026-pkh-7-juta-kpm-sembako-12-juta)
- [Belanja Bansos Semester I 2026 Rp78,3 T — Katadata](https://katadata.co.id/finansial/makro/6a6179c4bb880/belanja-bansos-semester-i-2026-rp-78-3-t-termasuk-pkh-hingga-kartu-sembako)
- [Anggaran MBG Rp900 Miliar per Hari Mulai 2026 — Investor Trust](https://investortrust.id/macro/87187/anggaran-mbg-capai-rp-900-miliar-per-hari-mulai-2026-85-untuk-pangan)
- [Menilik Eksistensi Program MBG — Media Keuangan Kemenkeu](https://mediakeuangan.kemenkeu.go.id/article/show/menilik-eksistensi-program-mbg-atau-makan-bergizi-gratis)
- [Sekolah Rakyat: Fasilitas, Syarat, Sistem Pendidikan 2026 — ITERA](https://blog.itera.ac.id/sekolah-rakyat-gratis-atau-bayar-ini-fasilitas-syarat-dan-sistem-pendidikan-2026/)
- [Ingin Daftar ke Sekolah Rakyat? Cek Syaratnya — Indonesia Baik](https://cmsin.indonesiabaik.id/infografis/ingin-daftar-ke-sekolah-rakyat-cek-syaratnya)
- [Kriteria Penerima BLT Kesra 2026 Rp900.000 — BeritaSatu](https://www.beritasatu.com/ekonomi/2995549/kriteria-penerima-blt-kesra-2026-rp900000-begini-cek-status-bansos)
- [Beda BLT Kesra dan BLT Dana Desa — Detik](https://www.detik.com/jogja/bisnis/d-8472105/apa-bedanya-blt-kesra-dan-blt-dana-desa-ini-pengertian-besaran-jadwal-cairnya)
- [Bagaimana Kriteria Penerima PBI BPJS Kesehatan — Hukumonline](https://www.hukumonline.com/klinik/a/bagaimana-kriteria-penerima-pbi-bpjs-kesehatan-lt69b8f28a35d6a/)
- [Kriteria Penerima Bantuan Iuran Jaminan Kesehatan — BPK Kalsel (PDF)](https://kalsel.bpk.go.id/easy/doc/TULISANHUKUM/Tulisan-hukum-bantuan-iuran-jaminan-kesehatan-final-Binbangkum.pdf)
- [Pelatihan Vokasi Kemnaker 2026: Syarat & Cara Daftar — KompasTV](https://www.kompas.tv/amp/info-publik/658591/besok-pendaftaran-terakhir-pelatihan-vokasi-kemnaker-2026-ini-syarat-dan-cara-daftarnya)
- [Bulan Pelatihan Vokasi Nasional, Target 60 Ribu Peserta — Detik](https://news.detik.com/berita/d-8141827/bulan-pelatihan-vokasi-nasional-kemnaker-targetkan-latih-60-ribu-peserta)
- [Pemkot Cimahi Realisasikan Program Sanimas DAK 2025](https://cimahikota.go.id/artikel/detail/1658-pemkot-cimahi-realisasikan-program-sanimas-dak-tahun-2025)
- [Penyediaan Sanitasi & Air Minum via Pamsimas dan Sanimas — Dinas PUTR Buleleng](https://putr.bulelengkab.go.id/informasi/detail/artikel/penyediaan-sanitasi-dan-air-minum-sehat-melalui-pamsimas-dan-sanimas-libatkan-masyarakat-64)
- [5 Pilar STBM — Dinkes Sumut](https://dinkes.sumutprov.go.id/artikel/5-pilar-stbm)
- [Pendamping PKH Perlu Sukseskan Program lewat Sekolah Rakyat–DTSEN — Antara](https://www.antaranews.com/berita/4898845/pendamping-pkh-perlu-sukseskan-program-lewat-sekolah-rakyat-dtsen)
- [Tupoksi Pendamping Sosial PKH — Blog PKH Poso](https://blogpkhposo.wordpress.com/sdm-pkh/tupoksi-pendamping-sosial/)
- [Basic Income and Conditional Cash Transfers in Indonesia — BIEN](https://basicincome.org/news/2025/07/basic-income-and-conditional-cash-transfers-in-indonesia/)
- [PKH Conditional Cash Transfer — World Bank (PDF)](https://documents1.worldbank.org/curated/en/845441468258848819/pdf/Program-Keluarga-Harapan-PKH-conditional-cash-transfer.pdf)
- [Improving Targeting of a Conditional Cash Transfer Program in Indonesia — J-PAL](https://www.povertyactionlab.org/evaluation/improving-targeting-conditional-cash-transfer-program-indonesia)

---

*Dokumen ini disusun dari riset web sekunder pada 25 Agustus 2026. Semua angka bertanda 🟡/🟠 wajib diverifikasi ke sumber primer sebelum masuk lingkungan produksi. Angka bertanda 🔴 sengaja dikosongkan — jangan diisi dengan estimasi.*
