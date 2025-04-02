@echo off
echo ====================================================
echo      HISAABSETU PENDRIVE SETUP INSTALLATION
echo ====================================================
echo.

:: Get current drive letter
set DRIVE=%~d0
set APP_PATH=%~dp0

echo Setting up HISAABSETU on %DRIVE% drive
echo.

:: Check if Python is available
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python not found. Checking if portable Python is available...
    
    if exist %APP_PATH%\WinPython\python.exe (
        echo Found portable Python in the WinPython folder.
        set PYTHON_PATH=%APP_PATH%\WinPython\python.exe
    ) else if exist %APP_PATH%\WinPython\python-3.9*\python.exe (
        echo Found portable Python in the WinPython\python-3.9 folder.
        set PYTHON_PATH=%APP_PATH%\WinPython\python-3.9*\python.exe
    ) else if exist %APP_PATH%\WinPython\python-3.10*\python.exe (
        echo Found portable Python in the WinPython\python-3.10 folder.
        set PYTHON_PATH=%APP_PATH%\WinPython\python-3.10*\python.exe
    ) else (
        echo.
        echo ====================================================
        echo ERROR: Python not found!
        echo.
        echo Please install WinPython to the WinPython folder:
        echo 1. Download WinPython from https://winpython.github.io/
        echo 2. Extract it to the %DRIVE% drive as "WinPython" folder
        echo ====================================================
        echo.
        pause
        exit /b 1
    )
) else (
    set PYTHON_PATH=python
)

echo Using Python: %PYTHON_PATH%
echo.

:: Create necessary directories
echo Creating directory structure...
if not exist %APP_PATH%\data (
    mkdir %APP_PATH%\data
    echo Created data directory
)

if not exist %APP_PATH%\data\backups (
    mkdir %APP_PATH%\data\backups
    echo Created backups directory
)

if not exist %APP_PATH%\.streamlit (
    mkdir %APP_PATH%\.streamlit
    echo Created .streamlit directory
)

:: Create streamlit config
echo Creating Streamlit configuration...
echo [server]> %APP_PATH%\.streamlit\config.toml
echo headless = true>> %APP_PATH%\.streamlit\config.toml
echo address = "127.0.0.1">> %APP_PATH%\.streamlit\config.toml
echo port = 5000>> %APP_PATH%\.streamlit\config.toml
echo baseUrlPath = "">> %APP_PATH%\.streamlit\config.toml
echo enableCORS = false>> %APP_PATH%\.streamlit\config.toml
echo enableXsrfProtection = false>> %APP_PATH%\.streamlit\config.toml
echo.>> %APP_PATH%\.streamlit\config.toml
echo [browser]>> %APP_PATH%\.streamlit\config.toml
echo gatherUsageStats = false>> %APP_PATH%\.streamlit\config.toml
echo.>> %APP_PATH%\.streamlit\config.toml
echo [theme]>> %APP_PATH%\.streamlit\config.toml
echo primaryColor = "#1E88E5">> %APP_PATH%\.streamlit\config.toml
echo backgroundColor = "#0E1117">> %APP_PATH%\.streamlit\config.toml
echo secondaryBackgroundColor = "#262730">> %APP_PATH%\.streamlit\config.toml
echo textColor = "#FAFAFA">> %APP_PATH%\.streamlit\config.toml
echo font = "sans-serif">> %APP_PATH%\.streamlit\config.toml
echo Config file created.

:: Install required packages
echo.
echo Installing required packages...
%PYTHON_PATH% -m pip install streamlit pandas openpyxl trafilatura --quiet
if %ERRORLEVEL% NEQ 0 (
    echo Failed to install required packages. Please check your Python installation.
    pause
    exit /b 1
)
echo Packages installed successfully.

:: Check if setup.py exists and run it
if exist %APP_PATH%\setup.py (
    echo.
    echo Running initial setup script...
    %PYTHON_PATH% %APP_PATH%\setup.py
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to run setup.py. Please check for errors.
        pause
        exit /b 1
    )
    echo Initial setup completed.
)

