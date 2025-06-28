#!/usr/bin/env python3
"""
MediMind AI - Multimodal Health Assistant CLI
A command-line interface for the health assistant using Google Gemini 2.0.
"""

import argparse
import sys
from pathlib import Path

from src.health_assistant import HealthAssistant
from src.config import SUPPORTED_LANGUAGES, HEALTH_CATEGORIES


def print_banner():
    """Print the application banner."""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║        🏥 MediMind AI - Health Assistant 🏥                 ║
    ║                                                              ║
    ║    Powered by Google Gemini 2.0 API                         ║
    ║    Text • Image • Audio Analysis                             ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_disclaimer():
    """Print the health disclaimer."""
    disclaimer = """
⚠️ IMPORTANT DISCLAIMER ⚠️
This health assistant is for educational and informational purposes only. 
It is not a substitute for professional medical advice, diagnosis, or treatment. 
Always consult with a qualified healthcare provider for medical concerns.
Never disregard professional medical advice or delay seeking it because of information provided by this assistant.
    """
    print(disclaimer)


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
            print("4. Show session summary")
            print("5. Export session data")
            print("6. Health tips")
            print("7. Help")
            print("8. Quit")
            
            choice = input("\nEnter your choice (1-8): ").strip()
            
            if choice == '1':
                handle_text_input(assistant)
            elif choice == '2':
                handle_image_input(assistant)
            elif choice == '3':
                handle_audio_input(assistant)
            elif choice == '4':
                show_session_summary(assistant)
            elif choice == '5':
                export_session_data(assistant)
            elif choice == '6':
                show_health_tips(assistant)
            elif choice == '7':
                show_help()
            elif choice == '8':
                print("👋 Thank you for using MediMind AI!")
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
    result = assistant.process_query(text_input=text, language=language)
    
    display_result(result)


def handle_image_input(assistant: HealthAssistant):
    """Handle image input from user."""
    print("\n🖼️  Image Analysis Mode")
    image_path = input("Enter image file path: ").strip()
    
    if not image_path:
        print("❌ Image path cannot be empty.")
        return
    
    description = input("Optional description of the image: ").strip()
    
    print("🔄 Processing image...")
    result = assistant.process_query(image_path=image_path, description=description)
    
    display_result(result)


def handle_audio_input(assistant: HealthAssistant):
    """Handle audio input from user."""
    print("\n🎵 Audio Analysis Mode")
    audio_path = input("Enter audio file path: ").strip()
    
    if not audio_path:
        print("❌ Audio path cannot be empty.")
        return
    
    language = input(f"Expected language (default: en): ").strip() or 'en'
    
    if language not in SUPPORTED_LANGUAGES:
        print(f"❌ Unsupported language. Using English instead.")
        language = 'en'
    
    print(f"🔄 Processing audio in {SUPPORTED_LANGUAGES[language]}...")
    result = assistant.process_query(audio_path=audio_path, language=language)
    
    display_result(result)


def display_result(result: dict):
    """Display the analysis result."""
    if not result.get('success', False):
        print(f"❌ Error: {result.get('error', 'Unknown error')}")
        return
    
    print("\n" + "="*60)
    print("📋 ANALYSIS RESULT")
    print("="*60)
    print(f"Input Type: {result.get('input_type', 'unknown')}")
    print(f"Language: {SUPPORTED_LANGUAGES.get(result.get('language', 'en'), result.get('language', 'en'))}")
    print(f"Timestamp: {result.get('timestamp', 'N/A')}")
    print("-"*60)
    print("Response:")
    print(result.get('response', 'No response'))
    print("="*60)


def show_session_summary(assistant: HealthAssistant):
    """Show session summary."""
    summary = assistant.get_session_summary()
    
    if not summary.get('success', False):
        print(f"❌ Error: {summary.get('error', 'Unknown error')}")
        return
    
    print("\n" + "="*50)
    print("📊 SESSION SUMMARY")
    print("="*50)
    print(f"Total Queries: {summary.get('total_queries', 0)}")
    print(f"Successful: {summary.get('successful_queries', 0)}")
    print(f"Success Rate: {summary.get('success_rate', 0)}%")
    print(f"Duration: {summary.get('session_duration_minutes', 0)} minutes")
    
    if summary.get('language_stats'):
        print(f"\nLanguage Usage: {summary['language_stats']}")
    if summary.get('input_type_stats'):
        print(f"Input Types: {summary['input_type_stats']}")
    
    print("="*50)


