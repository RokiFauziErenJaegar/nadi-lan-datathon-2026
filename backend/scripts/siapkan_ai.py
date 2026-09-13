"""Penyiapan dan pemeriksaan layanan AI (OpenCode Zen atau penyedia sejenis).

Skrip ini menyelesaikan satu masalah kecil yang sering menyita waktu: menebak
nama model. Penyedia yang kompatibel dengan OpenAI menyediakan titik akhir
``/models``, sehingga cukup satu kunci API - sisanya ditemukan sendiri.

Yang dikerjakan skrip ini, berurutan:

1. Menghubungi penyedia dan mengambil daftar model yang benar-benar tersedia
   bagi kunci Anda. Bila kunci ditolak, yang muncul adalah sebab yang jelas,
   bukan kegagalan diam-diam saat aplikasi sudah berjalan.
2. Mengirim satu permintaan sungguhan ke model terpilih. Daftar model yang
   berhasil diambil belum membuktikan model itu dapat dipakai - kuota, izin,
   dan nama yang sudah usang baru ketahuan saat benar-benar dipanggil.
3. Menguji penghalang privasi dengan muatan yang sengaja mengandung NIK palsu.
   Bila penghalang tidak menahannya, skrip berhenti dan menolak menulis
   konfigurasi. Janji privasi pada proposal ditegakkan di sini, bukan
   dipercayakan pada kehati-hatian pemakai.
4. Menulis hasilnya ke berkas ``.env`` - hanya baris yang bersangkutan,
   sisanya dibiarkan apa adanya.

Contoh pemakaian::

    python backend/scripts/siapkan_ai.py --kunci sk-xxxxxxxx
    python backend/scripts/siapkan_ai.py --daftar
    python backend/scripts/siapkan_ai.py --model qwen3-coder
    python backend/scripts/siapkan_ai.py            # periksa ulang yang sudah ada
"""

from __future__ import annotations

import argparse
import asyncio
import re
import sys
from pathlib import Path

AKAR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(AKAR / "backend"))

from nadi.ai.provider import (  # noqa: E402
    LLMTidakTersedia,
    Peran,
    PenyediaKompatibelOpenAI,
    PesanChat,
)
from nadi.config import settings  # noqa: E402
from nadi.security.pii import PIILeakError, pastikan_bersih  # noqa: E402

BERKAS_ENV = AKAR / ".env"

# Ketika penyedia menawarkan banyak model, urutan ini menentukan mana yang
# dipilih lebih dahulu.
#
# Copilot NADI tidak menghitung apa pun. Seluruh angka - skor kerentanan,
# faktor risiko, rekomendasi program, hasil simulasi - sudah dihitung lokal
# sebelum model bahasa dipanggil. Tugas model hanya menyusun kalimat
# penjelasan dari data terstruktur itu, dalam bahasa Indonesia yang rapi,
# tanpa menambah satu angka pun. Yang menentukan adalah kepatuhan pada
# instruksi dan kualitas bahasa - bukan kemampuan menalar berat atau menulis
# kode. Karena itu model menengah yang cepat lebih cocok daripada model
# terbesar: jawaban muncul dalam hitungan detik saat demo, dengan biaya jauh
# lebih rendah, tanpa kehilangan mutu pada tugas seringan ini.
URUTAN_PILIHAN = (
    "claude-sonnet-4-5",
    "claude-haiku-4-5",
    "claude-sonnet-4-6",
    "claude-sonnet-5",
    "gemini-3-flash",
    "gemini-3.5-flash",
    "gpt-5.4-mini",
    "gpt-5.1",
    "qwen3.6-plus",
    "glm-5.2",
    "deepseek-v4-flash",
    "kimi-k2.5",
)

