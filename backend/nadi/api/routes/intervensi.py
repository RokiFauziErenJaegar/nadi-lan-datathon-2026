"""Outcome Monitoring - pencatatan intervensi dan penilaian hasilnya.

Modul ini menutup lingkar yang dijanjikan proposal: kasus terdeteksi, petugas
memverifikasi, intervensi dicatat, lalu hasilnya dinilai terhadap kondisi
keluarga pada gelombang berikutnya.

Tiga keputusan rancangan yang menentukan bentuk seluruh modul ini:

**Penilaian dihitung, bukan diketik.** Bidang ``penilaian`` tidak pernah
diterima dari pemanggil. Ia diturunkan dari selisih skor kerentanan antara dua
gelombang, memakai ambang yang sama bagi setiap keluarga. Petugas hanya
memicu penilaian dan menambahkan catatan. Akibatnya angka capaian pada layar
monitoring tidak dapat dipoles oleh pihak yang dinilai - dan itulah satu-
satunya cara angka tersebut berguna bagi pimpinan yang membacanya.

**Perubahan bukan sebab.** Skor keluarga naik dan turun karena banyak hal:
panen membaik, anggota keluarga bekerja lagi, guncangan mereda sendiri, atau
sekadar regresi ke rata-rata. Diukur pada seluruh 200.000 pengamatan
antargelombang, simpangan baku perubahan skor adalah 7,0 poin, dan 11,4 persen
keluarga membaik lebih dari 5 poin **tanpa menerima apa pun**. Karena itu
setiap angka capaian pada modul ini selalu disajikan berdampingan dengan
tingkat perubahan kelompok pembanding: keluarga sebanding yang tidak menerima
intervensi. Tanpa pembanding itu, "tiga puluh persen membaik" tidak berarti
apa-apa.

**Yang mencatat bukan yang menilai.** Kewenangan ``CATAT_INTERVENSI`` dipegang
OPD pelaksana, ``CATAT_OUTCOME`` dipegang Dinas Sosial. Pemisahan itu
ditegakkan di matriks kewenangan, bukan di sini - lihat catatan pada
``nadi/security/rbac.py``.
"""

from __future__ import annotations

import logging
from datetime import date, datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy import select, text

from nadi.api.deps import KonteksPengguna, PenggunaAktif, SesiDB, catat_audit, wajib
from nadi.db.enums import StatusIntervensi, StatusKasus
from nadi.db.models import HasilIntervensi, Intervensi, Kasus
from nadi.security.pseudonym import kode_intervensi
from nadi.security.rbac import AMBANG_SEL_KECIL, CakupanData, Kewenangan

logger = logging.getLogger("nadi.api.intervensi")
router = APIRouter(prefix="/intervensi", tags=["intervensi"])


# ---------------------------------------------------------------------------
# Ambang penilaian
# ---------------------------------------------------------------------------
# Diturunkan dari data, bukan dipilih karena enak dilihat. Sebaran perubahan
# skor antargelombang pada seluruh keluarga: rerata -0,28 dan simpangan baku
# 7,00 poin. Ambang lima poin berarti kira-kira 0,7 simpangan baku - cukup
# besar untuk melampaui derau pencatatan biasa, namun tidak begitu besar
# sehingga hanya perubahan dramatis yang terhitung.
#
# Pada ambang ini, tanpa intervensi apa pun: 11,4 persen keluarga tergolong
# membaik, 9,7 persen memburuk, 78,8 persen tetap. Angka-angka itulah garis
# dasar yang wajib ditampilkan bersama setiap capaian.
AMBANG_PERUBAHAN_BERMAKNA: float = 5.0

PENILAIAN_MEMBAIK = "membaik"
PENILAIAN_TETAP = "tetap"
PENILAIAN_MEMBURUK = "memburuk"

# Lebar pita pencocokan kelompok pembanding. Keluarga dengan skor awal tinggi
# lebih mungkin turun dengan sendirinya - regresi ke rata-rata bekerja paling
# kuat di ujung sebaran. Membandingkan tanpa mencocokkan skor awal akan
# melebih-lebihkan capaian intervensi yang menyasar keluarga paling rentan,
# yakni justru intervensi yang paling penting dinilai jujur.
LEBAR_PITA_SKOR: float = 10.0

