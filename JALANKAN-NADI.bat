@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul 2>&1
title NADI - Navigasi AI Data Intervensi

REM ===========================================================================
REM  Peluncur satu-klik NADI.
REM
REM  Skrip ini memeriksa setiap prasyarat lebih dahulu, lalu hanya mengerjakan
REM  yang memang belum ada. Menjalankannya untuk kedua kali karena itu langsung
REM  membuka aplikasi dalam hitungan detik - penting ketika dijalankan di depan
REM  dewan juri, saat tidak ada waktu untuk menunggu apa pun.
REM
REM  Seluruh langkah dicetak apa adanya. Bila ada yang gagal, yang terlihat
REM  adalah langkah mana yang gagal dan apa yang perlu dilakukan - bukan sekadar
REM  jendela yang tertutup sendiri.
REM ===========================================================================

cd /d "%~dp0"

echo.
echo  ============================================================
echo    NADI - Navigasi AI Data Intervensi
echo    Kabupaten Pringsewu, Provinsi Lampung
echo  ============================================================
echo.

REM --------------------------------------------------------------------------
REM  1. Python
REM --------------------------------------------------------------------------
if not exist ".venv\Scripts\python.exe" (
    echo  [1/5] Menyiapkan lingkungan Python...
    where python >nul 2>&1
    if errorlevel 1 (
        echo.
        echo  GAGAL: Python tidak ditemukan.
        echo  Pasang Python 3.10 atau lebih baru dari https://www.python.org/downloads/
        echo  Saat memasang, centang "Add Python to PATH".
        echo.
        pause
        exit /b 1
    )
    python -m venv .venv
    if errorlevel 1 (
        echo  GAGAL membuat lingkungan Python.
        pause
        exit /b 1
    )
    echo        Memasang pustaka Python, mohon tunggu beberapa menit...
    .venv\Scripts\python.exe -m pip install --quiet --upgrade pip
    .venv\Scripts\python.exe -m pip install --quiet -r backend\requirements.txt
    if errorlevel 1 (
        echo  GAGAL memasang pustaka Python.
        pause
        exit /b 1
    )
) else (
    echo  [1/5] Lingkungan Python siap.
)

REM --------------------------------------------------------------------------
REM  2. Berkas konfigurasi
REM --------------------------------------------------------------------------
if not exist ".env" (
    echo  [2/5] Membuat berkas konfigurasi .env...
    copy /y ".env.example" ".env" >nul
    for /f "delims=" %%K in ('.venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(48))"') do set KUNCI=%%K
    .venv\Scripts\python.exe -c "import pathlib,sys; p=pathlib.Path('.env'); p.write_text(p.read_text(encoding='utf-8').replace('ganti-nilai-ini-dengan-kunci-acak-yang-panjang', sys.argv[1]), encoding='utf-8')" "!KUNCI!"
    echo        Kunci rahasia acak dibuat.
) else (
    echo  [2/5] Berkas konfigurasi sudah ada.
)

REM --------------------------------------------------------------------------
REM  3. Basis data dan model
REM --------------------------------------------------------------------------
if not exist "data\nadi.db" (
    echo  [3/5] Membangun basis data dan data sintetis...
    echo        Langkah ini hanya berjalan sekali, sekitar satu menit.
    .venv\Scripts\python.exe backend\scripts\siapkan_data.py
    if errorlevel 1 (
        echo  GAGAL membangun basis data.
        pause
        exit /b 1
    )
    echo.
    echo        Melatih model kerentanan dan menilai seluruh keluarga...
    echo        Langkah ini memakan waktu sekitar sepuluh menit. Hanya sekali.
    .venv\Scripts\python.exe backend\scripts\latih_model.py --tanpa-perbandingan
    if errorlevel 1 (
        echo  GAGAL melatih model.
        pause
        exit /b 1
    )
    echo.
    echo        Membentuk antrean kasus dan akun pengguna...
    .venv\Scripts\python.exe backend\scripts\deteksi_kasus.py
) else (
    echo  [3/5] Basis data sudah siap.
)

REM --------------------------------------------------------------------------
REM  4. Antarmuka
REM --------------------------------------------------------------------------
if not exist "frontend\dist\index.html" (
    echo  [4/5] Membangun antarmuka...
    where npm >nul 2>&1
    if errorlevel 1 (
        echo.
        echo  PERINGATAN: Node.js tidak ditemukan, antarmuka tidak dapat dibangun.
        echo  API tetap dapat dipakai melalui http://127.0.0.1:8000/dokumentasi
        echo  Untuk antarmuka lengkap, pasang Node.js dari https://nodejs.org
        echo.
        timeout /t 5 >nul
    ) else (
        pushd frontend
        if not exist "node_modules" (
            echo        Memasang pustaka antarmuka, mohon tunggu...
            call npm install --no-audit --no-fund --silent
        )
        call npm run build
        popd
    )
) else (
    echo  [4/5] Antarmuka sudah dibangun.
)

REM --------------------------------------------------------------------------
REM  5. Jalankan
REM --------------------------------------------------------------------------
echo  [5/5] Menjalankan NADI...
echo.
echo  ============================================================
echo    Aplikasi berjalan di:  http://127.0.0.1:8000
echo    Dokumentasi API     :  http://127.0.0.1:8000/dokumentasi
echo.
echo    Akun untuk mencoba:
echo      dinsos      / NadiDinsos#2026     (Dinas Sosial)
echo      bupati      / NadiPimpinan#2026   (Pimpinan Daerah)
echo      bappeda     / NadiPerencana#2026  (Bappeda)
echo      pupr        / NadiPupr#2026       (Dinas PUPR)
echo      verifikator / NadiVerif#2026      (Petugas lapangan)
echo.
echo    Tekan Ctrl+C untuk menghentikan.
echo  ============================================================
echo.

start "" http://127.0.0.1:8000
cd backend
..\.venv\Scripts\python.exe -m uvicorn nadi.main:app --host 127.0.0.1 --port 8000

endlocal
