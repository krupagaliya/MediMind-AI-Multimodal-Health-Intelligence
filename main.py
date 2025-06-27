#!/usr/bin/env python3
"""
Multimodal Health Assistant - Main Application
A comprehensive health assistant using Google's Gemini 2.0 API for text, image, and audio analysis.
"""

import argparse
import sys
import json
from pathlib import Path
from typing import Optional

from src.health_assistant import HealthAssistant
from src.utils import (
    validate_file_path, 
    format_response_for_display, 
    create_visualization_summary,
    save_sample_data,
    load_sample_data,
    create_health_tips_database
)
from src.config import HEALTH_DISCLAIMER, SUPPORTED_LANGUAGES


def print_banner():
    """Print the application banner."""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║        🏥 Multimodal Health Assistant 🏥                    ║
    ║                                                              ║
    ║    Powered by Google Gemini 2.0 API                         ║
    ║    Text • Image • Audio Analysis                             ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_disclaimer():
    """Print the health disclaimer."""
    print("\n" + "="*80)
    print(HEALTH_DISCLAIMER)
    print("="*80 + "\n")


def interactive_mode(assistant: HealthAssistant):
    """Run the assistant in interactive mode."""
    print("🎯 Interactive Mode - Type 'help' for commands, 'quit' to exit")
    print("Supported languages:", ", ".join([f"{code} ({name})" for code, name in SUPPORTED_LANGUAGES.items()]))
    
    while True:
        try:
            print("\n" + "-"*50)
            print("Choose input type:")
            print("1. Text query")
            print("2. Image analysis")
            print("3. Audio analysis")
            print("4. Comprehensive analysis")
            print("5. Show session summary")
            print("6. Export session data")
            print("7. Health tips")
            print("8. Help")
            print("9. Quit")
            
            choice = input("\nEnter your choice (1-9): ").strip()
            
            if choice == '1':
                handle_text_input(assistant)
            elif choice == '2':
                handle_image_input(assistant)
            elif choice == '3':
                handle_audio_input(assistant)
            elif choice == '4':
                handle_comprehensive_input(assistant)
            elif choice == '5':
                show_session_summary(assistant)
            elif choice == '6':
                export_session_data(assistant)
            elif choice == '7':
                show_health_tips()
            elif choice == '8':
                show_help()
            elif choice == '9':
                print("👋 Thank you for using the Health Assistant!")
                break
            else:
                print("❌ Invalid choice. Please try again.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


def handle_text_input(assistant: HealthAssistant):
    """Handle text input from user."""
    print("\n📝 Text Analysis Mode")
    text = input("Enter your health question: ").strip()
    
    if not text:
        print("❌ Text cannot be empty.")
        return
    
    language = input(f"Language (default: en): ").strip() or 'en'
    
    if language not in SUPPORTED_LANGUAGES:
        print(f"❌ Unsupported language. Using English instead.")
        language = 'en'
    
    print(f"\n🔄 Processing text in {SUPPORTED_LANGUAGES[language]}...")
    result = assistant.analyze_text(text, language)
    
    display_result(result)


def handle_image_input(assistant: HealthAssistant):
    """Handle image input from user."""
    print("\n🖼️  Image Analysis Mode")
    image_path = input("Enter image file path: ").strip()
    
    if not image_path:
        print("❌ Image path cannot be empty.")
        return
    
    # Validate image path
    is_valid, error_msg = validate_file_path(image_path, 'image')
    if not is_valid:
        print(f"❌ {error_msg}")
        return
    
    description = input("Optional description of the image: ").strip()
    
    print("🔄 Processing image...")
    result = assistant.analyze_image(image_path, description)
    
    display_result(result)


def handle_audio_input(assistant: HealthAssistant):
    """Handle audio input from user."""
    print("\n🎵 Audio Analysis Mode")
    audio_path = input("Enter audio file path: ").strip()
    
    if not audio_path:
        print("❌ Audio path cannot be empty.")
        return
    
    # Validate audio path
    is_valid, error_msg = validate_file_path(audio_path, 'audio')
    if not is_valid:
        print(f"❌ {error_msg}")
        return
    
    language = input(f"Expected language (default: en): ").strip() or 'en'
    
    if language not in SUPPORTED_LANGUAGES:
        print(f"❌ Unsupported language. Using English instead.")
        language = 'en'
    
    print(f"🔄 Processing audio in {SUPPORTED_LANGUAGES[language]}...")
    result = assistant.analyze_audio(audio_path, language)
    
    display_result(result)


def handle_comprehensive_input(assistant: HealthAssistant):
    """Handle comprehensive analysis with multiple inputs."""
    print("\n🔍 Comprehensive Analysis Mode")
    
    text_input = input("Text query (optional): ").strip() or None
    image_path = input("Image file path (optional): ").strip() or None
    audio_path = input("Audio file path (optional): ").strip() or None
    
    if not any([text_input, image_path, audio_path]):
        print("❌ At least one input is required.")
        return
    
    # Validate file paths
    if image_path:
        is_valid, error_msg = validate_file_path(image_path, 'image')
        if not is_valid:
            print(f"❌ {error_msg}")
            return
    
    if audio_path:
        is_valid, error_msg = validate_file_path(audio_path, 'audio')
        if not is_valid:
            print(f"❌ {error_msg}")
            return
    
    language = input(f"Language (default: en): ").strip() or 'en'
    
    if language not in SUPPORTED_LANGUAGES:
        print(f"❌ Unsupported language. Using English instead.")
        language = 'en'
    
    print("🔄 Processing comprehensive analysis...")
    result = assistant.comprehensive_analysis(
        text_input=text_input,
        image_path=image_path,
        audio_path=audio_path,
        language=language
    )
    
    display_result(result)


def display_result(result: dict):
    """Display the analysis result."""
    formatted_result = format_response_for_display(result)
    
    if formatted_result['status'] == 'error':
        print(f"❌ Error: {formatted_result['message']}")
        return
    
    print("\n" + "="*60)
    print("📋 ANALYSIS RESULT")
    print("="*60)
    print(f"Input Type: {formatted_result['input_type']}")
    print(f"Language: {SUPPORTED_LANGUAGES.get(formatted_result['language'], formatted_result['language'])}")
    print(f"Word Count: {formatted_result['word_count']}")
    print(f"Character Count: {formatted_result['character_count']}")
    print(f"Timestamp: {formatted_result['timestamp']}")
    print("-"*60)
    print("Response:")
    print(formatted_result['response'])
    print("="*60)


def show_session_summary(assistant: HealthAssistant):
    """Show session summary."""
    summary = assistant.get_session_summary()
    
    print("\n" + "="*50)
    print("📊 SESSION SUMMARY")
    print("="*50)
    print(f"Session ID: {summary['session_id']}")
    print(f"Total Interactions: {summary['total_interactions']}")
    print(f"Session Duration: {summary['session_duration']:.1f} seconds")
    
    if summary['interactions_by_type']:
        print("\nInteractions by Type:")
        for input_type, count in summary['interactions_by_type'].items():
            print(f"  • {input_type}: {count}")
    
    if summary['start_time']:
        print(f"\nStart Time: {summary['start_time']}")
    if summary['end_time']:
        print(f"End Time: {summary['end_time']}")
    
    print("="*50)


def export_session_data(assistant: HealthAssistant):
    """Export session data."""
    try:
        output_path = assistant.export_session_data()
        print(f"\n✅ Session data exported to: {output_path}")
        
        # Create visualization if there's data
        summary = assistant.get_session_summary()
        if summary['total_interactions'] > 0:
            try:
                viz_path = create_visualization_summary(assistant.session_history)
                print(f"📊 Visualization created: {viz_path}")
            except Exception as e:
                print(f"⚠️  Could not create visualization: {e}")
                
    except Exception as e:
        print(f"❌ Error exporting session data: {e}")


def show_health_tips():
    """Show health tips by category."""
    tips = create_health_tips_database()
    
    print("\n" + "="*50)
    print("💡 HEALTH TIPS")
    print("="*50)
    
    for category, tip_list in tips.items():
        print(f"\n🏷️  {category}:")
        for i, tip in enumerate(tip_list, 1):
            print(f"  {i}. {tip}")
    
    print("="*50)


def show_help():
    """Show help information."""
    help_text = """
    🆘 HELP - Multimodal Health Assistant
    
    Available Commands:
    • Text Analysis: Answer health questions with text input
    • Image Analysis: Analyze health-related images (rashes, medications, etc.)
    • Audio Analysis: Process spoken health concerns
    • Comprehensive Analysis: Combine multiple input types for detailed insights
    
    Supported Languages:
    """ + ", ".join([f"{code} ({name})" for code, name in SUPPORTED_LANGUAGES.items()]) + """
    
    Supported File Formats:
    • Images: JPG, JPEG, PNG, BMP, TIFF, WebP
    • Audio: WAV, MP3, M4A, FLAC, OGG
    
    Tips:
    • Be specific in your questions for better responses
    • For images, provide context about what you're showing
    • For audio, speak clearly and describe symptoms in detail
    • Always consult healthcare professionals for medical advice
    
    Remember: This assistant is for educational purposes only!
    """
    print(help_text)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Multimodal Health Assistant using Google Gemini 2.0 API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --text "What causes headaches?"
  python main.py --image rash.jpg --description "Red rash on arm"
  python main.py --audio symptoms.wav --language hi
  python main.py --comprehensive --text "I feel dizzy" --image medication.jpg
  python main.py --interactive
        """
    )
    
    parser.add_argument('--text', help='Text query for health analysis')
    parser.add_argument('--image', help='Path to image file for analysis')
    parser.add_argument('--audio', help='Path to audio file for analysis')
    parser.add_argument('--description', help='Description for image analysis')
    parser.add_argument('--language', default='en', help='Language code (default: en)')
    parser.add_argument('--comprehensive', action='store_true', help='Perform comprehensive analysis')
    parser.add_argument('--interactive', action='store_true', help='Run in interactive mode')
    parser.add_argument('--credentials', help='Path to credentials JSON file')
    parser.add_argument('--project-id', help='Google Cloud project ID')
    parser.add_argument('--location', default='us-central1', help='Google Cloud location (default: us-central1)')
    parser.add_argument('--export', action='store_true', help='Export session data after analysis')
    parser.add_argument('--sample-data', action='store_true', help='Generate sample data')
    
    args = parser.parse_args()
    
    # Print banner and disclaimer
    print_banner()
    print_disclaimer()
    
    # Handle sample data generation
    if args.sample_data:
        try:
            output_path = save_sample_data()
            print(f"✅ Sample data saved to: {output_path}")
            return
        except Exception as e:
            print(f"❌ Error generating sample data: {e}")
            return
    
    # Initialize health assistant
    try:
        assistant = HealthAssistant(
            credentials_path=args.credentials,
            project_id=args.project_id,
            location=args.location
        )
        print("✅ Health Assistant initialized successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize Health Assistant: {e}")
        print("Please check your credentials file and API access.")
        return
    
    # Run in interactive mode
    if args.interactive:
        interactive_mode(assistant)
        return
    
    # Handle single input types
    if args.text and not args.comprehensive:
        result = assistant.analyze_text(args.text, args.language)
        display_result(result)
    
    elif args.image and not args.comprehensive:
        result = assistant.analyze_image(args.image, args.description or "")
        display_result(result)
    
    elif args.audio and not args.comprehensive:
        result = assistant.analyze_audio(args.audio, args.language)
        display_result(result)
    
    # Handle comprehensive analysis
    elif args.comprehensive:
        result = assistant.comprehensive_analysis(
            text_input=args.text,
            image_path=args.image,
            audio_path=args.audio,
            language=args.language
        )
        display_result(result)
    
    # No valid input provided
    else:
        print("❌ No valid input provided. Use --help for usage information.")
        return
    
    # Export session data if requested
    if args.export:
        try:
            output_path = assistant.export_session_data()
            print(f"\n✅ Session data exported to: {output_path}")
        except Exception as e:
            print(f"❌ Error exporting session data: {e}")


if __name__ == "__main__":
    main() 