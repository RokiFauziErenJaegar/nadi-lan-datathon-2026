# NADI — Navigasi AI Data Intervensi

**Sistem pendukung keputusan untuk deteksi dini kerentanan kemiskinan dan orkestrasi intervensi lintas perangkat daerah.**
Kabupaten Pringsewu, Provinsi Lampung · LAN Datathon 2026

---

## Menjalankan

Klik dua kali **`JALANKAN-NADI.bat`**.

Skrip memeriksa setiap prasyarat lalu hanya mengerjakan yang belum ada. Penyiapan pertama memakan waktu sekitar dua belas menit — membangun basis data, melatih model, menilai empat puluh ribu keluarga. Menjalankannya untuk kedua kali membuka aplikasi dalam hitungan detik.

Aplikasi terbuka di **http://127.0.0.1:8000**

### Akun untuk mencoba

| Pengguna | Sandi | Peran | Cakupan |
|---|---|---|---|
| `dinsos` | `NadiDinsos#2026` | Dinas Sosial | Seluruh kabupaten, dapat membuka data keluarga |
| `bupati` | `NadiPimpinan#2026` | Pimpinan Daerah | **Agregat saja** |
| `bappeda` | `NadiPerencana#2026` | Bappeda | **Agregat saja** |
| `pupr` | `NadiPupr#2026` | Dinas PUPR | Wilayah penugasan |
| `verifikator` | `NadiVerif#2026` | Petugas lapangan | **Hanya Kec. Pagelaran Utara** |

> Masuklah sebagai Pimpinan Daerah lalu coba buka data satu keluarga — sistem akan menolaknya. Pembatasan akses yang hanya dijelaskan selalu terdengar meyakinkan; yang dapat dicoba sendiri jauh lebih sulit dibantah.

---

## Yang perlu diketahui sebelum menilai

**Seluruh data pada sistem ini sintetis.** Empat puluh ribu keluarga, seratus tiga puluh tiga ribu jiwa, dan dua ratus empat puluh ribu potret kondisi — tidak satu pun merujuk keluarga nyata. Yang ditiru adalah bentuk statistiknya, dikalibrasi terhadap publikasi BPS Kabupaten Pringsewu.

**Keluaran sistem adalah antrean pemeriksaan, bukan keputusan.** Tidak ada jalur pada aplikasi ini yang menghentikan, mengurangi, atau menunda bantuan siapa pun.

**Sistem tidak menyimpan identitas.** Tidak ada nama, nomor induk kependudukan, maupun alamat di dalam basis data. Yang beredar hanyalah kode semu yang tidak dapat dibalik tanpa kunci rahasia. Koordinat pun digeser acak dalam radius 250 meter sebelum disimpan.

---

## Apa yang membedakan NADI

Kami tidak mengklaim NADI adalah sistem data kemiskinan pertama di Indonesia. Riset yang menyertai pembangunan ini memetakan **tiga belas sistem Indonesia dan sebelas sistem internasional** — DTSEN, SIKS-NG, SEPAKAT, SIMNANGKIS, SIPINTER, Carik Jakarta, sampai SISBEN Kolombia dan Cadastro Único Brasil.

Yang ditemukan: semuanya berhenti sebelum satu langkah yang sama.

| Sistem | Prediksi risiko **ke depan** | Penjelasan **per keluarga** | Penugasan ke **OPD spesifik** | Simulasi **what-if** | Pemantauan **outcome keluarga** |
|---|:--:|:--:|:--:|:--:|:--:|
| DTSEN / SIKS-NG | ❌ | ❌ | ❌ | ❌ | ❌ |
| SEPAKAT (Bappenas) | ❌ | ❌ | 🟡 level wilayah | 🟡 alokasi anggaran | ✅ agregat |
| SIMNANGKIS / SIPINTER | ❌ | ❌ | ✅ | ❌ | 🟡 output |
| SIGA-KRS / e-PKH | 🟡 aturan | ✅ aturan | ❌ | ❌ | ✅ terbatas |
| **NADI** | ✅ | ✅ | ✅ | ✅ | ✅ |

