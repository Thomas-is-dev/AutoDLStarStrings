@echo off
setlocal
cd /d "%~dp0.."

if not exist ".venv\Scripts\python.exe" (
    py -3 -m venv .venv
    if errorlevel 1 goto :error
)

".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto :error

echo.
call :msg bat_venv_ready "Virtual environment ready in .venv"
if /i not "%~1"=="nopause" pause
exit /b 0

:error
echo.
call :msg bat_setup_check "Setup failed. Check that Python 3 is installed and available through py."
if /i not "%~1"=="nopause" pause
exit /b 1

:msg
py -3 "src\i18n.py" %1 2>nul
if errorlevel 1 echo %~2
exit /b 0
