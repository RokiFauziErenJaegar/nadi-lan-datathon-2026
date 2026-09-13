"""Susun berkas data awal wilayah Kabupaten Pringsewu.

Menggabungkan tiga sumber menjadi satu berkas siap muat:

* daftar 131 pekon dan kelurahan beserta kode Kemendagri, titik pusat, dan
  luas menurut Badan Informasi Geospasial;
* rekapitulasi kecamatan dari publikasi *Pringsewu Dalam Angka 2025*;
* Indeks Desa Membangun 2024 dari Kementerian Desa.

Indeks Desa Membangun dipakai bukan sekadar sebagai keterangan tambahan.
Ia menjadi dasar pengaruh wilayah pada generator data sintetis: pekon berstatus
Berkembang - lima belas di antaranya, terpusat di Pagelaran Utara dan Pardasuka -
dibangkitkan dengan kemampuan ekonomi lebih rendah. Dengan begitu, kantong
kemiskinan pada data sintetis jatuh di tempat yang memang tertinggal menurut
penilaian resmi, bukan tersebar acak. Peta yang dihasilkan pun menunjukkan pola
yang dapat dikenali orang yang mengenal daerahnya.

Jalankan dengan:
    python backend/scripts/siapkan_wilayah.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

AKAR = Path(__file__).resolve().parents[2]
SUMBER = AKAR / "docs" / "research" / "pringsewu-seed" / "seed_desa_pringsewu.json"
GEOJSON_SUMBER = AKAR / "docs" / "research" / "pringsewu-seed" / "pringsewu_desa.geojson"
TUJUAN = AKAR / "data" / "seed" / "wilayah.json"
GEOJSON_TUJUAN = AKAR / "data" / "geo" / "pringsewu_desa.geojson"

# ---------------------------------------------------------------------------
# Rekapitulasi kecamatan
# ---------------------------------------------------------------------------
# Sumber: BPS, Pringsewu Dalam Angka 2025, Tabel 1.1.1 dan 3.1.1.
# Penduduk berasal dari Data Konsolidasi Bersih Semester II 2024 Kemendagri.
#
# PERINGATAN yang perlu diingat saat menyajikan angka: terdapat dua definisi
# penduduk yang berbeda dan tidak boleh dicampur. Data Konsolidasi Bersih
# mencatat 444.834 jiwa dan tersedia sampai tingkat kecamatan, sedangkan
# proyeksi BPS hasil Sensus Penduduk 2020 mencatat 424,68 ribu jiwa dan menjadi
# dasar seluruh indikator makro termasuk angka kemiskinan. Selisihnya sekitar
# dua puluh ribu jiwa. Angka kecamatan di sini memakai Data Konsolidasi Bersih
# karena hanya itu yang tersedia per kecamatan.
KECAMATAN = [
    # kode, nama, ibu kota, luas km2, penduduk 2024, lat, lon
    ("18.10.01", "Pringsewu", "Pringsewu", 45.28, 88_758, -5.35643, 104.96524),
    ("18.10.02", "Gading Rejo", "Gading Rejo", 67.79, 85_447, -5.36943, 105.02848),
    ("18.10.03", "Ambarawa", "Ambarawa", 33.11, 40_517, -5.41087, 104.95014),
    ("18.10.04", "Pardasuka", "Pardasuka", 87.31, 38_594, -5.50645, 104.92690),
    ("18.10.05", "Pagelaran", "Pagelaran", 48.42, 56_839, -5.37236, 104.90441),
    ("18.10.06", "Banyumas", "Banyumas", 42.71, 23_610, -5.29113, 104.91433),
    ("18.10.07", "Adiluwih", "Adi Luwih", 68.80, 39_457, -5.24862, 105.01708),
    ("18.10.08", "Sukoharjo", "Sukoharjo", 65.59, 54_760, -5.30244, 104.98688),
    ("18.10.09", "Pagelaran Utara", "Fajar Mulia", 158.19, 16_852, -5.25807, 104.83917),
]

# Indeks Desa Membangun 2024, Kementerian Desa.
# Bentuknya: nama kecamatan -> (jumlah Berkembang, Maju, Mandiri).
# Tidak ada pekon berstatus Tertinggal maupun Sangat Tertinggal di Pringsewu.
IDM_2024 = {
    "Pardasuka": (6, 7, 0),
    "Ambarawa": (0, 3, 5),
    "Pagelaran": (1, 14, 7),
    "Pagelaran Utara": (7, 3, 0),
    "Pringsewu": (1, 4, 5),
    "Gading Rejo": (0, 10, 13),
    "Sukoharjo": (0, 14, 2),
    "Banyumas": (0, 11, 0),
    "Adiluwih": (0, 9, 4),
}

#: Pengaruh status Indeks Desa Membangun terhadap kemampuan ekonomi keluarga,
#: dalam satuan logaritma. Selisih antara pekon Berkembang dan Mandiri sekitar
#: dua puluh dua persen pengeluaran per kapita - besaran yang sejalan dengan
#: selisih antar-wilayah yang teramati pada data kabupaten.
EFEK_IDM = {
    "Berkembang": -0.13,
    "Maju": 0.0,
    "Mandiri": 0.09,
}

#: Ambang kepadatan penduduk untuk menggolongkan sebuah pekon sebagai
#: perkotaan. Seluruh kelurahan otomatis tergolong perkotaan.
AMBANG_KEPADATAN_PERKOTAAN = 1_500.0


def _urutkan_idm(desa_kecamatan: list[dict], jumlah: tuple[int, int, int]) -> None:
    """Tetapkan status Indeks Desa Membangun pada pekon di satu kecamatan.

    Rincian per pekon tidak tersedia pada sumber, yang tersedia hanya
    jumlahnya per kecamatan. Penetapan dilakukan menurut luas wilayah: pekon
    terluas menerima status paling rendah lebih dahulu.

    Dasarnya bukan kebetulan. Pada Pringsewu, wilayah yang lebih luas berarti
    lebih jarang penduduknya dan lebih jauh dari pusat layanan - Pagelaran
    Utara meliputi 25,63 persen luas kabupaten namun hanya dihuni 16.852 jiwa,
    dan di sanalah tujuh dari lima belas pekon Berkembang berada. Aturan ini
    karenanya mereproduksi pola yang memang ada, bukan menciptakan pola baru.

    Kelurahan dikecualikan sebab Indeks Desa Membangun hanya menilai pekon.
    """
    berkembang, maju, mandiri = jumlah
    pekon = [d for d in desa_kecamatan if d["status"] == "pekon"]
    pekon.sort(key=lambda d: d["luas_ha_big"], reverse=True)

    for i, d in enumerate(pekon):
        if i < berkembang:
            d["status_idm"] = "Berkembang"
        elif i < berkembang + maju:
            d["status_idm"] = "Maju"
        else:
            d["status_idm"] = "Mandiri"

    for d in desa_kecamatan:
        if d["status"] == "kelurahan":
            d["status_idm"] = None

    diharapkan = berkembang + maju + mandiri
    if len(pekon) != diharapkan:
        raise SystemExit(
            f"Jumlah pekon tidak cocok dengan data Indeks Desa Membangun: "
            f"{len(pekon)} pekon terdaftar, {diharapkan} menurut sumber."
        )


def _bagi_penduduk(desa_kecamatan: list[dict], penduduk_kecamatan: int) -> None:
    """Bagikan penduduk kecamatan ke pekon dan kelurahan di bawahnya.

    Penduduk tingkat desa tidak ditemukan pada sumber mana pun, sehingga
    pembagian ini merupakan ASUMSI dan ditandai demikian pada berkas keluaran.

    Dua pertimbangan mendasarinya. Pertama, penduduk bertambah lebih lambat
    daripada luas wilayah - desa yang dua kali lebih luas tidak berpenduduk dua
    kali lipat, sebab desa luas justru cenderung berupa perbukitan yang jarang
    dihuni. Karena itu dipakai luas berpangkat 0,7, bukan luas apa adanya.
    Kedua, kelurahan merupakan inti perkotaan Pringsewu dengan kepadatan jauh
    di atas pekon, sehingga diberi pengali tersendiri.
    """
    bobot = []
    for d in desa_kecamatan:
        w = d["luas_ha_big"] ** 0.7
        if d["status"] == "kelurahan":
            w *= 3.5
        bobot.append(w)

    total = sum(bobot)
    sisa = penduduk_kecamatan
    for i, d in enumerate(desa_kecamatan):
        if i == len(desa_kecamatan) - 1:
            d["jumlah_penduduk"] = sisa  # baris terakhir menyerap sisa pembulatan
        else:
            n = round(penduduk_kecamatan * bobot[i] / total)
            d["jumlah_penduduk"] = n
            sisa -= n


def main() -> int:
    if not SUMBER.exists():
        print(f"Berkas sumber tidak ditemukan: {SUMBER}", file=sys.stderr)
        return 1

    desa = json.loads(SUMBER.read_text(encoding="utf-8"))
    if len(desa) != 131:
        print(f"Diharapkan 131 desa dan kelurahan, ditemukan {len(desa)}.", file=sys.stderr)
        return 1

    per_kecamatan: dict[str, list[dict]] = {}
    for d in desa:
        per_kecamatan.setdefault(d["kode_kec"], []).append(d)

    wilayah: list[dict] = []

    # --- Tingkat kabupaten ---
    total_penduduk = sum(k[4] for k in KECAMATAN)
    total_luas = sum(k[3] for k in KECAMATAN)
    wilayah.append(
        {
            "kode": "18.10",
            "nama": "Pringsewu",
            "jenis": "kabupaten",
            "induk": None,
            "tingkat": 0,
            "lintang": -5.33636,
            "bujur": 104.93341,
            "luas_km2": round(total_luas, 2),
            "jumlah_penduduk": total_penduduk,
            "klasifikasi": None,
        }
    )

    # --- Tingkat kecamatan dan desa ---
    for kode, nama, ibukota, luas, penduduk, lat, lon in KECAMATAN:
        anak = per_kecamatan.get(kode, [])
        if not anak:
            print(f"Kecamatan {nama} tidak memiliki desa pada berkas sumber.", file=sys.stderr)
            return 1

        _urutkan_idm(anak, IDM_2024[nama])
        _bagi_penduduk(anak, penduduk)

        kepadatan = penduduk / luas
        wilayah.append(
            {
                "kode": kode,
                "nama": nama,
                "jenis": "kecamatan",
                "induk": "18.10",
                "tingkat": 1,
                "ibukota": ibukota,
                "lintang": lat,
                "bujur": lon,
                "luas_km2": luas,
                "jumlah_penduduk": penduduk,
                "kepadatan_per_km2": round(kepadatan, 1),
                "klasifikasi": "perkotaan" if kepadatan >= AMBANG_KEPADATAN_PERKOTAAN else "perdesaan",
                "idm_berkembang": IDM_2024[nama][0],
                "idm_maju": IDM_2024[nama][1],
                "idm_mandiri": IDM_2024[nama][2],
            }
        )

        for d in sorted(anak, key=lambda x: x["kode"]):
            luas_km2 = d["luas_ha_big"] / 100.0
            kepadatan_desa = d["jumlah_penduduk"] / luas_km2 if luas_km2 else 0.0
            perkotaan = d["status"] == "kelurahan" or kepadatan_desa >= AMBANG_KEPADATAN_PERKOTAAN
            wilayah.append(
                {
                    "kode": d["kode"],
                    "nama": d["nama"],
                    "jenis": d["status"],
                    "induk": kode,
                    "tingkat": 2,
                    "lintang": d["lat"],
                    "bujur": d["lon"],
                    "luas_km2": round(luas_km2, 4),
                    "jumlah_penduduk": d["jumlah_penduduk"],
                    "kepadatan_per_km2": round(kepadatan_desa, 1),
                    "klasifikasi": "perkotaan" if perkotaan else "perdesaan",
                    "status_idm": d["status_idm"],
                    "efek_ekonomi": EFEK_IDM.get(d["status_idm"], 0.02),
                }
            )

    keluaran = {
        "_keterangan": (
            "Struktur wilayah Kabupaten Pringsewu: 1 kabupaten, 9 kecamatan, "
            "126 pekon, dan 5 kelurahan. Kode mengikuti Kepmendagri Nomor "
            "300.2.2-2138/2025 dan cocok seluruhnya dengan layer batas desa "
            "Badan Informasi Geospasial."
        ),
        "_sumber": {
            "daftar_wilayah": "Kepmendagri No. 300.2.2-2138/2025",
            "batas_dan_luas": "Badan Informasi Geospasial, layer batas desa 1:10.000",
            "penduduk_kecamatan": "Data Konsolidasi Bersih Semester II 2024 Kemendagri, via BPS Pringsewu Dalam Angka 2025",
            "indeks_desa_membangun": "Kementerian Desa PDTT, 2024",
        },
        "_asumsi": [
            "Penduduk tingkat desa TIDAK tersedia pada sumber mana pun. Angka pada "
            "berkas ini dibagi dari penduduk kecamatan menurut luas berpangkat 0,7, "
            "dengan pengali 3,5 bagi kelurahan. Ini asumsi, bukan data resmi.",
            "Status Indeks Desa Membangun per desa tidak tersedia; yang tersedia "
            "hanya jumlahnya per kecamatan. Penetapan dilakukan menurut luas wilayah "
            "dari yang terluas. Jumlah per kecamatan tetap persis sesuai sumber.",
            "Penggolongan perkotaan dan perdesaan memakai ambang kepadatan 1.500 "
            "jiwa per kilometer persegi, ditambah seluruh kelurahan.",
        ],
        "_peringatan": (
            "Dua definisi penduduk beredar dan tidak boleh dicampur. Data "
            "Konsolidasi Bersih Semester II 2024 mencatat 444.834 jiwa, sedangkan "
            "proyeksi BPS hasil Sensus Penduduk 2020 mencatat 424,68 ribu jiwa dan "
            "menjadi dasar seluruh indikator makro termasuk angka kemiskinan. "
            "Berkas ini memakai Data Konsolidasi Bersih karena hanya itu yang "
            "tersedia sampai tingkat kecamatan."
        ),
        "wilayah": wilayah,
    }

    TUJUAN.parent.mkdir(parents=True, exist_ok=True)
    TUJUAN.write_text(
        json.dumps(keluaran, ensure_ascii=False, indent=1), encoding="utf-8"
    )

    # --- Salin batas wilayah ---
    if GEOJSON_SUMBER.exists():
        GEOJSON_TUJUAN.parent.mkdir(parents=True, exist_ok=True)
        GEOJSON_TUJUAN.write_bytes(GEOJSON_SUMBER.read_bytes())

    # --- Ringkasan ---
    jml = {"kabupaten": 0, "kecamatan": 0, "pekon": 0, "kelurahan": 0}
    for w in wilayah:
        jml[w["jenis"]] += 1
    print("Berkas wilayah ditulis:", TUJUAN.relative_to(AKAR))
    print(
        f"  {jml['kabupaten']} kabupaten, {jml['kecamatan']} kecamatan, "
        f"{jml['pekon']} pekon, {jml['kelurahan']} kelurahan "
        f"(total {len(wilayah)} baris)"
    )
    idm = {}
    for w in wilayah:
        if w.get("status_idm"):
            idm[w["status_idm"]] = idm.get(w["status_idm"], 0) + 1
    print(f"  Indeks Desa Membangun: {idm}")
    if GEOJSON_SUMBER.exists():
        print(
            f"  Batas wilayah disalin ke {GEOJSON_TUJUAN.relative_to(AKAR)} "
            f"({GEOJSON_TUJUAN.stat().st_size / 1024 / 1024:.1f} MB)"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