*Penilaian berdasarkan bukti publik per Agustus 2026. Tanda ❌ berarti tidak ditemukan bukti publik, bukan bukti ketiadaan. Sistem yang dibandingkan memiliki mandat berbeda-beda.*

**Rumusan yang tepat:** DTSEN memberi tahu siapa yang miskin **hari ini**. Yang belum ada adalah siapa yang **akan** jatuh dalam enam sampai dua belas bulan ke depan, karena tekanan apa, dan siapa yang harus bertindak.

---

## Delapan modul

| Modul | Isi |
|---|---|
| **Executive Command Center** | Angka pokok kabupaten, tren enam gelombang, sebaran risiko, peringkat kecamatan |
| **GeoAI Poverty Radar** | Peta 131 pekon dengan batas asli Badan Informasi Geospasial; empat ukuran yang dapat dipetakan |
| **Household Digital Twin** | Lintasan keluarga sepanjang tiga tahun, guncangan, riwayat program, kontribusi tiap faktor |
| **Mismatch & Anomaly Queue** | Antrean kasus berprioritas, masing-masing membawa bukti yang dapat diperiksa |
| **Intervention Recommender** | Usulan program beserta OPD, tindakan, perkiraan manfaat, dan apa yang masih kurang |
| **What-if Policy Simulator** | Aritmetika penuntasan RTLH, kapasitas verifikasi, cakupan dan biaya program |
| **AI Policy Copilot** | Tanya jawab berbasis pengetahuan sistem, dengan sumber yang ditampilkan |
| **Outcome Monitoring** | Capaian intervensi selalu berdampingan dengan kelompok pembanding yang dicocokkan |
| **Transparansi Model** | Metrik, pemeriksaan keadilan, dan daftar hal yang **tidak** dapat dilakukan sistem |

---

## Kinerja model

Diuji pada gelombang yang tidak pernah dilihat model saat pelatihan.

| Model | Fitur | AUC | Brier | Presisi@300 | Dibanding acak |
|---|---|---|---|---|---|
| Indeks dasar (aturan) | 19 | 0,792 | 0,0818 | 57,0% | 5,4× |
| DTSEN saja | 39 | 0,856 | 0,0716 | 76,7% | 7,3× |
| **NADI (DTSEN + lintas OPD)** | **43** | **0,858** | **0,0714** | **77,0%** | **7,4×** |
| + survei konsumsi *(batas atas)* | 48 | 0,943 | 0,0504 | 99,0% | 9,4× |

Target proposal AUC ≥ 0,75 terlampaui. Angka ini berada tepat pada pita yang dilaporkan kajian lintas negara untuk penargetan kemiskinan (0,72–0,85) — **bukan di atasnya**. Sistem ini memperlakukan AUC di atas 0,90 sebagai tanda kebocoran data, bukan sebagai prestasi, dan memperingatkannya secara otomatis.

### Target "Recall ≥ 80%" dan anggarannya

| Recall | Keluarga diperiksa | % populasi | Presisi |
|---|---|---|---|
| 50% | 4.493 | 11,2% | 46,7% |
| 70% | 8.336 | 20,8% | 35,2% |
| **80%** | **11.956** | **29,9%** | **28,1%** |
| Tanpa model | 32.000 | 80,0% | 10,5% |

Model memangkas beban verifikasi dari 80% populasi menjadi 30% untuk recall yang sama — **2,7× lebih hemat**.

### Pemeriksaan keadilan

| Ukuran | Hasil |
|---|---|
| Selisih AUC antar-kecamatan | 0,025 (0,846–0,871) |
| Selisih recall menurut jenis kelamin kepala keluarga | 0,9 poin persen |
| Selisih recall menurut desa/kota | 2,5 poin persen |
| AUC pada keluarga yang belum pernah dilihat | 0,838 |

---

## Keputusan rancangan yang menentukan

**Pengeluaran terukur dikeluarkan dari model.** DTSEN tidak memuatnya — justru karena mengukur konsumsi itu mahal, pemerintah memakai proksi. Memberi model angka konsumsi berarti memberinya jawaban yang seharusnya ia tebak. Menyertakannya menaikkan AUC dari 0,858 menjadi 0,943, dan membuat sistem mustahil dijalankan.

