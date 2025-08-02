@echo off
ECHO.
ECHO ===================================================
ECHO      Build Script untuk RepetitionApp AlphaV1
ECHO ===================================================

REM --- Langkah 1: Mengaktifkan Virtual Environment ---
ECHO.
ECHO [1/4] Mencari virtual environment di folder atas (../.env)...
CALL .env\Scripts\activate
IF %ERRORLEVEL% NEQ 0 (
    ECHO [GAGAL] Virtual environment tidak ditemukan di "../.env".
    ECHO Pastikan folder '.env' berada satu level di atas folder tempat 'build.bat' ini.
    GOTO End
)
ECHO Virtual environment berhasil diaktifkan.

REM --- Langkah 2: Menjalankan Perintah PyInstaller ---
ECHO.
ECHO [2/4] Memulai proses pembuatan aplikasi .exe...
pyinstaller --name "RepetitionApp AlphaV1" --onefile --windowed --distpath hasil --add-data "assets;assets" --add-data "data;data" --icon="assets/images/icons/bird_2.png" main.py

REM --- Jika Gagal, Hentikan Skrip ---
IF %ERRORLEVEL% NEQ 0 (
    ECHO [GAGAL] Proses PyInstaller tidak berhasil.
    GOTO End
)

REM --- Langkah 3: Membersihkan dan Merapikan File ---
ECHO.
ECHO [3/4] Merapikan file hasil build...
MOVE /Y "build" "hasil"
MOVE /Y "RepetitionApp AlphaV1.spec" "hasil"
ECHO Folder 'build' dan file '.spec' berhasil dipindahkan ke folder 'hasil'.

ECHO.
ECHO [4/4] Proses Selesai!
ECHO Aplikasi Anda (.exe) telah berhasil dibuat di dalam folder "hasil".
ECHO.

:End
PAUSE