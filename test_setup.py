#!/usr/bin/env python3
"""
Test script to verify the Multimodal Health Assistant setup.
This script tests imports and basic functionality without making API calls.
"""

import sys
from pathlib import Path

def test_imports():
    """Test if all modules can be imported successfully."""
    print("🔍 Testing imports...")
    
    try:
        from src.config import (
            SUPPORTED_LANGUAGES, 
            HEALTH_CATEGORIES, 
            SUPPORTED_IMAGE_FORMATS,
            SUPPORTED_AUDIO_FORMATS
        )
        print("✅ Config module imported successfully")
        
        from src.utils import (
            validate_file_path,
            create_sample_data,
            create_health_tips_database
        )
        print("✅ Utils module imported successfully")
        
        from src.gemini_client import GeminiClient
        print("✅ Gemini client module imported successfully")
        
        from src.health_assistant import HealthAssistant
        print("✅ Health assistant module imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_config():
    """Test configuration values."""
    print("\n🔧 Testing configuration...")
    
    try:
        from src.config import (
            SUPPORTED_LANGUAGES, 
            HEALTH_CATEGORIES, 
            SUPPORTED_IMAGE_FORMATS,
            SUPPORTED_AUDIO_FORMATS
        )
        
        print(f"✅ Supported languages: {len(SUPPORTED_LANGUAGES)} languages")
        print(f"✅ Health categories: {len(HEALTH_CATEGORIES)} categories")
        print(f"✅ Image formats: {len(SUPPORTED_IMAGE_FORMATS)} formats")
        print(f"✅ Audio formats: {len(SUPPORTED_AUDIO_FORMATS)} formats")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


def test_utils():
    """Test utility functions."""
    print("\n🛠️ Testing utility functions...")
    
    try:
        from src.utils import (
            validate_file_path,
            create_sample_data,
            create_health_tips_database
        )
        
        # Test file validation
        is_valid, error_msg = validate_file_path("test.txt", "any")
        print(f"✅ File validation test: {is_valid}, {error_msg}")
        
        # Test sample data creation
        sample_data = create_sample_data()
        print(f"✅ Sample data created: {len(sample_data)} categories")
        
        # Test health tips
        tips = create_health_tips_database()
        print(f"✅ Health tips created: {len(tips)} categories")
        
        return True
        
    except Exception as e:
        print(f"❌ Utils test failed: {e}")
        return False


def test_credentials():
    """Test credentials file."""
    print("\n🔐 Testing credentials...")
    
    cred_path = Path("cred.json")
    
    if not cred_path.exists():
        print("⚠️ Credentials file not found. Please create cred.json with your Google Cloud credentials.")
        return False
    
    try:
        import json
        with open(cred_path, 'r') as f:
            creds = json.load(f)
        
        required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email']
        missing_fields = [field for field in required_fields if field not in creds]
        
        if missing_fields:
            print(f"❌ Missing required fields in credentials: {missing_fields}")
            return False
        
        print("✅ Credentials file structure is valid")
        print(f"✅ Project ID: {creds['project_id']}")
        print(f"✅ Client Email: {creds['client_email']}")
        
        return True
        
    except json.JSONDecodeError:
        print("❌ Credentials file is not valid JSON")
        return False
    except Exception as e:
        print(f"❌ Credentials test failed: {e}")
        return False


def test_dependencies():
    """Test if required dependencies are installed."""
    print("\n📦 Testing dependencies...")
    
    required_packages = [
        'google.genai',
        'pydub',
        'Pillow',
        'pandas',
        'matplotlib',
        'streamlit',
        'numpy',
        'scipy',
        'librosa',
        'soundfile'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - NOT INSTALLED")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️ Missing packages: {missing_packages}")
        print("Please install missing packages with: pip install -r requirements.txt")
        return False
    
    print("✅ All required dependencies are installed")
    return True


def main():
    """Run all tests."""
    print("="*60)
    print("🏥 MULTIMODAL HEALTH ASSISTANT - SETUP TEST")
    print("="*60)
    
    tests = [
        ("Dependencies", test_dependencies),
        ("Imports", test_imports),
        ("Configuration", test_config),
        ("Utilities", test_utils),
        ("Credentials", test_credentials)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your setup is ready.")
        print("\nNext steps:")
        print("1. Ensure your Google Cloud project has Vertex AI and Gemini APIs enabled")
        print("2. Run: python main.py --interactive")
        print("3. Or run: streamlit run streamlit_app.py")
    else:
        print("\n⚠️ Some tests failed. Please fix the issues above before proceeding.")
    
    print("="*60)


if __name__ == "__main__":
    main() 