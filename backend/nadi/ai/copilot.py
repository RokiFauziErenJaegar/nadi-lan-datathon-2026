"""AI Policy Copilot - tanya jawab berbasis pengetahuan yang terkendali.

Perannya sengaja dipersempit, dan penyempitan itu adalah keputusan rancangan
yang paling menentukan pada modul ini: **copilot menjelaskan apa yang sudah ada
di dalam sistem, dan tidak menghasilkan penilaian baru tentang siapa pun.**

Ia boleh menerangkan mengapa sebuah kecamatan berisiko lebih tinggi, program apa
yang menangani sanitasi buruk, atau apa arti desil kesejahteraan. Ia tidak boleh
menyatakan sebuah keluarga layak menerima bantuan, tidak boleh memperkirakan
angka yang tidak dihitung sistem, dan tidak boleh menganjurkan penghentian
bantuan siapa pun.

Tiga lapis penjagaan bekerja bersamaan:

**Pengambilan terbatas.** Model bahasa hanya menerima potongan pengetahuan yang
diambil dari basis data dan katalog program. Ia tidak memiliki akses ke basis
data, tidak dapat menjalankan kueri, dan tidak dapat melihat apa pun di luar
yang disodorkan.

**Daftar-izin struktural.** Konteks disusun dari bidang yang ditetapkan satu per
satu. Nama, nomor induk kependudukan, alamat, dan koordinat tidak pernah masuk
karena tidak pernah disalin.

**Pemindaian keluar.** Muatan diperiksa :mod:`nadi.security.pii` tepat sebelum
dikirim. Bila lolos dua lapis sebelumnya namun tetap memuat pengenal pribadi,
permintaan dibatalkan - bukan disamarkan diam-diam.

Bila layanan model bahasa tidak tersedia, copilot tetap menjawab dari potongan
pengetahuan yang sama, hanya dengan bahasa templat. Angka yang disampaikan sama
persis; yang hilang hanyalah keluwesan kalimatnya.
"""

from __future__ import annotations

import logging
import re
import time
from dataclasses import dataclass, field
from typing import Any

from rank_bm25 import BM25Okapi
from sqlalchemy import text
from sqlalchemy.orm import Session

from nadi.ai.provider import (
    HasilLLM,
    LLMTidakTersedia,
    PesanChat,
    Peran,
    dapatkan_penyedia,
)
from nadi.security.pii import pastikan_bersih, redaksi_teks, ringkas_untuk_log

logger = logging.getLogger("nadi.copilot")

#: Banyaknya potongan pengetahuan yang disertakan pada satu jawaban.
JUMLAH_POTONGAN = 6

#: Panjang maksimum pertanyaan pengguna.
BATAS_PERTANYAAN = 600

INSTRUKSI_SISTEM = """\
Anda adalah asisten penjelas untuk NADI, sistem pendukung keputusan penanggulangan
kemiskinan di Kabupaten Pringsewu, Lampung.

ATURAN YANG TIDAK BOLEH DILANGGAR:

1. Jawab HANYA berdasarkan potongan pengetahuan yang diberikan di bawah. Bila
   jawabannya tidak ada di sana, katakan terus terang bahwa keterangan itu belum
   tersedia pada sistem, lalu sebutkan ke mana pengguna sebaiknya bertanya.
2. JANGAN PERNAH mengarang angka. Setiap angka yang Anda sebut harus muncul pada
   potongan pengetahuan. Bila sebuah angka bertanda tingkat keyakinan
   "perkiraan", sebutkan penandaan itu.
3. JANGAN menyatakan seseorang layak atau tidak layak menerima bantuan. Kelayakan
   ditetapkan lewat verifikasi petugas dan musyawarah pekon, bukan oleh Anda.
4. JANGAN menganjurkan penghentian, pengurangan, atau penundaan bantuan siapa pun.
5. Bila pengguna menanyakan identitas seseorang, jelaskan bahwa sistem ini tidak
   menyimpan nama, nomor induk kependudukan, maupun alamat - hanya kode semu.
6. Ingatkan bahwa seluruh data pada sistem ini bersifat sintetis apabila pengguna
   tampak menganggapnya data nyata.

7. JANGAN menuliskan proses berpikir, rencana menjawab, atau catatan untuk diri
   sendiri. Tulis langsung jawaban akhirnya saja. Sebagian model membeberkan
   penalarannya bila tidak diminta menahan diri - dan penalaran itu kerap
   berbahasa Inggris, sehingga tampil di layar petugas sebagai teks asing.

GAYA: Bahasa Indonesia yang jernih dan ringkas. Hindari istilah teknis tanpa
penjelasan. Sebutkan angka beserta satuannya. Panjang jawaban dua sampai lima
paragraf pendek, atau daftar bila lebih jelas demikian.
"""


