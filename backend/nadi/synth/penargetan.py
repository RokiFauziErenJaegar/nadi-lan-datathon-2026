"""Simulasi penargetan program bantuan, lengkap dengan kesalahannya.

Bagian ini sengaja dibuat tidak sempurna, dan itu justru intinya. Sistem yang
dibangun untuk menemukan ketidaksesuaian sasaran mustahil diuji pada data yang
tidak memiliki ketidaksesuaian. Bila penargetan di sini berjalan sempurna,
antrean verifikasi NADI akan kosong pada setiap demonstrasi, dan tidak ada yang
dapat dibuktikan.

Empat sumber kesalahan ditirukan, keempatnya berasal dari cara kerja yang
sesungguhnya di lapangan:

**Data yang tertinggal.** Penetapan penerima memakai desil kesejahteraan dari
pemutakhiran sebelumnya, bukan keadaan hari ini. Keluarga yang baru jatuh
miskin belum terbaca, dan keluarga yang sudah membaik masih tercatat miskin.

**Kelamban an kepesertaan.** Sekali masuk daftar penerima, sebuah keluarga
cenderung tetap di sana. Mengeluarkan penerima menuntut verifikasi, keberanian
administratif, dan seringkali menghadapi keberatan - jauh lebih mudah
membiarkannya.

**Keterbatasan kuota.** Jumlah penerima dibatasi anggaran, sehingga sebagian
keluarga yang memenuhi syarat tetap tidak terjangkau. Siapa yang terpilih di
antara yang sama-sama layak sering ditentukan hal yang tidak tercatat: kedekatan
dengan aparat pekon, kehadiran pada musyawarah, atau sekadar keberuntungan.

**Hambatan administratif.** Keluarga tanpa dokumen kependudukan yang sah tidak
dapat ditetapkan sebagai penerima, sebaik apa pun penargetannya.

Besaran kesalahan mengikuti kisaran yang dilaporkan kajian evaluasi penargetan
bantuan sosial di Indonesia, dan dapat disetel pada :mod:`nadi.synth.parameter`.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from nadi.synth.parameter import PARAMETER


@dataclass(frozen=True)
class ProgramSintetis:
    """Ketentuan satu program pada simulasi penargetan.

    Hanya program berskala besar yang ditirukan di sini. Program kecil dan
    program berbasis lokasi tidak ikut, sebab yang diperlukan adalah pola
    kepesertaan yang wajar - bukan replika seluruh katalog. Katalog lengkap
    tetap dipakai oleh mesin rekomendasi, dan justru perbedaan antara keduanya
    yang menjadi bahan temuan sistem.
    """

    kode: str
    desil_maks: int
    cakupan: float
    """Bagian keluarga memenuhi syarat yang benar-benar menerima. Nilai di bawah
    satu mencerminkan keterbatasan kuota."""

    nilai_bulanan: float
    """Nilai manfaat per keluarga per bulan, dalam rupiah."""

    per_kapita: bool = False
    """Bila benar, nilai manfaat dikalikan jumlah anggota keluarga."""

    syarat: str | None = None
    """Syarat tambahan di luar desil: ``anak_sekolah``, ``balita``, ``lansia``,
    ``disabilitas``, atau ``tanpa_jkn``."""


#: Program berskala besar yang ditirukan. Nilai manfaat mengikuti katalog pada
#: ``data/seed/program.json``, dibulatkan ke besaran bulanan.
PROGRAM_UTAMA: tuple[ProgramSintetis, ...] = (
    ProgramSintetis("PKH", desil_maks=2, cakupan=0.62, nilai_bulanan=250_000, syarat="komponen"),
    ProgramSintetis("SEMBAKO", desil_maks=3, cakupan=0.58, nilai_bulanan=200_000),
    # Bantuan iuran jaminan kesehatan tidak menuntut keluarga belum berjaminan.
    # Program ini justru jalur utama keluarga miskin memperoleh jaminan, dan
    # kepesertaannya menentukan cakupan jaminan keluarga tersebut.
    ProgramSintetis("PBI-JKN", desil_maks=4, cakupan=0.58, nilai_bulanan=42_000, per_kapita=True),
    ProgramSintetis("PIP", desil_maks=4, cakupan=0.44, nilai_bulanan=62_500, syarat="anak_sekolah"),
    ProgramSintetis("BLT-DD", desil_maks=2, cakupan=0.18, nilai_bulanan=75_000),
    ProgramSintetis("BAPANG", desil_maks=3, cakupan=0.52, nilai_bulanan=120_000),
)

#: Bagian nilai bantuan yang benar-benar terbaca sebagai tambahan pengeluaran.
#: Tidak seluruhnya, sebab sebagian dipakai melunasi utang, ditabung, atau
#: menggantikan pengeluaran yang sebelumnya ditanggung kerabat. Angka ini
#: menentukan seberapa besar perbaikan yang tampak pada pemantauan hasil, dan
#: sengaja dibuat wajar - bukan mengesankan bantuan menyelesaikan segalanya.
DAYA_SERAP_BANTUAN = 0.72


def _memenuhi_syarat_tambahan(
    syarat: str | None,
    *,
    jumlah_anak_sekolah: np.ndarray,
    jumlah_balita: np.ndarray,
    jumlah_lansia: np.ndarray,
    jumlah_disabilitas: np.ndarray,
    jumlah_ibu_hamil: np.ndarray,
    cakupan_jkn: np.ndarray,
) -> np.ndarray:
    """Periksa syarat di luar desil kesejahteraan."""
    n = len(jumlah_anak_sekolah)
    if syarat is None:
        return np.ones(n, dtype=bool)
    if syarat == "anak_sekolah":
        return jumlah_anak_sekolah > 0
    if syarat == "balita":
        return jumlah_balita > 0
    if syarat == "lansia":
        return jumlah_lansia > 0
    if syarat == "disabilitas":
        return jumlah_disabilitas > 0
    if syarat == "tanpa_jkn":
        return cakupan_jkn < 1.0
    if syarat == "komponen":
        # PKH menuntut adanya salah satu komponen kesehatan, pendidikan, atau
        # kesejahteraan sosial. Keluarga miskin tanpa satu pun komponen - dua
        # orang dewasa usia produktif tanpa anak - memang tidak layak PKH,
        # walaupun miskin. Kekhususan ini kerap disalahpahami sebagai kesalahan
        # sasaran, padahal justru sesuai ketentuan.
        return (
            (jumlah_anak_sekolah > 0)
            | (jumlah_balita > 0)
            | (jumlah_lansia > 0)
            | (jumlah_disabilitas > 0)
            | (jumlah_ibu_hamil > 0)
        )
    return np.ones(n, dtype=bool)


def tentukan_kepesertaan(
    *,
    desil_tercatat: np.ndarray,
    kepesertaan_sebelumnya: dict[str, np.ndarray] | None,
    jumlah_anggota: np.ndarray,
    jumlah_anak_sekolah: np.ndarray,
    jumlah_balita: np.ndarray,
    jumlah_lansia: np.ndarray,
    jumlah_disabilitas: np.ndarray,
    jumlah_ibu_hamil: np.ndarray,
    cakupan_jkn: np.ndarray,
    ada_masalah_dokumen: np.ndarray,
    rng: np.random.Generator,
) -> tuple[dict[str, np.ndarray], np.ndarray]:
    """Tentukan program apa saja yang diterima tiap keluarga pada satu gelombang.

    Args:
        desil_tercatat: desil kesejahteraan MENURUT CATATAN, yang tertinggal
            beberapa gelombang dari keadaan sesungguhnya. Inilah sumber utama
            ketidaksesuaian sasaran, dan sengaja tidak diganti dengan desil
            terkini.
        kepesertaan_sebelumnya: kepesertaan pada gelombang sebelumnya, atau
            ``None`` pada gelombang pertama.

    Returns:
        Tiga hal: peta kode program ke penanda kepesertaan, larik nilai bantuan
        bulanan per keluarga, dan peta kode program ke penanda kelayakan
        menurut ketentuan. Kelayakan dikembalikan terpisah agar ketepatan
        sasaran dapat diukur terhadap ketentuan program, bukan hanya terhadap
        garis kemiskinan - dua ukuran yang menjawab pertanyaan berbeda dan
        kerap tertukar.
    """
    n = len(desil_tercatat)
    hasil: dict[str, np.ndarray] = {}
    kelayakan: dict[str, np.ndarray] = {}
    nilai_total = np.zeros(n, dtype=np.float64)

    for prog in PROGRAM_UTAMA:
        layak_desil = desil_tercatat <= prog.desil_maks
        layak_syarat = _memenuhi_syarat_tambahan(
            prog.syarat,
            jumlah_anak_sekolah=jumlah_anak_sekolah,
            jumlah_balita=jumlah_balita,
            jumlah_lansia=jumlah_lansia,
            jumlah_disabilitas=jumlah_disabilitas,
            jumlah_ibu_hamil=jumlah_ibu_hamil,
            cakupan_jkn=cakupan_jkn,
        )
        layak = layak_desil & layak_syarat

        # Hambatan administratif: tanpa dokumen kependudukan yang sah, keluarga
        # tidak dapat ditetapkan sebagai penerima sama sekali.
        layak = layak & ~ada_masalah_dokumen

        sebelumnya = (
            kepesertaan_sebelumnya.get(prog.kode)
            if kepesertaan_sebelumnya is not None
            else None
        )

        if sebelumnya is None:
            # Gelombang pertama: penetapan murni dari kelayakan dan kuota.
            terima = layak & (rng.random(n) < prog.cakupan)
        else:
            # --- Yang sudah menerima ---
            # Kelambanan bekerja dua arah. Penerima yang masih layak hampir
            # selalu bertahan. Penerima yang sudah tidak layak pun sebagian
            # besar bertahan - dan merekalah kesalahan inklusi yang menjadi
            # sasaran penandaan sistem.
            bertahan_layak = sebelumnya & layak & (rng.random(n) < PARAMETER.kelambanan_kepesertaan)
            bertahan_tak_layak = (
                sebelumnya & ~layak & (rng.random(n) < 1.0 - PARAMETER.galat_inklusi)
            )

            # --- Yang baru masuk ---
            # Sisa kuota setelah penerima lama bertahan. Keluarga yang baru
            # layak harus mengantre, dan sebagian tidak kebagian - inilah
            # kesalahan eksklusi.
            baru_layak = layak & ~sebelumnya
            peluang_masuk = prog.cakupan * (1.0 - PARAMETER.galat_eksklusi)
            masuk_baru = baru_layak & (rng.random(n) < peluang_masuk)

            terima = bertahan_layak | bertahan_tak_layak | masuk_baru

        hasil[prog.kode] = terima
        kelayakan[prog.kode] = layak

        nilai = np.where(
            terima,
            prog.nilai_bulanan * (jumlah_anggota if prog.per_kapita else 1),
            0.0,
        )
        nilai_total += nilai

    return hasil, nilai_total, kelayakan


def ringkas_kepesertaan(kepesertaan: dict[str, np.ndarray]) -> np.ndarray:
    """Hitung banyaknya program yang diterima tiap keluarga."""
    if not kepesertaan:
        return np.zeros(0, dtype=np.int16)
    tumpuk = np.vstack([v.astype(np.int16) for v in kepesertaan.values()])
    return tumpuk.sum(axis=0).astype(np.int16)


def ukur_ketepatan_sasaran(
    kepesertaan: dict[str, np.ndarray],
    status_miskin: np.ndarray,
    kelayakan: dict[str, np.ndarray] | None = None,
) -> dict[str, dict[str, float]]:
    """Ukur ketepatan sasaran setiap program dari dua sudut sekaligus.

    Dua ukuran dilaporkan berdampingan, dan membedakannya penting.

    **Terhadap garis kemiskinan.** Berapa bagian keluarga miskin yang tidak
    terjangkau, dan berapa bagian penerima yang sebenarnya tidak miskin. Ukuran
    ini kerap dikutip untuk mengkritik penargetan bantuan, dan angkanya memang
    selalu tampak buruk - tetapi sebagian besar bukan karena penargetannya
    salah. Program bantuan menyasar desil terbawah pemeringkatan kesejahteraan,
    yang mencakup jauh lebih banyak keluarga daripada yang berada di bawah
    garis kemiskinan. Penerima yang "tidak miskin" itu umumnya keluarga rentan
    yang memang dimaksudkan tercakup.

    **Terhadap ketentuan program.** Berapa bagian keluarga yang memenuhi syarat
    namun tidak menerima, dan berapa bagian penerima yang tidak lagi memenuhi
    syarat. Inilah ukuran yang benar-benar menunjukkan kualitas pelaksanaan,
    dan inilah yang menjadi sasaran penandaan kasus oleh NADI.

    Menyajikan hanya salah satunya akan menyesatkan pembacanya ke arah yang
    berlawanan - yang pertama membuat program tampak kacau, yang kedua membuat
    program tampak rapi.
    """
    hasil: dict[str, dict[str, float]] = {}
    n = len(status_miskin)
    n_miskin = max(1, int(status_miskin.sum()))

    for kode, terima in kepesertaan.items():
        n_terima = max(1, int(terima.sum()))
        butir = {
            "cakupan": float(terima.sum() / n),
            "cakupan_pada_miskin": float((terima & status_miskin).sum() / n_miskin),
            "eksklusi_thd_garis_kemiskinan": float((~terima & status_miskin).sum() / n_miskin),
            "inklusi_thd_garis_kemiskinan": float((terima & ~status_miskin).sum() / n_terima),
        }

        if kelayakan and kode in kelayakan:
            layak = kelayakan[kode]
            n_layak = max(1, int(layak.sum()))
            butir.update(
                {
                    "proporsi_layak": float(layak.sum() / n),
                    "cakupan_pada_yang_layak": float((terima & layak).sum() / n_layak),
                    "eksklusi_thd_ketentuan": float((~terima & layak).sum() / n_layak),
                    "inklusi_thd_ketentuan": float((terima & ~layak).sum() / n_terima),
                }
            )

        hasil[kode] = butir
    return hasil


__all__ = [
    "DAYA_SERAP_BANTUAN",
    "PROGRAM_UTAMA",
    "ProgramSintetis",
    "ringkas_kepesertaan",
    "tentukan_kepesertaan",
    "ukur_ketepatan_sasaran",
]
