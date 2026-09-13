"""Siapkan basis data NADI dari nol.

Menjalankan seluruh rangkaian penyiapan:

1. membentuk skema basis data;
2. memuat basis pengetahuan - organisasi perangkat daerah, faktor risiko,
   dan katalog program;
3. memuat struktur wilayah Kabupaten Pringsewu;
4. membangkitkan dataset keluarga sintetis beserta panel kondisinya.

Contoh pemakaian:

    python backend/scripts/siapkan_data.py
    python backend/scripts/siapkan_data.py --keluarga 5000 --gelombang 4
    python backend/scripts/siapkan_data.py --ulang        # kosongkan lebih dulu
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path

AKAR_BACKEND = Path(__file__).resolve().parents[1]
if str(AKAR_BACKEND) not in sys.path:
    sys.path.insert(0, str(AKAR_BACKEND))

from nadi.db.seed import muat_basis_pengetahuan  # noqa: E402
from nadi.db.session import buat_seluruh_tabel, sesi_transaksi  # noqa: E402
from nadi.synth.generator import (  # noqa: E402
    bangkitkan_dataset,
    kosongkan_data_sintetis,
)


def _atur_log(rinci: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if rinci else logging.INFO,
        format="%(asctime)s  %(levelname)-7s %(name)-14s %(message)s",
        datefmt="%H:%M:%S",
    )
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def main() -> int:
    p = argparse.ArgumentParser(description="Penyiapan basis data NADI")
    p.add_argument("--keluarga", type=int, default=None, help="Jumlah keluarga yang dibangkitkan")
    p.add_argument("--gelombang", type=int, default=None, help="Jumlah gelombang waktu")
    p.add_argument("--benih", type=int, default=None, help="Benih pembangkit bilangan acak")
    p.add_argument("--ulang", action="store_true", help="Kosongkan data sintetis lebih dahulu")
    p.add_argument("--tanpa-data", action="store_true", help="Hanya muat basis pengetahuan")
    p.add_argument("--rinci", action="store_true", help="Tampilkan log terperinci")
    arg = p.parse_args()

    _atur_log(arg.rinci)
    log = logging.getLogger("siapkan")
    mulai = time.perf_counter()

    log.info("Membentuk skema basis data...")
    buat_seluruh_tabel()

    with sesi_transaksi() as sesi:
        if arg.ulang:
            log.info("Mengosongkan data sintetis lama...")
            kosongkan_data_sintetis(sesi)

        log.info("Memuat basis pengetahuan...")
        hasil = muat_basis_pengetahuan(sesi)
        log.info("  %s", hasil.ringkas())
        for peringatan in hasil.peringatan:
            log.warning("  %s", peringatan)

    if arg.tanpa_data:
        log.info("Selesai dalam %.1f detik (tanpa pembangkitan data).", time.perf_counter() - mulai)
        return 0

    with sesi_transaksi() as sesi:
        log.info("Membangkitkan dataset sintetis...")
        ringkasan = bangkitkan_dataset(
            sesi,
            jumlah_keluarga=arg.keluarga,
            jumlah_gelombang=arg.gelombang,
            benih=arg.benih,
        )

    print()
    print("=" * 72)
    print("  DATASET SINTETIS NADI SIAP")
    print("=" * 72)
    print(f"  Wilayah        : {ringkasan.jumlah_wilayah:>10,}".replace(",", "."))
    print(f"  Keluarga       : {ringkasan.jumlah_keluarga:>10,}".replace(",", "."))
    print(f"  Anggota        : {ringkasan.jumlah_anggota:>10,}".replace(",", "."))
    print(f"  Kondisi        : {ringkasan.jumlah_snapshot:>10,}".replace(",", "."))
    print(f"  Guncangan      : {ringkasan.jumlah_guncangan:>10,}".replace(",", "."))
    print(f"  Kepesertaan    : {ringkasan.jumlah_kepesertaan:>10,}".replace(",", "."))
    print(f"  Gelombang      : {ringkasan.jumlah_gelombang:>10}")
    print()
    print("  Kalibrasi angka kemiskinan (cakupan desil 1-5):")
    print(f"    {'Gel':>4}  {'Sasaran':>9}  {'Tercapai':>9}  {'Median pengeluaran':>20}")
    for c in ringkasan.kalibrasi:
        median = f"{c['median_pengeluaran']:,.0f}".replace(",", ".")
        print(
            f"    {c['gelombang']:>4}  {c['sasaran_persen']:>8.2f}%  "
            f"{c['tercapai_persen']:>8.2f}%  {median:>20}"
        )
    print()
    print(f"  Selesai dalam {time.perf_counter() - mulai:.1f} detik.")
    print("=" * 72)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