# Contoh perintah untuk menguji kunci di luar NADI. Bila perintah ini pun
# ditolak, penyebabnya ada pada kunci atau akun - bukan pada aplikasi ini.
# Membuktikan hal itu lebih dahulu menghemat banyak waktu penelusuran.
# Contoh perintah untuk menguji kunci di luar NADI.
#
# Muatan JSON ditulis ke berkas lebih dahulu, bukan disisipkan sebaris.
# PowerShell membuang tanda kutip ganda ketika argumen diserahkan kepada
# program native, sehingga bentuk sebaris berubah menjadi JSON rusak -
# dan Zen menjawabnya dengan 'ModelError' berkode 401. Nomor 401 itu lalu
# terbaca sebagai kunci ditolak, padahal kunci belum sempat diperiksa
# sama sekali. Bentuk berkas menghindarkan jebakan tersebut sepenuhnya.
#
# 'curl.exe', bukan 'curl': pada PowerShell 'curl' adalah alias bagi
# Invoke-WebRequest, yang tidak mengenali satu pun tanda hubung di bawah.
_MUATAN_UJI = '{"model":"claude-haiku-4-5","messages":[{"role":"user","content":"halo"}],"max_tokens":10}'

CONTOH_CURL = (
    f"'{_MUATAN_UJI}' | Set-Content -Encoding ascii \"$env:TEMP\zen.json\"",
    "curl.exe -s https://opencode.ai/zen/v1/chat/completions"
    ' -H "Authorization: Bearer KUNCI-ANDA"'
    ' -H "Content-Type: application/json"'
    ' -d "@$env:TEMP\zen.json"',
)

HIJAU, MERAH, KUNING, ABU, PADAM = "\033[92m", "\033[91m", "\033[93m", "\033[90m", "\033[0m"


def periksa_bentuk_kunci(kunci: str) -> list[str]:
    """Cari kejanggalan yang membuat kunci benar tampak seperti kunci salah.

    Penyedia hanya menjawab "Invalid API key" - satu kalimat yang sama untuk
    kunci yang salah ketik, kunci yang tersalin sebagian, maupun kunci yang
    ikut membawa tanda kutip. Pemeriksaan di bawah memisahkan sebab-sebab itu
    tanpa pernah menampilkan kuncinya sendiri.
    """
    catatan: list[str] = []
    if kunci != kunci.strip():
        catatan.append("ada spasi atau baris baru di awal/akhir")
    if any(c.isspace() for c in kunci.strip()):
        catatan.append("ada spasi di tengah kunci")
    if not kunci.isascii():
        catatan.append("ada karakter non-ASCII (kemungkinan tersalin dari dokumen)")
    if kunci[:1] in "\"'" or kunci[-1:] in "\"'":
        catatan.append("kunci masih terbungkus tanda kutip")
    if "..." in kunci or "…" in kunci:
        catatan.append("mengandung titik-titik - kemungkinan tersalin dari tampilan yang dipotong")
    if len(kunci.strip()) < 20:
        catatan.append(f"hanya {len(kunci.strip())} karakter - kemungkinan tersalin sebagian")
    return catatan


def _lambang(ok: bool) -> str:
    return f"{HIJAU}OK{PADAM}" if ok else f"{MERAH}GAGAL{PADAM}"


def _peringkat(nama: str) -> tuple[int, int, str]:
    """Urutkan model menurut kecocokannya dengan tugas Copilot.

    Nama persis selalu menang atas kecocokan sebagian. Tanpa aturan itu,
    ``claude-sonnet-4`` akan terpilih mendahului ``claude-sonnet-4-5`` hanya
    karena namanya lebih pendek secara abjad.
    """
    rendah = nama.lower()
    for i, pilihan in enumerate(URUTAN_PILIHAN):
        if rendah == pilihan:
            return (0, i, nama)
    for i, pilihan in enumerate(URUTAN_PILIHAN):
        if rendah.startswith(pilihan):
            return (1, i, nama)
    # Model bertanda "-free" ditempatkan paling belakang: berguna untuk
    # mencoba tanpa biaya, namun ketersediaannya tidak dijamin saat demo.
    return (3 if rendah.endswith("-free") else 2, len(URUTAN_PILIHAN), nama)