**Kepesertaan program juga dikeluarkan.** Fitur ini mencerminkan *keputusan* penargetan pemerintah, bukan *keadaan* keluarga. Pengukuran menunjukkan penanda "tidak menerima bantuan apa pun" berkorelasi **negatif** dengan kemiskinan periode berikutnya — model yang memakainya akan menempatkan keluarga yang belum tersentuh lebih rendah pada antrean, padahal merekalah yang harus ditemukan. Biaya mengeluarkannya: AUC 0,859 → 0,858.

**Desil dibangkitkan sebagai keluaran proxy means test, bukan dari pengeluaran langsung.** Rancangan awal mengelompokkan pengeluaran sebenarnya; akibatnya satu fitur menguasai 86% keputusan model dan seluruh evaluasi kehilangan makna. Kajian lintas negara mencatat daya jelas proxy means test hanya 0,40–0,60, dan generator ini dikalibrasi ke sana.

**Aset disimpan sebagai jumlah, bukan ya/tidak.** DTSEN 2025 mencatat jumlah unit dan kuantitas kontinu — gram emas, hektar lahan. Skema lama DTKS memakai boolean. Menyalin pola lama akan memutus pemadanan saat pipeline diarahkan ke data sesungguhnya.

**Rumah layak huni menuntut empat kriteria.** Rumah bertembok berlantai keramik tetap **tidak** layak huni bila keluarganya buang air besar sembarangan. Menyederhanakannya akan melaporkan angka RTLH lebih rendah dari kenyataan — dan angka itulah yang dipakai menyusun anggaran bedah rumah.

---

## Privasi dan tata kelola

| Perlindungan | Wujud teknis |
|---|---|
| Data pribadi tidak keluar ke layanan AI | `nadi/security/pii.py` — 32 uji, penghalang berjalan sebelum setiap permintaan HTTP |
| Identitas dipseudonimkan | HMAC-SHA256, stabil, tidak dapat dibalik tanpa kunci rahasia |
| Akses berbasis peran | Enam peran, dua lapis: kewenangan tindakan dan cakupan data |
| Sel kecil disembunyikan | Wilayah dengan kurang dari sepuluh keluarga tidak menampilkan angka |
| Jejak audit | Setiap pembukaan data keluarga tercatat beserta pelakunya |
| Koordinat digeser | Radius 250 meter sebelum disimpan |

Rancangan ini menempatkan tiga alasan pelarangan sistem **SyRI** di Belanda sebagai daftar periksa terbalik: tidak buram, data diminimalkan, dan tujuannya khusus — hanya untuk memperluas jangkauan layanan, tidak pernah untuk memutus bantuan maupun mendeteksi kecurangan.

---

## Susunan proyek

```
NADI - LAN DATATHON/
├─ JALANKAN-NADI.bat          Peluncur satu-klik
├─ backend/
│  ├─ nadi/
│  │  ├─ security/            PII guard, pseudonimisasi, RBAC, autentikasi
│  │  ├─ db/                  25 tabel, penamaan mengikuti istilah DTSEN
│  │  ├─ synth/               Generator data sintetis terkalibrasi
│  │  ├─ ml/                  Fitur, aturan, indeks dasar, LightGBM, TreeSHAP, evaluasi
│  │  ├─ services/            Penilaian, deteksi anomali, rekomendasi, simulator
│  │  ├─ ai/                  Penyedia LLM agnostik + Policy Copilot
│  │  └─ api/                 45 titik akhir
│  └─ scripts/                siapkan_data · latih_model · deteksi_kasus
├─ frontend/                  React + Vite + Tailwind + Leaflet + Recharts
├─ data/
│  ├─ seed/                   Katalog program, faktor risiko, OPD, wilayah
│  └─ geo/                    Batas 131 desa dari Badan Informasi Geospasial
└─ docs/
   ├─ 00-design-brief.md      Design brief 11.700 kata
   └─ research/               Lima dokumen riset, 435 KB
```

## Perintah manual

