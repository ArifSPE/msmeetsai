#!/usr/bin/env python3
"""
Simple runner script for the Agentic Business Rules POC

This script handles the Python path setup and provides easy access to all functionality.
"""
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

# Set working directory to project root
os.chdir(project_root)

if __name__ == "__main__":
    # Import and run the main module
    from src.main import main
    main()