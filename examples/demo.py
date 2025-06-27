#!/usr/bin/env python3
"""
Demo script for the Multimodal Health Assistant.
Showcases various capabilities with sample data and examples.
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from health_assistant import HealthAssistant
from utils import create_sample_data, create_health_tips_database
from config import SUPPORTED_LANGUAGES


def print_demo_header():
    """Print demo header."""
    print("="*80)
    print("🏥 MULTIMODAL HEALTH ASSISTANT - DEMO")
    print("="*80)
    print("This demo showcases the capabilities of the Health Assistant")
    print("using sample data and various input types.")
    print("="*80)


def demo_text_analysis(assistant):
    """Demo text analysis capabilities."""
    print("\n📝 TEXT ANALYSIS DEMO")
    print("-" * 40)
    
    sample_queries = [
        "What are the common symptoms of dehydration?",
        "How can I improve my sleep quality?",
        "What should I do for a mild headache?",
        "What are the benefits of regular exercise?",
        "How can I manage stress and anxiety?"
    ]
    
    for i, query in enumerate(sample_queries, 1):
        print(f"\n{i}. Query: {query}")
        print("Processing...")
        
        result = assistant.analyze_text(query, 'en')
        
        if result['success']:
            print("✅ Success!")
            print(f"Response: {result['response'][:200]}...")
        else:
            print(f"❌ Error: {result['error']}")
        
        time.sleep(1)  # Rate limiting simulation


def demo_multilingual_support(assistant):
    """Demo multilingual support."""
    print("\n🌍 MULTILINGUAL SUPPORT DEMO")
    print("-" * 40)
    
    multilingual_queries = {
        'hi': "मुझे सिरदर्द हो रहा है, क्या करूं?",
        'es': "¿Qué debo hacer para un dolor de cabeza?",
        'fr': "Que dois-je faire pour un mal de tête?",
        'de': "Was soll ich bei Kopfschmerzen tun?"
    }
    
    for lang_code, query in multilingual_queries.items():
        lang_name = SUPPORTED_LANGUAGES.get(lang_code, lang_code)
        print(f"\nLanguage: {lang_name} ({lang_code})")
        print(f"Query: {query}")
        print("Processing...")
        
        result = assistant.analyze_text(query, lang_code)
        
        if result['success']:
            print("✅ Success!")
            print(f"Response: {result['response'][:200]}...")
        else:
            print(f"❌ Error: {result['error']}")
        
        time.sleep(1)  # Rate limiting simulation


def demo_comprehensive_analysis(assistant):
    """Demo comprehensive analysis with multiple inputs."""
    print("\n🔍 COMPREHENSIVE ANALYSIS DEMO")
    print("-" * 40)
    
    # Simulate comprehensive analysis with text and description
    text_input = "I've been feeling dizzy and tired for the past few days"
    image_description = "A red rash on the arm"
    
    print(f"Text Input: {text_input}")
    print(f"Image Description: {image_description}")
    print("Processing comprehensive analysis...")
    
    result = assistant.comprehensive_analysis(
        text_input=text_input,
        image_path=None,  # No actual image file in demo
        audio_path=None,  # No actual audio file in demo
        language='en'
    )
    
    if result['success']:
        print("✅ Success!")
        print(f"Response: {result['response'][:300]}...")
    else:
        print(f"❌ Error: {result['error']}")


def demo_session_management(assistant):
    """Demo session management features."""
    print("\n📊 SESSION MANAGEMENT DEMO")
    print("-" * 40)
    
    # Get session summary
    summary = assistant.get_session_summary()
    
    print(f"Session ID: {summary['session_id']}")
    print(f"Total Interactions: {summary['total_interactions']}")
    print(f"Session Duration: {summary['session_duration']:.1f} seconds")
    
    if summary['interactions_by_type']:
        print("\nInteractions by Type:")
        for input_type, count in summary['interactions_by_type'].items():
            print(f"  • {input_type}: {count}")
    
    # Export session data
    try:
        output_path = assistant.export_session_data()
        print(f"\n✅ Session data exported to: {output_path}")
    except Exception as e:
        print(f"❌ Error exporting session data: {e}")


def demo_health_tips(assistant):
    """Demo health tips database."""
    print("\n💡 HEALTH TIPS DEMO")
    print("-" * 40)
    
    tips = create_health_tips_database()
    
    for category, tip_list in tips.items():
        print(f"\n🏷️ {category}:")
        for i, tip in enumerate(tip_list[:3], 1):  # Show first 3 tips per category
            print(f"  {i}. {tip}")


def demo_error_handling(assistant):
    """Demo error handling capabilities."""
    print("\n⚠️ ERROR HANDLING DEMO")
    print("-" * 40)
    
    # Test with empty text
    print("1. Testing empty text input...")
    result = assistant.analyze_text("", "en")
    if not result['success']:
        print(f"✅ Properly handled: {result['error']}")
    
    # Test with unsupported language
    print("\n2. Testing unsupported language...")
    result = assistant.analyze_text("Test query", "xx")
    if not result['success']:
        print(f"✅ Properly handled: {result['error']}")
    
    # Test with non-existent file
    print("\n3. Testing non-existent image file...")
    result = assistant.analyze_image("non_existent_file.jpg", "")
    if not result['success']:
        print(f"✅ Properly handled: {result['error']}")


def run_full_demo():
    """Run the complete demo."""
    print_demo_header()
    
    # Initialize assistant (you'll need valid credentials)
    try:
        assistant = HealthAssistant()
        print("✅ Health Assistant initialized successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize Health Assistant: {e}")
        print("Please ensure you have valid credentials configured.")
        return
    
    # Run demos
    try:
        demo_text_analysis(assistant)
        demo_multilingual_support(assistant)
        demo_comprehensive_analysis(assistant)
        demo_session_management(assistant)
        demo_health_tips(assistant)
        demo_error_handling(assistant)
        
        print("\n" + "="*80)
        print("🎉 DEMO COMPLETED SUCCESSFULLY!")
        print("="*80)
        print("The Multimodal Health Assistant demo has showcased:")
        print("• Text analysis with health queries")
        print("• Multilingual support (English, Hindi, Spanish, French, German)")
        print("• Comprehensive analysis capabilities")
        print("• Session management and data export")
        print("• Health tips database")
        print("• Robust error handling")
        print("\nFor more features, try the interactive mode or web interface!")
        
    except Exception as e:
        print(f"❌ Demo failed with error: {e}")


def run_quick_demo():
    """Run a quick demo with minimal API calls."""
    print_demo_header()
    print("🚀 QUICK DEMO MODE")
    
    try:
        assistant = HealthAssistant()
        print("✅ Health Assistant initialized successfully!")
        
        # Single text analysis demo
        print("\n📝 Quick Text Analysis Demo")
        print("-" * 30)
        
        query = "What are the benefits of drinking water?"
        print(f"Query: {query}")
        
        result = assistant.analyze_text(query, 'en')
        
        if result['success']:
            print("✅ Success!")
            print(f"Response: {result['response'][:200]}...")
        else:
            print(f"❌ Error: {result['error']}")
        
        # Session summary
        summary = assistant.get_session_summary()
        print(f"\n📊 Session Summary: {summary['total_interactions']} interactions")
        
        print("\n🎉 Quick demo completed!")
        
    except Exception as e:
        print(f"❌ Quick demo failed: {e}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Health Assistant Demo")
    parser.add_argument("--quick", action="store_true", help="Run quick demo with minimal API calls")
    
    args = parser.parse_args()
    
    if args.quick:
        run_quick_demo()
    else:
        run_full_demo() 