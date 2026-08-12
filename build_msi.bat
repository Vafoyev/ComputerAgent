@echo off
title JARVIS MSI Installer Builder
echo ============================================================
echo   JARVIS NEURAL CORE - MSI INSTALLER BUILDER
echo ============================================================
echo.

cd /d "%~dp0"

if exist "venv\Scripts\python.exe" (
    .\venv\Scripts\python.exe build_msi.py
) else (
    python build_msi.py
)

echo.
pause
