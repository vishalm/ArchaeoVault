#!/bin/bash
# Run script for ArchaeoVault

set -e

echo "🏺 Starting ArchaeoVault..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Run the application
echo "🚀 Starting ArchaeoVault application..."
streamlit run streamlit_app_full.py
