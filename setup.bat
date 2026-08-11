@echo off
title JARVIS & Humanoid Robot Setup
echo ============================================================
echo   JARVIS - O'rnatish va Sozlash Dasturi
echo ============================================================
echo.

cd /d "%~dp0"

echo [1/3] Python virtualenv yaratilmoqda...
python -m venv venv

echo [2/3] Kerakli kutubxonalar o'rnatilmoqda (requirements.txt)...
.\venv\Scripts\python.exe -m pip install --upgrade pip
.\venv\Scripts\pip.exe install -r requirements.txt

echo.
echo ============================================================
echo   [OK] O'rnatish muvaffaqiyatli yakunlandi!
echo   Servisni ishga tushirish uchun "start_robot_agent.bat" faylini bosing.
echo ============================================================
echo.
pause
