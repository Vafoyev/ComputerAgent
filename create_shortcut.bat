@echo off
title JARVIS Desktop Shortcut Creator
echo Creating Desktop Shortcut for JARVIS Controller...

set SCRIPT="%TEMP%\%RANDOM%-%RANDOM%-%RANDOM%-%RANDOM%.vbs"
set EXE_PATH=%~dp0dist\JARVIS_Robot_Controller\JARVIS_Robot_Controller.exe
set DESKTOP_PATH=%USERPROFILE%\Desktop\JARVIS Robot Controller.lnk

echo Set oWS = WScript.CreateObject("WScript.Shell") >> %SCRIPT%
echo sLinkFile = "%DESKTOP_PATH%" >> %SCRIPT%
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> %SCRIPT%
echo oLink.TargetPath = "%EXE_PATH%" >> %SCRIPT%
echo oLink.WorkingDirectory = "%~dp0dist\JARVIS_Robot_Controller" >> %SCRIPT%
echo oLink.Description = "JARVIS Neural Core Humanoid Robot Controller" >> %SCRIPT%
echo oLink.Save >> %SCRIPT%

cscript /nologo %SCRIPT%
del %SCRIPT%

echo [OK] Ish stolidagi yorliq (Desktop Shortcut) yaratildi!
echo Fayl: %DESKTOP_PATH%
pause
