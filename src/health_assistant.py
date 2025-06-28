"""
Health Assistant module for processing multimodal health queries.
Provides a unified interface for text, image, and audio health analysis.
"""
import json
import time
from typing import Dict, Any, Optional, List
from pathlib import Path

from .gemini_client import GeminiClient
from .config import (
    SUPPORTED_LANGUAGES, 
    HEALTH_DISCLAIMER, 
    HEALTH_CATEGORIES,
    OUTPUT_PATH
)


class HealthAssistant:
    """
    Main health assistant class that handles multimodal health queries.
    Supports text, image, and audio inputs with multilingual capabilities.
    """
    
    def __init__(self, credentials_path: Optional[str] = None, project_id: Optional[str] = None):
        """
        Initialize the health assistant.
        
        Args:
            credentials_path: Path to Google Cloud credentials
            project_id: Google Cloud project ID
        """
        self.gemini_client = GeminiClient(credentials_path, project_id)
        self.session_data = {
            'queries': [],
            'start_time': time.time(),
            'language_stats': {},
            'input_type_stats': {}
        }
        self.current_session_id = None
    
    def process_query(self, 
                     text_input: Optional[str] = None,
                     image_path: Optional[str] = None,
                     audio_path: Optional[str] = None,
                     language: str = 'en',
                     description: Optional[str] = None,
                     save_to_session: bool = True) -> Dict[str, Any]:
        """
        Process a health-related query with multimodal input support.
        
        Args:
            text_input: Optional text query
            image_path: Optional path to image file
            audio_path: Optional path to audio file
            language: Language code (en, hi, es)
            save_to_session: Whether to save this query to session
            
        Returns:
            Dictionary containing the response and metadata
        """
        # Validate language
        if language not in SUPPORTED_LANGUAGES:
            return {
                'success': False,
                'error': f"Unsupported language: {language}. Supported: {list(SUPPORTED_LANGUAGES.keys())}"
            }
        
        # Validate that at least one input is provided
        if not any([text_input, image_path, audio_path]):
            return {
                'success': False,
                'error': "At least one input (text, image, or audio) must be provided"
            }
        
        try:
            # Process the query based on input types
            if text_input and not image_path and not audio_path:
                # Text-only query
                result = self.gemini_client.process_text(text_input, language)
                input_type = 'text'
                
            elif image_path and not text_input and not audio_path:
                # Image-only query
                result = self.gemini_client.process_image(image_path, description)
                input_type = 'image'
                
            elif audio_path and not text_input and not image_path:
                # Audio-only query
                result = self.gemini_client.process_audio(audio_path, language)
                input_type = 'audio'
                
            else:
                # Multiple inputs - use combine_inputs
                result = self.gemini_client.combine_inputs(
                    text_input=text_input,
                    image_path=image_path,
                    audio_path=audio_path,
                    language=language
                )
                input_type = 'multimodal'
            
            # Add disclaimer to successful responses
            if result.get('success', False):
                result['response'] = f"{result['response']}\n\n{HEALTH_DISCLAIMER}"
            
            # Update session data
            if save_to_session:
                self._update_session_stats(language, input_type)
                self._save_query_to_session(result, input_type, language)
            
            return result
            
        except Exception as e:
            error_result = {
                'success': False,
                'error': f"Processing failed: {str(e)}",
                'input_type': 'unknown',
                'language': language,
                'timestamp': time.time()
            }
            
            if save_to_session:
                self._save_query_to_session(error_result, 'unknown', language)
            
            return error_result
    
    def get_health_tips(self, category: Optional[str] = None, language: str = 'en') -> Dict[str, Any]:
        """
        Get general health tips by category.
        
        Args:
            category: Health category (optional)
            language: Language code
            
        Returns:
            Dictionary containing health tips
        """
        if language not in SUPPORTED_LANGUAGES:
            return {
                'success': False,
                'error': f"Unsupported language: {language}"
            }
        
        if category and category not in HEALTH_CATEGORIES:
            return {
                'success': False,
                'error': f"Invalid category. Available: {HEALTH_CATEGORIES}"
            }
        
        # Create a prompt for health tips
        if category:
            prompt = f"Provide 5 helpful health tips about {category} in {SUPPORTED_LANGUAGES[language]}."
        else:
            prompt = f"Provide 5 general wellness tips in {SUPPORTED_LANGUAGES[language]}."
        
        return self.gemini_client.process_text(prompt, language)
    
    def get_session_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current session.
        
        Returns:
            Dictionary containing session statistics
        """
        if not self.session_data['queries']:
            return {
                'success': False,
                'error': "No queries in current session"
            }
        
        total_queries = len(self.session_data['queries'])
        session_duration = time.time() - self.session_data['start_time']
        
        # Calculate success rate
        successful_queries = sum(1 for q in self.session_data['queries'] if q.get('success', False))
        success_rate = (successful_queries / total_queries) * 100 if total_queries > 0 else 0
        
        return {
            'success': True,
            'total_queries': total_queries,
            'successful_queries': successful_queries,
            'success_rate': round(success_rate, 2),
            'session_duration_minutes': round(session_duration / 60, 2),
            'language_stats': self.session_data['language_stats'],
            'input_type_stats': self.session_data['input_type_stats'],
            'session_id': self.current_session_id
        }
    
    def save_session_to_file(self, filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Save the current session to a file.
        
        Args:
            filename: Optional filename (will generate one if not provided)
            
        Returns:
            Dictionary containing save status
        """
        if not filename:
            timestamp = int(time.time())
            filename = f"health_session_{timestamp}.json"
        
        filepath = OUTPUT_PATH / filename
        
        try:
            # Ensure output directory exists
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            # Save session data
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.session_data, f, indent=2, ensure_ascii=False, default=str)
            
            return {
                'success': True,
                'filepath': str(filepath),
                'message': f"Session saved to {filepath}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to save session: {str(e)}"
            }
    
    def load_session_from_file(self, filepath: str) -> Dict[str, Any]:
        """
        Load a session from a file.
        
        Args:
            filepath: Path to the session file
            
        Returns:
            Dictionary containing load status
        """
        try:
            session_data = json.load(open(filepath, 'r', encoding='utf-8'))
            
            self.session_data = session_data
            self.current_session_id = Path(filepath).stem
            return {
                'success': True,
                'message': f"Session loaded from {filepath}",
                'session_data': session_data
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to load session: {str(e)}"
            }
    
    def _update_session_stats(self, language: str, input_type: str):
        """Update session statistics."""
        # Update language stats
        if language not in self.session_data['language_stats']:
            self.session_data['language_stats'][language] = 0
        self.session_data['language_stats'][language] += 1
        
        # Update input type stats
        if input_type not in self.session_data['input_type_stats']:
            self.session_data['input_type_stats'][input_type] = 0
        self.session_data['input_type_stats'][input_type] += 1
    
    def _save_query_to_session(self, result: Dict[str, Any], input_type: str, language: str):
        """Save a query result to the session."""
        query_entry = {
            'timestamp': time.time(),
            'input_type': input_type,
            'language': language,
            'success': result.get('success', False),
            'response': result.get('response', ''),
            'error': result.get('error', '')
        }
        
        self.session_data['queries'].append(query_entry) 