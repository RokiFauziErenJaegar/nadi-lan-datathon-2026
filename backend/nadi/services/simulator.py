"""Simulator kebijakan what-if.

Satu garis batas menaungi seluruh modul ini, dan garis itu bukan formalitas:
**simulator ini menghitung aritmetika cakupan dan biaya, bukan memperkirakan
dampak kebijakan.**

Perbedaannya menentukan. Pertanyaan "berapa keluarga tercakup bila ambang desil
digeser dari 2 ke 3, dan berapa biayanya" dapat dijawab dengan pasti - itu
penjumlahan. Pertanyaan "berapa penurunan angka kemiskinan bila PKH dinaikkan"
tidak dapat dijawab sistem ini, dan tidak akan pernah dapat dijawab hanya dari
data pengamatan. Menjawabnya tetap berarti mengarang angka yang terdengar
berwibawa, lalu anggaran satu kabupaten disusun di atasnya.

Empat mesin hitung disediakan, dan seluruhnya menjawab pertanyaan jenis pertama:

* **Kalkulator cakupan dan biaya** - berapa yang layak, berapa yang tercakup
  pagu, dan siapa saja yang layak namun tidak tercakup. Keluaran terakhir itu
  yang paling berharga: ia mengubah keterbatasan anggaran dari angka abstrak
  menjadi daftar keluarga yang nyata.
* **Simulator alokasi Dana Desa** - menghormati batas regulasi yang berlaku.
* **Simulator penuntasan rumah tidak layak huni** - menggabungkan beberapa
  sumber dana dan menghitung berapa tahun sisa kebutuhan akan tuntas.
* **Kurva kapasitas verifikasi** - menjawab "kalau petugas ditambah, apa
  untungnya" dengan kurva yang melandai, bukan janji yang lurus.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd

from nadi.synth.parameter import ACUAN

logger = logging.getLogger("nadi.simulator")

#: Kalimat yang WAJIB menyertai setiap hasil simulasi pada antarmuka.
PENAFIAN = (
    "Simulasi ini adalah perhitungan aritmetika cakupan dan biaya berdasarkan "
    "aturan kelayakan program serta pagu yang dimasukkan. Simulasi ini BUKAN "
    "prediksi dampak kebijakan dan tidak mengandung klaim sebab-akibat. Angka "
    "nominal program mengikuti sumber yang tercantum beserta tingkat "
    "keyakinannya masing-masing."
)

# ---------------------------------------------------------------------------
# Batas regulasi Dana Desa
# ---------------------------------------------------------------------------
#: Batas alokasi Dana Desa yang berlaku. Ditetapkan peraturan, bukan pilihan
#: daerah, sehingga simulator menolak komposisi yang melanggarnya alih-alih
#: menghitungnya diam-diam.
BATAS_DANA_DESA = {
    "blt_maksimum": 0.15,
    "ketahanan_pangan_minimum": 0.20,
}

#: Besaran bantuan langsung tunai Dana Desa per keluarga.
BLT_PER_BULAN = 300_000.0
BLT_BULAN_MAKSIMUM = 3

# ---------------------------------------------------------------------------
# Sumber pendanaan perbaikan rumah
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class SumberRTLH:
    kode: str
    nama: str
    nominal_per_unit: float
    kapasitas_tahunan: int
    sumber_dana: str
    tingkat_keyakinan: str


#: Sumber pendanaan perbaikan rumah beserta kapasitas tahunannya.
#: Kapasitas APBD memakai realisasi nyata Kabupaten Pringsewu tahun 2025:
#: 80 keluarga penerima dengan total anggaran Rp1,2 miliar.
SUMBER_RTLH: tuple[SumberRTLH, ...] = (
    SumberRTLH("BSPS", "Bantuan Stimulan Perumahan Swadaya", 20_000_000, 0, "APBN", "pasti"),
    SumberRTLH("RST", "Rumah Sejahtera Terpadu", 20_000_000, 0, "APBN", "cukup_kuat"),
    SumberRTLH("RUTILAHU-D", "Rutilahu APBD Kabupaten", 15_000_000, 80, "APBD Kabupaten", "cukup_kuat"),
    SumberRTLH("DANA-DESA", "Dana Desa", 15_000_000, 0, "Dana Desa", "perkiraan"),
)


# ===========================================================================
# (a) Kalkulator cakupan dan biaya
# ===========================================================================
@dataclass
class HasilCakupan:
    jumlah_layak: int = 0
    jumlah_tercakup: int = 0
    jumlah_tidak_tercakup: int = 0
    biaya_per_penerima_tahunan: float = 0.0
    biaya_total_tahunan: float = 0.0
    pagu: float | None = None
    sisa_pagu: float | None = None
    persen_terlayani: float = 0.0
    rincian_wilayah: list[dict] = field(default_factory=list)
    keluarga_tidak_tercakup: list[str] = field(default_factory=list)
    asumsi: list[str] = field(default_factory=list)
    penafian: str = PENAFIAN

    def ke_dict(self) -> dict[str, Any]:
        return {
            "jumlah_layak": self.jumlah_layak,
            "jumlah_tercakup": self.jumlah_tercakup,
            "jumlah_tidak_tercakup": self.jumlah_tidak_tercakup,
            "biaya_per_penerima_tahunan": self.biaya_per_penerima_tahunan,
            "biaya_total_tahunan": self.biaya_total_tahunan,
            "pagu": self.pagu,
            "sisa_pagu": self.sisa_pagu,
            "persen_terlayani": round(self.persen_terlayani, 2),
            "rincian_wilayah": self.rincian_wilayah,
            "jumlah_contoh_tidak_tercakup": len(self.keluarga_tidak_tercakup),
            "keluarga_tidak_tercakup": self.keluarga_tidak_tercakup,
            "asumsi": self.asumsi,
            "penafian": self.penafian,
        }


def hitung_cakupan(
    kandidat: pd.DataFrame,
    *,
    biaya_satuan_tahunan: float,
    pagu: float | None = None,
    kolom_prioritas: str = "skor",
    kolom_wilayah: str = "kecamatan",
    kolom_kode: str = "kode_semu",
    contoh_tidak_tercakup: int = 25,
    asumsi: list[str] | None = None,
) -> HasilCakupan:
    """Hitung berapa keluarga tercakup pagu, dan siapa yang tidak.

    Args:
        kandidat: keluarga yang memenuhi syarat, satu baris per keluarga.
        biaya_satuan_tahunan: biaya per penerima per tahun.
        pagu: batas anggaran. Bila kosong, seluruh kandidat dianggap tercakup.
        kolom_prioritas: kolom yang menentukan urutan pelayanan. Bawaannya
            skor kerentanan - yang paling rentan dilayani lebih dahulu.

    Kunci kejujuran modul ini ada pada ``keluarga_tidak_tercakup``. Simulator
    yang hanya melaporkan "tercakup 1.240 dari 3.100 keluarga" membiarkan sisa
    1.860 tetap berupa angka. Menyebutkan kode keluarga yang tidak tercakup
    mengubahnya menjadi daftar yang dapat dibawa ke rapat anggaran.
    """
    hasil = HasilCakupan(
        biaya_per_penerima_tahunan=float(biaya_satuan_tahunan),
        pagu=pagu,
        asumsi=asumsi or [],
    )
    if kandidat.empty or biaya_satuan_tahunan <= 0:
        return hasil

    urut = (
        kandidat.sort_values(kolom_prioritas, ascending=False)
        if kolom_prioritas in kandidat.columns
        else kandidat
    )
    hasil.jumlah_layak = len(urut)

    if pagu is None:
        muat = len(urut)
    else:
        muat = int(min(len(urut), np.floor(pagu / biaya_satuan_tahunan)))

    tercakup = urut.iloc[:muat]
    tidak = urut.iloc[muat:]

    hasil.jumlah_tercakup = len(tercakup)
    hasil.jumlah_tidak_tercakup = len(tidak)
    hasil.biaya_total_tahunan = round(len(tercakup) * biaya_satuan_tahunan, 0)
    if pagu is not None:
        hasil.sisa_pagu = round(pagu - hasil.biaya_total_tahunan, 0)
    hasil.persen_terlayani = (
        len(tercakup) / len(urut) * 100.0 if len(urut) else 0.0
    )

    if kolom_wilayah in urut.columns:
        rekap = (
            urut.assign(_tercakup=[True] * muat + [False] * (len(urut) - muat))
            .groupby(kolom_wilayah)
            .agg(layak=("_tercakup", "size"), tercakup=("_tercakup", "sum"))
            .reset_index()
        )
        rekap["tidak_tercakup"] = rekap["layak"] - rekap["tercakup"]
        rekap["persen"] = (rekap["tercakup"] / rekap["layak"] * 100).round(1)
        hasil.rincian_wilayah = rekap.sort_values("tidak_tercakup", ascending=False).to_dict("records")

    if kolom_kode in tidak.columns:
        hasil.keluarga_tidak_tercakup = tidak[kolom_kode].head(contoh_tidak_tercakup).tolist()

    return hasil


# ===========================================================================
# (b) Simulator alokasi Dana Desa
# ===========================================================================
@dataclass
class HasilDanaDesa:
    pagu: float
    alokasi: dict[str, float] = field(default_factory=dict)
    kpm_blt: int = 0
    bulan_blt: int = 0
    pelanggaran: list[str] = field(default_factory=list)
    catatan: list[str] = field(default_factory=list)
    penafian: str = PENAFIAN

    @property
    def sah(self) -> bool:
        return not self.pelanggaran


def simulasi_dana_desa(
    pagu: float,
    *,
    porsi_blt: float = 0.15,
    porsi_ketahanan_pangan: float = 0.20,
    porsi_stunting: float = 0.10,
    porsi_padat_karya: float = 0.15,
    bulan_blt: int = 3,
) -> HasilDanaDesa:
    """Bagi pagu Dana Desa satu pekon menurut komposisi yang diminta.

    Batas regulasi diperiksa dan dilaporkan sebagai pelanggaran, bukan
    dibetulkan diam-diam. Simulator yang memperbaiki masukan pengguna tanpa
    memberi tahu akan membuat pengguna mengira komposisinya sah, lalu
    menemukannya ditolak saat penyusunan anggaran sesungguhnya.
    """
    hasil = HasilDanaDesa(pagu=float(pagu), bulan_blt=int(bulan_blt))

    if porsi_blt > BATAS_DANA_DESA["blt_maksimum"]:
        hasil.pelanggaran.append(
            f"Porsi bantuan langsung tunai {porsi_blt * 100:.1f} persen melampaui "
            f"batas {BATAS_DANA_DESA['blt_maksimum'] * 100:.0f} persen."
        )
    if porsi_ketahanan_pangan < BATAS_DANA_DESA["ketahanan_pangan_minimum"]:
        hasil.pelanggaran.append(
            f"Porsi ketahanan pangan {porsi_ketahanan_pangan * 100:.1f} persen berada "
            f"di bawah batas minimum {BATAS_DANA_DESA['ketahanan_pangan_minimum'] * 100:.0f} persen."
        )
    if bulan_blt > BLT_BULAN_MAKSIMUM:
        hasil.pelanggaran.append(
            f"Penyaluran bantuan langsung tunai {bulan_blt} bulan melampaui batas "
            f"{BLT_BULAN_MAKSIMUM} bulan."
        )

    total_porsi = porsi_blt + porsi_ketahanan_pangan + porsi_stunting + porsi_padat_karya
    if total_porsi > 1.0:
        hasil.pelanggaran.append(
            f"Jumlah seluruh porsi {total_porsi * 100:.1f} persen melampaui pagu."
        )

    hasil.alokasi = {
        "bantuan_langsung_tunai": round(pagu * porsi_blt, 0),
        "ketahanan_pangan": round(pagu * porsi_ketahanan_pangan, 0),
        "penanganan_stunting": round(pagu * porsi_stunting, 0),
        "padat_karya_tunai": round(pagu * porsi_padat_karya, 0),
        "operasional_dan_lainnya": round(pagu * max(0.0, 1.0 - total_porsi), 0),
    }

    biaya_per_kpm = BLT_PER_BULAN * min(bulan_blt, BLT_BULAN_MAKSIMUM)
    hasil.kpm_blt = int(hasil.alokasi["bantuan_langsung_tunai"] // biaya_per_kpm)
    hasil.catatan.append(
        f"Dengan Rp{BLT_PER_BULAN:,.0f} per bulan selama {min(bulan_blt, BLT_BULAN_MAKSIMUM)} bulan, "
        f"alokasi ini menjangkau {hasil.kpm_blt} keluarga.".replace(",", ".")
    )
    hasil.catatan.append(
        "Bantuan langsung tunai Dana Desa ditetapkan lewat musyawarah pekon, "
        "sehingga dapat menjangkau keluarga yang belum tercatat pada data pusat - "
        "jalur tercepat menanggapi guncangan mendadak."
    )
    return hasil


# ===========================================================================
# (c) Simulator penuntasan rumah tidak layak huni
# ===========================================================================
@dataclass
class HasilRTLH:
    backlog: int
    kapasitas_tahunan: int
    tahun_tuntas: float
    biaya_tahunan: float
    biaya_total: float
    rincian_sumber: list[dict] = field(default_factory=list)
    lintasan: list[dict] = field(default_factory=list)
    catatan: list[str] = field(default_factory=list)
    penafian: str = PENAFIAN


def simulasi_rtlh(
    *,
    backlog: int | None = None,
    kapasitas: dict[str, int] | None = None,
    tahun_maksimum: int = 25,
    pertumbuhan_backlog_tahunan: float = 0.0,
) -> HasilRTLH:
    """Hitung berapa tahun sisa kebutuhan perbaikan rumah akan tuntas.

    Args:
        backlog: sisa unit yang belum tertangani. Bawaannya angka Kabupaten
            Pringsewu, yakni sekitar 1.700 unit.
        kapasitas: unit per tahun per sumber dana.
        pertumbuhan_backlog_tahunan: bagian rumah yang MEMBURUK menjadi tidak
            layak setiap tahun. Diabaikan pada perhitungan dasar, padahal di
            lapangan tidak dapat diabaikan - rumah menua lebih cepat daripada
            anggaran bertambah. Menyediakan parameter ini memungkinkan
            pertanyaan yang lebih jujur diajukan.
    """
    backlog = int(backlog if backlog is not None else ACUAN.backlog_rtlh)
    kapasitas = kapasitas or {s.kode: s.kapasitas_tahunan for s in SUMBER_RTLH}

    peta = {s.kode: s for s in SUMBER_RTLH}
    total_unit = 0
    biaya_tahunan = 0.0
    rincian: list[dict] = []

    for kode, unit in kapasitas.items():
        s = peta.get(kode)
        if s is None or unit <= 0:
            continue
        total_unit += int(unit)
        biaya = float(unit) * s.nominal_per_unit
        biaya_tahunan += biaya
        rincian.append(
            {
                "kode": kode,
                "nama": s.nama,
                "unit_per_tahun": int(unit),
                "nominal_per_unit": s.nominal_per_unit,
                "biaya_tahunan": round(biaya, 0),
                "sumber_dana": s.sumber_dana,
                "tingkat_keyakinan": s.tingkat_keyakinan,
            }
        )

    hasil = HasilRTLH(
        backlog=backlog,
        kapasitas_tahunan=total_unit,
        tahun_tuntas=float("inf"),
        biaya_tahunan=round(biaya_tahunan, 0),
        biaya_total=0.0,
        rincian_sumber=rincian,
    )

    if total_unit <= 0:
        hasil.catatan.append(
            "Tidak ada kapasitas penanganan pada skenario ini, sehingga sisa "
            "kebutuhan tidak akan pernah tuntas."
        )
        return hasil

    sisa = float(backlog)
    lintasan: list[dict] = []
    for tahun in range(1, tahun_maksimum + 1):
        sisa = max(0.0, sisa - total_unit)
        sisa += sisa * pertumbuhan_backlog_tahunan
        lintasan.append({"tahun": tahun, "sisa_unit": int(round(sisa))})
        if sisa <= 0:
            hasil.tahun_tuntas = float(tahun)
            break
    else:
        hasil.tahun_tuntas = float("inf")

    hasil.lintasan = lintasan
    if hasil.tahun_tuntas != float("inf"):
        hasil.biaya_total = round(biaya_tahunan * hasil.tahun_tuntas, 0)
        hasil.catatan.append(
            f"Dengan kapasitas {total_unit} unit per tahun, sisa kebutuhan {backlog} unit "
            f"tuntas dalam {hasil.tahun_tuntas:.0f} tahun."
        )
    else:
        hasil.catatan.append(
            f"Dengan kapasitas {total_unit} unit per tahun dan pertumbuhan "
            f"{pertumbuhan_backlog_tahunan * 100:.1f} persen, sisa kebutuhan tidak tuntas "
            f"dalam {tahun_maksimum} tahun."
        )

    hasil.catatan.append(
        "Perhitungan ini tidak memuat kenaikan biaya bahan bangunan maupun "
        "perubahan kriteria kelayakan."
    )
    return hasil


# ===========================================================================
# (d) Kurva kapasitas verifikasi
# ===========================================================================
def kurva_kapasitas(
    y: np.ndarray,
    skor: np.ndarray,
    *,
    titik: tuple[int, ...] = (50, 100, 200, 300, 500, 750, 1000, 1500, 2000, 3000, 5000),
) -> dict[str, Any]:
    """Bentuk kurva hasil terhadap kapasitas verifikasi.

    Menjawab pertanyaan yang paling sering diajukan pimpinan daerah - "kalau
    petugas saya tambah, apa untungnya" - dan menjawabnya dengan kurva yang
    melandai. Tambahan seratus kunjungan pertama bernilai jauh lebih besar
    daripada seratus kunjungan berikutnya, dan kurva itu memperlihatkannya
    tanpa perlu dijelaskan.
    """
    from nadi.ml.evaluasi import metrik_pada_anggaran

    y = np.asarray(y).astype(bool)
    baris: list[dict] = []
    sebelumnya = 0.0

    for k in titik:
        if k > len(y):
            break
        m = metrik_pada_anggaran(y, skor, k)
        tambahan = m["tertangkap"] - sebelumnya
        sebelumnya = m["tertangkap"]
        baris.append(
            {
                "k": int(k),
                "tertangkap": int(m["tertangkap"]),
                "tambahan_dari_titik_sebelumnya": int(tambahan),
                "presisi": round(m["presisi"], 4),
                "recall": round(m["recall"], 4),
                "pengganda": round(m["pengganda"], 2),
            }
        )

    return {
        "prevalensi": round(float(y.mean()), 4),
        "total_positif": int(y.sum()),
        "titik": baris,
        "penafian": PENAFIAN,
        "catatan": (
            "Setiap penambahan kapasitas memberi hasil yang makin mengecil. "
            "Angka 'tambahan' menunjukkan berapa keluarga baru yang ditemukan "
            "oleh setiap kenaikan kapasitas, dan itulah dasar yang tepat untuk "
            "menimbang penambahan petugas."
        ),
    }


__all__ = [
    "BATAS_DANA_DESA",
    "BLT_PER_BULAN",
    "HasilCakupan",
    "HasilDanaDesa",
    "HasilRTLH",
    "PENAFIAN",
    "SUMBER_RTLH",
    "SumberRTLH",
    "hitung_cakupan",
    "kurva_kapasitas",
    "simulasi_dana_desa",
    "simulasi_rtlh",
]
