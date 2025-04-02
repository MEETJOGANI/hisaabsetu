#!/usr/bin/env python
"""
Create autorun files for HISAABSETU pendrive distribution
This script creates the necessary files for auto-launching HISAABSETU from a pendrive
"""
import os
import sys

def create_autorun_files(output_dir="."):
    """Create autorun files in the specified directory"""
    # Create autorun.inf
    autorun_content = """[autorun]
open=HISAABSETU.exe
icon=HISAABSETU.exe
label=HISAABSETU Application
action=Run HISAABSETU Accounting Software
"""
    with open(os.path.join(output_dir, "autorun.inf"), "w") as f:
        f.write(autorun_content)
    print(f"Created autorun.inf in {output_dir}")
    
    # Create a desktop.ini for folder icon customization
    desktop_ini_content = """[.ShellClassInfo]
IconResource=HISAABSETU.exe,0
[ViewState]
Mode=
Vid=
FolderType=Generic
"""
    with open(os.path.join(output_dir, "desktop.ini"), "w") as f:
        f.write(desktop_ini_content)
    
    # Make desktop.ini hidden and system file for Windows to respect it
    try:
        import subprocess
        subprocess.run(["attrib", "+S", "+H", os.path.join(output_dir, "desktop.ini")])
        # Also make the directory itself a system folder
        subprocess.run(["attrib", "+S", output_dir])
    except:
        print("Note: Could not set file attributes. This is normal if not running on Windows.")
    
    print(f"Created desktop.ini in {output_dir}")
    
    print("Successfully created autorun files.")
    print("NOTE: Autorun functionality depends on Windows settings and may be disabled for security reasons.")
    print("      Users can always manually run HISAABSETU.exe from the pendrive.")

if __name__ == "__main__":
    # If a directory is provided as an argument, use it
    output_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    
    create_autorun_files(output_dir)