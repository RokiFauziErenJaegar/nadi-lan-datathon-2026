"""Lapisan penyedia model bahasa.

Aplikasi tidak pernah memanggil vendor tertentu secara langsung. Seluruh
pemanggilan melewati antarmuka :class:`PenyediaLLM`, sehingga penyedia dapat
diganti lewat berkas ``.env`` tanpa menyentuh satu baris pun kode fitur.

Tiga hal yang dijaga modul ini:

**Privasi.** Setiap muatan melewati :func:`nadi.security.pii.pastikan_bersih`
tepat sebelum dikirim. Bila lolos pemeriksaan struktural namun tetap
mengandung pengenal pribadi, permintaan dibatalkan - bukan disamarkan diam-diam.

**Ketahanan demo.** Bila kunci API kosong, jaringan putus, kuota habis, atau
penyedia sedang bermasalah, sistem beralih ke :class:`PenyediaTemplat` yang
menyusun jawaban dari data terstruktur tanpa jaringan sama sekali. Presentasi
di hadapan dewan juri tidak boleh bergantung pada koneksi internet ruang rapat.

**Kejujuran.** Setiap hasil menandai dirinya sendiri: model apa yang menjawab,
berapa lama, dan apakah jawaban berasal dari cadangan luring. Antarmuka
menampilkan penanda tersebut kepada pengguna.
"""

from __future__ import annotations

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Sequence

import httpx

from nadi.ai.dialek import koreksi_muatan, siapkan_muatan
from nadi.config import settings
from nadi.security.pii import pastikan_bersih, ringkas_untuk_log

logger = logging.getLogger("nadi.ai")


class Peran(str, Enum):
    SISTEM = "system"
    PENGGUNA = "user"
    ASISTEN = "assistant"


@dataclass(frozen=True)
class PesanChat:
    peran: Peran
    isi: str

    def ke_dict(self) -> dict[str, str]:
        return {"role": self.peran.value, "content": self.isi}


@dataclass
class HasilLLM:
    """Hasil satu pemanggilan model bahasa, lengkap dengan asal-usulnya."""

    teks: str
    model: str
    penyedia: str
    durasi_ms: int
    token_masukan: int | None = None
    token_keluaran: int | None = None
    dari_cadangan: bool = False
    catatan: str | None = None

    @property
    def ringkasan_sumber(self) -> str:
        if self.dari_cadangan:
            return f"Mode luring ({self.penyedia}) - {self.catatan or 'layanan AI tidak tersedia'}"
        return f"{self.model} melalui {self.penyedia} - {self.durasi_ms} ms"


class LLMTidakTersedia(RuntimeError):
    """Diangkat bila penyedia gagal menjawab setelah seluruh percobaan ulang."""


# ---------------------------------------------------------------------------
# Antarmuka
# ---------------------------------------------------------------------------
class PenyediaLLM(ABC):
    nama: str = "abstrak"

    @abstractmethod
    async def chat(
        self,
        pesan: Sequence[PesanChat],
        *,
        suhu: float | None = None,
        maks_token: int | None = None,
    ) -> HasilLLM:
        """Kirim percakapan dan kembalikan jawaban model."""

    async def periksa(self) -> dict[str, Any]:
        """Uji ketersediaan penyedia. Dipakai oleh titik akhir kesehatan."""
        return {"penyedia": self.nama, "tersedia": True}

    async def tutup(self) -> None:
        """Lepaskan sumber daya jaringan."""


# ---------------------------------------------------------------------------
# Pemutus arus sederhana
# ---------------------------------------------------------------------------
@dataclass
class PemutusArus:
    """Menghentikan permintaan ke penyedia yang sedang bermasalah.

    Setelah sejumlah kegagalan beruntun, seluruh permintaan langsung
    dialihkan ke cadangan luring selama masa pemulihan - jauh lebih baik
    daripada membuat pengguna menunggu batas waktu berulang kali saat demo.
    """

    ambang_kegagalan: int = 3
    masa_pemulihan_detik: float = 60.0
    _kegagalan: int = field(default=0, init=False)
    _terbuka_sampai: float = field(default=0.0, init=False)

    @property
    def terbuka(self) -> bool:
        return time.monotonic() < self._terbuka_sampai

    @property
    def sisa_detik(self) -> int:
        return max(0, int(self._terbuka_sampai - time.monotonic()))

    def catat_sukses(self) -> None:
        self._kegagalan = 0
        self._terbuka_sampai = 0.0

    def catat_gagal(self) -> None:
        self._kegagalan += 1
        if self._kegagalan >= self.ambang_kegagalan:
            self._terbuka_sampai = time.monotonic() + self.masa_pemulihan_detik
            logger.warning(
                "Pemutus arus layanan AI terbuka selama %.0f detik setelah %d kegagalan beruntun.",
                self.masa_pemulihan_detik,
                self._kegagalan,
            )