@dataclass
class Potongan:
    """Satu potongan pengetahuan yang dapat diambil."""

    id: str
    judul: str
    isi: str
    jenis: str
    sumber: str | None = None

    def teks_cari(self) -> str:
        return f"{self.judul} {self.isi}"


@dataclass
class JawabanCopilot:
    jawaban: str
    potongan_dipakai: list[dict] = field(default_factory=list)
    dari_cadangan: bool = False
    model: str | None = None
    durasi_ms: int = 0
    pertanyaan_diredaksi: bool = False
    catatan: list[str] = field(default_factory=list)

    def ke_dict(self) -> dict[str, Any]:
        return {
            "jawaban": self.jawaban,
            "sumber": self.potongan_dipakai,
            "dari_cadangan": self.dari_cadangan,
            "model": self.model,
            "durasi_ms": self.durasi_ms,
            "pertanyaan_diredaksi": self.pertanyaan_diredaksi,
            "catatan": self.catatan,
            "penafian": (
                "Jawaban disusun dari basis pengetahuan sistem. Copilot tidak "
                "menetapkan kelayakan bantuan dan tidak membuat keputusan apa pun."
            ),
        }


# ===========================================================================
# Penyusunan basis pengetahuan
# ===========================================================================
def susun_basis_pengetahuan(sesi: Session) -> list[Potongan]:
    """Bentuk potongan pengetahuan dari basis data.

    Setiap potongan disusun dari bidang yang ditetapkan satu per satu. Tidak ada
    penyalinan menyeluruh dari tabel mana pun, sehingga penambahan kolom baru
    pada basis data tidak dapat diam-diam membocorkan isinya ke layanan luar.
    """
    potongan: list[Potongan] = []

    # --- Program ---
    for b in sesi.execute(
        text(
            """
            SELECT p.kode, p.nama_resmi, p.singkatan, p.deskripsi, p.kementerian,
                   p.jenis_intervensi, p.sumber_dana, p.frekuensi,
                   p.desil_min, p.desil_maks, p.biaya_satuan_tahunan,
                   p.mekanisme_penyaluran, p.status, p.tingkat_keyakinan, p.catatan,
                   GROUP_CONCAT(o.singkatan) AS opd
            FROM program p
            LEFT JOIN program_opd po ON po.program_id = p.id
            LEFT JOIN opd o          ON o.id = po.opd_id
            GROUP BY p.id
            """
        )
    ).all():
        biaya = (
            f"Perkiraan biaya Rp{b.biaya_satuan_tahunan:,.0f} per penerima per tahun. ".replace(",", ".")
            if b.biaya_satuan_tahunan
            else ""
        )
        potongan.append(
            Potongan(
                id=f"program:{b.kode}",
                judul=f"Program {b.nama_resmi} ({b.singkatan})",
                isi=(
                    f"{b.deskripsi or ''} Kementerian pengampu: {b.kementerian or 'tidak tercatat'}. "
                    f"OPD pelaksana di kabupaten: {b.opd or 'belum ditetapkan'}. "
                    f"Jenis intervensi: {b.jenis_intervensi}. Sumber dana: {b.sumber_dana}. "
                    f"Frekuensi: {b.frekuensi}. Sasaran desil {b.desil_min} sampai {b.desil_maks}. "
                    f"{biaya}Mekanisme: {b.mekanisme_penyaluran or 'tidak tercatat'}. "
                    f"Status: {b.status}. Tingkat keyakinan data: {b.tingkat_keyakinan}. "
                    f"{b.catatan or ''}"
                ),
                jenis="program",
                sumber="Katalog program NADI",
            )
        )

    # --- Faktor risiko ---
    for b in sesi.execute(
        text(
            """
            SELECT f.kode, f.nama, f.deskripsi, f.dimensi, f.indikator,
                   GROUP_CONCAT(p.singkatan) AS program
            FROM faktor_risiko f
            LEFT JOIN program_faktor_risiko pf ON pf.faktor_risiko_id = f.id
            LEFT JOIN program p                ON p.id = pf.program_id
            GROUP BY f.id
            """
        )
    ).all():
        potongan.append(
            Potongan(
                id=f"faktor:{b.kode}",
                judul=f"Faktor risiko {b.kode}: {b.nama}",
                isi=(
                    f"{b.deskripsi or ''} Dimensi: {b.dimensi}. "
                    f"Cara dikenali: {b.indikator or 'tidak tercatat'}. "
                    f"Program yang menanganinya: {b.program or 'belum ada'}."
                ),
                jenis="faktor_risiko",
                sumber="Katalog faktor risiko NADI",
            )
        )

    # --- Statistik kecamatan pada gelombang terakhir ---
    g = int(sesi.execute(text("SELECT MAX(gelombang) FROM statistik_wilayah")).scalar() or 0)
    for b in sesi.execute(
        text(
            """
            SELECT kec.nama, kec.kode, kec.jumlah_penduduk, kec.luas_km2, kec.klasifikasi,
                   SUM(st.jumlah_keluarga) AS keluarga,
                   SUM(st.jumlah_miskin)   AS miskin,
                   ROUND(SUM(st.jumlah_miskin)*100.0/NULLIF(SUM(st.jumlah_keluarga),0),2) AS persen,
                   ROUND(AVG(st.skor_rata_rata),1)          AS skor,
                   ROUND(AVG(st.persen_sanitasi_layak),1)   AS sanitasi,
                   ROUND(AVG(st.persen_air_minum_layak),1)  AS air,
                   ROUND(AVG(st.persen_hunian_layak),1)     AS hunian,
                   ROUND(AVG(st.persen_penerima_bantuan),1) AS bantuan
            FROM statistik_wilayah st
            JOIN wilayah desa ON desa.id = st.wilayah_id
            JOIN wilayah kec  ON kec.id = desa.induk_id
            WHERE st.gelombang = :g
            GROUP BY kec.id
            """
        ),
        {"g": g},
    ).all():
        potongan.append(
            Potongan(
                id=f"wilayah:{b.kode}",
                judul=f"Kecamatan {b.nama}",
                isi=(
                    f"Penduduk {b.jumlah_penduduk:,} jiwa, luas {b.luas_km2} kilometer persegi, "
                    f"tergolong {b.klasifikasi}. Pada data sistem: {b.keluarga:,} keluarga terdata, "
                    f"{b.miskin:,} di antaranya miskin ({b.persen} persen). "
                    f"Skor kerentanan rata-rata {b.skor} dari 100. "
                    f"Sanitasi layak {b.sanitasi} persen, air minum layak {b.air} persen, "
                    f"hunian layak {b.hunian} persen. "
                    f"Penerima bantuan {b.bantuan} persen keluarga."
                ).replace(",", "."),
                jenis="wilayah",
                sumber=f"Statistik wilayah NADI, gelombang {g}",
            )
        )

    # --- Kinerja model ---
    for b in sesi.execute(
        text(
            "SELECT nama, versi, jenis, algoritma, jumlah_fitur, jumlah_baris_latih, metrik, catatan "
            "FROM versi_model WHERE aktif = 1"
        )
    ).all():
        import json as _json

        m = _json.loads(b.metrik) if isinstance(b.metrik, str) else (b.metrik or {})
        auc = m.get("auc")
        anggaran = m.get("pada_anggaran", {}).get("300", {})
        potongan.append(
            Potongan(
                id=f"model:{b.versi}",
                judul=f"Kinerja model kerentanan {b.nama} {b.versi}",
                isi=(
                    f"Algoritma: {b.algoritma}. Dilatih pada {b.jumlah_baris_latih:,} baris "
                    f"dengan {b.jumlah_fitur} fitur. "
                    f"AUC pada gelombang penguji: {auc}. "
                    f"Pada anggaran verifikasi 300 keluarga, presisi "
                    f"{round(anggaran.get('presisi', 0) * 100, 1)} persen, yakni "
                    f"{anggaran.get('pengganda', 0)} kali lebih baik daripada memeriksa acak. "
                    f"{b.catatan or ''}"
                ).replace(",", "."),
                jenis="model",
                sumber="Catatan versi model NADI",
            )
        )

    potongan.extend(_potongan_agregat(sesi, g))
    potongan.extend(_potongan_tetap())
    logger.info("Basis pengetahuan copilot: %d potongan.", len(potongan))
    return potongan


