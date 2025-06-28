#!/usr/bin/env python3
"""
Demo script for MediMind AI - Multimodal Health Assistant
Demonstrates the capabilities of the health assistant with sample data.
"""

import sys
import time
from pathlib import Path

# Add the parent directory to the path to import src modules
sys.path.append(str(Path(__file__).parent.parent))

from src.health_assistant import HealthAssistant
from src.config import SUPPORTED_LANGUAGES, HEALTH_CATEGORIES


def print_banner():
    """Print demo banner."""
    print("="*60)
    print("🏥 MediMind AI - Health Assistant Demo")
    print("="*60)
    print("Powered by Google Gemini 2.0 API")
    print("Text • Image • Audio Analysis")
    print("="*60)


def print_disclaimer():
    """Print health disclaimer."""
    print("\n⚠️  IMPORTANT DISCLAIMER ⚠️")
    print("This demo is for educational purposes only.")
    print("It is not a substitute for professional medical advice.")
    print("Always consult healthcare professionals for medical concerns.\n")


def demo_text_analysis(assistant):
    """Demonstrate text analysis capabilities."""
    print("📝 TEXT ANALYSIS DEMO")
    print("-" * 30)
    
    # English text
    print("1. English Query:")
    query_en = "What are the common symptoms of dehydration?"
    print(f"   Query: {query_en}")
    
    result = assistant.process_query(text_input=query_en, language='en')
    if result['success']:
        print("   ✅ Response received")
        print(f"   Response: {result['response'][:100]}...")
    else:
        print(f"   ❌ Error: {result['error']}")
    
    print()
    
    # Hindi text
    print("2. Hindi Query:")
    query_hi = "सिरदर्द के लक्षण क्या हैं?"
    print(f"   Query: {query_hi}")
    
    result = assistant.process_query(text_input=query_hi, language='hi')
    if result['success']:
        print("   ✅ Response received")
        print(f"   Response: {result['response'][:100]}...")
    else:
        print(f"   ❌ Error: {result['error']}")
    
    print()
    
    # Spanish text
    print("3. Spanish Query:")
    query_es = "¿Cuáles son los síntomas del resfriado común?"
    print(f"   Query: {query_es}")
    
    result = assistant.process_query(text_input=query_es, language='es')
    if result['success']:
        print("   ✅ Response received")
        print(f"   Response: {result['response'][:100]}...")
    else:
        print(f"   ❌ Error: {result['error']}")
    
    print()


def demo_health_tips(assistant):
    """Demonstrate health tips functionality."""
    print("💡 HEALTH TIPS DEMO")
    print("-" * 30)
    
    # General tips
    print("1. General Health Tips (English):")
    result = assistant.get_health_tips(language='en')
    if result['success']:
        print("   ✅ Tips received")
        print(f"   Tips: {result['response'][:100]}...")
    else:
        print(f"   ❌ Error: {result['error']}")
    
    print()
    
    # Category-specific tips
    print("2. Nutrition Tips (Hindi):")
    result = assistant.get_health_tips(category="Nutrition", language='hi')
    if result['success']:
        print("   ✅ Tips received")
        print(f"   Tips: {result['response'][:100]}...")
    else:
        print(f"   ❌ Error: {result['error']}")
    
    print()
    
    # Spanish tips
    print("3. Exercise Tips (Spanish):")
    result = assistant.get_health_tips(category="Exercise", language='es')
    if result['success']:
        print("   ✅ Tips received")
        print(f"   Tips: {result['response'][:100]}...")
    else:
        print(f"   ❌ Error: {result['error']}")
    
    print()


def demo_session_management(assistant):
    """Demonstrate session management capabilities."""
    print("📊 SESSION MANAGEMENT DEMO")
    print("-" * 30)
    
    # Get session summary
    print("1. Session Summary:")
    summary = assistant.get_session_summary()
    if summary['success']:
        print(f"   ✅ Total Queries: {summary['total_queries']}")
        print(f"   ✅ Successful: {summary['successful_queries']}")
        print(f"   ✅ Success Rate: {summary['success_rate']}%")
        print(f"   ✅ Duration: {summary['session_duration_minutes']} minutes")
        
        if summary['language_stats']:
            print(f"   ✅ Language Usage: {summary['language_stats']}")
        if summary['input_type_stats']:
            print(f"   ✅ Input Types: {summary['input_type_stats']}")
    else:
        print(f"   ❌ Error: {summary['error']}")
    
    print()
    
    # Save session
    print("2. Save Session:")
    save_result = assistant.save_session_to_file("demo_session.json")
    if save_result['success']:
        print(f"   ✅ Session saved to: {save_result['filepath']}")
    else:
        print(f"   ❌ Error: {save_result['error']}")
    
    print()


def demo_language_support():
    """Demonstrate language support."""
    print("🌍 LANGUAGE SUPPORT DEMO")
    print("-" * 30)
    
    print("Supported Languages:")
    for code, name in SUPPORTED_LANGUAGES.items():
        print(f"   • {code} - {name}")
    
    print()
    print("Health Categories:")
    for category in HEALTH_CATEGORIES:
        print(f"   • {category}")
    
    print()


def run_quick_demo(assistant):
    """Run a quick demo with basic functionality."""
    print("🚀 QUICK DEMO MODE")
    print("=" * 30)
    
    # Single text query
    print("Testing text analysis...")
    result = assistant.process_query(
        text_input="What are the symptoms of a common cold?",
        language='en'
    )
    
    if result['success']:
        print("✅ Text analysis working!")
        print(f"Response: {result['response'][:150]}...")
    else:
        print(f"❌ Text analysis failed: {result['error']}")
    
    print()
    
    # Health tips
    print("Testing health tips...")
    result = assistant.get_health_tips(language='en')
    
    if result['success']:
        print("✅ Health tips working!")
        print(f"Tips: {result['response'][:150]}...")
    else:
        print(f"❌ Health tips failed: {result['error']}")
    
    print()
    
    # Session summary
    print("Testing session management...")
    summary = assistant.get_session_summary()
    
    if summary['success']:
        print("✅ Session management working!")
        print(f"Total queries: {summary['total_queries']}")
    else:
        print(f"❌ Session management failed: {summary['error']}")


def main():
    """Main demo function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="MediMind AI Health Assistant Demo")
    parser.add_argument('--quick', action='store_true', help='Run quick demo only')
    parser.add_argument('--credentials', default='cred.json', help='Path to credentials file')
    parser.add_argument('--project-id', help='Google Cloud project ID')
    
    args = parser.parse_args()
    
    # Print banner and disclaimer
    print_banner()
    print_disclaimer()
    
    # Initialize health assistant
    try:
        print("🔧 Initializing Health Assistant...")
        assistant = HealthAssistant(args.credentials, args.project_id)
        print("✅ Health Assistant initialized successfully!")
        print()
    except Exception as e:
        print(f"❌ Failed to initialize Health Assistant: {e}")
        print("\n💡 Make sure you have:")
        print("   • Valid credentials file (cred.json)")
        print("   • Google Cloud project with Vertex AI enabled")
        print("   • Proper permissions set up")
        return
    
    if args.quick:
        run_quick_demo(assistant)
    else:
        # Run full demo
        demo_language_support()
        print()
        
        demo_text_analysis(assistant)
        print()
        
        demo_health_tips(assistant)
        print()
        
        demo_session_management(assistant)
        print()
    
    print("🎉 Demo completed!")
    print("\n💡 Try running with --quick for a faster demo")
    print("💡 Use --help for more options")


if __name__ == "__main__":
    main() 