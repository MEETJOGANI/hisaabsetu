@echo off
echo ====================================================
echo           HISAABSETU ACCOUNTING SOFTWARE
echo ====================================================
echo.
echo Starting HISAABSETU application...
echo.
echo Once the server starts, please access the application at:
echo http://localhost:5000 or http://127.0.0.1:5000
echo.
echo If the browser doesn't open automatically, please copy and
echo paste one of these addresses into your web browser.
echo.
echo Note: Do NOT use 0.0.0.0:5000 as the address.
echo.
echo Press Ctrl+C to stop the application when done.
echo ====================================================
echo.

:: Get current directory
cd /d %~dp0

:: Check if Python is in PATH
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python not found in PATH. Looking for Python in the WinPython directory...
    if exist WinPython\python.exe (
        set PYTHON_PATH=WinPython\python.exe
    ) else if exist WinPython\python-3.9*\python.exe (
        set PYTHON_PATH=WinPython\python-3.9*\python.exe
    ) else if exist WinPython\python-3.10*\python.exe (
        set PYTHON_PATH=WinPython\python-3.10*\python.exe
    ) else (
        echo Python not found. Please install Python first.
        pause
        exit /b 1
    )
) else (
    set PYTHON_PATH=python
)

:: Run Streamlit app
%PYTHON_PATH% -m streamlit run app.py --server.port 5000 --server.address 127.0.0.1

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ====================================================
    echo Error running the application. 
    echo Please make sure Streamlit is installed by running:
    echo %PYTHON_PATH% -m pip install streamlit pandas openpyxl trafilatura
    echo ====================================================
    pause
)

pause