```bash
# Penyiapan
.venv\Scripts\python.exe backend\scripts\siapkan_data.py
.venv\Scripts\python.exe backend\scripts\latih_model.py
.venv\Scripts\python.exe backend\scripts\deteksi_kasus.py

# Menjalankan
cd backend && ..\.venv\Scripts\python.exe -m uvicorn nadi.main:app --port 8000

# Pengujian
cd backend && ..\.venv\Scripts\python.exe -m pytest
```

## Mengaktifkan layanan AI

Policy Copilot berjalan dalam mode luring tanpa konfigurasi apa pun — seluruh angka, skor, rekomendasi, dan simulasi tetap tersedia karena semuanya dihitung secara lokal. Yang berbeda hanya keluwesan kalimat jawabannya.

### Dari dalam aplikasi

Masuk sebagai `admin`, buka **Pengaturan AI** pada menu. Halaman itu menyediakan tujuh penyedia siap pakai, mengambil sendiri daftar model yang tersedia bagi kunci Anda, dan menguji sambungan sebelum menyimpan. Perubahan berlaku seketika — peladen tidak perlu dijalankan ulang.

Tiga hal yang ditegakkan halaman tersebut:

- **Kunci API tidak pernah dapat dibaca kembali**, bahkan oleh administrator yang memasukkannya. Yang ditampilkan hanya bentuk tersamar (`sk-pro...aKEA`). Kunci disimpan pada `.env` di server, tidak di dalam basis data — berkas basis data memang dimaksudkan untuk disalin, dan rahasia tidak boleh ikut tersalin bersamanya.
- **Hanya delapan variabel yang boleh disunting** lewat antarmuka, ditegakkan dengan daftar putih. Permintaan yang menyentuh `NADI_SECRET_KEY` atau `NADI_DATABASE_URL` ditolak, apa pun bentuk badannya.
- **Penghalang PII berlaku bagi penyedia mana pun.** Mengganti penyedia tidak melonggarkan pemeriksaan itu satu pun.

Salah satu pilihan pada katalog adalah **model lokal** (Ollama / LM Studio). Ketika NADI kelak dijalankan di atas data keluarga yang sesungguhnya, pilihan itu menjawab pertanyaan kedaulatan data secara mutlak: tidak ada satu kata pun yang keluar dari jaringan pemerintah daerah.

### Perbedaan dialek antarpenyedia

"Kompatibel dengan OpenAI" ternyata bukan satu bahasa. Keluarga `gpt-5` dan `o-series` menolak `max_tokens` (menuntut `max_completion_tokens`) **dan** menolak `temperature` selain 1. NADI menanganinya dengan dua lapis: tebakan dari nama model untuk kasus yang sudah dikenal, dan koreksi otomatis dari pesan galat untuk model yang belum ada ketika kode ini ditulis. Diuji langsung terhadap `gpt-4o-mini`, `gpt-4.1-mini`, `gpt-5-mini`, `gpt-5`, dan `o4-mini` — kelimanya berjalan.

### Dari baris perintah

Untuk mengaktifkan mode daring, cukup satu perintah dengan kunci API Anda:

```
python backend/scripts/siapkan_ai.py --kunci <kunci-anda>
```

Skrip itu menguji penghalang privasi, mengambil sendiri daftar model yang tersedia bagi kunci tersebut, mengirim satu permintaan sungguhan untuk membuktikan model itu benar-benar dapat dipakai, lalu menulis hasilnya ke `.env`. Nama model tidak perlu ditebak.

Perintah lain yang tersedia:

```
python backend/scripts/siapkan_ai.py --daftar          # lihat model yang tersedia
python backend/scripts/siapkan_ai.py --model NAMA      # pilih model tertentu
python backend/scripts/siapkan_ai.py --tanpa-simpan    # uji tanpa menyunting .env
```

### Membaca galat HTTP 401

OpenCode Zen menjawab **401 untuk tiga keadaan yang sama sekali berbeda**, sehingga nomor statusnya sendiri tidak mendiagnosis apa pun. Yang menentukan adalah `error.type` pada badan tanggapan:

| `error.type` | Artinya | Tindakan |
|---|---|---|
| `AuthError` | Kunci ditolak | Ganti kunci |
| `CreditsError` | **Kunci sah**, akun belum punya metode pembayaran | Pasang pembayaran, atau pakai model gratis |
| `ModelError` | Nama model salah — kunci belum sempat diperiksa | Perbaiki `NADI_LLM_MODEL` |