# ---------------------------------------------------------------------------
# Penerjemah galat penyedia
# ---------------------------------------------------------------------------
# Nomor status saja hampir tidak pernah cukup. OpenCode Zen, misalnya,
# menjawab 401 baik ketika kunci tidak terkirim sama sekali ("Missing API
# key.") maupun ketika kunci terkirim tetapi ditolak ("Invalid API key.").
# Keduanya menuntut perbaikan yang sama sekali berbeda, dan selisihnya hanya
# ada di badan tanggapan. Membuang badan itu berarti membiarkan pemakai
# menebak - persis keadaan yang paling mahal saat menyiapkan demo.

_SARAN_STATUS: dict[int, str] = {
    400: "Bentuk permintaan ditolak; paling sering nama model tidak dikenal. Periksa NADI_LLM_MODEL.",
    401: "Kunci API tidak diterima. Periksa NADI_LLM_API_KEY.",
    402: "Saldo atau kuota penyedia habis. Isi ulang kredit pada akun Anda.",
    403: "Kunci sah namun tidak berhak memakai model ini. Coba model lain.",
    404: "Alamat tidak ditemukan. Periksa NADI_LLM_BASE_URL - untuk OpenCode Zen harus berakhir '/zen/v1'.",
    413: "Permintaan terlalu besar. Turunkan NADI_LLM_MAX_TOKENS.",
    422: "Muatan ditolak penyedia. Periksa nama model dan parameter.",
}


# Kata kunci yang menandai persoalan tagihan, bukan persoalan kunci. Beberapa
# penyedia - OpenCode Zen di antaranya - menjawab 401 untuk keduanya, sehingga
# kode status saja menyesatkan: pemakai akan menghabiskan waktu memeriksa kunci
# yang sebenarnya sudah benar.
_PENANDA_TAGIHAN = (
    "payment method",
    "billing",
    "insufficient",
    "credit",
    "quota",
    "balance",
    "saldo",
)


# Sebagian penyedia memberi nama pada jenis galatnya. OpenCode Zen memakai
# "AuthError", "CreditsError", dan "ModelError" - ketiganya dikirim dengan
# kode 401 yang sama persis. Nama itu jauh lebih dapat diandalkan daripada
# mencocokkan kalimat, yang bisa berubah sewaktu-waktu.
_JENIS_KE_SARAN: dict[str, str] = {
    "autherror": "Kunci API ditolak penyedia. Periksa NADI_LLM_API_KEY.",
    "creditserror": (
        "Kunci API-nya sah; yang belum siap adalah tagihan atau saldo akun "
        "penyedia. Ikuti tautan pada pesan di atas, atau pakai model gratis."
    ),
    "modelerror": (
        "Nama model tidak dikenal penyedia - kunci belum sempat diperiksa. "
        "Periksa NADI_LLM_MODEL."
    ),
    "freeusagelimiterror": (
        "Batas pemakaian model gratis tercapai. Tunggu beberapa saat, atau "
        "pakai model lain."
    ),
}


def _jenis_galat(tanggapan: httpx.Response) -> str:
    """Ambil nama jenis galat dari tanggapan, bila penyedia menyebutkannya."""
    try:
        data = tanggapan.json()
    except ValueError:
        return ""
    if isinstance(data, dict):
        galat = data.get("error")
        if isinstance(galat, dict) and isinstance(galat.get("type"), str):
            return galat["type"].strip().lower()
        if isinstance(data.get("type"), str) and data.get("type") != "error":
            return data["type"].strip().lower()
    return ""


