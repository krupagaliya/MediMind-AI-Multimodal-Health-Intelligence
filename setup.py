#!/usr/bin/env python3
"""
Setup script for the Multimodal Health Assistant.
Helps users install dependencies and configure the project.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is compatible."""
    print("🐍 Checking Python version...")
    
    if sys.version_info < (3, 8):
        print(f"❌ Python {sys.version} is not supported. Please use Python 3.8 or higher.")
        return False
    
    print(f"✅ Python {sys.version.split()[0]} is compatible")
    return True


def install_dependencies():
    """Install required dependencies."""
    print("\n📦 Installing dependencies...")
    
    # Upgrade pip first
    if not run_command("pip install --upgrade pip", "Upgrading pip"):
        return False
    
    # Install requirements
    if not run_command("pip install -r requirements.txt", "Installing requirements"):
        return False
    
    return True


def create_directories():
    """Create necessary directories."""
    print("\n📁 Creating directories...")
    
    directories = ["output", "sample_data"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    return True


def setup_credentials():
    """Guide user through credentials setup."""
    print("\n🔐 Setting up credentials...")
    
    cred_file = Path("cred.json")
    
    if cred_file.exists():
        print("✅ Credentials file already exists")
        return True
    
    print("⚠️ Credentials file not found.")
    print("\nTo set up credentials:")
    print("1. Go to Google Cloud Console: https://console.cloud.google.com/")
    print("2. Create a new project or select an existing one")
    print("3. Enable Vertex AI API and Gemini API")
    print("4. Create a service account with appropriate permissions")
    print("5. Download the JSON key file")
    print("6. Save it as 'cred.json' in the project root")
    print("\nOr copy from the example:")
    print("cp cred.json.example cred.json")
    print("Then edit cred.json with your actual credentials")
    
    response = input("\nWould you like to copy the example file? (y/n): ").lower()
    
    if response == 'y':
        example_file = Path("cred.json.example")
        if example_file.exists():
            import shutil
            shutil.copy(example_file, cred_file)
            print("✅ Copied cred.json.example to cred.json")
            print("⚠️ Please edit cred.json with your actual credentials")
            return True
        else:
            print("❌ Example file not found")
            return False
    
    return False


def run_tests():
    """Run the test script."""
    print("\n🧪 Running tests...")
    
    test_script = Path("test_setup.py")
    if test_script.exists():
        return run_command("python test_setup.py", "Running setup tests")
    else:
        print("⚠️ Test script not found")
        return True


def main():
    """Main setup function."""
    print("="*60)
    print("🏥 MULTIMODAL HEALTH ASSISTANT - SETUP")
    print("="*60)
    print("Using google-genai with Vertex AI integration")
    print("="*60)
    
    steps = [
        ("Python Version Check", check_python_version),
        ("Install Dependencies", install_dependencies),
        ("Create Directories", create_directories),
        ("Setup Credentials", setup_credentials),
        ("Run Tests", run_tests)
    ]
    
    failed_steps = []
    
    for step_name, step_func in steps:
        try:
            if not step_func():
                failed_steps.append(step_name)
        except Exception as e:
            print(f"❌ {step_name} failed with exception: {e}")
            failed_steps.append(step_name)
    
    # Summary
    print("\n" + "="*60)
    print("📊 SETUP SUMMARY")
    print("="*60)
    
    if not failed_steps:
        print("🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Edit cred.json with your Google Cloud credentials")
        print("2. Ensure Vertex AI and Gemini APIs are enabled in your Google Cloud project")
        print("3. Run: python main.py --interactive")
        print("4. Or run: streamlit run streamlit_app.py")
        print("5. Or run: python examples/demo.py --quick")
        print("\nTechnical notes:")
        print("- Using google-genai library with Vertex AI")
        print("- Model: gemini-2.0-flash-001")
        print("- Authentication: Environment variables (GOOGLE_APPLICATION_CREDENTIALS)")
        print("- Project ID: Set via GOOGLE_CLOUD_PROJECT or --project-id parameter")
    else:
        print("⚠️ Setup completed with some issues:")
        for step in failed_steps:
            print(f"  • {step} failed")
        print("\nPlease fix the issues above before proceeding.")
    
    print("="*60)


if __name__ == "__main__":
    main() 