PENAFIAN_OUTCOME = (
    "Angka pada modul ini menunjukkan PERUBAHAN kondisi, bukan SEBAB. "
    "Keluarga yang membaik setelah menerima intervensi belum tentu membaik "
    "karena intervensi tersebut. Bandingkan selalu dengan kelompok pembanding "
    "yang disertakan pada setiap rekap."
)


def _penilaian_dari_selisih(selisih: float) -> str:
    """Terjemahkan selisih skor menjadi penilaian.

    Skor kerentanan naik ketika keadaan memburuk, sehingga selisih negatif
    berarti membaik. Aturan ini disimpan di satu tempat agar tidak ada dua
    bagian sistem yang menghitungnya berbeda.
    """
    if selisih <= -AMBANG_PERUBAHAN_BERMAKNA:
        return PENILAIAN_MEMBAIK
    if selisih >= AMBANG_PERUBAHAN_BERMAKNA:
        return PENILAIAN_MEMBURUK
    return PENILAIAN_TETAP


def _gelombang_terakhir(sesi) -> int:
    return int(sesi.execute(text("SELECT MAX(gelombang) FROM snapshot_keluarga")).scalar() or 0)


def _batasi_opd(pengguna: KonteksPengguna) -> int | None:
    """Kembalikan id OPD yang boleh dilihat pengguna, atau None bila seluruhnya.

    RBAC proyek ini membatasi baris menurut wilayah, bukan menurut OPD -
    ``CakupanData`` memang tidak punya dimensi itu. Padahal seorang petugas
    dinas tidak berkepentingan membaca catatan penyaluran dinas lain. Batasan
    tersebut karena itu ditegakkan di sini, secara eksplisit, dan bukan
    diserahkan kepada lapisan kewenangan yang tidak mengenal konsepnya.
    """
    if pengguna.cakupan == CakupanData.SELURUH_KABUPATEN:
        return None
    return pengguna.opd_id


# ===========================================================================
# Pencatatan intervensi
# ===========================================================================
class PermintaanIntervensi(BaseModel):
    kode_program: str = Field(min_length=2, max_length=32)
    kode_kasus: str | None = Field(None, max_length=20)
    kode_keluarga: str | None = Field(None, max_length=20)
    kode_opd: str | None = Field(None, max_length=32)
    tanggal_mulai: date | None = None
    nilai_manfaat_bulanan: float | None = Field(None, ge=0)
    komponen: list[str] | None = None
    catatan: str | None = Field(None, max_length=2000)


