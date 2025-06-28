"""
Utility functions for the Multimodal Health Assistant.
Handles file operations, data processing, and visualization.
"""
import os
import json
import base64
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image
import io

from .config import (
    SUPPORTED_IMAGE_FORMATS,
    SUPPORTED_AUDIO_FORMATS,
    OUTPUT_PATH
)


def save_session(session_data: Dict[str, Any], filepath: Path) -> None:
    """
    Save session data to a JSON file.
    
    Args:
        session_data: Session data dictionary
        filepath: Path to save the session file
    """
    try:
        # Ensure output directory exists
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Save session data
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False, default=str)
            
    except Exception as e:
        raise Exception(f"Failed to save session: {str(e)}")


def load_session(filepath: str) -> Dict[str, Any]:
    """
    Load session data from a JSON file.
    
    Args:
        filepath: Path to the session file
        
    Returns:
        Session data dictionary
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            session_data = json.load(f)
        return session_data
        
    except Exception as e:
        raise Exception(f"Failed to load session: {str(e)}")


def get_file_info(filepath: str) -> Dict[str, Any]:
    """
    Get information about a file.
    
    Args:
        filepath: Path to the file
        
    Returns:
        Dictionary containing file information
    """
    try:
        path = Path(filepath)
        if not path.exists():
            return {'error': 'File not found'}
        
        stat = path.stat()
        return {
            'name': path.name,
            'size': stat.st_size,
            'modified': stat.st_mtime,
            'extension': path.suffix.lower(),
            'exists': True
        }
        
    except Exception as e:
        return {'error': str(e)}


def validate_file_path(file_path: str, file_type: str = 'any') -> Tuple[bool, str]:
    """
    Validate if a file path exists and has the correct format.
    
    Args:
        file_path: Path to the file
        file_type: Type of file ('image', 'audio', 'any')
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not file_path:
        return False, "File path cannot be empty"
    
    path = Path(file_path)
    
    if not path.exists():
        return False, f"File not found: {file_path}"
    
    if not path.is_file():
        return False, f"Path is not a file: {file_path}"
    
    # Check file format
    if file_type == 'image':
        if path.suffix.lower() not in SUPPORTED_IMAGE_FORMATS:
            return False, f"Unsupported image format. Supported: {SUPPORTED_IMAGE_FORMATS}"
    elif file_type == 'audio':
        if path.suffix.lower() not in SUPPORTED_AUDIO_FORMATS:
            return False, f"Unsupported audio format. Supported: {SUPPORTED_AUDIO_FORMATS}"
    
    return True, ""


def encode_image_to_base64(image_path: str) -> Optional[str]:
    """
    Encode an image file to base64 string.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Base64 encoded string or None if error
    """
    try:
        with open(image_path, 'rb') as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')
    except Exception as e:
        print(f"Error encoding image: {e}")
        return None


def resize_image(image_path: str, max_size: Tuple[int, int] = (800, 600)) -> Optional[str]:
    """
    Resize an image to fit within specified dimensions.
    
    Args:
        image_path: Path to the image file
        max_size: Maximum width and height
        
    Returns:
        Path to resized image or None if error
    """
    try:
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Resize if larger than max_size
            if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Save resized image
            output_path = Path(image_path).parent / f"resized_{Path(image_path).name}"
            img.save(output_path, quality=85, optimize=True)
            
            return str(output_path)
            
    except Exception as e:
        print(f"Error resizing image: {e}")
        return None


