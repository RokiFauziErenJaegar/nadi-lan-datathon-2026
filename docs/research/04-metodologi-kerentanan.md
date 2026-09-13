# 04 — Metodologi Pengukuran Kerentanan Kemiskinan & Penargetan Bansos Berbasis Machine Learning

> **Tujuan dokumen:** menjadi dasar ilmiah dan spesifikasi teknis untuk **NADI Vulnerability Score** — definisi label, pemilihan fitur, metrik evaluasi, kalibrasi probabilitas, explainability, fairness, deteksi anomali, dan pembuatan data sintetis yang realistis untuk demo.
> **Tanggal riset:** 25 Agustus 2026
> **Metode:** ~30 pencarian web (Bahasa Indonesia & Inggris) + ekstraksi teks penuh dari PDF sumber primer (NBER, arXiv, ILO, Cambridge *Data & Policy*, jurnal STIS).
> **Konteks aplikasi:** Kabupaten Pringsewu, Provinsi Lampung. Basis data sasaran: **DTSEN** (lihat `01-skema-data-dtsen.md`), katalog program: `02-katalog-program-intervensi.md`.

---

## 0. CARA MEMBACA DOKUMEN INI

### 0.1 Legenda keyakinan

| Tanda | Arti |
|---|---|
| 🟢 **PRIMER** | Angka/pernyataan diekstrak langsung dari teks penuh paper/dokumen (PDF berhasil di-parse). Boleh dikutip apa adanya. |
| 🟡 **SEKUNDER** | Dari abstrak, ringkasan mesin pencari, atau situs pihak ketiga kredibel. Verifikasi sebelum masuk slide/publikasi. |
| 🟠 **KONFLIK** | Sumber-sumber tidak sepakat. Ditandai eksplisit; jangan pilih satu angka tanpa catatan. |
| 🔴 **TIDAK DITEMUKAN** | Gagal dikonfirmasi dalam riset ini. **Jangan mengarang.** |

### 0.2 Tiga temuan paling penting untuk tim build

1. **PMT — termasuk PMT DTSEN — secara desain hanya menjelaskan ±50% variasi kesejahteraan.** R² PMT di negara berkembang tipikal **0,40–0,60** (Kidd & Wylde 2017; Brown, Ravallion & van de Walle 2016 rata-rata R²=0,53). Konsekuensinya *exclusion error* struktural: di Indonesia, uji coba Bank Dunia mengeksklusi **51%** dari target 30% termiskin. **NADI tidak boleh mengklaim akurasi yang mustahil.** Target AUC realistis: **0,72–0,85**, bukan 0,95+.
2. **Metrik yang benar untuk NADI bukan accuracy, melainkan recall@k pada anggaran verifikasi yang nyata.** Kelas positif langka, kapasitas verifikasi lapangan terbatas, dan biaya *exclusion error* jauh lebih besar daripada *inclusion error* dari sudut kesejahteraan sosial (Dietrich, Malerba & Gassmann 2024).
3. **Kerentanan ≠ kemiskinan.** Definisi operasional paling mapan: (a) **VEP/Chaudhuri** — probabilitas konsumsi jatuh di bawah garis kemiskinan periode depan, ambang **0,5**; dan (b) **garis kerentanan Bank Dunia** — 1,0–1,5 × garis kemiskinan. Keduanya harus tampil di UI karena menjawab pertanyaan berbeda ("seberapa besar risikonya?" vs "di pita mana dia sekarang?").

---

# BAGIAN I — PROXY MEANS TEST (PMT)

## 1. Cara Kerja PMT

### 1.1 Mekanika dasar

PMT adalah metode pemeringkatan kesejahteraan ketika pendapatan/konsumsi sulit diobservasi dan diverifikasi. Alurnya dua tahap:

| Tahap | Isi |
|---|---|
| **1. Kalibrasi** | Regresi `ln(konsumsi per kapita)` terhadap karakteristik yang mudah diverifikasi (aset, kondisi rumah, demografi, pendidikan/pekerjaan kepala RT) menggunakan **survei rumah tangga** (Indonesia: SUSENAS). Menghasilkan bobot β. |
| **2. Prediksi** | Bobot β diterapkan ke data sensus/registrasi (Indonesia: Regsosek/DTSEN) → **skor PMT** = prediksi konsumsi per kapita. Rumah tangga diurutkan; N% termiskin dinyatakan eligible. |

> 🟢 "PMT typically consists of two stages: (1) an estimation stage that calibrates a statistical model and (2) a prediction stage that calculates the scores that determine program inclusion." — Follett & Henderson (2022), arXiv:2201.01356, hlm. 5.

**Variabel yang lazim dipakai** (Brown, Ravallion & van de Walle 2016, "Basic PMT") 🟢: jenis toilet; material lantai, dinding, atap; bahan bakar memasak; karakteristik kepala RT (gender, pendidikan, pekerjaan); agama; ukuran & komposisi demografi; dummy kategori ukuran RT, usia kepala RT, bulan survei, dan region.

**Dua eksklusi penting yang jarang disadari** (Brown et al. 2016) 🟢:
- **Harga hampir tidak pernah dipakai** dan aset dicatat dalam kategori kasar — "dua rumah tangga sama-sama punya 'kulkas', tetapi satu berumur 30 tahun dan nyaris rusak, satu lagi model baru."
- **Efek geografis halus (level desa) tidak bisa dipakai**, karena kalibrasi dilakukan pada survei sampel yang hanya mencakup sebagian desa. Efek geografis untuk seluruh populasi tidak diketahui. → **Ini celah terbesar yang bisa diisi NADI di level kabupaten** (lihat §8.8 & §17).

### 1.2 Penerapan di Indonesia: BDT → DTKS → DTSEN

| Era | Sistem | Catatan |
|---|---|---|
| 2005–2011 | PSE05 / PPLS08 | BLT 2005 & 2008 |
| 2011–2015 | **Basis Data Terpadu (BDT)**, dikelola TNP2K | Survei PPLS 2011; PMT untuk peringkat 40% terbawah |
| 2015–2024 | **DTKS** (Kemensos) | Pemutakhiran PBDT 2015 |
| 2025– | **DTSEN** (BPS, Inpres 4/2025) | Integrasi Regsosek + DTKS + P3KE + Dukcapil; **desil 1–10 nasional** |

**Metode DTSEN (penjelasan resmi BPS, Agustus 2026)** 🟡:

> "Berbagai informasi tersebut dipertimbangkan secara bersama-sama menggunakan metode statistik **Proxy Means Test (PMT)** untuk mengestimasi tingkat kesejahteraan keluarga berdasarkan karakteristik yang dapat diamati."

Dimensi variabel pemeringkatan DTSEN yang disebut BPS 🟡: **kondisi perumahan, sumber air minum, bahan bakar & energi untuk memasak, kepemilikan aset, daya & konsumsi listrik, komposisi keluarga, pendidikan, pekerjaan, kesehatan, serta disabilitas.**

**Pernyataan BPS yang wajib jadi copy UI NADI** 🟡:

> "Desil dalam DTSEN merupakan **pemeringkatan relatif** tingkat kesejahteraan keluarga, **bukan ukuran absolut kemiskinan, pendapatan, atau kekayaan**."

→ **Implikasi UI:** NADI tidak boleh menampilkan "Desil 3 = miskin". Yang benar: "Desil 3 = 30% terbawah secara relatif di antara keluarga terdata secara nasional."

**Regsosek 2022 sebagai sumber variabel** 🟡: 464.975 petugas lapangan; kuesioner **90 variabel** (sosial-ekonomi, demografi, pendidikan, ketenagakerjaan, kepemilikan usaha, kesehatan, program perlindungan sosial, perumahan, sanitasi air bersih, kondisi kerentanan kelompok khusus, tingkat kesejahteraan, pemberdayaan ekonomi). Target **85.036.166 keluarga**. Metode door-to-door PAPI + **geotag dan foto khusus untuk keluarga miskin**.

### 1.3 Mekanisme usul-sanggah (penting untuk desain alur NADI)

Alur resmi yang ditemukan 🟡 (agregasi sumber Kemensos/Dinsos/pemberitaan):

```
Warga -> (a) aplikasi Cek Bansos, fitur "Usul/Sanggah"
      -> (b) pendamping PKH
      -> (c) kantor desa/kelurahan
            |
   Verifikasi & Validasi lapangan oleh petugas desa (dibantu RT/RW)
   - pencocokan kondisi rumah via FOTO + KOORDINAT vs data yang diajukan
            |
   MUSYAWARAH DESA/KELURAHAN (Musdes/Muskel)
   - bersama perwakilan masyarakat & perangkat desa; memutuskan kelayakan
            |
   Usulan resmi -> Pemda (Dinas Sosial) -> Pusdatin Kemensos
                -> BPS (pembaruan DTSEN, siklus triwulanan)
```

→ **Implikasi produk:** NADI paling bernilai jika memposisikan diri sebagai **alat bantu prioritisasi antrean verifikasi dan bahan Musdes**, bukan pengganti keputusan. Ini sekaligus menyelesaikan masalah legitimasi PMT (lihat §3.3–3.4).

---

## 2. Akurasi PMT: angka-angka yang bisa dikutip

### 2.1 R² (kekuatan penjelas model)

| Sumber | Konteks | R² |
|---|---|---|
| Brown, Ravallion & van de Walle (2016), NBER WP 22919 — 9 negara Afrika (LSMS) | "Basic PMT", OLS | Rata-rata **0,53**; rentang **0,32 (Ethiopia) – 0,64 (Burkina Faso)** 🟢 |
| Ibid., survei literatur (footnote 42) | Grosh & Baker (1995) 0,3–0,4; Ahmed & Bouis (2002) 0,43; Narayan & Yoshida (2005) 0,59; Sharif (2009) 0,57; Stoeffler et al. (2015) 0,62; Pop (2015) 0,54; Cnobloch et al. (2015) 0,5–0,7 | Rata-rata sederhana **0,52** 🟢 |
| Kidd & Wylde (2017), ILO ESS / DFAT | Mayoritas PMT negara berkembang | **0,40–0,60** 🟢 |

> 🟢 "…the majority of PMTs used in developing countries have R-squared values between 40 per cent and 60 per cent; in other words, around half of the variation in consumption between households remains unexplained. This means that, **by design, PMTs only weakly predict a household's level of poverty**." — Kidd & Wylde (2017).

### 2.2 Exclusion & inclusion error — tabel referensi utama

| Sumber | Setting | Cakupan target | Exclusion error | Inclusion error |
|---|---|---|---|---|
| Brown/Ravallion/van de Walle 2016 🟢 | 9 negara Afrika, garis kemiskinan tetap, H=0,2 | 20% termiskin | **81%** (rentang 55–100%) | **48%** (rentang 33–100%) |
| Ibid. 🟢 | H=0,4 | 40% termiskin | **36%** (rentang 24–56%) | **31%** (rentang 25–40%) |
| Ibid. 🟢 | tingkat kemiskinan tetap (kuota) | H=0,2 | rata-rata targeting error **51%** | simetris |
| Ibid. 🟢 | tingkat kemiskinan tetap | H=0,4 | rata-rata targeting error **32%** | simetris |
| Kidd & Wylde 2017 🟢 | desain PMT umum | 10% termiskin | ±**60%** | ±60% |
| Kidd & Wylde 2017 🟢 | desain PMT umum | 20% termiskin | ±**50%** | ±50% |
| **Indonesia** — uji coba Bank Dunia (Alatas et al. 2012) via Kidd & Wylde 🟢 | | 30% termiskin | **51%** | signifikan (bocor ke 70% terkaya) |
| **Indonesia** — PKH (Alatas et al. 2016) via Kidd & Wylde 🟢 | PKH | 5% termiskin | **93% dieksklusi** | — |
| Mexico Oportunidades (Veras et al. 2007) via Kidd & Wylde 🟢 | | 20% termiskin | ±**70%** | — |
| Georgia TSA (Kidd & Gelders 2016) 🟢 | "PMT terbaik" | 15% termiskin | ±**50%** (vs konsumsi); ±**66%** (vs pendapatan) | — |
| Pakistan BISP (World Bank 2009) via Kidd & Wylde 🟢 | prediksi ex-ante | 10% termiskin | **88%** | — |
| Development Pathways 🟡 | agregat | 20% cakupan | 44–55% (gabungan) | idem |
| Development Pathways 🟡 | agregat | 10% cakupan | 57–71% (gabungan) | idem |

**Bias sistematis paling relevan untuk NADI** 🟢:

> "For the poorest 20% in terms of actual consumption, the mean residual ranges from **−0,73 to −0,37**, implying that the PMT regressions yield predicted consumptions for the poor **between 50% and 100% above their actual consumption**." — Brown et al. (2016).

Penyebabnya struktural: **garis regresi OLS melewati rata-rata data**, residual berkorelasi positif dengan variabel dependen → **PMT overestimate kesejahteraan si paling miskin** (regression to the mean). Ini bukan bug, melainkan konsekuensi matematis dari minimisasi MSE. 🟢

> **Implikasi langsung:** model NADI yang meregresikan proksi pengeluaran akan mewarisi bias yang sama. **Mitigasi yang terbukti:** (a) **quantile regression** pada kuantil = tingkat kemiskinan — Brown et al. 🟢 menemukan "a poverty-quantile method dominating in most cases"; (b) melatih **klasifikasi biner terhadap ambang**, bukan regresi konsumsi; (c) *loss* asimetris yang menghukum false negative lebih berat.

### 2.3 Error implementasi (bukan error desain) — Indonesia

| Temuan | Angka | Sumber |
|---|---|---|
| Sel kuesioner PMT Indonesia 2011 diisi tidak akurat | rata-rata **14,7%**, di satu wilayah **>37%** | SMERU (2011) via Kidd & Wylde 🟢 |
| Cakupan survei PMT Indonesia | hanya **40% rumah tangga** (Pakistan BISP: 85%) | Kidd & Wylde 🟢 |
| Biaya survei PMT Indonesia | **US$60 juta** (2011); **US$100 juta** (2015) | Kidd & Wylde 🟢 |
| Jeda antar-survei | **4 tahun** (2011 → 2015) | Kidd & Wylde 🟢 |

---

## 3. Kritik terhadap PMT (dan artinya untuk NADI)