Skrip penyiapan sudah membedakan ketiganya dan menyebutkan tindakan yang tepat. Model bertanda `-free` tidak terkena `CreditsError`, sehingga sistem tetap dapat dijalankan penuh tanpa metode pembayaran — hanya lebih lambat.

Bila menguji dengan `curl` di PowerShell, tulis muatan JSON ke berkas lebih dahulu dan panggil `curl.exe -d "@berkas"`. Bentuk sebaris akan dirusak PowerShell, menghasilkan `ModelError` berkode 401 yang mudah disalahartikan sebagai kunci ditolak.

Bila diisi manual, kuncinya adalah `NADI_LLM_BASE_URL`, `NADI_LLM_API_KEY`, dan `NADI_LLM_MODEL`. Lapisan penyedia bersifat agnostik: endpoint bergaya OpenAI mana pun dapat dipakai tanpa mengubah kode.

---

## Monitoring hasil, dan mengapa angkanya disajikan berpasangan

Modul kedelapan menutup lingkar: kasus terdeteksi, petugas memverifikasi, OPD mencatat penyaluran, lalu Dinas Sosial menilai hasilnya terhadap kondisi keluarga pada gelombang berikutnya.

Tiga hal menentukan bentuknya.

**Penilaian dihitung, bukan diketik.** Nilai membaik, tetap, atau memburuk diturunkan peladen dari selisih skor kerentanan antardua gelombang. Tidak ada bidang pada permintaan yang dapat menentukannya. Petugas hanya menekan tombol dan menulis catatan.

**Yang menyalurkan tidak menilai.** `CATAT_INTERVENSI` dipegang OPD pelaksana; `CATAT_OUTCOME` dipegang Dinas Sosial. Diuji lewat HTTP: akun `pupr` mendapat 403 ketika mencoba menilai intervensi yang ia catat sendiri.

**Capaian tidak pernah berdiri sendiri.** Ini yang paling menentukan. Pada data sistem, 68,1 persen keluarga membaik setelah menerima intervensi — angka yang terdengar meyakinkan sampai orang melihat pembandingnya:

| | Membaik | Tetap | Memburuk |
|---|---|---|---|
| Menerima intervensi | 68,1% | 20,8% | 11,1% |
| **Pembanding — tidak menerima apa pun** | **45,5%** | 37,4% | 17,1% |
| Selisih | **+22,6 pp** | −16,6 pp | −6,0 pp |

Kelompok pembanding adalah keluarga yang tidak menerima intervensi, dicocokkan pada gelombang yang sama dan pita skor awal selebar 10 poin. Pencocokan itu perlu karena keluarga berskor tinggi cenderung turun dengan sendirinya pada pengukuran berikutnya — regresi ke rata-rata, bukan keberhasilan program. Sebanyak 466 dari 467 intervensi berhasil dicocokkan.

Ambang perubahan bermakna ±5 poin bukan angka pilihan: simpangan baku perubahan skor antargelombang pada 200.000 pengamatan adalah 7,0 poin, sehingga 5 poin berarti kira-kira 0,7 simpangan baku.

Riwayat demo dibangkitkan `backend/scripts/seed_intervensi.py`. Skrip itu hanya mencatat intervensi bagi keluarga yang **memang** mulai menerima program menurut panel sintetis, lalu menghitung hasilnya dari skor yang sudah ada. Tidak ada keluarga yang dipilih karena membaik.

---

## Uji asap antarmuka

```
cd frontend && npm run uji
```

Perintah ini memasang **kesebelas halaman** ke dalam peramban tiruan, memanggil API peladen yang sedang berjalan, menunggu setiap kueri reda, lalu memeriksa apakah halamannya benar-benar berisi.

Perkakas ini lahir dari satu kekeliruan yang lolos dari seluruh pemeriksaan lain. Halaman Pengaturan memanggil tiga `useMutation` di bawah cabang `if (isLoading) return`: render pertama memanggil nol hook mutasi, render kedua memanggil tiga, dan React membatalkan seluruh pohon komponen. Yang terlihat hanyalah halaman kosong — tanpa pesan galat apa pun.

