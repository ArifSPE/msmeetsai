#!/usr/bin/env python3
"""
Setup script for the Agentic Business Rules POC

This script helps set up the environment and dependencies.
"""
import sys
import subprocess
import os
from pathlib import Path

project_root = Path(__file__).parent.absolute()
os.chdir(project_root)

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"❌ {description} failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} failed: {str(e)}")
        return False

def main():
    print("🚀 Setting up Agentic Business Rules POC")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 11):
        print("❌ Python 3.11+ is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version} detected")
    
    # Create virtual environment if it doesn't exist
    venv_path = project_root / ".venv"
    if not venv_path.exists():
        if not run_command("python -m venv .venv", "Creating virtual environment"):
            sys.exit(1)
    else:
        print("✅ Virtual environment already exists")
    
    # Activate virtual environment and install dependencies
    if sys.platform == "win32":
        pip_path = venv_path / "Scripts" / "pip"
        python_path = venv_path / "Scripts" / "python"
    else:
        pip_path = venv_path / "bin" / "pip"
        python_path = venv_path / "bin" / "python"
    
    # Install dependencies
    if not run_command(f"{pip_path} install --upgrade pip", "Upgrading pip"):
        sys.exit(1)
    
    if not run_command(f"{pip_path} install -r requirements.txt", "Installing dependencies"):
        sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Make sure Docker is running")
    print("2. Start Qdrant: docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant")
    print("3. Install Ollama: https://ollama.com/")
    print("4. Pull required models: ollama pull llama2:7b && ollama pull nomic-embed-text")
    print("5. Run the POC: python run.py")
    print("\nOr use the quick start script: python examples/quick_start.py")

if __name__ == "__main__":
    main()