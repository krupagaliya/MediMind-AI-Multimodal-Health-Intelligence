"""
Gemini API Client for the Multimodal Health Assistant.
Handles authentication and API interactions with Google's Gemini 2.0 model.
"""
import json
import os
import time
from typing import Optional, Dict, Any, List
from pathlib import Path

from google import genai
from google.genai import types

from .config import (
    CREDENTIALS_PATH, 
    GEMINI_MODEL_NAME, 
    MAX_TOKENS, 
    TEMPERATURE,
    MAX_REQUESTS_PER_MINUTE,
    REQUEST_TIMEOUT
)


class GeminiClient:
    """
    Client for interacting with Google's Gemini 2.0 API.
    Handles text, image, and audio processing for health-related queries.
    """
    
    def __init__(self, credentials_path: Optional[str] = None, project_id: Optional[str] = None, location: str = "us-central1"):
        """
        Initialize the Gemini client with authentication.
        
        Args:
            credentials_path: Path to the service account credentials JSON file
            project_id: Google Cloud project ID
            location: Google Cloud location (default: us-central1)
        """
        self.credentials_path = credentials_path or str(CREDENTIALS_PATH)
        self.project_id = project_id
        self.location = location
        self.client = None
        self.last_request_time = 0
        self.request_count = 0
        self.request_window_start = time.time()
        
        self._authenticate()
        self._initialize_client()
    
    def _authenticate(self):
        """Authenticate with Google Cloud using environment variables."""
        try:
            if not os.path.exists(self.credentials_path):
                raise FileNotFoundError(
                    f"Credentials file not found at {self.credentials_path}. "
                    "Please ensure your cred.json file is properly configured."
                )
            
            # Set environment variables for authentication
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.credentials_path
            
            # Set project ID if provided
            if self.project_id:
                os.environ["GOOGLE_CLOUD_PROJECT"] = self.project_id
            else:
                # Try to get project ID from credentials file
                try:
                    with open(self.credentials_path, 'r') as f:
                        creds_data = json.load(f)
                        project_id = creds_data.get('project_id')
                        if project_id:
                            os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
                            self.project_id = project_id
                        else:
                            raise ValueError("Project ID not found in credentials file")
                except Exception as e:
                    raise ValueError(f"Could not determine project ID: {e}")
                
            print(f"✅ Successfully configured authentication for project: {self.project_id}")
            
        except Exception as e:
            raise Exception(f"Authentication failed: {str(e)}")
    
    def _initialize_client(self):
        """Initialize the Gemini client."""
        try:
            # Create client for Vertex AI API
            self.client = genai.Client(
                vertexai=True, 
                project=self.project_id, 
                location=self.location
            )
            print(f"✅ Successfully initialized Gemini client for Vertex AI")
            print(f"   Project: {self.project_id}")
            print(f"   Location: {self.location}")
            
        except Exception as e:
            raise Exception(f"Failed to initialize Gemini client: {str(e)}")
    
    def _rate_limit(self):
        """Implement rate limiting for API requests."""
        current_time = time.time()
        
        # Reset counter if window has passed
        if current_time - self.request_window_start >= 60:
            self.request_count = 0
            self.request_window_start = current_time
        
        # Check if we're at the limit
        if self.request_count >= MAX_REQUESTS_PER_MINUTE:
            sleep_time = 60 - (current_time - self.request_window_start)
            if sleep_time > 0:
                print(f"Rate limit reached. Waiting {sleep_time:.1f} seconds...")
                time.sleep(sleep_time)
                self.request_count = 0
                self.request_window_start = time.time()
        
        # Ensure minimum time between requests
        time_since_last = current_time - self.last_request_time
        if time_since_last < (60 / MAX_REQUESTS_PER_MINUTE):
            time.sleep((60 / MAX_REQUESTS_PER_MINUTE) - time_since_last)
        
        self.last_request_time = time.time()
        self.request_count += 1
    
    def process_text(self, text: str, language: str = 'en') -> Dict[str, Any]:
        """
        Process text input for health-related queries.
        
        Args:
            text: The text query to process
            language: Language code for the input text
            
        Returns:
            Dictionary containing the response and metadata
        """
        self._rate_limit()
        
        try:
            # Create a health-focused prompt
            prompt = f"""
            You are a helpful health assistant. Please provide informative and helpful 
            responses to health-related questions. Always include appropriate disclaimers 
            about consulting healthcare professionals.
            
            User Query ({language}): {text}
            
            Please provide:
            1. A helpful response to the query
            2. Relevant health information
            3. When to seek professional medical help
            4. General wellness tips if applicable
            
            Remember: This is for educational purposes only and not a substitute for medical advice.
            """
            
            response = self.client.models.generate_content(
                model=GEMINI_MODEL_NAME,
                contents=prompt
            )
            
            return {
                'success': True,
                'response': response.text,
                'input_type': 'text',
                'language': language,
                'timestamp': time.time()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'input_type': 'text',
                'language': language,
                'timestamp': time.time()
            }
    
    def process_image(self, image_path: str, description: str = "") -> Dict[str, Any]:
        """
        Process image input for health-related analysis.
        
        Args:
            image_path: Path to the image file
            description: Optional description of the image
            
        Returns:
            Dictionary containing the response and metadata
        """
        self._rate_limit()
        
        try:
            # Load and prepare the image
            image_path = Path(image_path)
            if not image_path.exists():
                raise FileNotFoundError(f"Image file not found: {image_path}")
            
            with open(image_path, 'rb') as img_file:
                image_data = img_file.read()
            
            # Create a health-focused prompt for image analysis
            prompt = f"""
            You are a health assistant analyzing an image. Please provide helpful 
            observations about what you see in the image, especially if it appears 
            to be health-related (symptoms, medications, medical devices, etc.).
            
            User Description: {description}
            
            Please provide:
            1. What you observe in the image
            2. Potential health implications (if any)
            3. General advice (if applicable)
            4. When to seek professional medical help
            
            IMPORTANT: This analysis is for educational purposes only. 
            Always consult healthcare professionals for proper diagnosis and treatment.
            """
            
            # Create content with text and image
            contents = [
                prompt,
                types.Part.from_data(image_data, mime_type="image/jpeg")
            ]
            
            # Generate content with image
            response = self.client.models.generate_content(
                model=GEMINI_MODEL_NAME,
                contents=contents
            )
            
            return {
                'success': True,
                'response': response.text,
                'input_type': 'image',
                'image_path': str(image_path),
                'description': description,
                'timestamp': time.time()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'input_type': 'image',
                'image_path': str(image_path) if 'image_path' in locals() else image_path,
                'description': description,
                'timestamp': time.time()
            }
    
    def process_audio(self, audio_path: str, language: str = 'en') -> Dict[str, Any]:
        """
        Process audio input for health-related queries.
        
        Args:
            audio_path: Path to the audio file
            language: Expected language of the audio content
            
        Returns:
            Dictionary containing the response and metadata
        """
        self._rate_limit()
        
        try:
            # Load and prepare the audio
            audio_path = Path(audio_path)
            if not audio_path.exists():
                raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
            with open(audio_path, 'rb') as audio_file:
                audio_data = audio_file.read()
            
            # Create a health-focused prompt for audio analysis
            prompt = f"""
            You are a health assistant analyzing audio content. Please provide helpful 
            responses to health-related questions or concerns mentioned in the audio.
            
            Expected Language: {language}
            
            Please provide:
            1. A summary of the health concern described
            2. Helpful information and advice
            3. When to seek professional medical help
            4. General wellness recommendations if applicable
            
            IMPORTANT: This analysis is for educational purposes only. 
            Always consult healthcare professionals for proper diagnosis and treatment.
            """
            
            # Create content with text and audio
            contents = [
                prompt,
                types.Part.from_data(audio_data, mime_type="audio/wav")
            ]
            
            # Generate content with audio
            response = self.client.models.generate_content(
                model=GEMINI_MODEL_NAME,
                contents=contents
            )
            
            return {
                'success': True,
                'response': response.text,
                'input_type': 'audio',
                'audio_path': str(audio_path),
                'language': language,
                'timestamp': time.time()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'input_type': 'audio',
                'audio_path': str(audio_path) if 'audio_path' in locals() else audio_path,
                'language': language,
                'timestamp': time.time()
            }
    
    def combine_inputs(self, 
                      text_input: Optional[str] = None,
                      image_path: Optional[str] = None,
                      audio_path: Optional[str] = None,
                      language: str = 'en') -> Dict[str, Any]:
        """
        Combine multiple inputs for comprehensive health analysis.
        
        Args:
            text_input: Optional text query
            image_path: Optional path to image file
            audio_path: Optional path to audio file
            language: Language for processing
            
        Returns:
            Dictionary containing the combined response and metadata
        """
        self._rate_limit()
        
        try:
            responses = []
            inputs_processed = []
            
            # Process text input
            if text_input:
                text_response = self.process_text(text_input, language)
                responses.append(f"Text Analysis: {text_response['response']}")
                inputs_processed.append('text')
            
            # Process image input
            if image_path:
                image_response = self.process_image(image_path)
                responses.append(f"Image Analysis: {image_response['response']}")
                inputs_processed.append('image')
            
            # Process audio input
            if audio_path:
                audio_response = self.process_audio(audio_path, language)
                responses.append(f"Audio Analysis: {audio_response['response']}")
                inputs_processed.append('audio')
            
            if not responses:
                raise ValueError("No inputs provided for processing")
            
            # Combine all responses
            individual_analyses = '\n\n'.join(responses)
            
            combined_prompt = f"""
            You are a comprehensive health assistant. Below are analyses from different 
            types of inputs (text, image, audio). Please provide a unified, helpful response 
            that integrates all the information provided.
            
            Inputs Processed: {', '.join(inputs_processed)}
            Language: {language}
            
            Individual Analyses: {individual_analyses}
            
            Please provide:
            1. A comprehensive summary of all inputs
            2. Integrated health insights and recommendations
            3. Priority actions to take
            4. When to seek professional medical help
            5. General wellness advice
            
            IMPORTANT: This is for educational purposes only. 
            Always consult healthcare professionals for proper diagnosis and treatment.
            """
            
            combined_response = self.client.models.generate_content(
                model=GEMINI_MODEL_NAME,
                contents=combined_prompt
            )
            
            return {
                'success': True,
                'response': combined_response.text,
                'input_types': inputs_processed,
                'language': language,
                'individual_responses': responses,
                'timestamp': time.time()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'input_types': inputs_processed if 'inputs_processed' in locals() else [],
                'language': language,
                'timestamp': time.time()
            } 