"""Bangkitkan riwayat verifikasi, intervensi, dan penilaian hasil.

Layar monitoring yang kosong tidak dapat menunjukkan apa pun, sedangkan
menunggu petugas sungguhan mengisinya membutuhkan waktu bertahun-tahun. Skrip
ini mengisi riwayat awal - tetapi dengan satu batasan yang menentukan segala
sesuatunya:

**Tidak ada satu angka hasil pun yang dikarang.**

Intervensi hanya dicatat untuk keluarga yang MEMANG mulai menerima program itu
menurut panel sintetis, pada gelombang yang memang tercatat di
``kepesertaan_program``. Penilaian hasilnya kemudian dihitung dari
``skor_kerentanan`` yang sudah ada, memakai rumus yang sama persis dengan yang
dipakai titik akhir sungguhan.

Konsekuensinya penting: skrip ini tidak memilih keluarga menurut apakah mereka
membaik. Ia memilih menurut prioritas kasus, lalu membiarkan hasilnya jatuh
apa adanya. Bila ternyata banyak yang tidak membaik, angka itulah yang akan
tampil di layar. Sebuah riwayat demo yang selalu berakhir bagus tidak akan
bertahan pada pertanyaan pertama dewan juri.

Jalankan:

    python backend/scripts/seed_intervensi.py
    python backend/scripts/seed_intervensi.py --hapus     # kosongkan lalu isi ulang
"""

from __future__ import annotations

import argparse
import sys
from datetime import date, datetime, timezone
from pathlib import Path

import numpy as np

AKAR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(AKAR / "backend"))

from sqlalchemy import text  # noqa: E402

from nadi.db.enums import HasilVerifikasi, StatusIntervensi, StatusKasus  # noqa: E402
from nadi.db.models import HasilIntervensi, Intervensi, Verifikasi  # noqa: E402
from nadi.db.session import sesi_transaksi  # noqa: E402
from nadi.security.pseudonym import kode_intervensi  # noqa: E402

BENIH = 20260826

# Sebaran hasil verifikasi lapangan. Angka-angka ini adalah asumsi tentang
# perilaku petugas, bukan tentang keluarga - dan sengaja tidak terlalu
# memihak sistem: lebih dari seperlima penandaan ternyata keliru ketika
# diperiksa langsung. Sistem yang mengaku selalu benar tidak dipercaya siapa
# pun yang pernah bekerja di lapangan.
SEBARAN_HASIL = (
    (HasilVerifikasi.SESUAI, 0.61),
    (HasilVerifikasi.TIDAK_SESUAI, 0.22),
    (HasilVerifikasi.PERLU_DATA_TAMBAHAN, 0.11),
    (HasilVerifikasi.TIDAK_DITEMUKAN, 0.06),
)

PETA_STATUS = {
    HasilVerifikasi.SESUAI: StatusKasus.TERVERIFIKASI_SESUAI,
    HasilVerifikasi.TIDAK_SESUAI: StatusKasus.TERVERIFIKASI_TIDAK_SESUAI,
    HasilVerifikasi.PERLU_DATA_TAMBAHAN: StatusKasus.PERLU_DATA_TAMBAHAN,
    HasilVerifikasi.TIDAK_DITEMUKAN: StatusKasus.PERLU_DATA_TAMBAHAN,
}

METODE = ("kunjungan_lapangan", "kunjungan_lapangan", "kunjungan_lapangan", "wawancara_telepon")

# Sekitar seperempat kasus terbuka pada tiga gelombang pertama. Untuk
# kabupaten sebesar Pringsewu selama tiga tahun, itu berarti kira-kira
# delapan ratus kunjungan per tahun - beban yang masuk akal bagi satu tim
# verifikator, dan cukup untuk mengisi setiap sel rekap di atas ambang
# penyembunyian sel kecil.
JUMLAH_KASUS_DIVERIFIKASI = 2600
AMBANG_PERUBAHAN_BERMAKNA = 5.0


def _penilaian(selisih: float) -> str:
    if selisih <= -AMBANG_PERUBAHAN_BERMAKNA:
        return "membaik"
    if selisih >= AMBANG_PERUBAHAN_BERMAKNA:
        return "memburuk"
    return "tetap"


def kosongkan(sesi) -> None:
    for tabel in ("hasil_intervensi", "intervensi", "verifikasi"):
        n = sesi.execute(text(f"DELETE FROM {tabel}")).rowcount
        print(f"  {tabel:<20} {n or 0} baris dihapus")
    sesi.execute(
        text(
            "UPDATE kasus SET status = 'baru', ditutup_pada = NULL "
            "WHERE status NOT IN ('baru', 'ditugaskan')"
        )
    )
    sesi.commit()


