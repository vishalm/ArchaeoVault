#!/usr/bin/env python3
"""
Run script for ArchaeoVault.

This script provides a simple way to run the ArchaeoVault application
using Streamlit directly.
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Main entry point for running ArchaeoVault."""
    try:
        # Get the app directory
        app_dir = Path(__file__).parent / "app"
        
        # Run streamlit with the app
        cmd = [sys.executable, "-m", "streamlit", "run", "streamlit_app_full.py"]
        
        print("🏺 Starting ArchaeoVault...")
        print(f"📁 App directory: {app_dir}")
        print(f"🚀 Command: {' '.join(cmd)}")
        
        # Run the command
        subprocess.run(cmd, check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Streamlit error: {e}")
        print("Please install the required dependencies:")
        print("  pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Application error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