def _potongan_agregat(sesi: Session, g: int) -> list[Potongan]:
    """Angka pokok tingkat kabupaten.

    Sebelum potongan ini ada, basis pengetahuan hanya memuat rincian - program,
    faktor risiko, statistik per kecamatan - tanpa satu pun angka menyeluruh.
    Akibatnya pertanyaan paling wajar seorang kepala dinas, "berapa keluarga
    yang belum tersentuh bantuan", dijawab dengan "keterangan belum tersedia",
    padahal sistem menghitung angka itu pada setiap layar ringkasan.

    Angka di bawah diambil dari kueri yang sama dengan yang menyusun Executive
    Command Center, sehingga jawaban copilot dan angka pada layar tidak mungkin
    berselisih.
    """
    potongan: list[Potongan] = []

    b = sesi.execute(
        text(
            """
            SELECT COUNT(*)                                                  AS keluarga,
                   SUM(s.jumlah_anggota)                                     AS jiwa,
                   SUM(s.status_miskin)                                      AS miskin,
                   SUM(s.status_miskin * s.jumlah_anggota)                   AS jiwa_miskin,
                   SUM(CASE WHEN s.status_miskin = 0 AND s.rasio_garis_kemiskinan < 1.5
                            THEN 1 ELSE 0 END)                               AS rentan,
                   SUM(CASE WHEN s.jumlah_program_diterima = 0 THEN 1 ELSE 0 END) AS tanpa_bantuan,
                   SUM(CASE WHEN s.jumlah_program_diterima = 0 AND s.status_miskin = 1
                            THEN 1 ELSE 0 END)                               AS miskin_tanpa_bantuan,
                   SUM(s.nilai_bantuan_bulanan)                              AS bantuan_bulanan
            FROM snapshot_keluarga s WHERE s.gelombang = :g
            """
        ),
        {"g": g},
    ).one()

    risiko = {
        r.kategori: int(r.n)
        for r in sesi.execute(
            text("SELECT kategori, COUNT(*) AS n FROM skor_kerentanan WHERE gelombang = :g GROUP BY kategori"),
            {"g": g},
        ).all()
    }
    tinggi = risiko.get("tinggi", 0) + risiko.get("sangat_tinggi", 0)

    memburuk = sesi.execute(
        text(
            "SELECT COUNT(*) FROM skor_kerentanan "
            "WHERE gelombang = :g AND perubahan_dari_sebelumnya >= 12"
        ),
        {"g": g},
    ).scalar() or 0

    tinggi_tanpa_bantuan = sesi.execute(
        text(
            """
            SELECT COUNT(*) FROM skor_kerentanan sk
            JOIN snapshot_keluarga s
              ON s.keluarga_id = sk.keluarga_id AND s.gelombang = sk.gelombang
            WHERE sk.gelombang = :g
              AND sk.kategori IN ('tinggi', 'sangat_tinggi')
              AND s.jumlah_program_diterima = 0
            """
        ),
        {"g": g},
    ).scalar() or 0

    potongan.append(
        Potongan(
            id="agregat:kabupaten",
            judul="Angka pokok Kabupaten Pringsewu pada sistem NADI",
            isi=(
                f"Cakupan sistem: {int(b.keluarga or 0):,} keluarga, {int(b.jiwa or 0):,} jiwa. "
                f"Keluarga miskin {int(b.miskin or 0):,} ({int(b.jiwa_miskin or 0):,} jiwa). "
                f"Keluarga rentan - belum miskin namun pengeluarannya di bawah satu setengah kali "
                f"garis kemiskinan - berjumlah {int(b.rentan or 0):,}. "
                f"Keluarga berisiko tinggi dan sangat tinggi: {tinggi:,}. "
                f"Keluarga yang belum menerima program apa pun: {int(b.tanpa_bantuan or 0):,}, "
                f"di antaranya {int(b.miskin_tanpa_bantuan or 0):,} tergolong miskin dan "
                f"{tinggi_tanpa_bantuan:,} berisiko tinggi atau sangat tinggi. "
                f"Keluarga yang skor kerentanannya memburuk dua belas poin atau lebih sejak "
                f"pemutakhiran sebelumnya: {int(memburuk or 0):,}. "
                f"Nilai bantuan yang tersalurkan Rp{float(b.bantuan_bulanan or 0):,.0f} per bulan. "
                f"Angka-angka ini berlaku untuk gelombang {g}, yang terkini."
            ).replace(",", "."),
            jenis="agregat",
            sumber=f"Ringkasan kabupaten NADI, gelombang {g}",
        )
    )

    kasus = sesi.execute(
        text("SELECT jenis, COUNT(*) AS n FROM kasus WHERE gelombang = :g GROUP BY jenis ORDER BY n DESC"),
        {"g": g},
    ).all()
    if kasus:
        from nadi.db.enums import JenisAnomali

        def _label(k: str) -> str:
            try:
                return JenisAnomali(k).label
            except ValueError:
                return k.replace("_", " ")

        rincian = "; ".join(f"{_label(k.jenis)}: {int(k.n):,}".replace(",", ".") for k in kasus)
        potongan.append(
            Potongan(
                id="agregat:antrean",
                judul="Antrean kasus yang menunggu verifikasi",
                isi=(
                    f"Total {sum(int(k.n) for k in kasus):,} kasus pada gelombang {g}. "
                    f"Rinciannya menurut jenis - {rincian}. "
                    "Setiap kasus adalah usulan pemeriksaan, bukan tuduhan dan bukan keputusan. "
                    "Petugas verifikasi yang menentukan kesimpulannya di lapangan."
                ).replace(",", "."),
                jenis="agregat",
                sumber=f"Antrean kasus NADI, gelombang {g}",
            )
        )

    tren = sesi.execute(
        text(
            """
            SELECT gelombang, MIN(tanggal_kondisi) AS tanggal,
                   SUM(status_miskin * jumlah_anggota) AS jiwa_miskin,
                   SUM(jumlah_anggota) AS jiwa
            FROM snapshot_keluarga GROUP BY gelombang ORDER BY gelombang
            """
        )
    ).all()
    if len(tren) > 1:
        titik = ", ".join(
            f"{r.tanggal} sebesar {round(int(r.jiwa_miskin or 0) / max(1, int(r.jiwa or 1)) * 100, 2)} persen"
            for r in tren
        )
        potongan.append(
            Potongan(
                id="agregat:tren",
                judul="Tren kemiskinan antarwaktu pada cakupan sistem",
                isi=(
                    f"Persentase penduduk miskin dalam cakupan sistem menurut gelombang: {titik}. "
                    "Persentase ini dihitung terhadap cakupan desil 1 sampai 5, bukan terhadap "
                    "seluruh penduduk kabupaten, sehingga angkanya lebih tinggi daripada angka "
                    "resmi BPS meski jumlah orangnya sama."
                ),
                jenis="agregat",
                sumber="Tren gelombang NADI",
            )
        )

    return potongan


