#!/usr/bin/env python
import os
import sys
import subprocess
import platform

def print_header(message):
    """Print a formatted header message"""
    print("\n" + "=" * 60)
    print(f" {message}")
    print("=" * 60)

def is_tool_installed(name):
    """Check if a program is installed and available in the PATH"""
    try:
        devnull = open(os.devnull, 'w')
        subprocess.Popen([name], stdout=devnull, stderr=devnull).communicate()
        return True
    except OSError:
        return False

def install_python():
    """Check Python installation and display appropriate messages"""
    print_header("Checking Python Installation")
    
    if sys.version_info < (3, 7):
        print("Error: Python 3.7 or higher is required.")
        print(f"Current Python version: {platform.python_version()}")
        print("\nPlease install a compatible Python version from:")
        print("  https://www.python.org/downloads/")
        return False
    
    print(f"✓ Python {platform.python_version()} detected")
    return True

def install_dependencies():
    """Install required Python packages"""
    print_header("Installing Dependencies")
    
    requirements = [
        "streamlit",
        "pandas",
        "trafilatura",
        "openpyxl"
    ]
    
    print(f"Installing {len(requirements)} required packages...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        for package in requirements:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✓ {package} installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        return False
        
    print("\n✓ All dependencies installed successfully")
    return True

def create_directories():
    """Create necessary directories if they don't exist"""
    print_header("Configuring Application")
    
    directories = [
        "data",
        "data/exports",
        ".streamlit"
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✓ Created directory: {directory}")
        else:
            print(f"✓ Directory already exists: {directory}")
    
    # Create streamlit config file if it doesn't exist
    config_file = ".streamlit/config.toml"
    if not os.path.exists(config_file):
        with open(config_file, "w") as f:
            f.write("""[server]
headless = true
address = "0.0.0.0"
port = 5000

[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"
""")
        print(f"✓ Created Streamlit configuration file: {config_file}")
    else:
        print(f"✓ Streamlit configuration file already exists: {config_file}")
    
    return True

def main():
    """Main setup function"""
    print_header("HISAABSETU - Portable Accounting Software Setup")
    print("""
This setup script will:
1. Check Python installation
2. Install required dependencies
3. Configure application directories
4. Set up the database structure
""")
    
    input("Press Enter to continue or Ctrl+C to cancel...")
    
    # Step 1: Check Python installation
    if not install_python():
        return
    
    # Step 2: Install dependencies
    if not install_dependencies():
        return
    
    # Step 3: Create necessary directories
    if not create_directories():
        return
    
    # Final message
    print_header("Setup Complete")
    print("""
HISAABSETU has been set up successfully!

To run the application:
  - Open a terminal/command prompt
  - Navigate to the HISAABSETU directory
  - Run the command: streamlit run app.py

Thank you for installing HISAABSETU!
""")

if __name__ == "__main__":
    main()