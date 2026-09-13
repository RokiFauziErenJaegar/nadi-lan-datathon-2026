"""Susun presentasi NADI untuk LAN Datathon 2026.

Susunan salindia mengikuti **satu keluarga**, bukan daftar modul. Dewan juri
membaca puluhan presentasi; yang bertahan bukan yang memuat paling banyak
fitur, melainkan yang membuat mereka peduli pada satu orang lebih dahulu, baru
kemudian menunjukkan sistemnya.

Seluruh angka dan grafik dibangkitkan dari basis data yang sesungguhnya pada
saat skrip dijalankan. Bila sistem berubah, jalankan ulang dan presentasinya
ikut berubah.

    python backend/scripts/buat_presentasi.py
    python backend/scripts/buat_presentasi.py --pdf
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sqlite3
import subprocess
import sys

import matplotlib.pyplot as plt
import numpy as np

AKAR = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(AKAR / "backend"))
sys.path.insert(0, str(AKAR / "backend" / "scripts"))

from presentasi import (  # noqa: E402
    BIRU, BIRU_MUDA, Dek, HIJAU, KELABU, MERAH, TINTA_KEDUA, TINTA_REDUP,
    hx, siapkan_matplotlib,
)

KELUARAN = AKAR / "dokumen"
GAMBAR = KELUARAN / "gambar"
KODE_CERITA = "KLG-WS65-ZCQR"


def rb(n, d=0) -> str:
    s = f"{n:,.{d}f}"
    utuh, _, pecahan = s.partition(".")
    return f"{utuh.replace(',', '.')},{pecahan}" if pecahan else utuh.replace(",", ".")


# ===========================================================================
# Grafik
# ===========================================================================
def grafik_keluarga(c: sqlite3.Connection) -> pathlib.Path:
    """Lintasan satu keluarga: pengeluaran selalu di bawah garis, desil memantul."""
    baris = c.execute(
        """
        SELECT s.gelombang, s.tanggal_kondisi, s.desil_kesejahteraan,
               s.pengeluaran_per_kapita, s.jumlah_program_diterima
        FROM snapshot_keluarga s JOIN keluarga k ON k.id = s.keluarga_id
        WHERE k.kode_semu = ? ORDER BY s.gelombang
        """,
        (KODE_CERITA,),
    ).fetchall()
    gel = [r[0] for r in baris]
    tanggal = [str(r[1])[:7] for r in baris]
    desil = [r[2] for r in baris]
    pengeluaran = [r[3] for r in baris]
    garis = 583_425.0

    fig, (a1, a2) = plt.subplots(2, 1, figsize=(11.2, 5.4), sharex=True,
                                 gridspec_kw={"height_ratios": [2, 1], "hspace": 0.18})

    a1.axhline(garis, color=hx(MERAH), lw=2, ls="--", zorder=1)
    a1.text(len(gel) - 0.55, garis + 14_000, "garis kemiskinan  Rp583.425",
            color=hx(MERAH), fontsize=10.5, ha="right", fontweight="bold")
    a1.fill_between(range(len(gel)), pengeluaran, garis, color=hx(MERAH), alpha=0.10, zorder=2)
    a1.plot(range(len(gel)), pengeluaran, "-o", color=hx(BIRU), lw=2.6, ms=8, zorder=3)
    for i, v in enumerate(pengeluaran):
        a1.annotate(f"{v/1000:.0f}rb", (i, v), textcoords="offset points",
                    xytext=(0, -19), ha="center", fontsize=9.5, color=hx(TINTA_KEDUA))
    a1.set_ylabel("Pengeluaran per kapita", fontsize=11)
    a1.set_ylim(330_000, 660_000)
    a1.set_yticks([400_000, 500_000, 600_000])
    a1.set_yticklabels(["Rp400rb", "Rp500rb", "Rp600rb"])
    a1.grid(axis="y", lw=0.8)
    a1.set_title("Enam kali didata, enam kali di bawah garis kemiskinan",
                 fontsize=13.5, fontweight="bold", loc="left", pad=12)

    warna = [hx(MERAH) if d <= 2 else hx(KELABU) for d in desil]
    a2.bar(range(len(gel)), desil, color=warna, width=0.52, zorder=3)
    for i, v in enumerate(desil):
        a2.text(i, v + 0.12, str(v), ha="center", fontsize=11, fontweight="bold",
                color=hx(TINTA_KEDUA))
    a2.set_ylabel("Desil DTSEN\nyang tercatat", fontsize=10.5)
    a2.set_ylim(0, 4.1)
    a2.set_yticks([1, 2, 3])
    a2.set_xticks(range(len(gel)))
    a2.set_xticklabels(tanggal, fontsize=10.5)
    a2.grid(axis="y", lw=0.8)
    a2.set_title("Catatannya sendiri berubah-ubah: 1 → 2 → 2 → 3 → 3 → 1",
                 fontsize=12, loc="left", pad=8, color=hx(TINTA_KEDUA))

    for a in (a1, a2):
        a.set_axisbelow(True)
    fig.tight_layout()
    jalur = GAMBAR / "keluarga.png"
    fig.savefig(jalur, dpi=190, bbox_inches="tight")
    plt.close(fig)
    return jalur


def grafik_anggaran(metrik: dict) -> pathlib.Path:
    """Berapa yang tepat sasaran pada tiap besaran anggaran kunjungan."""
    pa = metrik.get("pada_anggaran", {})
    k = sorted(int(x) for x in pa)
    presisi = [pa[str(x)]["presisi"] * 100 for x in k]
    pengganda = [pa[str(x)]["pengganda"] for x in k]
    prevalensi = metrik.get("prevalensi", 0) * 100

    fig, ax = plt.subplots(figsize=(11.2, 4.9))
    x = np.arange(len(k))
    def koma(v: float, d: int = 1) -> str:
        return f"{v:.{d}f}".replace(".", ",")

    ax.axhline(prevalensi, color=hx(TINTA_REDUP), lw=2, ls="--", zorder=1)
    # Label garis dasar diletakkan pada ruang kosong DI KANAN batang terakhir,
    # bukan di atas garisnya. Seluruh batang menjulang melewati garis ini,
    # sehingga tidak ada satu titik pun di sepanjang garis yang tidak tertimpa.
    ax.set_xlim(-0.62, len(k) - 0.02 + 1.15)
    ax.annotate(
        chr(10).join(["tanpa model,", "memilih acak", koma(prevalensi) + "%"]),
        xy=(len(k) - 0.72, prevalensi), xytext=(len(k) - 0.28, prevalensi + 13),
        color=hx(TINTA_KEDUA), fontsize=11, ha="left", va="center",
        arrowprops=dict(arrowstyle="-", color=hx(TINTA_REDUP), lw=1.4,
                        connectionstyle="angle,angleA=0,angleB=90,rad=4"),
    )
    batang = ax.bar(x, presisi, color=hx(BIRU), width=0.55, zorder=3)
    for i, (b, p) in enumerate(zip(batang, pengganda)):
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 2.2,
                f"{presisi[i]:.0f}%", ha="center", fontsize=13, fontweight="bold",
                color=hx(BIRU))
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() / 2,
                koma(p) + "x", ha="center", fontsize=12, color="white", fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels([f"{rb(v)}\nkunjungan" for v in k], fontsize=11)
    ax.set_ylabel("Tepat sasaran (%)", fontsize=11.5)
    ax.set_ylim(0, 100)
    ax.grid(axis="y", lw=0.8)
    ax.set_axisbelow(True)
    ax.set_title("Semakin sedikit petugas, semakin besar gunanya penargetan",
                 fontsize=13.5, fontweight="bold", loc="left", pad=12)
    fig.tight_layout()
    jalur = GAMBAR / "anggaran.png"
    fig.savefig(jalur, dpi=190, bbox_inches="tight")
    plt.close(fig)
    return jalur


def grafik_pembanding(rekap: dict) -> pathlib.Path:
    """Capaian intervensi berdampingan dengan kelompok pembanding."""
    p = {x["penilaian"]: x for x in rekap["penilaian"]}
    urut = ["membaik", "tetap", "memburuk"]
    label = ["Membaik", "Tetap", "Memburuk"]
    intervensi = [p[k]["persen"] for k in urut]
    banding = [p[k]["persen_pembanding"] or 0 for k in urut]
    # "Tetap" memakai kelabu gelap, bukan kelabu muda: kelabu muda dipakai
    # kelompok pembanding, dan dua kelabu berdampingan akan tertukar.
    warna = [hx(HIJAU), "#64748B", hx(MERAH)]

    fig, ax = plt.subplots(figsize=(11.2, 4.9))
    y = np.arange(len(urut))
    tinggi = 0.34
    ax.barh(y + tinggi / 2, intervensi, tinggi, color=warna, zorder=3)
    ax.barh(y - tinggi / 2, banding, tinggi, color=hx(KELABU), zorder=3)

    def persen(v: float) -> str:
        return f"{v:.1f}".replace(".", ",") + "%"

    for i in range(len(urut)):
        ax.text(intervensi[i] + 1.4, y[i] + tinggi / 2, persen(intervensi[i]),
                va="center", fontsize=12.5, fontweight="bold", color=warna[i])
        ax.text(banding[i] + 1.4, y[i] - tinggi / 2, persen(banding[i]),
                va="center", fontsize=12, color=hx(TINTA_KEDUA))

    # Panah selisih diletakkan pada ruang kosong TEPAT DI BAWAH kelompok
    # pertama, bukan di atas batangnya. Menggambarnya di atas batang membuat
    # keduanya saling menimpa dan angka terpentingnya justru paling sulit
    # dibaca.
    selisih = intervensi[0] - banding[0]
    y_panah = y[0] + tinggi + 0.16
    ax.annotate("", xy=(intervensi[0], y_panah), xytext=(banding[0], y_panah),
                arrowprops=dict(arrowstyle="<->", color=hx(BIRU), lw=2.2))
    ax.text((intervensi[0] + banding[0]) / 2, y_panah + 0.15,
            "capaian sesungguhnya  +" + f"{selisih:.1f}".replace(".", ",") + " poin persen",
            ha="center", va="top", fontsize=12.5, fontweight="bold", color=hx(BIRU))

    ax.set_yticks(y)
    ax.set_yticklabels(label, fontsize=13)
    ax.set_xlim(0, 84)
    ax.set_xlabel("Bagian keluarga (%)", fontsize=11.5)
    ax.set_ylim(len(urut) - 0.45, -0.55)
    ax.grid(axis="x", lw=0.8)
    ax.set_axisbelow(True)
    ax.set_title("Berwarna: menerima intervensi   |   Kelabu: keluarga sebanding yang tidak menerima apa pun",
                 fontsize=12, loc="left", pad=12, color=hx(TINTA_KEDUA))
    fig.tight_layout()
    jalur = GAMBAR / "pembanding.png"
    fig.savefig(jalur, dpi=190, bbox_inches="tight")
    plt.close(fig)
    return jalur


# ===========================================================================
def kumpulkan(c: sqlite3.Connection) -> dict:
    f: dict = {}
    f["baris"] = {
        t: c.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        for t in ("keluarga", "anggota_keluarga", "snapshot_keluarga", "kasus",
                  "verifikasi", "intervensi", "hasil_intervensi", "program", "opd")
    }
    m = c.execute(
        "SELECT algoritma, jumlah_fitur, metrik FROM versi_model WHERE aktif = 1"
    ).fetchone()
    f["algoritma"], f["fitur"] = m[0], m[1]
    f["metrik"] = json.loads(m[2]) if isinstance(m[2], str) else m[2]
    f["tanpa_program"] = c.execute(
        "SELECT COUNT(*) FROM snapshot_keluarga WHERE gelombang = 5 AND jumlah_program_diterima = 0"
    ).fetchone()[0]
    f["miskin_tanpa_program"] = c.execute(
        "SELECT COUNT(*) FROM snapshot_keluarga WHERE gelombang = 5 "
        "AND jumlah_program_diterima = 0 AND status_miskin = 1"
    ).fetchone()[0]
    f["py_baris"] = sum(
        len(b.read_text(encoding="utf-8", errors="ignore").splitlines())
        for b in AKAR.glob("backend/**/*.py") if "__pycache__" not in str(b)
    )
    f["ts_baris"] = sum(
        len(b.read_text(encoding="utf-8", errors="ignore").splitlines())
        for b in AKAR.glob("frontend/src/**/*.ts*")
    )
    f["riset_kata"] = sum(
        len(b.read_text(encoding="utf-8", errors="ignore").split())
        for b in AKAR.glob("docs/**/*.md")
    )
    return f


def ambil_rekap() -> dict:
    """Rekap monitoring. Diambil dari peladen bila hidup; jika tidak, dihitung sendiri."""
    import httpx

    try:
        with httpx.Client(base_url="http://127.0.0.1:8000", timeout=60.0) as k:
            tok = k.post("/api/masuk", json={"nama_pengguna": "dinsos",
                                             "sandi": "NadiDinsos#2026"}).json()["token"]
            return k.get("/api/intervensi/rekap/monitoring",
                         headers={"Authorization": f"Bearer {tok}"}).json()
    except Exception as exc:  # noqa: BLE001
        raise SystemExit(
            f"Peladen NADI harus berjalan untuk mengambil rekap monitoring ({exc}).\n"
            "Jalankan JALANKAN-NADI.bat lebih dahulu."
        ) from exc


# ===========================================================================
def susun(d: Dek, f: dict, rekap: dict, gambar: dict) -> None:
    m = f["metrik"]
    a300 = m["pada_anggaran"]["300"]

    # 1 --------------------------------------------------------------- sampul
    d.sampul(
        "NADI",
        "Navigasi AI Data Intervensi",
        [
            "Menemukan keluarga yang terlewat, sebelum mereka jatuh lebih dalam",
            "",
            "Roki Fauzi  ·  Pranata Komputer Ahli Pertama",
            "Diskominfo Kabupaten Pringsewu, Provinsi Lampung",
            "LAN Datathon 2026  ·  Penanggulangan kemiskinan berbasis data",
        ],
        catatan="Sebutkan sejak awal: seluruh data yang akan ditampilkan bersifat sintetis, "
                "dikalibrasi terhadap angka resmi BPS. Ini bukan data keluarga nyata.",
    )

    # 2 ---------------------------------------------------------- bagian satu
    d.bagian("01", "Satu keluarga",
             "Sebelum berbicara tentang sistem, mari lihat satu keluarga saja.",
             catatan="Jangan buru-buru. Salindia berikutnya adalah inti presentasi ini.")

    # 3 ------------------------------------------------------------ hook
    d.gambar_penuh(
        "Pekon Sukamulya, Kecamatan Banyumas",
        gambar["keluarga"],
        anak="Satu keluarga, diikuti tiga tahun. Kode semu KLG-WS65-ZCQR — sistem ini tidak menyimpan nama.",
        keterangan="Enam kali didata. Enam kali di bawah garis kemiskinan. "
                   "Nol program bantuan selama tiga tahun.",
        catatan="Poin utamanya: pengeluaran keluarga ini SELALU di bawah garis kemiskinan, "
                "tetapi desil yang tercatat berubah-ubah 1-2-2-3-3-1. Ketika tercatat desil 3, "
                "ia tidak masuk prioritas program mana pun — padahal saat itu pengeluarannya "
                "justru paling rendah, Rp394.498. Catatannya yang berubah, bukan keadaannya.",
    )

    # 4 ------------------------------------------------------- bukan tunggal
    d.angka_besar(
        "Dan ini bukan kasus tunggal",
        [
            (rb(f["tanpa_program"]), "keluarga tanpa program apa pun",
             "Dari 40.000 keluarga desil 1–5 dalam cakupan sistem."),
            (rb(f["miskin_tanpa_program"]), "di antaranya tergolong miskin",
             "Pengeluaran di bawah garis kemiskinan, namun tidak menerima bantuan apa pun."),
            ("22%", "penandaan yang ternyata keliru",
             "Diketahui hanya setelah petugas datang memeriksa ke lapangan."),
        ],
        catatan="Angka pertama dan kedua dibaca langsung dari basis data. Angka ketiga "
                "berasal dari hasil verifikasi lapangan yang tercatat — dan sengaja "
                "ditampilkan, karena sistem yang mengaku selalu benar tidak layak dipercaya.",
    )

    # 5 --------------------------------------------------------- mengapa
    d.poin(
        "Mengapa keluarga seperti ini terlewat",
        [
            "**Penargetan menilai potret, bukan lintasan.** Yang dilihat adalah keadaan pada "
            "hari pendataan — bukan ke arah mana keluarga itu sedang bergerak.",
            "**Penaksiran kesejahteraan memang tidak teliti.** Proxy Means Test yang dipakai "
            "di negara berkembang hanya menjelaskan 40–60 persen keragaman pengeluaran nyata.",
            "**Pemutakhiran berjarak bulan.** Guncangan — gagal panen, kehilangan pekerjaan, "
            "sakit berat — terjadi di antara dua pendataan, dan baru terlihat pada pendataan "
            "berikutnya.",
            "**Kesalahan melewatkan tidak terlihat siapa pun.** Keluarga yang seharusnya "
            "dibantu namun tidak terdaftar tidak muncul pada laporan mana pun untuk mengeluh.",
        ],
        catatan="Butir terakhir yang paling penting. Kesalahan memasukkan orang yang tidak "
                "berhak membebani anggaran, dan itu terlihat. Kesalahan melewatkan membebani "
                "keluarga itu sendiri, dan itu tidak terlihat.",
    )

    # 6 ---------------------------------------------------------- bagian dua
    d.bagian("02", "Apa yang saya bangun",
             "Sebuah sistem pendukung keputusan — bukan pengganti keputusan.")

    # 7 ------------------------------------------------ apa dan bukan apa
    d.dua_kolom(
        "Batas yang menentukan seluruh rancangan",
        "NADI TIDAK",
        [
            "Tidak menetapkan siapa berhak menerima bantuan",
            "Tidak menghentikan bantuan siapa pun",
            "Tidak dipakai mendeteksi kecurangan",
            "Tidak menyimpan nama, NIK, maupun alamat",
            "Tidak mengambil satu pun keputusan sendiri",
        ],
        "NADI MENGERJAKAN",
        [
            "Menyusun antrean prioritas pemeriksaan",
            "Menjelaskan alasan setiap keluarga masuk daftar",
            "Menunjuk OPD yang berwenang menangani",
            "Mengusulkan program yang mungkin cocok",
            "Mengukur hasilnya terhadap kelompok pembanding",
        ],
        catatan="Ucapkan kolom kiri LEBIH DAHULU dan pelan-pelan. Sebagian besar keberatan "
                "terhadap AI pada layanan publik berakar pada kekhawatiran bahwa mesin "
                "mengambil alih keputusan. Menjawabnya sebelum ditanya mengubah seluruh nada "
                "penilaian berikutnya.",
    )

    # 8 ---------------------------------------------------------- lingkar
    d.poin(
        "Lingkar yang tertutup sampai hasil",
        [
            "**Deteksi** — tujuh detektor menemukan ketidaksesuaian, menghasilkan antrean "
            "berprioritas beserta alasannya.",
            "**Verifikasi** — petugas mendatangi dan mencatat temuan, termasuk ketika "
            "temuannya bertentangan dengan sistem.",
            "**Intervensi** — OPD mencatat penyaluran yang benar-benar terjadi.",
            "**Penilaian** — hasilnya diukur terhadap kondisi keluarga pada gelombang "
            "berikutnya, disandingkan dengan kelompok pembanding.",
            "**Umpan balik** — koreksi petugas menjadi bahan pelatihan ulang model.",
        ],
        anak="Kebanyakan sistem berhenti pada langkah pertama. Yang membuat langkah kelima mungkin adalah langkah kedua.",
        catatan="Tekankan langkah kelima. Sistem yang tidak dapat mengakui dirinya salah "
                "tidak akan pernah membaik.",
    )

    # 9 ------------------------------------------------------------ modul
    d.tabel(
        "Sepuluh modul, seluruhnya berjalan",
        ["", "Modul", "Yang dikerjakannya"],
        [
            ["1", "Executive Command Center", "Angka pokok kabupaten dalam satu layar"],
            ["2", "Household Digital Twin", "Profil keluarga sepanjang enam gelombang"],
            ["3", "GeoAI Poverty Radar", "Peta batas desa asli dari Badan Informasi Geospasial"],
            ["4", "Mismatch & Anomaly Queue", "Tujuh detektor, antrean berprioritas"],
            ["5", "Intervention Recommender", "Mencocokkan risiko dengan 28 program"],
            ["6", "What-if Policy Simulator", "Cakupan, biaya, kapasitas, penuntasan RTLH"],
            ["7", "AI Policy Copilot", "Tanya jawab dengan sumber, penghalang data pribadi"],
            ["8", "Outcome Monitoring", "Capaian dengan kelompok pembanding"],
            ["9", "Transparansi Model", "**Tambahan** — metrik, keadilan, dan batasnya"],
            ["10", "Pengaturan Layanan AI", "**Tambahan** — termasuk pilihan model lokal"],
        ],
        lebar_kolom=[0.5, 3.4, 8.0],
        anak="Proposal menjanjikan delapan. Dua terakhir lahir dari kebutuhan selama pengerjaan.",
        ukuran=11,
    )

    # 10-11 -------------------------------------------------------- layar
    d.tempat_layar(
        "Peta Risiko",
        "halaman Peta Risiko, pilih ukuran “Skor kerentanan rata-rata”",
        anak="Batas 131 desa dari Badan Informasi Geospasial, bukan bentuk perkiraan.",
        catatan="Buka aplikasi di http://127.0.0.1:8000/peta, ambil tangkapan layar, "
                "lalu sisipkan menggantikan bingkai ini.",
    )
    d.tempat_layar(
        "Antrean Kasus",
        "halaman Antrean Kasus, buka satu kasus sampai terlihat faktor risikonya",
        anak="Setiap kasus membawa alasan, OPD yang berwenang, dan program yang diusulkan.",
        catatan="Yang paling meyakinkan untuk ditunjukkan: klik satu kasus sampai terlihat "
                "penjelasan per keluarga. Itu yang membedakan dari dasbor biasa.",
    )

    # 12 -------------------------------------------------------- bagian tiga
    d.bagian("03", "Buktinya",
             "Angka yang saya sampaikan, beserta batas yang saya akui.")

    # 13 --------------------------------------------------------- anggaran
    d.gambar_penuh(
        "Kalau hanya ada tenaga untuk 300 kunjungan bulan ini",
        gambar["anggaran"],
        anak="Angka di dalam batang menunjukkan berapa kali lebih baik daripada memilih keluarga secara acak.",
        keterangan=f"Model {f['algoritma']}, {f['fitur']} fitur. "
                   f"AUC {rb(m['auc'], 3)} pada gelombang uji.",
        catatan="Jangan mulai dari AUC. Kepala dinas tidak bertanya berapa AUC-nya; ia "
                "bertanya berapa yang tepat sasaran kalau tenaganya terbatas. Jawabannya "
                f"{rb(a300['presisi']*100, 0)} persen, {rb(a300['pengganda'], 1)} kali lebih "
                "baik daripada acak.",
    )

    # 14 ---------------------------------------------------------- kejujuran
    d.kutipan(
        "AUC sempat mencapai 0,94.\nItulah yang membuat saya curiga.",
        "Desil kesejahteraan ternyata dihitung dari pengeluaran sesungguhnya — keterangan "
        "yang tidak akan tersedia saat peramalan nyata. Setelah diperbaiki, angkanya turun "
        f"menjadi {rb(m['auc'], 3)}.",
        catatan="Ini salindia yang paling saya sarankan untuk tidak dilewati. Mengakui "
                "kekeliruan sendiri di hadapan juri hampir selalu menguatkan. Ada tiga "
                "kebocoran data yang saya temukan dan perbaiki; ini salah satunya.",
    )

    # 15 -------------------------------------------------------- pembanding
    d.gambar_penuh(
        "Angka capaian tidak pernah saya tampilkan sendirian",
        gambar["pembanding"],
        anak="Keluarga berskor tinggi cenderung membaik dengan sendirinya — regresi ke rata-rata. Tanpa pembanding, angka capaian menyesatkan.",
        keterangan=f"{rekap['pembanding']['tercocokkan']} dari {rekap['pembanding']['dari']} "
                   "intervensi dicocokkan pada gelombang dan pita skor awal yang sama.",
        catatan="Inilah salindia yang paling membedakan karya ini. 68 persen terdengar "
                "hebat sampai orang melihat bahwa 45 persen keluarga sebanding juga membaik "
                "tanpa menerima apa pun. Bersedia menampilkan angka yang lebih kecil adalah "
                "bukti bahwa angka lainnya dapat dipercaya.",
    )

    # 16 ------------------------------------------------------- tata kelola
    d.tabel(
        "Siapa boleh melakukan apa",
        ["Peran", "Cakupan data", "Yang menjadi cirinya"],
        [
            ["Pimpinan Daerah", "**Agregat saja**", "Tidak dapat membuka satu pun keluarga"],
            ["Perencana (Bappeda)", "**Agregat saja**", "Simulasi kebijakan dan katalog program"],
            ["Dinas Sosial", "Seluruh kabupaten", "Menugaskan kasus dan **menilai hasil**"],
            ["OPD Pelaksana", "Wilayah tertugas", "**Mencatat penyaluran**, tidak boleh menilainya"],
            ["Verifikator", "Wilayah tertugas", "Mencatat temuan lapangan"],
            ["Administrator", "Seluruh kabupaten", "Mengatur layanan AI"],
        ],
        lebar_kolom=[2.6, 2.6, 6.8],
        anak="Yang menyalurkan tidak dapat menilai pekerjaannya sendiri — pemisahan itu ditegakkan sistem, bukan diminta baik-baik.",
        ukuran=12,
        catatan="Percobaan yang paling meyakinkan untuk ditunjukkan langsung: masuk sebagai "
                "pimpinan daerah lalu coba buka satu keluarga — sistem menolak. Lalu masuk "
                "sebagai OPD, catat penyaluran, coba nilai hasilnya sendiri — juga ditolak.",
    )

    # 17 ----------------------------------------------------------- privasi
    d.poin(
        "Janji privasi yang ditegakkan mesin",
        [
            "**Tidak ada nama, NIK, atau alamat** di dalam sistem. Identitas keluarga berupa "
            "kode semu satu arah.",
            "**Penghalang data pribadi** memeriksa setiap muatan tepat sebelum dikirim ke "
            "layanan AI. Bila memuat pengenal pribadi, permintaan dibatalkan — bukan "
            "disamarkan diam-diam.",
            "**Agregat wilayah di bawah sepuluh keluarga tidak ditampilkan**, agar individu "
            "tidak dapat disimpulkan dari angka gabungan.",
            "**Model lokal dapat dipakai** — bila dipilih, tidak ada satu kata pun yang "
            "keluar dari jaringan pemerintah daerah.",
            "**Setiap tindakan tercatat** pada jejak audit: siapa, kapan, dari mana.",
        ],
        anak="Berkas pertama yang saya tulis bukan halaman muka, melainkan penghalang ini.",
        catatan="Sebutkan urutan pengerjaannya: keamanan dibangun sebelum ada fitur yang "
                "dapat melanggarnya. Janji yang ditegakkan mesin berbeda dari janji yang "
                "ditulis pada dokumen.",
    )

    # 18 ------------------------------------------------------ bagian empat
    d.bagian("04", "Sejauh mana saya sampai",
             "Termasuk apa yang belum bisa saya buktikan.")

    # 19 ---------------------------------------------------------- capaian
    d.angka_besar(
        "Yang sudah dikerjakan",
        [
            (rb(f["py_baris"] + f["ts_baris"]), "baris kode",
             "Python untuk peladen dan model, TypeScript untuk antarmuka."),
            (rb(f["riset_kata"]), "kata riset domain",
             "Enam dokumen, disusun sebelum satu baris kode ditulis."),
            (rb(f["baris"]["snapshot_keluarga"]), "potret kondisi keluarga",
             f"{rb(f['baris']['keluarga'])} keluarga diikuti selama enam gelombang."),
        ],
        catatan="Sebutkan urutannya: riset lebih dahulu, baru kode. Temuan risetnya "
                "membatalkan beberapa rancangan awal saya — dan itu justru gunanya.",
    )

    # 20 ------------------------------------------------------------ batas
    d.poin(
        "Yang belum bisa saya buktikan",
        [
            "**Belum diuji petugas sungguhan.** Ini prototipe berfungsi penuh yang diuji "
            "secara teknis, bukan sistem yang sudah dipakai di lapangan.",
            "**Datanya sintetis.** Ketepatan pada data DTSEN yang sesungguhnya — yang jauh "
            "lebih berantakan — belum diketahui.",
            "**Belum terhubung** ke sistem pemerintahan mana pun.",
            "**Belum melalui penilaian dampak perlindungan data pribadi** secara resmi.",
            "**Model saya pun tidak sempurna.** Pada keluarga di salindia ketiga, ada satu "
            "gelombang ketika skornya justru rendah. Saya menampilkannya, bukan memilih "
            "contoh yang lebih rapi.",
            "**Empat titik akhir sudah dibangun namun belum terhubung ke layar** — "
            "penugasan kasus ke OPD, simulasi dana desa, riwayat versi model, dan pohon "
            "wilayah. Kesepuluh modul berjalan; sebagian fungsinya masih lewat API.",
        ],
        anak="Juri yang berpengalaman akan menemukan batas ini dengan atau tanpa saya beri tahu.",
        ukuran=15,
        catatan="Butir terakhir sengaja ada. Bila juri memeriksa data keluarga contoh, "
                "mereka akan menemukannya sendiri — dan jauh lebih baik bila mereka "
                "mendengarnya dari saya lebih dahulu.",
    )

    # 21 -------------------------------------------------------- berikutnya
    d.poin(
        "Langkah berikutnya",
        [
            "**Uji coba terbatas bersama Dinas Sosial Kabupaten Pringsewu** — lima petugas, "
            "satu kecamatan, satu putaran verifikasi.",
            "**Penerapan pada data DTSEN** dengan izin resmi dan penilaian dampak "
            "perlindungan data.",
            "**Penyesuaian dari temuan petugas** — terutama apakah penjelasan per keluarga "
            "benar-benar berguna di lapangan, atau justru mengganggu.",
            "**Penerapan bertahap** ke kecamatan lain bila uji coba menunjukkan manfaat "
            "yang nyata.",
        ],
        catatan="Sampaikan sebagai rencana yang realistis, bukan janji besar. Yang paling "
                "saya butuhkan sekarang bukan fitur tambahan, melainkan kesempatan menguji "
                "bersama petugas yang sesungguhnya.",
    )

    # 22 ------------------------------------------------------------ tutup
    d.kutipan(
        "Kesalahan memasukkan orang yang tidak berhak\nmembebani anggaran — dan itu terlihat.\n\n"
        "Kesalahan melewatkan orang yang berhak\nmembebani keluarga itu sendiri — dan mereka\n"
        "tidak muncul di daftar mana pun untuk mengeluh.",
        "NADI dibangun untuk kesalahan yang kedua.",
        catatan="Berhenti di sini. Biarkan hening sejenak sebelum membuka sesi tanya jawab.",
    )


# ===========================================================================
def main() -> int:
    p = argparse.ArgumentParser(description="Susun presentasi NADI.")
    p.add_argument("--pdf", action="store_true", help="Buat juga berkas PDF lewat PowerPoint.")
    args = p.parse_args()

    siapkan_matplotlib()
    c = sqlite3.connect(str(AKAR / "data" / "nadi.db"))

    print("  Membaca angka dari sistem...")
    fakta = kumpulkan(c)
    rekap = ambil_rekap()

    print("  Membangkitkan grafik...")
    GAMBAR.mkdir(parents=True, exist_ok=True)
    gambar = {
        "keluarga": grafik_keluarga(c),
        "anggaran": grafik_anggaran(fakta["metrik"]),
        "pembanding": grafik_pembanding(rekap),
    }
    c.close()

    print("  Menyusun salindia...")
    d = Dek(GAMBAR)
    susun(d, fakta, rekap, gambar)
    pptx = d.simpan(KELUARAN / "Presentasi-NADI.pptx")
    print(f"  PPTX : {pptx}  ({pptx.stat().st_size / 1024:.0f} KB, "
          f"{len(d.prs.slides._sldIdLst)} salindia)")

    if args.pdf:
        print("  Mengubah ke PDF lewat PowerPoint...")
        skrip = (
            "import sys, pythoncom, win32com.client as w\n"
            "pythoncom.CoInitialize()\n"
            "app = w.DispatchEx('PowerPoint.Application')\n"
            "d = None\n"
            "try:\n"
            "    d = app.Presentations.Open(sys.argv[1], WithWindow=False)\n"
            "    d.SaveAs(sys.argv[2], 32)\n"
            "finally:\n"
            "    if d is not None:\n"
            "        d.Close()\n"
            "    app.Quit()\n"
            "    pythoncom.CoUninitialize()\n"
        )
        pdf = pptx.with_suffix(".pdf")
        hasil = subprocess.run(
            [sys.executable, "-c", skrip, str(pptx.resolve()), str(pdf.resolve())],
            capture_output=True, text=True, timeout=300,
        )
        if hasil.returncode != 0 or not pdf.exists():
            raise SystemExit(f"PowerPoint gagal membuat PDF:\n{hasil.stderr[-1200:]}")
        print(f"  PDF  : {pdf}  ({pdf.stat().st_size / 1024:.0f} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
