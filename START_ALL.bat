@echo off
title Churn Tahmin - Servis Baslatici
color 0A
cls

echo ============================================================
echo   CALISANLAR CHURN TAHMIN SISTEMi - TUM SERViSLER
echo ============================================================
echo.

set "PROJE=%~dp0"
set "PGBIN=C:\Program Files\PostgreSQL\16\bin"
set "PGDATA=C:\Program Files\PostgreSQL\16\data"
set "BACKEND=%PROJE%backend"
set "FRONTEND=%PROJE%frontend"
set "N8N=%PROJE%n8n"
set "NODE20=C:\node20"

REM ---- 1. PostgreSQL ----
echo [1/4] PostgreSQL baslatiliyor...
"%PGBIN%\pg_isready.exe" -h 127.0.0.1 -p 5432 >nul 2>&1
if %errorlevel%==0 (
    echo       PostgreSQL zaten calisiyor. [ATILDI]
) else (
    REM postmaster.pid varsa temizle
    if exist "%PGDATA%\postmaster.pid" (
        echo       Eski PID dosyasi temizleniyor...
        del /f "%PGDATA%\postmaster.pid"
    )
    start "PostgreSQL 16" /min cmd /c ""%PGBIN%\pg_ctl.exe" start -D "%PGDATA%" -l "%PGDATA%\pg_log\startup.log" && pause"
    echo       PostgreSQL baslatma komutu gonderildi.
    timeout /t 4 /nobreak >nul
)

REM ---- 2. FastAPI Backend ----
echo [2/4] FastAPI backend baslatiliyor...
netstat -an | findstr ":8000 " | findstr LISTEN >nul 2>&1
if %errorlevel%==0 (
    echo       Backend zaten calisiyor. [ATILDI]
) else (
    start "FastAPI Backend" cmd /k "cd /d "%BACKEND%" && call venv\Scripts\activate.bat && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
    echo       Backend penceresi acildi.
    timeout /t 3 /nobreak >nul
)

REM ---- 3. React Frontend ----
echo [3/4] React frontend baslatiliyor...
netstat -an | findstr ":5173 " | findstr LISTEN >nul 2>&1
if %errorlevel%==0 (
    echo       Frontend zaten calisiyor. [ATILDI]
) else (
    start "React Frontend" cmd /k "cd /d "%FRONTEND%" && npm run dev"
    echo       Frontend penceresi acildi.
    timeout /t 2 /nobreak >nul
)

REM ---- 4. n8n ----
echo [4/4] n8n baslatiliyor...
netstat -an | findstr ":5678 " | findstr LISTEN >nul 2>&1
if %errorlevel%==0 (
    echo       n8n zaten calisiyor. [ATILDI]
) else (
    start "n8n Workflow" cmd /k "cd /d "%N8N%" && SET PATH=%NODE20%;%NODE20%\node_modules\.bin;%PATH% && SET N8N_PORT=5678 && SET N8N_BASIC_AUTH_ACTIVE=false && SET N8N_SKIP_WEBHOOK_DEREGISTRATION_SHUTDOWN=true && SET N8N_USER_FOLDER=%N8N%\.n8n_data && node "%NODE20%\node_modules\n8n\bin\n8n" start"
    echo       n8n penceresi acildi.
)

echo.
echo ============================================================
echo   Servisler baslatiliyor, hazir olmasi icin bekleniyor...
echo ============================================================
timeout /t 8 /nobreak >nul

echo.
echo Durum kontrolu:
echo.

REM ---- Durum Kontrolu ----
"%PGBIN%\pg_isready.exe" -h 127.0.0.1 -p 5432 >nul 2>&1
if %errorlevel%==0 (echo   [OK]  PostgreSQL    - http://127.0.0.1:5432) else (echo   [!!]  PostgreSQL    - BASLAMADI, log: "%PGDATA%\pg_log\startup.log")

powershell -Command "try { $r=(New-Object Net.WebClient).DownloadString('http://127.0.0.1:8000/health'); Write-Host '  [OK]  FastAPI       - http://127.0.0.1:8000' } catch { Write-Host '  [!!]  FastAPI       - BASLAMADI (biraz daha bekle)' }" 2>nul

powershell -Command "try { $r=(New-Object Net.WebClient).DownloadString('http://localhost:5173'); Write-Host '  [OK]  React UI      - http://localhost:5173' } catch { Write-Host '  [!!]  React UI      - BASLAMADI (biraz daha bekle)' }" 2>nul

powershell -Command "try { $r=(New-Object Net.WebClient).DownloadString('http://localhost:5678/healthz'); Write-Host '  [OK]  n8n           - http://localhost:5678' } catch { Write-Host '  [!!]  n8n           - BASLAMADI (biraz daha bekle)' }" 2>nul

echo.
echo ============================================================
echo   TUM SERViSLER HAZIR!
echo.
echo   React  UI  : http://localhost:5173
echo   API Docs   : http://127.0.0.1:8000/docs
echo   n8n Panel  : http://localhost:5678
echo              : admin@churn.local / Admin1234!
echo ============================================================
echo.
pause
