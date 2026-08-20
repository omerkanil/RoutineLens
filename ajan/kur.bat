@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0.."

echo ==============================================
echo   RoutineLens - Ajan Kurulumu
echo ==============================================
echo.

REM --- Python kontrolu ---
where python >nul 2>nul
if errorlevel 1 (
  echo [HATA] Python bulunamadi.
  echo.
  echo Lutfen https://www.python.org/downloads/ adresinden Python 3.11 kurun
  echo ve kurulum sirasinda "Add python.exe to PATH" kutusunu isaretleyin.
  echo.
  pause
  exit /b 1
)

python -c "import sys; sys.exit(0 if (3,9) <= sys.version_info[:2] <= (3,12) else 1)"
if errorlevel 1 (
  echo [HATA] Python 3.9 - 3.12 gerekli. Kurulu surum:
  python --version
  echo.
  echo Onemli: torch/ultralytics, Python 3.11 ile en uyumludur.
  pause
  exit /b 1
)

echo Python surumu:
python --version
echo.

REM --- Sanal ortam ---
if not exist "venv\Scripts\python.exe" (
  echo Sanal ortam olusturuluyor...
  python -m venv venv
  if errorlevel 1 (
    echo [HATA] Sanal ortam olusturulamadi.
    pause
    exit /b 1
  )
)

set "PY=venv\Scripts\python.exe"

echo Bagimliliklar kuruluyor (ilk kurulum bir kac dakika surebilir)...
"%PY%" -m pip install --upgrade pip
"%PY%" -m pip install -r agent_requirements.txt
if errorlevel 1 (
  echo [HATA] Bagimliliklar kurulamadi. Internet baglantinizi kontrol edin.
  pause
  exit /b 1
)

echo.
echo YOLO modelleri indiriliyor (ilk kurulum)...
"%PY%" -c "from ultralytics import YOLO; YOLO('yolov8n-pose.pt'); YOLO('yolov8n.pt'); print('Modeller hazir.')"

REM --- Ayar dosyasi ---
if not exist "ajan_ayarlar.txt" (
  copy /Y "ajan_ayarlar_ornek.txt" "ajan_ayarlar.txt" >nul
  echo.
  echo "ajan_ayarlar.txt" olusturuldu.
)

echo.
echo ==============================================
echo   Kurulum tamamlandi.
echo.
echo   1) "ajan_ayarlar.txt" dosyasini acip SUNUCU ve KULLANICI degerlerini girin.
echo   2) Takibi baslatmak icin "ajan\RoutineLensAjan.bat" dosyasina cift tiklayin.
echo ==============================================
pause
