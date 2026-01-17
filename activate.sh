#!/bin/bash
# Quick activation script for the virtual environment

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Activate the virtual environment
source "$SCRIPT_DIR/venv/bin/activate"

echo "Virtual environment activated!"
echo "You can now run: python run.py"
echo "To deactivate, type: deactivate"