def _saran_galat(kode: int, pesan: str, jenis: str = "") -> str:
    """Pilih saran yang sesuai dengan isi galat, bukan sekadar kode statusnya."""
    if jenis and jenis in _JENIS_KE_SARAN:
        return _JENIS_KE_SARAN[jenis]
    rendah = pesan.lower()

    # Nama model yang keliru muncul dengan kode status yang berbeda-beda:
    # OpenAI menjawab 404, OpenCode Zen menjawab 401, sebagian lain 400.
    # Isinya yang menentukan, bukan nomornya - dan menyarankan pemakai
    # memeriksa alamat padahal yang salah nama model akan membuang waktunya.
    if "model" in rendah and any(
        k in rendah for k in ("does not exist", "not found", "not supported", "unknown", "tidak dikenal")
    ):
        return "Nama model tidak dikenal penyedia. Periksa NADI_LLM_MODEL."

    if any(k in rendah for k in _PENANDA_TAGIHAN):
        return (
            "Kunci API-nya sah; yang belum siap adalah tagihan atau saldo akun "
            "penyedia. Ikuti tautan pada pesan di atas, atau pakai model gratis "
            "untuk sementara."
        )
    return _SARAN_STATUS.get(
        kode, "Periksa NADI_LLM_API_KEY, NADI_LLM_MODEL, dan NADI_LLM_BASE_URL."
    )


def _pesan_penyedia(tanggapan: httpx.Response, batas: int = 400) -> str:
    """Ambil pesan galat apa adanya dari tanggapan penyedia.

    Bentuk badan galat berbeda-beda antarpenyedia. Fungsi ini menangani
    bentuk-bentuk yang lazim dan, bila tidak satu pun cocok, mengembalikan
    teks mentahnya - lebih baik menampilkan sesuatu yang berantakan daripada
    menyembunyikan satu-satunya petunjuk yang ada.

    Yang dikembalikan berasal dari penyedia, bukan dari basis data kita,
    sehingga tidak mungkin memuat data keluarga.
    """
    try:
        data = tanggapan.json()
    except ValueError:
        return tanggapan.text.strip()[:batas] or "(tanpa keterangan)"

    if isinstance(data, dict):
        galat = data.get("error")
        if isinstance(galat, dict):
            for kunci in ("message", "detail", "type"):
                nilai = galat.get(kunci)
                if isinstance(nilai, str) and nilai.strip():
                    return nilai.strip()[:batas]
        if isinstance(galat, str) and galat.strip():
            return galat.strip()[:batas]
        for kunci in ("message", "detail", "msg", "error_description"):
            nilai = data.get(kunci)
            if isinstance(nilai, str) and nilai.strip():
                return nilai.strip()[:batas]

    return str(data)[:batas] or "(tanpa keterangan)"