### 3.1 Kritik teknis
1. **Design error tinggi & tak hilang** dengan menambah cakupan desil (§2.2).
2. **Asumsi statis.** PMT memotret aset; kemiskinan bersifat dinamis dan stokastik. Aset berubah lambat, konsumsi berubah cepat.
3. **Degradasi model seiring waktu.** Aiken, Ohlenburg & Blumenstock (COMPASS '23, *Moving targets*) menemukan akurasi PMT **menurun terus-menerus** menggunakan data survei nasional dari **6 negara** LMIC. 🟡 (🔴 angka penurunan per tahun tidak berhasil diekstrak — ACM DL 403, OpenReview terkunci.)
4. **Tidak konsisten lintas waktu.** Sohnesen & Stender (2017) 🟡: random forest sering lebih akurat daripada praktik umum (multiple imputation + stepwise/Lasso) *dalam tahun yang sama*, **tetapi tidak satu pun metode konsisten akurat lintas waktu** — "technical model fitting by any method within a single year is not always, by itself, sufficient for accurate predictions of poverty over time."

### 3.2 Kritik keadilan & kesejahteraan
Dietrich, Malerba & Gassmann (2024), *Data & Policy* 6:e3 — paper paling relevan untuk desain metrik NADI 🟢:

- Membangun **kerangka penilaian targeting yang diperluas** dengan **social welfare weights** (fungsi kesejahteraan Atkinson 1970, parameter *inequality aversion* ρ). Bobot: `ω_b = (y_b / y_a)^(−ρ)`, dinormalisasi terhadap **garis kemiskinan** sebagai titik acuan.
- Temuan inti: **"an increase in prediction accuracy can even result in welfare losses if poorer households are misclassified."** Akurasi naik ≠ kesejahteraan naik.
- **Label bias** (kesalahan pengukuran variabel dependen) dan **bobot PMT yang tidak stabil** menyebabkan **hingga separuh** kerugian kesejahteraan akibat targeting error — dan kerugian itu **tidak merata antar kelompok**.
- Studi kasus (Tanzania & Malawi): **rumah tangga kecil** dirugikan sistematis — lebih mungkin salah diklasifikasi sebagai non-miskin.
- Transparansi: dari **10 program cash transfer publik ber-PMT di Afrika Timur**, hanya **separuh** membagikan informasi metodologi targeting, dan hanya **satu** yang mempublikasikan bobot PMT lengkap.

### 3.3 Kritik sosial (kohesi komunitas) — Indonesia
Semua dari Kidd & Wylde (2017) 🟢:
- **Protes terjadi di ±30% desa** saat rollout BLT (Widjaja 2009).
- **Kejahatan meningkat 5,8%** akibat mistargeting PMT (Cameron & Shah 2011, IZA DP 6736).
- Distribusi awal PKH di satu komunitas memicu **pelemparan batu dan pembakaran bangunan** (Hannigan 2010).
- **Raskin lazim dibagi rata** oleh pemimpin komunitas — komunitas mensubversi mekanisme PMT (TNP2K 2013).
- **Mekanisme banding tidak bisa berfungsi**: "if people could appeal their exclusion on the basis of their poverty, the high level of exclusion error would mean that **over half of the intended beneficiaries would be eligible to appeal**."

### 3.4 Bukti eksperimental Indonesia: PMT vs Community Targeting
Alatas, Banerjee, Hanna, Olken & Tobias (2012), *AER* 102(4):1206–1240 — eksperimen di **640 desa Indonesia** 🟡:
- Tiga metode: **PMT**, **community targeting** (warga memeringkat semua orang), **hybrid**.
- Dengan definisi kemiskinan PPP$2/kapita/hari, community targeting & hybrid **sedikit lebih buruk** dari PMT — "though not by enough to significantly affect poverty outcomes for a typical program."
- **Elite capture BUKAN penjelasannya.** Komunitas memakai **konsep kemiskinan yang berbeda** (mis. *earning capacity*, bukan konsumsi).
- **Community targeting menghasilkan kepuasan warga yang lebih tinggi.**

> **Temuan kunci untuk NADI.** Model statistik dan warga bukan "satu benar satu salah" — keduanya mengukur konstruk berbeda. Desain yang benar: **model memberi urutan awal, Musdes memberi keputusan akhir**, dan **ketidaksepakatan antara keduanya adalah sinyal, bukan gangguan** (kandidat kuat untuk fitur "flag selisih skor model vs peringkat Musdes").

**Pendekatan hybrid canggih (referensi desain)** 🟢: Follett & Henderson (2022) mengusulkan kerangka Bayesian di mana bobot PMT **dikalibrasi ke peringkat preferensi komunitas**, bukan ke konsumsi. Fitur turunan: agregasi multi-ranker, **penyesuaian eksplisit untuk elite capture**, dan **prosedur dynamic updating**. Diilustrasikan dengan data Burkina Faso dan **Indonesia (data Alatas et al. 2012)**.

---

# BAGIAN II — KERANGKA KONSEPTUAL KERENTANAN KEMISKINAN

## 4. Tiga Aliran Besar Pengukuran Kerentanan

| Pendekatan | Singkatan | Definisi | Perintis |
|---|---|---|---|
| Vulnerability as **Expected Poverty** | **VEP** | Probabilitas ex-ante bahwa konsumsi masa depan jatuh di bawah garis kemiskinan | **Chaudhuri, Jalan & Suryahadi (2002)** |
| Vulnerability as **Low Expected Utility** | **VEU** | Selisih antara utilitas dari konsumsi ekuivalen-pasti pada garis kemiskinan dengan ekspektasi utilitas konsumsi aktual | **Ligon & Schechter (2003)** |
| Vulnerability as **Uninsured Exposure to Risk** | **VER** | Sejauh mana guncangan menyebabkan penurunan konsumsi (ex-post) | **Dercon & Krishnan (2000)** |

> 🟡 "There are three main methods for measuring vulnerability: vulnerability as exposure to risk (VER), vulnerability as expected poverty (VEP), and vulnerability as low expected utility (VEU)." — ADBI Working Paper 611, *Concepts and Measurement of Vulnerability to Poverty*.

**Untuk NADI, VEP adalah pilihan yang benar** karena: (a) hanya butuh data **cross-sectional** — DTSEN adalah cross-section berulang, bukan panel individu panjang; (b) outputnya **probabilitas**, langsung bisa dikalibrasi dan di-ranking; (c) sudah diaplikasikan ke Indonesia sejak awal.

> 🟡 "The Vulnerability as Expected Poverty (VEP) approach was proposed as the best option whenever a **single visit household survey** is used."

## 5. Metode Chaudhuri, Jalan & Suryahadi (VEP) — detail operasional

**Referensi:** Chaudhuri, S., Jalan, J. & Suryahadi, A. (2002). *Assessing Household Vulnerability to Poverty from Cross-Sectional Data: A Methodology and Estimates from Indonesia.* Columbia University Discussion Paper No. 0102-52.

### 5.1 Definisi

```
V_ht = Pr( c_h,t+1 < z )
```
- `V_ht` = tingkat kerentanan rumah tangga h pada waktu t
- `c_h,t+1` = pengeluaran per kapita rumah tangga h pada t+1
- `z` = garis kemiskinan pada waktu t

Konsumsi ditentukan oleh: karakteristik teramati (X_h), keadaan ekonomi agregat pada waktu t (β_t), pengaruh time-invariant tak-teramati (α_h), dan faktor idiosinkratik/guncangan (e_h):
```
c_ht = c(X_h, β_t, α_h, e_ht)
```
🟢 Formulasi dari Rahman & Wulansari, *Jurnal ASKS* Politeknik Statistika STIS, hlm. 57, yang mereproduksi Chaudhuri et al.

### 5.2 Prosedur FGLS tiga tahap 🟢

Dengan data cross-sectional, diasumsikan:
```
(3)  ln c_h    = X_h β + e_h
(4)  σ²_e,h    = X_h θ            (heteroskedastisitas: varians juga fungsi karakteristik)
```

| Tahap | Operasi |
|---|---|
| **1** | Estimasi Persamaan (3) dengan **OLS**. Ambil residual, kuadratkan, lalu regresikan `ê²_h = X_h θ + η_h` (Persamaan 5) untuk memodelkan varians. |
| **2** | Gunakan hasil (5) untuk **mentransformasi persamaan (5) itu sendiri**: `ê²_h / X_hθ̂ = (X_h / X_hθ̂)θ + η_h / X_hθ̂` → penduga θ yang **asimtotik efisien**. |
| **3** | Transformasi persamaan (3) dengan membagi tiap observasi dengan `√(X_hθ̂)`: `ln c_h/√(X_hθ̂) = (X_h/√(X_hθ̂))β + e_h/√(X_hθ̂)` → penduga β **konsisten dan asimtotik efisien**. |

**Estimasi kerentanan** (asumsi ln c berdistribusi normal):
```
V̂_h = Pr(ln c_h < ln z | X_h) = Φ[ ( ln z − X_h β̂ ) / √( X_h θ̂ ) ]
```
di mana Φ = CDF normal standar.

**Dekomposisi yang sangat berguna untuk UI NADI:** pembilang `ln z − X_hβ̂` adalah komponen **"rata-rata rendah"** (kemiskinan struktural); penyebut `√(X_hθ̂)` adalah komponen **"varians tinggi"** (volatilitas/risiko). Dua rumah tangga dengan V̂ sama bisa punya cerita berbeda:
- Rata-rata rendah + varians rendah → **miskin kronis** → butuh bantuan reguler (PKH/Sembako).
- Rata-rata cukup + varians tinggi → **rentan volatil** → butuh proteksi (PBI JKN, bantuan adaptif, asuransi, dana darurat).

> Temuan asli Chaudhuri et al. untuk Indonesia 🟡: korelasi **negatif** antara pendidikan dan kerentanan; kerentanan rumah tangga perdesaan tanpa pendidikan formal berasal dari **rendahnya rata-rata prospek konsumsi** (bukan dari volatilitas).

### 5.3 Ambang batas kerentanan

🟢 **Cut-off 0,5** adalah konvensi standar, bersumber dari Pritchett, Suryahadi & Sumarto (2000):

> "Untuk mengelompokkan rumah tangga menurut status kemiskinannya, peluang yang dimiliki setiap rumah tangga selanjutnya dibandingkan dengan **nilai cut off 0,5** karena sebuah rumah tangga dikatakan rentan jika menghadapi **kemungkinan 50 persen atau lebih untuk menjadi rumah tangga miskin dalam waktu dekat**." — Rahman & Wulansari, Jurnal ASKS.

**Justifikasi teoretis** 🟡: (a) 50-50 adalah *focal point* yang intuitif; (b) rumah tangga yang persis di garis kemiskinan dan menghadapi guncangan simetris ber-mean nol **secara matematis memiliki kerentanan tepat 0,5** — jadi 0,5 adalah titik netral yang natural.

**Alternatif ambang di literatur** 🟡: (i) ambang = **tingkat kemiskinan observasi** (jika headcount 9%, ambang V = 0,09) — lebih longgar, menangkap "relatively vulnerable"; (ii) ambang ganda: V ≥ 0,5 = **highly vulnerable**, headcount ≤ V < 0,5 = **relatively vulnerable**.

### 5.4 Taksonomi Suryahadi–Sumarto (klasifikasi silang)

Tiga sumbu: **konsumsi sekarang** (c vs z), **konsumsi harapan** (E[c] vs z), dan **probabilitas kerentanan** (V vs 0,5). 🟢/🟡

| Kondisi | Kategori | Intervensi yang tepat |
|---|---|---|
| c < z **dan** E[c] < z | **Miskin kronis** (chronic poor) | Bantuan reguler + intervensi struktural (pendidikan, pekerjaan) |
| c < z **dan** E[c] ≥ z | **Miskin transien** (transient poor) | Bantuan sementara + pemulihan guncangan |
| c ≥ z **dan** V ≥ 0,5 | **Rentan miskin / highly vulnerable non-poor** | **Pencegahan**: JKN, proteksi guncangan, asuransi |
| c ≥ z **dan** V < 0,5 | Tidak miskin, kerentanan rendah | — |

> 🟡 Suryahadi & Sumarto (2003), *Asian Economic Journal* 17(1): "the chronic poor are the currently poor who have expected consumption levels **below** the poverty line…"; "the vulnerable non-poor group comprises households that are not currently in poverty but are vulnerable to events — **a bad harvest, a lost job, an illness, an unexpected expense, an economic downturn** — that could easily push them into poverty." Temuan: kerentanan pasca-krisis 1997/98 meningkat tak-ambigu; proporsi rumah tangga dengan kerentanan tinggi **lebih dari dua kali lipat** sejak krisis.

### 5.5 Vulnerability to Poverty Line (VPL)

Pritchett, Suryahadi & Sumarto (SMERU Working Paper) mengusulkan **VPL** = tingkat pengeluaran di bawah mana rumah tangga dinyatakan rentan. Ini memungkinkan **headcount vulnerability rate** — analog langsung dari headcount poverty rate. 🟡

**Temuan kuantitatif kunci** 🟡:
> "if the poverty line is set so that the headcount poverty rate is **20 percent**, the proportion of households vulnerable to poverty is roughly **30–50 percent**."

→ **Rule of thumb untuk NADI:** populasi rentan berukuran **1,5×–2,5× populasi miskin**. Angka ini menentukan ukuran antrean prioritas yang masuk akal untuk Pringsewu.

## 6. Ligon & Schechter (VEU) dan Dercon

**Ligon, E. & Schechter, L. (2003), "Measuring Vulnerability", *The Economic Journal* 113(486):C95–C102.** Dikerjakan dalam proyek **UNU/WIDER "Insurance against Poverty"** yang diarahkan **Stefan Dercon**. 🟡

Kontribusi utama: ukuran kerentanan yang **dapat didekomposisi**:
```
Vulnerability = Poverty + Aggregate risk + Idiosyncratic risk (+ measurement error / unexplained risk)
```

Temuan empiris (panel Bulgaria 1994) 🟡:
- **Kemiskinan adalah komponen tunggal terbesar** — lebih dari **separuh** kerentanan teramati.
- **Guncangan agregat lebih penting daripada risiko idiosinkratik.**
- Rumah tangga dengan kepala **laki-laki, bekerja, berpendidikan** lebih tahan terhadap guncangan agregat.

> **Implikasi untuk NADI:** dekomposisi ini adalah *blueprint* langsung untuk panel "Mengapa keluarga ini berisiko?" — pisahkan kontribusi (i) deprivasi struktural, (ii) paparan guncangan wilayah (banjir, harga gabah, PHK massal — sama untuk seluruh pekon), (iii) guncangan individual (sakit, kematian pencari nafkah). Tiga komponen ini memetakan ke tiga jenis intervensi yang berbeda.

**Dercon, S. (2006), "Vulnerability to Poverty", CSAE WPS/2007-03** 🟡 — kerangka yang menekankan bahwa kerentanan adalah fungsi dari **paparan risiko × kapasitas mengelola risiko**, dan bahwa **strategi coping yang merusak** (menjual aset produktif, menarik anak dari sekolah, mengurangi kualitas gizi) mengubah guncangan transien menjadi kemiskinan permanen.

## 7. Garis Kerentanan Versi Bank Dunia untuk Indonesia

### 7.1 Kelas ekonomi (klasifikasi Bank Dunia — *Aspiring Indonesia*, 2019)

| Kelas | Batas (× garis kemiskinan nasional) | Share Sept 2024 | Jumlah |
|---|---|---|---|
| **Miskin** (poor) | < 1,0 GK | 8,57% | 24,06 juta |
| **Rentan miskin** (vulnerable) | **1,0 – 1,5 GK** | **24,42%** | **68,51 juta** |
| **Menuju kelas menengah** (aspiring middle class) | **1,5 – 3,5 GK** | 49,29% | 138,31 juta |
| **Kelas menengah** (middle class) | 3,5 – 17 GK | 17,25% | 48,41 juta |
| **Kelas atas** (affluent) | > 17 GK | 0,46% | 1,29 juta |

🟡 Definisi batas dari World Bank, *Aspiring Indonesia — Expanding the Middle Class* (Sept 2019); angka share Sept 2024 dari pemberitaan yang mengutip BPS/Bank Dunia.

**Definisi "aspiring middle class"** 🟡: kelompok yang **tidak miskin dan tidak sangat rentan**, tetapi **belum mencapai tingkat/stabilitas konsumsi kelas menengah**. Kuncinya bukan pendapatan semata melainkan **stabilitas**.

### 7.2 Angka jangkar untuk Pringsewu/Lampung

| Indikator | Nilai | Periode | Keyakinan |
|---|---|---|---|
| **GK nasional** | **Rp669.235** /kapita/bulan (naik 4,33% vs Sept 2025) | Maret 2026 | 🟡 |
| — komponen makanan | Rp499.886 (**74,70%**) | Maret 2026 | 🟡 |
| — komponen bukan makanan | Rp169.349 (**25,30%**) | Maret 2026 | 🟡 |
| GK per rumah tangga (asumsi 4,62 ART) | Rp3.091.866 /bulan | Maret 2026 | 🟡 |
| Kemiskinan nasional | **8,07%** (22,93 juta), turun dari 8,25% (23,36 juta) | Maret 2026 | 🟡 |
| **GK Provinsi Lampung** | **Rp657.467** /kapita/bulan (naik 3,69% vs Sept 2025) | Maret 2026 | 🟡 |
| — GK perkotaan Lampung | Rp708.693 | Maret 2026 | 🟡 |
| — GK perdesaan Lampung | Rp631.717 | Maret 2026 | 🟡 |
| Kemiskinan Lampung | **9,31%** (turun 0,35 pp dari 9,66%) | Maret 2026 | 🟡 |
| — perdesaan | 10,41% | Maret 2026 | 🟡 |
| — perkotaan | 7,28% | Maret 2026 | 🟡 |
| GK nasional Sept 2025 (pembanding) | Rp641.443 /kapita/bulan | Sept 2025 | 🟡 |
| **Kemiskinan Kabupaten Pringsewu (P0)** | **7,60%** (31,66 ribu jiwa); 2024: 8,32% (34,42 ribu) | 2025 / 2024 | ✅ dari `03-profil-pringsewu.md` |
| **Garis Kemiskinan Pringsewu** | ±Rp613.000 (2025, ⚠️ naratif); **Rp583.425** (2024, ✅) | 2025 / 2024 | ✅ dari `03-profil-pringsewu.md` |
| P1 (kedalaman) / P2 (keparahan) Pringsewu | 0,58 / 0,10 (2025); 0,92 / 0,16 (2024) | | ✅ dari `03-profil-pringsewu.md` |
| Gini Ratio Pringsewu | 0,299 (2025); 0,266 (2024) | | ✅ dari `03-profil-pringsewu.md` |

**Garis kerentanan turunan — gunakan GK KABUPATEN PRINGSEWU, bukan GK provinsi:**
```
OPSI A (dianjurkan) - GK Pringsewu 2024, angka BPS terverifikasi:
   Garis kemiskinan (z)      = Rp   583.425 /kapita/bulan   [GK Pringsewu 2024]
   Garis kerentanan (1,5z)   = Rp   875.138 /kapita/bulan
   Batas aspiring MC (3,5z)  = Rp 2.041.988 /kapita/bulan

OPSI B - GK Pringsewu 2025 (naratif "lebih dari enam ratus tiga belas ribu"):
   Garis kemiskinan (z)      = Rp   613.000 /kapita/bulan   [!! angka naratif]
   Garis kerentanan (1,5z)   = Rp   919.500 /kapita/bulan
   Batas aspiring MC (3,5z)  = Rp 2.145.500 /kapita/bulan

PEMBANDING - GK perdesaan Lampung Mar 2026 = Rp 631.717 (1,5z = Rp 947.576)
```
⚠️ Semua angka 1,5z dan 3,5z adalah **hasil perkalian** — tandai `is_derived: true` di seed data; jangan tampilkan sebagai angka resmi BPS. GK Pringsewu 2024 (Rp583.425) adalah **satu-satunya angka GK level kabupaten yang terverifikasi silang dua dokumen**; lihat `03-profil-pringsewu.md`.

---

# BAGIAN III — MACHINE LEARNING UNTUK PENARGETAN KEMISKINAN

## 8. Paper Kunci dan Angka yang Bisa Dikutip

### 8.1 Aiken, Bellue, Karlan, Udry & Blumenstock (2022), *Nature* 603:864–870 🟢
**"Machine learning and phone data can improve targeting of humanitarian aid"** — evaluasi program **Novissi** (Togo, COVID-19). Seluruh angka di bawah diekstrak dari teks penuh NBER WP 29070.

| Metode | Spearman | AUC | Exclusion error |
|---|---|---|---|
| *Panel A — layak diimplementasi di Togo 2020* | | | |
| Prefecture (Admin-2) blanket | 0,30 | 0,64 | (recall 39%) |
| Canton (Admin-3) blanket | 0,19 | 0,59 | (recall 33%) |
| Phone expenditure (tanpa ML) | — | 0,57 (rural) / 0,63 (nasional) | — |
| **Phone-based ML** | — | **0,70 (rural) / 0,73 (nasional)** | **53% (rural) / 50% (nasional)** |
| Occupation-based (kriteria asli Novissi: pekerja informal) | — | — | 76% |
| Occupation-based "optimal" (semua transfer ke pekerja pertanian) | — | — | **48%** |
| *Panel B — butuh social registry (tidak feasible di Togo)* | | | |
| Asset-based wealth index | — | 0,55–0,75 | — |
| Poverty Probability Index (PPI) | — | **0,81** | — |
| PMT "perfectly calibrated" | — | **0,85** | — |

**Kesimpulan abstrak** 🟢: "Relative to the geographic targeting options considered by the Government of Togo, the machine learning approach **reduces errors of exclusion by 4–21%**. Relative to methods requiring a comprehensive social registry…, the machine learning approach **increases exclusion errors by 9–35%**."

**Peringatan yang wajib dikutip NADI** 🟢:
> "the performance of the 'perfectly calibrated' PMT may **substantially over-estimate the performance of a real-world PMT**, which declines steadily over time since calibration."

**Metodologi metrik yang layak ditiru NADI** 🟢:
- **Spearman**, bukan Pearson: "targeting concerns itself only with the **ordering** of observations according to poverty."
- **ROC/AUC** mengikuti Hanna & Olken (2018): pada tiap ambang T, simulasikan menargetkan T% populasi teratas menurut proksi, hitung TPR & FPR terhadap T% termiskin menurut ground truth.
- **Kurva "Coverage vs Recall"** — bagaimana precision & recall berubah seiring naiknya persentase populasi penerima. **Ketika kuota = prevalensi, precision = recall secara konstruksi.**
- **Exclusion error = 1 − recall.**
- **Social welfare** dengan utilitas **CRRA** (mengikuti Hanna & Olken 2018): anggaran tetap (USD 4 juta untuk 154.238 registran), transfer sama rata, telusuri kurva kesejahteraan pada berbagai ambang → temukan *beneficiary share* optimal. Temuan: **semua metode targeting mengalahkan UBI bila share & besaran transfer dikalibrasi baik.**

**Audit fairness (metodologi yang harus ditiru)** 🟢:
1. **Normalized rank residuals** per subkelompok (boxplot) — kelompok yang konsisten *under-ranked* terlihat sebagai box bergeser ke kiri.
2. **Demographic parity gap** — selisih persentase poin antara *proporsi subkelompok yang ditargetkan* dan *proporsi subkelompok yang benar-benar miskin* menurut ground truth.

Hasil: pendekatan phone-based **tidak** membuat perempuan lebih mungkin salah-eksklusi dibanding laki-laki; juga tidak menciptakan exclusion error signifikan untuk etnis, agama, kelompok umur, atau tipe rumah tangga tertentu.

**Dekomposisi sumber eksklusi program (Tabel 2)** — kerangka berpikir yang sangat berguna 🟢:

| Sumber eksklusi | Tingkat lolos |
|---|---|
| (i) Harus punya SIM card/HP | 65% orang dewasa, 85% rumah tangga |
| (ii) Harus baru memakai SIM (agar skor bisa dihitung) | 72–97% registran |
| (iii) Harus pemilih terdaftar | ±87% dewasa |
| (iv) Harus *self-target* & mencoba mendaftar | ±40% orang eligible mencoba |
| (v) Harus berhasil mendaftar (literasi digital) | 72% berhasil, rata-rata 4 percobaan |
| (vi) Harus diidentifikasi eligible oleh algoritma | **47% recall** |

> 🟢 "algorithmic targeting errors are an important source of program exclusion, but **real-world programs also face structural and environmental constraints to inclusion**."
> → **NADI harus memodelkan eksklusi non-algoritmik ini secara eksplisit** (NIK tidak padan, tidak punya rekening/KKS, tidak tahu programnya ada, tidak bisa mengakses kantor pekon).

### 8.2 Aiken, Bedoya, Blumenstock & Coville (2023), *Journal of Development Economics* 🟢
**"Program targeting with machine learning and mobile phone data: Evidence from an anti-poverty intervention in Afghanistan"** (arXiv:2206.11400)

Setting: program **Targeting the Ultra-Poor (TUP)**, Balkh. Ground truth = penetapan "ultra-poor" hasil metode hybrid (community wealth ranking + survei singkat). N survei 2.582–2.852; N matched dengan CDR = **535**; kuota targeting 27%.

| Metode | Precision & Recall | AUC |
|---|---|---|
| CDR (mobile phone) + ML | 42% | 0,68 |
| Consumption | 45% | 0,71 |
| Asset wealth index | 49% | **0,73** |
| CDR + assets | — | 0,76 |
| Kombinasi dua sumber lainnya | — | 0,75–0,76 |
| **CDR + assets + consumption** | — | **0,78** |

**Empat temuan yang langsung relevan** 🟢:
1. Sumber data non-tradisional **hampir seakurat** ukuran survei konvensional.
2. **Menggabungkan sumber data selalu lebih akurat daripada sumber tunggal manapun.**
3. **Ukuran kesejahteraan saling berkorelasi lemah:** korelasi asset index vs consumption hanya **0,37** (survei penuh) / **0,34** (subsampel). "less than half of the ultra-poor fall into the bottom 27% of the sample by wealth index or consumption." → **Aset dan konsumsi bukan hal yang sama.** Model yang hanya memakai aset akan sistematis melewatkan sebagian orang miskin.
4. **Karakter error-nya sistematis, bukan acak:** "false negatives score higher on **food security, financial inclusion, and psychological well-being** than true positives" — model salah-mengeksklusi rumah tangga ultra-miskin yang relatif lebih baik pada dimensi yang **tidak dipakai** untuk targeting.

### 8.3 McBride & Nichols (2018), *World Bank Economic Review* 32(3):531–550 🟡
**"Retooling Poverty Targeting Using Out-of-Sample Validation and Machine Learning"**

Argumen inti: prosedur estimasi PMT yang populer **meminimalkan error in-sample**, padahal tujuan sesungguhnya adalah **prediksi out-of-sample**. Dengan **cross-validation** dan **stochastic ensemble methods** (regression forests, quantile regression forests), performa out-of-sample dapat **membaik secara substansial**. Didemonstrasikan dengan **USAID poverty assessment tool** dan basis datanya.
🔴 Angka perbaikan spesifik tidak berhasil diekstrak — WBER berbayar, abstrak tidak memuat angka.

### 8.4 Sohnesen & Stender (2017), *Poverty & Public Policy* (World Bank WPS 7612) 🟡
**"Is Random Forest a Superior Methodology for Predicting Poverty? An Empirical Assessment"**
- Membandingkan prediksi out-of-sample pada survei tahun yang sama di **6 negara**.
- **Random forest sering lebih akurat** daripada praktik umum (multiple imputation dengan variabel dipilih via stepwise dan Lasso).
- **Tetapi:** tidak satu pun metode konsisten memberikan prediksi akurat **lintas waktu**.

### 8.5 Jean, Burke, Xie, Davis, Lobell & Ermon (2016), *Science* 353(6301):790–794 🟡
**"Combining satellite imagery and machine learning to predict poverty"**
- **Transfer learning bertingkat:** natural images (ImageNet) → intensitas cahaya malam (nightlights) sebagai proksi kaya-data → ukuran kemiskinan.
- Menggabungkan peta cahaya malam dengan citra siang resolusi tinggi untuk memperkirakan konsumsi rumah tangga & aset.
- Relevansi untuk NADI: **prediksi level area (agregat), bukan level rumah tangga.** Cocok memberi **prior geografis per pekon/kecamatan**, tidak untuk memutuskan kelayakan individu.

### 8.6 SWIFT — Survey of Well-being via Instant and Frequent Tracking (World Bank) 🟡
- Dimulai **2014**; **>100 survei SWIFT** di **>50 negara**; dipakai di **>50 operasi pinjaman**.
- Mekanisme: **15–20 pertanyaan sederhana** non-konsumsi; model imputasi dikembangkan dari LSMS untuk **mengimputasi konsumsi**.
- Varian: SWIFT 1.0 (klasik), **SWIFT Plus** (lokasi mengalami guncangan ekonomi), SWIFT-COVID19, SWIFT 2.0 (area tanpa data terkini yang andal).
- **Relevansi NADI:** cetak biru untuk **modul survei singkat pendamping/kader** — 15–20 pertanyaan yang bisa diselesaikan di lapangan, hasilnya diimputasi ke skala kesejahteraan yang sama dengan model utama. Ini cara yang sah untuk memutakhirkan data **di antara** siklus DTSEN triwulanan.

### 8.7 Poverty Probability Index (PPI) 🟢/🟡
**Referensi metodologi:** Kshirsagar, Wieczorek, Ramanathan & Wells (2017), *Household poverty classification in data-scarce environments: a machine learning approach*, NIPS 2017 (arXiv:1711.06813).

Kendala desain yang mereka hormati — sangat instruktif untuk UI NADI 🟢:
1. Model memakai **maksimum 10 pertanyaan** (kadang 8–12); 10–15 menit vs beberapa jam untuk survei konsumsi penuh.
2. **Tidak butuh komputasi selain aritmetika sederhana** — enumerator menjumlahkan poin lalu mengecek tabel lookup skor → probabilitas miskin.
3. **Satu spesifikasi model untuk seluruh negara**, meski ada perbedaan sub-nasional besar. Konsekuensinya: model **harus dievaluasi per region, bukan hanya nasional**.
4. Kandidat pertanyaan awal **30–100 variabel** (memilih 10 dari 30 = >2 juta kombinasi; 10 dari 50 = >10 miliar) → butuh algoritma seleksi variabel yang prinsipiel (regularisasi + cross-validation + stability selection, menggantikan stepwise regression).
5. Model dibatasi ke **varian regresi logistik tanpa interaksi** agar enumerator tak perlu mengalikan bobot.

**PPI Indonesia** 🟡: dibuat **Oktober 2023** oleh Innovations for Poverty Action (IPA), berbasis **SUSENAS 2022**, memakai metodologi baru IPA (berlaku untuk semua PPI setelah Juli 2017).
Skala global 🟢: scorecard tersedia untuk ~60 negara yang mencakup **>90% penduduk miskin dunia**; dipakai oleh **hampir 600 organisasi**.

> **Rekomendasi konkret untuk NADI:** sediakan **"Mode Cepat"** — 10 pertanyaan bergaya PPI untuk kader/pendamping yang menemui keluarga yang belum ada di DTSEN atau yang datanya diragukan. Skor Mode Cepat harus dikalibrasi ke skala probabilitas yang sama dengan model utama dan **ditandai berbeda** di UI (`source: rapid_assessment`).

### 8.8 Gonzales Martinez & Cooray (2025), arXiv:2503.04300 🟢
**"Enhancing Poverty Targeting with Spatial Machine Learning: An application to Indonesia"** — paper paling langsung relevan dengan NADI.

| Aspek | Detail |
|---|---|
| Data | SUSENAS/DTKS **2016–2020** (n=1.533.746, 134 variabel) dan **2016–2021** (n=1.512.887, 255 variabel) |
| Label | Pengeluaran per kapita → biner, **ambang kemiskinan 40%** (sesuai skema DTKS) |
| Metode | **Spatial ML**: matriks kontiguitas spasial; clustering hierarkis spasial via **Delaunay Triangulation** pada sentroid **kabupaten**; model ML terpisah per klaster; fitur = X standar + **spatially lagged features Z = WX** |
| Algoritma dibandingkan (8) | Elastic Net, Gradient Boosting, Linear Regression, Logistic Classification, Naive Bayes, Neural Network, Random Forest, SGD |
| Metrik | **EE = fn/(tp+fn)**, **IE = fp/(tp+fp)**, sensitivity, specificity, R² |
| Hasil 2016–2020 | Baseline EE **28,20%** (linear regression) → **SML 20,14%** (Naive Bayes, 12 klaster) = **turun 8 pp**. Baseline IE 27,36% → SML 28,97% |
| Hasil 2016–2021 | Baseline EE 26,73% → SML **24,19%** (Naive Bayes, 4 klaster) = turun 2,54 pp. Baseline IE 27,53% → SML 31,23% |
| Temuan tambahan | **Model tanpa PCA mengungguli model dengan PCA** — "feature engineering may outperform statistical dimensionality reduction techniques" |

> 🟠 Catatan metodologis: paper menyebut split **"80% test sample, 20% training sample"** — rasio tidak lazim (terbalik dari konvensi). Tandai sebagai kemungkinan salah tulis; jangan tiru rasionya.

> **Implikasi terkuat untuk NADI:** **geografi adalah fitur, bukan gangguan.** Menambahkan struktur spasial (klaster + lagged features tetangga) menurunkan exclusion error **8 poin persentase**. NADI beroperasi di **satu kabupaten** — artinya ia bisa memakai **efek pekon/kecamatan** yang secara struktural **tidak tersedia** bagi PMT nasional (lihat kutipan Brown et al. di §1.1).

### 8.9 Ohlenburg dan referensi terkait 🟡
- **Okamura, Y., Ohlenburg, T. & Tesliuc, E. (2024).** *Scaling Up Social Assistance Where Data is Scarce — Opportunities and Limits of Novel Data and AI.* World Bank. (Dokumen ditemukan; 🔴 ekstraksi isi gagal — PDF 7,1 MB tidak ter-parse.)
- **Aiken, E., Ohlenburg, T. & Blumenstock, J. (2023).** *Moving targets: When does a poverty prediction model need to be updated?* COMPASS '23, Cape Town. DOI 10.1145/3588001.3609369.
- 🔴 **Tidak ditemukan** IZA Discussion Paper karya Ohlenburg tentang targeting — kemungkinan referensi dalam brief awal keliru.

### 8.10 Referensi kerangka teoretis tambahan
- **Hanna, R. & Olken, B. (2018).** "Universal Basic Incomes versus Targeted Transfers", *JEP* 32(4):201–226 🟡. Studi **Indonesia dan Peru**. Meskipun PMT tidak sempurna, **transfer tertarget menghasilkan gain kesejahteraan jauh lebih tinggi** daripada program universal untuk anggaran total yang sama — **tetapi** menimbulkan lebih banyak pelanggaran *horizontal equity* dan pajak implisit pada konsumsi di zona phase-out.
- **Coady, D., Grosh, M. & Hoddinott, J. (2004).** *Targeting of Transfers in Developing Countries.* World Bank 🟡. Basis data **>100 intervensi antikemiskinan di 47 negara**. Program median mentransfer **25% lebih banyak** ke si miskin dibanding alokasi universal; performa sangat bervariasi; **means testing, geographic targeting, dan self-selection berbasis persyaratan kerja** paling konsisten progresif.
- **Fischer-Abaigar, U., Kern, C. & Perdomo, J.C. (2025).** *The Value of Prediction in Identifying the Worst-Off*, arXiv:2501.19334 🟡.
- **Yamin, J.C. (2026).** *Poverty Targeting with Imperfect Information*, arXiv:2506.18188 🟡. Ketegangan sentral: **akurasi targeting vs cakupan program**. Kerangka: Bayes risk, regret bounds vs oracle, ukuran kemiskinan kelas FGT.

---

# BAGIAN IV — METRIK EVALUASI PENARGETAN SOSIAL

## 9. Definisi dan Rumus

### 9.1 Matriks konfusi dalam bahasa targeting

|  | Diprediksi eligible | Diprediksi tidak eligible |
|---|---|---|
| **Benar-benar layak (miskin/rentan)** | TP — *correct inclusion* | **FN — EXCLUSION ERROR / undercoverage** |
| **Benar-benar tidak layak** | **FP — INCLUSION ERROR / leakage** | TN — *correct exclusion* |

```
Exclusion Error (EE)  = FN / (TP + FN)   = 1 − Recall     = undercoverage
Inclusion Error (IE)  = FP / (TP + FP)   = 1 − Precision  = leakage rate
Coverage rate         = (TP + FP) / N                      (share populasi dijangkau)
Recall @ k            = TP@k / (total yang benar-benar layak)
Precision @ k         = TP@k / k
Lift @ k              = Precision@k / prevalensi
```
🟢 Definisi EE dan IE persis ini dipakai Gonzales Martinez & Cooray (2025) untuk Indonesia.

> ⚠️ **Hati-hati dengan definisi ganda.** Sebagian literatur mendefinisikan leakage = FP/(TP+FP) (basis penerima), sebagian lain FP/(total tidak layak) (basis populasi = FPR). **NADI wajib menuliskan denominator di label metrik**, mis. `Leakage (basis: penerima) = 24%`.

**Sifat penting** 🟢: Brown et al. (2016) — ketika tingkat kemiskinan dipertahankan tetap (targeting berbasis kuota), **setiap exclusion error otomatis menghasilkan satu inclusion error**, sehingga **IER = EER**. Aiken et al. mencatat hal yang sama: "by construction, **precision and recall are equal** in this simulation."

### 9.2 Targeting Differential (TD) — Ravallion

```
TD  = (transfer rata-rata ke si miskin) − (transfer rata-rata ke si tidak miskin)
```
Untuk transfer seragam kepada semua yang dinyatakan eligible 🟡:
```
TD  = Pr(diprediksi miskin | benar miskin) − Pr(diprediksi miskin | benar tidak miskin)
    = TPR − FPR
    = Youden's J statistic
NTD = TD / rata-rata penerimaan transfer      (Normalized Targeting Differential)
```
> 🟡 "The Targeting Differential (TD) is defined as the mean transfer made to the poor less that made to the non-poor… The NTD divides this measure by the mean transfer receipt, to make the resulting measure more comparable across countries and programs." — Brown, Ravallion & van de Walle (2016).

Brown et al. mencatat 🟢: ketika tingkat kemiskinan ditetapkan tetap, **NTD adalah transformasi linear sederhana dari exclusion rate.** → Jika NADI sudah melaporkan recall@k, NTD tidak menambah informasi baru; laporkan salah satu saja plus penjelasan.

### 9.3 Coady-Grosh-Hoddinott (CGH) Index

```
CGH = (share total transfer yang diterima kelompok sasaran) / (share populasi kelompok sasaran)
```
🟡 Interpretasi:
- **CGH > 1** → progresif (mis. bottom 40% menerima lebih dari 40% total transfer)
- **CGH = 1** → setara alokasi universal/acak
- **CGH < 1** → regresif
- Benchmark global: program median = **1,25** (25% lebih banyak ke si miskin dibanding alokasi universal).

CGH hanya bermakna ketika NADI mengetahui **nominal transfer** per keluarga (tersedia dari `02-katalog-program-intervensi.md`). Untuk skor kerentanan murni tanpa nominal, gunakan recall@k dan targeting differential.

### 9.4 ROC-AUC dan Spearman

- **AUC** = 0,5 (acak) sampai 1,0 (sempurna). Konstruksi mengikuti Hanna & Olken (2018) 🟢: pada tiap ambang T, targetkan T% teratas menurut proksi, hitung TPR & FPR terhadap T% termiskin menurut ground truth.
- **AUC tidak bergantung pada ambang** — Aiken et al. tidak melaporkannya ulang saat mengubah definisi garis kemiskinan 🟢.
- **Spearman ρ**, bukan Pearson: "targeting concerns itself only with the **ordering** of observations." 🟢

**Benchmark AUC realistis (untuk menetapkan ekspektasi NADI):**

| Sumber | Metode | AUC |
|---|---|---|
| Aiken et al. 2022 | geographic blanket | 0,59–0,68 |
| Aiken et al. 2022 | phone ML | 0,70–0,73 |
| Aiken et al. 2022 | asset wealth index | 0,55–0,75 |
| Aiken et al. 2022 | **PPI** | **0,81** |
| Aiken et al. 2022 | **PMT "perfectly calibrated"** (batas atas optimistis) | **0,85** |
| Aiken et al. 2023 (Afghanistan) | assets / consumption / CDR | 0,73 / 0,71 / 0,68 |
| Aiken et al. 2023 | kombinasi tiga sumber | 0,78 |

> **Aturan main untuk NADI:** setiap AUC di atas **0,90** pada data mirip-DTSEN harus dianggap **bukti kebocoran (leakage)**, bukan bukti model bagus. Lihat §15.

### 9.5 Mengapa recall@k lebih relevan daripada accuracy

**Empat argumen, urut dari yang paling kuat:**

**(1) Argumen anggaran — masalahnya adalah alokasi sumber daya, bukan klasifikasi.**
Kapasitas verifikasi lapangan tetap: jumlah pendamping × hari kerja. Yang menentukan adalah **berapa banyak keluarga layak yang tertangkap dalam k slot pertama**, bukan berapa persen prediksi yang benar secara keseluruhan.
> 🟡 "Given limited capacity, top-k metrics focus on instances that will be prioritized"; "…is fundamentally a **resource-allocation problem** where investigation teams have fixed analyst capacity; a scored queue determines which accounts receive review and which do not."

**(2) Argumen prevalensi — accuracy menyesatkan pada kelas tak seimbang.**
Bila 12% keluarga layak, model yang memprediksi "tidak layak" untuk semua orang mencapai **accuracy 88%** dan **recall 0%**. Accuracy adalah metrik yang aktif berbahaya di sini.

**(3) Argumen asimetri biaya — exclusion error jauh lebih mahal secara kesejahteraan.**
Dietrich et al. (2024) 🟢 memformalkan ini dengan bobot kesejahteraan Atkinson: kesalahan pada rumah tangga sangat miskin dibobot jauh lebih berat. Brown/Ravallion/van de Walle 🟢: "Inclusion errors are generally costly to the public budget while **exclusion errors save public money**" — pemerintah dan lembaga keuangan internasional karena itu cenderung terlalu menekankan inclusion error; "Some observers have questioned this prioritization, arguing that **exclusion errors should get higher weight when the policy objective is to minimize poverty**."

**(4) Argumen alur kerja — output NADI adalah antrean, bukan keputusan.**
Keputusan final ada di Musdes/Muskel. Model hanya menentukan **siapa yang diperiksa lebih dulu**. Metrik yang tepat untuk sistem ranking adalah metrik ranking.

**Metrik yang HARUS ada di dashboard NADI:**
```
recall@100, recall@300, recall@500        <- k = kapasitas verifikasi nyata per triwulan
precision@100, @300, @500
exclusion error @ budget                  <- = 1 - recall@k
lift@k = precision@k / prevalensi         <- "berapa kali lebih baik dari acak"
AUC + Spearman rho                        <- ringkasan tak-bergantung-ambang
CGH index                                 <- bila nominal program diketahui
Brier score + ECE + reliability diagram   <- kalibrasi (Bagian V)
recall@k terpisah per kecamatan / gender KK / urban-rural  <- fairness (Bagian VII)
```

**Metrik yang TIDAK BOLEH jadi headline:** accuracy, F1 tanpa konteks k, dan klaim jenis "model kami 94% akurat".

---

# BAGIAN V — KALIBRASI PROBABILITAS

## 10. Mengapa Kalibrasi Wajib untuk NADI

**Perbedaan yang sering dilewatkan:** *ranking* yang baik (AUC tinggi) **tidak** berarti *probabilitas* yang benar. Gradient boosting terkenal menghasilkan skor **tidak terkalibrasi** — cenderung *underconfident* di rentang probabilitas rendah dan *overconfident* di rentang menengah. 🟡

**Kalibrasi menjadi wajib jika (dan NADI memenuhi ketiganya):**
1. **Skor ditampilkan sebagai angka ke manusia.** "Risiko 72%" harus berarti: dari 100 keluarga dengan skor ini, ±72 benar-benar berada dalam kondisi target. Kalau tidak, angka itu berbohong.
2. **Skor dibandingkan lintas wilayah/waktu.** Jika model kurang terkalibrasi di perdesaan dibanding perkotaan, membandingkan "risiko rata-rata Pekon A vs Pekon B" menjadi tidak sah.
3. **Ambang keputusan memicu tindakan.** Ambang yang keliru = keputusan yang keliru:
> 🟡 "If decision thresholds have been appropriately decided, score calibration is a **necessary condition for a fair procedure** because if scores are miscalibrated, this is equivalent to implementing inappropriate decision thresholds."

### 10.1 Metode kalibrasi

| Metode | Cara kerja | Kapan dipakai | Kelemahan |
|---|---|---|---|
| **Platt scaling** (sigmoid) | Fit `P = 1/(1+exp(A·f + B))` pada skor mentah, di set kalibrasi terpisah | Kurva kalibrasi berbentuk **sigmoid** & monoton naik; **data kalibrasi terbatas** | Hanya 2 parameter — tak bisa memperbaiki distorsi non-sigmoid |
| **Isotonic regression** | Fit fungsi tangga monoton non-parametrik | Kurva kalibrasi **bukan sigmoid**; **data kalibrasi banyak** | Butuh lebih banyak data; menghasilkan **tangga tajam**; rawan overfit di ekor distribusi |

🟡 Ringkasan literatur: "Platt Scaling works best when the calibration curve is monotonically increasing and has a sigmoid shape, and is computationally efficient and requires relatively less data compared to Isotonic Regression"; "Isotonic Regression makes fewer assumptions… however, it generally requires more data to yield stable results and can sometimes produce **sharp steps**."

### 10.2 Metrik dan diagnostik kalibrasi

| Alat | Rumus / cara | Interpretasi |
|---|---|---|
| **Brier score** | `BS = (1/N) Σ (p̂ᵢ − yᵢ)²` | Semakin kecil semakin baik. **Proper scoring rule** — menggabungkan kalibrasi + refinement. Dekomposisi Murphy: `BS = Reliability − Resolution + Uncertainty` |
| **Log loss** | `−(1/N) Σ [y log p̂ + (1−y) log(1−p̂)]` | Proper scoring rule; menghukum sangat berat prediksi confident-tapi-salah |
| **Reliability diagram** | Bin prediksi; plot rata-rata p̂ (sumbu x) vs frekuensi observasi (sumbu y) | Diagonal = sempurna. Di bawah diagonal = overconfident; di atas = underconfident |
| **ECE** (Expected Calibration Error) | `ECE = Σ (n_b/N) · |acc(b) − conf(b)|` atas bin b | Rata-rata tertimbang deviasi absolut dari diagonal |

🟡 Contoh magnitudo nyata dari literatur (LightGBM): model tanpa kalibrasi Brier **0,082** → setelah Platt scaling **0,080**. **Perbaikan kalibrasi biasanya kecil dalam angka absolut tetapi besar dalam kegunaan tampilan.**

### 10.3 Resep konkret untuk NADI

```
SPLIT:  train (60%) / calibration (20%) / test (20%)
        stratified by kecamatan x label
        !! Split HARUS di level KELUARGA (nomor KK), bukan individu.
        !! Untuk uji generalisasi spasial, tambahkan LEAVE-ONE-KECAMATAN-OUT CV.

1. Latih LightGBM/XGBoost pada train
2. Fit isotonic regression pada calibration set (jika n_calib >= ~3.000);
   jika kurang, pakai Platt scaling
3. Evaluasi di test: Brier, ECE (10 bin), reliability diagram
4. Laporkan reliability diagram TERPISAH untuk:
      - perkotaan vs perdesaan
      - kepala keluarga perempuan vs laki-laki
      - tiap kecamatan
   -> jika ada subkelompok yang kurvanya jauh dari diagonal,
      JANGAN pakai satu ambang global
5. Tampilkan di UI dalam PITA, bukan angka desimal:
      "Risiko tinggi (60-80%)"   BUKAN   "72,4%"
   Alasan: presisi palsu memicu overtrust
```

⚠️ **Kalibrasi dilakukan SETELAH semua penyeimbangan kelas.** Jika memakai undersampling/SMOTE, probabilitas ter-shift secara sistematis dan harus dikoreksi. Literatur menandai keterbatasan Platt scaling setelah undersampling secara khusus (arXiv:2410.18144). 🟡

⚠️ **Impossibility theorem yang harus disadari** 🟡:
> "Imperfectly accurate predictors **cannot satisfy between-group calibration and equality of false positives and false negatives** when the base rate distribution is unequal between groups."

Karena tingkat kemiskinan perdesaan Lampung (10,41%) ≠ perkotaan (7,28%), **NADI tidak bisa sekaligus** terkalibrasi per-wilayah **dan** menyamakan FPR/FNR antar-wilayah. Pilihan harus dibuat sadar dan didokumentasikan (lihat §12.3–12.4).

---

# BAGIAN VI — EXPLAINABILITY

## 11. TreeSHAP, Penyajian, dan Bahaya Salah Tafsir

### 11.1 TreeSHAP: mengapa cocok untuk NADI

**Referensi:** Lundberg, S.M. et al. (2020), "From local explanations to global understanding with explainable AI for trees", *Nature Machine Intelligence* 2:56–67.

- Menghitung **nilai Shapley eksak** untuk model berbasis pohon (XGBoost/LightGBM/CatBoost) dalam waktu polinomial.
- Kompleksitas turun dari `O(T·L·2^M)` (exact KernelSHAP) menjadi **`O(T·L·D²)`** — T = jumlah pohon, L = maks daun per pohon, D = kedalaman maksimum, M = jumlah fitur. 🟡
- **Menghilangkan noise sampling** yang mengganggu metode SHAP generik.
- Sifat **aditif lokal**: `f(x) = φ₀ + Σⱼ φⱼ(x)` — kontribusi tiap fitur menjumlah tepat ke prediksi. Inilah yang membuat penjelasan "faktor A menambah X poin, faktor B mengurangi Y poin" secara matematis sah.

### 11.2 Cara menyajikan ke pengguna non-teknis

**Prinsip: satu kalimat, satu arah, satu besaran relatif.**

| ❌ Jangan | ✅ Lakukan |
|---|---|
| "SHAP value untuk `luas_lantai_per_kapita` = −0,214" | "**Rumah sempit untuk 6 orang** — faktor pendorong risiko terbesar" |
| Beeswarm plot di layar petugas pekon | 3 kartu "Pendorong risiko" + 2 kartu "Penahan risiko", terurut |
| "Model memprediksi 0,7243" | "**Risiko tinggi.** Sekitar 3 dari 5 keluarga dengan profil serupa mengalami penurunan kesejahteraan dalam setahun terakhir." |
| Menampilkan 25 fitur | Top-3 pendorong + top-2 penahan; sisanya di balik "Lihat semua faktor" |

**Template kalimat yang direkomendasikan:**
```
[Nama Keluarga] - Skor kerentanan: TINGGI (pita 60-80%)

Faktor yang MENAIKKAN risiko:
  ^ Kepala keluarga bekerja sebagai buruh tani harian (tidak tetap)
  ^ Ada anggota keluarga dengan penyakit kronis, belum terdaftar PBI JKN
  ^ Rumah: lantai tanah, luas 4,2 m2/orang (di bawah standar 7,2 m2)

Faktor yang MENAHAN risiko:
  v Dua anak bersekolah dan menerima PIP
  v Memiliki lahan pekarangan produktif

(i) Faktor-faktor ini menjelaskan BAGAIMANA MODEL MENGHITUNG skor -
    bukan sebab-akibat. Memperbaiki satu faktor tidak otomatis
    menurunkan risiko yang sesungguhnya.
```

**Kanal penyajian bertingkat:**

| Pengguna | Yang ditampilkan |
|---|---|
| Kader / pendamping pekon | 3 pendorong + 2 penahan, bahasa awam, tanpa angka SHAP |
| Operator Dinsos | + kontribusi numerik, + perbandingan dengan rata-rata kecamatan |
| Analis / auditor | + beeswarm, dependence plot, global importance, versi model & tanggal latih |

### 11.3 ⚠️ Bahaya salah tafsir SHAP sebagai kausalitas

Ini bagian **paling berisiko secara etis** untuk NADI. Lima masalah nyata:

**(1) SHAP menjelaskan MODEL, bukan DUNIA.**
Chen, Janizek, Lundberg & Lee (2020), *True to the Model or True to the Data?* (arXiv:2006.16234) 🟡: terdapat dua cara menghubungkan model ML ke *coalitional game* — **interventional** vs **observational conditional expectation**. Pilihannya **bergantung aplikasi**, dan menentukan apakah kita "true to the model" atau "true to the data". Tidak ada jawaban universal.

**(2) Nilai Shapley tidak dirancang untuk tujuan explainability manusiawi.**
Kumar, Venkatasubramanian, Scheidegger & Friedler (2020), ICML 🟡: "mathematical problems arise when Shapley values are used for feature importance and that the solutions to mitigate these **necessarily induce further complexity, such as the need for causal reasoning**"; dan "Shapley values **do not provide explanations which suit human-centric goals of explainability**."

**(3) Korelasi fitur merusak interpretasi.**
Ketika fitur berkorelasi tinggi — dan variabel DTSEN **sangat** berkorelasi (lantai tanah ↔ tanpa jamban ↔ tanpa listrik memadai) — algoritma dapat mengevaluasi **kombinasi nilai fitur yang tidak realistis** saat merata-ratakan efek terhadap background dataset. 🟡

**(4) Path dependency problem pada TreeSHAP.** 🟡
"In Tree SHAP, path probability is computed by implicitly **assuming that splitting variables are independent** of other remaining variables, and such an assumption **does not hold in general**." Bahkan ada klaim bahwa algoritma TreeSHAP tidak menghitung penjelasan SHAP sebagaimana didefinisikan semula.

**(5) SHAP bisa dimanipulasi untuk menyembunyikan bias.** 🟡
"it's possible to create **intentionally misleading interpretations** with SHAP, which can hide biases."

**Aturan wajib untuk NADI:**
```
1. SETIAP tampilan SHAP wajib membawa disclaimer:
   "Menjelaskan cara model menghitung skor, BUKAN sebab-akibat."

2. DILARANG memakai SHAP untuk merumuskan rekomendasi kebijakan kausal
   ("turunkan X untuk menurunkan kemiskinan").
   Rekomendasi program HARUS datang dari ATURAN KELAYAKAN PROGRAM
   (lihat 02-katalog-program-intervensi.md), bukan dari SHAP.

3. Karena fitur DTSEN berkorelasi tinggi, laporkan SHAP pada level
   KELOMPOK FITUR (perumahan, aset, pekerjaan, pendidikan, kesehatan),
   bukan fitur individual. Ini mengurangi masalah (3) & (4) secara material.

4. Simpan versi model + tanggal latih + hash dataset bersama tiap penjelasan
   (audit trail).
```

### 11.4 Counterfactual / actionable explanations

**Referensi:** Wachter, S., Mittelstadt, B. & Russell, C. (2017), "Counterfactual Explanations Without Opening the Black Box: Automated Decisions and the GDPR" 🟡; Karimi, von Kügelgen, Schölkopf & Valera, "Algorithmic Recourse: from Counterfactual Explanations to Interventions" 🟡.

Konsep inti 🟡:
- **Recourse** = kemampuan individu mengubah hasil model melalui perubahan yang **actionable**.
- Metode recourse membatasi pada **subset fitur** untuk menghindari perubahan tak realistis ("kurangi usia dari 50 ke 25").
- Sebagian fitur **mutable tetapi tidak directly actionable** — mis. skor kredit tidak bisa diubah langsung; ia berubah sebagai efek dari pendapatan.

**Untuk konteks bansos, framing counterfactual harus DIBALIK.**
Di kredit, counterfactual ditujukan ke **pemohon** ("naikkan pendapatan Anda"). Dalam bansos itu **berbahaya dan tidak etis** — menyalahkan keluarga miskin atas kemiskinannya, dan memicu **gaming** (merusak lantai rumah agar terlihat miskin — masalah nyata yang terdokumentasi di literatur PMT).

**Framing yang benar untuk NADI — counterfactual ditujukan ke PROGRAM, bukan ke keluarga:**
```
X  "Agar layak, keluarga ini perlu ..."

OK "Jika keluarga ini terdaftar PBI JKN, skor risiko turun dari 74% ke 61%."
OK "Faktor yang paling bisa diintervensi Pemkab: akses air bersih
    (3 dari 5 keluarga berisiko tinggi di Pekon X berbagi kendala yang sama)."
OK "Data yang jika diperbarui akan paling mengubah skor: status pekerjaan KK
    (terakhir diperbarui 14 bulan lalu)."   <- counterfactual sebagai
                                               PRIORITAS VERIFIKASI
```
Penggunaan ketiga — **counterfactual sebagai alat prioritisasi verifikasi data** — adalah aplikasi paling aman dan paling bernilai untuk NADI. Ia menjawab: "field mana yang paling layak diverifikasi ulang karena paling menggerakkan skor?"

⚠️ **Risiko gaming**: Aiken et al. (2022) 🟢 mengingatkan bahwa metode sederhana yang transparan "may also introduce scope for strategic **'gaming'** if used repeatedly over time." NADI tidak boleh mempublikasikan bobot fitur eksak ke publik; tetapi **harus** mempublikasikan **daftar dimensi** yang dipakai (transparansi prosedural tanpa memberi peta untuk memanipulasi).

---

# BAGIAN VII — FAIRNESS

## 12. Bias, Metrik Fairness, dan Mana yang Tepat untuk Bansos

### 12.1 Sumber bias yang harus diuji di konteks Indonesia

| Jenis bias | Mekanisme | Uji yang harus dilakukan |
|---|---|---|
| **Bias geografis** | Model dilatih pada distribusi nasional/provinsi; pekon terpencil under-represented. PMT nasional **secara struktural tidak bisa** memakai efek desa (Brown et al. 🟢) | recall@k per kecamatan; leave-one-kecamatan-out CV; residual rata-rata per pekon |
| **Bias urban-rural** | Base rate berbeda (Lampung: desa 10,41% vs kota 7,28% 🟡); biaya hidup & bentuk aset berbeda (lahan vs kendaraan) | Reliability diagram terpisah; recall@k terpisah; pastikan GK berbeda (Rp631.717 vs Rp708.693) dipakai sebagai deflator |
| **Bias gender kepala keluarga** | KK perempuan sering karena kematian suami, perceraian, atau suami merantau. **Kerja tak dibayar tidak tercatat** — "PPLS dan Susenas tidak memasukkan jam kerja tidak dibayar karena masih bias pekerjaan berbayar" 🟡 | Rank residual per gender KK; demographic parity gap; recall@k terpisah |
| **Bias ukuran rumah tangga** | **Terbukti empiris** 🟢: Dietrich et al. menemukan **rumah tangga kecil** sistematis lebih mungkin salah diklasifikasi sebagai non-miskin akibat reporting bias + bobot PMT tak stabil | recall@k per kuintil ukuran keluarga — **uji WAJIB** |
| **Bias disabilitas & lansia** | Rumah tangga lansia tunggal punya konsumsi rendah tapi aset "cukup" (rumah warisan) → sering dinilai tidak miskin | recall@k untuk keluarga dengan ART lansia / disabilitas |
| **Label bias** | Ground truth (desil DTSEN) itu sendiri adalah **output PMT** — bukan kebenaran. Melatih model pada desil = mereplikasi error PMT | Bandingkan dengan sumber label independen (Musdes, verifikasi lapangan) |
| **Bias representasi / coverage** | Keluarga tanpa NIK padan Dukcapil tidak muncul sama sekali → **invisible exclusion** | Hitung & laporkan jumlah keluarga di luar DTSEN yang dikenali kader |

**Angka konteks Indonesia** 🟡: "Hampir **3 juta rumah tangga dengan kepala rumah tangga perempuan** ada di 3 desil terendah dalam basis data terpadu."

### 12.2 Metrik fairness: definisi

| Metrik | Definisi formal | Arti operasional |
|---|---|---|
| **Demographic parity** (statistical parity) | `P(Ŷ=1 | A=a)` sama untuk semua a | Proporsi yang ditargetkan sama antar kelompok — **terlepas dari kebutuhan sesungguhnya** |
| **Equal opportunity** | `P(Ŷ=1 | Y=1, A=a)` sama untuk semua a | **TPR (= recall) sama antar kelompok.** Di antara yang benar-benar layak, peluang terjangkau sama |
| **Equalized odds** | TPR **dan** FPR sama antar kelompok | Equal opportunity + syarat leakage setara |
| **Calibration within groups** (sufficiency) | `P(Y=1 | p̂=p, A=a) = p` untuk semua a | Skor 70% berarti hal yang sama di desa dan di kota |

🟡 "Demographic Parity requires independence between prediction and protected features…, while Equalized Odds requires conditional independence of model output from protected features given the ground truth. **Equal opportunity is a relaxed version of equalized odds that only considers conditional expectations with respect to positive labels**."

### 12.3 Mana yang tepat untuk bansos? — **EQUAL OPPORTUNITY**

> **Rekomendasi: metrik fairness utama NADI adalah EQUAL OPPORTUNITY (paritas recall/TPR antar kelompok), didampingi calibration-within-groups sebagai pemeriksaan sekunder.**

**Alasan, urut kekuatan argumen:**

**(1) Demographic parity SALAH untuk bansos karena base rate memang berbeda secara sah.**
Kemiskinan perdesaan Lampung (10,41%) memang lebih tinggi dari perkotaan (7,28%). Memaksa proporsi penargetan sama antara desa dan kota berarti **sengaja mengeksklusi keluarga miskin desa** demi simetri statistik. 🟡 "Parity metrics take **no account of the actual utility consequences** of being selected or rejected"; "Strict parity may come at significant social cost, especially in reduction of aggregate utility or welfare."

**(2) Equal opportunity menjawab pertanyaan keadilan yang benar untuk bansos.**
Pertanyaannya bukan "apakah tiap kelompok mendapat porsi sama?" melainkan **"jika seorang perempuan kepala keluarga benar-benar layak, apakah peluangnya terjangkau sama besarnya dengan laki-laki kepala keluarga yang sama-sama layak?"** Itu persis definisi TPR-parity.

**(3) Equalized odds terlalu ketat dan berpotensi kontraproduktif.**
Menyamakan FPR berarti menyamakan tingkat kebocoran. Namun dari sudut kesejahteraan (Dietrich et al. 🟢), inclusion error pada keluarga hampir-miskin di desa **jauh lebih tidak merugikan** daripada exclusion error. Menegakkan FPR-parity dapat memaksa penurunan recall justru di kelompok yang paling membutuhkan.

**(4) Konsisten dengan praktik terbaik dalam literatur.**
Aiken et al. (2022) 🟢 mengaudit fairness dengan bertanya apakah suatu kelompok **"systematically more likely to be incorrectly excluded"** — itu bahasa exclusion-error-parity = equal opportunity, bukan demographic parity.

**(5) Kesadaran akan impossibility theorem.** 🟡
Calibration-within-groups + equalized odds **tidak bisa** dipenuhi bersamaan ketika base rate berbeda. Karena base rate desa-kota **memang** berbeda, NADI harus memilih: **prioritaskan equal opportunity untuk keputusan penargetan; pantau kalibrasi per kelompok untuk keputusan penampilan angka.** Dokumentasikan trade-off ini secara eksplisit — ini justru menjadi nilai jual "AI yang bertanggung jawab".

### 12.4 Implementasi konkret

```
FAIRNESS DASHBOARD NADI  (wajib, di halaman "Kesehatan Model")

Untuk setiap atribut sensitif A dalam {kecamatan, urban/rural, gender KK,
kuintil ukuran keluarga, ada ART disabilitas, ada ART lansia}:

  1. recall@k per kelompok  ->  EQUAL OPPORTUNITY GAP = maks - min
     Ambang alarm: gap > 10 poin persentase  ->  tandai MERAH
  2. Normalized rank residual boxplot per kelompok   (mengikuti Aiken et al.)
  3. Demographic parity gap (informasional saja, TIDAK untuk dioptimasi):
     (% kelompok ditargetkan) - (% kelompok yang benar-benar layak)
  4. Reliability diagram per kelompok  ->  calibration gap
  5. Prevalensi kelompok di data latih vs di populasi Pringsewu
     ->  deteksi bias representasi

MITIGASI (urut preferensi):
  a. Perbaiki DATA (tambah sampel kelompok under-represented)  <- SELALU PERTAMA
  b. Group-aware threshold: ambang berbeda per kecamatan agar recall setara
     !! perlu justifikasi kebijakan tertulis; ini keputusan politik, bukan teknis
  c. Reweighting saat training (bobot lebih tinggi untuk kelompok minoritas)
  d. Post-processing (Hardt et al. equalized odds) - pilihan terakhir,
     karena mengorbankan kalibrasi
```

> 🟢 Prinsip penutup dari Dietrich et al. (2024): "These results call for closer scrutiny and more transparency in targeting procedures (**'fairness through awareness'**; Dwork et al., 2012). However, they also raise the question of whether, in certain contexts, **targeting should be regarded as a prediction problem in the first place**."

---

# BAGIAN VIII — DETEKSI ANOMALI

## 13. Deteksi Mismatch Inclusion/Exclusion pada Data Penerima

### 13.1 Bukti empiris skala masalah di Indonesia

| Temuan | Angka | Sumber |
|---|---|---|
| NIK KPM tidak valid | **3.877.965** | BPKP (2020) 🟡 |
| KPM duplikat (nama + NIK identik) | **41.985** | BPKP (2020) 🟡 |
| KPM tidak layak di Jabodetabek | **3.060** | BPKP 🟡 |
| NIK ART tidak valid di DTKS | **10.922.479** | BPK 🟡 |
| Nomor KK tidak valid | **16.373.682** | BPK 🟡 |
| ART bernama kosong | **5.702** | BPK 🟡 |
| ART dengan NIK duplikat | **86.465** | BPK 🟡 |
| Data penerima bansos dipangkas (pembersihan DTKS) | **21 juta** | Indonesia.go.id 🟡 |
| Penerima "anomali" ditemukan (2025–2026) | **>100.000** (ASN, TNI-Polri, BUMN/BUMD, dokter, dosen, manajer, eksekutif); **55.000** sudah dihentikan, **44.000** dalam proses | Kemensos via Menpan.go.id 🟡 |
| KPM dicoret Mei 2026 | **11.014** | 🟡 |

**Penyebab anomali yang teridentifikasi** 🟡: perpindahan KK, perbaikan nama di Dukcapil, kegagalan pemadanan NIK.

### 13.2 Arsitektur deteksi tiga lapis (rekomendasi NADI)

> **Prinsip: rule-based dulu, unsupervised kemudian, supervised terakhir.** Aturan deterministik menangkap sebagian besar masalah dengan false positive nol dan explainability penuh. ML hanya untuk sisa yang tidak bisa diaturkan.

#### LAPIS 1 — Validasi berbasis aturan (deterministik, prioritas tertinggi)

```
A. INTEGRITAS IDENTITAS
   x  NIK bukan 16 digit / gagal validasi struktur (kode wilayah, tanggal lahir, urut)
   x  NIK duplikat lintas KK
   x  NIK sama, nama berbeda (indikasi salah input / pinjam NIK)
   x  Nama kosong / 1 karakter / mengandung karakter non-nama
   x  Status padan Dukcapil = TIDAK PADAN
   x  Tanggal lahir mustahil (usia > 120 th; tanggal lahir > hari ini)
   x  Individu terdaftar aktif di lebih dari 1 KK

B. KONTRADIKSI LOGIS ANTAR-FIELD
   x  Desil 1-4 TAPI daya listrik >= 2.200 VA
   x  Desil 1-4 TAPI memiliki mobil / lahan > 2 ha
   x  Pekerjaan = ASN/TNI/Polri/pegawai BUMN TAPI desil 1-4
   x  Menerima >= 3 program bansos utama sekaligus (overlap tidak lazim)
   x  Jumlah ART = 0 atau > 20
   x  Kepala keluarga berusia < 15 tahun
   x  Ada ART tercatat bersekolah TAPI seluruh ART berusia > 25
   x  Luas lantai per kapita > 100 m2 TAPI desil rendah

C. TANDA HIDUP / KELAYAKAN BERKELANJUTAN
   x  Status Dukcapil = MENINGGAL tapi masih penerima aktif
   x  Pindah domisili keluar kabupaten tapi masih tercatat
   x  Tidak ada transaksi penyaluran > 2 siklus berturut-turut  -> cek kelayakan
   x  Rekening / KKS tidak aktif

D. KONSISTENSI SPASIAL
   x  Koordinat geotag di luar batas administratif pekon yang tercatat
   x  Koordinat duplikat persis untuk > 3 KK berbeda (indikasi enumerator malas)
   x  Koordinat (0,0) atau null
```

Setiap aturan menghasilkan **flag bernama** dengan tingkat keparahan (`blocking` / `review` / `info`) — bukan skor buram. Inilah yang bisa dipertanggungjawabkan di forum Musdes.

#### LAPIS 2 — Anomaly detection unsupervised

**Isolation Forest** — Liu, F.T., Ting, K.M. & Zhou, Z.-H. (2008), ICDM; versi jurnal *"Isolation-Based Anomaly Detection"*, ACM TKDD 6(1) (2012). 🟡

| Aspek | Detail |
|---|---|
| Prinsip | Anomali **sedikit dan berbeda**, sehingga **lebih mudah diisolasi** dengan split acak. Skor = kedalaman rata-rata daun yang mengisolasi titik |
| Kekuatan | Kompleksitas waktu **linear rendah** via subsampling; memori kecil; **bekerja baik pada dimensi tinggi dengan banyak atribut tak relevan**; menangani *swamping* dan *masking*; tidak butuh label anomali |
| Parameter kritis | **`contamination`** — proporsi anomali yang diharapkan. "the contamination parameter is where most practitioners go wrong… getting it wrong either floods you with false positives or misses real threats" 🟡 |

**Local Outlier Factor (LOF)** — Breunig et al. (2000). 🟡
- Membandingkan **densitas lokal** suatu titik dengan densitas tetangganya. Densitas jauh lebih rendah = anomali.
- **Kelebihan untuk NADI:** menangkap anomali **kontekstual** — keluarga yang "normal" secara nasional tetapi **aneh untuk pekonnya**. Ini persis kasus "satu-satunya rumah tembok berlantai keramik di RT yang seluruhnya lantai tanah".
- **Kelemahan:** komputasi mahal seiring ukuran data, terutama dimensi tinggi.

**Autoencoder** 🟡 — rekonstruksi input; error rekonstruksi tinggi = anomali. Berguna untuk data campuran kategorikal-numerik berdimensi tinggi, tetapi **kalah dalam explainability**. **Rekomendasi: jangan dipakai di NADI v1** — biaya explainability tidak sebanding dengan gain.

#### LAPIS 3 — Analisis residual (paling bernilai, sering dilewatkan)

Ini bukan anomaly detection generik, melainkan **deteksi mismatch antara skor model dan status program** — persis masalah inclusion/exclusion yang ingin dijawab NADI.

```
Untuk setiap keluarga, hitung:
   r = skor_kerentanan_model  -  implied_kerentanan_dari_desil_DTSEN

  r >> 0  (model bilang berisiko tinggi, DTSEN bilang desil tinggi, TIDAK menerima)
          ->  KANDIDAT EXCLUSION ERROR  ->  ANTREAN VERIFIKASI PRIORITAS
  r << 0  (model bilang berisiko rendah, tapi MENERIMA banyak program)
          ->  KANDIDAT INCLUSION ERROR  ->  ANTREAN AUDIT

Perkuat dengan:
  - Isolation Forest dijalankan pada VEKTOR RESIDUAL, bukan pada fitur mentah
    -> menemukan pola mismatch yang tak tertangkap ambang sederhana
  - LOF dalam grup pekon -> mismatch relatif terhadap tetangga
  - Analisis level-pekon: pekon dengan rata-rata |r| tinggi
    -> indikasi masalah SISTEMIK (kualitas enumerasi, data usang), bukan individual
```

### 13.3 Praktik audit yang harus dianut

| Prinsip | Alasan |
|---|---|
| **Anomali ≠ kecurangan.** Setiap flag adalah **hipotesis untuk diverifikasi manusia**, bukan vonis | Bias data lebih sering daripada kecurangan. Penghapusan otomatis menciptakan exclusion error baru |
| **Tidak ada penghapusan otomatis** dari daftar penerima | Konsekuensi false positive: keluarga miskin kehilangan bantuan |
| **Setiap flag punya penjelasan bahasa manusia** | Harus bisa dibacakan di Musdes |
| **Jejak audit lengkap** (siapa, kapan, apa, alasan, bukti foto/koordinat) | Akuntabilitas & penyelesaian sengketa |
| **Ukur presisi flag secara berkala** | Berapa % flag yang terkonfirmasi benar setelah verifikasi lapangan? Bila < 30%, aturan perlu diperketat |
| **Audit dua sisi** | Audit *inclusion* (yang tak layak menerima) DAN *exclusion* (yang layak tidak menerima). Sistem audit yang hanya mencari kebocoran akan **memperburuk** exclusion error |

---

# BAGIAN IX — DINAMIKA KEMISKINAN & GUNCANGAN

## 14. Chronic vs Transient vs Vulnerable Non-Poor

### 14.1 Definisi operasional (lihat juga §5.4)

| Kategori | Definisi | Karakteristik | Intervensi yang tepat |
|---|---|---|---|
| **Chronic poor** | Miskin sekarang **dan** konsumsi harapan di bawah GK | Faktor **struktural**: pendidikan rendah, layanan kesehatan minim, lokasi terpencil/perdesaan, tidak ada akses kredit, bekerja di pertanian 🟡 | Bantuan reguler jangka panjang + investasi SDM (PKH, Sembako, PIP) |
| **Transient poor** | Miskin sekarang **tetapi** konsumsi harapan di atas GK | Akibat **guncangan negatif**: sakit, krisis ekonomi, gagal panen 🟡 | Bantuan sementara + pemulihan (BLT, bantuan darurat) |
| **Vulnerable non-poor** | Tidak miskin sekarang, **tetapi** V ≥ 0,5 (atau di pita 1,0–1,5 GK) | Konsumsi di atas GK tetapi **tanpa penyangga**; sedikit guncangan menjatuhkan | **Pencegahan**: PBI JKN, asuransi pertanian, dana cadangan pekon, diversifikasi usaha |

### 14.2 Angka Indonesia — ⚠️ SUMBER BERKONFLIK

🟠 **Estimasi komposisi kronis vs transien SANGAT berbeda antar studi.** Jangan pakai satu angka tanpa catatan.

| Studi | Data | Chronic | Transient |
|---|---|---|---|
| Studi A 🟡 | SUSENAS panel 2005 & 2007 | 28% dari RT miskin kronis; 7% RT tidak miskin rentan jadi transient poor | — |
| Studi B 🟡 | SUSENAS panel 2005 & 2007 | **18,89%** | **81,11%** |
| Studi C 🟡 | SUSENAS panel 2008 & 2010 | 6,7% dari **total** RT kronis | — |
| Studi D 🟡 (*Cogent Economics* 2023, "Indonesia's poverty puzzle") | — | **77%** dari kemiskinan | 23% |
| IFLS 1993–2014 🟡 | 5 gelombang | **11,9%** tetap miskin kronis; **34,4%** dari si miskin naik ke kelas menengah | — |

**Penyebab konflik (wajib disebut dalam dokumentasi NADI):** perbedaan definisi (kronis = miskin di 2 periode vs E[c] < GK), unit analisis (RT miskin vs total RT), panjang panel, dan **measurement error** dalam data konsumsi cross-section. Brown et al. 🟢 menunjukkan memakai *time-mean consumption* dari panel memperbaiki ukuran targeting — mengindikasikan noise pengukuran memang berperan.

**Kesimpulan yang aman:** kemiskinan Indonesia menunjukkan **churning substansial** — arus masuk-keluar besar relatif terhadap stok. Karena itu **snapshot desil saja tidak cukup**; kerentanan (arus) harus dimodelkan terpisah dari status (stok). **Inilah justifikasi inti keberadaan NADI Vulnerability Score.**

### 14.3 Guncangan pemicu (shocks) — daftar untuk desain fitur

| Guncangan | Bukti / angka | Fitur yang bisa dimodelkan di NADI |
|---|---|---|
| **Sakit / biaya kesehatan katastropik** | ~**62.685** penduduk Indonesia jatuh di bawah garis kemiskinan **dalam satu bulan** akibat biaya penyakit katastropik; rawat inap kanker di RS tipe A Jakarta **Rp80–250 juta**; kelompok paling rentan **desil 3–6** — pekerja/petani kecil yang tidak tergolong miskin tapi tanpa cadangan finansial 🟡 | `ada_art_penyakit_kronis`, `status_kepesertaan_jkn`, `segmen_jkn (PBI/mandiri/PPU/none)`, `ada_art_disabilitas` |
| **Kehilangan pekerjaan / PHK** | Guncangan utama pada kelas menengah rentan 🟡 | `status_pekerjaan_kk (tetap/tidak tetap/harian)`, `sektor_pekerjaan_kk`, `jumlah_art_bekerja`, `rasio_ketergantungan` |
| **Gagal panen** | Guncangan klasik transient poverty 🟡. Studi Sambas 🟢: ~60% KRT rentan miskin bekerja di sektor primer, terutama pertanian tanaman pangan dengan penguasaan lahan sempit; 68,75% KRT rentan miskin berpendidikan SD ke bawah | `kk_sektor_pertanian`, `luas_lahan_garapan`, `status_lahan (milik/sewa/bagi hasil)`, `komoditas_utama`, `punya_asuransi_tani` |
| **Kematian pencari nafkah** | Pemicu utama KRT perempuan: "suami meninggal, suami tidak produktif lagi, perceraian, dan suami pergi merantau" 🟡 | `gender_kk`, `status_kawin_kk`, `usia_kk`, `jumlah_pencari_nafkah` |
| **Bencana** | Konteks Lampung: banjir, longsor, kekeringan | `zona_rawan_bencana_pekon`, `riwayat_bencana_12bln` (level pekon) |
| **Kenaikan harga pangan** | "Rumah tangga sedikit di atas garis kemiskinan tetap rentan jatuh miskin akibat guncangan kecil seperti kenaikan harga beras" 🟡. Komponen makanan = **74,70%** dari GK 🟡 → elastisitas terhadap harga pangan sangat tinggi | `share_pengeluaran_pangan` (proksi), `inflasi_pangan_kabupaten` (time-varying) |
| **Konteks makro** | Survei LPEM FEB UI 2024 🟡: hanya **17%** penduduk berstatus kelas menengah stabil, turun dari **23%** pada 2018 | Bahan diskusi, bukan fitur |

**Prinsip desain fitur guncangan:** guncangan hadir dalam **dua level**:
- **Idiosinkratik** (level keluarga): sakit, kematian, PHK individual
- **Kovarian/agregat** (level pekon/kecamatan/kabupaten): bencana, gagal panen massal, inflasi pangan, penutupan pabrik

Ligon & Schechter 🟡 menemukan **guncangan agregat lebih penting daripada risiko idiosinkratik**. → NADI **harus** menyertakan fitur level-pekon dan level-waktu, bukan hanya fitur keluarga. Ini juga sejalan dengan temuan Spatial ML Indonesia (§8.8).

---

# BAGIAN X — DATA SINTETIS YANG REALISTIS

## 15. Membuat Data Demo yang Tidak Berbohong

**Masalah yang harus dihindari:** data sintetis naif menghasilkan **AUC ~0,99** karena label dihitung sebagai fungsi deterministik dari fitur yang sama yang dipakai model. Demo terlihat spektakuler, tetapi (a) tidak jujur secara ilmiah, (b) juri/reviewer yang paham akan langsung mengenalinya, (c) tidak memberi informasi apa pun tentang perilaku sistem di dunia nyata.

> 🟡 "Leakage issues often remain unnoticed because they do not produce visible errors but instead manifest as **unusually high accuracy, overly smooth learning curves, or lack of class confusions**."

### 15.1 Prinsip #1 — Sisipkan variabel laten yang TIDAK diberikan ke model

Teknik terpenting, dan sejalan langsung dengan realitas: **PMT hanya menjelaskan ~50% variasi karena setengahnya memang tak teramati.**

```
GENERATIVE PROCESS (DGP) - desain berlapis

1. VARIABEL LATEN (dibangkitkan, DISIMPAN, tapi TIDAK MASUK fitur model):
   L1  kapasitas_pendapatan_riil   ~ f(pendidikan, sektor, jaringan sosial, keberuntungan)
   L2  kualitas_jaringan_sosial    ~ berkorelasi dengan pekon, tak teramati
   L3  guncangan_kesehatan_laten   ~ Bernoulli(p_umur x p_pekerjaan)
   L4  kualitas_enumerasi_pekon    ~ per-pekon, memengaruhi kebisingan pengukuran
   L5  akses_kredit_informal       ~ penyangga tak teramati

2. FITUR TERAMATI = fungsi NOISY dari laten:
   luas_lantai      = g(L1) + e1        e1 ~ N(0, s1^2)
   kepemilikan_aset = h(L1, L5) + e2
   daya_listrik     = diskretisasi(k(L1)) + kesalahan_pencatatan(L4)
   !! Noise pengukuran s HARUS cukup besar. Kalibrasi s sehingga
      R^2(fitur -> ln konsumsi) sekitar 0,45-0,55   <- target realistis (lihat 2.1)

3. LABEL dibangkitkan dari LATEN + noise, BUKAN dari fitur teramati:
   ln(konsumsi) = b*L1 + c*L2 - d*L3 + eta          eta ~ N(0, s_eta^2)
   miskin       = 1[konsumsi < GK]
   rentan       = 1[V >= 0,5]   dengan V dari model VEP berheteroskedastisitas

4. TAMBAHKAN NOISE LABEL (label bias - dokumentasikan sebagai fitur, bukan bug):
   - 3-5% label dibalik secara acak (kesalahan enumerasi)
   - Pembalikan TIDAK acak sempurna: buat lebih sering pada
     rumah tangga kecil (replikasi temuan Dietrich et al.) dan pada
     pekon dengan L4 rendah
   -> Ini yang membuat pengujian FAIRNESS di demo menjadi bermakna,
      bukan sekadar hiasan

5. VERIFIKASI: latih model, ukur AUC.
   TARGET: AUC dalam [0,72 ; 0,85]
   Jika AUC > 0,90 -> naikkan sigma noise, atau kurangi berapa banyak
                      informasi L1 yang bocor ke fitur teramati
   Jika AUC < 0,65 -> model terlalu lemah untuk mendemonstrasikan nilai
```

**Justifikasi angka target:** dari §9.4 — asset index 0,55–0,75; phone ML 0,70–0,73; PPI 0,81; PMT "perfectly calibrated" 0,85 (dan itu pun dinyatakan **overestimate** performa PMT dunia nyata 🟢). AUC **0,78–0,82** adalah *sweet spot* yang kredibel sekaligus tetap impresif.

### 15.2 Prinsip #2 — Kalibrasi marginal ke statistik agregat resmi (IPF / raking)

**Iterative Proportional Fitting (IPF)** — juga dikenal sebagai *raking* atau prosedur Deming–Stephan. 🟡

> "The primary concept of IPF is to **maintain the dependence structure from the disaggregated data** and alter the joint distribution to **fit the marginal distribution** of the attributes from the aggregated data."

**Algoritma:**
```
Input:  tabel awal (seed) dengan struktur dependensi realistis
        + target marginal dari statistik resmi
Ulangi sampai konvergen:
   untuk setiap dimensi d:
      skala seluruh sel sepanjang d sehingga jumlahnya = target marginal d
Konvergensi: perubahan maksimum antar-iterasi < toleransi (mis. 1e-6)
```

**Target marginal untuk Pringsewu (yang berhasil dikonfirmasi dalam riset ini):**

| Marginal | Nilai | Level | Keyakinan |
|---|---|---|---|
| Tingkat kemiskinan | 9,31% | Provinsi Lampung, Maret 2026 | 🟡 |
| — perdesaan | 10,41% | Lampung | 🟡 |
| — perkotaan | 7,28% | Lampung | 🟡 |
| Garis kemiskinan | Rp657.467 /kapita/bln | Lampung, Mar 2026 | 🟡 |
| — perdesaan | Rp631.717 | Lampung | 🟡 |
| — perkotaan | Rp708.693 | Lampung | 🟡 |
| Rata-rata ART per RT | 4,62 | Nasional, Mar 2026 | 🟡 |
| Share pangan dalam GK | 74,70% | Nasional, Mar 2026 | 🟡 |
| Distribusi kelas (poor/vulnerable/aspiring/middle/affluent) | 8,57 / 24,42 / 49,29 / 17,25 / 0,46 (%) | Nasional, Sept 2024 | 🟡 |
| **Kemiskinan Kab. Pringsewu (P0)** | **7,60%** (2025) / **8,32%** (2024) | Kabupaten | ✅ `03-profil-pringsewu.md` |
| **Garis Kemiskinan Pringsewu** | **Rp583.425** (2024, ✅) / ±Rp613.000 (2025, ⚠️ naratif) | Kabupaten | ✅ `03-profil-pringsewu.md` |
| **P1 / P2 Pringsewu** | 0,58 / 0,10 (2025); 0,92 / 0,16 (2024) | Kabupaten | ✅ `03-profil-pringsewu.md` |
| **Gini Ratio Pringsewu** | 0,299 (2025); 0,266 (2024) | Kabupaten | ✅ `03-profil-pringsewu.md` |
| **Struktur administrasi** | **9 kecamatan, 126 pekon, 5 kelurahan** | Kabupaten | ✅ `03-profil-pringsewu.md` |
| Penduduk Pringsewu | 424,68 ribu (proyeksi SP2020, 2024); 444.834 (Dukcapil Sem. II 2024) | Kabupaten | ✅ `03-profil-pringsewu.md` |
| TPT Pringsewu | 4,39% (2024) | Kabupaten | ✅ `03-profil-pringsewu.md` |

✅ **Angka kabupaten TERSEDIA** (lihat `03-profil-pringsewu.md`, diverifikasi silang dua dokumen BPS). Kalibrasi utama harus memakai **marginal Kabupaten Pringsewu**, dengan marginal provinsi/nasional hanya untuk dimensi yang tidak tersedia di level kabupaten (mis. distribusi 5 kelas ekonomi Bank Dunia).

Label wajib di UI demo:
> *"Data sintetis. Marginal dikalibrasi ke statistik resmi Kabupaten Pringsewu (BPS). Setiap keluarga adalah rekaan — bukan data riil penduduk."*

**Prioritas sumber marginal:** Kabupaten (Pringsewu) → Provinsi (Lampung) → Nasional. Jangan mencampur tahun: pilih satu tahun jangkar (dianjurkan **2024**, karena GK Pringsewu Rp583.425 dan P0 8,32% keduanya ✅ terverifikasi) dan konsisten.

**Dimensi yang harus di-rake:**
```
Dimensi 1: kecamatan (9) x urban/rural     -> target: distribusi populasi
           per kecamatan; total 126 pekon + 5 kelurahan
Dimensi 2: ukuran keluarga (1,2,3,4,5,6+)  -> target: rata-rata 4,62 ART
Dimensi 3: gender kepala keluarga          -> target: share KK perempuan
Dimensi 4: kelas ekonomi (5 pita)          -> target: 8,57/24,42/49,29/17,25/0,46
Dimensi 5: kelompok umur KK                -> target: piramida penduduk
```

### 15.3 Prinsip #3 — Copula untuk dependensi antar-variabel

**Masalah dengan IPF sendirian** 🟡: "although IPF is simple, computationally efficient, and rigorously founded, **it is unclear whether IPF well preserves the dependence structure** of the reference joint table sufficiently when fitting it to target margins."

**Solusi: Gaussian copula.** Memisahkan (a) **marginal tiap variabel** dari (b) **struktur dependensi**, sehingga keduanya bisa dispesifikasi secara independen — persis yang dibutuhkan.

```
LANGKAH GAUSSIAN COPULA
1. Tentukan marginal target F_j untuk tiap variabel j
   (dari statistik BPS untuk yang tersedia; dari asumsi berdokumentasi untuk sisanya)

2. Tentukan matriks korelasi Sigma pada skala latent normal.
   Gunakan korelasi yang plausibel & terdokumentasi, misalnya:
        corr(pendidikan_kk, pendapatan_laten)  =  +0,45
        corr(lantai_tanah,  tanpa_jamban)      =  +0,55
        corr(sektor_pertanian, perdesaan)      =  +0,60
        corr(asset_index, konsumsi)            =  +0,37   <- TEMUAN EMPIRIS
                                                             Aiken et al. 2023
   !! corr(asset, konsumsi) = 0,37 adalah angka empiris nyata (Afghanistan).
      Memakainya mencegah data sintetis yang terlalu "rapi".

3. Sampling: Z ~ MVN(0, Sigma);  U_j = Phi(Z_j);  X_j = F_j^{-1}(U_j)

4. Variabel kategorikal/boolean: cumulative-frequency embedding
   agar bisa masuk copula gabungan yang sama
```

🟡 Referensi: Jeong, B. et al. (2016), *Copula-Based Approach to Synthetic Population Generation*, PLOS ONE 11(8):e0159496; Li, Z. et al., *SynC: A Unified Framework for Generating Synthetic Population with Gaussian Copula*, arXiv:1904.07998; implementasi praktis: **SDV GaussianCopulaSynthesizer**.

🟡 Temuan komparatif: "Copula frameworks… **consistently surpass Iterative Proportional Fitting in terms of SRMSE** in transferability experiments, while introducing **unique observations not found in the original training sample**."

**Pipeline hibrida yang direkomendasikan untuk NADI:**
```
Copula (struktur dependensi realistis)
   -> IPF / raking (paksa marginal cocok dengan statistik BPS)
   -> injeksi variabel laten + noise (15.1)
   -> injeksi anomali terencana (15.4)
```

### 15.4 Prinsip #4 — Injeksi anomali terencana (agar Bagian VIII bisa didemokan)

Data sintetis harus **secara sengaja** mengandung anomali yang bisa ditemukan, dengan **ground truth tercatat** sehingga presisi detektor bisa diukur:

```
Sisipkan dengan proporsi terdokumentasi:
   ~0,8%  NIK duplikat lintas KK
   ~0,5%  keluarga desil 1-4 dengan daya listrik >= 2.200 VA
   ~0,3%  penerima dengan pekerjaan ASN/BUMN
   ~1,2%  ART berstatus meninggal masih aktif menerima
   ~2,0%  koordinat geotag di luar batas pekon
   ~0,4%  koordinat duplikat persis pada > 3 KK
   ~3,0%  keluarga sangat rentan yang TIDAK terdaftar di program apa pun
          <- kandidat EXCLUSION ERROR; ini yang paling penting untuk didemokan

Simpan kolom `is_planted_anomaly` + `anomaly_type` di tabel ground truth
(TIDAK diekspos ke aplikasi) untuk mengukur precision/recall detektor.
```

### 15.5 Prinsip #5 — Validasi kualitas data sintetis

| Metrik | Tujuan | Target |
|---|---|---|
| **KSComplement** (per kolom) 🟡 | Kesetiaan marginal | > 0,90 |
| **Column Pair Trends / CorrelationSimilarity** 🟡 | Pelestarian korelasi | > 0,85 |
| **Overall QualityScore** (SDV) 🟡 | Rata-rata dua di atas | > 0,88 |
| **TSTR** (Train on Synthetic, Test on Real) 🟡 | Utilitas prediktif | 🔴 N/A — tidak ada data riil untuk NADI |
| **AUC model pada data sintetis** | **Uji anti-leakage** | **0,72 – 0,85** ← paling penting |
| Reliability diagram | Kalibrasi bisa didemokan | Deviasi terlihat sebelum kalibrasi, membaik sesudahnya |
| Fairness gap | Uji fairness bermakna | Ada gap yang bisa dideteksi (mis. 8–15 pp), bukan 0 |

⚠️ **Peringatan leakage yang khusus relevan** 🟡: "When SMOTE-ENN oversampling is performed **before data splitting**, synthetic samples appear nearly identical to test points, leading to **near-perfect classification and inflated accuracy**." → **Split dulu, oversample belakangan, selalu.** Untuk NADI: **bangkitkan seluruh populasi sintetis dulu, baru split** — jangan membangkitkan train dan test dari proses generatif yang parameternya identik tanpa noise per-keluarga.

---

# BAGIAN XI — SPESIFIKASI KONKRET: NADI VULNERABILITY SCORE

## 16. Definisi Label (keputusan paling penting)

### 16.1 Masalah: DTSEN tidak menyediakan label kerentanan

DTSEN memberi **desil kesejahteraan** — output PMT, statis, relatif. Ia **bukan** label kerentanan. Melatih model untuk memprediksi desil hanya akan **mereplikasi PMT beserta seluruh error-nya** (label bias, Dietrich et al. 🟢), menghasilkan sistem yang tidak menambah nilai apa pun.

### 16.2 Rekomendasi: DUA SKOR TERPISAH, bukan satu

| | **Skor A — Deprivasi Saat Ini** | **Skor B — Risiko Memburuk (NADI Vulnerability Score)** |
|---|---|---|
| Pertanyaan yang dijawab | "Seberapa kurang kondisinya sekarang?" | "Seberapa besar peluang memburuk dalam 12 bulan?" |
| Analog literatur | PMT / desil DTSEN | VEP (Chaudhuri et al.) |
| Label | `1[konsumsi_proksi < GK]` atau `1[desil ≤ 4]` | `1[V̂ ≥ 0,5]`, `V̂ = Φ[(ln z − Xβ̂)/√(Xθ̂)]` |
| Jenis output | Pita + peringkat | **Probabilitas terkalibrasi** |
| Kegunaan di UI | Kelayakan program berbasis desil | **Prioritisasi antrean verifikasi & pencegahan** |
| Sudah ada? | Ya (DTSEN) — NADI **mereplikasi & mengaudit** | **Tidak ada** — ini kontribusi NADI |

> **Skor B adalah alasan NADI ada.** Skor A hanya dipakai untuk mengaudit konsistensi dengan DTSEN dan mendeteksi mismatch (§13.2 Lapis 3).

### 16.3 Tiga varian label untuk Skor B (implementasikan bertahap)

```
L1 - VEP CROSS-SECTIONAL                              [v1, WAJIB]
     Metode Chaudhuri / FGLS 3 tahap (5.2) pada proksi pengeluaran
     Label: V-hat >= 0,5
     + hanya butuh cross-section; sudah mapan; sitasi kuat
     - asumsi normalitas ln c; varians diestimasi dari cross-section

L2 - PITA GARIS KERENTANAN            [v1, WAJIB - untuk UI, bukan model]
     Label: 1,0 <= konsumsi_proksi / GK < 1,5     (definisi Bank Dunia)
     + mudah dijelaskan ke pemangku kepentingan; sitasi resmi
     - deterministik, tidak menangkap risiko

L3 - TRANSISI TERAMATI   [v2, jika panel DTSEN antar-triwulan tersedia]
     Label: keluarga yang desilnya TURUN >= 1 tingkat antar-snapshot DTSEN,
            ATAU beralih dari non-penerima ke penerima bansos darurat
     + label PALING dekat dengan "jatuh miskin" sesungguhnya
     - butuh >= 2 snapshot; churn desil bisa artefak pemutakhiran, bukan riil
     !! DTSEN diperbarui triwulanan -> L3 realistis mulai kuartal ke-3 operasi
```

**Keputusan v1:** latih model pada **L1**, tampilkan **L2** sebagai konteks pita di UI, siapkan skema data untuk **L3**.

## 17. Fitur

### 17.1 Prinsip pemilihan

1. **Semua fitur harus dapat diverifikasi di lapangan** (prinsip PMT) — kalau kader tidak bisa memeriksanya, jangan pakai.
2. **Pisahkan fitur STOK (aset, kondisi rumah) dari fitur ALIRAN (pekerjaan, guncangan).** Stok memprediksi Skor A; aliran memprediksi Skor B.
3. **Sertakan fitur level-pekon.** Ini keunggulan struktural NADI atas PMT nasional (§1.1, §8.8).
4. **Jangan masukkan penerimaan bansos sebagai fitur** untuk Skor B — itu kebocoran target (menerima bansos adalah *konsekuensi* dinilai miskin). Pakai hanya sebagai variabel audit.

### 17.2 Daftar fitur yang direkomendasikan

| Kelompok | Fitur | Skor A | Skor B | Sumber |
|---|---|---|---|---|
| **Demografi** | jumlah_art, rasio_ketergantungan, jumlah_art_balita, jumlah_art_lansia, jumlah_art_disabilitas | ✓ | ✓ | DTSEN |
| | usia_kk, gender_kk, status_kawin_kk, pendidikan_tertinggi_kk | ✓ | ✓ | DTSEN |
| **Perumahan (stok)** | status_kepemilikan_rumah, luas_lantai_per_kapita, jenis_lantai, jenis_dinding, jenis_atap | ✓ | ○ | DTSEN |
| | sumber_air_minum, fasilitas_bab, sumber_penerangan, **daya_listrik_va**, bahan_bakar_masak | ✓ | ○ | DTSEN + PLN |
| **Aset (stok)** | kepemilikan: motor, mobil, perahu, kulkas, AC, TV, HP, emas ≥10 gr, ternak besar/kecil | ✓ | ○ | DTSEN (±19 sub-variabel) |
| | luas_lahan_pertanian, status_penguasaan_lahan | ✓ | ✓ | DTSEN |
| **Pekerjaan (aliran)** | sektor_pekerjaan_kk, **status_pekerjaan_kk (tetap/tidak tetap/harian)**, jumlah_art_bekerja, jumlah_sumber_pendapatan | ○ | ✓✓ | DTSEN |
| **Kesehatan (aliran/risiko)** | kepesertaan_jkn, segmen_jkn, ada_art_penyakit_kronis, ada_art_disabilitas_berat | ○ | ✓✓ | DTSEN + BPJS (PBI) |
| **Pendidikan (aliran)** | jumlah_art_usia_sekolah_tidak_sekolah, jumlah_art_penerima_pip | ○ | ✓ | DTSEN |
| **Guncangan (aliran)** | kematian_art_12bln, sakit_berat_art_12bln, kehilangan_pekerjaan_kk_12bln, terdampak_bencana_12bln | — | ✓✓✓ | **Perlu ditambahkan** — tidak ada di DTSEN standar |
| **Level pekon** | tingkat_kemiskinan_pekon, jarak_ke_puskesmas, jarak_ke_pasar, akses_jalan, zona_rawan_bencana, share_pertanian_pekon | ✓ | ✓✓ | Podes / data pemda |
| **Spatial lag** | rata-rata fitur kunci dari pekon-pekon tetangga (`Z = WX`) | ✓ | ✓ | Diturunkan — mengikuti §8.8 |
| **Temporal** | bulan (musim tanam/panen), inflasi_pangan_kabupaten, **umur_data_hari** | — | ✓✓ | Kalender + BPS |
| **Kualitas data (meta)** | umur_record_hari, kelengkapan_field_pct, status_padan_dukcapil | audit | audit | Diturunkan |

Legenda: ✓✓✓ sangat penting · ✓✓ penting · ✓ berguna · ○ marginal · — jangan pakai

**Fitur `umur_data_hari` sangat penting dan sering dilupakan.** Karena akurasi PMT terdegradasi seiring waktu (Aiken/Ohlenburg/Blumenstock 🟡; Kidd & Wylde: jeda 4 tahun antar-survei Indonesia 🟢), model **harus tahu seberapa basi datanya** dan menurunkan keyakinannya. Ini langsung menghasilkan fitur produk: **"Data keluarga ini terakhir diperbarui 14 bulan lalu — prioritaskan verifikasi."**

### 17.3 Yang HARUS DIHINDARI sebagai fitur

| Jangan pakai | Alasan |
|---|---|
| Desil DTSEN sebagai fitur untuk Skor B | Kebocoran (desil adalah output PMT dari fitur yang sama) |
| Status penerimaan bansos | Kebocoran target + memperkuat lingkaran umpan balik |
| Agama, etnis/suku | Atribut terlindungi; tidak ada justifikasi untuk targeting |
| Afiliasi politik / data pemilih | Risiko penyalahgunaan sangat tinggi |
| Nama, alamat detail, NIK sebagai fitur numerik | Privasi + tidak bermakna prediktif |
| Foto rumah mentah ke model v1 | Kompleksitas & risiko bias tinggi; simpan sebagai **bukti verifikasi**, bukan fitur |

⚠️ Gender KK **boleh** dipakai sebagai **fitur audit fairness** (§12) tetapi masuk sebagai fitur model hanya jika ada justifikasi eksplisit yang didokumentasikan — perempuan kepala keluarga memang menghadapi risiko berbeda secara struktural, sehingga mengeluarkannya dapat justru **memperburuk** recall untuk kelompok itu ("fairness through unawareness" adalah anti-pola yang diketahui).

## 18. Model

```
BASELINE WAJIB (untuk perbandingan jujur):
  M0  Logistic regression pada 10 fitur (gaya PPI)     <- benchmark "cukup baik"
  M1  Geographic targeting: semua keluarga di pekon termiskin
                                                       <- benchmark "tanpa model"
      (mengikuti Aiken et al. yang membandingkan ke geographic blanketing)

MODEL UTAMA:
  M2  LightGBM / XGBoost, tuned via cross-validation
      + kalibrasi isotonic pada set kalibrasi terpisah
      + class weight atau focal loss (asimetri biaya FN >> FP)

EKSTENSI (v2):
  M3  M2 + spatial lag features (Z = WX antar-pekon)
      <- lihat 8.8: penurunan exclusion error hingga 8 pp
  M4  Quantile regression pada kuantil = tingkat kemiskinan
      <- Brown et al.: "poverty-quantile method dominating in most cases"

VALIDASI:
  - 5-fold stratified CV di level KELUARGA (nomor KK)
  - LEAVE-ONE-KECAMATAN-OUT   <- uji generalisasi spasial; WAJIB
  - Temporal holdout bila data multi-snapshot tersedia   <- uji drift
```

> **Laporkan M0 dan M1 di sebelah M2.** Jika M2 hanya sedikit mengalahkan M0, itu **informasi penting** — bukan kegagalan. Hanna & Olken 🟡 dan Brown et al. 🟢 sama-sama menemukan metode sederhana sering hampir sebaik metode canggih.

## 19. Kartu Metrik NADI (template dashboard)

```
+- KARTU PERFORMA MODEL - NADI Vulnerability Score v1 ----------------+
|                                                                     |
|  DISKRIMINASI                                                       |
|    AUC ....................... 0,__   (target 0,72-0,85)            |
|    Spearman rho .............. 0,__                                 |
|                                                                     |
|  PERFORMA PADA ANGGARAN NYATA   <-- METRIK UTAMA                    |
|    recall@100 ................ __%   (kapasitas 1 pendamping/bulan) |
|    recall@300 ................ __%   (kapasitas triwulanan)         |
|    recall@500 ................ __%                                  |
|    precision@300 ............. __%                                  |
|    lift@300 .................. __x    (vs pemilihan acak)           |
|    exclusion error @300 ...... __%    (= 1 - recall@300)            |
|                                                                     |
|  KALIBRASI                                                          |
|    Brier score ............... 0,___                                |
|    ECE (10 bin) .............. 0,___                                |
|    [reliability diagram]                                            |
|                                                                     |
|  FAIRNESS (Equal Opportunity Gap = maks-min recall@300)             |
|    antar kecamatan ........... __ pp   [ambang alarm: 10 pp]        |
|    urban vs rural ............ __ pp                                |
|    gender KK ................. __ pp                                |
|    kuintil ukuran keluarga ... __ pp   <- uji WAJIB (Dietrich et al)|
|                                                                     |
|  BASELINE PEMBANDING                                                |
|    Geographic targeting ...... recall@300 = __%                     |
|    Logistic 10-fitur (PPI) ... recall@300 = __%                     |
|                                                                     |
|  META                                                               |
|    Versi model / tanggal latih / hash dataset / prevalensi label    |
|    Median umur data (hari) ... ___                                  |
+---------------------------------------------------------------------+
```

## 20. Guardrail Etis (masukkan ke dokumentasi produk & UI)

| # | Guardrail | Dasar |
|---|---|---|
| 1 | **Model tidak pernah memutuskan.** Output adalah antrean prioritas verifikasi; keputusan ada di Musdes/Muskel & Dinsos | Alatas et al. 2012 🟡; alur usul-sanggah resmi 🟡 |
| 2 | **Tidak ada penghapusan otomatis** dari daftar penerima berdasarkan skor/anomali | §13.3 |
| 3 | **Setiap skor punya penjelasan bahasa manusia** yang bisa dibacakan di Musdes | Kidd & Wylde 🟢 tentang kegagalan legitimasi PMT |
| 4 | **Disclaimer non-kausal wajib** pada setiap tampilan SHAP | Kumar et al. 2020 🟡; Chen et al. 2020 🟡 |
| 5 | **Angka ditampilkan sebagai pita**, bukan desimal presisi palsu | §10.3 |
| 6 | **Bobot fitur eksak tidak dipublikasikan; daftar dimensi dipublikasikan** | Aiken et al. 🟢 (risiko gaming) vs Dietrich et al. 🟢 (transparansi) |
| 7 | **Audit dua sisi**: cari exclusion error seintensif mencari inclusion error | Brown/Ravallion/van de Walle 🟢 |
| 8 | **Dashboard fairness terlihat oleh pengguna**, bukan hanya oleh developer | Dwork et al. "fairness through awareness" via Dietrich et al. 🟢 |
| 9 | **Umur data ditampilkan** di setiap kartu keluarga | Degradasi model 🟡 |
| 10 | **Label "DATA SINTETIS — BUKAN DATA RIIL"** permanen dan mencolok pada demo | Integritas riset |

---

## 21. Daftar Pustaka

### Proxy Means Test & targeting
- Alatas, V., Banerjee, A., Hanna, R., Olken, B.A. & Tobias, J. (2012). "Targeting the Poor: Evidence from a Field Experiment in Indonesia." *American Economic Review* 102(4):1206–1240. https://economics.mit.edu/sites/default/files/publications/Targeting%20Paper%20AER%20--%20Final%20Published.pdf
- Alatas, V., Banerjee, A., Hanna, R., Olken, B.A., Purnamasari, R. & Wai-Poi, M. (2016). "Self-Targeting: Evidence from a Field Experiment in Indonesia." *Journal of Political Economy* 124(2):371–427.
- Brown, C., Ravallion, M. & van de Walle, D. (2016). "A Poor Means Test? Econometric Targeting in Africa." NBER Working Paper 22919. https://www.nber.org/system/files/working_papers/w22919/w22919.pdf 🟢 *(teks penuh diekstrak)*
- Coady, D., Grosh, M. & Hoddinott, J. (2004). *Targeting of Transfers in Developing Countries: Review of Lessons and Experience.* World Bank. https://documents1.worldbank.org/curated/en/464231468779449856/pdf/302300PAPER0Targeting0of0transfers.pdf
- Coady, D., Grosh, M. & Hoddinott, J. (2004). "Targeting Outcomes Redux." *World Bank Research Observer* 19(1):61–85. https://documents1.worldbank.org/curated/en/569401468337868966/pdf/764760JRN0Targ0Box0374379B00PUBLIC0.pdf
- Follett, L. & Henderson, H. (2022). "A Hybrid Approach to Targeting Social Assistance." arXiv:2201.01356. https://arxiv.org/pdf/2201.01356 🟢 *(teks penuh diekstrak)*
- Hanna, R. & Olken, B.A. (2018). "Universal Basic Incomes versus Targeted Transfers: Anti-Poverty Programs in Developing Countries." *Journal of Economic Perspectives* 32(4):201–226. https://www.aeaweb.org/articles?id=10.1257/jep.32.4.201
- Kidd, S. & Wylde, E. (2017). *Exclusion by Design: An Assessment of the Effectiveness of the Proxy Means Test Poverty Targeting Mechanism.* ILO ESS / Development Pathways. https://www.ilo.org/wcmsp5/groups/public/---dgreports/---integration/documents/publication/wcms_568678.pdf 🟢 *(teks penuh diekstrak)*
- DFAT Australia. "Targeting the poorest: An assessment of the proxy means test methodology." https://www.dfat.gov.au/about-us/publications/Pages/targeting-the-poorest-an-assessment-of-the-proxy-means-test-methodology
- TNP2K. *Indonesia's Unified Database for Social Protection Programmes: Management Standards.* https://www.tnp2k.go.id/downloads/indonesias-unified-database-for-social-protection-programmes-management-standards
- Yamin, J.C. (2026). "Poverty Targeting with Imperfect Information." arXiv:2506.18188.

### Kerentanan kemiskinan
- Chaudhuri, S., Jalan, J. & Suryahadi, A. (2002). *Assessing Household Vulnerability to Poverty from Cross-Sectional Data: A Methodology and Estimates from Indonesia.* Columbia University Discussion Paper 0102-52.
- Ligon, E. & Schechter, L. (2003). "Measuring Vulnerability." *The Economic Journal* 113(486):C95–C102. https://users.ssc.wisc.edu/~lschechter/vulnerability.pdf
- Ligon, E. & Schechter, L. (2002). "Measuring Vulnerability: The Director's Cut." UNU-WIDER Discussion Paper 2002/86. https://users.ssc.wisc.edu/~lschechter/directors.pdf
- Dercon, S. (2006). "Vulnerability to Poverty." CSAE WPS/2007-03. https://www.researchgate.net/profile/Stefan-Dercon/publication/46469623_Vulnerability_to_Poverty
- Pritchett, L., Suryahadi, A. & Sumarto, S. (2000). *Quantifying Vulnerability to Poverty: A Proposed Measure, with Application to Indonesia.* SMERU Working Paper. https://smeru.or.id/en/publication/quantifying-vulnerability-poverty-proposed-measure-application-indonesia
- Suryahadi, A. & Sumarto, S. (2003). "Poverty and Vulnerability in Indonesia Before and After the Economic Crisis." *Asian Economic Journal* 17(1):45–64.
- Suryahadi, A. & Sumarto, S. "The Chronic Poor, the Transient Poor, and the Vulnerable in Indonesia Before and After the Crisis." SMERU. https://media.neliti.com/media/publications/51069-EN-the-chronic-poor-the-transient-poor-and-the-vulnerable-in-indonesia-before-and-a.pdf
- ADBI (2016). *Concepts and Measurement of Vulnerability to Poverty.* ADBI Working Paper 611. https://www.adb.org/sites/default/files/publication/210526/adbi-wp611.pdf
- Rahman, A. & Wulansari, I.Y. "Kerentanan Kemiskinan: Pendugaan, Pemetaan, Penciri, dan Rekomendasi Kebijakan pada Data Sampel Kecil." *Jurnal ASKS*, Politeknik Statistika STIS. https://jurnal.stis.ac.id/index.php/jurnalasks/article/download/77/59/550 🟢 *(teks penuh diekstrak)*
- World Bank (2019). *Aspiring Indonesia — Expanding the Middle Class.* https://documents1.worldbank.org/curated/en/519991580138621024/pdf/Aspiring-Indonesia-Expanding-the-Middle-Class.pdf
- "Indonesia's poverty puzzle: Chronic vs. transient poverty dynamics." *Cogent Economics & Finance* (2023). https://www.tandfonline.com/doi/full/10.1080/23322039.2023.2267927

### Machine learning untuk penargetan
- Aiken, E., Bellue, S., Karlan, D., Udry, C. & Blumenstock, J.E. (2022). "Machine learning and phone data can improve targeting of humanitarian aid." *Nature* 603(7903):864–870. https://www.nature.com/articles/s41586-022-04484-9 · NBER WP 29070 (teks penuh): https://www.nber.org/system/files/working_papers/w29070/w29070.pdf 🟢
- Aiken, E., Bedoya, G., Blumenstock, J.E. & Coville, A. (2023). "Program targeting with machine learning and mobile phone data: Evidence from an anti-poverty intervention in Afghanistan." *Journal of Development Economics*. arXiv:2206.11400 🟢 *(teks penuh diekstrak)*
- Aiken, E., Ohlenburg, T. & Blumenstock, J.E. (2023). "Moving targets: When does a poverty prediction model need to be updated?" COMPASS '23. DOI 10.1145/3588001.3609369
- McBride, L. & Nichols, A. (2018). "Retooling Poverty Targeting Using Out-of-Sample Validation and Machine Learning." *World Bank Economic Review* 32(3):531–550. https://academic.oup.com/wber/article-abstract/32/3/531/2447896
- Sohnesen, T.P. & Stender, N. (2017). "Is Random Forest a Superior Methodology for Predicting Poverty? An Empirical Assessment." *Poverty & Public Policy*. World Bank WPS 7612. https://openknowledge.worldbank.org/entities/publication/a7fd997c-1162-52c9-8c5b-5a47c1e8513d/full
- Jean, N., Burke, M., Xie, M., Davis, W.M., Lobell, D.B. & Ermon, S. (2016). "Combining satellite imagery and machine learning to predict poverty." *Science* 353(6301):790–794. https://www.science.org/doi/10.1126/science.aaf7894
- Gonzales Martinez, R. & Cooray, M. (2025). "Enhancing Poverty Targeting with Spatial Machine Learning: An application to Indonesia." arXiv:2503.04300. https://arxiv.org/html/2503.04300 🟢
- Kshirsagar, V., Wieczorek, J., Ramanathan, S. & Wells, R. (2017). "Household poverty classification in data-scarce environments: a machine learning approach." NIPS 2017. arXiv:1711.06813 🟢 *(teks penuh diekstrak)*
- Okamura, Y., Ohlenburg, T. & Tesliuc, E. (2024). *Scaling Up Social Assistance Where Data is Scarce — Opportunities and Limits of Novel Data and AI.* World Bank. https://documents.worldbank.org/en/publication/documents-reports/documentdetail/099050824132537925
- Fischer-Abaigar, U., Kern, C. & Perdomo, J.C. (2025). "The Value of Prediction in Identifying the Worst-Off." arXiv:2501.19334
- World Bank. *SWIFT (Survey of Well-being via Instant and Frequent Tracking).* https://documents1.worldbank.org/curated/en/099850407092448908/pdf/IDU-b116cf02-f30e-4d87-96f7-06fdca4cb242.pdf
- Poverty Probability Index. https://www.povertyindex.org/ · Indonesia: https://www.povertyindex.org/country/indonesia

### Fairness, kalibrasi, explainability
- Dietrich, S., Malerba, D. & Gassmann, F. (2024). "Predicting social assistance beneficiaries: On the social welfare damage of data biases." *Data & Policy* 6:e3. DOI 10.1017/dap.2023.38 🟢 *(teks penuh diekstrak; Open Access CC-BY)*
- Kumar, I.E., Venkatasubramanian, S., Scheidegger, C. & Friedler, S. (2020). "Problems with Shapley-value-based explanations as feature importance measures." ICML 2020. arXiv:2002.11097
- Chen, H., Janizek, J.D., Lundberg, S. & Lee, S.-I. (2020). "True to the Model or True to the Data?" arXiv:2006.16234
- Lundberg, S.M. et al. (2020). "From local explanations to global understanding with explainable AI for trees." *Nature Machine Intelligence* 2:56–67.
- Wachter, S., Mittelstadt, B. & Russell, C. (2017). "Counterfactual Explanations Without Opening the Black Box: Automated Decisions and the GDPR."
- Karimi, A.-H., von Kügelgen, J., Schölkopf, B. & Valera, I. "Algorithmic Recourse: from Counterfactual Explanations to Interventions."
- "Is calibration a fairness requirement?" FAccT 2022. https://facctconference.org/static/pdfs_2022/facct22-3533245.pdf
- Molnar, C. *Interpretable Machine Learning*, Bab 18 (SHAP). https://christophm.github.io/interpretable-ml-book/shap.html
- Fairlearn documentation. https://fairlearn.org/
- "Using Platt's scaling for calibration after undersampling — limitations and how to address them." arXiv:2410.18144

### Anomaly detection
- Liu, F.T., Ting, K.M. & Zhou, Z.-H. (2008). "Isolation Forest." ICDM 2008.
- Liu, F.T., Ting, K.M. & Zhou, Z.-H. (2012). "Isolation-Based Anomaly Detection." *ACM TKDD* 6(1). https://dl.acm.org/doi/10.1145/2133360.2133363
- Breunig, M.M., Kriegel, H.-P., Ng, R.T. & Sander, J. (2000). "LOF: Identifying Density-Based Local Outliers." SIGMOD.
- scikit-learn IsolationForest. https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html

### Data sintetis
- Jeong, B. et al. (2016). "Copula-Based Approach to Synthetic Population Generation." *PLOS ONE* 11(8):e0159496. https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0159496
- Li, Z. et al. (2019). "SynC: A Unified Framework for Generating Synthetic Population with Gaussian Copula." arXiv:1904.07998
- Patki, N., Wedge, R. & Veeramachaneni, K. "The Synthetic Data Vault." https://sdv.dev/
- "A Comparative Study of Open-Source Libraries for Synthetic Tabular Data Generation: SDV vs. SynthCity." arXiv:2506.17847

### Sumber Indonesia (resmi & pemberitaan)
- BPS. "DTSEN Jadi Rujukan Bersama, BPS Jelaskan Arti Desil" (22 Agustus 2026). https://www.bps.go.id/en/news/2026/08/22/938/dtsen-jadi-rujukan-bersama--bps-jelaskan-arti-desil.html *(WebFetch 403; isi diperoleh via Kompas/CNN/Detik yang mengutip)*
- BPS. "Understanding the Differences in Poverty Rates Reported by the World Bank and Statistics Indonesia (BPS)" (2 Mei 2025). https://www.bps.go.id/en/news/2025/05/02/702/ *(WebFetch 403)*
- BPS. "Persentase Penduduk Miskin September 2025 turun menjadi 8,25 persen." https://www.bps.go.id/id/pressrelease/2026/02/05/2536/
- BPS Provinsi Lampung. https://lampung.bps.go.id/
- BPS Kabupaten Pringsewu — tabel indikator SDG 1.2.1. https://pringsewukab.bps.go.id/id/statistics-table/2/NjQzIzI=/
- Ombudsman RI. "Problematika Bantuan Sosial dan DTKS." https://ombudsman.go.id/artikel/r/pwkinternal--problematika-bantuan-sosial-dan-dtks
- Kemenpan RB. "Kemensos Hentikan 55 Ribu Penerima Bansos Anomali." https://www.menpan.go.id/site/berita-terkini/berita-daerah/kemensos-hentikan-55-ribu-penerima-bansos-anomali
- Indonesia.go.id. "Benahi DTKS, 21 Juta Data Penerima Bansos Dipangkas." https://indonesia.go.id/kategori/editorial/2838/benahi-dtks-21-juta-data-penerima-bansos-dipangkas
- SMERU. "Miskin Menurut Siapa? Solusi Menaikkan Garis Kemiskinan Indonesia." https://smeru.or.id/id/article-id/miskin-menurut-siapa-solusi-menaikkan-garis-kemiskinan-indonesia
- SMERU. "Inequality, Elite Capture, and Targeting of Social Protection." https://smeru.or.id/sites/default/files/publication/inequalitytargeting.pdf

---

## 22. Yang TIDAK Berhasil Ditemukan (jujur — jangan diisi asal)

| # | Yang dicari | Status | Catatan |
|---|---|---|---|
| 1 | **Tingkat kemiskinan & garis kemiskinan Kabupaten Pringsewu** | ✅ **DITEMUKAN** (di dokumen lain) | Tidak berhasil diambil dalam riset **ini** (tabel SDG 1.2.1 BPS Pringsewu gagal difetch), **tetapi tersedia lengkap & terverifikasi di `03-profil-pringsewu.md`**: P0 7,60% (2025) / 8,32% (2024); GK Rp583.425 (2024). Section §7.2 & §15.2 sudah diperbarui memakai angka tersebut. |
| 2 | **Jumlah pekon & kecamatan Pringsewu** | ✅ **DITEMUKAN** (di dokumen lain) | **9 kecamatan, 126 pekon, 5 kelurahan** — lihat `03-profil-pringsewu.md` (catatan: 126, **bukan** 128). |
| 3 | **Bobot/koefisien PMT DTSEN yang eksak** | 🔴 | Tidak dipublikasikan — konsisten dengan temuan Dietrich et al. 🟢 bahwa hanya 1 dari 10 program mempublikasikan bobot PMT lengkap. Daftar **dimensi** variabel berhasil dikonfirmasi. |
| 4 | **Enumerasi eksplisit 13 variabel individu + 25 variabel keluarga DTSEN** | 🔴 | Klaim ini muncul di `01-skema-data-dtsen.md`; riset ini hanya berhasil mengonfirmasi **dimensi**, bukan enumerasi bernomor. Perlu verifikasi silang ke lampiran Peraturan BPS 6/2025. |
| 5 | **Angka degradasi akurasi PMT per tahun** (Aiken/Ohlenburg/Blumenstock 2023) | 🔴 | ACM DL 403; OpenReview terkunci verifikasi browser. Temuan kualitatif ("menurun terus, 6 negara") terkonfirmasi. |
| 6 | **Angka perbaikan spesifik McBride & Nichols (2018)** | 🔴 | WBER berbayar; abstrak tidak memuat angka. |
| 7 | **Isi World Bank "Scaling Up Social Assistance Where Data is Scarce" (2024)** | 🔴 | PDF 7,1 MB gagal di-parse. URL terkonfirmasi & tersedia untuk pengambilan manual. |
| 8 | **Halaman TNP2K "Unifikasi Sistem Penetapan Sasaran Nasional"** | 🔴 | `connect ECONNREFUSED` — server tidak dapat dijangkau saat riset. |
| 9 | **Angka exclusion/inclusion error resmi PKH/BPNT versi SMERU** | 🟠 | Ditemukan angka sekunder (leakage 17–23% dari total pengeluaran; 47,81% responden setuju tidak semua keluarga miskin menerima) tetapi **bukan dari publikasi SMERU primer**. Jangan kutip sebagai angka SMERU. |
| 10 | **Komposisi chronic vs transient poverty Indonesia yang disepakati** | 🟠 | Lima studi memberi angka bertentangan (18,89% – 77%). Lihat §14.2. Laporkan sebagai rentang dengan catatan metodologis. |
| 11 | **Rasio train/test di Gonzales Martinez & Cooray (2025)** | 🟠 | Paper menyebut "80% test, 20% training" — kemungkinan salah tulis. Angka EE tetap dilaporkan tetapi ditandai. |
| 12 | **Publikasi Ohlenburg di IZA tentang targeting** | 🔴 | Tidak ditemukan. Karya Ohlenburg yang relevan ada di World Bank (2024) dan COMPASS (2023). |
| 13 | **Data panel DTSEN antar-snapshot** (untuk label L3) | 🔴 | Belum tersedia publik; DTSEN diperbarui triwulanan sejak 2025. |

---

*Dokumen ini adalah riset sekunder + ekstraksi sumber primer. Semua angka bertanda 🟢 diekstrak langsung dari teks penuh PDF sumber. Angka bertanda 🟡 berasal dari abstrak/ringkasan/pemberitaan dan harus diverifikasi sebelum dipublikasikan. **Tidak ada angka dalam dokumen ini yang dikarang.***
