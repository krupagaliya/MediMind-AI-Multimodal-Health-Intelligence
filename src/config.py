"""
Configuration settings for the Multimodal Health Assistant.
"""
import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
CREDENTIALS_PATH = PROJECT_ROOT / "cred.json"
SAMPLE_DATA_PATH = PROJECT_ROOT / "sample_data"
OUTPUT_PATH = PROJECT_ROOT / "output"

# Create directories if they don't exist
SAMPLE_DATA_PATH.mkdir(exist_ok=True)
OUTPUT_PATH.mkdir(exist_ok=True)

# Gemini API Configuration
GEMINI_MODEL_NAME = "gemini-2.0-flash-001"  # Latest model for google-genai
MAX_TOKENS = 4096
TEMPERATURE = 0.7

# Supported file formats
SUPPORTED_IMAGE_FORMATS = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']
SUPPORTED_AUDIO_FORMATS = ['.wav', '.mp3', '.m4a', '.flac', '.ogg']

# Health Assistant Configuration
HEALTH_DISCLAIMER = """
⚠️ IMPORTANT DISCLAIMER ⚠️
This health assistant is for educational and informational purposes only. 
It is not a substitute for professional medical advice, diagnosis, or treatment. 
Always consult with a qualified healthcare provider for medical concerns.
Never disregard professional medical advice or delay seeking it because of information provided by this assistant.
"""

# Multilingual support - Limited to 3 languages
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'hi': 'Hindi',
    'es': 'Spanish'
}

# Health categories for better organization
HEALTH_CATEGORIES = [
    'General Health',
    'Symptoms',
    'Medications',
    'First Aid',
    'Nutrition',
    'Exercise',
    'Mental Health',
    'Emergency'
]

# API Rate limiting
MAX_REQUESTS_PER_MINUTE = 60
REQUEST_TIMEOUT = 30  # seconds 