# ---------------------------------------------------------------------------
# Penyedia kompatibel-OpenAI (OpenCode Zen, OpenRouter, OpenAI, dan sejenisnya)
# ---------------------------------------------------------------------------
class PenyediaKompatibelOpenAI(PenyediaLLM):
    """Klien untuk titik akhir bergaya ``/chat/completions``.

    Bekerja dengan OpenCode Zen, OpenRouter, OpenAI, Groq, Together, dan
    layanan lain yang mengikuti bentuk permintaan yang sama.
    """

    nama = "kompatibel-openai"

    _STATUS_LAYAK_ULANG = frozenset({408, 409, 425, 429, 500, 502, 503, 504})

    def __init__(
        self,
        base_url: str,
        api_key: str,
        model: str,
        *,
        timeout: float = 60.0,
        maks_percobaan: int = 3,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.maks_percobaan = maks_percobaan
        self._pemutus = PemutusArus()
        self._klien = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=httpx.Timeout(timeout, connect=10.0),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                # Beberapa gerbang memakai tajuk ini untuk atribusi aplikasi.
                "HTTP-Referer": "https://github.com/nadi-pringsewu",
                "X-Title": "NADI - Navigasi AI Data Intervensi",
            },
        )

    async def chat(
        self,
        pesan: Sequence[PesanChat],
        *,
        suhu: float | None = None,
        maks_token: int | None = None,
    ) -> HasilLLM:
        if self._pemutus.terbuka:
            raise LLMTidakTersedia(
                f"Pemutus arus masih terbuka, coba lagi dalam {self._pemutus.sisa_detik} detik."
            )

        muatan: dict[str, Any] = siapkan_muatan(
            model=self.model,
            pesan=[p.ke_dict() for p in pesan],
            maks_token=settings.llm_max_tokens if maks_token is None else maks_token,
            suhu=settings.llm_temperature if suhu is None else suhu,
        )

        # --- Penghalang privasi: baris di bawah ini adalah gerbang terakhir ---
        if settings.llm_block_pii:
            pastikan_bersih(muatan)
        logger.info("Permintaan ke layanan AI: %s", ringkas_untuk_log(muatan))

        mulai = time.perf_counter()
        galat_terakhir: Exception | None = None
        koreksi_dialek = 0
        percobaan = 0

        while percobaan < self.maks_percobaan:
            percobaan += 1
            try:
                tanggapan = await self._klien.post("/chat/completions", json=muatan)

                # Penyedia menolak bentuk permintaannya, bukan isinya. Bila
                # keluhannya menyebut nama parameter yang bermasalah, muatan
                # diperbaiki lalu dikirim ulang. Ini yang membuat model baru -
                # yang belum ada ketika baris ini ditulis - tetap dapat dipakai
                # tanpa menyunting kode.
                if tanggapan.status_code in (400, 422) and koreksi_dialek < 2:
                    perbaikan = koreksi_muatan(muatan, _pesan_penyedia(tanggapan))
                    if perbaikan is not None:
                        muatan, keterangan = perbaikan
                        koreksi_dialek += 1
                        # Penyesuaian dialek bukan percobaan ulang: ia tidak
                        # menunggu keadaan membaik, melainkan mengirim
                        # permintaan yang memang berbeda.
                        percobaan -= 1
                        logger.info("Menyesuaikan dialek permintaan: %s", keterangan)
                        continue

                if tanggapan.status_code in self._STATUS_LAYAK_ULANG:
                    jeda = self._hitung_jeda(tanggapan, percobaan)
                    galat_terakhir = LLMTidakTersedia(
                        f"HTTP {tanggapan.status_code} dari penyedia: "
                        f"{_pesan_penyedia(tanggapan)}"
                    )
                    if percobaan < self.maks_percobaan:
                        logger.warning(
                            "Layanan AI menjawab %s; mencoba ulang dalam %.1f detik (percobaan %d/%d).",
                            tanggapan.status_code,
                            jeda,
                            percobaan,
                            self.maks_percobaan,
                        )
                        await asyncio.sleep(jeda)
                        continue
                    break

                tanggapan.raise_for_status()
                data = tanggapan.json()
                self._pemutus.catat_sukses()
                return self._ke_hasil(data, mulai)

            except (httpx.TimeoutException, httpx.TransportError) as exc:
                galat_terakhir = exc
                if percobaan < self.maks_percobaan:
                    jeda = min(2.0**percobaan, 8.0)
                    logger.warning(
                        "Gangguan jaringan ke layanan AI (%s); mencoba ulang dalam %.1f detik.",
                        type(exc).__name__,
                        jeda,
                    )
                    await asyncio.sleep(jeda)
                    continue
            except httpx.HTTPStatusError as exc:
                # 400/401/403/404 tidak layak diulang - konfigurasi yang salah.
                self._pemutus.catat_gagal()
                kode = exc.response.status_code
                pesan = _pesan_penyedia(exc.response)
                jenis = _jenis_galat(exc.response)
                raise LLMTidakTersedia(
                    f"Penyedia menolak permintaan (HTTP {kode}): "
                    f"{pesan.rstrip('.')}. " + _saran_galat(kode, pesan, jenis)
                ) from exc

        self._pemutus.catat_gagal()
        raise LLMTidakTersedia(
            f"Layanan AI tidak menjawab setelah {self.maks_percobaan} percobaan."
        ) from galat_terakhir

    @staticmethod
    def _hitung_jeda(tanggapan: httpx.Response, percobaan: int) -> float:
        """Hormati tajuk ``Retry-After`` bila ada, jika tidak gunakan mundur eksponensial."""
        tajuk = tanggapan.headers.get("Retry-After")
        if tajuk:
            try:
                return min(float(tajuk), 15.0)
            except ValueError:
                pass
        return min(2.0**percobaan, 8.0)

    def _ke_hasil(self, data: dict[str, Any], mulai: float) -> HasilLLM:
        pilihan = (data.get("choices") or [{}])[0]
        pesan = pilihan.get("message") or {}
        isi = pesan.get("content") or ""
        pemakaian = data.get("usage") or {}

        # Sebagian model - terutama yang berorientasi penalaran - memisahkan
        # rantai pikirnya ke "reasoning_content" dan menyisakan "content"
        # kosong bila anggaran token habis lebih dahulu. Sebelumnya keadaan
        # ini lolos sebagai jawaban kosong: pengguna melihat layar hampa
        # tanpa satu pun keterangan. Diperlakukan sebagai kegagalan, sehingga
        # lapisan berikutnya beralih ke ringkasan templat yang selalu terisi.
        #
        # Isi "reasoning_content" sengaja TIDAK dipakai sebagai pengganti.
        # Rantai pikir bukan jawaban: ia kerap berbahasa Inggris, memuat
        # keraguan yang belum diselesaikan, dan sesekali berisi angka yang
        # akhirnya ditolak model itu sendiri. Menampilkannya kepada petugas
        # akan lebih merugikan daripada tidak menampilkan apa pun.
        if not isi.strip():
            alasan = pilihan.get("finish_reason")
            if pesan.get("reasoning_content"):
                keterangan = (
                    "Model menghabiskan seluruh anggaran token untuk menalar dan "
                    "belum sempat menuliskan jawaban."
                )
                if alasan == "length":
                    keterangan += " Naikkan NADI_LLM_MAX_TOKENS atau pilih model yang lebih ringkas."
            else:
                keterangan = f"Model mengembalikan jawaban kosong (finish_reason={alasan})."
            raise LLMTidakTersedia(keterangan)

        return HasilLLM(
            teks=isi.strip(),
            model=data.get("model") or self.model,
            penyedia=self.nama,
            durasi_ms=int((time.perf_counter() - mulai) * 1000),
            token_masukan=pemakaian.get("prompt_tokens"),
            token_keluaran=pemakaian.get("completion_tokens"),
        )

    async def daftar_model(self) -> list[str]:
        """Ambil daftar model yang tersedia dari penyedia.

        Berguna saat penyiapan awal: pengguna cukup memberi kunci API, lalu
        nama model yang sah dapat ditemukan sendiri tanpa menebak.
        """
        try:
            tanggapan = await self._klien.get("/models")
            tanggapan.raise_for_status()
            data = tanggapan.json()
            butir = data.get("data") if isinstance(data, dict) else data
            return sorted(
                str(m.get("id")) for m in (butir or []) if isinstance(m, dict) and m.get("id")
            )
        except (httpx.HTTPError, ValueError, AttributeError) as exc:
            logger.warning("Gagal mengambil daftar model: %s", exc)
            return []

    async def periksa(self) -> dict[str, Any]:
        if self._pemutus.terbuka:
            return {
                "penyedia": self.nama,
                "tersedia": False,
                "alasan": f"pemutus arus terbuka ({self._pemutus.sisa_detik} detik lagi)",
            }
        try:
            hasil = await self.chat(
                [
                    PesanChat(Peran.SISTEM, "Jawab dengan satu kata."),
                    PesanChat(Peran.PENGGUNA, "Balas: SIAP"),
                ],
                maks_token=10,
            )
            return {
                "penyedia": self.nama,
                "tersedia": True,
                "model": hasil.model,
                "durasi_ms": hasil.durasi_ms,
                "base_url": self.base_url,
            }
        except LLMTidakTersedia as exc:
            return {"penyedia": self.nama, "tersedia": False, "alasan": str(exc)}

    async def tutup(self) -> None:
        await self._klien.aclose()


