@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

title RoutineLens - Baslat (Dashboard + Kamera)

echo ============================================
echo   RoutineLens - Dashboard + Kamera
echo ============================================
echo.

REM 1) Docker (dashboard icin)
where docker >nul 2>nul
if errorlevel 1 (
    echo [HATA] Docker bulunamadi. Docker Desktop kurun.
    pause
    exit /b 1
)

docker info >nul 2>nul
if errorlevel 1 (
    echo Docker motoru kapali. Docker Desktop baslatiliyor...
    start "" "%ProgramFiles%\Docker\Docker\Docker Desktop.exe" 2>nul
    start "" "%LOCALAPPDATA%\Programs\DockerDesktop\Docker Desktop.exe" 2>nul
    echo Docker hazir olana kadar bekleniyor...
    timeout /t 30 /nobreak >nul
)

echo Dashboard baslatiliyor (Docker)...
docker compose up -d

REM 2) Python kontrolu (kamera icin)
where python >nul 2>nul
if errorlevel 1 (
    echo [UYARI] Python bulunamadi - kamera baslamayacak, sadece panel acilacak.
    goto tarayici
)

python --version 2>&1 | findstr /i /c:"3.9" /c:"3.10" /c:"3.11" /c:"3.12" >nul
if errorlevel 1 (
    echo [UYARI] Python 3.9-3.12 gerekli - kamera baslamayacak.
    goto tarayici
)

REM 3) Ajan bagimliliklari (bir kez)
if not exist "venv\Scripts\python.exe" (
    echo Ajan bagimliliklari kuruluyor - bir kac dakika...
    python -m venv venv
    venv\Scripts\python.exe -m pip install --upgrade pip
    venv\Scripts\python.exe -m pip install -r agent_requirements.txt
    echo GPU hizlandirmasi icin CUDA torch kuruluyor...
    venv\Scripts\python.exe -m pip install --upgrade --force-reinstall torch torchvision --index-url https://download.pytorch.org/whl/cu121
    echo YOLO modelleri indiriliyor...
    venv\Scripts\python.exe -c "from ultralytics import YOLO; YOLO('yolov8n-pose.pt'); YOLO('yolov8n.pt'); print('Modeller hazir')"
)

REM 4) Kamera kontrolcusunu baslat (kamera, paneldeki Takibi Baslat ile acilir)
echo Ajan kontrolcusu baslatiliyor...
start "RoutineLens Kontrol" "venv\Scripts\python.exe" ajan\kontrol.py

:tarayici
echo Tarayici aciliyor - http://localhost:8501
start "" "http://localhost:8501"

echo.
echo Dashboard - http://localhost:8501
echo Giris - admin / admin123
echo Kamera - panelde "Takibi Baslat" butonuna basin.

