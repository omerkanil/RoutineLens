@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0.."

title RoutineLens Ajan

REM --- Varsayilanlar ---
set "SUNUCU=http://127.0.0.1:8000"
set "KULLANICI=genel"

REM --- ajan_ayarlar.txt oku ---
if exist "ajan_ayarlar.txt" (
  for /f "usebackq tokens=1,* delims==" %%A in ("ajan_ayarlar.txt") do (
    if /i "%%A"=="SUNUCU" set "SUNUCU=%%B"
    if /i "%%A"=="KULLANICI" set "KULLANICI=%%B"
  )
)

REM --- Python secimi ---
set "PY=venv\Scripts\python.exe"
if not exist "%PY%" set "PY=python"

echo Sunucu   : %SUNUCU%
echo Kullanici: %KULLANICI%
echo.
echo Kamera penceresi aciliyor... Kapatmak icin pencereye tiklayip "q" tusuna basin.

"%PY%" main.py --kullanici "%KULLANICI%" --sunucu "%SUNUCU%"

echo.
echo Ajan durdu.
pause
