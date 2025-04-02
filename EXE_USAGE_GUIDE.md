# HISAABSETU Executable Version Usage Guide

## Overview

This guide explains how to build and use the executable version of HISAABSETU, which allows you to run the application without installing Python or any dependencies. The executable version is perfect for use on pendrives/USB drives and for easy distribution to users who don't have technical knowledge.

## Building the Executable

### Prerequisites
- Windows operating system
- Python installed (temporary, only needed for building)
- All HISAABSETU files (app.py, database.py, etc.)

### Steps to Build the Executable

1. Run the `BUILD_EXE.bat` file by double-clicking it
2. Wait for the build process to complete (this may take several minutes)
3. Once complete, a folder named `HISAABSETU_Distribution` will be created
4. This folder contains everything needed to run HISAABSETU independently

## Using the Executable

### On a Computer
1. Navigate to the `HISAABSETU_Distribution` folder
2. Double-click the `HISAABSETU.exe` file
3. The application will start and automatically open in your web browser
4. All data is stored in the `data` folder within the distribution directory

### On a Pendrive/USB Drive
1. Copy the entire `HISAABSETU_Distribution` folder to your pendrive
2. When inserting the pendrive into a Windows computer, the application may auto-launch (depending on Windows autorun settings)
3. If it doesn't auto-launch, navigate to the pendrive and double-click `HISAABSETU.exe`
4. All data will be stored on the pendrive itself, making it fully portable

## Auto-Start Feature

The executable version includes an auto-start feature that will:
- Automatically launch when inserted into a computer (if Windows autorun is enabled)
- Open the application in the default web browser
- Initialize the database if it doesn't exist

## Important Notes

1. **Data Storage**: All data is stored in the `data` folder next to the executable. Make sure this folder is not deleted.

2. **Windows Security**: Some Windows security settings may block autorun features or the execution of programs from external drives. Users may need to manually run the executable in these cases.

3. **First-Time Initialization**: The first time you run the application, it may take a little longer to start as it initializes the database.

4. **Backup**: Regularly back up the `data` folder to prevent data loss.

## Troubleshooting

If the application doesn't start:
1. Make sure the `data` folder exists in the same directory as the executable
2. Try running the executable as administrator
3. Check if your antivirus software is blocking the application
4. If all else fails, refer to the original HISAABSETU setup instructions