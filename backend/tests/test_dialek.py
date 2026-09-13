"""Uji penyesuaian dialek antarpenyedia model bahasa.

Kekeliruan pada lapisan ini tidak muncul sebagai galat yang jelas: ia muncul
sebagai satu keluarga model yang selalu gagal dipakai, dengan pesan penyedia
yang terbaca seperti kesalahan konfigurasi. Karena itu setiap aturannya diuji
di sini, tanpa jaringan.
"""

from __future__ import annotations

import pytest

from nadi.ai.dialek import keluarga_penalar, koreksi_muatan, siapkan_muatan


# ---------------------------------------------------------------------------
# Pengenalan keluarga model
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "model",
    [
        "gpt-5",
        "gpt-5-mini",
        "gpt-5.4",
        "gpt-5.2-codex",
        "o1",
        "o1-pro",
        "o3-mini",
        "o4-mini",
        "openai/gpt-5-mini",  # bentuk gerbang seperti OpenRouter
        "deepseek-r1",
    ],
)
def test_keluarga_penalar_dikenali(model: str) -> None:
    assert keluarga_penalar(model) is True


@pytest.mark.parametrize(
    "model",
    [
        "gpt-4o-mini",
        "gpt-4.1-mini",
        "claude-haiku-4-5",
        "claude-sonnet-4-5",
        "hy3-free",
        "qwen3.6-plus",
        "llama-3.3-70b-versatile",
        "gemma2:9b",
        "",
    ],
)
def test_model_biasa_bukan_penalar(model: str) -> None:
    assert keluarga_penalar(model) is False


@pytest.mark.parametrize("model", ["gpt-5-chat-latest", "gpt-5.2-chat-latest"])
def test_varian_percakapan_memakai_dialek_lama(model: str) -> None:
    """Varian '-chat' disediakan justru agar aplikasi lama tidak perlu berubah."""
    assert keluarga_penalar(model) is False


# ---------------------------------------------------------------------------
# Penyusunan muatan
# ---------------------------------------------------------------------------
def test_model_biasa_memakai_max_tokens_dan_suhu() -> None:
    m = siapkan_muatan(model="gpt-4o-mini", pesan=[], maks_token=500, suhu=0.2)
    assert m["max_tokens"] == 500
    assert m["temperature"] == 0.2
    assert "max_completion_tokens" not in m


def test_model_penalar_memakai_max_completion_tokens_tanpa_suhu() -> None:
    m = siapkan_muatan(model="gpt-5", pesan=[], maks_token=500, suhu=0.2)
    assert m["max_completion_tokens"] == 500
    assert "max_tokens" not in m
    # Suhu tidak disetel 1, melainkan tidak disertakan sama sekali - penyedia
    # memakai nilai bawaannya sendiri.
    assert "temperature" not in m


def test_muatan_selalu_membawa_model_dan_pesan() -> None:
    pesan = [{"role": "user", "content": "halo"}]
    for nama in ("gpt-4o-mini", "gpt-5"):
        m = siapkan_muatan(model=nama, pesan=pesan, maks_token=10, suhu=0.5)
        assert m["model"] == nama
        assert m["messages"] == pesan


# ---------------------------------------------------------------------------
# Koreksi dari pesan galat
# ---------------------------------------------------------------------------
def test_koreksi_mengganti_max_tokens() -> None:
    """Pesan asli OpenAI, disalin apa adanya dari tanggapan sungguhan."""
    muatan = {"model": "gpt-5", "max_tokens": 100, "temperature": 0.2}
    hasil = koreksi_muatan(
        muatan,
        "Unsupported parameter: 'max_tokens' is not supported with this model. "
        "Use 'max_completion_tokens' instead.",
    )
    assert hasil is not None
    baru, _ = hasil
    assert baru["max_completion_tokens"] == 100
    assert "max_tokens" not in baru
    # Muatan asal tidak boleh ikut berubah.
    assert muatan["max_tokens"] == 100


def test_koreksi_membuang_suhu() -> None:
    muatan = {"model": "gpt-5", "max_completion_tokens": 100, "temperature": 0.2}
    hasil = koreksi_muatan(
        muatan,
        "Unsupported value: 'temperature' does not support 0.2 with this model. "
        "Only the default (1) value is supported.",
    )
    assert hasil is not None
    baru, _ = hasil
    assert "temperature" not in baru
    assert baru["max_completion_tokens"] == 100


def test_koreksi_menyerah_pada_galat_yang_bukan_parameter() -> None:
    """Kunci ditolak tidak akan membaik dengan diulang - jangan mengulangnya."""
    muatan = {"model": "gpt-5", "max_tokens": 100, "temperature": 0.2}
    assert koreksi_muatan(muatan, "Invalid API key.") is None
    assert koreksi_muatan(muatan, "No payment method.") is None
    assert koreksi_muatan(muatan, "") is None


def test_koreksi_tidak_mengulang_bila_sudah_diperbaiki() -> None:
    """Setelah suku pilihan habis, tidak ada lagi yang dapat dikoreksi."""
    muatan = {"model": "gpt-5", "max_completion_tokens": 100}
    assert koreksi_muatan(muatan, "Unsupported parameter: 'temperature'") is None


def test_urutan_koreksi_menyelesaikan_kedua_ketaksesuaian() -> None:
    """Dua koreksi berurutan harus menghasilkan muatan yang diterima gpt-5."""
    muatan = siapkan_muatan(model="model-baru-yang-belum-dikenal", pesan=[], maks_token=100, suhu=0.2)
    assert "max_tokens" in muatan and "temperature" in muatan

    hasil = koreksi_muatan(muatan, "'max_tokens' is not supported. Use 'max_completion_tokens'.")
    assert hasil is not None
    muatan = hasil[0]

    hasil = koreksi_muatan(muatan, "Unsupported value: 'temperature' does not support 0.2")
    assert hasil is not None
    muatan = hasil[0]

    assert set(muatan) == {"model", "messages", "max_completion_tokens"}
