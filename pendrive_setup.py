#!/usr/bin/env python3
"""
HISAABSETU Pendrive Setup Script

This script helps users set up the HISAABSETU application on their pendrive.
It creates the necessary directory structure and files needed for portable operation.
"""

import os
import sys
import shutil
import zipfile
import subprocess
import urllib.request
from datetime import datetime

def print_header(message):
    """Print a formatted header message"""
    print("\n" + "=" * 60)
    print(f" {message}")
    print("=" * 60)

def print_step(message):
    """Print a step message"""
    print(f"\n>> {message}")

def check_if_running_on_pendrive():
    """Check if the script is running from a pendrive"""
    # This is a basic check that might work on Windows
    try:
        drive_letter = os.path.splitdrive(os.path.abspath(__file__))[0]
        if drive_letter.upper() != "C:":  # Assuming C: is the main drive
            print_step(f"Detected running from drive {drive_letter} - likely a pendrive!")
            return True
        else:
            print_step("This script appears to be running from your main drive, not a pendrive.")
            return False
    except Exception:
        print_step("Could not determine if running from pendrive.")
        return False

def create_directory_structure():
    """Create the necessary directory structure for HISAABSETU"""
    print_step("Creating directory structure...")
    
    # Get the base directory (where this script is located)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create directories
    directories = [
        os.path.join(base_dir, "HISAABSETU"),
        os.path.join(base_dir, "HISAABSETU", "data"),
        os.path.join(base_dir, "HISAABSETU", "data", "backups"),
        os.path.join(base_dir, "HISAABSETU", ".streamlit")
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"  Created: {directory}")
        else:
            print(f"  Already exists: {directory}")
    
    return base_dir

def create_startup_script(base_dir):
    """Create the startup batch script for Windows"""
    print_step("Creating startup script...")
    
    # Create the batch file
    startup_script_path = os.path.join(base_dir, "START_HISAABSETU.bat")
    
    script_content = """@echo off
setlocal

rem Get the drive letter of the USB drive
set "DRIVE=%~d0"
set "APP_PATH=%~dp0HISAABSETU"
set "PYTHON_PATH=%APP_PATH%\\WinPython\\python"

rem Activate Python environment
call "%PYTHON_PATH%\\Scripts\\activate.bat"

rem Set environment variables
set "PYTHONPATH=%APP_PATH%"
set "STREAMLIT_HOME=%APP_PATH%\\.streamlit"
set "PATH=%PYTHON_PATH%;%PATH%"

rem Navigate to the app directory
cd /d "%APP_PATH%"

rem Run the setup script if first time
if not exist "%APP_PATH%\\data\\hisaabsetu.db" (
    echo First time setup - Installing dependencies...
    python setup.py
)

rem Run HISAABSETU application
echo Starting HISAABSETU...
echo The application will open in your browser at http://localhost:5000
echo If it doesn't open automatically, please go to http://localhost:5000 manually
python -m streamlit run app.py --server.port 5000 --server.headless true

rem Keep the window open if there's an error
if %ERRORLEVEL% NEQ 0 (
    echo Error encountered. Press any key to exit.
    pause
)

endlocal
"""
    
    with open(startup_script_path, "w") as file:
        file.write(script_content)
    
    print(f"  Created: {startup_script_path}")
    return startup_script_path

def create_config_file(base_dir):
    """Create the Streamlit config file"""
    print_step("Creating Streamlit configuration...")
    
    config_dir = os.path.join(base_dir, "HISAABSETU", ".streamlit")
    config_path = os.path.join(config_dir, "config.toml")
    
    config_content = """
[server]
headless = true
address = "127.0.0.1"
port = 5000
baseUrlPath = ""
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#E694FF"
backgroundColor = "#00172B"
secondaryBackgroundColor = "#0083B8"
textColor = "#FFFFFF"
font = "sans-serif"
"""
    
    with open(config_path, "w") as file:
        file.write(config_content)
    
    print(f"  Created: {config_path}")

def download_portable_python(base_dir):
    """
    Download the portable Python distribution (WinPython)
    This is just a placeholder - in a real implementation, you would 
    download the actual WinPython package and extract it
    """
    print_step("Downloading portable Python environment...")
    print("  This step requires internet connection.")
    print("  Please download WinPython from https://winpython.github.io/")
    print("  and extract it to the HISAABSETU folder on your pendrive.")
    print("  Recommended version: WinPython 3.9+ (64-bit)")
    
    # In a real implementation, you might download and extract WinPython automatically
    # For example:
    # url = "https://github.com/winpython/winpython/releases/download/4.3.20210620/Winpython64-3.9.5.0.exe"
    # download_path = os.path.join(base_dir, "winpython_installer.exe")
    # urllib.request.urlretrieve(url, download_path)
    # Then run the installer or extract the files

def copy_application_files(base_dir):
    """
    Copy application files to the HISAABSETU directory
    This assumes the repository files are in the current directory
    """
    print_step("Copying application files...")
    
    # Source and destination paths
    source_dir = os.path.dirname(os.path.abspath(__file__))
    dest_dir = os.path.join(base_dir, "HISAABSETU")
    
    # Files to copy
    files_to_copy = [
        "app.py",
        "calculations.py",
        "database.py",
        "utils.py",
        "setup.py",
        "PENDRIVE_INSTALLATION.md",
        "README.md" # if exists
    ]
    
    for file in files_to_copy:
        source_file = os.path.join(source_dir, file)
        dest_file = os.path.join(dest_dir, file)
        
        if os.path.exists(source_file):
            shutil.copy2(source_file, dest_file)
            print(f"  Copied: {file}")
        else:
            print(f"  Warning: File {file} not found, skipping.")

def main():
    """Main setup function"""
    print_header("HISAABSETU Pendrive Setup")
    print("\nThis script will set up HISAABSETU as a portable application on your pendrive.")
    
    # Check if running from pendrive
    is_pendrive = check_if_running_on_pendrive()
    if not is_pendrive:
        proceed = input("Continue anyway? (y/n): ").lower().strip()
        if proceed != 'y':
            print("Setup cancelled.")
            return
    
    # Create directory structure
    base_dir = create_directory_structure()
    
    # Create startup script
    startup_script = create_startup_script(base_dir)
    
    # Create Streamlit config
    create_config_file(base_dir)
    
    # Copy application files
    copy_application_files(base_dir)
    
    # Download portable Python (or instruct user to download)
    download_portable_python(base_dir)
    
    # Final instructions
    print_header("Setup Complete!")
    print("\nTo complete the setup:")
    print("1. Download WinPython from https://winpython.github.io/")
    print("2. Extract it to the 'HISAABSETU' folder on your pendrive")
    print("3. Rename the extracted folder to 'WinPython'")
    print("4. Double-click the 'START_HISAABSETU.bat' file to run the application")
    
    print("\nYour HISAABSETU portable application is ready to use!")
    print(f"Startup script: {startup_script}")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()