# ---------------------------------------------------------------------------
# Cadangan luring
# ---------------------------------------------------------------------------
class PenyediaTemplat(PenyediaLLM):
    """Cadangan tanpa jaringan.

    Penyedia ini tidak menghasilkan kalimat baru. Ia mengembalikan pesan jujur
    bahwa layanan AI sedang tidak tersedia, sehingga lapisan di atasnya dapat
    menyajikan ringkasan berbasis templat dari data terstruktur yang sudah
    dihitung sistem - skor, faktor risiko, dan rekomendasi tetap tampil karena
    semuanya berasal dari model dan aturan lokal, bukan dari model bahasa.

    Konsekuensi rancangan yang disengaja: seluruh angka dan keputusan NADI
    berasal dari perhitungan lokal. Model bahasa hanya memperindah penyajian.
    Bila ia mati, sistem kehilangan gaya bahasa - bukan kehilangan analisis.
    """

    nama = "templat-luring"

    def __init__(self, alasan: str = "layanan AI tidak dikonfigurasi") -> None:
        self.alasan = alasan

    async def chat(
        self,
        pesan: Sequence[PesanChat],
        *,
        suhu: float | None = None,
        maks_token: int | None = None,
    ) -> HasilLLM:
        return HasilLLM(
            teks="",
            model="templat-luring",
            penyedia=self.nama,
            durasi_ms=0,
            dari_cadangan=True,
            catatan=self.alasan,
        )

    async def periksa(self) -> dict[str, Any]:
        return {"penyedia": self.nama, "tersedia": True, "alasan": self.alasan}