def _potongan_tetap() -> list[Potongan]:
    """Penjelasan istilah dan batas sistem yang tidak berasal dari basis data."""
    from nadi.synth.parameter import ACUAN

    return [
        Potongan(
            id="istilah:desil",
            judul="Apa itu desil kesejahteraan",
            isi=(
                "Desil kesejahteraan adalah pemeringkatan keluarga menurut tingkat "
                "kesejahteraan relatif, dibagi sepuluh kelompok yang masing-masing "
                "memuat sekitar sepuluh persen keluarga. Desil 1 adalah sepuluh persen "
                "termiskin. Desil ini BUKAN hasil pengukuran pengeluaran langsung, "
                "melainkan keluaran proxy means test - sebuah penduga yang memperkirakan "
                "kesejahteraan dari penanda tak langsung seperti kondisi rumah, aset, "
                "dan pendidikan. Kajian lintas negara mencatat penduga semacam ini hanya "
                "menjelaskan sekitar empat puluh sampai enam puluh persen keragaman "
                "kesejahteraan antar-keluarga."
            ),
            jenis="istilah",
        ),
        Potongan(
            id="istilah:garis_kemiskinan",
            judul="Garis kemiskinan dan garis kerentanan Kabupaten Pringsewu",
            isi=(
                f"Garis kemiskinan Kabupaten Pringsewu sebesar Rp{ACUAN.garis_kemiskinan:,.0f} "
                "per kapita per bulan menurut BPS tahun 2024. Keluarga dengan pengeluaran "
                "di bawah angka itu tergolong miskin. Garis kerentanan sebesar "
                f"Rp{ACUAN.garis_kerentanan:,.0f}, yakni satu setengah kali garis kemiskinan, "
                "mengikuti klasifikasi Bank Dunia - kelompok antara keduanya belum tercatat "
                "miskin namun cukup satu guncangan untuk jatuh. Angka garis kerentanan "
                "adalah nilai TURUNAN, bukan statistik resmi BPS. "
                f"Angka kemiskinan kabupaten: {ACUAN.persen_miskin_2023} persen pada 2023, "
                f"{ACUAN.persen_miskin_2024} persen pada 2024, dan "
                f"{ACUAN.persen_miskin_2025} persen pada 2025."
            ).replace(",", "."),
            jenis="istilah",
            sumber="BPS Kabupaten Pringsewu",
        ),
        Potongan(
            id="istilah:skor",
            judul="Apa arti NADI Vulnerability Score",
            isi=(
                "Skor kerentanan bernilai nol sampai seratus dan menyatakan peluang "
                "terkalibrasi sebuah keluarga berada di bawah garis kemiskinan pada "
                "pemutakhiran data berikutnya. Skor 70 berarti dari seratus keluarga "
                "berskor serupa, sekitar tujuh puluh benar-benar berada di bawah garis "
                "kemiskinan pada periode berikutnya. Skor adalah perkiraan berpeluang, "
                "bukan pernyataan tentang keadaan seseorang, dan tidak pernah menjadi "
                "dasar penghentian bantuan."
            ),
            jenis="istilah",
        ),
        Potongan(
            id="batas:sistem",
            judul="Apa yang tidak dilakukan NADI",
            isi=(
                "NADI tidak menetapkan penerima bantuan, tidak menghentikan bantuan "
                "siapa pun, dan tidak dipakai mendeteksi kecurangan. Keluarannya berupa "
                "antrean prioritas pemeriksaan. Penetapan penerima tetap melalui "
                "musyawarah pekon dan keputusan pejabat berwenang. Sistem ini juga tidak "
                "menyimpan nama, nomor induk kependudukan, maupun alamat - identitas "
                "keluarga hanya berupa kode semu yang tidak dapat dibalik. Seluruh data "
                "pada sistem ini bersifat sintetis dan tidak merujuk keluarga nyata mana pun."
            ),
            jenis="batas",
        ),
    ]