def create_visualization_summary(session_data: List[Dict[str, Any]], 
                               output_path: Optional[str] = None) -> str:
    """
    Create visualizations for session data.
    
    Args:
        session_data: List of interaction dictionaries
        output_path: Optional custom output path
        
    Returns:
        Path to the generated visualization file
    """
    if not session_data:
        raise ValueError("No session data provided for visualization")
    
    # Prepare data for visualization
    df_data = []
    for interaction in session_data:
        df_data.append({
            'timestamp': pd.to_datetime(interaction['timestamp']),
            'input_type': interaction['input_type'],
            'language': interaction.get('language', 'Unknown'),
            'success': interaction['result']['success'],
            'response_length': len(interaction['result'].get('response', ''))
        })
    
    df = pd.DataFrame(df_data)
    
    # Create visualizations
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Health Assistant Session Analysis', fontsize=16, fontweight='bold')
    
    # 1. Input types distribution
    input_type_counts = df['input_type'].value_counts()
    axes[0, 0].pie(input_type_counts.values, labels=input_type_counts.index, autopct='%1.1f%%')
    axes[0, 0].set_title('Distribution of Input Types')
    
    # 2. Language distribution
    language_counts = df['language'].value_counts()
    axes[0, 1].bar(language_counts.index, language_counts.values)
    axes[0, 1].set_title('Language Distribution')
    axes[0, 1].tick_params(axis='x', rotation=45)
    
    # 3. Success rate over time
    df['hour'] = df['timestamp'].dt.hour
    success_by_hour = df.groupby('hour')['success'].mean()
    axes[1, 0].plot(success_by_hour.index, success_by_hour.values, marker='o')
    axes[1, 0].set_title('Success Rate by Hour')
    axes[1, 0].set_xlabel('Hour of Day')
    axes[1, 0].set_ylabel('Success Rate')
    axes[1, 0].grid(True, alpha=0.3)
    
    # 4. Response length distribution
    axes[1, 1].hist(df['response_length'], bins=20, alpha=0.7, edgecolor='black')
    axes[1, 1].set_title('Response Length Distribution')
    axes[1, 1].set_xlabel('Response Length (characters)')
    axes[1, 1].set_ylabel('Frequency')
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save visualization
    if output_path:
        output_file = Path(output_path)
    else:
        output_file = OUTPUT_PATH / f"session_analysis_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.png"
    
    output_file.parent.mkdir(exist_ok=True)
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    return str(output_file)


