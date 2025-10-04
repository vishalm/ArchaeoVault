#!/usr/bin/env python3
"""
Main entry point for ArchaeoVault.

This script provides a simple way to run the ArchaeoVault application
with proper configuration and error handling.
"""

import sys
import os
from pathlib import Path

# Add the app directory to the Python path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir))

def main():
    """Main entry point for running ArchaeoVault."""
    try:
        # Import and run the application
        from app import main as app_main
        app_main()
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please install the required dependencies:")
        print("  pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Application error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
