@echo off
title AutoUpdate StarStrings
cd /d "%~dp0.."

if not exist ".venv\Scripts\python.exe" goto :setup

".venv\Scripts\python.exe" -c "import requests, dotenv" >nul 2>&1
if errorlevel 1 goto :setup

goto :run

:setup
call "scripts\setup_venv.bat" nopause
if errorlevel 1 goto :error

:run
".venv\Scripts\python.exe" "src\autoupdate.py" %*
set "exit_code=%errorlevel%"

echo.
call :msg bat_press_key "Press any key to close..."
pause > nul
exit /b %exit_code%

:error
echo.
call :msg bat_setup_failed "Unable to set up the virtual environment."
pause > nul
exit /b 1

:msg
rem Print a translated message (key %1), or the English fallback %2 if Python is unavailable
py -3 "src\i18n.py" %1 2>nul
if errorlevel 1 echo %~2
exit /b 0