# ===========================================================================
# Pengambilan
# ===========================================================================
def _tokenkan(teks: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", teks.lower())


class PengambilPotongan:
    """Pengambil potongan pengetahuan berbasis BM25.

    BM25 dipilih ketimbang penyandian semantik dengan alasan praktis. Basis
    pengetahuan ini berukuran ratusan potongan, bukan jutaan, dan pertanyaan
    pengguna hampir selalu memuat kata kunci yang sama dengan isinya - nama
    program, nama kecamatan, istilah baku. Penyandian semantik akan menambah
    ratusan megabita ketergantungan pada peladen demi perbaikan yang tidak
    terasa pada skala ini.
    """

    def __init__(self, potongan: list[Potongan]) -> None:
        self.potongan = potongan
        self._korpus = [_tokenkan(p.teks_cari()) for p in potongan]
        self._bm25 = BM25Okapi(self._korpus) if self._korpus else None

    def ambil(self, pertanyaan: str, jumlah: int = JUMLAH_POTONGAN) -> list[tuple[Potongan, float]]:
        if not self._bm25:
            return []
        nilai = self._bm25.get_scores(_tokenkan(pertanyaan))
        urut = sorted(range(len(nilai)), key=lambda i: -nilai[i])[:jumlah]
        return [(self.potongan[i], float(nilai[i])) for i in urut if nilai[i] > 0]


# ===========================================================================
# Copilot
# ===========================================================================
class Copilot:
    """Menjawab pertanyaan dari basis pengetahuan yang terkendali."""

    def __init__(self, potongan: list[Potongan]) -> None:
        self.pengambil = PengambilPotongan(potongan)

    async def jawab(self, pertanyaan: str, *, peran_pengguna: str = "") -> JawabanCopilot:
        mulai = time.perf_counter()

        # Masukan pengguna diredaksi, bukan ditolak. Petugas yang terlanjur
        # mengetikkan nomor induk kependudukan pada kolom tanya-jawab tidak
        # seharusnya kehilangan pertanyaannya - nilainya cukup dihapus.
        bersih = redaksi_teks(pertanyaan.strip()[:BATAS_PERTANYAAN])
        diredaksi = bersih != pertanyaan.strip()[:BATAS_PERTANYAAN]

        diambil = self.pengambil.ambil(bersih)
        if not diambil:
            return JawabanCopilot(
                jawaban=(
                    "Maaf, saya tidak menemukan keterangan yang relevan pada basis "
                    "pengetahuan sistem. Coba sebutkan nama program, nama kecamatan, "
                    "atau istilah yang lebih khusus. Untuk hal di luar cakupan sistem "
                    "ini, silakan hubungi Dinas Sosial atau Bappeda Kabupaten Pringsewu."
                ),
                pertanyaan_diredaksi=diredaksi,
                durasi_ms=int((time.perf_counter() - mulai) * 1000),
            )

        konteks = self._susun_konteks(diambil)
        sumber = [
            {"id": p.id, "judul": p.judul, "jenis": p.jenis, "sumber": p.sumber, "nilai": round(n, 2)}
            for p, n in diambil
        ]

        muatan = {"pertanyaan": bersih, "konteks": konteks}
        pastikan_bersih(muatan)
        logger.info("Copilot: %s", ringkas_untuk_log(muatan))

        pesan = [
            PesanChat(Peran.SISTEM, INSTRUKSI_SISTEM),
            PesanChat(
                Peran.PENGGUNA,
                f"POTONGAN PENGETAHUAN:\n\n{konteks}\n\n"
                f"PERTANYAAN PENGGUNA{f' (peran: {peran_pengguna})' if peran_pengguna else ''}:\n{bersih}",
            ),
        ]

        try:
            hasil: HasilLLM = await dapatkan_penyedia().chat(pesan)
        except LLMTidakTersedia as exc:
            logger.warning("Layanan AI tidak tersedia: %s", exc)
            hasil = HasilLLM(teks="", model="templat-luring", penyedia="templat-luring",
                             durasi_ms=0, dari_cadangan=True, catatan=str(exc))

        if hasil.dari_cadangan or not hasil.teks:
            jawaban = self._jawaban_templat(bersih, diambil)
            catatan = [
                "Layanan model bahasa tidak tersedia, sehingga jawaban disusun dari "
                "templat atas potongan pengetahuan yang sama. Seluruh angka yang "
                "disampaikan identik; yang berbeda hanya keluwesan kalimatnya."
            ]
            if hasil.catatan:
                catatan.append(hasil.catatan)
            return JawabanCopilot(
                jawaban=jawaban,
                potongan_dipakai=sumber,
                dari_cadangan=True,
                model=hasil.model,
                durasi_ms=int((time.perf_counter() - mulai) * 1000),
                pertanyaan_diredaksi=diredaksi,
                catatan=catatan,
            )

        return JawabanCopilot(
            jawaban=hasil.teks,
            potongan_dipakai=sumber,
            dari_cadangan=False,
            model=hasil.model,
            durasi_ms=int((time.perf_counter() - mulai) * 1000),
            pertanyaan_diredaksi=diredaksi,
        )

    # ------------------------------------------------------------------
    @staticmethod
    def _susun_konteks(diambil: list[tuple[Potongan, float]]) -> str:
        bagian = []
        for i, (p, _) in enumerate(diambil, 1):
            asal = f" [sumber: {p.sumber}]" if p.sumber else ""
            bagian.append(f"[{i}] {p.judul}{asal}\n{p.isi}")
        return "\n\n".join(bagian)

    @staticmethod
    def _jawaban_templat(pertanyaan: str, diambil: list[tuple[Potongan, float]]) -> str:
        """Susun jawaban tanpa model bahasa.

        Bukan jawaban yang luwes, namun jujur dan lengkap: seluruh keterangan
        yang relevan disajikan apa adanya, disertai sumbernya.
        """
        baris = [
            "Berikut keterangan yang tersedia pada basis pengetahuan sistem terkait "
            "pertanyaan Anda.",
            "",
        ]
        for i, (p, _) in enumerate(diambil[:4], 1):
            baris.append(f"{i}. {p.judul}")
            baris.append(f"   {p.isi.strip()}")
            if p.sumber:
                baris.append(f"   Sumber: {p.sumber}")
            baris.append("")
        baris.append(
            "Keterangan di atas disajikan apa adanya dari basis pengetahuan. Untuk hal "
            "yang belum terjawab, silakan hubungi dinas pengampu program terkait."
        )
        return "\n".join(baris)


# ---------------------------------------------------------------------------
_copilot: Copilot | None = None


def dapatkan_copilot(sesi: Session, *, muat_ulang: bool = False) -> Copilot:
    """Kembalikan copilot bersama, membangun basis pengetahuannya sekali saja."""
    global _copilot
    if _copilot is None or muat_ulang:
        _copilot = Copilot(susun_basis_pengetahuan(sesi))
    return _copilot


__all__ = [
    "Copilot",
    "JawabanCopilot",
    "PengambilPotongan",
    "Potongan",
    "dapatkan_copilot",
    "susun_basis_pengetahuan",
]
