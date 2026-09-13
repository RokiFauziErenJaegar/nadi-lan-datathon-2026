"""Deteksi ketidaksesuaian sasaran dan kejanggalan data.

Menghasilkan antrean kasus untuk diperiksa manusia. Tujuh jenis kejanggalan
dikenali, dan urutan penyajiannya bukan urutan penulisan kode melainkan urutan
kepentingan menurut dampaknya bagi keluarga.

**Yang terlewat lebih dahulu.** Keluarga sangat rentan yang tidak menerima
program relevan diletakkan paling atas. Alasannya bukan teknis melainkan
kesejahteraan: kesalahan memasukkan orang yang tidak berhak membebani anggaran
negara, sedangkan kesalahan melewatkan orang yang berhak membebani keluarga
itu sendiri - dan keluarga itu tidak muncul di daftar mana pun untuk mengeluh.
Sistem semacam ini secara alami condong menemukan kesalahan jenis kedua, sebab
data penerima selalu lebih mudah diperiksa daripada data bukan-penerima. Urutan
di sini melawan kecondongan itu dengan sengaja.

**Setiap kasus membawa buktinya.** Tidak ada kasus yang muncul hanya dengan
label. Masing-masing menyertakan angka yang menjadi dasarnya, sehingga petugas
dapat menilai sendiri apakah penandaan itu masuk akal sebelum berangkat ke
lapangan - dan dapat menyatakan sistem keliru bila memang keliru.

**Tidak satu pun kasus adalah keputusan.** Seluruh keluaran modul ini berupa
usulan pemeriksaan. Tidak ada jalur pada aplikasi yang mengubahnya menjadi
penghentian bantuan tanpa melewati verifikasi manusia.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine

from nadi.db.enums import JenisAnomali, StatusKasus
from nadi.ml.fitur import PETA_FITUR

logger = logging.getLogger("nadi.anomali")

#: Bagian teratas populasi yang diperlakukan sebagai prioritas.
#:
#: Ambang ditetapkan secara RELATIF, bukan sebagai angka skor mutlak. Percobaan
#: pertama memakai ambang tetap 60 dari 100, dan hasilnya antrean yang nyaris
#: kosong pada jenis kasus terpenting - hanya dua keluarga terlewat yang
#: terdeteksi dari empat puluh ribu. Sebabnya sederhana: skor adalah peluang
#: terkalibrasi, dan pada persoalan dengan prevalensi sebelas persen, peluang di
#: atas enam puluh persen memang jarang. Ambang tetap itu benar secara
#: aritmetika namun tidak berguna secara operasional.
#:
#: Ambang relatif menjawab pertanyaan yang sesungguhnya diajukan dinas: "dari
#: sekian ribu keluarga, mana yang harus saya datangi lebih dahulu dengan
#: petugas yang saya punya". Nilainya karena itu ditetapkan menurut kapasitas
#: verifikasi, bukan menurut sifat sebaran skor.
PORSI_PRIORITAS = 0.05

#: Batas bawah skor mutlak agar keluarga berskor sangat rendah tidak ikut
#: terangkat hanya karena wilayahnya secara keseluruhan berskor rendah.
AMBANG_SKOR_MINIMUM = 25.0

#: Desil di atas ini dianggap sudah tidak memenuhi kriteria bantuan reguler.
DESIL_LEWAT_AMBANG = 6

#: Umur data dalam bulan yang dianggap kedaluwarsa untuk keluarga berisiko.
BATAS_UMUR_DATA_BULAN = 18

#: Pasangan program yang manfaatnya bertumpuk pada kebutuhan yang sama.
#: Menerima keduanya sekaligus bukan pelanggaran, namun patut diperiksa sebab
#: satu kebutuhan terlayani dua kali sementara keluarga lain belum terlayani
#: sama sekali.
PROGRAM_BERTUMPUK: tuple[tuple[str, str, str], ...] = (
    ("BSPS", "RST", "perbaikan rumah"),
    ("BSPS", "RUTILAHU-D", "perbaikan rumah"),
    ("RST", "RUTILAHU-D", "perbaikan rumah"),
    ("PENA", "PPSE", "modal usaha"),
    ("PENA", "KUBE", "modal usaha"),
)
# CATATAN: Program Sembako dan Bantuan Pangan Beras sempat dimasukkan ke daftar
# ini sebagai sama-sama "bantuan pangan", dan hasilnya keliru secara telak -
# tiga ribu lima ratus kasus, delapan puluh tujuh persen isi antrean, untuk
# keadaan yang justru dirancang begitu. Keduanya program pangan nasional yang
# memang saling melengkapi: satu berupa saldo untuk membeli pangan bergizi, satu
# lagi berupa beras. Menerima keduanya bukan penyimpangan.
#
# Yang tertinggal pada daftar ini hanyalah program yang benar-benar menyelesaikan
# SATU kebutuhan yang sama dengan cara yang sama - tiga program perbaikan rumah
# dengan nominal setara, dan tiga program modal usaha. Menerima dua di antaranya
# berarti satu rumah diperbaiki dua kali sementara rumah lain belum tersentuh.


@dataclass
class Temuan:
    """Satu kasus yang ditandai untuk diperiksa."""

    keluarga_id: int
    gelombang: int
    jenis: JenisAnomali
    skor_prioritas: float
    tingkat_prioritas: int
    alasan: list[dict[str, Any]] = field(default_factory=list)
    ringkasan: str = ""
    sumber_deteksi: str = "aturan"
    opd_disarankan: str | None = None


@dataclass
class RingkasanDeteksi:
    jumlah: int = 0
    per_jenis: dict[str, int] = field(default_factory=dict)
    gelombang: int = 0


# ===========================================================================
# Pemuatan bahan
# ===========================================================================
def muat_bahan_deteksi(mesin: Engine, gelombang: int) -> pd.DataFrame:
    """Kumpulkan seluruh bahan yang diperlukan untuk satu gelombang."""
    kondisi = pd.read_sql(
        text(
            """
            SELECT s.keluarga_id, s.gelombang, s.desil_kesejahteraan,
                   s.jumlah_program_diterima, s.nilai_bantuan_bulanan,
                   s.jumlah_anggota, s.jumlah_balita, s.jumlah_anak_usia_sekolah,
                   s.jumlah_lansia, s.jumlah_disabilitas, s.jumlah_ibu_hamil,
                   s.jumlah_ber_jkn, s.jumlah_tanpa_dokumen,
                   s.ada_anak_putus_sekolah, s.ada_penyakit_biaya_tinggi,
                   s.ada_gizi_bermasalah,
                   s.luas_lantai_m2, s.jenis_lantai_terluas, s.jenis_dinding_terluas,
                   s.jenis_atap_terluas, s.sumber_air_minum_utama, s.fasilitas_bab,
                   s.jenis_kloset, s.pembuangan_akhir_tinja, s.daya_terpasang,
                   s.jumlah_mobil, s.jumlah_ac, s.jumlah_sepeda_motor,
                   s.gram_emas_perhiasan, s.luas_sawah_kebun_ha,
                   s.kelengkapan_data, s.umur_data_bulan,
                   k.wilayah_id, k.kode_semu,
                   sk.skor, sk.kategori, sk.perubahan_dari_sebelumnya, sk.faktor_dominan
            FROM snapshot_keluarga s
            JOIN keluarga k ON k.id = s.keluarga_id
            LEFT JOIN skor_kerentanan sk
                   ON sk.keluarga_id = s.keluarga_id AND sk.gelombang = s.gelombang
            WHERE s.gelombang = :gel
            """
        ),
        mesin,
        params={"gel": gelombang},
    )

    peserta = pd.read_sql(
        text(
            """
            SELECT kp.keluarga_id, p.kode AS program
            FROM kepesertaan_program kp
            JOIN program p ON p.id = kp.program_id
            WHERE kp.gelombang_mulai <= :gel
              AND (kp.gelombang_selesai IS NULL OR kp.gelombang_selesai > :gel)
            """
        ),
        mesin,
        params={"gel": gelombang},
    )

    if not peserta.empty:
        lebar = (
            peserta.assign(ada=1)
            .pivot_table(index="keluarga_id", columns="program", values="ada", aggfunc="max")
            .fillna(0)
            .astype(bool)
        )
        lebar.columns = [f"prog_{c}" for c in lebar.columns]
        kondisi = kondisi.merge(lebar, on="keluarga_id", how="left")
        for c in lebar.columns:
            kondisi[c] = kondisi[c].fillna(False).astype(bool)

    return kondisi


# ===========================================================================
# Detektor
# ===========================================================================
def _ambang_prioritas(df: pd.DataFrame) -> float:
    """Hitung ambang skor yang memisahkan bagian teratas populasi.

    Dihitung dari sebaran skor yang sedang diperiksa, bukan ditetapkan sebagai
    angka tetap. Dengan begitu antrean tetap terisi secara wajar pada gelombang
    mana pun, termasuk ketika keadaan kabupaten membaik dan skor seluruh
    penduduk turun bersamaan - keadaan yang justru diharapkan terjadi.
    """
    skor = df["skor"].dropna()
    if skor.empty:
        return AMBANG_SKOR_MINIMUM
    ambang = float(skor.quantile(1.0 - PORSI_PRIORITAS))
    return max(ambang, AMBANG_SKOR_MINIMUM)


def _prioritas_dari_skor(skor: float, keyakinan: float) -> tuple[float, int]:
    """Gabungkan kerentanan dan keyakinan penandaan menjadi satu angka urut.

    Kerentanan diberi bobot dua kali keyakinan. Kasus yang sangat meyakinkan
    pada keluarga yang tidak begitu rentan tetap perlu diperiksa, tetapi bukan
    lebih dahulu daripada kasus yang agak meragukan pada keluarga yang berada
    di ujung kesulitan.
    """
    nilai = float(np.clip(0.67 * skor + 0.33 * keyakinan * 100.0, 0.0, 100.0))
    if nilai >= 85:
        tingkat = 1
    elif nilai >= 70:
        tingkat = 2
    elif nilai >= 55:
        tingkat = 3
    elif nilai >= 40:
        tingkat = 4
    else:
        tingkat = 5
    return round(nilai, 2), tingkat


def deteksi_exclusion(df: pd.DataFrame) -> list[Temuan]:
    """Keluarga sangat rentan yang belum tersentuh program relevan.

    Jenis kesalahan yang paling merugikan sekaligus paling sulit ditemukan
    dengan cara biasa, sebab yang terdampak tidak tercatat di daftar penerima
    mana pun - tidak ada berkas yang bisa diaudit untuk menemukan mereka.
    """
    hasil: list[Temuan] = []
    ambang = _ambang_prioritas(df)

    # Dua jalur, sebab keluarga dapat terlewat karena dua sebab yang berbeda.
    #
    # Jalur pertama: skor tinggi namun tidak menerima apa pun. Inilah kasus
    # klasik keluarga yang luput dari pendataan.
    #
    # Jalur kedua: desil terbawah namun tidak menerima apa pun. Keluarga ini
    # bahkan lolos dari saringan paling sederhana yang dipakai seluruh program -
    # desil kesejahteraan - sehingga tidak memerlukan model apa pun untuk
    # menemukannya. Justru karena itu keberadaannya paling sulit dijelaskan.
    # Keluarga bermasalah dokumen TIDAK dikeluarkan dari penandaan.
    #
    # Rancangan pertama mengeluarkannya, dengan alasan yang terdengar masuk akal:
    # keluarga tanpa dokumen kependudukan memang tidak dapat ditetapkan sebagai
    # penerima, jadi untuk apa ditandai. Pengukuran menunjukkan alasan itu
    # terbalik dan akibatnya besar - dari 555 keluarga miskin yang tidak
    # menerima apa pun, 420 di antaranya terhalang dokumen. Menyaringnya keluar
    # menghapus tiga perempat kasus terpenting dari antrean, dan yang tersisa
    # justru yang paling mudah ditangani.
    #
    # Keluarga yang tidak dapat dibantu KARENA dokumennya belum lengkap adalah
    # kasus paling mendesak, bukan paling layak diabaikan. Tindakannya pun jelas
    # dan murah: urus dokumen lebih dahulu, baru daftarkan ke program. Penandaan
    # ini menyertakan keterangan itu agar petugas tidak berangkat membawa
    # formulir pendaftaran yang pasti ditolak.
    tanpa_program = df["jumlah_program_diterima"] == 0
    penanda = tanpa_program & (
        ((df["skor"].fillna(0) >= ambang) & (df["desil_kesejahteraan"] <= 4))
        | ((df["desil_kesejahteraan"] <= 2) & (df["skor"].fillna(0) >= AMBANG_SKOR_MINIMUM))
    )
    for _, r in df[penanda].iterrows():
        alasan = [
            {
                "kode": "skor_tinggi",
                "ringkasan": f"Skor kerentanan {r['skor']:.0f} dari 100",
                "bukti": {"skor": float(r["skor"]), "kategori": r["kategori"]},
                "keyakinan": "tinggi",
            },
            {
                "kode": "desil_bawah",
                "ringkasan": f"Desil kesejahteraan {int(r['desil_kesejahteraan'])} - termasuk sasaran program reguler",
                "bukti": {"desil": int(r["desil_kesejahteraan"])},
                "keyakinan": "tinggi",
            },
            {
                "kode": "tanpa_program",
                "ringkasan": "Tidak menerima satu pun program bantuan",
                "bukti": {"jumlah_program": 0},
                "keyakinan": "tinggi",
            },
        ]
        terhalang_dokumen = int(r["jumlah_tanpa_dokumen"]) > 0
        if terhalang_dokumen:
            alasan.append(
                {
                    "kode": "terhalang_dokumen",
                    "ringkasan": (
                        f"{int(r['jumlah_tanpa_dokumen'])} anggota belum memiliki dokumen "
                        "kependudukan yang sah - inilah penghalangnya, bukan kelayakannya"
                    ),
                    "bukti": {"jumlah_tanpa_dokumen": int(r["jumlah_tanpa_dokumen"])},
                    "keyakinan": "tinggi",
                }
            )

        skor_p, tingkat = _prioritas_dari_skor(float(r["skor"]), 0.95)
        hasil.append(
            Temuan(
                keluarga_id=int(r["keluarga_id"]),
                gelombang=int(r["gelombang"]),
                jenis=JenisAnomali.EXCLUSION_MISMATCH,
                skor_prioritas=skor_p,
                tingkat_prioritas=tingkat,
                alasan=alasan,
                ringkasan=(
                    (
                        f"Keluarga berisiko {r['kategori']} pada desil "
                        f"{int(r['desil_kesejahteraan'])} belum menerima bantuan apa pun, "
                        "dan penghalangnya adalah dokumen kependudukan yang belum lengkap. "
                        "Urus dokumen lebih dahulu; pendaftaran program sebelum itu akan ditolak."
                    )
                    if terhalang_dokumen
                    else (
                        f"Keluarga berisiko {r['kategori']} pada desil "
                        f"{int(r['desil_kesejahteraan'])} namun belum menerima bantuan apa pun."
                    )
                ),
                opd_disarankan="disdukcapil" if terhalang_dokumen else "dinsos",
            )
        )
    return hasil


def deteksi_inclusion(df: pd.DataFrame) -> list[Temuan]:
    """Penerima yang kondisinya sudah membaik melewati ambang kelayakan."""
    hasil: list[Temuan] = []
    penanda = (
        (df["desil_kesejahteraan"] >= DESIL_LEWAT_AMBANG)
        & (df["jumlah_program_diterima"] > 0)
    )
    for _, r in df[penanda].iterrows():
        skor = float(r["skor"]) if pd.notna(r["skor"]) else 20.0
        alasan = [
            {
                "kode": "desil_naik",
                "ringkasan": f"Desil kesejahteraan kini {int(r['desil_kesejahteraan'])}, di luar sasaran program reguler",
                "bukti": {"desil": int(r["desil_kesejahteraan"])},
                "keyakinan": "sedang",
            },
            {
                "kode": "masih_menerima",
                "ringkasan": f"Masih menerima {int(r['jumlah_program_diterima'])} program",
                "bukti": {
                    "jumlah_program": int(r["jumlah_program_diterima"]),
                    "nilai_bulanan": float(r["nilai_bantuan_bulanan"]),
                },
                "keyakinan": "tinggi",
            },
        ]
        # Prioritas sengaja DIBALIK arahnya: makin rendah kerentanan, makin
        # jelas ketidaksesuaiannya. Namun tetap ditempatkan di bawah kasus
        # keluarga yang terlewat - memindahkan bantuan tidak sedesak
        # menjangkau yang belum tersentuh sama sekali.
        skor_p, tingkat = _prioritas_dari_skor(max(0.0, 55.0 - skor), 0.7)
        hasil.append(
            Temuan(
                keluarga_id=int(r["keluarga_id"]),
                gelombang=int(r["gelombang"]),
                jenis=JenisAnomali.INCLUSION_MISMATCH,
                skor_prioritas=skor_p,
                tingkat_prioritas=max(3, tingkat),
                alasan=alasan,
                ringkasan=(
                    "Kondisi keluarga membaik melewati ambang kelayakan namun bantuan "
                    "masih berjalan. Perlu verifikasi sebelum penetapan ulang sasaran."
                ),
                opd_disarankan="dinsos",
            )
        )
    return hasil


def deteksi_duplikasi(df: pd.DataFrame) -> list[Temuan]:
    """Keluarga menerima beberapa program yang manfaatnya bertumpuk."""
    hasil: list[Temuan] = []
    for a, b, kebutuhan in PROGRAM_BERTUMPUK:
        ka, kb = f"prog_{a}", f"prog_{b}"
        if ka not in df.columns or kb not in df.columns:
            continue
        penanda = df[ka] & df[kb]
        for _, r in df[penanda].iterrows():
            skor_p, tingkat = _prioritas_dari_skor(45.0, 0.8)
            hasil.append(
                Temuan(
                    keluarga_id=int(r["keluarga_id"]),
                    gelombang=int(r["gelombang"]),
                    jenis=JenisAnomali.DUPLIKASI_BANTUAN,
                    skor_prioritas=skor_p,
                    tingkat_prioritas=tingkat,
                    alasan=[
                        {
                            "kode": "manfaat_bertumpuk",
                            "ringkasan": f"Menerima {a} dan {b} yang sama-sama menangani {kebutuhan}",
                            "bukti": {"program": [a, b], "kebutuhan": kebutuhan},
                            "keyakinan": "tinggi",
                        }
                    ],
                    ringkasan=(
                        f"Kebutuhan {kebutuhan} terlayani dua program sekaligus. "
                        "Salah satunya dapat dialihkan ke keluarga lain yang belum terlayani."
                    ),
                    opd_disarankan="dinsos",
                )
            )
    return hasil


def deteksi_inkonsistensi(df: pd.DataFrame) -> list[Temuan]:
    """Isian data yang saling bertentangan.

    Ditemukan lewat aturan, bukan model. Untuk kejanggalan yang dapat
    dinyatakan setegas ini - keluarga desil satu yang memiliki mobil - aturan
    lebih tepat daripada model: hasilnya pasti, dapat dijelaskan dalam satu
    kalimat, dan tidak berubah ketika model dilatih ulang.
    """
    hasil: list[Temuan] = []

    pemeriksaan = [
        (
            (df["desil_kesejahteraan"] <= 2) & (df["jumlah_mobil"] > 0),
            "aset_tidak_sesuai_desil",
            "Tercatat pada desil terbawah namun memiliki mobil",
        ),
        (
            (df["desil_kesejahteraan"] <= 2) & (df["jumlah_ac"] > 0),
            "aset_tidak_sesuai_desil",
            "Tercatat pada desil terbawah namun memiliki pendingin ruangan",
        ),
        (
            (df["desil_kesejahteraan"] <= 2) & (df["luas_sawah_kebun_ha"] > 2.0),
            "lahan_luas_desil_bawah",
            "Tercatat pada desil terbawah namun menguasai lahan lebih dari dua hektar",
        ),
        (
            (df["desil_kesejahteraan"] >= 5) & (df["daya_terpasang"] == 0),
            "listrik_tidak_sesuai_desil",
            "Tercatat pada desil menengah namun rumahnya tidak berlistrik",
        ),
        (
            (df["jumlah_ber_jkn"] > df["jumlah_anggota"]),
            "jumlah_tidak_masuk_akal",
            "Jumlah anggota berjaminan kesehatan melebihi jumlah anggota keluarga",
        ),
        (
            (df["luas_lantai_m2"] / df["jumlah_anggota"].clip(lower=1)) < 2.0,
            "luas_tidak_masuk_akal",
            "Luas lantai per orang di bawah dua meter persegi - kemungkinan salah catat",
        ),
    ]

    for penanda, kode, kalimat in pemeriksaan:
        for _, r in df[penanda.fillna(False)].iterrows():
            skor_p, tingkat = _prioritas_dari_skor(40.0, 0.85)
            hasil.append(
                Temuan(
                    keluarga_id=int(r["keluarga_id"]),
                    gelombang=int(r["gelombang"]),
                    jenis=JenisAnomali.INKONSISTENSI_DATA,
                    skor_prioritas=skor_p,
                    tingkat_prioritas=tingkat,
                    alasan=[
                        {
                            "kode": kode,
                            "ringkasan": kalimat,
                            "bukti": {
                                "desil": int(r["desil_kesejahteraan"]),
                                "kelengkapan_data": float(r["kelengkapan_data"]),
                            },
                            "keyakinan": "tinggi",
                        }
                    ],
                    ringkasan=kalimat + ". Perlu pemeriksaan ulang isian data.",
                    opd_disarankan="dinsos",
                )
            )
    return hasil


def deteksi_perubahan_belum_ditindak(df: pd.DataFrame) -> list[Temuan]:
    """Kondisi memburuk tajam namun penanganan belum berubah.

    Inilah jenis kasus yang paling menjelaskan alasan keberadaan NADI. Keluarga
    ini belum tentu miskin hari ini, dan karena itu tidak muncul pada daftar
    mana pun. Yang berubah bukan keadaannya, melainkan arahnya.
    """
    hasil: list[Temuan] = []
    # Lonjakan diukur relatif terhadap sebaran perubahan pada gelombang ini,
    # bukan terhadap angka tetap. Pada gelombang yang tenang, dua belas poin
    # sudah termasuk lonjakan tajam; pada gelombang penuh guncangan, ambang yang
    # sama akan menandai terlalu banyak keluarga sekaligus.
    perubahan = df["perubahan_dari_sebelumnya"].fillna(0)
    naik = perubahan[perubahan > 0]
    ambang_naik = float(naik.quantile(0.95)) if len(naik) > 50 else 8.0
    ambang_naik = max(ambang_naik, 5.0)
    penanda = (perubahan >= ambang_naik) & (df["skor"].fillna(0) >= AMBANG_SKOR_MINIMUM)
    for _, r in df[penanda].iterrows():
        naik = float(r["perubahan_dari_sebelumnya"])
        faktor = _baca_faktor(r.get("faktor_dominan"))
        alasan = [
            {
                "kode": "skor_melonjak",
                "ringkasan": f"Skor kerentanan naik {naik:.0f} poin sejak pemutakhiran sebelumnya",
                "bukti": {"skor_kini": float(r["skor"]), "kenaikan": naik},
                "keyakinan": "tinggi",
            }
        ]
        if faktor:
            alasan.append(
                {
                    "kode": "faktor_pendorong",
                    "ringkasan": "Faktor pendorong utama: " + ", ".join(faktor[:3]),
                    "bukti": {"faktor": faktor[:3]},
                    "keyakinan": "sedang",
                }
            )
        if int(r["jumlah_program_diterima"]) == 0:
            alasan.append(
                {
                    "kode": "belum_ditangani",
                    "ringkasan": "Belum menerima program apa pun meski risiko meningkat",
                    "bukti": {"jumlah_program": 0},
                    "keyakinan": "tinggi",
                }
            )

        skor_p, tingkat = _prioritas_dari_skor(float(r["skor"]) + naik * 0.5, 0.85)
        hasil.append(
            Temuan(
                keluarga_id=int(r["keluarga_id"]),
                gelombang=int(r["gelombang"]),
                jenis=JenisAnomali.PERUBAHAN_BELUM_DITINDAK,
                skor_prioritas=skor_p,
                tingkat_prioritas=tingkat,
                alasan=alasan,
                ringkasan=(
                    f"Risiko keluarga ini meningkat tajam ({naik:+.0f} poin) namun "
                    "penanganannya belum berubah."
                ),
                opd_disarankan="dinsos",
            )
        )
    return hasil


def deteksi_data_kedaluwarsa(df: pd.DataFrame) -> list[Temuan]:
    """Data lama pada keluarga berisiko tinggi.

    Data usang bukan sekadar persoalan kerapian. Pada keluarga berisiko, tidak
    mengetahui keadaan terkini adalah risiko tersendiri - dan satu-satunya
    jenis risiko yang dapat dihapus hanya dengan berkunjung.
    """
    hasil: list[Temuan] = []
    penanda = (df["umur_data_bulan"] >= BATAS_UMUR_DATA_BULAN) & (
        df["skor"].fillna(0) >= _ambang_prioritas(df)
    )
    for _, r in df[penanda].iterrows():
        skor_p, tingkat = _prioritas_dari_skor(float(r["skor"]), 0.6)
        hasil.append(
            Temuan(
                keluarga_id=int(r["keluarga_id"]),
                gelombang=int(r["gelombang"]),
                jenis=JenisAnomali.DATA_KEDALUWARSA,
                skor_prioritas=skor_p,
                tingkat_prioritas=max(3, tingkat),
                alasan=[
                    {
                        "kode": "data_lama",
                        "ringkasan": f"Data terakhir dimutakhirkan {int(r['umur_data_bulan'])} bulan lalu",
                        "bukti": {
                            "umur_data_bulan": int(r["umur_data_bulan"]),
                            "kelengkapan": float(r["kelengkapan_data"]),
                        },
                        "keyakinan": "tinggi",
                    }
                ],
                ringkasan=(
                    "Keluarga berisiko tinggi dengan data yang sudah lama tidak "
                    "dimutakhirkan. Skornya dihitung dari keadaan yang mungkin sudah berubah."
                ),
                opd_disarankan="dinsos",
            )
        )
    return hasil


def deteksi_pola_tidak_lazim(df: pd.DataFrame, porsi: float = 0.01) -> list[Temuan]:
    """Keluarga yang polanya menyimpang dari keluarga sebanding.

    Memakai Isolation Forest, satu-satunya detektor di modul ini yang berbasis
    model dan bukan aturan. Perannya melengkapi, bukan menggantikan: aturan
    menemukan kejanggalan yang sudah terpikirkan, sedangkan pencilan statistik
    menemukan yang belum. Karena tidak dapat menjelaskan dirinya sendiri
    sebaik aturan, keyakinannya ditandai lebih rendah dan prioritasnya
    diletakkan di bawah kasus berbasis aturan.
    """
    from sklearn.ensemble import IsolationForest

    kolom = [
        "desil_kesejahteraan",
        "jumlah_anggota",
        "luas_lantai_m2",
        "daya_terpasang",
        "jumlah_sepeda_motor",
        "gram_emas_perhiasan",
        "luas_sawah_kebun_ha",
        "jumlah_program_diterima",
        "nilai_bantuan_bulanan",
        "jumlah_ber_jkn",
    ]
    tersedia = [k for k in kolom if k in df.columns]
    if len(tersedia) < 5 or len(df) < 500:
        return []

    X = df[tersedia].fillna(0.0).to_numpy(dtype=float)
    model = IsolationForest(
        n_estimators=150, contamination=porsi, random_state=20260913, n_jobs=-1
    )
    label = model.fit_predict(X)
    nilai = model.score_samples(X)

    hasil: list[Temuan] = []
    for i in np.flatnonzero(label == -1):
        r = df.iloc[i]
        keanehan = float(-nilai[i])
        skor_p, tingkat = _prioritas_dari_skor(float(r["skor"]) if pd.notna(r["skor"]) else 35.0, 0.45)
        hasil.append(
            Temuan(
                keluarga_id=int(r["keluarga_id"]),
                gelombang=int(r["gelombang"]),
                jenis=JenisAnomali.POLA_TIDAK_LAZIM,
                skor_prioritas=skor_p,
                tingkat_prioritas=max(4, tingkat),
                sumber_deteksi="statistik",
                alasan=[
                    {
                        "kode": "pencilan_statistik",
                        "ringkasan": (
                            "Pola data keluarga ini menyimpang dari keluarga sebanding "
                            "di wilayahnya"
                        ),
                        "bukti": {"nilai_keanehan": round(keanehan, 4)},
                        "keyakinan": "rendah",
                    }
                ],
                ringkasan=(
                    "Terdeteksi sebagai pencilan statistik. Penandaan ini tidak "
                    "menyebut kesalahan tertentu, hanya menyarankan pemeriksaan."
                ),
                opd_disarankan="dinsos",
            )
        )
    return hasil


def _baca_faktor(nilai: Any) -> list[str]:
    if nilai is None or (isinstance(nilai, float) and pd.isna(nilai)):
        return []
    try:
        kode = json.loads(nilai) if isinstance(nilai, str) else list(nilai)
    except (ValueError, TypeError):
        return []
    from nadi.ml.baseline import IndeksDasar

    katalog = {f["kode"]: f["nama"] for f in IndeksDasar.dari_berkas().faktor}
    return [katalog.get(k, k) for k in kode]


# ===========================================================================
# Titik masuk
# ===========================================================================
DETEKTOR = (
    ("exclusion", deteksi_exclusion),
    ("perubahan", deteksi_perubahan_belum_ditindak),
    ("inklusi", deteksi_inclusion),
    ("duplikasi", deteksi_duplikasi),
    ("inkonsistensi", deteksi_inkonsistensi),
    ("kedaluwarsa", deteksi_data_kedaluwarsa),
    ("pola", deteksi_pola_tidak_lazim),
)


def jalankan_deteksi(mesin: Engine, gelombang: int) -> list[Temuan]:
    """Jalankan seluruh detektor pada satu gelombang."""
    df = muat_bahan_deteksi(mesin, gelombang)
    if df.empty:
        logger.warning("Tidak ada data pada gelombang %d.", gelombang)
        return []

    semua: list[Temuan] = []
    for nama, fungsi in DETEKTOR:
        try:
            temuan = fungsi(df)
        except Exception as exc:  # noqa: BLE001 - satu detektor gagal tidak boleh menggagalkan sisanya
            logger.exception("Detektor '%s' gagal: %s", nama, exc)
            continue
        logger.info("  detektor %-14s menemukan %5d kasus", nama, len(temuan))
        semua.extend(temuan)

    semua.sort(key=lambda t: (-t.skor_prioritas, t.tingkat_prioritas))
    return semua


__all__ = [
    "AMBANG_SKOR_MINIMUM",
    "PORSI_PRIORITAS",
    "BATAS_UMUR_DATA_BULAN",
    "DETEKTOR",
    "PROGRAM_BERTUMPUK",
    "RingkasanDeteksi",
    "Temuan",
    "jalankan_deteksi",
    "muat_bahan_deteksi",
]