def jalankan(sesi, *, jumlah: int = JUMLAH_KASUS_DIVERIFIKASI, verbose: bool = True) -> dict:
    rng = np.random.default_rng(BENIH)

    tanggal = {
        int(r.gelombang): r.tanggal
        for r in sesi.execute(
            text("SELECT gelombang, MIN(tanggal_kondisi) AS tanggal FROM snapshot_keluarga GROUP BY gelombang")
        ).all()
    }
    gelombang_akhir = max(tanggal)

    # Petugas hanya dapat memverifikasi kasus yang sudah ada potret sesudahnya,
    # sehingga gelombang terakhir dikecualikan - hasilnya belum dapat dinilai.
    kasus = sesi.execute(
        text(
            """
            SELECT k.id, k.kode_semu, k.keluarga_id, k.gelombang, k.jenis,
                   k.skor_prioritas, k.opd_ditugaskan_id
            FROM kasus k
            WHERE k.gelombang < :akhir
            ORDER BY k.skor_prioritas DESC, k.id
            LIMIT :n
            """
        ),
        {"akhir": gelombang_akhir, "n": jumlah},
    ).all()

    if not kasus:
        raise SystemExit("Tidak ada kasus pada gelombang selain yang terakhir.")

    pengguna = {
        r.peran: int(r.id)
        for r in sesi.execute(text("SELECT id, peran FROM pengguna WHERE aktif = 1")).all()
    }
    id_verifikator = pengguna.get("verifikator") or pengguna.get("dinas_sosial") or 1
    id_dinsos = pengguna.get("dinas_sosial") or id_verifikator

    jenis_hasil = [h for h, _ in SEBARAN_HASIL]
    bobot = np.array([b for _, b in SEBARAN_HASIL], dtype=float)
    bobot /= bobot.sum()

    n_verifikasi = n_intervensi = n_hasil = 0
    sebaran_penilaian: dict[str, int] = {}

    for k in kasus:
        hasil = jenis_hasil[int(rng.choice(len(jenis_hasil), p=bobot))]

        sesi.add(
            Verifikasi(
                kasus_id=int(k.id),
                pengguna_id=id_verifikator,
                hasil=hasil,
                metode=str(rng.choice(METODE)),
                setuju_dengan_sistem=hasil == HasilVerifikasi.SESUAI,
                durasi_menit=int(rng.integers(20, 75)),
                catatan=None,
            )
        )
        n_verifikasi += 1

        status = PETA_STATUS[hasil]
        sesi.execute(
            text("UPDATE kasus SET status = :s WHERE id = :i"),
            {"s": status.value, "i": int(k.id)},
        )
        if not status.terbuka:
            sesi.execute(
                text("UPDATE kasus SET ditutup_pada = :t WHERE id = :i"),
                {"t": datetime.now(timezone.utc), "i": int(k.id)},
            )

        # Hanya kasus yang terbukti benar yang berbuah penyaluran. Kasus yang
        # datanya ternyata keliru justru berakhir sebagai koreksi data, bukan
        # bantuan - dan itu memang salah satu keluaran sah dari sistem ini.
        if hasil != HasilVerifikasi.SESUAI:
            continue

        # Cari program yang MEMANG mulai diterima keluarga ini pada atau
        # sesudah gelombang kasus. Bila tidak ada, tidak ada intervensi yang
        # dicatat - keluarga itu memang tidak menerima apa pun, dan angka
        # cakupan tidak boleh menutupi kenyataan tersebut.
        mulai = sesi.execute(
            text(
                """
                SELECT kp.program_id, kp.gelombang_mulai, kp.nilai_manfaat_bulanan,
                       p.singkatan, p.biaya_satuan_tahunan
                FROM kepesertaan_program kp
                JOIN program p ON p.id = kp.program_id
                WHERE kp.keluarga_id = :kid AND kp.gelombang_mulai >= :g
                  AND kp.gelombang_mulai < :akhir
                ORDER BY kp.gelombang_mulai
                LIMIT 1
                """
            ),
            {"kid": int(k.keluarga_id), "g": int(k.gelombang), "akhir": gelombang_akhir},
        ).first()
        if mulai is None:
            continue

        g_mulai = int(mulai.gelombang_mulai)
        opd = sesi.execute(
            text("SELECT opd_id FROM program_opd WHERE program_id = :p LIMIT 1"),
            {"p": int(mulai.program_id)},
        ).scalar()

        nilai = float(mulai.nilai_manfaat_bulanan or 0.0)
        if nilai <= 0 and mulai.biaya_satuan_tahunan:
            nilai = round(float(mulai.biaya_satuan_tahunan) / 12.0, 0)

        itv = Intervensi(
            kode_semu="",
            keluarga_id=int(k.keluarga_id),
            program_id=int(mulai.program_id),
            opd_id=int(opd) if opd else k.opd_ditugaskan_id,
            kasus_id=int(k.id),
            gelombang_mulai=g_mulai,
            tanggal_mulai=date.fromisoformat(str(tanggal[g_mulai])[:10]),
            status=StatusIntervensi.SELESAI,
            nilai_manfaat_bulanan=nilai or None,
            ditetapkan_oleh_id=id_dinsos,
            catatan=None,
        )
        sesi.add(itv)
        sesi.flush()
        itv.kode_semu = kode_intervensi(itv.id)
        itv.tanggal_selesai = date.fromisoformat(str(tanggal[gelombang_akhir])[:10])
        n_intervensi += 1

        sesi.execute(
            text("UPDATE kasus SET status = :s, ditutup_pada = :t WHERE id = :i"),
            {"s": StatusKasus.SELESAI.value, "t": datetime.now(timezone.utc), "i": int(k.id)},
        )

        # --- Penilaian hasil, dihitung dari data yang sudah ada -------------
        potret = {
            int(r.gelombang): r
            for r in sesi.execute(
                text(
                    """
                    SELECT sk.gelombang, sk.skor, s.status_miskin, s.pengeluaran_per_kapita,
                           s.jumlah_program_diterima, s.desil_kesejahteraan
                    FROM skor_kerentanan sk
                    JOIN snapshot_keluarga s
                      ON s.keluarga_id = sk.keluarga_id AND s.gelombang = sk.gelombang
                    WHERE sk.keluarga_id = :kid AND sk.gelombang IN (:a, :b)
                    """
                ),
                {"kid": int(k.keluarga_id), "a": g_mulai, "b": gelombang_akhir},
            ).all()
        }
        if g_mulai not in potret or gelombang_akhir not in potret:
            continue

        a, b = potret[g_mulai], potret[gelombang_akhir]
        selisih = round(float(b.skor) - float(a.skor), 2)
        penilaian = _penilaian(selisih)
        sebaran_penilaian[penilaian] = sebaran_penilaian.get(penilaian, 0) + 1

        sesi.add(
            HasilIntervensi(
                intervensi_id=itv.id,
                keluarga_id=int(k.keluarga_id),
                gelombang_sebelum=g_mulai,
                gelombang_sesudah=gelombang_akhir,
                skor_sebelum=round(float(a.skor), 2),
                skor_sesudah=round(float(b.skor), 2),
                selisih_skor=selisih,
                miskin_sebelum=bool(a.status_miskin),
                miskin_sesudah=bool(b.status_miskin),
                pengeluaran_sebelum=float(a.pengeluaran_per_kapita),
                pengeluaran_sesudah=float(b.pengeluaran_per_kapita),
                indikator_berubah={
                    "desil_kesejahteraan": [int(a.desil_kesejahteraan), int(b.desil_kesejahteraan)],
                    "jumlah_program_diterima": [
                        int(a.jumlah_program_diterima),
                        int(b.jumlah_program_diterima),
                    ],
                },
                penilaian=penilaian,
                dinilai_pada=datetime.now(timezone.utc),
            )
        )
        n_hasil += 1

    sesi.commit()

    ringkas = {
        "verifikasi": n_verifikasi,
        "intervensi": n_intervensi,
        "hasil_dinilai": n_hasil,
        "penilaian": sebaran_penilaian,
    }
    if verbose:
        print()
        print(f"  Verifikasi dicatat   : {n_verifikasi}")
        print(f"  Intervensi dicatat   : {n_intervensi}")
        print(f"  Hasil dinilai        : {n_hasil}")
        print()
        for nama in ("membaik", "tetap", "memburuk"):
            n = sebaran_penilaian.get(nama, 0)
            persen = n / n_hasil * 100 if n_hasil else 0
            print(f"    {nama:<10} {n:>4}  ({persen:4.1f}%)")
    return ringkas


def main() -> int:
    p = argparse.ArgumentParser(description="Isi riwayat verifikasi, intervensi, dan hasilnya.")
    p.add_argument("--hapus", action="store_true", help="Kosongkan riwayat lama lebih dahulu.")
    p.add_argument("--jumlah", type=int, default=JUMLAH_KASUS_DIVERIFIKASI,
                   help="Berapa kasus yang diverifikasi.")
    args = p.parse_args()

    with sesi_transaksi() as sesi:
        if args.hapus:
            print("Mengosongkan riwayat lama...")
            kosongkan(sesi)
        ada = sesi.execute(text("SELECT COUNT(*) FROM intervensi")).scalar() or 0
        if ada:
            print(f"Sudah ada {ada} intervensi. Jalankan dengan --hapus untuk mengisi ulang.")
            return 0
        jalankan(sesi, jumlah=args.jumlah)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