@router.post("", summary="Catat intervensi yang disalurkan")
def catat(
    data: PermintaanIntervensi,
    sesi: SesiDB,
    request: Request,
    pengguna: KonteksPengguna = Depends(wajib(Kewenangan.CATAT_INTERVENSI)),
) -> dict:
    """Catat satu intervensi yang benar-benar disalurkan kepada keluarga.

    Titik akhir ini menerima ``kode_kasus`` atau ``kode_keluarga``. Bila kasus
    yang disebutkan, keluarganya diturunkan dari kasus itu dan status kasus
    berpindah ke ``ditindaklanjuti`` - sehingga jejak dari deteksi sampai
    penyaluran tetap utuh dan dapat ditelusuri kembali oleh pemeriksa.
    """
    kasus: Kasus | None = None
    if data.kode_kasus:
        kasus = sesi.scalar(select(Kasus).where(Kasus.kode_semu == data.kode_kasus.strip().upper()))
        if kasus is None:
            raise HTTPException(404, f"Kasus '{data.kode_kasus}' tidak ditemukan.")
        keluarga_id = kasus.keluarga_id
        gelombang_mulai = kasus.gelombang
    elif data.kode_keluarga:
        baris = sesi.execute(
            text("SELECT id FROM keluarga WHERE kode_semu = :k"),
            {"k": data.kode_keluarga.strip().upper()},
        ).first()
        if baris is None:
            raise HTTPException(404, f"Keluarga '{data.kode_keluarga}' tidak ditemukan.")
        keluarga_id = int(baris.id)
        gelombang_mulai = _gelombang_terakhir(sesi)
    else:
        raise HTTPException(422, "Sebutkan kode_kasus atau kode_keluarga.")

    program = sesi.execute(
        text("SELECT id, singkatan, nama_resmi, biaya_satuan_tahunan FROM program WHERE singkatan = :s"),
        {"s": data.kode_program.strip().upper()},
    ).first()
    if program is None:
        raise HTTPException(404, f"Program '{data.kode_program}' tidak dikenal.")

    # OPD: yang disebut pemanggil bila ia berwenang lintas dinas, jika tidak
    # selalu OPD pengguna sendiri. Petugas satu dinas tidak boleh mencatatkan
    # penyaluran atas nama dinas lain.
    opd_id: int | None = pengguna.opd_id
    if data.kode_opd:
        baris = sesi.execute(
            text("SELECT id FROM opd WHERE singkatan = :s"), {"s": data.kode_opd.strip()}
        ).first()
        if baris is None:
            raise HTTPException(404, f"OPD '{data.kode_opd}' tidak dikenal.")
        diminta = int(baris.id)
        if diminta != pengguna.opd_id and pengguna.cakupan != CakupanData.SELURUH_KABUPATEN:
            raise HTTPException(403, "Anda hanya dapat mencatat penyaluran atas nama OPD sendiri.")
        opd_id = diminta

    itv = Intervensi(
        kode_semu="",  # diisi setelah flush, lihat catatan di bawah
        keluarga_id=keluarga_id,
        program_id=int(program.id),
        opd_id=opd_id,
        kasus_id=kasus.id if kasus else None,
        gelombang_mulai=gelombang_mulai,
        tanggal_mulai=data.tanggal_mulai or date.today(),
        status=StatusIntervensi.BERJALAN,
        nilai_manfaat_bulanan=data.nilai_manfaat_bulanan,
        komponen=data.komponen,
        ditetapkan_oleh_id=pengguna.id,
        catatan=data.catatan,
    )
    sesi.add(itv)

    # Kode semu diturunkan dari id, sehingga keunikannya dijamin basis data
    # meskipun tabel intervensi tidak memiliki UniqueConstraint pada kolom itu.
    # Karena id baru ada setelah flush, kode diisi pada langkah kedua.
    sesi.flush()
    itv.kode_semu = kode_intervensi(itv.id)

    if kasus is not None:
        kasus.status = StatusKasus.DITINDAKLANJUTI

    catat_audit(
        sesi,
        pengguna,
        "catat_intervensi",
        entitas="intervensi",
        entitas_id=itv.kode_semu,
        ringkasan=f"Program {program.singkatan} untuk kasus {data.kode_kasus or '-'}",
        request=request,
        rincian={
            "program": program.singkatan,
            "kasus": data.kode_kasus,
            "nilai_manfaat_bulanan": data.nilai_manfaat_bulanan,
        },
    )
    sesi.commit()

    return {
        "kode": itv.kode_semu,
        "status": StatusIntervensi.BERJALAN.value,
        "program": program.nama_resmi,
        "gelombang_mulai": gelombang_mulai,
        "kasus": data.kode_kasus,
        "catatan": (
            "Hasil intervensi baru dapat dinilai setelah tersedia potret kondisi "
            "keluarga pada gelombang berikutnya."
        ),
    }


class PermintaanStatus(BaseModel):
    status: StatusIntervensi
    tanggal_selesai: date | None = None
    catatan: str | None = Field(None, max_length=2000)