def format_response_for_display(response_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format response data for better display.
    
    Args:
        response_data: Raw response data from the assistant
        
    Returns:
        Formatted response data
    """
    if not response_data.get('success', False):
        return {
            'status': 'error',
            'message': response_data.get('error', 'Unknown error occurred'),
            'input_type': response_data.get('input_type', 'unknown'),
            'timestamp': response_data.get('timestamp', '')
        }
    
    # Format successful response
    formatted_response = {
        'status': 'success',
        'response': response_data.get('response', ''),
        'input_type': response_data.get('input_type', 'unknown'),
        'timestamp': response_data.get('timestamp', ''),
        'language': response_data.get('language', 'en'),
        'word_count': len(response_data.get('response', '').split()),
        'character_count': len(response_data.get('response', ''))
    }
    
    # Add specific fields based on input type
    if response_data.get('input_type') == 'image':
        formatted_response['image_path'] = response_data.get('image_path', '')
        formatted_response['description'] = response_data.get('description', '')
    elif response_data.get('input_type') == 'audio':
        formatted_response['audio_path'] = response_data.get('audio_path', '')
    elif response_data.get('input_type') == 'comprehensive':
        formatted_response['input_types'] = response_data.get('input_types', [])
        formatted_response['individual_responses'] = response_data.get('individual_responses', [])
    
    return formatted_response


def create_sample_data() -> Dict[str, str]:
    """
    Create sample data for testing the health assistant.
    
    Returns:
        Dictionary containing sample text, image, and audio prompts
    """
    sample_data = {
        'text_queries': [
            "What are the common symptoms of dehydration?",
            "How can I improve my sleep quality?",
            "What should I do for a mild headache?",
            "What are the benefits of regular exercise?",
            "How can I manage stress and anxiety?",
            "What foods are good for boosting immunity?",
            "What are the warning signs of a heart attack?",
            "How can I maintain good posture while working?",
            "What are the symptoms of seasonal allergies?",
            "How can I improve my mental health?"
        ],
        'image_descriptions': [
            "A red rash on the arm",
            "A medication bottle label",
            "A bruise or injury",
            "A skin condition",
            "A medical device",
            "A wound or cut",
            "A mole or skin growth",
            "A swollen joint",
            "A rash on the face",
            "A medication pill"
        ],
        'audio_transcripts': [
            "I've been feeling dizzy and tired for the past few days",
            "My throat is sore and I have difficulty swallowing",
            "I have a persistent cough that won't go away",
            "My stomach has been upset and I feel nauseous",
            "I have a headache that started this morning",
            "My joints are stiff and painful",
            "I'm having trouble sleeping at night",
            "I feel anxious and stressed all the time",
            "My vision is blurry and my eyes hurt",
            "I have a fever and body aches"
        ],
        'multilingual_queries': {
            'hi': [
                "मुझे सिरदर्द हो रहा है, क्या करूं?",
                "थकान के लक्षण क्या हैं?",
                "बुखार के लिए क्या करना चाहिए?"
            ],
            'es': [
                "¿Qué debo hacer para un dolor de cabeza?",
                "¿Cuáles son los síntomas de la deshidratación?",
                "¿Cómo puedo mejorar mi sueño?"
            ],
            'fr': [
                "Que dois-je faire pour un mal de tête?",
                "Quels sont les symptômes de la déshydratation?",
                "Comment puis-je améliorer mon sommeil?"
            ]
        }
    }
    
    return sample_data


def save_sample_data(output_path: Optional[str] = None) -> str:
    """
    Save sample data to a JSON file.
    
    Args:
        output_path: Optional custom output path
        
    Returns:
        Path to the saved sample data file
    """
    sample_data = create_sample_data()
    
    if output_path:
        output_file = Path(output_path)
    else:
        output_file = OUTPUT_PATH / "sample_data.json"
    
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(sample_data, f, indent=2, ensure_ascii=False)
    
    return str(output_file)


def load_sample_data(file_path: str) -> Dict[str, Any]:
    """
    Load sample data from a JSON file.
    
    Args:
        file_path: Path to the sample data file
        
    Returns:
        Dictionary containing sample data
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading sample data: {e}")
        return create_sample_data()


def create_health_tips_database() -> Dict[str, List[str]]:
    """
    Create a database of general health tips by category.
    
    Returns:
        Dictionary containing health tips organized by category
    """
    health_tips = {
        'General Health': [
            "Stay hydrated by drinking 8-10 glasses of water daily",
            "Get 7-9 hours of quality sleep each night",
            "Maintain a balanced diet with plenty of fruits and vegetables",
            "Exercise regularly for at least 30 minutes daily",
            "Practice good hygiene habits"
        ],
        'Mental Health': [
            "Practice mindfulness and meditation",
            "Stay connected with friends and family",
            "Set realistic goals and celebrate small achievements",
            "Take breaks when feeling overwhelmed",
            "Seek professional help when needed"
        ],
        'Nutrition': [
            "Eat a variety of colorful fruits and vegetables",
            "Include lean proteins in your diet",
            "Limit processed foods and added sugars",
            "Don't skip meals, especially breakfast",
            "Listen to your body's hunger and fullness cues"
        ],
        'Exercise': [
            "Start with low-impact activities if you're a beginner",
            "Include both cardio and strength training",
            "Stretch before and after exercise",
            "Stay consistent with your routine",
            "Listen to your body and rest when needed"
        ],
        'Sleep': [
            "Maintain a consistent sleep schedule",
            "Create a relaxing bedtime routine",
            "Keep your bedroom cool, dark, and quiet",
            "Avoid screens 1-2 hours before bedtime",
            "Limit caffeine intake, especially in the afternoon"
        ],
        'Stress Management': [
            "Practice deep breathing exercises",
            "Take regular breaks throughout the day",
            "Engage in hobbies and activities you enjoy",
            "Learn to say no when necessary",
            "Consider talking to a therapist or counselor"
        ]
    }
    
    return health_tips 