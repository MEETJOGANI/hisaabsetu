# How to Create HISAABSETU Executable (.exe)

This guide provides step-by-step instructions to create a standalone executable (.exe) file for HISAABSETU that can be run on any Windows computer without needing to install Python or any other dependencies.

## Prerequisites

Before you begin, make sure you have:
- A Windows computer
- Python installed (Python 3.8 or later)
- All the HISAABSETU files from this project

## Step 1: Install Required Python Packages

Open Command Prompt as Administrator and run the following commands:

```
pip install pyinstaller
pip install streamlit pandas openpyxl trafilatura twilio
```

## Step 2: Use the Provided Build Files

1. Copy all the files from this project to your computer
2. Double-click the `BUILD_EXE.bat` file
3. Wait for the build process to complete (this may take several minutes)
4. When complete, you'll find a folder named `HISAABSETU_Distribution` containing your executable

## Step 3: Test Your Executable

1. Navigate to the `HISAABSETU_Distribution` folder
2. Double-click `HISAABSETU.exe`
3. The application should start and open in your web browser

## Step 4: Move to Pendrive (Optional)

1. Copy the entire `HISAABSETU_Distribution` folder to your pendrive
2. Test by inserting the pendrive into a different computer
3. The application should either auto-launch or be runnable by double-clicking the executable

## Manual Build Instructions (If the Batch File Doesn't Work)

If the provided batch file doesn't work, you can manually build the executable with these steps:

1. Open Command Prompt
2. Navigate to the folder containing all HISAABSETU files
3. Run the following command:

```
pyinstaller --clean --onefile --windowed --icon=generated-icon.png --name HISAABSETU --add-data "app.py;." --add-data "calculations.py;." --add-data "database.py;." --add-data "utils.py;." --add-data "check_db.py;." --add-data "data;data" --add-data ".streamlit;.streamlit" --hidden-import streamlit --hidden-import pandas --hidden-import openpyxl --hidden-import sqlite3 --hidden-import trafilatura --hidden-import twilio hisaabsetu_launcher.py
```

4. The executable will be created in the `dist` folder

## Troubleshooting

If you encounter issues during building:
- Make sure all required packages are installed
- Try running Command Prompt as Administrator
- Ensure all project files are in the same directory

If the executable doesn't run:
- Check Windows Defender or your antivirus software (they might block the executable)
- Try running the executable as Administrator
- Make sure all required files were included in the build

## Notes

- The executable includes all dependencies, making it larger in size but completely portable
- All data will be stored in the `data` directory next to the executable
- When used on a pendrive, the application will automatically attempt to launch when the pendrive is inserted (if Windows autorun is enabled)