def tulis_env(nilai: dict[str, str]) -> list[str]:
    """Perbarui kunci tertentu pada .env tanpa mengganggu baris lainnya."""
    if not BERKAS_ENV.exists():
        contoh = AKAR / ".env.example"
        if not contoh.exists():
            raise SystemExit(f"Berkas {BERKAS_ENV} tidak ada dan tidak ada contohnya.")
        BERKAS_ENV.write_text(contoh.read_text(encoding="utf-8"), encoding="utf-8")

    baris = BERKAS_ENV.read_text(encoding="utf-8").splitlines()
    tersisa = dict(nilai)
    berubah: list[str] = []

    for i, isi in enumerate(baris):
        cocok = re.match(r"^\s*([A-Z0-9_]+)\s*=", isi)
        if cocok and cocok.group(1) in tersisa:
            kunci = cocok.group(1)
            baru = f"{kunci}={tersisa.pop(kunci)}"
            if baru != isi:
                baris[i] = baru
                berubah.append(kunci)

    for kunci, isi in tersisa.items():
        baris.append(f"{kunci}={isi}")
        berubah.append(kunci)

    BERKAS_ENV.write_text("\n".join(baris) + "\n", encoding="utf-8")
    return berubah


def uji_penghalang_privasi() -> bool:
    """Pastikan penghalang PII menahan muatan yang jelas-jelas mengandung NIK.

    Dijalankan sebelum kunci ditulis. Bila penghalang ini rusak - misalnya
    karena berkas tersunting keliru - lebih baik penyiapan gagal sekarang
    daripada data keluarga terkirim ke layanan luar tanpa ada yang tahu.
    """
    umpan = {
        "model": "uji",
        "messages": [{"role": "user", "content": "Keluarga dengan NIK 1871064503920001 perlu dibantu."}],
    }
    try:
        pastikan_bersih(umpan)
    except PIILeakError:
        return True
    return False


