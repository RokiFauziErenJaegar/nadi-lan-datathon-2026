"""Katalog penyedia model bahasa yang sudah dikenal.

Daftar ini semata-mata kenyamanan: seluruh penyedia di bawah berbicara dialek
yang sama - titik akhir bergaya ``/chat/completions`` - sehingga sebenarnya
alamat mana pun dapat diketik sendiri. Yang disediakan di sini hanyalah alamat
yang benar, supaya tidak ada yang perlu mencari-cari dan salah ketik.

Satu pilihan pada daftar ini pantas mendapat perhatian khusus: **model lokal**.
Ketika NADI dijalankan di atas data keluarga yang sesungguhnya - bukan data
sintetis seperti sekarang - pertanyaan pertama pengawas data pribadi adalah ke
mana teks itu dikirim. Menjalankan model di server dinas sendiri menjawab
pertanyaan itu secara mutlak: tidak ada yang keluar dari jaringan pemerintah
daerah. Penghalang PII pada sistem ini tetap bekerja, namun jaminan terkuat
selalu berupa data yang memang tidak pernah berangkat ke mana pun.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Penyedia:
    kode: str
    nama: str
    base_url: str
    keterangan: str
    butuh_kunci: bool = True
    model_disarankan: tuple[str, ...] = field(default_factory=tuple)
    petunjuk_kunci: str | None = None


KATALOG: tuple[Penyedia, ...] = (
    Penyedia(
        kode="opencode_zen",
        nama="OpenCode Zen",
        base_url="https://opencode.ai/zen/v1",
        keterangan=(
            "Gerbang yang menyatukan banyak penyedia dalam satu kunci. Menyediakan "
            "beberapa model gratis, sehingga sistem tetap dapat dijalankan penuh "
            "tanpa memasang metode pembayaran."
        ),
        model_disarankan=("claude-sonnet-4-5", "claude-haiku-4-5", "gemini-3-flash", "hy3-free"),
        petunjuk_kunci="Dibuat pada konsol OpenCode Zen. Model berbayar menuntut metode pembayaran terpasang.",
    ),
    Penyedia(
        kode="openai",
        nama="OpenAI",
        base_url="https://api.openai.com/v1",
        keterangan=(
            "Layanan asal. Keluarga gpt-5 dan o-series memakai dialek parameter "
            "yang berbeda; NADI menyesuaikannya sendiri."
        ),
        model_disarankan=("gpt-4.1-mini", "gpt-4o-mini", "gpt-5-mini", "gpt-5"),
        petunjuk_kunci="Kunci berawalan sk- atau sk-proj-, dibuat di platform.openai.com.",
    ),
    Penyedia(
        kode="openrouter",
        nama="OpenRouter",
        base_url="https://openrouter.ai/api/v1",
        keterangan="Gerbang lintas penyedia. Nama model ditulis 'penyedia/model'.",
        model_disarankan=("openai/gpt-4.1-mini", "anthropic/claude-3.5-haiku", "google/gemini-flash-1.5"),
        petunjuk_kunci="Kunci berawalan sk-or-, dibuat di openrouter.ai/keys.",
    ),
    Penyedia(
        kode="groq",
        nama="Groq",
        base_url="https://api.groq.com/openai/v1",
        keterangan="Sangat cepat untuk model terbuka. Berguna ketika jawaban harus muncul seketika saat demo.",
        model_disarankan=("llama-3.3-70b-versatile", "llama-3.1-8b-instant"),
        petunjuk_kunci="Kunci berawalan gsk_, dibuat di console.groq.com.",
    ),
    Penyedia(
        kode="deepseek",
        nama="DeepSeek",
        base_url="https://api.deepseek.com/v1",
        keterangan="Biaya rendah dengan mutu bahasa yang memadai untuk penjelasan kebijakan.",
        model_disarankan=("deepseek-chat",),
        petunjuk_kunci="Dibuat di platform.deepseek.com.",
    ),
    Penyedia(
        kode="lokal",
        nama="Model lokal (Ollama / LM Studio)",
        base_url="http://127.0.0.1:11434/v1",
        keterangan=(
            "Model berjalan di komputer atau server dinas sendiri. Tidak ada satu "
            "kata pun yang keluar dari jaringan. Pilihan paling tepat bila NADI "
            "kelak dijalankan di atas data keluarga yang sesungguhnya."
        ),
        butuh_kunci=False,
        model_disarankan=("qwen2.5:7b-instruct", "llama3.1:8b", "gemma2:9b"),
        petunjuk_kunci="Tidak memerlukan kunci. Pastikan Ollama berjalan lebih dahulu.",
    ),
    Penyedia(
        kode="lainnya",
        nama="Penyedia lain",
        base_url="",
        keterangan="Alamat apa pun yang menyediakan titik akhir bergaya OpenAI.",
        model_disarankan=(),
        petunjuk_kunci=None,
    ),
)

PETA_KATALOG: dict[str, Penyedia] = {p.kode: p for p in KATALOG}


def tebak_penyedia(base_url: str) -> str:
    """Tebak kode penyedia dari alamatnya. Dipakai untuk menandai pilihan aktif."""
    alamat = (base_url or "").strip().rstrip("/").lower()
    if not alamat:
        return "lainnya"
    for p in KATALOG:
        if p.base_url and alamat == p.base_url.rstrip("/").lower():
            return p.kode
    # Alamat lokal dikenali dari inangnya, karena nomor porta bisa berbeda-beda.
    if alamat.startswith(("http://127.0.0.1", "http://localhost", "http://0.0.0.0")):
        return "lokal"
    return "lainnya"


def ke_dict(p: Penyedia) -> dict:
    return {
        "kode": p.kode,
        "nama": p.nama,
        "base_url": p.base_url,
        "keterangan": p.keterangan,
        "butuh_kunci": p.butuh_kunci,
        "model_disarankan": list(p.model_disarankan),
        "petunjuk_kunci": p.petunjuk_kunci,
    }


__all__ = ["KATALOG", "PETA_KATALOG", "Penyedia", "ke_dict", "tebak_penyedia"]
