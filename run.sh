#!/bin/bash
# Fable Book Exporter - Mac/Linux Launcher
# This script sets up and runs the Fable Book Exporter

echo ""
echo "================================"
echo "  FABLE BOOK EXPORTER"
echo "  Mac/Linux Launcher"
echo "================================"
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "ERROR: uv is not installed"
    echo ""
    echo "Please install uv from https://docs.astral.sh/uv/getting-started/"
    echo "Or run: pip install uv"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Setting up Python environment with uv..."
    echo ""
    uv venv
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create virtual environment"
        exit 1
    fi
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
echo ""
uv pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

# Run the CLI
echo ""
echo "Starting Fable Book Exporter..."
echo ""
python cli.py