@router.post("/{kode}/status", summary="Perbarui status intervensi")
def ubah_status(
    kode: str,
    data: PermintaanStatus,
    sesi: SesiDB,
    request: Request,
    pengguna: KonteksPengguna = Depends(wajib(Kewenangan.CATAT_INTERVENSI)),
) -> dict:
    """Pindahkan intervensi ke tahap berikutnya.

    Ketika seluruh intervensi pada satu kasus selesai, kasusnya ikut ditutup.
    Penutupan itu tidak pernah terjadi sendiri pada versi sebelumnya - status
    ``selesai`` ada pada kosakata sejak awal namun tidak pernah disetel kode
    mana pun, sehingga antrean tidak pernah menyusut meskipun pekerjaannya
    rampung.
    """
    itv = sesi.scalar(select(Intervensi).where(Intervensi.kode_semu == kode.strip().upper()))
    if itv is None:
        raise HTTPException(404, f"Intervensi '{kode}' tidak ditemukan.")

    batas_opd = _batasi_opd(pengguna)
    if batas_opd is not None and itv.opd_id != batas_opd:
        raise HTTPException(403, "Intervensi ini dicatat oleh OPD lain.")

    itv.status = data.status
    if data.catatan:
        itv.catatan = data.catatan
    if data.status == StatusIntervensi.SELESAI:
        itv.tanggal_selesai = data.tanggal_selesai or date.today()

    kasus_ditutup = False
    if itv.kasus_id is not None and data.status == StatusIntervensi.SELESAI:
        # Sesi proyek ini dibuat dengan autoflush=False, sehingga perubahan
        # status di atas belum terlihat oleh kueri SQL mentah di bawah. Tanpa
        # flush ini, intervensi yang baru saja diselesaikan masih terhitung
        # sebagai pekerjaan tersisa dan kasusnya tidak pernah tertutup -
        # persis kegagalan senyap yang paling sulit ditemukan, karena tidak
        # ada satu pun galat yang muncul.
        sesi.flush()
        tersisa = sesi.execute(
            text(
                "SELECT COUNT(*) FROM intervensi "
                "WHERE kasus_id = :k AND status NOT IN ('selesai', 'dibatalkan')"
            ),
            {"k": itv.kasus_id},
        ).scalar() or 0
        if tersisa == 0:
            kasus = sesi.get(Kasus, itv.kasus_id)
            if kasus is not None:
                kasus.status = StatusKasus.SELESAI
                kasus.ditutup_pada = datetime.now(timezone.utc)
                kasus_ditutup = True

    catat_audit(
        sesi,
        pengguna,
        "ubah_status_intervensi",
        entitas="intervensi",
        entitas_id=itv.kode_semu,
        ringkasan=f"Status menjadi {data.status.value}",
        request=request,
        rincian={"kasus_ditutup": kasus_ditutup},
    )
    sesi.commit()

    return {
        "kode": itv.kode_semu,
        "status": data.status.value,
        "kasus_ditutup": kasus_ditutup,
    }


# ===========================================================================
# Penilaian hasil
# ===========================================================================
class PermintaanHasil(BaseModel):
    gelombang_sesudah: int | None = Field(None, ge=0)
    catatan: str | None = Field(None, max_length=2000)


@router.post("/{kode}/hasil", summary="Nilai hasil intervensi")
def nilai_hasil(
    kode: str,
    data: PermintaanHasil,
    sesi: SesiDB,
    request: Request,
    pengguna: KonteksPengguna = Depends(wajib(Kewenangan.CATAT_OUTCOME)),
) -> dict:
    """Bandingkan kondisi keluarga sebelum dan sesudah intervensi.

    Seluruh angka dihitung dari basis data; pemanggil tidak dapat menentukan
    satu pun di antaranya. Yang dapat ia sumbangkan hanya catatan penjelas dan
    keputusan kapan penilaian dilakukan. Rancangan ini disengaja: bila pihak
    yang dinilai dapat menuliskan nilainya sendiri, seluruh layar monitoring
    berubah menjadi hiasan.
    """
    itv = sesi.scalar(select(Intervensi).where(Intervensi.kode_semu == kode.strip().upper()))
    if itv is None:
        raise HTTPException(404, f"Intervensi '{kode}' tidak ditemukan.")

    gel_sebelum = int(itv.gelombang_mulai)
    gel_sesudah = data.gelombang_sesudah if data.gelombang_sesudah is not None else _gelombang_terakhir(sesi)
    if gel_sesudah <= gel_sebelum:
        raise HTTPException(
            422,
            f"Belum ada potret kondisi sesudah gelombang {gel_sebelum}. "
            "Penilaian menunggu pemutakhiran data berikutnya.",
        )

    baris = sesi.execute(
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
        {"kid": itv.keluarga_id, "a": gel_sebelum, "b": gel_sesudah},
    ).all()
    potret = {int(b.gelombang): b for b in baris}
    if gel_sebelum not in potret or gel_sesudah not in potret:
        raise HTTPException(422, "Potret kondisi keluarga tidak lengkap untuk kedua gelombang.")

    a, b = potret[gel_sebelum], potret[gel_sesudah]
    skor_a, skor_b = float(a.skor), float(b.skor)
    selisih = round(skor_b - skor_a, 2)

    indikator = {
        "desil_kesejahteraan": [int(a.desil_kesejahteraan), int(b.desil_kesejahteraan)],
        "jumlah_program_diterima": [int(a.jumlah_program_diterima), int(b.jumlah_program_diterima)],
    }

    lama = sesi.scalar(select(HasilIntervensi).where(HasilIntervensi.intervensi_id == itv.id))
    hasil = lama or HasilIntervensi(intervensi_id=itv.id)
    hasil.keluarga_id = itv.keluarga_id  # denormalisasi; basis data tidak menjaganya
    hasil.gelombang_sebelum = gel_sebelum
    hasil.gelombang_sesudah = gel_sesudah
    hasil.skor_sebelum = round(skor_a, 2)
    hasil.skor_sesudah = round(skor_b, 2)
    hasil.selisih_skor = selisih
    hasil.miskin_sebelum = bool(a.status_miskin)
    hasil.miskin_sesudah = bool(b.status_miskin)
    hasil.pengeluaran_sebelum = float(a.pengeluaran_per_kapita)
    hasil.pengeluaran_sesudah = float(b.pengeluaran_per_kapita)
    hasil.indikator_berubah = indikator
    hasil.penilaian = _penilaian_dari_selisih(selisih)
    hasil.catatan = data.catatan
    hasil.dinilai_pada = datetime.now(timezone.utc)
    if lama is None:
        sesi.add(hasil)

    catat_audit(
        sesi,
        pengguna,
        "nilai_hasil_intervensi",
        entitas="intervensi",
        entitas_id=itv.kode_semu,
        ringkasan=f"Penilaian {hasil.penilaian}, selisih skor {selisih:+.2f}",
        request=request,
        rincian={"gelombang": [gel_sebelum, gel_sesudah], "dinilai_ulang": lama is not None},
    )
    sesi.commit()

    return {
        "kode": itv.kode_semu,
        "penilaian": hasil.penilaian,
        "skor_sebelum": hasil.skor_sebelum,
        "skor_sesudah": hasil.skor_sesudah,
        "selisih_skor": selisih,
        "gelombang": [gel_sebelum, gel_sesudah],
        "miskin_sebelum": hasil.miskin_sebelum,
        "miskin_sesudah": hasil.miskin_sesudah,
        "pengeluaran_sebelum": hasil.pengeluaran_sebelum,
        "pengeluaran_sesudah": hasil.pengeluaran_sesudah,
        "ambang_perubahan_bermakna": AMBANG_PERUBAHAN_BERMAKNA,
        "dinilai_ulang": lama is not None,
        "penafian": PENAFIAN_OUTCOME,
    }