:: Create desktop shortcut
echo.
echo Creating shortcut file...
echo @echo off> %APP_PATH%\START_HISAABSETU.bat
echo echo ====================================================>> %APP_PATH%\START_HISAABSETU.bat
echo echo           HISAABSETU ACCOUNTING SOFTWARE>> %APP_PATH%\START_HISAABSETU.bat
echo echo ====================================================>> %APP_PATH%\START_HISAABSETU.bat
echo echo.>> %APP_PATH%\START_HISAABSETU.bat
echo echo Starting HISAABSETU application...>> %APP_PATH%\START_HISAABSETU.bat
echo echo.>> %APP_PATH%\START_HISAABSETU.bat
echo echo Once the server starts, please access the application at:>> %APP_PATH%\START_HISAABSETU.bat
echo echo http://localhost:5000 or http://127.0.0.1:5000>> %APP_PATH%\START_HISAABSETU.bat
echo echo.>> %APP_PATH%\START_HISAABSETU.bat
echo echo If the browser doesn't open automatically, please copy and>> %APP_PATH%\START_HISAABSETU.bat
echo echo paste one of these addresses into your web browser.>> %APP_PATH%\START_HISAABSETU.bat
echo echo.>> %APP_PATH%\START_HISAABSETU.bat
echo echo Note: Do NOT use 0.0.0.0:5000 as the address.>> %APP_PATH%\START_HISAABSETU.bat
echo echo.>> %APP_PATH%\START_HISAABSETU.bat
echo echo Press Ctrl+C to stop the application when done.>> %APP_PATH%\START_HISAABSETU.bat
echo echo ====================================================>> %APP_PATH%\START_HISAABSETU.bat
echo echo.>> %APP_PATH%\START_HISAABSETU.bat
echo.>> %APP_PATH%\START_HISAABSETU.bat
echo cd /d %APP_PATH%>> %APP_PATH%\START_HISAABSETU.bat
echo.>> %APP_PATH%\START_HISAABSETU.bat
echo :: Check if Python is in PATH>> %APP_PATH%\START_HISAABSETU.bat
echo python --version ^>nul 2^>^&1>> %APP_PATH%\START_HISAABSETU.bat
echo if %%ERRORLEVEL%% NEQ 0 (>> %APP_PATH%\START_HISAABSETU.bat
echo     echo Python not found in PATH. Looking for Python in the WinPython directory...>> %APP_PATH%\START_HISAABSETU.bat
echo     if exist WinPython\python.exe (>> %APP_PATH%\START_HISAABSETU.bat
echo         set PYTHON_PATH=WinPython\python.exe>> %APP_PATH%\START_HISAABSETU.bat
echo     ^) else if exist WinPython\python-3.9*\python.exe (>> %APP_PATH%\START_HISAABSETU.bat
echo         set PYTHON_PATH=WinPython\python-3.9*\python.exe>> %APP_PATH%\START_HISAABSETU.bat
echo     ^) else if exist WinPython\python-3.10*\python.exe (>> %APP_PATH%\START_HISAABSETU.bat
echo         set PYTHON_PATH=WinPython\python-3.10*\python.exe>> %APP_PATH%\START_HISAABSETU.bat
echo     ^) else (>> %APP_PATH%\START_HISAABSETU.bat
echo         echo Python not found. Please install Python first.>> %APP_PATH%\START_HISAABSETU.bat
echo         pause>> %APP_PATH%\START_HISAABSETU.bat
echo         exit /b 1>> %APP_PATH%\START_HISAABSETU.bat
echo     ^)>> %APP_PATH%\START_HISAABSETU.bat
echo ^) else (>> %APP_PATH%\START_HISAABSETU.bat
echo     set PYTHON_PATH=python>> %APP_PATH%\START_HISAABSETU.bat
echo ^)>> %APP_PATH%\START_HISAABSETU.bat
echo.>> %APP_PATH%\START_HISAABSETU.bat
echo :: Run Streamlit app>> %APP_PATH%\START_HISAABSETU.bat
echo %%PYTHON_PATH%% -m streamlit run app.py --server.port 5000 --server.address 127.0.0.1>> %APP_PATH%\START_HISAABSETU.bat
echo.>> %APP_PATH%\START_HISAABSETU.bat
echo if %%ERRORLEVEL%% NEQ 0 (>> %APP_PATH%\START_HISAABSETU.bat
echo     echo.>> %APP_PATH%\START_HISAABSETU.bat
echo     echo ====================================================>> %APP_PATH%\START_HISAABSETU.bat
echo     echo Error running the application. >> %APP_PATH%\START_HISAABSETU.bat
echo     echo Please make sure Streamlit is installed by running:>> %APP_PATH%\START_HISAABSETU.bat
echo     echo %%PYTHON_PATH%% -m pip install streamlit pandas openpyxl trafilatura>> %APP_PATH%\START_HISAABSETU.bat
echo     echo ====================================================>> %APP_PATH%\START_HISAABSETU.bat
echo     pause>> %APP_PATH%\START_HISAABSETU.bat
echo ^)>> %APP_PATH%\START_HISAABSETU.bat
echo.>> %APP_PATH%\START_HISAABSETU.bat
echo pause>> %APP_PATH%\START_HISAABSETU.bat
echo Shortcut file created.

echo.
echo ====================================================
echo HISAABSETU Pendrive Setup Complete!
echo.
echo To start the application:
echo 1. Double-click on START_HISAABSETU.bat
echo 2. Open your browser to http://localhost:5000 if it doesn't open automatically
echo ====================================================
echo.

pause