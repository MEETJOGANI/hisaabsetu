# HISAABSETU Pendrive Installation Guide

This guide will help you set up HISAABSETU as a portable application that runs directly from your pendrive/USB drive.

## Requirements

- A USB drive with at least 100MB of free space
- Windows 10/11 computer (for initial setup)
- Internet connection (only for initial setup)

## Installation Steps

### Step 1: Prepare Your USB Drive

1. Insert your USB drive into your computer
2. Format the USB drive if needed (backup any important files first)
3. Create a new folder called "HISAABSETU" on the USB drive

### Step 2: Install Portable Python

1. Download the portable version of Python from [WinPython](https://winpython.github.io/)
   - Select the latest WinPython 3.9+ or 3.10+ version (64-bit recommended)
2. Extract the downloaded WinPython package directly to your USB drive in the HISAABSETU folder
3. You should now have a folder structure like: `[USB Drive]/HISAABSETU/WinPython-XX`

### Step 3: Copy HISAABSETU Files

1. Download the HISAABSETU application files from the provided zip file or repository
2. Extract all files to the HISAABSETU folder on your USB drive
3. Make sure the following files and folders are included:
   - `app.py` - Main application file
   - `calculations.py` - Financial calculations
   - `database.py` - Database handling
   - `utils.py` - Utility functions
   - `setup.py` - Setup script
   - `data/` folder - Will store your database file
   - `.streamlit/` folder - Contains configuration

### Step 4: Use the Setup and Launch Scripts

HISAABSETU comes with two important batch files that handle setup and running the application:

1. **SETUP_PENDRIVE.bat** - First-time setup script that:
   - Creates the necessary folder structure
   - Sets up configuration files
   - Installs required Python packages
   - Creates the startup script

2. **START_HISAABSETU.bat** - The main startup script that:
   - Locates Python on your system or in the WinPython folder
   - Starts the HISAABSETU application with the correct parameters
   - Opens the application in your browser

Simply copy these files to the root of your USB drive along with the application files.

### Step 5: First-Time Setup

**Important:** When running HISAABSETU, always use the provided batch files instead of directly running Python commands!

1. Insert the USB drive into a Windows computer with internet access
2. Double-click the `START_HISAABSETU.bat` file
3. Wait for the first-time setup to complete (this will install required dependencies)
4. The HISAABSETU application should automatically launch in your default web browser

## Usage Instructions

1. To use HISAABSETU on any computer:
   - Insert your USB drive
   - Double-click the `START_HISAABSETU.bat` file
   - The application will open in your default web browser
   - The database file is stored on the USB drive in the `data` folder

2. Important notes:
   - All data is stored on the USB drive - no data is saved to the host computer
   - Always safely eject the USB drive when you're done using HISAABSETU
   - Regularly backup the `data` folder to prevent data loss
   - The application runs locally on port 5000 (http://localhost:5000 or http://127.0.0.1:5000)
   - **Important**: When the application starts, use `localhost:5000` in your browser, NOT `0.0.0.0:5000`

## Backup and Data Safety

1. To backup your data:
   - Navigate to the `[USB Drive]/HISAABSETU/data` folder
   - Copy the `hisaabsetu.db` file to a secure location
   - You can also use the built-in backup/restore function in the HISAABSETU Settings page

2. To restore from a backup:
   - Replace the `hisaabsetu.db` file in the `data` folder with your backup
   - Or use the restore function in the HISAABSETU Settings page

## Troubleshooting

If you encounter any issues:

1. Make sure you have administrator privileges on the computer
2. Check that no other application is using port 5000
3. Try running the setup.py script manually to reinstall dependencies:
   ```
   [USB Drive]/HISAABSETU/WinPython-XX/python-3.XX.X/python.exe setup.py
   ```
4. Ensure your USB drive has enough free space
5. Check that all required files are present on the USB drive

## System Requirements for Host Computers

- Windows 7/8/10/11 (64-bit recommended)
- 4GB RAM minimum
- Any modern web browser (Chrome, Firefox, Edge recommended)
- No installation required on the host computer
- No administrative privileges required (in most cases)