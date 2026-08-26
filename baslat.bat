@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

title RoutineLens - Baslat

echo ============================================
echo   RoutineLens - Panel + Kamera
echo ============================================
echo.

REM Docker varsa durdur (8501 portunu serbest birak)
docker compose down >nul 2>nul

REM Python kontrolu
where python >nul 2>nul
if errorlevel 1 (
    echo [HATA] Python bulunamadi. Python 3.11 kurun.
    pause
    exit /b 1
)

python -c "import sys; sys.exit(0 if (3,9) <= sys.version_info[:2] <= (3,12) else 1)"
if errorlevel 1 (
    echo [HATA] Python 3.9 - 3.12 gerekli.
    pause
    exit /b 1
)

REM Ilk kurulum: sanal ortam + bagimliliklar + modeller
if not exist "venv\Scripts\python.exe" (
    echo Ilk kurulum basliyor - bir kac dakika surebilir...
    python -m venv venv
    venv\Scripts\python.exe -m pip install --upgrade pip
    venv\Scripts\python.exe -m pip install -r requirements.txt
    echo GPU hizlandirmasi icin CUDA torch kuruluyor...
    venv\Scripts\python.exe -m pip install --upgrade --force-reinstall torch torchvision --index-url https://download.pytorch.org/whl/cu121
    echo YOLO modelleri indiriliyor...
    venv\Scripts\python.exe -c "from ultralytics import YOLO; YOLO('yolov8n-pose.pt'); YOLO('yolov8n.pt'); print('Modeller hazir')"
)

set "PY=venv\Scripts\python.exe"

echo Panel baslatiliyor - http://localhost:8501
start "RoutineLens Panel" "%PY%" -m streamlit run dashboard.py --server.port=8501 --server.headless=false

timeout /t 6 /nobreak >nul
start "" "http://localhost:8501"

echo.
echo Panel - http://localhost:8501
echo Giris - admin / admin123
echo Kamera icin panelde "Takibi Baslat" butonuna tiklayin.
pause