# ---------------------------------------------------------------------------
# Penyedia dengan peralihan otomatis
# ---------------------------------------------------------------------------
class PenyediaBerlapis(PenyediaLLM):
    """Membungkus penyedia utama dan beralih ke cadangan bila gagal."""

    nama = "berlapis"

    def __init__(self, utama: PenyediaLLM, cadangan: PenyediaLLM) -> None:
        self.utama = utama
        self.cadangan = cadangan

    async def chat(
        self,
        pesan: Sequence[PesanChat],
        *,
        suhu: float | None = None,
        maks_token: int | None = None,
    ) -> HasilLLM:
        try:
            return await self.utama.chat(pesan, suhu=suhu, maks_token=maks_token)
        except LLMTidakTersedia as exc:
            logger.warning("Beralih ke cadangan luring: %s", exc)
            hasil = await self.cadangan.chat(pesan, suhu=suhu, maks_token=maks_token)
            hasil.catatan = str(exc)
            return hasil

    async def periksa(self) -> dict[str, Any]:
        return await self.utama.periksa()

    async def tutup(self) -> None:
        await self.utama.tutup()
        await self.cadangan.tutup()


# ---------------------------------------------------------------------------
# Pabrik
# ---------------------------------------------------------------------------
_penyedia_tunggal: PenyediaLLM | None = None


def buat_penyedia() -> PenyediaLLM:
    """Bangun penyedia sesuai konfigurasi yang berlaku."""
    if not settings.llm_configured:
        return PenyediaTemplat(settings.alasan_llm_belum_siap or "konfigurasi layanan AI belum lengkap")

    utama = PenyediaKompatibelOpenAI(
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key,
        model=settings.llm_model,
        timeout=settings.llm_timeout_seconds,
    )
    return PenyediaBerlapis(utama, PenyediaTemplat("layanan AI sedang tidak menjawab"))


def dapatkan_penyedia() -> PenyediaLLM:
    """Kembalikan penyedia bersama untuk seluruh proses."""
    global _penyedia_tunggal
    if _penyedia_tunggal is None:
        _penyedia_tunggal = buat_penyedia()
    return _penyedia_tunggal


async def tutup_penyedia() -> None:
    """Tutup penyedia bersama saat aplikasi berhenti."""
    global _penyedia_tunggal
    if _penyedia_tunggal is not None:
        await _penyedia_tunggal.tutup()
        _penyedia_tunggal = None


__all__ = [
    "HasilLLM",
    "LLMTidakTersedia",
    "PemutusArus",
    "Peran",
    "PenyediaBerlapis",
    "PenyediaKompatibelOpenAI",
    "PenyediaLLM",
    "PenyediaTemplat",
    "PesanChat",
    "buat_penyedia",
    "dapatkan_penyedia",
    "tutup_penyedia",
]
