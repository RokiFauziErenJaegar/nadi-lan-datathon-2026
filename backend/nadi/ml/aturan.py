"""Mesin aturan tervektorisasi.

Satu penilai aturan dipakai bersama oleh tiga bagian sistem yang berbeda:

* **indeks kerentanan dasar** - mendeteksi faktor risiko dari ekspresi pada
  katalog faktor risiko;
* **penandaan kasus** - memeriksa kondisi yang perlu diverifikasi manusia;
* **mesin rekomendasi** - menguji kelayakan keluarga terhadap ketentuan program.

Menyatukannya bukan sekadar penghematan kode. Bila ketiganya menafsirkan
"desil paling banyak 2" dengan cara yang sedikit berbeda, sistem akan
menjelaskan sesuatu yang tidak sama dengan yang direkomendasikannya - dan
pengguna yang menemukan ketidakcocokan itu akan berhenti mempercayai
keduanya. Satu penilai berarti satu tafsir.

Seluruh penilaian berlangsung secara vektor di atas ``pandas.DataFrame``.
Menilai kelayakan empat puluh ribu keluarga terhadap dua puluh delapan program
berarti lebih dari satu juta pemeriksaan; dikerjakan baris demi baris,
pekerjaan itu memakan waktu berpuluh detik, sedangkan secara vektor selesai
dalam hitungan puluhan milidetik.
"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np
import pandas as pd

logger = logging.getLogger("nadi.ml.aturan")


class AturanTidakSah(ValueError):
    """Diangkat saat sebuah aturan tidak dapat ditafsirkan."""


# ---------------------------------------------------------------------------
# Penilaian satu syarat
# ---------------------------------------------------------------------------
def evaluasi_syarat(syarat: dict[str, Any], X: pd.DataFrame) -> np.ndarray:
    """Nilai satu syarat terhadap seluruh baris matriks fitur.

    Args:
        syarat: berisi ``fitur`` atau ``bidang``, ``operator``, dan ``nilai``.
        X: matriks fitur.

    Returns:
        Larik boolean sepanjang jumlah baris.
    """
    nama = syarat.get("fitur") or syarat.get("bidang")
    if not nama:
        raise AturanTidakSah(f"Syarat tidak menyebut nama fitur: {syarat}")
    if nama not in X.columns:
        raise AturanTidakSah(
            f"Fitur '{nama}' tidak ada pada matriks. Aturan yang menunjuk fitur "
            "tak dikenal tidak akan pernah terpenuhi, sehingga menyembunyikan "
            "kekeliruan alih-alih memunculkannya."
        )

    kolom = X[nama].to_numpy()
    op = str(syarat.get("operator", "is_true"))
    nilai = syarat.get("nilai")

    if op == "is_true":
        return kolom.astype(bool)
    if op == "is_false":
        return ~kolom.astype(bool)
    if op == "exists":
        return ~pd.isna(kolom)
    if op == "eq":
        return kolom == nilai
    if op == "ne":
        return kolom != nilai
    if op == "gt":
        return kolom > nilai
    if op == "gte":
        return kolom >= nilai
    if op == "lt":
        return kolom < nilai
    if op == "lte":
        return kolom <= nilai
    if op == "in":
        return np.isin(kolom, np.asarray(nilai))
    if op == "not_in":
        return ~np.isin(kolom, np.asarray(nilai))
    if op == "between":
        if not isinstance(nilai, (list, tuple)) or len(nilai) != 2:
            raise AturanTidakSah(f"Operator 'between' memerlukan dua nilai: {syarat}")
        return (kolom >= nilai[0]) & (kolom <= nilai[1])

    raise AturanTidakSah(f"Operator '{op}' tidak dikenal.")


def evaluasi_ekspresi(ekspresi: dict[str, Any] | None, X: pd.DataFrame) -> np.ndarray:
    """Nilai ekspresi bersarang berisi penggabung ``semua`` dan ``salah_satu``.

    Ekspresi kosong menghasilkan seluruh baris bernilai salah - bukan benar.
    Pilihan ini disengaja: faktor risiko tanpa aturan deteksi berarti belum
    dapat dikenali otomatis, dan menandainya berlaku bagi semua orang akan
    membanjiri antrean verifikasi dengan kasus tanpa dasar.
    """
    n = len(X)
    if not ekspresi:
        return np.zeros(n, dtype=bool)

    if "semua" in ekspresi:
        hasil = np.ones(n, dtype=bool)
        for butir in ekspresi["semua"]:
            hasil &= _nilai_butir(butir, X)
        return hasil

    if "salah_satu" in ekspresi:
        hasil = np.zeros(n, dtype=bool)
        for butir in ekspresi["salah_satu"]:
            hasil |= _nilai_butir(butir, X)
        return hasil

    # Ekspresi tanpa penggabung dianggap sebagai satu syarat tunggal.
    return evaluasi_syarat(ekspresi, X)


def _nilai_butir(butir: dict[str, Any], X: pd.DataFrame) -> np.ndarray:
    if "semua" in butir or "salah_satu" in butir:
        return evaluasi_ekspresi(butir, X)
    return evaluasi_syarat(butir, X)


# ---------------------------------------------------------------------------
# Penjelasan berbahasa manusia
# ---------------------------------------------------------------------------
def jelaskan_syarat(syarat: dict[str, Any], nilai_baris: Any = None) -> str:
    """Susun kalimat penjelas sebuah syarat, untuk ditampilkan kepada pengguna."""
    from nadi.db.enums import OperatorAturan
    from nadi.ml.fitur import PETA_FITUR

    nama = syarat.get("fitur") or syarat.get("bidang") or "?"
    fitur = PETA_FITUR.get(nama)
    label = fitur.label if fitur else nama
    op = str(syarat.get("operator", "is_true"))
    nilai = syarat.get("nilai")

    try:
        kata = OperatorAturan(op).label
    except ValueError:
        kata = op

    if op in {"is_true", "is_false", "exists"}:
        kalimat = f"{label} {kata}"
    elif op == "between" and isinstance(nilai, (list, tuple)):
        kalimat = f"{label} {kata} {nilai[0]} dan {nilai[1]}"
    elif op in {"in", "not_in"} and isinstance(nilai, (list, tuple)):
        kalimat = f"{label} {kata} {', '.join(str(v) for v in nilai)}"
    else:
        kalimat = f"{label} {kata} {nilai}"

    if nilai_baris is not None:
        kalimat += f" (nilai keluarga ini: {_format(nilai_baris)})"
    return kalimat


def _format(nilai: Any) -> str:
    if isinstance(nilai, (bool, np.bool_)):
        return "ya" if nilai else "tidak"
    if isinstance(nilai, (int, np.integer)):
        return f"{int(nilai):,}".replace(",", ".")
    if isinstance(nilai, (float, np.floating)):
        if float(nilai).is_integer():
            return f"{int(nilai):,}".replace(",", ".")
        return f"{nilai:.2f}".replace(".", ",")
    return str(nilai)


# ---------------------------------------------------------------------------
# Penilaian sekumpulan aturan
# ---------------------------------------------------------------------------
def nilai_kumpulan_aturan(
    aturan: list[dict[str, Any]], X: pd.DataFrame
) -> tuple[np.ndarray, np.ndarray, dict[str, np.ndarray]]:
    """Nilai sekumpulan aturan kelayakan sekaligus.

    Args:
        aturan: setiap butir memuat ``bidang``, ``operator``, ``nilai``, dan
            ``wajib``.
        X: matriks fitur.

    Returns:
        Tiga hal: penanda kelayakan (seluruh aturan wajib terpenuhi), nilai
        kecocokan 0 sampai 1 dari aturan tidak wajib yang terpenuhi, dan peta
        hasil per aturan untuk keperluan penjelasan.
    """
    n = len(X)
    layak = np.ones(n, dtype=bool)
    poin = np.zeros(n, dtype=float)
    bobot_total = 0.0
    per_aturan: dict[str, np.ndarray] = {}

    for i, a in enumerate(aturan):
        try:
            hasil = evaluasi_syarat(a, X)
        except AturanTidakSah as exc:
            logger.warning("Aturan dilewati: %s", exc)
            continue

        kunci = f"{a.get('bidang', '?')}#{i}"
        per_aturan[kunci] = hasil

        if a.get("wajib", True):
            layak &= hasil
        else:
            # Aturan tidak wajib berbobot menurut prioritasnya. Prioritas
            # bernilai kecil berarti lebih penting, sehingga bobotnya dibalik.
            bobot = 1.0 / max(1.0, float(a.get("prioritas", 100)) / 10.0)
            poin += hasil.astype(float) * bobot
            bobot_total += bobot

    kecocokan = poin / bobot_total if bobot_total > 0 else np.zeros(n, dtype=float)
    return layak, kecocokan, per_aturan


__all__ = [
    "AturanTidakSah",
    "evaluasi_ekspresi",
    "evaluasi_syarat",
    "jelaskan_syarat",
    "nilai_kumpulan_aturan",
]
