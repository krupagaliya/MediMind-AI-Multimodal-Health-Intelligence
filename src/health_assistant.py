"""
Main Health Assistant class that orchestrates multimodal health analysis.
Combines text, image, and audio processing for comprehensive health insights.
"""
import json
import time
from typing import Optional, Dict, Any, List, Union
from pathlib import Path
import pandas as pd
from datetime import datetime

from .gemini_client import GeminiClient
from .config import (
    SUPPORTED_IMAGE_FORMATS,
    SUPPORTED_AUDIO_FORMATS,
    HEALTH_DISCLAIMER,
    SUPPORTED_LANGUAGES,
    HEALTH_CATEGORIES,
    OUTPUT_PATH
)


class HealthAssistant:
    """
    Main class for the Multimodal Health Assistant.
    Handles text, image, and audio inputs to provide comprehensive health insights.
    """
    
    def __init__(self, credentials_path: Optional[str] = None, project_id: Optional[str] = None, location: str = "us-central1"):
        """
        Initialize the Health Assistant.
        
        Args:
            credentials_path: Path to the service account credentials JSON file
            project_id: Google Cloud project ID
            location: Google Cloud location (default: us-central1)
        """
        self.gemini_client = GeminiClient(credentials_path, project_id, location)
        self.session_history = []
        self.current_session_id = None
        
    def _validate_file_format(self, file_path: str, supported_formats: List[str]) -> bool:
        """
        Validate if a file format is supported.
        
        Args:
            file_path: Path to the file
            supported_formats: List of supported file extensions
            
        Returns:
            True if format is supported, False otherwise
        """
        file_ext = Path(file_path).suffix.lower()
        return file_ext in supported_formats
    
    def _generate_session_id(self) -> str:
        """Generate a unique session ID for tracking interactions."""
        return f"session_{int(time.time())}_{len(self.session_history)}"
    
    def _log_interaction(self, interaction_data: Dict[str, Any]):
        """Log an interaction to the session history."""
        if not self.current_session_id:
            self.current_session_id = self._generate_session_id()
        
        interaction_data['session_id'] = self.current_session_id
        interaction_data['timestamp'] = datetime.now().isoformat()
        self.session_history.append(interaction_data)
    
    def analyze_text(self, text: str, language: str = 'en') -> Dict[str, Any]:
        """
        Analyze text input for health-related queries.
        
        Args:
            text: The text query to analyze
            language: Language code for the input text
            
        Returns:
            Dictionary containing analysis results
        """
        if not text.strip():
            return {
                'success': False,
                'error': 'Text input cannot be empty',
                'input_type': 'text'
            }
        
        if language not in SUPPORTED_LANGUAGES:
            return {
                'success': False,
                'error': f'Unsupported language: {language}',
                'input_type': 'text'
            }
        
        # Process the text
        result = self.gemini_client.process_text(text, language)
        
        # Log the interaction
        self._log_interaction({
            'input_type': 'text',
            'input_data': text,
            'language': language,
            'result': result
        })
        
        return result
    
    def analyze_image(self, image_path: str, description: str = "") -> Dict[str, Any]:
        """
        Analyze image input for health-related content.
        
        Args:
            image_path: Path to the image file
            description: Optional description of the image
            
        Returns:
            Dictionary containing analysis results
        """
        if not self._validate_file_format(image_path, SUPPORTED_IMAGE_FORMATS):
            return {
                'success': False,
                'error': f'Unsupported image format. Supported formats: {SUPPORTED_IMAGE_FORMATS}',
                'input_type': 'image'
            }
        
        if not Path(image_path).exists():
            return {
                'success': False,
                'error': f'Image file not found: {image_path}',
                'input_type': 'image'
            }
        
        # Process the image
        result = self.gemini_client.process_image(image_path, description)
        
        # Log the interaction
        self._log_interaction({
            'input_type': 'image',
            'input_data': image_path,
            'description': description,
            'result': result
        })
        
        return result
    
    def analyze_audio(self, audio_path: str, language: str = 'en') -> Dict[str, Any]:
        """
        Analyze audio input for health-related content.
        
        Args:
            audio_path: Path to the audio file
            language: Expected language of the audio content
            
        Returns:
            Dictionary containing analysis results
        """
        if not self._validate_file_format(audio_path, SUPPORTED_AUDIO_FORMATS):
            return {
                'success': False,
                'error': f'Unsupported audio format. Supported formats: {SUPPORTED_AUDIO_FORMATS}',
                'input_type': 'audio'
            }
        
        if not Path(audio_path).exists():
            return {
                'success': False,
                'error': f'Audio file not found: {audio_path}',
                'input_type': 'audio'
            }
        
        if language not in SUPPORTED_LANGUAGES:
            return {
                'success': False,
                'error': f'Unsupported language: {language}',
                'input_type': 'audio'
            }
        
        # Process the audio
        result = self.gemini_client.process_audio(audio_path, language)
        
        # Log the interaction
        self._log_interaction({
            'input_type': 'audio',
            'input_data': audio_path,
            'language': language,
            'result': result
        })
        
        return result
    
    def comprehensive_analysis(self,
                             text_input: Optional[str] = None,
                             image_path: Optional[str] = None,
                             audio_path: Optional[str] = None,
                             language: str = 'en') -> Dict[str, Any]:
        """
        Perform comprehensive analysis combining multiple input types.
        
        Args:
            text_input: Optional text query
            image_path: Optional path to image file
            audio_path: Optional path to audio file
            language: Language for processing
            
        Returns:
            Dictionary containing comprehensive analysis results
        """
        # Validate inputs
        inputs_provided = []
        
        if text_input:
            inputs_provided.append('text')
        
        if image_path:
            if not self._validate_file_format(image_path, SUPPORTED_IMAGE_FORMATS):
                return {
                    'success': False,
                    'error': f'Unsupported image format. Supported formats: {SUPPORTED_IMAGE_FORMATS}',
                    'input_types': inputs_provided
                }
            if not Path(image_path).exists():
                return {
                    'success': False,
                    'error': f'Image file not found: {image_path}',
                    'input_types': inputs_provided
                }
            inputs_provided.append('image')
        
        if audio_path:
            if not self._validate_file_format(audio_path, SUPPORTED_AUDIO_FORMATS):
                return {
                    'success': False,
                    'error': f'Unsupported audio format. Supported formats: {SUPPORTED_AUDIO_FORMATS}',
                    'input_types': inputs_provided
                }
            if not Path(audio_path).exists():
                return {
                    'success': False,
                    'error': f'Audio file not found: {audio_path}',
                    'input_types': inputs_provided
                }
            inputs_provided.append('audio')
        
        if not inputs_provided:
            return {
                'success': False,
                'error': 'No valid inputs provided',
                'input_types': []
            }
        
        if language not in SUPPORTED_LANGUAGES:
            return {
                'success': False,
                'error': f'Unsupported language: {language}',
                'input_types': inputs_provided
            }
        
        # Perform comprehensive analysis
        result = self.gemini_client.combine_inputs(
            text_input=text_input,
            image_path=image_path,
            audio_path=audio_path,
            language=language
        )
        
        # Log the interaction
        self._log_interaction({
            'input_type': 'comprehensive',
            'text_input': text_input,
            'image_path': image_path,
            'audio_path': audio_path,
            'language': language,
            'result': result
        })
        
        return result
    
    def get_session_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current session.
        
        Returns:
            Dictionary containing session summary
        """
        if not self.session_history:
            return {
                'session_id': None,
                'total_interactions': 0,
                'interactions_by_type': {},
                'session_duration': 0
            }
        
        # Calculate session statistics
        interactions_by_type = {}
        for interaction in self.session_history:
            input_type = interaction['input_type']
            interactions_by_type[input_type] = interactions_by_type.get(input_type, 0) + 1
        
        # Calculate session duration
        if len(self.session_history) >= 2:
            start_time = datetime.fromisoformat(self.session_history[0]['timestamp'])
            end_time = datetime.fromisoformat(self.session_history[-1]['timestamp'])
            session_duration = (end_time - start_time).total_seconds()
        else:
            session_duration = 0
        
        return {
            'session_id': self.current_session_id,
            'total_interactions': len(self.session_history),
            'interactions_by_type': interactions_by_type,
            'session_duration': session_duration,
            'start_time': self.session_history[0]['timestamp'] if self.session_history else None,
            'end_time': self.session_history[-1]['timestamp'] if self.session_history else None
        }
    
    def export_session_data(self, output_path: Optional[str] = None) -> str:
        """
        Export session data to JSON and CSV files.
        
        Args:
            output_path: Optional custom output path
            
        Returns:
            Path to the exported files
        """
        if not self.session_history:
            raise ValueError("No session data to export")
        
        # Generate output filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_id = self.current_session_id or f"session_{timestamp}"
        
        if output_path:
            output_dir = Path(output_path)
        else:
            output_dir = OUTPUT_PATH
        
        output_dir.mkdir(exist_ok=True)
        
        # Export to JSON
        json_path = output_dir / f"{session_id}_data.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({
                'session_summary': self.get_session_summary(),
                'interactions': self.session_history
            }, f, indent=2, ensure_ascii=False)
        
        # Export to CSV
        csv_path = output_dir / f"{session_id}_interactions.csv"
        df_data = []
        for interaction in self.session_history:
            row = {
                'timestamp': interaction['timestamp'],
                'input_type': interaction['input_type'],
                'language': interaction.get('language', ''),
                'success': interaction['result']['success'],
                'response_length': len(interaction['result'].get('response', ''))
            }
            
            # Add input data (truncated for CSV)
            if interaction['input_type'] == 'text':
                row['input_data'] = interaction['input_data'][:100] + '...' if len(interaction['input_data']) > 100 else interaction['input_data']
            else:
                row['input_data'] = interaction['input_data']
            
            df_data.append(row)
        
        df = pd.DataFrame(df_data)
        df.to_csv(csv_path, index=False, encoding='utf-8')
        
        return str(output_dir)
    
    def reset_session(self):
        """Reset the current session and clear history."""
        self.session_history = []
        self.current_session_id = None
    
    def get_health_disclaimer(self) -> str:
        """Get the health disclaimer text."""
        return HEALTH_DISCLAIMER
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get the list of supported languages."""
        return SUPPORTED_LANGUAGES.copy()
    
    def get_health_categories(self) -> List[str]:
        """Get the list of health categories."""
        return HEALTH_CATEGORIES.copy() 