# ===========================================================================
# Rekap monitoring
# ===========================================================================
# Dideklarasikan sebelum "/{kode}" karena FastAPI mencocokkan jalur menurut
# urutan pendaftaran; bila terbalik, "rekap" akan terbaca sebagai kode semu.
@router.get(
    "/rekap/monitoring",
    summary="Rekap capaian intervensi beserta kelompok pembanding",
    dependencies=[Depends(wajib(Kewenangan.BACA_OUTCOME))],
)
def rekap(sesi: SesiDB) -> dict:
    """Capaian intervensi, selalu berdampingan dengan kelompok pembanding.

    Bagian terpenting titik akhir ini bukan angka capaiannya, melainkan
    pembandingnya. Untuk setiap pasangan gelombang dan pita skor awal, dihitung
    pula bagaimana keluarga sebanding yang TIDAK menerima intervensi berubah
    pada rentang waktu yang sama. Selisih kedua angka itulah satu-satunya hal
    yang pantas disebut capaian - dan bahkan itu pun belum membuktikan sebab.
    """
    per_status = [
        {"status": r.status, "jumlah": int(r.n)}
        for r in sesi.execute(
            text("SELECT status, COUNT(*) AS n FROM intervensi GROUP BY status ORDER BY n DESC")
        ).all()
    ]

    dinilai = sesi.execute(
        text(
            """
            SELECT h.penilaian, h.skor_sebelum, h.selisih_skor,
                   h.gelombang_sebelum, h.gelombang_sesudah,
                   h.miskin_sebelum, h.miskin_sesudah,
                   p.singkatan AS program, o.singkatan AS opd
            FROM hasil_intervensi h
            JOIN intervensi i ON i.id = h.intervensi_id
            JOIN program p    ON p.id = i.program_id
            LEFT JOIN opd o   ON o.id = i.opd_id
            """
        )
    ).all()

    if not dinilai:
        return {
            "per_status": per_status,
            "dinilai": 0,
            "keterangan": "Belum ada intervensi yang dinilai hasilnya.",
            "ambang_perubahan_bermakna": AMBANG_PERUBAHAN_BERMAKNA,
            "penafian": PENAFIAN_OUTCOME,
        }

    hitung: dict[str, int] = {PENILAIAN_MEMBAIK: 0, PENILAIAN_TETAP: 0, PENILAIAN_MEMBURUK: 0}
    for d in dinilai:
        hitung[d.penilaian] = hitung.get(d.penilaian, 0) + 1
    total = len(dinilai)

    # --- Kelompok pembanding, dicocokkan pada gelombang dan pita skor awal ---
    pasangan = {(int(d.gelombang_sebelum), int(d.gelombang_sesudah)) for d in dinilai}
    pembanding: dict[tuple[int, int, int], dict[str, int]] = {}
    for gel_a, gel_b in pasangan:
        for r in sesi.execute(
            text(
                """
                SELECT CAST(a.skor / :lebar AS INTEGER)      AS pita,
                       b.skor - a.skor                        AS selisih
                FROM skor_kerentanan a
                JOIN skor_kerentanan b
                  ON b.keluarga_id = a.keluarga_id AND b.gelombang = :gb
                LEFT JOIN intervensi i ON i.keluarga_id = a.keluarga_id
                WHERE a.gelombang = :ga AND i.id IS NULL
                """
            ),
            {"ga": gel_a, "gb": gel_b, "lebar": LEBAR_PITA_SKOR},
        ).all():
            kunci = (gel_a, gel_b, int(r.pita))
            ember = pembanding.setdefault(
                kunci, {PENILAIAN_MEMBAIK: 0, PENILAIAN_TETAP: 0, PENILAIAN_MEMBURUK: 0}
            )
            ember[_penilaian_dari_selisih(float(r.selisih))] += 1

    # Harapan dasar: bagi setiap keluarga yang menerima intervensi, berapa
    # peluang ia membaik seandainya tidak menerima apa pun. Dirata-ratakan
    # atas seluruh keluarga yang dinilai, angka ini menjadi garis pembanding
    # yang setara - bukan rata-rata kabupaten yang komposisinya berbeda.
    harapan = {PENILAIAN_MEMBAIK: 0.0, PENILAIAN_TETAP: 0.0, PENILAIAN_MEMBURUK: 0.0}
    tercocokkan = 0
    for d in dinilai:
        kunci = (
            int(d.gelombang_sebelum),
            int(d.gelombang_sesudah),
            int(float(d.skor_sebelum) // LEBAR_PITA_SKOR),
        )
        ember = pembanding.get(kunci)
        if not ember:
            continue
        n = sum(ember.values())
        if n < AMBANG_SEL_KECIL:
            continue
        tercocokkan += 1
        for k in harapan:
            harapan[k] += ember[k] / n

    if tercocokkan:
        harapan = {k: v / tercocokkan for k, v in harapan.items()}

    keluar_miskin = sum(1 for d in dinilai if d.miskin_sebelum and not d.miskin_sesudah)
    masuk_miskin = sum(1 for d in dinilai if not d.miskin_sebelum and d.miskin_sesudah)

    per_program: dict[str, dict] = {}
    for d in dinilai:
        e = per_program.setdefault(d.program, {"program": d.program, "dinilai": 0, "membaik": 0, "selisih": 0.0})
        e["dinilai"] += 1
        e["membaik"] += 1 if d.penilaian == PENILAIAN_MEMBAIK else 0
        e["selisih"] += float(d.selisih_skor)

    return {
        "per_status": per_status,
        "dinilai": total,
        "penilaian": [
            {
                "penilaian": k,
                "jumlah": hitung.get(k, 0),
                "persen": round(hitung.get(k, 0) / total * 100, 1),
                "persen_pembanding": round(harapan.get(k, 0.0) * 100, 1) if tercocokkan else None,
            }
            for k in (PENILAIAN_MEMBAIK, PENILAIAN_TETAP, PENILAIAN_MEMBURUK)
        ],
        "pembanding": {
            "tercocokkan": tercocokkan,
            "dari": total,
            "keterangan": (
                "Kelompok pembanding adalah keluarga yang TIDAK menerima intervensi, "
                "dicocokkan pada gelombang yang sama dan pita skor awal selebar "
                f"{LEBAR_PITA_SKOR:.0f} poin. Sel dengan kurang dari {AMBANG_SEL_KECIL} "
                "keluarga tidak dipakai."
            ),
        },
        "selisih_skor_rata": round(sum(float(d.selisih_skor) for d in dinilai) / total, 2),
        "keluar_dari_miskin": keluar_miskin,
        "masuk_ke_miskin": masuk_miskin,
        "per_program": sorted(
            (
                {
                    # Bidang disebut satu per satu, bukan disebar dengan **e:
                    # akumulator "selisih" hanya alat hitung antara, dan
                    # menampilkannya di sebelah "selisih_rata" hanya akan
                    # membuat pembaca menebak-nebak mana yang benar.
                    "program": e["program"],
                    "dinilai": e["dinilai"],
                    "membaik": e["membaik"],
                    "persen_membaik": round(e["membaik"] / e["dinilai"] * 100, 1),
                    "selisih_rata": round(e["selisih"] / e["dinilai"], 2),
                }
                for e in per_program.values()
                if e["dinilai"] >= AMBANG_SEL_KECIL
            ),
            key=lambda e: e["dinilai"],
            reverse=True,
        ),
        "ambang_perubahan_bermakna": AMBANG_PERUBAHAN_BERMAKNA,
        "ambang_sel_kecil": AMBANG_SEL_KECIL,
        "penafian": PENAFIAN_OUTCOME,
    }


@router.get("", summary="Daftar intervensi", dependencies=[Depends(wajib(Kewenangan.BACA_OUTCOME))])
def daftar(
    sesi: SesiDB,
    pengguna: PenggunaAktif,
    status: str | None = Query(None),
    kode_program: str | None = Query(None),
    hanya_belum_dinilai: bool = Query(False),
    batas: int = Query(50, ge=1, le=500),
    lewati: int = Query(0, ge=0),
) -> dict:
    """Daftar intervensi yang tercatat, terbaru lebih dahulu."""
    syarat = ["1 = 1"]
    param: dict = {"batas": batas, "lewati": lewati}

    batas_opd = _batasi_opd(pengguna)
    if batas_opd is not None:
        syarat.append("i.opd_id = :opd")
        param["opd"] = batas_opd
    if status:
        syarat.append("i.status = :status")
        param["status"] = status
    if kode_program:
        syarat.append("p.singkatan = :prog")
        param["prog"] = kode_program.strip().upper()
    if hanya_belum_dinilai:
        syarat.append("h.id IS NULL")

    where = " AND ".join(syarat)
    total = sesi.execute(
        text(
            f"""
            SELECT COUNT(*) FROM intervensi i
            JOIN program p ON p.id = i.program_id
            LEFT JOIN hasil_intervensi h ON h.intervensi_id = i.id
            WHERE {where}
            """
        ),
        param,
    ).scalar() or 0

    baris = sesi.execute(
        text(
            f"""
            SELECT i.kode_semu, i.status, i.tanggal_mulai, i.tanggal_selesai,
                   i.gelombang_mulai, i.nilai_manfaat_bulanan,
                   p.singkatan AS program, p.nama_resmi AS program_nama,
                   o.singkatan AS opd,
                   k.kode_semu AS kasus,
                   kel.kode_semu AS keluarga,
                   desa.nama AS pekon, kec.nama AS kecamatan,
                   h.penilaian, h.selisih_skor, h.skor_sebelum, h.skor_sesudah
            FROM intervensi i
            JOIN program p        ON p.id = i.program_id
            JOIN keluarga kel     ON kel.id = i.keluarga_id
            JOIN wilayah desa     ON desa.id = kel.wilayah_id
            JOIN wilayah kec      ON kec.id = desa.induk_id
            LEFT JOIN opd o       ON o.id = i.opd_id
            LEFT JOIN kasus k     ON k.id = i.kasus_id
            LEFT JOIN hasil_intervensi h ON h.intervensi_id = i.id
            WHERE {where}
            ORDER BY i.dibuat_pada DESC, i.id DESC
            LIMIT :batas OFFSET :lewati
            """
        ),
        param,
    ).all()

    return {
        "total": int(total),
        "batas": batas,
        "lewati": lewati,
        "intervensi": [
            {
                "kode": b.kode_semu,
                "status": b.status,
                "tanggal_mulai": str(b.tanggal_mulai) if b.tanggal_mulai else None,
                "tanggal_selesai": str(b.tanggal_selesai) if b.tanggal_selesai else None,
                "gelombang_mulai": int(b.gelombang_mulai),
                "nilai_manfaat_bulanan": b.nilai_manfaat_bulanan,
                "program": b.program,
                "program_nama": b.program_nama,
                "opd": b.opd,
                "kasus": b.kasus,
                "keluarga": b.keluarga,
                "pekon": b.pekon,
                "kecamatan": b.kecamatan,
                "penilaian": b.penilaian,
                "selisih_skor": b.selisih_skor,
                "skor_sebelum": b.skor_sebelum,
                "skor_sesudah": b.skor_sesudah,
                "siap_dinilai": b.penilaian is None,
            }
            for b in baris
        ],
        "penafian": PENAFIAN_OUTCOME,
    }


@router.get("/{kode}", summary="Rincian satu intervensi", dependencies=[Depends(wajib(Kewenangan.BACA_OUTCOME))])
def rincian(kode: str, sesi: SesiDB, pengguna: PenggunaAktif) -> dict:
    """Rincian satu intervensi beserta hasilnya bila sudah dinilai."""
    b = sesi.execute(
        text(
            """
            SELECT i.kode_semu, i.status, i.tanggal_mulai, i.tanggal_selesai,
                   i.gelombang_mulai, i.nilai_manfaat_bulanan, i.komponen, i.catatan,
                   i.opd_id,
                   p.singkatan AS program, p.nama_resmi AS program_nama,
                   p.jenis_intervensi,
                   o.singkatan AS opd, o.nama_resmi AS opd_nama,
                   k.kode_semu AS kasus, k.jenis AS kasus_jenis,
                   kel.kode_semu AS keluarga,
                   desa.nama AS pekon, kec.nama AS kecamatan,
                   h.penilaian, h.selisih_skor, h.skor_sebelum, h.skor_sesudah,
                   h.gelombang_sebelum, h.gelombang_sesudah,
                   h.miskin_sebelum, h.miskin_sesudah,
                   h.pengeluaran_sebelum, h.pengeluaran_sesudah,
                   h.indikator_berubah, h.catatan AS catatan_hasil, h.dinilai_pada
            FROM intervensi i
            JOIN program p        ON p.id = i.program_id
            JOIN keluarga kel     ON kel.id = i.keluarga_id
            JOIN wilayah desa     ON desa.id = kel.wilayah_id
            JOIN wilayah kec      ON kec.id = desa.induk_id
            LEFT JOIN opd o       ON o.id = i.opd_id
            LEFT JOIN kasus k     ON k.id = i.kasus_id
            LEFT JOIN hasil_intervensi h ON h.intervensi_id = i.id
            WHERE i.kode_semu = :k
            """
        ),
        {"k": kode.strip().upper()},
    ).first()
    if b is None:
        raise HTTPException(404, f"Intervensi '{kode}' tidak ditemukan.")

    batas_opd = _batasi_opd(pengguna)
    if batas_opd is not None and b.opd_id != batas_opd:
        raise HTTPException(403, "Intervensi ini dicatat oleh OPD lain.")

    hasil = None
    if b.penilaian:
        hasil = {
            "penilaian": b.penilaian,
            "selisih_skor": b.selisih_skor,
            "skor_sebelum": b.skor_sebelum,
            "skor_sesudah": b.skor_sesudah,
            "gelombang": [int(b.gelombang_sebelum), int(b.gelombang_sesudah)],
            "miskin_sebelum": bool(b.miskin_sebelum),
            "miskin_sesudah": bool(b.miskin_sesudah),
            "pengeluaran_sebelum": b.pengeluaran_sebelum,
            "pengeluaran_sesudah": b.pengeluaran_sesudah,
            "indikator_berubah": b.indikator_berubah,
            "catatan": b.catatan_hasil,
            "dinilai_pada": str(b.dinilai_pada) if b.dinilai_pada else None,
        }

    return {
        "kode": b.kode_semu,
        "status": b.status,
        "tanggal_mulai": str(b.tanggal_mulai) if b.tanggal_mulai else None,
        "tanggal_selesai": str(b.tanggal_selesai) if b.tanggal_selesai else None,
        "gelombang_mulai": int(b.gelombang_mulai),
        "nilai_manfaat_bulanan": b.nilai_manfaat_bulanan,
        "komponen": b.komponen,
        "catatan": b.catatan,
        "program": {"kode": b.program, "nama": b.program_nama, "jenis": b.jenis_intervensi},
        "opd": {"kode": b.opd, "nama": b.opd_nama},
        "kasus": {"kode": b.kasus, "jenis": b.kasus_jenis} if b.kasus else None,
        "keluarga": {"kode": b.keluarga, "pekon": b.pekon, "kecamatan": b.kecamatan},
        "hasil": hasil,
        "ambang_perubahan_bermakna": AMBANG_PERUBAHAN_BERMAKNA,
        "penafian": PENAFIAN_OUTCOME,
    }


__all__ = ["router"]
