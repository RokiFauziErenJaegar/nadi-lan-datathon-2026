"""Penyesuaian dialek antarpenyedia model bahasa.

"Kompatibel dengan OpenAI" ternyata bukan satu bahasa, melainkan sekeluarga
dialek yang berbeda pada hal-hal kecil namun mematikan. Modul ini menampung
seluruh perbedaan itu di satu tempat, sehingga sisa aplikasi dapat menulis satu
bentuk permintaan saja.

Perbedaan yang benar-benar ditemui, diuji langsung terhadap layanan yang
bersangkutan:

* ``max_tokens`` versus ``max_completion_tokens``. Keluarga penalar OpenAI -
  ``o1``, ``o3``, ``o4``, dan ``gpt-5`` ke atas - menolak ``max_tokens`` dengan
  galat ``unsupported_parameter``. Model yang lebih tua justru hanya mengenal
  ``max_tokens``.
* ``temperature``. Keluarga yang sama menolak nilai selain 1, dengan galat
  ``unsupported_value``. Mengirim 0,2 - nilai yang dipakai NADI agar jawaban
  konsisten - membuat permintaan gagal seluruhnya.
* Beberapa gerbang mengabaikan tajuk atribusi, sebagian lain memerlukannya.

Dua lapis pertahanan dipakai bersama, dan itu disengaja:

**Tebakan dari nama model** menangani kasus yang sudah diketahui tanpa
memboroskan satu permintaan pun. **Koreksi dari pesan galat** menangani model
yang belum ada ketika baris ini ditulis: ketika penyedia menolak sebuah
parameter dan menyebutkan namanya, permintaan diperbaiki lalu diulang sekali.
Lapis kedua itulah yang membuat modul ini tidak perlu diperbarui setiap kali
sebuah penyedia merilis keluarga model baru.
"""

from __future__ import annotations

import re
from typing import Any

# Nama keluarga model yang memakai dialek penalar. Dicocokkan pada awal nama
# sesudah awalan penyedia dibuang, sehingga "openai/gpt-5-mini" pada gerbang
# seperti OpenRouter tetap terdeteksi.
_POLA_PENALAR = re.compile(
    r"^(?:o[1-9](?:-|$)|gpt-(?:[5-9]|\d{2,})(?:[.\-]|$)|grok-code|deepseek-r)",
    re.IGNORECASE,
)

# Model yang namanya mengandung penanda ini adalah varian percakapan biasa dari
# keluarga penalar, dan menerima parameter lama. OpenAI menyediakannya justru
# agar aplikasi lama tidak perlu berubah.
_PENANDA_PERCAKAPAN = ("-chat", "chat-latest")


def keluarga_penalar(model: str) -> bool:
    """Benar bila model diperkirakan memakai dialek keluarga penalar."""
    nama = (model or "").strip().lower()
    if not nama:
        return False
    # Gerbang seperti OpenRouter menuliskan "penyedia/model".
    if "/" in nama:
        nama = nama.rsplit("/", 1)[-1]
    if any(p in nama for p in _PENANDA_PERCAKAPAN):
        return False
    return bool(_POLA_PENALAR.match(nama))


def siapkan_muatan(
    *,
    model: str,
    pesan: list[dict[str, str]],
    maks_token: int,
    suhu: float,
) -> dict[str, Any]:
    """Susun muatan permintaan yang sesuai dengan dialek model bersangkutan."""
    muatan: dict[str, Any] = {"model": model, "messages": pesan}
    if keluarga_penalar(model):
        # Keluarga penalar menghabiskan sebagian anggaran token untuk menalar
        # sebelum menuliskan jawaban, sehingga batasnya dilonggarkan. Suhu
        # sengaja tidak disertakan sama sekali - bukan disetel 1 - agar
        # penyedia memakai nilai bawaannya sendiri.
        muatan["max_completion_tokens"] = maks_token
    else:
        muatan["max_tokens"] = maks_token
        muatan["temperature"] = suhu
    return muatan


# ---------------------------------------------------------------------------
# Koreksi dari pesan galat
# ---------------------------------------------------------------------------
def koreksi_muatan(muatan: dict[str, Any], pesan_galat: str) -> tuple[dict[str, Any], str] | None:
    """Perbaiki muatan berdasarkan keluhan penyedia, bila keluhannya dikenali.

    Kembalikan pasangan (muatan baru, keterangan perubahan), atau ``None`` bila
    galatnya bukan soal parameter dan mengulang permintaan tidak akan menolong.

    Fungsi ini sengaja hanya menangani keluhan tentang parameter. Galat lain -
    kunci ditolak, kuota habis, model tidak dikenal - tidak akan membaik dengan
    diulang, dan mengulangnya hanya menunda pesan yang perlu dibaca pemakai.
    """
    teks = (pesan_galat or "").lower()
    baru = dict(muatan)

    if "max_tokens" in teks and "max_completion_tokens" in teks and "max_tokens" in baru:
        baru["max_completion_tokens"] = baru.pop("max_tokens")
        return baru, "max_tokens diganti menjadi max_completion_tokens"

    if "temperature" in teks and "temperature" in baru:
        baru.pop("temperature")
        return baru, "temperature dihapus karena model hanya menerima nilai bawaan"

    if "top_p" in teks and "top_p" in baru:
        baru.pop("top_p")
        return baru, "top_p dihapus"

    # Beberapa penyedia menolak parameter tanpa menyebut penggantinya. Bila
    # keluhannya jelas menyangkut parameter yang tidak didukung dan muatan
    # masih membawa suku pilihan, buang yang paling sering bermasalah.
    if ("unsupported" in teks or "unrecognized" in teks or "not supported" in teks) and "temperature" in baru:
        baru.pop("temperature")
        return baru, "temperature dihapus setelah penyedia menolak parameter"

    return None


__all__ = ["keluarga_penalar", "koreksi_muatan", "siapkan_muatan"]
