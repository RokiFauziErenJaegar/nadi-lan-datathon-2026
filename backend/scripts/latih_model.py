"""Latih model kerentanan, nilai seluruh keluarga, dan simpan hasilnya.

Menjalankan seluruh rangkaian analitik:

1. memuat dataset dari basis data;
2. melatih indeks dasar yang dapat ditafsirkan sebagai pembanding;
3. melatih model gradient boosting pada tiga lapis ketersediaan data;
4. mencatat versi model beserta metriknya;
5. menilai seluruh keluarga pada seluruh gelombang dan menyimpan skornya;
6. membentuk rekap wilayah.

Contoh pemakaian:

    python backend/scripts/latih_model.py
    python backend/scripts/latih_model.py --tanpa-perbandingan   # lebih cepat
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path

AKAR_BACKEND = Path(__file__).resolve().parents[1]
if str(AKAR_BACKEND) not in sys.path:
    sys.path.insert(0, str(AKAR_BACKEND))

import numpy as np  # noqa: E402

from nadi.db.session import mesin, sesi_transaksi  # noqa: E402
from nadi.ml.baseline import IndeksDasar  # noqa: E402
from nadi.ml.dataset import muat_dataset  # noqa: E402
from nadi.ml.evaluasi import evaluasi_lengkap  # noqa: E402
from nadi.ml.fitur import (  # noqa: E402
    NAMA_FITUR_DTSEN,
    NAMA_FITUR_LENGKAP,
    NAMA_FITUR_OPERASIONAL,
    PETA_FITUR,
)
from nadi.ml.pelatihan import latih_model, uji_keluarga_terpisah  # noqa: E402
from nadi.services.penilaian import (  # noqa: E402
    daftarkan_versi_model,
    hitung_statistik_wilayah,
    nilai_seluruh_keluarga,
)


def _atur_log(rinci: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if rinci else logging.INFO,
        format="%(asctime)s  %(levelname)-7s %(name)-16s %(message)s",
        datefmt="%H:%M:%S",
    )
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def _garis(judul: str = "") -> None:
    print("=" * 78)
    if judul:
        print(f"  {judul}")
        print("=" * 78)


def main() -> int:
    p = argparse.ArgumentParser(description="Pelatihan dan penilaian model NADI")
    p.add_argument("--versi", default="v1.0.0")
    p.add_argument("--tanpa-perbandingan", action="store_true",
                   help="Lewati pelatihan lapis pembanding agar lebih cepat")
    p.add_argument("--tanpa-penilaian", action="store_true",
                   help="Hanya latih, jangan nilai seluruh keluarga")
    p.add_argument("--rinci", action="store_true")
    arg = p.parse_args()

    _atur_log(arg.rinci)
    log = logging.getLogger("latih")
    mulai = time.perf_counter()

    log.info("Memuat dataset...")
    data = muat_dataset(mesin)

    # -----------------------------------------------------------------
    # Model utama
    # -----------------------------------------------------------------
    log.info("Melatih model utama (DTSEN + sinyal lintas OPD)...")
    model, bagi, hasil = latih_model(
        data, fitur_dipakai=NAMA_FITUR_OPERASIONAL, versi=arg.versi
    )
    jalur = model.simpan()

    # -----------------------------------------------------------------
    # Pembanding
    # -----------------------------------------------------------------
    perbandingan: list[dict] = []

    dasar = IndeksDasar.dari_berkas()
    kalibrasi = data.saring_gelombang(bagi.gelombang_kalibrasi)
    dasar.kalibrasi(kalibrasi.X, kalibrasi.y)
    h_dasar = evaluasi_lengkap(bagi.uji.y, dasar.peluang(bagi.uji.X), bagi.uji.meta)
    perbandingan.append(
        {
            "model": "Indeks dasar (aturan)",
            "fitur": len(dasar.faktor),
            "auc": h_dasar.peringkat.auc,
            "brier": h_dasar.kalibrasi.brier,
            "presisi_300": h_dasar.peringkat.pada_anggaran[300]["presisi"],
            "pengganda_300": h_dasar.peringkat.pada_anggaran[300]["pengganda"],
        }
    )

    if not arg.tanpa_perbandingan:
        for nama, fset in (
            ("DTSEN saja", NAMA_FITUR_DTSEN),
            ("+ survei konsumsi (batas atas)", NAMA_FITUR_LENGKAP),
        ):
            log.info("Melatih pembanding: %s", nama)
            m2, _, h2 = latih_model(data, fitur_dipakai=fset, versi=arg.versi)
            perbandingan.append(
                {
                    "model": nama,
                    "fitur": len(fset),
                    "auc": h2.peringkat.auc,
                    "brier": h2.kalibrasi.brier,
                    "presisi_300": h2.peringkat.pada_anggaran[300]["presisi"],
                    "pengganda_300": h2.peringkat.pada_anggaran[300]["pengganda"],
                }
            )

    perbandingan.insert(
        1,
        {
            "model": "NADI (DTSEN + lintas OPD)  <-- dijalankan",
            "fitur": len(model.nama_fitur),
            "auc": hasil.peringkat.auc,
            "brier": hasil.kalibrasi.brier,
            "presisi_300": hasil.peringkat.pada_anggaran[300]["presisi"],
            "pengganda_300": hasil.peringkat.pada_anggaran[300]["pengganda"],
        },
    )

    # -----------------------------------------------------------------
    # Ketahanan
    # -----------------------------------------------------------------
    log.info("Menguji ketahanan pada keluarga yang belum pernah dilihat...")
    ketahanan = uji_keluarga_terpisah(data, model)

    # -----------------------------------------------------------------
    # Simpan dan nilai
    # -----------------------------------------------------------------
    catatan_ketahanan = (
        f"Uji keluarga terpisah: AUC {ketahanan['auc']:.3f}, "
        f"presisi@500 {ketahanan['presisi_500'] * 100:.1f}%."
    )
    with sesi_transaksi() as sesi:
        versi = daftarkan_versi_model(
            sesi,
            model,
            jalur_artefak=jalur,
            catatan=" ".join(model.catatan + [catatan_ketahanan]),
        )
        versi_id = versi.id

        if not arg.tanpa_penilaian:
            log.info("Menilai seluruh keluarga...")
            ringkasan = nilai_seluruh_keluarga(sesi, model, versi)
            log.info("Membentuk rekap wilayah...")
            hitung_statistik_wilayah(sesi)
        else:
            ringkasan = None

    # -----------------------------------------------------------------
    # Laporan
    # -----------------------------------------------------------------
    p_uji = hasil.peringkat
    print()
    _garis("HASIL PELATIHAN MODEL NADI")
    print(f"  Versi model      : {arg.versi} (id basis data {versi_id})")
    print(f"  Berkas           : {jalur.name}")
    print(f"  Dilatih pada     : gelombang {bagi.gelombang_latih}, {model.jumlah_baris_latih:,} baris".replace(",", "."))
    print(f"  Dikalibrasi pada : gelombang {bagi.gelombang_kalibrasi}")
    print(f"  Diuji pada       : gelombang {bagi.gelombang_uji}, prevalensi {p_uji.prevalensi * 100:.2f}%")
    print(f"  Fitur dipakai    : {len(model.nama_fitur)} dari {len(NAMA_FITUR_LENGKAP)}")
    print()

    _garis("PERBANDINGAN MODEL")
    print(f"  {'Model':38s}{'Fitur':>7s}{'AUC':>8s}{'Brier':>9s}{'Pres@300':>10s}{'Pengganda':>11s}")
    for b in perbandingan:
        print(
            f"  {b['model']:38s}{b['fitur']:>7d}{b['auc']:>8.3f}{b['brier']:>9.4f}"
            f"{b['presisi_300'] * 100:>9.1f}%{b['pengganda_300']:>10.2f}x"
        )
    print()

    _garis("KINERJA PADA ANGGARAN VERIFIKASI")
    print(f"  {'k':>8s}{'presisi':>10s}{'pengganda':>11s}{'recall':>9s}{'batas maks':>12s}{'efisiensi':>11s}")
    for k, v in p_uji.pada_anggaran.items():
        print(
            f"  {k:>8d}{v['presisi'] * 100:>9.1f}%{v['pengganda']:>10.2f}x"
            f"{v['recall'] * 100:>8.1f}%{v['recall_maksimum'] * 100:>11.1f}%"
            f"{v['efisiensi_anggaran'] * 100:>10.1f}%"
        )
    print()

    _garis("KALIBRASI DAN KEADILAN")
    print(f"  Brier {hasil.kalibrasi.brier:.4f} | galat kalibrasi {hasil.kalibrasi.ece:.4f}")
    kec = hasil.keadilan.get("kecamatan", [])
    if kec:
        auc_kec = [b["auc"] for b in kec]
        print(f"  AUC per kecamatan: {min(auc_kec):.3f} sampai {max(auc_kec):.3f} "
              f"(selisih {max(auc_kec) - min(auc_kec):.3f})")
        terburuk = min(kec, key=lambda b: b["auc"])
        print(f"  Kecamatan terlemah: {terburuk['nilai']} (AUC {terburuk['auc']:.3f})")
    for nama in ("kepala_keluarga_perempuan", "wilayah_perdesaan"):
        baris = hasil.keadilan.get(nama, [])
        if len(baris) >= 2:
            r = [b["recall_pada_k"] for b in baris]
            print(f"  Selisih recall menurut {nama}: {(max(r) - min(r)) * 100:.1f} poin persen")
    print(f"  Ketahanan pada keluarga baru: AUC {ketahanan['auc']:.3f}, "
          f"presisi@500 {ketahanan['presisi_500'] * 100:.1f}%")
    print()

    if hasil.catatan:
        _garis("PERINGATAN")
        for c in hasil.catatan:
            print(f"  ! {c}")
        print()

    _garis("SEPULUH FITUR PALING BERPENGARUH")
    for i, (n, v) in enumerate(list(model.kepentingan_fitur.items())[:10], 1):
        f = PETA_FITUR.get(n)
        label = f.label if f else n
        sumber = f.sumber if f else "?"
        print(f"  {i:2d}. {label[:48]:48s} {v:5.2f}%  [{sumber}]")
    print()

    if ringkasan:
        _garis("PENILAIAN SELURUH KELUARGA")
        print(f"  Skor tersimpan : {ringkasan.jumlah_skor:,}".replace(",", "."))
        print(f"  Gelombang      : {ringkasan.jumlah_gelombang}")
        print(f"  Waktu          : {ringkasan.detik:.1f} detik")
        print("  Sebaran kategori risiko:")
        for k, v in sorted(ringkasan.sebaran_kategori.items(), key=lambda x: -x[1]):
            print(f"    {k:16s} {v:>8,}".replace(",", "."))
        print()

    print(f"  Total waktu: {time.perf_counter() - mulai:.1f} detik.")
    _garis()

    laporan = {
        "versi": arg.versi,
        "perbandingan": perbandingan,
        "anggaran": p_uji.pada_anggaran,
        "kalibrasi": hasil.ke_dict()["kalibrasi"],
        "keadilan": hasil.keadilan,
        "ketahanan": ketahanan,
        "catatan": hasil.catatan,
    }
    berkas = AKAR_BACKEND.parent / "models" / "artifacts" / f"laporan_model_{arg.versi}.json"
    berkas.write_text(json.dumps(laporan, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
    print(f"  Laporan lengkap: {berkas.relative_to(AKAR_BACKEND.parent)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
