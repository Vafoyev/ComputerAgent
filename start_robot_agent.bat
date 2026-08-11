@echo off
title JARVIS & Humanoid Robot Controller Service
echo ============================================================
echo   JARVIS - Gumanoid Robot & Windows Command Controller
echo ============================================================
echo.

cd /d "%~dp0"

if "%GEMINI_API_KEY%"=="" (
    echo [!] Eslatma: GEMINI_API_KEY o'zgaruvchisi o'rnatilmagan.
    echo [!] Server fallback rejimida va REST API tayyor holatda ishlaydi.
    echo.
)

echo [1/2] Virtuall muhit va bog'liqliklar tekshirilmoqda...
if exist "venv\Scripts\python.exe" (
    echo [OK] Python venv topildi.
    echo [2/2] Servis ishga tushirilmoqda (http://127.0.0.1:5000)...
    echo.
    .\venv\Scripts\python.exe app.py
) else (
    echo [OK] Tizim Python-i ishlatilmoqda.
    echo [2/2] Servis ishga tushirilmoqda (http://127.0.0.1:5000)...
    echo.
    python app.py
)

pause