async def jalankan(args: argparse.Namespace) -> int:
    kunci = (args.kunci or settings.llm_api_key or "").strip()
    base_url = (args.base_url or settings.llm_base_url or "").strip()

    terpasang = bool(kunci) and not kunci.startswith("isi-api-key")
    samar = f"{kunci[:6]}...{kunci[-4:]}" if len(kunci) > 14 else "terlalu pendek"

    print()
    print(f"  Penyedia   : {base_url}")
    print(f"  Kunci API  : {samar if terpasang else ABU + 'belum diisi' + PADAM}"
          f"{ABU + '  (' + str(len(kunci)) + ' karakter)' + PADAM if terpasang else ''}")

    if terpasang:
        for catatan in periksa_bentuk_kunci(kunci):
            print(f"  {KUNING}Perhatian : {catatan}{PADAM}")
    print()

    if not terpasang:
        print(f"  {MERAH}Kunci API belum ada.{PADAM}")
        print()
        print("  Jalankan ulang dengan kunci Anda:")
        print(f"    {ABU}python backend/scripts/siapkan_ai.py --kunci sk-xxxxxxxx{PADAM}")
        print()
        return 2

    # --- Langkah 0: penghalang privasi ---------------------------------------
    aman = uji_penghalang_privasi()
    print(f"  [1/4] Penghalang privasi ......... {_lambang(aman)}")
    if not aman:
        print()
        print(f"  {MERAH}Penghalang PII tidak menahan NIK pada muatan uji.{PADAM}")
        print("  Penyiapan dihentikan; konfigurasi tidak ditulis.")
        print()
        return 1

    klien = PenyediaKompatibelOpenAI(
        base_url=base_url,
        api_key=kunci,
        model=args.model or settings.llm_model or "sementara",
        timeout=args.batas_waktu,
        maks_percobaan=1,
    )

    try:
        # --- Langkah 1: daftar model ----------------------------------------
        model_tersedia = await klien.daftar_model()
        print(f"  [2/4] Daftar model ............... {_lambang(bool(model_tersedia))}"
              f"  {ABU}{len(model_tersedia)} model{PADAM}")

        if model_tersedia:
            urut = sorted(model_tersedia, key=_peringkat)
            print()
            for i, nama in enumerate(urut[:20]):
                tanda = f"{HIJAU}<- disarankan{PADAM}" if i == 0 else ""
                print(f"          {ABU}{i + 1:2d}.{PADAM} {nama}  {tanda}")
            if len(urut) > 20:
                print(f"          {ABU}... dan {len(urut) - 20} lainnya{PADAM}")
            print()
        elif not args.model and not settings.llm_model.strip():
            print()
            print(f"  {KUNING}Penyedia tidak memberikan daftar model.{PADAM}")
            print("  Sebutkan namanya sendiri:")
            print(f"    {ABU}python backend/scripts/siapkan_ai.py --model NAMA-MODEL{PADAM}")
            print()
            return 2

        if args.daftar:
            return 0

        # --- Langkah 2: pilih model ------------------------------------------
        pilihan = (args.model or "").strip()
        if pilihan and model_tersedia and pilihan not in model_tersedia:
            mirip = [m for m in model_tersedia if pilihan.lower() in m.lower()]
            if len(mirip) == 1:
                print(f"  {KUNING}'{pilihan}' tidak persis ada; memakai '{mirip[0]}'.{PADAM}")
                pilihan = mirip[0]
            elif mirip:
                print(f"  {MERAH}'{pilihan}' cocok dengan beberapa model:{PADAM} {', '.join(mirip)}")
                return 2
            else:
                print(f"  {MERAH}Model '{pilihan}' tidak tersedia untuk kunci ini.{PADAM}")
                return 2
        asal = "argumen --model"

        # Model yang sudah tercatat pada .env harus menang atas peringkat
        # bawaan. Tanpa aturan ini, memeriksa ulang konfigurasi yang SUDAH
        # berjalan justru menguji model lain - lalu melaporkan kegagalan atas
        # sesuatu yang sama sekali tidak dipakai aplikasi. Karena daftar model
        # selalu berhasil diambil (titik akhir /models terbuka tanpa kunci),
        # cabang cadangan pada versi sebelumnya tidak pernah tercapai, sehingga
        # kekeliruan ini tersembunyi justru pada keadaan yang paling sering:
        # konfigurasi yang sudah benar.
        if not pilihan:
            tercatat = settings.llm_model.strip()
            if tercatat and (not model_tersedia or tercatat in model_tersedia):
                pilihan, asal = tercatat, "berkas .env"
        if not pilihan and model_tersedia:
            pilihan, asal = sorted(model_tersedia, key=_peringkat)[0], "peringkat bawaan"
        if not pilihan:
            print(f"  {MERAH}Tidak ada model yang dapat dipilih.{PADAM}")
            return 2

        print(f"  Model diuji: {pilihan}  {ABU}(dari {asal}){PADAM}")
        print()

        klien.model = pilihan

        # --- Langkah 3: panggilan sungguhan ----------------------------------
        try:
            hasil = await klien.chat(
                [
                    PesanChat(
                        Peran.SISTEM,
                        "Anda asisten kebijakan sosial. Jawab ringkas dalam bahasa Indonesia.",
                    ),
                    PesanChat(
                        Peran.PENGGUNA,
                        "Sebutkan satu sebab utama keluarga miskin tidak menerima bantuan sosial. "
                        "Jawab satu kalimat.",
                    ),
                ],
                # Longgar dengan sengaja. Model berorientasi penalaran
                # menghabiskan ratusan token untuk menalar sebelum menulis
                # kalimat pertama; anggaran sempit membuat model yang
                # sebenarnya baik tampak gagal pada tahap penyiapan.
                maks_token=1500,
            )
            berhasil = bool(hasil.teks)
        except LLMTidakTersedia as exc:
            print(f"  [3/4] Panggilan ke model ......... {_lambang(False)}")
            print()
            print(f"  {MERAH}{exc}{PADAM}")
            print()

            pesan = str(exc).lower()
            tautan = re.search(r"https?://\S+", str(exc))
            # OpenCode Zen menjawab 401 untuk dua keadaan yang sangat berbeda.
            # Membedakannya menentukan langkah berikutnya, jadi dibedakan di sini.
            if any(k in pesan for k in ("payment method", "billing", "insufficient",
                                        "credit", "quota", "balance", "saldo")):
                print("  Kunci API Anda SAH. Yang menghalangi adalah tagihan akun penyedia.")
                print("  Model berbayar terkunci sampai metode pembayaran terpasang.")
                if tautan:
                    print()
                    print(f"  Pasang di: {tautan.group(0).rstrip('.')}")
                print()
                print("  Sementara itu, model gratis tetap dapat dipakai:")
                print(f"    {ABU}python backend/scripts/siapkan_ai.py --model hy3-free{PADAM}")
                print(f"  {ABU}Lebih lambat dan berbatas laju, namun cukup untuk mencoba.{PADAM}")
            elif "missing api key" in pesan:
                print("  Kunci tidak sampai ke server sama sekali. Sebab yang lazim:")
                print("    - nilainya kosong setelah dibaca dari .env")
                print("    - kunci diapit tanda kutip yang ikut terkirim")
                print(f"  {ABU}Coba langsung tanpa .env:{PADAM}")
                print(f"    {ABU}python backend/scripts/siapkan_ai.py --kunci <kunci> --tanpa-simpan{PADAM}")
            elif "invalid api key" in pesan or "401" in pesan:
                print("  Kunci sampai ke server dengan benar, tetapi nilainya ditolak.")
                print("  Berarti bukan soal konfigurasi NADI. Periksa berurutan:")
                print()
                print("    1. Kunci ini kunci OpenCode Zen, bukan token login OpenCode CLI")
                print("       atau kunci layanan lain. Keduanya berbeda.")
                print("    2. Kunci tersalin utuh - tanpa terpotong di ujung.")
                print("    3. Kunci belum dicabut, dan akunnya sudah punya saldo.")
                print()
                print(f"  {ABU}Uji di luar NADI, untuk memastikan bukan aplikasi ini penyebabnya:{PADAM}")
                for isi in CONTOH_CURL:
                    print(f"    {ABU}{isi}{PADAM}")
                print()
                print()
                print("  Bacalah 'type' pada tanggapannya, bukan nomor statusnya - Zen")
                print("  menjawab 401 untuk tiga hal yang sama sekali berbeda:")
                print(f"    {ABU}AuthError    -> kunci memang ditolak{PADAM}")
                print(f"    {ABU}CreditsError -> kunci sah, tagihan yang belum siap{PADAM}")
                print(f"    {ABU}ModelError   -> nama model salah; kunci belum sempat diperiksa{PADAM}")
            print()
            return 1

        print(f"  [3/4] Panggilan ke model ......... {_lambang(berhasil)}"
              f"  {ABU}{hasil.model}, {hasil.durasi_ms} ms{PADAM}")
        if hasil.teks:
            print()
            print(f"          {ABU}Jawaban: {hasil.teks[:200]}{PADAM}")
            print()
        if not berhasil:
            print(f"  {MERAH}Model menjawab kosong. Coba model lain.{PADAM}")
            return 1

        # --- Langkah 4: simpan ------------------------------------------------
        if args.tanpa_simpan:
            print(f"  [4/4] Menyimpan .env ............. {ABU}dilewati (--tanpa-simpan){PADAM}")
            print()
            return 0

        berubah = tulis_env(
            {
                "NADI_LLM_ENABLED": "true",
                "NADI_LLM_BASE_URL": base_url,
                "NADI_LLM_API_KEY": kunci,
                "NADI_LLM_MODEL": pilihan,
            }
        )
        print(f"  [4/4] Menyimpan .env ............. {_lambang(True)}"
              f"  {ABU}{len(berubah)} baris{PADAM}")
        print()
        print(f"  {HIJAU}Layanan AI siap.{PADAM} Model aktif: {pilihan}")
        print(f"  {ABU}Jalankan ulang server agar konfigurasi baru terbaca.{PADAM}")
        print()
        return 0

    finally:
        await klien.tutup()


def main() -> int:
    p = argparse.ArgumentParser(
        description="Siapkan dan uji layanan AI untuk Policy Copilot NADI.",
    )
    p.add_argument("--kunci", help="Kunci API penyedia. Bila kosong, dibaca dari .env.")
    p.add_argument("--model", help="Nama model. Bila kosong, dipilih dari daftar penyedia.")
    p.add_argument("--base-url", help="Alamat dasar API, bawaannya dari .env.")
    p.add_argument("--daftar", action="store_true", help="Hanya tampilkan daftar model, lalu berhenti.")
    p.add_argument("--tanpa-simpan", action="store_true", help="Uji saja, jangan sunting .env.")
    p.add_argument("--batas-waktu", type=float, default=45.0, help="Batas waktu per permintaan (detik).")
    return asyncio.run(jalankan(p.parse_args()))


if __name__ == "__main__":
    raise SystemExit(main())
