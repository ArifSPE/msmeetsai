#!/usr/bin/env python3
"""
Quick Start Script for Agentic Business Rules POC

This script helps you get started quickly with the POC by:
1. Checking prerequisites (Qdrant, Ollama)
2. Setting up the environment
3. Running a simple demo
"""
import subprocess
import sys
import time
import requests
from pathlib import Path


def check_command_exists(command):
    """Check if a command exists in the system PATH"""
    try:
        subprocess.run([command, "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def check_service_running(url, service_name):
    """Check if a service is running by making a request"""
    try:
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False


def run_command(command, description, check=True):
    """Run a command and print the result"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=check)
        if result.returncode == 0:
            print(f"   ✅ Success")
            return True
        else:
            print(f"   ❌ Failed: {result.stderr}")
            return False
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Failed: {e}")
        return False


def main():
    """Main setup and demo function"""
    print("🚀 Agentic Business Rules POC - Quick Start")
    print("=" * 50)
    
    # Check prerequisites
    print("\n1. 🔍 Checking Prerequisites...")
    
    # Check Python
    print(f"   • Python: {sys.version.split()[0]} ✅")
    
    # Check Docker
    if check_command_exists("docker"):
        print("   • Docker: Available ✅")
    else:
        print("   • Docker: Not found ❌")
        print("     Please install Docker to run Qdrant")
        return
    
    # Check Ollama
    if check_command_exists("ollama"):
        print("   • Ollama: Available ✅")
    else:
        print("   • Ollama: Not found ❌")
        print("     Please install Ollama from https://ollama.ai")
        return
    
    # Check services
    print("\n2. 🔗 Checking Services...")
    
    # Check Qdrant
    qdrant_running = check_service_running("http://localhost:6333", "Qdrant")
    if qdrant_running:
        print("   • Qdrant: Running ✅")
    else:
        print("   • Qdrant: Not running ⚠️")
        print("     Starting Qdrant container...")
        if run_command(
            "docker run -d -p 6333:6333 --name qdrant qdrant/qdrant",
            "Starting Qdrant container"
        ):
            time.sleep(5)  # Wait for Qdrant to start
            if check_service_running("http://localhost:6333", "Qdrant"):
                print("   • Qdrant: Now running ✅")
            else:
                print("   • Qdrant: Failed to start ❌")
                return
    
    # Check Ollama service
    ollama_running = check_service_running("http://localhost:11434", "Ollama")
    if ollama_running:
        print("   • Ollama: Running ✅")
    else:
        print("   • Ollama: Not running ⚠️")
        print("     Please start Ollama: 'ollama serve'")
        return
    
    # Check/Download models
    print("\n3. 📦 Checking Models...")
    
    # Check Llama2 model
    result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
    if "llama2" in result.stdout:
        print("   • Llama2: Available ✅")
    else:
        print("   • Llama2: Not found, downloading...")
        if run_command("ollama pull llama2:7b", "Downloading Llama2 model"):
            print("   • Llama2: Downloaded ✅")
        else:
            print("   • Llama2: Download failed ❌")
            return
    
    # Check embedding model
    if "nomic-embed-text" in result.stdout:
        print("   • Embedding model: Available ✅")
    else:
        print("   • Embedding model: Not found, downloading...")
        if run_command("ollama pull nomic-embed-text", "Downloading embedding model"):
            print("   • Embedding model: Downloaded ✅")
        else:
            print("   • Embedding model: Download failed ❌")
            return
    
    # Install Python dependencies
    print("\n4. 📚 Installing Dependencies...")
    if run_command("pip install -r requirements.txt", "Installing Python packages"):
        print("   • Python packages: Installed ✅")
    else:
        print("   • Python packages: Installation failed ❌")
        return
    
    # Set up environment
    print("\n5. ⚙️ Setting Up Environment...")
    env_file = Path(".env")
    if not env_file.exists():
        print("   • Creating .env file...")
        with open(".env", "w") as f:
            with open(".env.example", "r") as example:
                f.write(example.read())
        print("   • Environment file: Created ✅")
    else:
        print("   • Environment file: Already exists ✅")
    
    print("\n6. 🎯 System Ready!")
    print("=" * 50)
    print("\nNext steps:")
    print("1. Run the demo: 'python examples/demo_scenarios.py'")
    print("2. Start the API server: 'python -m src.api.main'")
    print("3. Open the API docs: 'http://localhost:8000/docs'")
    
    # Ask if user wants to run demo
    choice = input("\n🤖 Would you like to run the demo scenarios now? (y/n): ")
    if choice.lower().startswith('y'):
        print("\n🚀 Starting demo scenarios...")
        subprocess.run([sys.executable, "examples/demo_scenarios.py"])
    
    print("\n🎉 Quick start complete!")


if __name__ == "__main__":
    main()