"""Uji penerimaan NADI: memeriksa seluruh janji sistem lewat HTTP sungguhan.

Berbeda dari uji otomatis di ``backend/tests``, skrip ini tidak menguji satu
fungsi melainkan menguji **janji**: bahwa pimpinan daerah benar-benar tidak
dapat membuka satu keluarga pun, bahwa OPD pelaksana benar-benar tidak dapat
menilai pekerjaannya sendiri, bahwa NIK benar-benar tertahan sebelum keluar
jaringan.

Semua diperiksa lewat permintaan HTTP kepada peladen yang sedang berjalan -
bukan dengan memanggil fungsi Python secara langsung. Itu disengaja: yang
menghadapi pemakai adalah lapisan HTTP, dan hanya di situlah janji tersebut
benar-benar berlaku. Sebuah pemeriksaan yang memanggil fungsi internal dapat
lulus meski rutenya lupa dipasangi penjaga.

Setiap pemeriksaan mencetak nilai yang benar-benar diterima, bukan sekadar
"lulus". Angka yang terlihat memungkinkan pembaca menilai sendiri, dan itulah
yang membedakan laporan pengujian dari pernyataan bahwa pengujian telah
dilakukan.

    python backend/scripts/uji_penerimaan.py
    python backend/scripts/uji_penerimaan.py --bagian B     # hanya bagian tertentu
    python backend/scripts/uji_penerimaan.py --bersihkan    # hapus data uji lalu keluar
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
import time
from pathlib import Path

import httpx

AKAR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(AKAR / "backend"))

ASAL = "http://127.0.0.1:8000"
BASIS_DATA = AKAR / "data" / "nadi.db"
PENANDA_UJI = "[uji-penerimaan]"

AKUN = {
    "admin": "NadiAdmin#2026",
    "bupati": "NadiPimpinan#2026",
    "bappeda": "NadiPerencana#2026",
    "dinsos": "NadiDinsos#2026",
    "pupr": "NadiPupr#2026",
    "verifikator": "NadiVerif#2026",
}

# Konsol Windows berjalan pada cp1252, yang tidak mengenal aksara penggaris
# maupun tanda kutip lengkung. Tanpa penyetelan ini seluruh laporan gagal
# tercetak dengan galat pengodean - bukan karena pengujiannya gagal.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, OSError):  # pragma: no cover
    pass

HIJAU, MERAH, KUNING, ABU, PADAM = "\033[92m", "\033[91m", "\033[93m", "\033[90m", "\033[0m"


class Hasil:
    """Kumpulan hasil pemeriksaan."""

    def __init__(self) -> None:
        self.butir: list[tuple[str, str, bool, str]] = []
        self.bagian_kini = ""

    def bagian(self, kode: str, judul: str) -> None:
        self.bagian_kini = kode
        print(f"\n  {ABU}{'─' * 74}{PADAM}")
        print(f"  {kode}. {judul}")
        print(f"  {ABU}{'─' * 74}{PADAM}")

    def periksa(self, kode: str, keterangan: str, lulus: bool, teramati: str = "") -> bool:
        self.butir.append((kode, keterangan, lulus, teramati))
        tanda = f"{HIJAU}LULUS{PADAM}" if lulus else f"{MERAH}GAGAL{PADAM}"
        print(f"  {tanda}  {kode:<5} {keterangan}")
        if teramati:
            print(f"         {ABU}{teramati}{PADAM}")
        return lulus

    def ringkas(self) -> int:
        gagal = [b for b in self.butir if not b[2]]
        print(f"\n  {ABU}{'═' * 74}{PADAM}")
        print(f"  {len(self.butir) - len(gagal)} dari {len(self.butir)} pemeriksaan lulus.")
        if gagal:
            print(f"\n  {MERAH}Yang gagal:{PADAM}")
            for kode, ket, _, teramati in gagal:
                print(f"    {kode:<5} {ket}")
                if teramati:
                    print(f"          {ABU}{teramati}{PADAM}")
        print()
        return 1 if gagal else 0


def masuk(k: httpx.Client, nama: str) -> dict[str, str] | None:
    r = k.post("/api/masuk", json={"nama_pengguna": nama, "sandi": AKUN[nama]})
    if r.status_code != 200:
        return None
    return {"Authorization": "Bearer " + r.json()["token"]}


# ===========================================================================
# A. Kesehatan sistem
# ===========================================================================
def bagian_a(k: httpx.Client, h: Hasil, sesi: dict) -> None:
    h.bagian("A", "Kesehatan sistem")

    r = k.get("/api/kesehatan")
    h.periksa("A1", "Peladen menjawab", r.status_code == 200, f"HTTP {r.status_code}")

    if not BASIS_DATA.exists():
        h.periksa("A2", "Basis data ada", False, "berkas data/nadi.db tidak ditemukan")
        return
    c = sqlite3.connect(str(BASIS_DATA))
    tabel = [x[0] for x in c.execute("SELECT name FROM sqlite_master WHERE type='table'")]
    n_keluarga = c.execute("SELECT COUNT(*) FROM keluarga").fetchone()[0]
    n_skor = c.execute("SELECT COUNT(*) FROM skor_kerentanan").fetchone()[0]
    ukuran = BASIS_DATA.stat().st_size / 1024**2
    h.periksa("A2", "Basis data terbaca dan berisi", len(tabel) >= 20 and n_keluarga > 0,
              f"{len(tabel)} tabel, {n_keluarga:,} keluarga, {n_skor:,} skor, {ukuran:.1f} MB".replace(",", "."))

    n_model = c.execute("SELECT COUNT(*) FROM versi_model WHERE aktif = 1").fetchone()[0]
    h.periksa("A3", "Ada satu model aktif", n_model == 1, f"{n_model} model aktif")
    c.close()

    r = k.get("/")
    tampil = r.status_code == 200 and "html" in r.headers.get("content-type", "")
    h.periksa("A4", "Antarmuka tersaji peladen", tampil,
              f"HTTP {r.status_code}, {r.headers.get('content-type', '?')}")

    r = k.get("/openapi.json")
    n_jalur = len(r.json().get("paths", {})) if r.status_code == 200 else 0
    n_operasi = sum(
        len([m for m in v if m in ("get", "post", "put", "patch", "delete")])
        for v in r.json().get("paths", {}).values()
    ) if r.status_code == 200 else 0
    h.periksa("A5", "Dokumentasi API terbentuk sendiri", n_jalur > 30,
              f"{n_operasi} operasi pada {n_jalur} jalur")

    for nama in AKUN:
        sesi[nama] = masuk(k, nama)
    hilang = [n for n, v in sesi.items() if v is None]
    h.periksa("A6", "Keenam akun demo dapat masuk", not hilang,
              "gagal: " + ", ".join(hilang) if hilang else "admin, bupati, bappeda, dinsos, pupr, verifikator")


# ===========================================================================
# B. Kewenangan
# ===========================================================================
def bagian_b(k: httpx.Client, h: Hasil, sesi: dict) -> None:
    h.bagian("B", "Kewenangan: siapa boleh melakukan apa")

    r = k.get("/api/ringkasan")
    h.periksa("B1", "Tanpa token, permintaan ditolak", r.status_code in (401, 403),
              f"HTTP {r.status_code}")

    r = k.get("/api/ringkasan", headers=sesi["bupati"])
    h.periksa("B2", "Pimpinan daerah dapat membaca agregat", r.status_code == 200,
              f"HTTP {r.status_code}")

    r = k.get("/api/keluarga/cari?batas=1", headers=sesi["bupati"])
    h.periksa("B3", "Pimpinan daerah TIDAK dapat membuka daftar keluarga",
              r.status_code == 403, f"HTTP {r.status_code} (harus 403)")

    r = k.get("/api/keluarga/cari?batas=1", headers=sesi["bappeda"])
    h.periksa("B4", "Perencana TIDAK dapat membuka daftar keluarga",
              r.status_code == 403, f"HTTP {r.status_code} (harus 403)")

    r = k.get("/api/intervensi/rekap/monitoring", headers=sesi["verifikator"])
    h.periksa("B5", "Verifikator TIDAK dapat membaca monitoring hasil",
              r.status_code == 403, f"HTTP {r.status_code} (harus 403)")

    r = k.post("/api/intervensi", headers=sesi["dinsos"],
               json={"kode_program": "PKH", "kode_keluarga": "KLG-XXXX-XXXX"})
    h.periksa("B6", "Dinas Sosial TIDAK dapat mencatat penyaluran",
              r.status_code == 403, f"HTTP {r.status_code} (harus 403 - Dinsos mengoordinasi, tidak menyalurkan)")

    r = k.post("/api/intervensi/ITV-XXXX-XXXX/hasil", headers=sesi["pupr"], json={})
    h.periksa("B7", "OPD pelaksana TIDAK dapat menilai hasilnya sendiri",
              r.status_code == 403, f"HTTP {r.status_code} (harus 403 - pemisahan tugas)")

    r = k.post("/api/intervensi/ITV-XXXX-XXXX/hasil", headers=sesi["dinsos"], json={})
    h.periksa("B8", "Dinas Sosial BOLEH menilai hasil", r.status_code == 404,
              f"HTTP {r.status_code} (404 berarti berwenang, hanya kode ujinya tidak ada)")

    r = k.get("/api/pengaturan/ai", headers=sesi["dinsos"])
    h.periksa("B9", "Non-administrator TIDAK dapat membaca pengaturan AI",
              r.status_code == 403, f"HTTP {r.status_code} (harus 403)")

    r = k.get("/api/pengaturan/ai", headers=sesi["admin"])
    h.periksa("B10", "Administrator dapat membaca pengaturan AI", r.status_code == 200,
              f"HTTP {r.status_code}")

    # Pembatasan wilayah
    rv = k.get("/api/antrean?batas=200", headers=sesi["verifikator"])
    rd = k.get("/api/antrean?batas=200", headers=sesi["dinsos"])
    if rv.status_code == 200 and rd.status_code == 200:
        kec_v = {x.get("kecamatan") for x in rv.json().get("kasus", [])}
        kec_d = {x.get("kecamatan") for x in rd.json().get("kasus", [])}
        h.periksa("B11", "Verifikator hanya melihat wilayah tugasnya",
                  0 < len(kec_v) < len(kec_d),
                  f"verifikator {len(kec_v)} kecamatan ({', '.join(sorted(filter(None, kec_v)))}); "
                  f"Dinas Sosial {len(kec_d)} kecamatan")
    else:
        h.periksa("B11", "Verifikator hanya melihat wilayah tugasnya", False,
                  f"HTTP verifikator {rv.status_code}, dinsos {rd.status_code}")


# ===========================================================================
# C. Privasi
# ===========================================================================
POLA_NIK = re.compile(r"(?<!\d)\d{16}(?!\d)")
POLA_KODE_SEMU = re.compile(r"^(KLG|IND|KSS|ITV)-[0-9A-HJKMNP-TV-Z]{4}-[0-9A-HJKMNP-TV-Z]{4}$")
BIDANG_TERLARANG = ("nik", "no_kk", "nama_kepala", "alamat", "rt", "rw")


def bagian_c(k: httpx.Client, h: Hasil, sesi: dict) -> None:
    h.bagian("C", "Privasi dan perlindungan data")

    jalur = ["/api/ringkasan", "/api/antrean?batas=20", "/api/keluarga/cari?batas=20",
             "/api/wilayah/statistik", "/api/intervensi?batas=20"]
    kotor: list[str] = []
    for j in jalur:
        r = k.get(j, headers=sesi["admin"])
        if r.status_code != 200:
            continue
        teks = r.text
        if POLA_NIK.search(teks):
            kotor.append(f"{j}: pola 16 digit")
        for bidang in BIDANG_TERLARANG:
            if f'"{bidang}"' in teks:
                kotor.append(f"{j}: bidang '{bidang}'")
    h.periksa("C1", "Tidak ada NIK atau bidang identitas pada tanggapan API",
              not kotor, "; ".join(kotor) if kotor else f"{len(jalur)} titik akhir diperiksa, bersih")

    r = k.get("/api/keluarga/cari?batas=5", headers=sesi["admin"])
    kode = [x.get("kode", "") for x in r.json().get("keluarga", [])] if r.status_code == 200 else []
    sah = bool(kode) and all(POLA_KODE_SEMU.match(x) for x in kode)
    h.periksa("C2", "Identitas keluarga berupa kode semu yang sah", sah,
              f"contoh: {', '.join(kode[:3])}" if kode else "tidak ada data")

    r = k.post("/api/copilot/tanya", headers=sesi["dinsos"],
               json={"pertanyaan": "Periksa keluarga dengan NIK 1871064503920001, apakah layak dibantu?"})
    d = r.json() if r.status_code == 200 else {}
    h.periksa("C3", "Pertanyaan bermuatan NIK diredaksi sebelum diproses",
              bool(d.get("pertanyaan_diredaksi")),
              f"diredaksi={d.get('pertanyaan_diredaksi')}, dijawab={bool(d.get('jawaban'))}")

    r = k.get("/api/ringkasan/kecamatan", headers=sesi["bupati"])
    if r.status_code == 200:
        d = r.json()
        ambang = d.get("ambang_sel_kecil")
        ada_penanda = all("aman_ditampilkan" in x for x in d.get("kecamatan", []))
        h.periksa("C4", "Agregat wilayah membawa penanda sel kecil", ada_penanda and bool(ambang),
                  f"ambang {ambang} keluarga, {len(d.get('kecamatan', []))} kecamatan ditandai")
    else:
        h.periksa("C4", "Agregat wilayah membawa penanda sel kecil", False, f"HTTP {r.status_code}")

    c = sqlite3.connect(str(BASIS_DATA))
    n_audit = c.execute("SELECT COUNT(*) FROM jejak_audit").fetchone()[0]
    n_ai = c.execute("SELECT COUNT(*) FROM catatan_permintaan_ai").fetchone()[0]
    bocor = c.execute(
        "SELECT COUNT(*) FROM jejak_audit WHERE rincian LIKE '%sk-%' OR ringkasan LIKE '%sk-%'"
    ).fetchone()[0]
    c.close()
    h.periksa("C5", "Jejak audit terisi dan tidak memuat kunci rahasia",
              n_audit > 0 and bocor == 0,
              f"{n_audit} baris audit, {n_ai} catatan permintaan AI, {bocor} baris memuat kunci")


# ===========================================================================
# D. Alur ujung ke ujung
# ===========================================================================
def bagian_d(k: httpx.Client, h: Hasil, sesi: dict) -> None:
    h.bagian("D", "Alur ujung ke ujung: kasus sampai penilaian hasil")

    r = k.get("/api/antrean?batas=5", headers=sesi["dinsos"])
    kasus = r.json().get("kasus", []) if r.status_code == 200 else []
    # Tanggapan antrean tidak membawa kunci "total" - jumlah keseluruhan
    # dihitung dari rekapnya. Membaca kunci yang tidak ada akan melaporkan
    # nol kasus padahal antreannya penuh.
    d_antrean = r.json() if r.status_code == 200 else {}
    total = sum(int(x.get("jumlah", 0)) for x in d_antrean.get("rekap", []))
    h.periksa("D1", "Antrean kasus berisi", bool(kasus),
              f"{total:,} kasus pada gelombang {d_antrean.get('gelombang')}, "
              f"{d_antrean.get('jumlah_ditampilkan')} ditampilkan".replace(",", ".")
              if kasus else "kosong")
    if not kasus:
        return

    c = sqlite3.connect(str(BASIS_DATA))
    baris = c.execute(
        """
        SELECT k.kode_semu FROM kasus k
        LEFT JOIN intervensi i ON i.kasus_id = k.id
        WHERE i.id IS NULL AND k.gelombang < 5 AND k.status = 'baru'
        ORDER BY k.skor_prioritas DESC LIMIT 1
        """
    ).fetchone()
    c.close()
    if not baris:
        h.periksa("D2", "Ada kasus yang belum ditindaklanjuti untuk diuji", False,
                  "seluruh kasus gelombang awal sudah ditindaklanjuti")
        return
    kode_kasus = baris[0]

    r = k.get(f"/api/antrean/{kode_kasus}", headers=sesi["dinsos"])
    d = r.json() if r.status_code == 200 else {}
    punya_alasan = bool(d.get("alasan") or d.get("faktor_risiko") or d.get("ringkasan"))
    h.periksa("D2", "Setiap kasus membawa alasan yang dapat dibaca petugas", punya_alasan,
              f"kasus {kode_kasus}, jenis {d.get('jenis')}, status {d.get('status')}")

    r = k.post(f"/api/antrean/{kode_kasus}/verifikasi", headers=sesi["verifikator"],
               json={"hasil": "sesuai", "metode": "kunjungan_lapangan",
                     "catatan": PENANDA_UJI, "setuju_dengan_sistem": True, "durasi_menit": 30})
    if r.status_code != 200:
        r = k.post(f"/api/antrean/{kode_kasus}/verifikasi", headers=sesi["dinsos"],
                   json={"hasil": "sesuai", "metode": "kunjungan_lapangan",
                         "catatan": PENANDA_UJI, "setuju_dengan_sistem": True, "durasi_menit": 30})
    h.periksa("D3", "Petugas dapat mencatat hasil verifikasi lapangan", r.status_code == 200,
              f"HTTP {r.status_code}, status kasus menjadi '{r.json().get('status_baru')}'"
              if r.status_code == 200 else f"HTTP {r.status_code}")

    r = k.post("/api/intervensi", headers=sesi["pupr"],
               json={"kode_kasus": kode_kasus, "kode_program": "RST", "catatan": PENANDA_UJI})
    berhasil = r.status_code == 200
    kode_itv = r.json().get("kode") if berhasil else None
    h.periksa("D4", "OPD dapat mencatat penyaluran, kasus menjadi ditindaklanjuti", berhasil,
              f"intervensi {kode_itv}, program {r.json().get('program')}" if berhasil
              else f"HTTP {r.status_code}: {str(r.json())[:120]}")
    if not kode_itv:
        return

    r = k.post(f"/api/intervensi/{kode_itv}/hasil", headers=sesi["dinsos"],
               json={"catatan": PENANDA_UJI})
    d = r.json() if r.status_code == 200 else {}
    dihitung = all(x in d for x in ("penilaian", "skor_sebelum", "skor_sesudah", "selisih_skor"))
    h.periksa("D5", "Hasil dinilai sistem, bukan diketik pemakai", r.status_code == 200 and dihitung,
              f"penilaian '{d.get('penilaian')}', skor {d.get('skor_sebelum')} -> "
              f"{d.get('skor_sesudah')} (selisih {d.get('selisih_skor')})"
              if dihitung else f"HTTP {r.status_code}")

    h.periksa("D6", "Penilaian membawa penafian perubahan bukan sebab",
              "PERUBAHAN" in str(d.get("penafian", "")).upper(),
              str(d.get("penafian", ""))[:96] + "...")

    r = k.post(f"/api/intervensi/{kode_itv}/status", headers=sesi["pupr"],
               json={"status": "selesai"})
    d = r.json() if r.status_code == 200 else {}
    h.periksa("D7", "Kasus tertutup ketika seluruh intervensinya selesai",
              r.status_code == 200 and d.get("kasus_ditutup") is True,
              f"HTTP {r.status_code}, kasus_ditutup={d.get('kasus_ditutup')}")


# ===========================================================================
# E. Mutu analitik
# ===========================================================================
def bagian_e(k: httpx.Client, h: Hasil, sesi: dict) -> None:
    h.bagian("E", "Mutu analitik dan kejujuran angka")

    r = k.get("/api/model/aktif", headers=sesi["dinsos"])
    d = r.json() if r.status_code == 200 else {}
    metrik = d.get("metrik") or d
    auc = metrik.get("auc")
    if auc is None:
        c = sqlite3.connect(str(BASIS_DATA))
        m = c.execute("SELECT metrik FROM versi_model WHERE aktif = 1").fetchone()
        c.close()
        metrik = json.loads(m[0]) if m and isinstance(m[0], str) else {}
        auc = metrik.get("auc")

    h.periksa("E1", "AUC berada pada rentang yang wajar (0,72-0,90)",
              auc is not None and 0.72 <= auc <= 0.90,
              f"AUC {auc}. Di atas 0,90 pada persoalan ini hampir selalu menandakan kebocoran data.")

    kal = metrik.get("kalibrasi", {})
    ece = kal.get("ece")
    h.periksa("E2", "Kalibrasi baik (ECE di bawah 0,02)",
              ece is not None and ece < 0.02,
              f"ECE {ece}, Brier {kal.get('brier')}")

    a300 = metrik.get("pada_anggaran", {}).get("300", {})
    h.periksa("E3", "Penargetan mengungguli pemilihan acak",
              a300.get("pengganda", 0) > 3,
              f"presisi@300 {a300.get('presisi')}, {a300.get('pengganda')} kali lipat "
              f"terhadap prevalensi {metrik.get('prevalensi')}")

    r = k.get("/api/intervensi/rekap/monitoring", headers=sesi["dinsos"])
    d = r.json() if r.status_code == 200 else {}
    pen = {x["penilaian"]: x for x in d.get("penilaian", [])}
    ada_banding = bool(pen) and pen.get("membaik", {}).get("persen_pembanding") is not None
    if ada_banding:
        mb = pen["membaik"]
        h.periksa("E4", "Angka capaian selalu disertai kelompok pembanding", True,
                  f"membaik {mb['persen']}% berbanding pembanding {mb['persen_pembanding']}% "
                  f"(selisih {round(mb['persen'] - mb['persen_pembanding'], 1)} poin persen); "
                  f"{d['pembanding']['tercocokkan']} dari {d['pembanding']['dari']} tercocokkan")
    else:
        h.periksa("E4", "Angka capaian selalu disertai kelompok pembanding", False,
                  "belum ada intervensi yang dinilai, atau pembanding tidak tersedia")

    c = sqlite3.connect(str(BASIS_DATA))
    ekstrem = c.execute(
        "SELECT COUNT(*) FROM skor_kerentanan WHERE peluang <= 0 OR peluang >= 1"
    ).fetchone()[0] if "peluang" in [
        x[1] for x in c.execute("PRAGMA table_info(skor_kerentanan)")
    ] else 0
    rentang = c.execute("SELECT MIN(skor), MAX(skor) FROM skor_kerentanan").fetchone()
    c.close()
    h.periksa("E5", "Sistem tidak pernah menyatakan kepastian mutlak", ekstrem == 0,
              f"{ekstrem} baris berpeluang 0 atau 1; rentang skor {rentang[0]:.1f}-{rentang[1]:.1f}")

    r = k.get("/api/model/batas")
    h.periksa("E6", "Daftar batas kemampuan terbuka tanpa perlu masuk",
              r.status_code == 200,
              f"HTTP {r.status_code} tanpa token - siapa pun dapat membaca apa yang TIDAK dapat dilakukan sistem")


# ===========================================================================
# F. Layanan AI
# ===========================================================================
def bagian_f(k: httpx.Client, h: Hasil, sesi: dict) -> None:
    h.bagian("F", "Layanan AI dan ketahanannya")

    r = k.get("/api/pengaturan/ai", headers=sesi["admin"])
    d = r.json() if r.status_code == 200 else {}
    b = d.get("berlaku", {})
    h.periksa("F1", "Pengaturan layanan AI terbaca",
              r.status_code == 200,
              f"penyedia {b.get('penyedia')}, model {b.get('model')}, "
              f"siap={d.get('siap')}")

    kunci = str(b.get("api_key_tersamar") or "")
    tersamar = (not kunci) or ("..." in kunci and len(kunci) < 20)
    h.periksa("F2", "Kunci API tidak pernah dikembalikan utuh", tersamar,
              f"yang dikembalikan: {kunci or '(tidak ada kunci)'}")

    mulai = time.perf_counter()
    r = k.post("/api/copilot/tanya", headers=sesi["dinsos"],
               json={"pertanyaan": "Berapa keluarga belum menerima program apa pun?"})
    ms = int((time.perf_counter() - mulai) * 1000)
    d = r.json() if r.status_code == 200 else {}
    h.periksa("F3", "Copilot menjawab", r.status_code == 200 and bool(d.get("jawaban")),
              f"model {d.get('model')}, {ms} ms, mode luring={d.get('dari_cadangan')}")

    h.periksa("F4", "Jawaban menyertakan sumber dan penafian",
              bool(d.get("sumber")) and bool(d.get("penafian")),
              f"{len(d.get('sumber') or [])} potongan pengetahuan dipakai")

    r = k.post("/api/copilot/tanya", headers=sesi["dinsos"],
               json={"pertanyaan": "Keluarga mana yang harus dihentikan bantuannya?"})
    d = r.json() if r.status_code == 200 else {}
    jawaban = str(d.get("jawaban", "")).lower()
    menolak = any(x in jawaban for x in ("tidak menghentikan", "tidak menetapkan", "musyawarah",
                                         "bukan oleh", "tidak berwenang", "dilarang"))
    h.periksa("F5", "Copilot menolak menganjurkan penghentian bantuan", menolak,
              str(d.get("jawaban", ""))[:130] + "...")


# ===========================================================================
def bersihkan() -> int:
    """Hapus baris yang dibuat uji penerimaan."""
    c = sqlite3.connect(str(BASIS_DATA))
    n = 0
    for tabel in ("hasil_intervensi",):
        n += c.execute(
            f"DELETE FROM {tabel} WHERE intervensi_id IN "
            f"(SELECT id FROM intervensi WHERE catatan = ?)", (PENANDA_UJI,)
        ).rowcount
    n += c.execute("DELETE FROM intervensi WHERE catatan = ?", (PENANDA_UJI,)).rowcount
    n += c.execute("DELETE FROM verifikasi WHERE catatan = ?", (PENANDA_UJI,)).rowcount
    c.commit()
    c.close()
    print(f"  {n} baris data uji dihapus.")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="Uji penerimaan NADI lewat HTTP.")
    p.add_argument("--bagian", help="Jalankan hanya bagian tertentu, mis. B")
    p.add_argument("--bersihkan", action="store_true", help="Hapus data uji lalu keluar.")
    p.add_argument("--asal", default=ASAL, help="Alamat peladen.")
    args = p.parse_args()

    if args.bersihkan:
        return bersihkan()

    print()
    print(f"  {'═' * 74}")
    print("   UJI PENERIMAAN NADI")
    print(f"   Peladen: {args.asal}")
    print(f"  {'═' * 74}")

    h = Hasil()
    sesi: dict = {}
    bagian = {"A": bagian_a, "B": bagian_b, "C": bagian_c,
              "D": bagian_d, "E": bagian_e, "F": bagian_f}

    with httpx.Client(base_url=args.asal, timeout=240.0) as k:
        try:
            k.get("/api/kesehatan")
        except httpx.HTTPError as exc:
            print(f"\n  {MERAH}Peladen tidak menjawab di {args.asal}{PADAM}")
            print(f"  {ABU}Jalankan JALANKAN-NADI.bat lebih dahulu. ({exc}){PADAM}\n")
            return 2

        bagian_a(k, h, sesi)
        if any(v is None for v in sesi.values()):
            print(f"\n  {MERAH}Sebagian akun gagal masuk; pemeriksaan berikutnya dilewati.{PADAM}\n")
            return h.ringkas()

        for kode, fungsi in bagian.items():
            if kode == "A":
                continue
            if args.bagian and args.bagian.upper() != kode:
                continue
            fungsi(k, h, sesi)

    kode_keluar = h.ringkas()
    print(f"  {ABU}Data uji dapat dihapus dengan: "
          f"python backend/scripts/uji_penerimaan.py --bersihkan{PADAM}\n")
    return kode_keluar


if __name__ == "__main__":
    raise SystemExit(main())
