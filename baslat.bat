@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

title RoutineLens - Panel Baslat

echo ============================================
echo   RoutineLens - Panel Baslat
echo ============================================
echo.

where docker >nul 2>nul
if errorlevel 1 (
    echo [HATA] Docker bulunamadi. Docker Desktop kurun ve baslatin.
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

docker info >nul 2>nul
if errorlevel 1 (
    echo [HATA] Docker motoru hazir degil. Docker Desktop'u elle acip bekleyin, sonra tekrar calistirin.
    pause
    exit /b 1
)

echo Konteynerler baslatiliyor...
docker compose up -d

echo Panel acilana kadar bekleniyor...
timeout /t 8 /nobreak >nul

start "" "http://localhost:8501"

echo.
echo Panel hazir - http://localhost:8501
echo Varsayilan giris - admin / admin123
echo Kapatmak icin - docker compose down
pause
