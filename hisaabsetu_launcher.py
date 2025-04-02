#!/usr/bin/env python3
"""
HISAABSETU Application Launcher
This script serves as the entry point for the HISAABSETU application executable.
It launches the Streamlit application with the appropriate settings.
"""

import os
import sys
import time
import webbrowser
import subprocess
import threading
from pathlib import Path

def ensure_data_dir():
    """Ensure data directory exists"""
    # When running as executable, look for data directory next to the executable
    if hasattr(sys, '_MEIPASS'):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Ensure data directory exists
    data_dir = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    
    # Ensure .streamlit config directory exists
    streamlit_dir = os.path.join(base_dir, ".streamlit")
    os.makedirs(streamlit_dir, exist_ok=True)
    
    # Create a default config.toml if it doesn't exist
    config_file = os.path.join(streamlit_dir, "config.toml")
    if not os.path.exists(config_file):
        with open(config_file, "w") as f:
            f.write("""
[server]
headless = true
port = 8501
address = "127.0.0.1"

[theme]
primaryColor = "#1E88E5"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#31333F"
font = "sans serif"
""")
    
    return base_dir

def open_browser(port):
    """Open browser after a short delay to ensure server is running"""
    time.sleep(2)  # Wait for Streamlit to start
    url = f"http://127.0.0.1:{port}"
    webbrowser.open(url)

def main():
    """Main entry point for the application"""
    # Ensure data directory exists
    base_dir = ensure_data_dir()
    
    # Determine the app.py location
    if hasattr(sys, '_MEIPASS'):
        # We're running as a PyInstaller bundle
        app_path = os.path.join(sys._MEIPASS, "app.py")
    else:
        # We're running as a script
        app_path = os.path.join(base_dir, "app.py")
    
    # Set up the port
    port = 8501
    
    # Start browser opening thread
    browser_thread = threading.Thread(target=open_browser, args=(port,))
    browser_thread.daemon = True
    browser_thread.start()
    
    # Start Streamlit with the app.py
    cmd = [
        "streamlit", "run",
        app_path,
        "--server.headless=true",
        f"--server.port={port}",
        "--server.address=127.0.0.1"
    ]
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("Application terminated by user")
    except Exception as e:
        print(f"Error running Streamlit: {e}")
        # Keep the console window open if there's an error
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()