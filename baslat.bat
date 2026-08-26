@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

title RoutineLens - Panel Baslat

echo ============================================
echo   RoutineLens - Panel Baslat
echo ============================================
echo.

REM 1) Docker kurulu mu?
where docker >nul 2>nul
if errorlevel 1 (
    echo [HATA] Docker bulunamadi.
    echo Lutfen Docker Desktop'u kurun ve bilgisayari yeniden baslatin:
    echo   https://www.docker.com/products/docker-desktop/
    pause
    exit /b 1
)

REM 2) Docker motoru calisiyor mu?
docker info >nul 2>nul
if errorlevel 1 (
    echo Docker motoru kapali. Docker Desktop baslatiliyor...
    if exist "%ProgramFiles%\Docker\Docker\Docker Desktop.exe" (
        start "" "%ProgramFiles%\Docker\Docker\Docker Desktop.exe"
    ) else if exist "%LOCALAPPDATA%\Programs\DockerDesktop\Docker Desktop.exe" (
        start "" "%LOCALAPPDATA%\Programs\DockerDesktop\Docker Desktop.exe"
    )
    echo Docker hazir olana kadar bekleniyor (ilk acilista 1-2 dakika)...
    for /l %%i in (1,1,30) do (
        timeout /t 5 /nobreak >nul
        docker info >nul 2>nul
        if not errorlevel 1 goto motor_hazir
    )
    echo [HATA] Docker motoru baslatilamadi. Docker Desktop'u elle acip tekrar deneyin.
    pause
    exit /b 1
)

:motor_hazir

REM 3) Konteynerleri baslat (ilk kurulumda imajlar derlenir)
echo Konteynerler baslatiliyor...
docker compose up -d
if errorlevel 1 (
    echo [HATA] Konteynerler baslatilamadi. Yukaridaki hatayi kontrol edin.
    pause
    exit /b 1
)

REM 4) Panelin acilmasini bekle
echo Panel acilana kadar bekleniyor...
timeout /t 6 /nobreak >nul

REM 5) Tarayiciyi ac
start "" "http://localhost:8501"

echo.
echo ============================================
echo   Panel hazir: http://localhost:8501
echo   Varsayilan giris: admin / admin123
echo   (.env olusturmadiysaniz varsayilan gecerli)
echo.
echo   Kapatmak icin: docker compose down
echo ============================================
pause