`tsc --noEmit` meloloskannya karena ini kekeliruan waktu jalan. `vite build` meloloskannya karena membangun berkas bukan menjalankannya. Hanya memasang halaman itu sungguhan dan menunggu render kedua yang dapat menangkapnya — dan begitu bug tersebut dikembalikan sebagai percobaan, uji ini langsung melaporkan `Rendered more hooks than during the previous render.`

Dua keputusan yang membuatnya berguna:

- **Memakai peladen sungguhan, bukan tanggapan tiruan.** Tiruan hanya menguji apa yang sudah terbayangkan; memanggil API yang sesungguhnya sekaligus memeriksa bahwa bentuk tanggapan cocok dengan yang dibaca komponen.
- **Penanda diambil dari isi halaman, bukan judulnya.** Judul berada di komponen tata letak yang sengaja tidak ikut dipasang, supaya yang diuji benar-benar halamannya.

---

## Panduan lengkap

`dokumen/Panduan-NADI.docx` dan `dokumen/Panduan-NADI.pdf` — 34 halaman, sepuluh bab: ringkasan eksekutif, inventaris yang dibangun, kronologi pembangunan beserta dua belas kekeliruan yang ditemukan dan diperbaiki, metodologi data dan model, tata kelola, kejujuran statistik pada monitoring, kamus 65 istilah untuk pembaca awam, bahan penjelasan kepada dewan juri lengkap dengan sepuluh pertanyaan tersulit, analisis celah berprioritas, dan lampiran teknis.

Seluruh angka di dalamnya dibaca langsung dari basis data dan berkas proyek saat dokumen disusun. Bila sistem berubah, jalankan ulang:

```
python backend/scripts/buat_panduan.py
```

PDF dihasilkan lewat Microsoft Word agar tata letaknya identik dengan berkas Word-nya. Tambahkan `--tanpa-pdf` bila Word tidak tersedia.

---

## Pengujian

Empat lapis, 112 pemeriksaan seluruhnya:

```
python -m pytest backend/tests -q              # 61 kasus uji — < 1 detik
cd frontend && npm run uji                     # 11 halaman antarmuka — ± 1 menit
python backend/scripts/uji_penerimaan.py       # 40 pemeriksaan janji sistem — ± 1 menit
```

Perintah ketiga adalah yang paling layak diperlihatkan kepada pemeriksa. Ia memeriksa **janji**, bukan fungsi: bahwa pimpinan daerah benar-benar tidak dapat membuka satu keluarga pun, bahwa OPD pelaksana benar-benar tidak dapat menilai pekerjaannya sendiri, bahwa NIK benar-benar tertahan sebelum keluar jaringan. Seluruhnya lewat HTTP kepada peladen yang sedang berjalan — sebuah rute yang lupa dipasangi penjaga akan tetap lulus pada uji fungsi, dan hanya ketukan HTTP yang menemukannya.

Setiap pemeriksaan mencetak nilai yang benar-benar diterima, bukan sekadar kata "lulus". Tambahkan `--bagian B` untuk satu bagian saja, dan `--bersihkan` sesudahnya karena pengujian ini membuat satu verifikasi, satu intervensi, dan satu penilaian hasil.

Panduan lengkapnya — termasuk uji manual per modul, uji ketahanan, lembar periksa sebelum demo, dan pemecahan masalah — ada pada `dokumen/Panduan-Pengujian-NADI.pdf` (19 halaman).

---

## Sumber data dan acuan

- BPS Kabupaten Pringsewu — *Potret Kemiskinan 2025*, *Pringsewu Dalam Angka 2025*
- Peraturan BPS Nomor 6 Tahun 2025 tentang DTSEN; Instruksi Presiden Nomor 4 Tahun 2025
- Kepmendagri Nomor 300.2.2-2138/2025 — daftar dan kode wilayah
- Badan Informasi Geospasial — layer batas desa 1:10.000
- Kementerian Desa PDTT — Indeks Desa Membangun 2024
- Undang-Undang Nomor 27 Tahun 2022 tentang Pelindungan Data Pribadi

Rincian setiap angka beserta tingkat keyakinannya tercantum pada `docs/research/`.
