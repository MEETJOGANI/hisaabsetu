@echo off
echo ============================================================
echo   HISAABSETU - Executable Builder
echo ============================================================
echo.

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Python is not installed or not in PATH.
    echo Please install Python 3.8 or higher before continuing.
    echo.
    pause
    exit /b 1
)

echo Checking Python packages...
python -m pip install --quiet --upgrade pip
python -m pip install --quiet pyinstaller streamlit pandas openpyxl trafilatura twilio

echo.
echo Building executable with PyInstaller...
python build_exe.py

if %ERRORLEVEL% neq 0 (
    echo.
    echo ============================================================
    echo   Error building executable. Please check the output above.
    echo ============================================================
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   Build complete! Your executable is in the HISAABSETU_Distribution folder.
echo   See exe_builder\EXE_USAGE_GUIDE.md for usage instructions.
echo ============================================================
echo.
pause