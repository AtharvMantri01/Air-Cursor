#!/usr/bin/env python3
"""
Launcher script for Hand Control System
Run this from the project root directory
"""

import sys
import os

# Add src directory to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, src_path)

# Import and run main
from main import main

if __name__ == "__main__":
    main()
