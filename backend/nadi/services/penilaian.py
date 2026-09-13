"""Layanan penilaian: menghitung dan menyimpan skor kerentanan.

Menjalankan model atas seluruh keluarga pada seluruh gelombang, lalu menuliskan
hasilnya beserta penjelasannya ke basis data.

Setiap baris skor menyimpan versi model yang menghasilkannya. Kelengkapan ini
bukan kerapian administratif melainkan syarat pertanggungjawaban: berbulan-bulan
setelah sebuah keluarga diprioritaskan, ketika model sudah dilatih ulang dua
kali dan petugas yang menanganinya sudah berpindah tugas, sistem harus tetap
sanggup menjawab mengapa keluarga itu muncul di antrean pada hari itu.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd
from sqlalchemy import delete, select, text, update
from sqlalchemy.orm import Session

from nadi.db.enums import KategoriRisiko
from nadi.db.models import SkorKerentanan, VersiModel
from nadi.db.session import mesin
from nadi.ml.dataset import muat_fitur_penilaian
from nadi.ml.penjelasan import Penjelas
from nadi.ml.pelatihan import ModelKerentanan
from nadi.security.pseudonym import sidik_jari_dataset

logger = logging.getLogger("nadi.nilai")

#: Ukuran potongan saat menghitung TreeSHAP. Menghitung seluruh dua ratus
#: empat puluh ribu baris sekaligus memakan memori besar dan tidak memberi
#: kemajuan yang terlihat; dipotong per lima ribu, kemajuannya dapat dilaporkan
#: dan pemakaian memori tetap datar.
POTONGAN_SHAP = 5_000


@dataclass
class RingkasanPenilaian:
    jumlah_skor: int = 0
    jumlah_gelombang: int = 0
    versi_model_id: int | None = None
    detik: float = 0.0
    sebaran_kategori: dict[str, int] = field(default_factory=dict)


def daftarkan_versi_model(
    sesi: Session,
    model: ModelKerentanan,
    *,
    jenis: str = "gbm",
    jadikan_aktif: bool = True,
    jalur_artefak: Path | None = None,
    catatan: str | None = None,
) -> VersiModel:
    """Catat versi model beserta metrik dan asal-usulnya ke basis data."""
    nama = "nadi-kerentanan"
    ada = sesi.scalar(
        select(VersiModel).where(VersiModel.nama == nama, VersiModel.versi == model.versi)
    )
    if ada is None:
        ada = VersiModel(nama=nama, versi=model.versi)
        sesi.add(ada)

    ada.jenis = jenis
    ada.algoritma = "LightGBM + kalibrasi isotonik"
    ada.dilatih_pada = model.dilatih_pada
    ada.gelombang_latih = model.gelombang_latih
    ada.gelombang_uji = model.gelombang_uji
    ada.jumlah_baris_latih = model.jumlah_baris_latih
    ada.jumlah_fitur = len(model.nama_fitur)
    ada.metrik = model.metrik
    ada.metrik_keadilan = model.metrik_keadilan
    ada.kepentingan_fitur = model.kepentingan_fitur
    ada.sidik_jari_dataset = sidik_jari_dataset("|".join(model.nama_fitur))
    ada.jalur_artefak = str(jalur_artefak) if jalur_artefak else None
    ada.catatan = catatan or (" ".join(model.catatan) if model.catatan else None)

    sesi.flush()

    if jadikan_aktif:
        # Hanya satu model boleh aktif pada satu waktu. Dua model aktif berarti
        # dua keluarga dapat dinilai dengan aturan berbeda pada hari yang sama.
        sesi.execute(
            update(VersiModel)
            .where(VersiModel.jenis == jenis, VersiModel.id != ada.id)
            .values(aktif=False)
        )
        ada.aktif = True
        sesi.flush()

    logger.info("Versi model tercatat: %s %s (id %s)", ada.nama, ada.versi, ada.id)
    return ada


def nilai_seluruh_keluarga(
    sesi: Session,
    model: ModelKerentanan,
    versi_model: VersiModel,
    *,
    hapus_lama: bool = True,
    gelombang_berpenjelasan: int = 2,
) -> RingkasanPenilaian:
    """Hitung skor seluruh keluarga pada seluruh gelombang dan simpan hasilnya.

    Args:
        gelombang_berpenjelasan: banyaknya gelombang TERAKHIR yang penjelasan
            rincinya ikut disimpan.

            Menghitung TreeSHAP untuk seluruh dua ratus empat puluh ribu baris
            memakan lebih dari seperempat jam pada laptop empat inti, sementara
            penjelasan gelombang lama hampir tidak pernah dibuka. Dua gelombang
            terakhir sudah cukup untuk menampilkan perbandingan sebelum dan
            sesudah pada pemantauan hasil; penjelasan gelombang yang lebih lama
            tetap dapat dihitung ulang seketika saat sebuah keluarga dibuka,
            sebab menghitung satu baris hanya memakan beberapa milidetik.
    """
    mulai = time.perf_counter()
    ringkasan = RingkasanPenilaian(versi_model_id=versi_model.id)

    X_penuh, meta = muat_fitur_penilaian(mesin)
    X = X_penuh[list(model.nama_fitur)]
    ringkasan.jumlah_gelombang = int(meta["gelombang"].nunique())
    logger.info("Menilai %d baris pada %d gelombang...", len(X), ringkasan.jumlah_gelombang)

    peluang = model.peluang(X_penuh)
    skor = np.round(peluang * 100.0, 2)

    # --- Penjelasan, hanya untuk gelombang terakhir ---
    penjelas = Penjelas()
    gelombang_semua = sorted(meta["gelombang"].unique())
    gelombang_dijelaskan = set(gelombang_semua[-max(1, gelombang_berpenjelasan) :])
    perlu = meta["gelombang"].isin(gelombang_dijelaskan).to_numpy()
    logger.info(
        "Menghitung penjelasan untuk %d baris pada gelombang %s (sisanya dihitung saat dibuka).",
        int(perlu.sum()),
        sorted(gelombang_dijelaskan),
    )

    faktor_dominan: list[list[str]] = [[] for _ in range(len(X))]
    kontribusi_ringkas: list[list[dict]] = [[] for _ in range(len(X))]
    posisi = np.flatnonzero(perlu)

    for awal in range(0, len(posisi), POTONGAN_SHAP):
        sebagian = posisi[awal : awal + POTONGAN_SHAP]
        potong = X.iloc[sebagian]
        kon = model.kontribusi(potong)
        dom = penjelas.faktor_dominan(potong, kon)
        rin = _ringkas_kontribusi(potong, kon)
        for lokal, global_ in enumerate(sebagian):
            faktor_dominan[global_] = dom[lokal]
            kontribusi_ringkas[global_] = rin[lokal]
        logger.info(
            "  penjelasan %d / %d baris",
            min(awal + POTONGAN_SHAP, len(posisi)),
            len(posisi),
        )

    # --- Peringkat dan perubahan antar-gelombang ---
    kerja = meta.copy()
    kerja["skor"] = skor
    kerja["peluang"] = peluang
    kerja["peringkat"] = (
        kerja.groupby("gelombang")["skor"].rank(ascending=False, method="first").astype(int)
    )
    kerja["persentil"] = kerja.groupby("gelombang")["skor"].rank(pct=True).round(4)
    kerja = kerja.sort_values(["keluarga_id", "gelombang"])
    kerja["selisih"] = kerja.groupby("keluarga_id")["skor"].diff()
    kerja = kerja.sort_index()

    kategori = [KategoriRisiko.dari_skor(float(s)).value for s in skor]

    if hapus_lama:
        sesi.execute(
            delete(SkorKerentanan).where(SkorKerentanan.versi_model_id == versi_model.id)
        )
        sesi.flush()

    baris = pd.DataFrame(
        {
            "keluarga_id": kerja["keluarga_id"].to_numpy(),
            "gelombang": kerja["gelombang"].to_numpy(),
            "versi_model_id": versi_model.id,
            "skor": skor,
            "probabilitas": np.round(peluang, 5),
            "kategori": kategori,
            "skor_baseline": None,
            "peringkat_kabupaten": kerja["peringkat"].to_numpy(),
            "persentil": kerja["persentil"].to_numpy(),
            "kontribusi_fitur": [_json(k) for k in kontribusi_ringkas],
            "faktor_dominan": [_json(f) for f in faktor_dominan],
            "perubahan_dari_sebelumnya": kerja["selisih"].round(2).to_numpy(),
            "penjelasan_singkat": None,
            "dihitung_pada": model.dilatih_pada,
            "dibuat_pada": model.dilatih_pada,
            "diperbarui_pada": model.dilatih_pada,
        }
    )

    # Ditulis lewat koneksi SESI, bukan lewat mesin.
    #
    # Perbedaannya sempat membuat pemuatan gagal dengan galat "database is
    # locked". Fungsi ini berjalan di dalam satu transaksi yang sudah memegang
    # kunci tulis akibat perintah penghapusan di atas; ``to_sql`` yang menerima
    # objek mesin akan mengambil koneksi BARU dari kumpulan, lalu koneksi itu
    # menunggu kunci yang tidak akan dilepas sampai transaksi luar selesai -
    # dan transaksi luar menunggu penulisan ini rampung. Keduanya saling
    # menunggu. Memakai koneksi yang sama menghapus persoalannya sekaligus
    # membuat seluruh penilaian menjadi satu transaksi yang utuh: bila gagal di
    # tengah jalan, tidak ada skor separuh jadi yang tertinggal.
    baris.to_sql(
        "skor_kerentanan",
        sesi.connection(),
        if_exists="append",
        index=False,
        chunksize=3000,
    )
    ringkasan.jumlah_skor = len(baris)
    ringkasan.sebaran_kategori = dict(pd.Series(kategori).value_counts())
    ringkasan.detik = time.perf_counter() - mulai

    logger.info(
        "Penilaian selesai: %d skor dalam %.1f detik. Sebaran: %s",
        ringkasan.jumlah_skor,
        ringkasan.detik,
        ringkasan.sebaran_kategori,
    )
    return ringkasan


def _ringkas_kontribusi(X: pd.DataFrame, kontribusi: np.ndarray, teratas: int = 8) -> list[list[dict]]:
    """Simpan hanya beberapa kontribusi terbesar per baris.

    Menyimpan seluruh empat puluh enam kontribusi untuk dua ratus empat puluh
    ribu baris akan menambah ratusan megabita pada basis data, sementara
    antarmuka tidak pernah menampilkan lebih dari delapan. Yang tidak disimpan
    tetap dapat dihitung ulang kapan saja dari model dan fiturnya.
    """
    nama = list(X.columns)
    hasil: list[list[dict]] = []
    nilai_fitur = X.to_numpy()

    for i in range(len(X)):
        k = kontribusi[i, :-1]
        urut = np.argsort(-np.abs(k))[:teratas]
        hasil.append(
            [
                {
                    "f": nama[j],
                    "n": round(float(nilai_fitur[i, j]), 3),
                    "k": round(float(k[j]), 4),
                }
                for j in urut
                if abs(k[j]) >= 0.01
            ]
        )
    return hasil


def _json(nilai) -> str:
    import json

    return json.dumps(nilai, ensure_ascii=False, separators=(",", ":"))


def hitung_statistik_wilayah(sesi: Session) -> int:
    """Bentuk ulang rekap per wilayah per gelombang.

    Dikerjakan dengan satu pernyataan SQL, bukan lewat lapisan objek. Untuk
    perhitungan gabungan atas ratusan ribu baris, basis data jauh lebih cepat
    daripada memindahkan seluruh baris ke Python untuk dijumlahkan di sana.
    """
    sesi.execute(text("DELETE FROM statistik_wilayah"))
    sesi.execute(
        text(
            """
            INSERT INTO statistik_wilayah (
                wilayah_id, gelombang, jumlah_keluarga, jumlah_individu,
                jumlah_miskin, persentase_miskin, jumlah_rentan,
                skor_rata_rata, skor_median,
                jumlah_risiko_tinggi, jumlah_risiko_sangat_tinggi,
                persen_sanitasi_layak, persen_air_minum_layak, persen_hunian_layak,
                persen_penerima_bantuan, jumlah_kasus_terbuka,
                jumlah_intervensi_berjalan, dibuat_pada, diperbarui_pada
            )
            SELECT
                k.wilayah_id,
                s.gelombang,
                COUNT(*)                                                   AS jumlah_keluarga,
                SUM(s.jumlah_anggota)                                      AS jumlah_individu,
                SUM(s.status_miskin)                                       AS jumlah_miskin,
                ROUND(AVG(s.status_miskin) * 100.0, 2)                     AS persentase_miskin,
                SUM(CASE WHEN s.status_miskin = 0
                          AND s.rasio_garis_kemiskinan < 1.5
                         THEN 1 ELSE 0 END)                                AS jumlah_rentan,
                ROUND(AVG(COALESCE(sk.skor, 0)), 2)                        AS skor_rata_rata,
                ROUND(AVG(COALESCE(sk.skor, 0)), 2)                        AS skor_median,
                SUM(CASE WHEN sk.kategori = 'tinggi' THEN 1 ELSE 0 END)    AS jumlah_risiko_tinggi,
                SUM(CASE WHEN sk.kategori = 'sangat_tinggi' THEN 1 ELSE 0 END) AS jumlah_sangat_tinggi,
                ROUND(AVG(CASE WHEN s.fasilitas_bab IN (1,2)
                                AND s.jenis_kloset = 1
                                AND s.pembuangan_akhir_tinja IN (1,2)
                               THEN 1.0 ELSE 0.0 END) * 100.0, 2)          AS persen_sanitasi,
                ROUND(AVG(CASE WHEN s.sumber_air_minum_utama IN (1,2,3,4,5,6,8)
                               THEN 1.0 ELSE 0.0 END) * 100.0, 2)          AS persen_air,
                ROUND(AVG(CASE WHEN s.jenis_lantai_terluas NOT IN (7,8,9,10)
                                AND s.jenis_dinding_terluas IN (1,2,3)
                                AND s.jenis_atap_terluas NOT IN (6,7)
                                AND (s.luas_lantai_m2 / s.jumlah_anggota) >= 7.2
                               THEN 1.0 ELSE 0.0 END) * 100.0, 2)          AS persen_hunian,
                ROUND(AVG(CASE WHEN s.jumlah_program_diterima > 0
                               THEN 1.0 ELSE 0.0 END) * 100.0, 2)          AS persen_bantuan,
                0, 0,
                :waktu, :waktu
            FROM snapshot_keluarga s
            JOIN keluarga k ON k.id = s.keluarga_id
            LEFT JOIN skor_kerentanan sk
                   ON sk.keluarga_id = s.keluarga_id
                  AND sk.gelombang = s.gelombang
            GROUP BY k.wilayah_id, s.gelombang
            """
        ),
        {"waktu": "2026-01-01 00:00:00"},
    )
    jumlah = sesi.scalar(text("SELECT COUNT(*) FROM statistik_wilayah")) or 0
    logger.info("Statistik wilayah dibentuk: %d baris.", jumlah)
    return int(jumlah)


__all__ = [
    "RingkasanPenilaian",
    "daftarkan_versi_model",
    "hitung_statistik_wilayah",
    "nilai_seluruh_keluarga",
]