def export_session_data(assistant: HealthAssistant):
    """Export session data."""
    try:
        save_result = assistant.save_session_to_file()
        if save_result.get('success', False):
            print(f"\n✅ Session data exported to: {save_result.get('filepath', 'unknown')}")
        else:
            print(f"❌ Error exporting session data: {save_result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ Error exporting session data: {e}")


def show_health_tips(assistant: HealthAssistant):
    """Show health tips by category."""
    print("\n" + "="*50)
    print("💡 HEALTH TIPS")
    print("="*50)
    
    print("Available categories:")
    for i, category in enumerate(HEALTH_CATEGORIES, 1):
        print(f"  {i}. {category}")
    
    category_choice = input("\nEnter category number (or press Enter for general tips): ").strip()
    
    if category_choice.isdigit() and 1 <= int(category_choice) <= len(HEALTH_CATEGORIES):
        category = HEALTH_CATEGORIES[int(category_choice) - 1]
        result = assistant.get_health_tips(category=category)
    else:
        result = assistant.get_health_tips()
    
    if result.get('success', False):
        print(f"\n💡 Health Tips:")
        print(result.get('response', 'No tips available'))
    else:
        print(f"❌ Error: {result.get('error', 'Unknown error')}")
    
    print("="*50)


def show_help():
    """Show help information."""
    help_text = """
    🆘 HELP - MediMind AI Health Assistant
    
    Available Commands:
    • Text Analysis: Answer health questions with text input
    • Image Analysis: Analyze health-related images (rashes, medications, etc.)
    • Audio Analysis: Process spoken health concerns
    
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
        description="MediMind AI - Multimodal Health Assistant using Google Gemini 2.0 API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --text "What are the symptoms of a common cold?"
  python main.py --image rash.jpg --description "Red rash on arm"
  python main.py --audio symptoms.wav --language hi
  python main.py --interactive
        """
    )
    
    parser.add_argument('--text', help='Text query for health analysis')
    parser.add_argument('--image', help='Path to image file for analysis')
    parser.add_argument('--audio', help='Path to audio file for analysis')
    parser.add_argument('--description', help='Description for image analysis')
    parser.add_argument('--language', default='en', choices=list(SUPPORTED_LANGUAGES.keys()), 
                       help='Language code (default: en)')
    parser.add_argument('--interactive', action='store_true', help='Run in interactive mode')
    parser.add_argument('--credentials', help='Path to credentials JSON file')
    parser.add_argument('--project-id', help='Google Cloud project ID')
    parser.add_argument('--save-session', help='Save session to specified file')
    parser.add_argument('--load-session', help='Load session from specified file')
    
    args = parser.parse_args()
    
    # Print banner and disclaimer
    print_banner()
    print_disclaimer()
    
    # Initialize health assistant
    try:
        assistant = HealthAssistant(args.credentials, args.project_id)
        print("✅ MediMind AI Health Assistant initialized successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize health assistant: {e}")
        sys.exit(1)
    
    # Load session if specified
    if args.load_session:
        result = assistant.load_session_from_file(args.load_session)
        if result['success']:
            print(f"✅ Session loaded: {result['message']}")
        else:
            print(f"❌ Failed to load session: {result['error']}")
    
    # Process based on input type
    if args.text:
        print(f"\n🔍 Processing text query in {SUPPORTED_LANGUAGES[args.language]}...")
        result = assistant.process_query(
            text_input=args.text,
            language=args.language
        )
        
    elif args.image:
        print(f"\n🖼️  Processing image analysis...")
        result = assistant.process_query(
            image_path=args.image,
            description=args.description or "",
            language=args.language
        )
        
    elif args.audio:
        print(f"\n🎵 Processing audio analysis in {SUPPORTED_LANGUAGES[args.language]}...")
        result = assistant.process_query(
            audio_path=args.audio,
            language=args.language
        )
        
    elif args.interactive:
        interactive_mode(assistant)
        return
        
    else:
        # No input provided, show help
        parser.print_help()
        return
    
    # Display results
    if result['success']:
        print(f"\n✅ Response:")
        print(f"{'='*50}")
        print(result['response'])
        print(f"{'='*50}")
    else:
        print(f"\n❌ Error: {result['error']}")
    
    # Save session if requested
    if args.save_session:
        save_result = assistant.save_session_to_file(args.save_session)
        if save_result['success']:
            print(f"\n💾 Session saved: {save_result['filepath']}")
        else:
            print(f"\n❌ Failed to save session: {save_result['error']}")


if __name__ == "__main__":
    main() 