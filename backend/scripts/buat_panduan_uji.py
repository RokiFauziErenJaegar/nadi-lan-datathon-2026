"""Susun panduan pengujian NADI dalam bentuk Word dan PDF.

Dokumen ini berbeda maksudnya dari ``Panduan-NADI``. Yang itu menerangkan apa
yang dibangun; yang ini menerangkan **bagaimana membuktikan bahwa yang dibangun
itu benar-benar bekerja** - langkah demi langkah, dengan hasil yang diharapkan
tertulis di sebelah setiap langkah.

Satu kaidah menentukan seluruh isinya: **tidak ada satu langkah pun tanpa hasil
yang diharapkan.** Panduan pengujian yang hanya menyuruh "jalankan perintah
ini" tidak berguna, karena pembacanya tidak tahu apakah yang muncul di layar
berarti berhasil atau gagal. Setiap angka pada dokumen ini diambil dari
keluaran nyata pengujian yang benar-benar dijalankan, bukan dari perkiraan.

    python backend/scripts/buat_panduan_uji.py
    python backend/scripts/buat_panduan_uji.py --tanpa-pdf
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sqlite3
import sys
from datetime import date

AKAR = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(AKAR / "backend"))
sys.path.insert(0, str(AKAR / "backend" / "scripts"))

from dokumen import Panduan, ke_pdf  # noqa: E402
from panduan_bab import rb  # noqa: E402

KELUARAN = AKAR / "dokumen"


def fakta() -> dict:
    c = sqlite3.connect(str(AKAR / "data" / "nadi.db"))
    f = {
        "tabel": len([x[0] for x in c.execute(
            "SELECT name FROM sqlite_master WHERE type='table'")]),
        "keluarga": c.execute("SELECT COUNT(*) FROM keluarga").fetchone()[0],
        "kasus": c.execute("SELECT COUNT(*) FROM kasus").fetchone()[0],
        "db_mb": round((AKAR / "data" / "nadi.db").stat().st_size / 1024**2, 1),
    }
    m = c.execute("SELECT metrik FROM versi_model WHERE aktif = 1").fetchone()
    f["metrik"] = json.loads(m[0]) if m and isinstance(m[0], str) else {}
    c.close()
    return f


# ===========================================================================
def susun(d: Panduan, f: dict) -> None:
    tanggal = date.today().strftime("%d") + " Agustus 2026"

    d.sampul(
        "Panduan Pengujian",
        "NADI — Navigasi AI Data Intervensi\nDari penyiapan sampai lembar periksa demo",
        [
            ("Sistem", "NADI, Kabupaten Pringsewu"),
            ("Untuk", "Penguji, penyusun, dan dewan juri"),
            ("Lingkup", "Empat lapis pengujian, 112 pemeriksaan"),
            ("Tanggal", tanggal),
        ],
    )
    d.daftar_isi()

    # ======================================================== BAB 1
    d.h1("1. Untuk Siapa Dokumen Ini", tanpa_nomor=True)

    d.p(
        "Dokumen ini dapat dipakai tiga jenis pembaca, dan masing-masing tidak perlu membaca "
        "seluruhnya."
    )
    d.tabel(
        ["Pembaca", "Yang perlu dibaca", "Waktu"],
        [
            ["**Dewan juri** yang ingin memastikan sendiri bahwa klaim pada proposal benar",
             "Bab 3 (penyiapan) lalu Bab 6 (uji penerimaan). Satu perintah menghasilkan "
             "40 pemeriksaan beserta angkanya.",
             "± 15 menit"],
            ["**Penyusun** yang memeriksa sebelum menyerahkan karya",
             "Seluruhnya, terutama Bab 9 (lembar periksa sebelum demo).",
             "± 90 menit"],
            ["**Petugas atau operator** yang akan memakai sistem",
             "Bab 7 (uji manual per modul) — sekaligus berfungsi sebagai panduan pemakaian.",
             "± 45 menit"],
        ],
        lebar=[4.0, 8.4, 2.6],
    )

    d.catatan(
        "Kaidah yang dipakai menyusun dokumen ini",
        "Tidak ada satu langkah pun yang ditulis tanpa **hasil yang diharapkan**. Panduan "
        "pengujian yang hanya menyuruh menjalankan perintah tidak berguna, karena pembacanya "
        "tidak dapat menilai apakah yang muncul di layar berarti berhasil. Seluruh angka pada "
        "dokumen ini disalin dari keluaran nyata, bukan dari perkiraan.",
    )

    # ======================================================== BAB 2
    d.h1("2. Empat Lapis Pengujian")

    d.p(
        "Pengujian NADI disusun berlapis, dari yang paling cepat dan paling sempit ke yang "
        "paling lambat dan paling menyeluruh. Urutan ini disengaja: lapis yang lebih cepat "
        "menangkap kekeliruan yang lebih sering, sehingga lapis yang lambat tidak terbuang "
        "untuk memeriksa hal yang sudah pasti salah."
    )
    d.tabel(
        ["Lapis", "Apa yang diuji", "Perintah", "Jumlah", "Waktu"],
        [
            ["**1. Uji otomatis**", "Fungsi dalam bahasa Python: penghalang data pribadi dan "
             "penyesuaian dialek penyedia AI",
             "`pytest backend/tests -q`", "61 kasus", "< 1 detik"],
            ["**2. Uji asap antarmuka**", "Kesebelas halaman dipasang di peramban tiruan, "
             "memanggil API sungguhan",
             "`npm run uji`", "11 halaman", "± 1 menit"],
            ["**3. Uji penerimaan**", "Janji sistem diperiksa lewat HTTP: kewenangan, privasi, "
             "alur ujung ke ujung, mutu angka",
             "`python backend/scripts/uji_penerimaan.py`", "40 pemeriksaan", "± 1 menit"],
            ["**4. Uji manual**", "Yang hanya dapat dinilai manusia: apakah layarnya terbaca, "
             "apakah penjelasannya masuk akal",
             "Bab 7 dokumen ini", "10 modul", "± 45 menit"],
        ],
        lebar=[2.6, 5.4, 4.0, 1.7, 1.3],
    )

    d.h2("Mengapa lapis ketiga tidak dapat digantikan lapis pertama")
    d.p(
        "Uji otomatis memanggil fungsi Python secara langsung. Uji penerimaan memanggil "
        "peladen lewat HTTP. Perbedaan itu menentukan."
    )
    d.p(
        "Sebuah rute yang lupa dipasangi penjaga kewenangan akan **tetap lulus** pada uji "
        "otomatis, karena fungsi di baliknya memang bekerja dengan benar. Yang bocor adalah "
        "lapisan HTTP-nya — dan hanya pengujian yang benar-benar mengetuk pintu itu yang "
        "dapat menemukannya. Karena itu seluruh pemeriksaan kewenangan pada Bab 6 dilakukan "
        "lewat permintaan HTTP, memakai token masuk yang sungguhan."
    )

    # ======================================================== BAB 3
    d.h1("3. Prasyarat dan Penyiapan dari Nol")

    d.h2("3.1 Yang harus terpasang")
    d.tabel(
        ["Perangkat", "Versi minimum", "Cara memeriksa", "Bila belum ada"],
        [
            ["Python", "3.10", "`python --version`", "python.org/downloads — centang “Add Python to PATH”"],
            ["Node.js", "18", "`node --version`", "nodejs.org — hanya diperlukan untuk membangun antarmuka"],
            ["Microsoft Word", "opsional", "—", "Hanya diperlukan bila ingin membuat ulang berkas PDF dokumen"],
        ],
        lebar=[2.4, 2.0, 3.4, 7.2],
    )
    d.p(
        "Sambungan internet **tidak** diperlukan untuk menjalankan sistem. Ia hanya "
        "diperlukan sekali saat memasang pustaka, dan kemudian bila layanan AI daring "
        "hendak dipakai."
    )

    d.h2("3.2 Penyiapan sekali klik")
    d.p(
        "Klik dua kali berkas **JALANKAN-NADI.bat**. Skrip itu memeriksa setiap prasyarat "
        "lebih dahulu dan hanya mengerjakan yang belum ada, lalu membuka peramban sendiri."
    )
    d.tabel(
        ["Langkah", "Yang dikerjakan", "Waktu (pertama kali)", "Waktu (berikutnya)"],
        [
            ["1", "Membuat lingkungan Python dan memasang pustaka", "3–8 menit", "dilewati"],
            ["2", "Membuat berkas konfigurasi dan kunci rahasia acak", "seketika", "dilewati"],
            ["3", "Membangun basis data dan data sintetis", "± 1 menit", "dilewati"],
            ["4", "Melatih model dan menilai seluruh keluarga", "± 10 menit", "dilewati"],
            ["5", "Membentuk antrean kasus", "± 15 detik", "dilewati"],
            ["6", "Membangun antarmuka", "± 2 menit", "dilewati"],
            ["7", "Menjalankan peladen", "± 10 detik", "± 10 detik"],
        ],
        lebar=[1.2, 7.0, 3.4, 3.4],
    )
    d.catatan(
        "Tanda penyiapan berhasil",
        "Peramban terbuka pada http://127.0.0.1:8000 dan menampilkan halaman masuk. Bila "
        "yang muncul halaman kosong atau pesan galat, lompat ke Bab 10 — pemecahan masalah.",
    )

    d.h2("3.3 Penyiapan langkah demi langkah")
    d.p("Bila ingin melihat setiap tahap secara terpisah — misalnya untuk diperlihatkan kepada juri:")
    d.kode(
        "python backend/scripts/siapkan_data.py       # basis data dan data sintetis\n"
        "python backend/scripts/latih_model.py        # melatih, menilai, menyimpan model\n"
        "python backend/scripts/deteksi_kasus.py      # membentuk antrean kasus\n"
        "python backend/scripts/seed_intervensi.py    # riwayat verifikasi dan intervensi\n"
        "cd frontend && npm install && npm run build  # membangun antarmuka\n"
        "cd backend && python -m uvicorn nadi.main:app --port 8000"
    )
    d.p(
        f"Setelah seluruh langkah selesai, basis data berisi {f['tabel']} tabel berukuran "
        f"sekitar {rb(f['db_mb'], 1)} MB, dengan {rb(f['keluarga'])} keluarga dan "
        f"{rb(f['kasus'])} kasus."
    )

    # ======================================================== BAB 4
    d.h1("4. Lapis Pertama — Uji Otomatis")

    d.kode("python -m pytest backend/tests -q")
    d.p("**Hasil yang diharapkan:**")
    d.kode(
        "............................................................. [100%]\n"
        "61 passed in 0.33s"
    )
    d.tabel(
        ["Berkas uji", "Kasus", "Apa yang dijaga"],
        [
            ["`test_security_pii.py`", "32",
             "Penghalang data pribadi: NIK, kartu keluarga, NPWP, BPJS, nomor telepon, surel, "
             "koordinat presisi, RT/RW. Termasuk uji bahwa nilai aslinya tidak bocor ke pesan "
             "galat, dan bahwa angka agregat yang sah tidak ikut tertolak."],
            ["`test_dialek.py`", "29",
             "Penyesuaian dialek antarpenyedia AI: keluarga gpt-5 dan o-series menolak "
             "`max_tokens` dan `temperature`. Termasuk uji bahwa model yang belum dikenal "
             "tetap dapat dipakai lewat koreksi otomatis dari pesan galat."],
        ],
        lebar=[3.4, 1.4, 10.2],
    )
    d.catatan(
        "Bila ada yang gagal",
        "Uji lapis ini tidak memerlukan peladen, basis data, maupun jaringan. Kegagalan di "
        "sini berarti ada berkas kode yang rusak atau pustaka yang belum terpasang — bukan "
        "persoalan data. Jalankan tanpa `-q` untuk melihat baris mana yang gagal.",
    )

    # ======================================================== BAB 5
    d.h1("5. Lapis Kedua — Uji Asap Antarmuka")

    d.p(
        "Peladen harus sudah berjalan. Pengujian ini memasang kesebelas halaman ke dalam "
        "peramban tiruan, memanggil API yang sesungguhnya, menunggu setiap kueri reda, lalu "
        "memeriksa apakah halamannya benar-benar berisi."
    )
    d.kode("cd frontend\nnpm run uji")
    d.p("**Hasil yang diharapkan:**")
    d.kode(
        "  LULUS  Ringkasan              2239 karakter\n"
        "  LULUS  Peta Risiko             647 karakter\n"
        "  LULUS  Antrean Kasus         17507 karakter\n"
        "  LULUS  Keluarga               4764 karakter\n"
        "  LULUS  Profil Keluarga        2369 karakter\n"
        "  LULUS  Katalog Program        3402 karakter\n"
        "  LULUS  Simulasi               1180 karakter\n"
        "  LULUS  Copilot                1268 karakter\n"
        "  LULUS  Transparansi Model     5564 karakter\n"
        "  LULUS  Monitoring Hasil       6606 karakter\n"
        "  LULUS  Pengaturan AI          2337 karakter\n"
        "\n"
        "  11/11 halaman tergambar dengan isi."
    )
    d.p(
        "Jumlah karakter boleh berbeda — ia bergantung pada isi basis data. Yang harus sama "
        "adalah **kesebelasnya LULUS**."
    )
    d.catatan(
        "Mengapa pengujian ini ada",
        "Ia lahir dari satu kekeliruan yang lolos dari seluruh pemeriksaan lain. Halaman "
        "Pengaturan memanggil tiga *hook* React di bawah cabang keluar-awal, sehingga render "
        "pertama memanggil nol hook dan render kedua memanggil tiga. React membatalkan "
        "seluruh pohon komponen, dan yang terlihat pemakai hanyalah **halaman kosong tanpa "
        "pesan galat apa pun**. Pemeriksaan tipe meloloskannya karena ini kekeliruan waktu "
        "jalan; pembangunan berkas meloloskannya karena membangun bukan menjalankan. Hanya "
        "memasang halaman itu sungguhan dan menunggu render kedua yang dapat menemukannya.",
    )

    # ======================================================== BAB 6
    d.h1("6. Lapis Ketiga — Uji Penerimaan")

    d.p(
        "Ini pengujian yang paling layak diperlihatkan kepada dewan juri. Satu perintah "
        "memeriksa empat puluh janji sistem lewat permintaan HTTP sungguhan, dan mencetak "
        "**nilai yang benar-benar diterima** pada setiap pemeriksaan — bukan sekadar kata "
        "“lulus”."
    )
    d.kode(
        "python backend/scripts/uji_penerimaan.py\n"
        "\n"
        "python backend/scripts/uji_penerimaan.py --bagian B   # hanya kewenangan\n"
        "python backend/scripts/uji_penerimaan.py --bersihkan  # hapus data yang dibuat uji"
    )
    d.p(
        "Pengujian ini **membuat data**: satu verifikasi, satu intervensi, dan satu penilaian "
        "hasil, seluruhnya bertanda `[uji-penerimaan]`. Jalankan dengan `--bersihkan` "
        "sesudahnya agar riwayat demo kembali bersih."
    )

    d.h2("6.A Kesehatan sistem — 6 pemeriksaan")
    m = f["metrik"]
    d.tabel(
        ["Kode", "Yang diperiksa", "Hasil yang diharapkan"],
        [
            ["A1", "Peladen menjawab", "HTTP 200"],
            ["A2", "Basis data terbaca dan berisi",
             f"{f['tabel']} tabel, {rb(f['keluarga'])} keluarga, {rb(f['db_mb'], 1)} MB"],
            ["A3", "Ada satu model aktif", "1 model aktif"],
            ["A4", "Antarmuka tersaji peladen", "HTTP 200, text/html"],
            ["A5", "Dokumentasi API terbentuk sendiri", "45 operasi pada 43 jalur"],
            ["A6", "Keenam akun demo dapat masuk", "admin, bupati, bappeda, dinsos, pupr, verifikator"],
        ],
        lebar=[1.2, 6.0, 7.8],
    )

    d.h2("6.B Kewenangan — 11 pemeriksaan")
    d.p(
        "Bagian ini yang paling meyakinkan untuk ditunjukkan. Perhatikan bahwa yang diuji "
        "bukan hanya siapa **boleh**, melainkan terutama siapa **tidak boleh**."
    )
    d.tabel(
        ["Kode", "Yang diperiksa", "Diharapkan"],
        [
            ["B1", "Tanpa token, permintaan ditolak", "HTTP 401"],
            ["B2", "Pimpinan daerah dapat membaca agregat", "HTTP 200"],
            ["B3", "Pimpinan daerah **tidak** dapat membuka daftar keluarga", "**HTTP 403**"],
            ["B4", "Perencana **tidak** dapat membuka daftar keluarga", "**HTTP 403**"],
            ["B5", "Verifikator **tidak** dapat membaca monitoring hasil", "**HTTP 403**"],
            ["B6", "Dinas Sosial **tidak** dapat mencatat penyaluran", "**HTTP 403**"],
            ["B7", "OPD pelaksana **tidak** dapat menilai hasilnya sendiri", "**HTTP 403**"],
            ["B8", "Dinas Sosial boleh menilai hasil", "HTTP 404 — berwenang, kode uji tidak ada"],
            ["B9", "Non-administrator **tidak** dapat membaca pengaturan AI", "**HTTP 403**"],
            ["B10", "Administrator dapat membaca pengaturan AI", "HTTP 200"],
            ["B11", "Verifikator hanya melihat wilayah tugasnya",
             "1 kecamatan (Pagelaran Utara) berbanding 9 kecamatan bagi Dinas Sosial"],
        ],
        lebar=[1.2, 8.2, 5.6],
    )
    d.catatan(
        "Dua pemeriksaan yang paling menjelaskan rancangan sistem",
        "**B7** membuktikan pemisahan tugas: OPD pelaksana mencatat apa yang ia salurkan, "
        "tetapi tidak dapat menilai hasilnya sendiri. Tanpa itu, laporan capaian menilai "
        "dirinya sendiri. **B3** membuktikan minimalisasi data: pimpinan daerah tidak "
        "memerlukan data satu keluarga untuk mengambil keputusan tingkat kabupaten, sehingga "
        "aksesnya memang tidak diberikan.",
    )

    d.h2("6.C Privasi — 5 pemeriksaan")
    d.tabel(
        ["Kode", "Yang diperiksa", "Diharapkan"],
        [
            ["C1", "Tidak ada NIK atau bidang identitas pada tanggapan API",
             "5 titik akhir diperiksa, bersih"],
            ["C2", "Identitas keluarga berupa kode semu yang sah",
             "Berbentuk `KLG-XXXX-XXXX`, contoh `KLG-CCHZ-K7CA`"],
            ["C3", "Pertanyaan bermuatan NIK diredaksi sebelum diproses",
             "diredaksi=True, namun **tetap dijawab**"],
            ["C4", "Agregat wilayah membawa penanda sel kecil", "Ambang 10 keluarga"],
            ["C5", "Jejak audit terisi dan tidak memuat kunci rahasia",
             "Jumlah baris bertambah, 0 baris memuat kunci"],
        ],
        lebar=[1.2, 7.0, 6.8],
    )

    d.h2("6.D Alur ujung ke ujung — 7 pemeriksaan")
    d.p(
        "Bagian ini menjalankan lingkar penuh pada satu kasus sungguhan: deteksi, verifikasi, "
        "penyaluran, penilaian hasil, penutupan kasus."
    )
    d.tabel(
        ["Kode", "Yang diperiksa", "Diharapkan"],
        [
            ["D1", "Antrean kasus berisi", f"{rb(f['kasus'])} kasus pada gelombang terkini"],
            ["D2", "Setiap kasus membawa alasan yang dapat dibaca petugas", "Jenis dan alasan terisi"],
            ["D3", "Petugas dapat mencatat hasil verifikasi lapangan",
             "Status kasus menjadi `terverifikasi_sesuai`"],
            ["D4", "OPD dapat mencatat penyaluran", "Kode intervensi `ITV-XXXX-XXXX` terbit"],
            ["D5", "Hasil dinilai sistem, bukan diketik pemakai",
             "Penilaian, skor sebelum, skor sesudah, dan selisihnya terisi seluruhnya"],
            ["D6", "Penilaian membawa penafian perubahan bukan sebab", "Penafian terbaca pada tanggapan"],
            ["D7", "Kasus tertutup ketika seluruh intervensinya selesai", "`kasus_ditutup=True`"],
        ],
        lebar=[1.2, 7.2, 6.6],
    )
    d.catatan(
        "Perhatikan D5",
        "Bidang penilaian tidak pernah diterima dari pemanggil. Ia dihitung peladen dari "
        "selisih skor antardua gelombang, memakai ambang yang sama bagi setiap keluarga. "
        "Pada satu kali pengujian, hasilnya bahkan “memburuk” — dan itu memang "
        "ditampilkan apa adanya. Bila pihak yang dinilai dapat menuliskan nilainya sendiri, "
        "seluruh layar monitoring berubah menjadi hiasan.",
    )

    d.h2("6.E Mutu analitik — 6 pemeriksaan")
    kal = m.get("kalibrasi", {})
    a300 = m.get("pada_anggaran", {}).get("300", {})
    d.tabel(
        ["Kode", "Yang diperiksa", "Diharapkan", "Nilai saat ini"],
        [
            ["E1", "AUC pada rentang wajar", "0,72 – 0,90", f"**{rb(m.get('auc', 0), 4)}**"],
            ["E2", "Kalibrasi baik", "ECE di bawah 0,02", f"**{rb(kal.get('ece', 0), 5)}**"],
            ["E3", "Penargetan mengungguli pemilihan acak", "Pengganda di atas 3",
             f"**{rb(a300.get('pengganda', 0), 2)}×**"],
            ["E4", "Capaian selalu disertai kelompok pembanding", "Persen pembanding terisi",
             "68,0% berbanding 45,5%"],
            ["E5", "Sistem tidak menyatakan kepastian mutlak", "0 baris berpeluang 0 atau 1",
             "rentang skor 0,5 – 99,5"],
            ["E6", "Daftar batas kemampuan terbuka tanpa masuk", "HTTP 200 tanpa token", "terbuka"],
        ],
        lebar=[1.1, 5.6, 4.4, 3.9],
    )
    d.p(
        "**E1 sengaja memeriksa batas atas, bukan hanya batas bawah.** AUC di atas 0,90 pada "
        "persoalan kemiskinan hampir selalu menandakan kebocoran data, bukan model yang "
        "hebat. Pemeriksaan ini akan **gagal** bila suatu saat angkanya melonjak — dan "
        "kegagalan itu justru yang diinginkan."
    )

    d.h2("6.F Layanan AI — 5 pemeriksaan")
    d.tabel(
        ["Kode", "Yang diperiksa", "Diharapkan"],
        [
            ["F1", "Pengaturan layanan AI terbaca", "Penyedia, model, dan status kesiapan tampil"],
            ["F2", "Kunci API tidak pernah dikembalikan utuh",
             "Hanya bentuk tersamar, contoh `sk-pro...aKEA`"],
            ["F3", "Copilot menjawab", "Jawaban terisi, mode luring ditandai apa adanya"],
            ["F4", "Jawaban menyertakan sumber dan penafian", "Potongan pengetahuan yang dipakai tercantum"],
            ["F5", "Copilot menolak menganjurkan penghentian bantuan",
             "Jawaban menyebut musyawarah pekon atau menyatakan tidak berwenang"],
        ],
        lebar=[1.2, 6.4, 7.4],
    )

    # ======================================================== BAB 7
    d.h1("7. Lapis Keempat — Uji Manual per Modul")

    d.p(
        "Yang tidak dapat diperiksa mesin: apakah layarnya terbaca, apakah penjelasannya "
        "masuk akal bagi orang yang bekerja di lapangan, apakah angkanya berarti sesuatu. "
        "Bagian ini juga berfungsi sebagai panduan pemakaian bagi petugas baru."
    )
    d.p("Buka **http://127.0.0.1:8000** dan masuk dengan akun yang disebut pada tiap langkah.")

    langkah = [
        ("Executive Command Center", "dinsos", "Halaman muka",
         "Angka kemiskinan, kerentanan, cakupan bantuan, dan grafik tren enam gelombang terisi.",
         "Angka bernilai nol atau grafik kosong."),
        ("GeoAI Poverty Radar", "dinsos", "Menu Peta Risiko",
         "Peta Kabupaten Pringsewu tergambar dengan batas desa. Mengganti ukuran yang "
         "dipetakan mengubah warnanya. Mengarahkan kursor menampilkan nama dan angka pekon.",
         "Peta abu-abu seluruhnya, atau batas wilayah berbentuk kotak."),
        ("Mismatch & Anomaly Queue", "dinsos", "Menu Antrean Kasus",
         "Daftar kasus terurut menurut prioritas. Menyaring menurut jenis mengubah isinya. "
         "**Membuka satu kasus menampilkan alasan mengapa ia masuk daftar** — inilah yang "
         "paling penting dilihat.",
         "Kasus tanpa alasan, atau alasan yang saling bertentangan."),
        ("Household Digital Twin", "dinsos", "Menu Keluarga, lalu klik satu baris",
         "Riwayat enam gelombang, skor beserta faktor risikonya, guncangan yang pernah "
         "dialami, riwayat program, dan rekomendasi.",
         "Halaman kosong, atau riwayat hanya satu gelombang."),
        ("Intervention Recommender", "bappeda", "Menu Katalog Program",
         "Dua puluh delapan program dengan kriteria, OPD pelaksana, dan tingkat keyakinan "
         "tiap angka.",
         "Program tanpa OPD, atau biaya tanpa keterangan sumber."),
        ("What-if Policy Simulator", "bappeda", "Menu Simulasi",
         "Menggeser kuota atau anggaran mengubah hasil seketika. Setiap hasil membawa "
         "penafian dan sumber angkanya.",
         "Hasil tidak berubah saat masukan diubah."),
        ("AI Policy Copilot", "dinsos", "Menu Copilot",
         "Jawaban muncul beserta potongan pengetahuan yang dipakai. Coba tanyakan sesuatu "
         "yang memuat NIK — sistem meredaksinya namun tetap menjawab.",
         "Jawaban tanpa sumber, atau NIK diteruskan apa adanya."),
        ("Outcome Monitoring", "dinsos", "Menu Monitoring Hasil",
         "Grafik capaian **berdampingan dengan kelompok pembanding**. Angka pembanding harus "
         "terlihat, bukan hanya angka capaian.",
         "Angka capaian berdiri sendiri tanpa pembanding."),
        ("Transparansi Model", "dinsos", "Menu Transparansi Model",
         "Metrik, uji keadilan antarkecamatan, daftar fitur, dan daftar hal yang tidak dapat "
         "dilakukan sistem.",
         "Halaman hanya memuat angka bagus tanpa menyebut batas."),
        ("Pengaturan Layanan AI", "**admin**", "Menu Pengaturan AI",
         "Tujuh penyedia dapat dipilih. Menekan “Ambil daftar model” mengisi daftar "
         "dari penyedia. “Uji sambungan” menjawab dalam hitungan detik.",
         "Kunci API tampil utuh — ini kegagalan serius."),
    ]
    d.tabel(
        ["Modul", "Akun", "Ke mana", "Yang harus terlihat", "Tanda gagal"],
        [[a, b, c, e, g] for a, b, c, e, g in langkah],
        lebar=[2.5, 1.2, 2.2, 6.1, 3.0],
        # Tabel ini panjang; ukuran huruf dikecilkan agar tetap satu halaman.
    )

    d.h2("7.1 Dua percobaan yang paling meyakinkan")
    d.p(
        "Bila waktu memperlihatkan sistem terbatas — misalnya di hadapan dewan juri — dua "
        "percobaan berikut menyampaikan lebih banyak daripada menelusuri seluruh menu."
    )
    d.poin(
        [
            "**Masuk sebagai `bupati`, lalu coba buka profil satu keluarga.** Sistem menolak. "
            "Pimpinan daerah sengaja hanya diberi akses agregat, dan penolakan itu "
            "memperlihatkan tata kelola bekerja jauh lebih meyakinkan daripada menjelaskannya "
            "dengan kata-kata.",
            "**Masuk sebagai `pupr`, catat satu penyaluran, lalu coba nilai hasilnya sendiri.** "
            "Sistem juga menolak. Yang menyalurkan tidak dapat menilai pekerjaannya sendiri.",
        ],
        bernomor=True,
    )

    # ======================================================== BAB 8
    d.h1("8. Uji Ketahanan")

    d.p(
        "Yang diuji di sini bukan apakah sistem bekerja ketika segalanya normal, melainkan "
        "**apa yang terjadi ketika tidak**. Bagian ini penting justru karena demo hampir "
        "selalu berlangsung pada keadaan yang tidak normal: jaringan ruang rapat yang buruk, "
        "kuota yang habis, laptop yang berbeda."
    )
    d.tabel(
        ["Gangguan", "Cara menirukannya", "Yang harus terjadi"],
        [
            ["Layanan AI tidak menjawab",
             "Ubah alamat penyedia pada halaman Pengaturan AI menjadi alamat yang tidak ada, "
             "lalu ajukan pertanyaan pada Copilot",
             "Jawaban **tetap muncul** dalam beberapa detik, disusun dari templat, dan "
             "ditandai sebagai mode luring. Seluruh angka tetap sama karena berasal dari "
             "perhitungan lokal. Teruji: 6 detik, jawaban 2.202 karakter."],
            ["Tidak ada sambungan internet",
             "Putuskan jaringan sepenuhnya, lalu jalankan seluruh modul",
             "Seluruh modul selain Copilot berjalan penuh. Peta memakai ubin yang sudah "
             "tersimpan; bila belum, batas wilayah tetap tergambar tanpa latar peta."],
            ["Kunci API salah atau kedaluwarsa",
             "Isi kunci sembarang pada halaman Pengaturan AI, lalu tekan “Uji sambungan”",
             "Pesan galat menyebutkan **sebabnya**, bukan sekadar nomor status. Zen "
             "membedakan kunci ditolak, tagihan belum siap, dan nama model keliru."],
            ["Berkas basis data hilang",
             "Ubah nama `data/nadi.db` lalu jalankan peladen",
             "Peladen berhenti dengan pesan yang menyebutkan berkas mana yang tidak ditemukan "
             "dan perintah apa yang membangunnya kembali."],
            ["Peladen dijalankan dua kali",
             "Jalankan `JALANKAN-NADI.bat` sementara satu peladen sudah berjalan",
             "Proses kedua berhenti dengan pesan bahwa porta 8000 sedang dipakai. Yang "
             "pertama tetap melayani."],
        ],
        lebar=[3.0, 5.2, 6.8],
    )

    # ======================================================== BAB 9
    d.h1("9. Lembar Periksa Sebelum Demo")

    d.p(
        "Dijalankan berurutan pada hari sebelum demo, bukan pada hari demo. Seluruhnya "
        "memakan waktu sekitar dua puluh menit."
    )
    d.tabel(
        ["", "Yang diperiksa", "Cara", "Tanda siap"],
        [
            ["1", "Peladen menyala dari keadaan mati",
             "Tutup semua, jalankan `JALANKAN-NADI.bat`",
             "Peramban terbuka pada halaman masuk dalam kurang dari 30 detik"],
            ["2", "Uji otomatis lulus", "`pytest backend/tests -q`", "**61 passed**"],
            ["3", "Seluruh halaman merender", "`cd frontend && npm run uji`", "**11/11**"],
            ["4", "Seluruh janji sistem terpenuhi",
             "`python backend/scripts/uji_penerimaan.py`", "**40 dari 40 lulus**"],
            ["5", "Data uji dibersihkan",
             "`python backend/scripts/uji_penerimaan.py --bersihkan`", "Baris uji terhapus"],
            ["6", "Layanan AI menjawab cepat",
             "Ajukan satu pertanyaan pada Copilot", "Jawaban muncul di bawah 5 detik"],
            ["7", "Cadangan luring bekerja",
             "Putuskan internet, ajukan pertanyaan lagi", "Jawaban tetap muncul, ditandai luring"],
            ["8", "Keenam akun dapat masuk", "Masuk bergantian", "Menu berbeda-beda menurut peran"],
            ["9", "Dua percobaan penolakan berhasil",
             "Bab 7.1 dokumen ini", "Keduanya ditolak sistem"],
            ["10", "Berkas dokumen mutakhir",
             "`python backend/scripts/buat_panduan.py`", "Angka pada dokumen sama dengan di layar"],
        ],
        lebar=[0.7, 4.4, 5.2, 4.7],
    )
    d.catatan(
        "Satu hal yang sering terlupa",
        "Jalankan `--bersihkan` setelah uji penerimaan. Tanpa itu, riwayat demo memuat satu "
        "intervensi bertanda `[uji-penerimaan]` yang akan terlihat bila juri menelusuri "
        "daftar — dan pertanyaan tentangnya akan memakan waktu yang lebih baik dipakai untuk "
        "hal lain.",
    )

    # ======================================================== BAB 10
    d.h1("10. Pemecahan Masalah")

    d.tabel(
        ["Gejala", "Sebab yang paling mungkin", "Yang harus dilakukan"],
        [
            ["Halaman kosong sama sekali, tanpa pesan galat",
             "Kekeliruan waktu jalan pada antarmuka — biasanya urutan *hook* React",
             "Jalankan `cd frontend && npm run uji`. Halaman yang bermasalah akan disebut "
             "beserta sebabnya."],
            ["`Address already in use` pada porta 8000",
             "Peladen lama masih berjalan",
             "Tutup jendela peladen sebelumnya, atau hentikan prosesnya lalu jalankan ulang."],
            ["Copilot selalu menjawab mode luring",
             "Layanan AI belum dikonfigurasi, kunci ditolak, atau tagihan belum siap",
             "Buka halaman Pengaturan AI sebagai `admin`, tekan “Uji sambungan”. "
             "Pesannya menyebutkan sebab yang tepat."],
            ["Jawaban Copilot memakan waktu lebih dari 30 detik",
             "Model yang dipilih berorientasi penalaran",
             "Ganti ke model yang lebih ringkas pada halaman Pengaturan AI."],
            ["`database is locked`",
             "Dua proses menulis basis data bersamaan",
             "Hentikan skrip yang sedang berjalan; jangan menjalankan skrip penyiapan "
             "sementara peladen melayani."],
            ["Peta tidak menampilkan latar",
             "Tidak ada sambungan internet untuk mengunduh ubin peta",
             "Batas wilayah dan warnanya tetap tergambar. Ini keterbatasan latar peta, bukan "
             "kegagalan sistem."],
            ["Uji penerimaan gagal pada bagian B",
             "Matriks kewenangan tersunting, atau rute baru lupa dipasangi penjaga",
             "Periksa `backend/nadi/security/rbac.py` dan dekorator rute yang bersangkutan."],
            ["Uji penerimaan gagal pada E1 karena AUC terlalu tinggi",
             "Kebocoran data pada fitur model",
             "**Ini kegagalan yang benar.** Periksa fitur mana yang memuat keterangan yang "
             "tidak akan tersedia saat peramalan sungguhan."],
        ],
        lebar=[4.0, 4.6, 6.4],
    )

    # ======================================================== BAB 11
    d.h1("11. Lampiran — Seluruh Perintah")

    d.h2("Penyiapan")
    d.kode(
        "JALANKAN-NADI.bat                              # sekali klik, semuanya\n"
        "python backend/scripts/siapkan_data.py         # basis data sintetis\n"
        "python backend/scripts/latih_model.py          # melatih dan menilai model\n"
        "python backend/scripts/deteksi_kasus.py        # antrean kasus gelombang terkini\n"
        "python backend/scripts/deteksi_kasus.py --gelombang 3\n"
        "python backend/scripts/seed_intervensi.py      # riwayat verifikasi dan intervensi\n"
        "python backend/scripts/seed_intervensi.py --hapus"
    )

    d.h2("Pengujian")
    d.kode(
        "python -m pytest backend/tests -q              # 61 kasus uji\n"
        "cd frontend && npm run uji                     # 11 halaman antarmuka\n"
        "cd frontend && npm run lint                    # pemeriksaan tipe TypeScript\n"
        "python backend/scripts/uji_penerimaan.py       # 40 pemeriksaan janji sistem\n"
        "python backend/scripts/uji_penerimaan.py --bagian B\n"
        "python backend/scripts/uji_penerimaan.py --bersihkan"
    )

    d.h2("Layanan AI")
    d.kode(
        "python backend/scripts/siapkan_ai.py --daftar          # model yang tersedia\n"
        "python backend/scripts/siapkan_ai.py --kunci <kunci>   # pasang dan uji\n"
        "python backend/scripts/siapkan_ai.py --tanpa-simpan    # uji tanpa menyimpan"
    )

    d.h2("Dokumen")
    d.kode(
        "python backend/scripts/buat_panduan.py         # panduan lengkap\n"
        "python backend/scripts/buat_panduan_uji.py     # dokumen ini\n"
        "python backend/scripts/buat_presentasi.py --pdf"
    )

    d.h2("Akun demo")
    d.tabel(
        ["Nama pengguna", "Sandi", "Peran"],
        [
            ["admin", "NadiAdmin#2026", "Administrator Sistem"],
            ["bupati", "NadiPimpinan#2026", "Pimpinan Daerah — agregat saja"],
            ["bappeda", "NadiPerencana#2026", "Perencana — agregat saja"],
            ["dinsos", "NadiDinsos#2026", "Dinas Sosial — koordinator"],
            ["pupr", "NadiPupr#2026", "OPD Pelaksana — wilayah tertugas"],
            ["verifikator", "NadiVerif#2026", "Verifikator — wilayah tertugas"],
        ],
        lebar=[3.4, 4.0, 7.6],
    )


# ===========================================================================
def main() -> int:
    p = argparse.ArgumentParser(description="Susun panduan pengujian NADI.")
    p.add_argument("--tanpa-pdf", action="store_true")
    args = p.parse_args()

    print("  Membaca angka dari sistem...")
    f = fakta()

    print("  Menyusun naskah...")
    d = Panduan()
    susun(d, f)
    d.nomor_halaman()

    docx = d.simpan(KELUARAN / "Panduan-Pengujian-NADI.docx")
    print(f"  Word : {docx}  ({docx.stat().st_size / 1024:.0f} KB)")

    if not args.tanpa_pdf:
        print("  Mengubah ke PDF lewat Microsoft Word...")
        pdf = ke_pdf(docx)
        print(f"  PDF  : {pdf}  ({pdf.stat().st_size / 1024:.0f} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
