#!/usr/bin/env python3
"""
Build script for creating HISAABSETU executable
This script creates a Windows executable (.exe) for the HISAABSETU application
"""

import os
import sys
import shutil
import subprocess
from datetime import datetime

def print_header(text):
    """Print formatted header text"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def copy_to_output(output_dir):
    """Copy additional files to the output directory"""
    # Ensure the data directory exists
    os.makedirs(os.path.join(output_dir, "data"), exist_ok=True)
    
    # Ensure .streamlit config directory exists
    os.makedirs(os.path.join(output_dir, ".streamlit"), exist_ok=True)
    
    # Copy necessary files
    files_to_copy = [
        "app.py",
        "database.py",
        "calculations.py",
        "utils.py",
        "check_db.py",
        "generated-icon.png",
        "README.md"
    ]
    
    for file in files_to_copy:
        if os.path.exists(file):
            shutil.copy2(file, output_dir)
            print(f"Copied {file} to {output_dir}")
    
    # Copy .streamlit directory contents
    streamlit_dir = ".streamlit"
    if os.path.exists(streamlit_dir) and os.path.isdir(streamlit_dir):
        streamlit_output = os.path.join(output_dir, ".streamlit")
        for item in os.listdir(streamlit_dir):
            s = os.path.join(streamlit_dir, item)
            d = os.path.join(streamlit_output, item)
            if os.path.isfile(s):
                shutil.copy2(s, d)
                print(f"Copied {s} to {d}")
    
    # Create a basic README.txt file with instructions
    with open(os.path.join(output_dir, "README.txt"), "w") as f:
        f.write("HISAABSETU - Accounting Software\n")
        f.write("=" * 40 + "\n\n")
        f.write("To start the application, simply double-click the HISAABSETU.exe file.\n")
        f.write("The application will open in your default web browser automatically.\n\n")
        f.write("All data is stored in the 'data' folder next to the executable.\n")
        f.write("Make regular backups of this folder to prevent data loss.\n\n")
        f.write(f"Built on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

def main():
    """Main build function"""
    print_header("HISAABSETU - Executable Builder")
    
    # Define the output directory
    output_dir = "HISAABSETU_Distribution"
    
    # If the directory already exists, remove it
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    
    # Create the output directory
    os.makedirs(output_dir)
    
    # Run PyInstaller
    try:
        # Build the command
        cmd = [
            "pyinstaller",
            "--clean",
            "--onefile",
            "--windowed",
            f"--icon=generated-icon.png",
            "--name=HISAABSETU",
            "--add-data=app.py;.",
            "--add-data=calculations.py;.",
            "--add-data=database.py;.",
            "--add-data=utils.py;.",
            "--add-data=check_db.py;.",
            "--add-data=data;data",
            "--add-data=.streamlit;.streamlit",
            "--hidden-import=streamlit",
            "--hidden-import=pandas",
            "--hidden-import=openpyxl",
            "--hidden-import=sqlite3",
            "--hidden-import=trafilatura",
            "--hidden-import=twilio",
            "exe_builder/hisaabsetu_launcher.py"
        ]
        
        # Run the command
        subprocess.run(cmd, check=True)
        
        # Copy the executable to the output directory
        if os.path.exists(os.path.join("dist", "HISAABSETU.exe")):
            shutil.copy2(os.path.join("dist", "HISAABSETU.exe"), output_dir)
            print(f"Copied HISAABSETU.exe to {output_dir}")
        
        # Copy additional files
        copy_to_output(output_dir)
        
        # Clean up PyInstaller build files
        if os.path.exists("build"):
            shutil.rmtree("build")
        if os.path.exists("dist"):
            shutil.rmtree("dist")
        if os.path.exists("HISAABSETU.spec"):
            os.remove("HISAABSETU.spec")
        
        print_header("Build Successful!")
        print(f"The executable and required files are in: {output_dir}")
        print("You can distribute this folder to users or copy it to a pendrive.")
        
    except subprocess.CalledProcessError as e:
        print(f"Error running PyInstaller: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error during build process: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()