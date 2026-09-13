"""Jalankan deteksi ketidaksesuaian dan bentuk antrean kasus.

Menjalankan tujuh detektor pada satu gelombang, lalu menuliskan hasilnya
sebagai kasus untuk diperiksa petugas. Sekaligus menyemai akun demonstrasi
bila belum ada.

Contoh pemakaian:

    python backend/scripts/deteksi_kasus.py
    python backend/scripts/deteksi_kasus.py --gelombang 4 --batas 3000
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

AKAR_BACKEND = Path(__file__).resolve().parents[1]
if str(AKAR_BACKEND) not in sys.path:
    sys.path.insert(0, str(AKAR_BACKEND))

import pandas as pd  # noqa: E402
from sqlalchemy import select, text  # noqa: E402

from nadi.db.enums import JenisAnomali, StatusKasus  # noqa: E402
from nadi.db.models import OPD  # noqa: E402
from nadi.db.session import mesin, sesi_transaksi  # noqa: E402
from nadi.security.pseudonym import kode_kasus  # noqa: E402
from nadi.services.anomali import jalankan_deteksi  # noqa: E402
from nadi.services.pengguna import semai_pengguna  # noqa: E402


def _atur_log(rinci: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if rinci else logging.INFO,
        format="%(asctime)s  %(levelname)-7s %(name)-16s %(message)s",
        datefmt="%H:%M:%S",
    )
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def main() -> int:
    p = argparse.ArgumentParser(description="Deteksi ketidaksesuaian sasaran")
    p.add_argument("--gelombang", type=int, default=None, help="Gelombang yang diperiksa")
    p.add_argument("--batas", type=int, default=4000,
                   help="Banyaknya kasus berprioritas tertinggi yang disimpan")
    p.add_argument("--hari-tenggat", type=int, default=30)
    p.add_argument("--rinci", action="store_true")
    arg = p.parse_args()

    _atur_log(arg.rinci)
    log = logging.getLogger("deteksi")
    mulai = time.perf_counter()

    with sesi_transaksi() as sesi:
        log.info("Menyemai akun demonstrasi...")
        hasil_akun = semai_pengguna(sesi)
        log.info("  %s", hasil_akun)

        g = arg.gelombang
        if g is None:
            g = int(sesi.execute(text("SELECT MAX(gelombang) FROM snapshot_keluarga")).scalar() or 0)
        log.info("Menjalankan deteksi pada gelombang %d...", g)

        temuan = jalankan_deteksi(mesin, g)
        if not temuan:
            log.warning("Tidak ada kasus terdeteksi.")
            return 0

        log.info("Total kasus terdeteksi: %d", len(temuan))
        # Hanya kasus berprioritas tertinggi yang disimpan. Antrean yang memuat
        # puluhan ribu kasus sama tidak bergunanya dengan antrean kosong -
        # keduanya tidak memberi tahu petugas harus mulai dari mana.
        terpilih = temuan[: arg.batas]
        if len(temuan) > arg.batas:
            log.info(
                "Disimpan %d kasus berprioritas tertinggi; %d sisanya tidak "
                "dimasukkan ke antrean agar tetap dapat dikerjakan.",
                len(terpilih),
                len(temuan) - len(terpilih),
            )

        sesi.execute(text("DELETE FROM kasus WHERE gelombang = :g"), {"g": g})
        sesi.flush()

        peta_opd = {o.kode: o.id for o in sesi.execute(select(OPD)).scalars().all()}
        tenggat = date.today() + timedelta(days=arg.hari_tenggat)

        baris = []
        for i, t in enumerate(terpilih, 1):
            baris.append(
                {
                    "kode_semu": kode_kasus(f"{g}-{t.keluarga_id}-{t.jenis.value}-{i}"),
                    "keluarga_id": t.keluarga_id,
                    "gelombang": t.gelombang,
                    "jenis": t.jenis.value,
                    "skor_prioritas": t.skor_prioritas,
                    "tingkat_prioritas": t.tingkat_prioritas,
                    "alasan": json.dumps(t.alasan, ensure_ascii=False),
                    "sumber_deteksi": t.sumber_deteksi,
                    "ringkasan": t.ringkasan,
                    "status": StatusKasus.BARU.value,
                    "opd_ditugaskan_id": peta_opd.get(t.opd_disarankan or ""),
                    "pengguna_ditugaskan_id": None,
                    "tenggat": tenggat if t.tingkat_prioritas <= 2 else None,
                    "ditutup_pada": None,
                    "dibuat_pada": "2026-01-01 00:00:00",
                    "diperbarui_pada": "2026-01-01 00:00:00",
                }
            )

        pd.DataFrame(baris).to_sql(
            "kasus", sesi.connection(), if_exists="append", index=False, chunksize=2000
        )

    # -----------------------------------------------------------------
    hitung = Counter(t.jenis.value for t in terpilih)
    prioritas = Counter(t.tingkat_prioritas for t in terpilih)

    print()
    print("=" * 76)
    print("  ANTREAN KASUS TERBENTUK")
    print("=" * 76)
    print(f"  Gelombang        : {g}")
    print(f"  Kasus terdeteksi : {len(temuan):,}".replace(",", "."))
    print(f"  Kasus disimpan   : {len(terpilih):,}".replace(",", "."))
    print()
    print("  Menurut jenis:")
    for jenis, n in hitung.most_common():
        label = JenisAnomali(jenis).label
        print(f"    {n:>6,}  {label}".replace(",", "."))
    print()
    print("  Menurut tingkat prioritas (1 paling mendesak):")
    for tingkat in sorted(prioritas):
        print(f"    Tingkat {tingkat}: {prioritas[tingkat]:>6,}".replace(",", "."))
    print()
    print(f"  Selesai dalam {time.perf_counter() - mulai:.1f} detik.")
    print("=" * 76)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
