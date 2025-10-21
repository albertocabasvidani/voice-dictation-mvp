"""
PyInstaller entry point wrapper
This ensures all modules are importable in frozen mode
"""
import os
import sys

# Add the directory containing this script to Python path
if getattr(sys, 'frozen', False):
    # Running as compiled exe - _MEIPASS contains extracted files
    bundle_dir = sys._MEIPASS
    # Add bundle dir so 'src' package is importable
    sys.path.insert(0, bundle_dir)
else:
    # Running as script - add current directory
    bundle_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, bundle_dir)

# Import and run main
from src import main

if __name__ == '__main__':
    main.main()
