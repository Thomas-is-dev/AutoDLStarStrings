@echo off
setlocal
cd /d "%~dp0.."

if not exist ".venv\Scripts\python.exe" (
    call "scripts\setup_venv.bat" nopause
    if errorlevel 1 goto :error
)

".venv\Scripts\python.exe" "scripts\build_exe.py"
if errorlevel 1 goto :error

echo.
pause
exit /b 0

:error
echo.
echo Build failed.
pause
exit /b 1
