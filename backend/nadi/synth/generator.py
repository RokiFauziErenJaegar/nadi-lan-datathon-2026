"""Orkestrator pembangkitan dataset lengkap.

Merangkai seluruh bagian generator dan menuliskannya ke basis data:

    wilayah -> keluarga -> anggota -> panel kondisi -> guncangan -> kepesertaan

Penulisan memakai pandas ``to_sql`` alih-alih objek ORM. Untuk seperempat juta
baris kondisi keluarga, membentuk objek Python satu per satu memakan waktu
berkali lipat tanpa memberi manfaat apa pun - tidak ada aturan bisnis yang
perlu dijalankan saat memuat data awal. Nilai enumerasi ditulis sebagai kode
mentah, persis seperti bentuk penyimpanannya, sehingga pembacaan lewat ORM
tetap menghasilkan objek enumerasi yang bertipe.

Seluruh isi dataset bersifat sintetis. Tidak ada satu pun keluarga nyata di
dalamnya.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from nadi.config import settings
from nadi.db.enums import JenisWilayah, StatusKepesertaan
from nadi.db.models import Program, Wilayah
from nadi.db.session import mesin
from nadi.security.pseudonym import kode_individu, kode_keluarga
from nadi.synth.dinamika import PanelSintetis, bangkitkan_panel
from nadi.synth.hunian import bangkitkan_hunian_dan_aset
from nadi.synth.keluarga import PopulasiSintetis, bangkitkan_populasi
from nadi.synth.parameter import PARAMETER

logger = logging.getLogger("nadi.synth")

#: Radius pergeseran koordinat dalam derajat. Satu derajat lintang kira-kira
#: 111 kilometer, sehingga 250 meter setara sekitar 0,00225 derajat.
_DERAJAT_PER_METER = 1.0 / 111_000.0

#: Cap waktu tetap untuk seluruh baris yang dimuat, demi hasil yang dapat
#: diulang persis. Menggunakan waktu berjalan akan membuat dua kali pembangkitan
#: menghasilkan berkas yang berbeda meski isinya sama.
_WAKTU_MUAT = datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)


@dataclass
class RingkasanDataset:
    """Ringkasan hasil pembangkitan, untuk dilaporkan dan diperiksa."""

    jumlah_wilayah: int = 0
    jumlah_keluarga: int = 0
    jumlah_anggota: int = 0
    jumlah_snapshot: int = 0
    jumlah_guncangan: int = 0
    jumlah_kepesertaan: int = 0
    jumlah_gelombang: int = 0
    detik: float = 0.0
    kalibrasi: list[dict] = field(default_factory=list)

    def ringkas(self) -> str:
        return (
            f"{self.jumlah_keluarga:,} keluarga, {self.jumlah_anggota:,} anggota, "
            f"{self.jumlah_snapshot:,} kondisi, {self.jumlah_guncangan:,} guncangan, "
            f"{self.jumlah_kepesertaan:,} kepesertaan "
            f"dalam {self.detik:.1f} detik"
        ).replace(",", ".")


# ===========================================================================
# Wilayah
# ===========================================================================
def muat_wilayah(sesi: Session, berkas: Path | None = None) -> dict[str, int]:
    """Muat struktur wilayah dari berkas data awal.

    Returns:
        Peta kode wilayah ke pengenal barisnya di basis data.
    """
    import json

    berkas = berkas or (settings.seed_dir / "wilayah.json")
    data = json.loads(berkas.read_text(encoding="utf-8"))["wilayah"]

    peta: dict[str, int] = {}
    # Diurutkan menurut tingkat agar induk selalu tersimpan sebelum anaknya.
    for butir in sorted(data, key=lambda w: w["tingkat"]):
        kode = butir["kode"]
        obj = sesi.scalar(select(Wilayah).where(Wilayah.kode == kode))
        if obj is None:
            obj = Wilayah(kode=kode)
            sesi.add(obj)

        obj.nama = butir["nama"]
        obj.jenis = JenisWilayah(butir["jenis"])
        obj.tingkat = butir["tingkat"]
        obj.lintang = butir.get("lintang")
        obj.bujur = butir.get("bujur")
        obj.luas_km2 = butir.get("luas_km2")
        obj.jumlah_penduduk = butir.get("jumlah_penduduk")
        obj.klasifikasi = butir.get("klasifikasi")

        induk_kode = butir.get("induk")
        obj.induk_id = peta.get(induk_kode) if induk_kode else None
        obj.jalur = f"{induk_kode}/{kode}" if induk_kode else kode
        if induk_kode and induk_kode in peta:
            induk = sesi.get(Wilayah, peta[induk_kode])
            if induk is not None:
                obj.jalur = f"{induk.jalur}/{kode}"

        sesi.flush()
        peta[kode] = obj.id

    logger.info("Wilayah dimuat: %d baris.", len(peta))
    return peta


# ===========================================================================
# Pembantu penulisan
# ===========================================================================
#: Batas jumlah parameter terikat pada satu pernyataan SQLite.
#: Versi lama membatasi 999, versi baru 32.766. Nilai aman dipakai agar
#: penulisan tetap berhasil pada penafsir Python mana pun.
_BATAS_PARAMETER_SQLITE = 900


def _tulis(nama_tabel: str, df: pd.DataFrame, koneksi, potongan: int = 5_000) -> int:
    """Tulis bingkai data ke tabel, sepotong demi sepotong.

    Penulisan memakai koneksi SESI yang sedang berjalan, bukan objek mesin.
    Mengambil koneksi baru dari kumpulan saat transaksi luar sedang memegang
    kunci tulis akan membuat keduanya saling menunggu, dan SQLite menjawabnya
    dengan galat "database is locked".

    Penyisipan memakai ``executemany`` bawaan, BUKAN ``method="multi"``.
    Perbedaannya sempat menggagalkan pemuatan: mode ``multi`` menggabungkan
    seluruh potongan menjadi satu pernyataan raksasa, sehingga lima ribu baris
    dikali dua puluh empat kolom menghasilkan seratus dua puluh ribu parameter
    terikat - jauh melampaui batas SQLite dan berujung galat "too many SQL
    variables". Cara bawaan mengirim satu pernyataan yang dijalankan berulang,
    yang justru lebih cepat pada SQLite sekaligus tidak memiliki batas itu.
    """
    if df.empty:
        return 0
    aman = max(1, min(potongan, _BATAS_PARAMETER_SQLITE * 20 // max(1, len(df.columns))))
    df.to_sql(
        nama_tabel,
        koneksi,
        if_exists="append",
        index=False,
        chunksize=aman,
    )
    return len(df)


def _tambah_cap_waktu(df: pd.DataFrame) -> pd.DataFrame:
    df["dibuat_pada"] = _WAKTU_MUAT
    df["diperbarui_pada"] = _WAKTU_MUAT
    return df


def _tanggal_gelombang(t: int) -> date:
    """Tanggal acuan sebuah gelombang.

    Gelombang nol jatuh pada Maret 2023, mengikuti waktu pencacahan Susenas,
    lalu berjarak enam bulan.
    """
    bulan_total = (PARAMETER.bulan_awal - 1) + t * PARAMETER.bulan_per_gelombang
    tahun = PARAMETER.tahun_awal + bulan_total // 12
    bulan = bulan_total % 12 + 1
    return date(tahun, bulan, 1)


# ===========================================================================
# Pembangkit utama
# ===========================================================================
def bangkitkan_dataset(
    sesi: Session,
    *,
    jumlah_keluarga: int | None = None,
    jumlah_gelombang: int | None = None,
    benih: int | None = None,
) -> RingkasanDataset:
    """Bangkitkan dan simpan dataset sintetis lengkap."""
    mulai = time.perf_counter()
    n = jumlah_keluarga or PARAMETER.jumlah_keluarga
    T = jumlah_gelombang or PARAMETER.jumlah_gelombang
    rng = np.random.default_rng(benih or PARAMETER.benih_acak)

    ringkasan = RingkasanDataset(jumlah_gelombang=T)

    # -----------------------------------------------------------------
    # 1. Wilayah
    # -----------------------------------------------------------------
    peta_wilayah = muat_wilayah(sesi)
    sesi.commit()
    ringkasan.jumlah_wilayah = len(peta_wilayah)

    # Koneksi diambil SESUDAH commit di atas. Commit melepas koneksi yang
    # sedang dipegang sesi, sehingga rujukan yang diambil sebelumnya menjadi
    # basi dan penulisan berikutnya gagal tanpa pesan yang menjelaskan.
    koneksi = sesi.connection()

    desa = (
        sesi.execute(select(Wilayah).where(Wilayah.tingkat == 2).order_by(Wilayah.kode))
        .scalars()
        .all()
    )
    if not desa:
        raise RuntimeError("Tidak ada wilayah tingkat desa. Jalankan siapkan_wilayah.py lebih dahulu.")

    import json

    seed_wilayah = json.loads(
        (settings.seed_dir / "wilayah.json").read_text(encoding="utf-8")
    )["wilayah"]
    efek_per_kode = {w["kode"]: w.get("efek_ekonomi", 0.0) for w in seed_wilayah}

    id_desa = np.array([d.id for d in desa])
    lintang_desa = np.array([d.lintang or 0.0 for d in desa])
    bujur_desa = np.array([d.bujur or 0.0 for d in desa])
    bobot = np.array([float(d.jumlah_penduduk or 1) for d in desa])
    bobot = bobot / bobot.sum()
    efek = np.array([efek_per_kode.get(d.kode, 0.0) for d in desa])

    # -----------------------------------------------------------------
    # 2. Populasi dan hunian
    # -----------------------------------------------------------------
    logger.info("Membangkitkan %d keluarga pada %d wilayah...", n, len(desa))
    pop = bangkitkan_populasi(n, bobot, efek, rng)
    hunian_awal = bangkitkan_hunian_dan_aset(
        pop.kemampuan_laten, pop.kk_lapangan_usaha, pop.jumlah_anggota, rng
    )

    # -----------------------------------------------------------------
    # 3. Panel
    # -----------------------------------------------------------------
    panel = bangkitkan_panel(
        kemampuan=pop.kemampuan_laten,
        jumlah_anggota=pop.jumlah_anggota,
        lapangan_usaha=pop.kk_lapangan_usaha,
        ada_penyakit_kronis=pop.ada_penyakit_kronis,
        jumlah_anak_sekolah=pop.jumlah_anak_sekolah,
        jumlah_balita=pop.jumlah_balita,
        jumlah_lansia=pop.jumlah_lansia,
        jumlah_disabilitas=pop.jumlah_disabilitas,
        jumlah_ibu_hamil=pop.jumlah_ibu_hamil,
        jumlah_ber_jkn=pop.jumlah_ber_jkn,
        jumlah_tanpa_dokumen=pop.jumlah_tanpa_dokumen,
        hunian_awal=hunian_awal,
        rng=rng,
        jumlah_gelombang=T,
    )
    ringkasan.kalibrasi = panel.catatan_kalibrasi

    # -----------------------------------------------------------------
    # 4. Tulis keluarga
    # -----------------------------------------------------------------
    id_keluarga = np.arange(1, n + 1, dtype=np.int64)
    wilayah_id = id_desa[pop.wilayah_idx]

    # Koordinat digeser acak dalam radius yang ditetapkan. Diterapkan meski
    # data ini sintetis, sebab kode yang sama kelak berjalan pada data
    # sesungguhnya - kebiasaan yang dibangun sejak awal lebih dapat diandalkan
    # daripada penyesuaian yang ditambahkan belakangan.
    radius = PARAMETER.pergeseran_koordinat_meter * _DERAJAT_PER_METER
    sudut = rng.uniform(0, 2 * np.pi, n)
    jarak = radius * np.sqrt(rng.uniform(0, 1, n))
    lintang = lintang_desa[pop.wilayah_idx] + jarak * np.cos(sudut)
    bujur = bujur_desa[pop.wilayah_idx] + jarak * np.sin(sudut) / np.cos(np.radians(-5.34))

    df_keluarga = pd.DataFrame(
        {
            "id": id_keluarga,
            "kode_semu": [kode_keluarga(int(i)) for i in id_keluarga],
            "wilayah_id": wilayah_id,
            "lintang": np.round(lintang, 5),
            "bujur": np.round(bujur, 5),
            "tanggal_terdaftar": _tanggal_gelombang(0),
            "sumber_data": "sintetis",
            "aktif": True,
        }
    )
    ringkasan.jumlah_keluarga = _tulis("keluarga", koneksi, _tambah_cap_waktu(df_keluarga))

    # -----------------------------------------------------------------
    # 5. Tulis anggota keluarga
    # -----------------------------------------------------------------
    tahun_awal = PARAMETER.tahun_awal
    n_ang = pop.n_anggota
    id_anggota = np.arange(1, n_ang + 1, dtype=np.int64)
    df_anggota = pd.DataFrame(
        {
            "id": id_anggota,
            "keluarga_id": id_keluarga[pop.anggota_keluarga_idx],
            "urutan": pop.anggota_urutan,
            "kode_semu": [kode_individu(int(i)) for i in id_anggota],
            "hubungan_kk": pop.anggota_hubungan,
            "jenis_kelamin": pop.anggota_jenis_kelamin,
            "tahun_lahir": tahun_awal - pop.anggota_umur,
            "status_perkawinan": pop.anggota_status_perkawinan,
            "partisipasi_sekolah": pop.anggota_partisipasi_sekolah,
            "pendidikan_tertinggi": pop.anggota_pendidikan,
            "status_kegiatan": pop.anggota_status_kegiatan,
            "lapangan_usaha": np.where(
                pop.anggota_status_kegiatan == 1,
                pop.kk_lapangan_usaha[pop.anggota_keluarga_idx],
                20,
            ),
            "status_pekerjaan": np.where(
                pop.anggota_status_kegiatan == 1,
                pop.kk_status_pekerjaan[pop.anggota_keluarga_idx],
                8,
            ),
            "jumlah_usaha": pop.anggota_jumlah_usaha,
            "jenis_disabilitas": pop.anggota_disabilitas,
            "penyakit_kronis": pop.anggota_penyakit_kronis,
            "status_gizi_balita": pop.anggota_gizi,
            "sedang_hamil": pop.anggota_hamil,
            "punya_jaminan_kesehatan": pop.anggota_jkn,
            "gelombang_masuk": 0,
            "gelombang_keluar": None,
            "sebab_keluar": None,
        }
    )
    ringkasan.jumlah_anggota = _tulis("anggota_keluarga", koneksi, _tambah_cap_waktu(df_anggota))

    # -----------------------------------------------------------------
    # 6. Tulis kondisi per gelombang
    # -----------------------------------------------------------------
    total_snapshot = 0
    for t in range(T):
        df = _bingkai_snapshot(t, id_keluarga, pop, panel, hunian=panel.hunian_per_gelombang[t])
        total_snapshot += _tulis("snapshot_keluarga", koneksi, _tambah_cap_waktu(df))
    ringkasan.jumlah_snapshot = total_snapshot

    # -----------------------------------------------------------------
    # 7. Tulis guncangan
    # -----------------------------------------------------------------
    g = panel.guncangan
    if g.keluarga_idx.size:
        tanggal = np.array([_tanggal_gelombang(int(w)) for w in g.gelombang])
        df_g = pd.DataFrame(
            {
                "keluarga_id": id_keluarga[g.keluarga_idx],
                "gelombang": g.gelombang,
                "tanggal_kejadian": tanggal,
                "jenis": g.jenis,
                "keparahan": g.keparahan,
                "dampak_pendapatan_persen": np.round(g.dampak, 1),
                "keterangan": None,
                "rincian": None,
            }
        )
        ringkasan.jumlah_guncangan = _tulis("guncangan", koneksi, _tambah_cap_waktu(df_g))

    # -----------------------------------------------------------------
    # 8. Tulis kepesertaan program
    # -----------------------------------------------------------------
    ringkasan.jumlah_kepesertaan = _tulis_kepesertaan(sesi, id_keluarga, pop, panel, T)

    ringkasan.detik = time.perf_counter() - mulai
    logger.info("Dataset sintetis selesai: %s", ringkasan.ringkas())
    return ringkasan


# ---------------------------------------------------------------------------
def _bingkai_snapshot(
    t: int,
    id_keluarga: np.ndarray,
    pop: PopulasiSintetis,
    panel: PanelSintetis,
    hunian: dict[str, np.ndarray],
) -> pd.DataFrame:
    """Susun bingkai data kondisi keluarga untuk satu gelombang."""
    bulan_berlalu = t * PARAMETER.bulan_per_gelombang
    umur_kk = pop.kk_umur + bulan_berlalu // 12
    jumlah_anggota = pop.jumlah_anggota
    bekerja = np.maximum(pop.jumlah_bekerja, 0)
    tanggungan = (jumlah_anggota - bekerja) / np.maximum(1, bekerja)

    data: dict[str, Any] = {
        "keluarga_id": id_keluarga,
        "gelombang": t,
        "tanggal_kondisi": _tanggal_gelombang(t),
        # --- Ekonomi ---
        "pengeluaran_per_kapita": np.round(panel.pengeluaran_per_kapita[t], 0),
        "pendapatan_bulanan": np.round(
            panel.pengeluaran_per_kapita[t] * jumlah_anggota * 1.12, 0
        ),
        "desil_kesejahteraan": panel.desil[t],
        "peringkat_kesejahteraan": np.round(
            panel.pengeluaran_per_kapita[t].argsort().argsort()
            / max(1, len(id_keluarga) - 1),
            4,
        ),
        "status_miskin": panel.status_miskin[t],
        "rasio_garis_kemiskinan": np.round(panel.rasio_garis_kemiskinan[t], 4),
        # --- Susunan keluarga ---
        "jumlah_anggota": jumlah_anggota,
        "jumlah_balita": pop.jumlah_balita,
        "jumlah_anak_usia_sekolah": pop.jumlah_anak_sekolah,
        "jumlah_lansia": pop.jumlah_lansia,
        "jumlah_disabilitas": pop.jumlah_disabilitas,
        "jumlah_bekerja": bekerja,
        "rasio_tanggungan": np.round(tanggungan, 3),
        # --- Kepala keluarga ---
        "kk_umur": umur_kk,
        "kk_jenis_kelamin": pop.kk_jenis_kelamin,
        "kk_pendidikan": pop.kk_pendidikan,
        "kk_status_kegiatan": pop.kk_status_kegiatan,
        "kk_lapangan_usaha": pop.kk_lapangan_usaha,
        "kk_status_pekerjaan": pop.kk_status_pekerjaan,
        # --- Kesehatan dan pendidikan ---
        "ada_penyakit_kronis": pop.ada_penyakit_kronis,
        "ada_penyakit_biaya_tinggi": _penyakit_biaya_tinggi(pop),
        "ada_gizi_bermasalah": pop.ada_gizi_bermasalah,
        "jumlah_ber_jkn": panel.jumlah_ber_jkn[t],
        "jumlah_ibu_hamil": pop.jumlah_ibu_hamil,
        "jumlah_tanpa_dokumen": pop.jumlah_tanpa_dokumen,
        "ada_anak_putus_sekolah": _ada_putus_sekolah(pop),
        "rata_lama_sekolah_dewasa": np.round(pop.rata_lama_sekolah_dewasa, 2),
        "jumlah_usaha_keluarga": pop.jumlah_usaha_keluarga,
        # --- Perlindungan sosial ---
        "jumlah_program_diterima": panel.jumlah_program_diterima[t],
        "nilai_bantuan_bulanan": np.round(panel.nilai_bantuan_bulanan[t], 0),
        # --- Kualitas data ---
        "kelengkapan_data": np.round(panel.kelengkapan_data[t], 3),
        "umur_data_bulan": panel.umur_data_bulan[t],
    }
    data.update(hunian)
    return pd.DataFrame(data)


def _penyakit_biaya_tinggi(pop: PopulasiSintetis) -> np.ndarray:
    """Apakah ada anggota berpenyakit yang biayanya mampu menjatuhkan keluarga."""
    from nadi.db.enums import PenyakitKronis

    kode_berat = [j.value for j in PenyakitKronis if j.biaya_tinggi]
    penanda = np.isin(pop.anggota_penyakit_kronis, kode_berat)
    return np.bincount(pop.anggota_keluarga_idx[penanda], minlength=pop.n) > 0


def _ada_putus_sekolah(pop: PopulasiSintetis) -> np.ndarray:
    """Apakah ada anak usia sekolah yang tidak lagi bersekolah."""
    anak = (
        (pop.anggota_umur >= 7)
        & (pop.anggota_umur <= 18)
        & (pop.anggota_partisipasi_sekolah == 3)
    )
    return np.bincount(pop.anggota_keluarga_idx[anak], minlength=pop.n) > 0


def _tulis_kepesertaan(
    sesi: Session,
    id_keluarga: np.ndarray,
    pop: PopulasiSintetis,
    panel: PanelSintetis,
    T: int,
) -> int:
    """Ubah penanda kepesertaan per gelombang menjadi rentang waktu.

    Basis data menyimpan kepesertaan sebagai rentang - gelombang mulai dan
    gelombang selesai - bukan sebagai penanda per gelombang. Bentuk rentang
    jauh lebih ringkas dan lebih sesuai dengan cara petugas memahaminya:
    "menerima PKH sejak awal 2024 sampai sekarang", bukan enam baris terpisah.
    """
    peta_program = {
        p.kode: p.id for p in sesi.execute(select(Program)).scalars().all()
    }
    baris: list[dict[str, Any]] = []

    kode_program = list(panel.kepesertaan[0].keys())
    for kode in kode_program:
        program_id = peta_program.get(kode)
        if program_id is None:
            logger.warning("Program %s tidak ada pada katalog; kepesertaan dilewati.", kode)
            continue

        matriks = np.vstack([panel.kepesertaan[t][kode] for t in range(T)])
        for i in range(len(id_keluarga)):
            deret = matriks[:, i]
            if not deret.any():
                continue
            t = 0
            while t < T:
                if deret[t]:
                    mulai = t
                    while t < T and deret[t]:
                        t += 1
                    baris.append(
                        {
                            "keluarga_id": int(id_keluarga[i]),
                            "program_id": program_id,
                            "gelombang_mulai": mulai,
                            "gelombang_selesai": None if t >= T else t,
                            "status": (
                                StatusKepesertaan.AKTIF.value
                                if t >= T
                                else StatusKepesertaan.DIHENTIKAN.value
                            ),
                            "nilai_manfaat_bulanan": 0.0,
                            "komponen_diterima": None,
                            "sumber_penetapan": "dtsen",
                            "catatan": None,
                        }
                    )
                else:
                    t += 1

    if not baris:
        return 0
    return _tulis("kepesertaan_program", sesi.connection(), _tambah_cap_waktu(pd.DataFrame(baris)))


def kosongkan_data_sintetis(sesi: Session) -> None:
    """Hapus seluruh data sintetis, menyisakan basis pengetahuan.

    Tabel dihapus menurut urutan ketergantungan kunci asing, dari yang paling
    bergantung menuju yang paling mendasar.
    """
    urutan = [
        "hasil_intervensi",
        "intervensi",
        "verifikasi",
        "rekomendasi",
        "kasus",
        "skor_kerentanan",
        "kepesertaan_program",
        "guncangan",
        "snapshot_keluarga",
        "anggota_keluarga",
        "keluarga",
        "statistik_wilayah",
    ]
    for tabel in urutan:
        sesi.execute(text(f"DELETE FROM {tabel}"))
    sesi.commit()
    logger.info("Data sintetis dikosongkan.")


__all__ = [
    "RingkasanDataset",
    "bangkitkan_dataset",
    "kosongkan_data_sintetis",
    "muat_wilayah",
]
