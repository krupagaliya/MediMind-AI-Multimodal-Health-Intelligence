import streamlit as st
import json
import time
from pathlib import Path
from datetime import datetime
import tempfile
import os
import uuid

from src.health_assistant import HealthAssistant
from src.config import SUPPORTED_LANGUAGES, HEALTH_CATEGORIES, HEALTH_DISCLAIMER


def main():
    st.set_page_config(
        page_title="MediMind AI - Health Assistant",
        page_icon="🏥",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .disclaimer {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<h1 class="main-header">🏥 MediMind AI - Health Assistant</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem;">Powered by Google Gemini 2.0 API</p>', unsafe_allow_html=True)
    
    # Disclaimer
    st.markdown('<div class="disclaimer">⚠️ <strong>IMPORTANT DISCLAIMER:</strong> This health assistant is for educational and informational purposes only. It is not a substitute for professional medical advice, diagnosis, or treatment. Always consult with a qualified healthcare provider for medical concerns.</div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Language selection
        language = st.selectbox(
            "Select Language",
            options=list(SUPPORTED_LANGUAGES.keys()),
            format_func=lambda x: SUPPORTED_LANGUAGES[x],
            index=0
        )
        
        # Credentials
        st.subheader("🔐 Authentication")
        
        uploaded_credentials = st.file_uploader(
            "Upload credentials JSON file",
            type=['json'],
            help="Upload your Google Cloud credentials JSON file"
        )
        
        # Session management
        st.subheader("💾 Session")
        if st.button("Save Session"):
            if 'assistant' in st.session_state:
                result = st.session_state.assistant.save_session_to_file()
                if result['success']:
                    st.success(f"Session saved to: {result['filepath']}")
                else:
                    st.error(f"Failed to save session: {result['error']}")
            else:
                st.error("No active session to save")
        
        if st.button("Show Session Summary"):
            if 'assistant' in st.session_state:
                summary = st.session_state.assistant.get_session_summary()
                if summary['success']:
                    st.json(summary)
                else:
                    st.error(f"Error getting summary: {summary['error']}")
            else:
                st.error("No active session")
    
    # Main content
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Text", "🖼️ Image", "🎵 Audio", "💡 Health Tips"])
    
    # Initialize assistant
    if 'assistant' not in st.session_state:
        # Only initialize if we have credentials
        if uploaded_credentials is not None:
            try:
                # Parse and validate JSON
                try:
                    credentials_data = json.loads(uploaded_credentials.getvalue().decode('utf-8'))
                except json.JSONDecodeError:
                    st.error("❌ Invalid JSON file. Please upload a valid credentials JSON file.")
                    st.stop()
                
                # Extract project ID from credentials
                project_id = credentials_data.get('project_id')
                if not project_id:
                    st.error("❌ Project ID not found in credentials JSON file. Please ensure your credentials file contains a 'project_id' field.")
                    st.stop()
                
                # Create a temporary file for uploaded credentials
                temp_dir = Path(tempfile.gettempdir()) / "medimind_credentials"
                temp_dir.mkdir(exist_ok=True)
                
                # Create a unique filename
                temp_filename = f"credentials_{uuid.uuid4().hex}.json"
                tmp_credentials_path = temp_dir / temp_filename
                
                # Write credentials to temporary file
                with open(tmp_credentials_path, 'w') as f:
                    json.dump(credentials_data, f)
                st.session_state.temp_credentials_path = str(tmp_credentials_path)
                
                st.session_state.assistant = HealthAssistant(str(tmp_credentials_path), project_id)
                st.success(f"✅ Health Assistant initialized successfully with project: {project_id}")
            except Exception as e:
                st.error(f"❌ Failed to initialize Health Assistant: {str(e)}")
                st.stop()
        else:
            # Show instructions if credentials are missing
            st.warning("⚠️ Please upload your Google Cloud credentials JSON file in the sidebar")
    
    # Text Analysis Tab
    with tab1:
        st.header("📝 Text Analysis")
        
        text_input = st.text_area(
            "Enter your health question:",
            height=150,
            placeholder="e.g., What are the symptoms of a common cold?"
        )
        
        if st.button("Analyze Text", type="primary"):
            if text_input.strip():
                with st.spinner("Processing text analysis..."):
                    result = st.session_state.assistant.process_query(
                        text_input=text_input,
                        language=language
                    )
                
                if result['success']:
                    st.markdown('<div class="success-box">', unsafe_allow_html=True)
                    st.markdown("### Analysis Result")
                    st.write(result['response'])
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="error-box">', unsafe_allow_html=True)
                    st.error(f"Error: {result['error']}")
                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.error("Please enter a text query")
    
    # Image Analysis Tab
    with tab2:
        st.header("🖼️ Image Analysis")
        
        uploaded_file = st.file_uploader(
            "Upload an image",
            type=['jpg', 'jpeg', 'png', 'bmp', 'tiff', 'webp'],
            help="Upload a health-related image for analysis"
        )
        
        description = st.text_input(
            "Image description (optional):",
            placeholder="e.g., Red rash on arm, medication bottle, etc."
        )
        
        if uploaded_file is not None:
            st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
            
            if st.button("Analyze Image", type="primary"):
                # Save uploaded file temporarily
                temp_path = Path("temp_image") / uploaded_file.name
                temp_path.parent.mkdir(exist_ok=True)
                
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                with st.spinner("Processing image analysis..."):
                    result = st.session_state.assistant.process_query(
                        image_path=str(temp_path),
                        description=description,
                        language=language
                    )
                
                # Clean up temp file
                temp_path.unlink(missing_ok=True)
                
                if result['success']:
                    st.markdown('<div class="success-box">', unsafe_allow_html=True)
                    st.markdown("### Analysis Result")
                    st.write(result['response'])
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="error-box">', unsafe_allow_html=True)
                    st.error(f"Error: {result['error']}")
                    st.markdown('</div>', unsafe_allow_html=True)
    
    # Audio Analysis Tab
    with tab3:
        st.header("🎵 Audio Analysis")
        
        audio_file = st.file_uploader(
            "Upload an audio file",
            type=['wav', 'mp3', 'm4a', 'flac', 'ogg'],
            help="Upload an audio file with health-related content"
        )
        
        if audio_file is not None:
            st.audio(audio_file)
            
            if st.button("Analyze Audio", type="primary"):
                # Save uploaded file temporarily
                temp_path = Path("temp_audio") / audio_file.name
                temp_path.parent.mkdir(exist_ok=True)
                
                with open(temp_path, "wb") as f:
                    f.write(audio_file.getbuffer())
                
                with st.spinner("Processing audio analysis..."):
                    result = st.session_state.assistant.process_query(
                        audio_path=str(temp_path),
                        language=language
                    )
                
                # Clean up temp file
                temp_path.unlink(missing_ok=True)
                
                if result['success']:
                    st.markdown('<div class="success-box">', unsafe_allow_html=True)
                    st.markdown("### Analysis Result")
                    st.write(result['response'])
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="error-box">', unsafe_allow_html=True)
                    st.error(f"Error: {result['error']}")
                    st.markdown('</div>', unsafe_allow_html=True)
    
    # Health Tips Tab
    with tab4:
        st.header("💡 Health Tips")
        
        category = st.selectbox(
            "Select Health Category",
            options=["General"] + HEALTH_CATEGORIES,
            help="Choose a specific health category for tips"
        )
        
        if st.button("Get Health Tips", type="primary"):
            with st.spinner("Getting health tips..."):
                if category == "General":
                    result = st.session_state.assistant.get_health_tips(language=language)
                else:
                    result = st.session_state.assistant.get_health_tips(
                        category=category,
                        language=language
                    )
            
            if result['success']:
                st.markdown('<div class="success-box">', unsafe_allow_html=True)
                st.markdown(f"### Health Tips - {category}")
                st.write(result['response'])
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="error-box">', unsafe_allow_html=True)
                st.error(f"Error: {result['error']}")
                st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<p style='text-align: center; color: #666;'>MediMind AI - Powered by Google Gemini 2.0 API</p>",
        unsafe_allow_html=True
    )


def cleanup_temp_credentials():
    """Clean up temporary credentials files."""
    if 'temp_credentials_path' in st.session_state and st.session_state.temp_credentials_path:
        try:
            temp_path = Path(st.session_state.temp_credentials_path)
            if temp_path.exists():
                temp_path.unlink()
                # Also try to remove the temp directory if it's empty
                temp_dir = temp_path.parent
                if temp_dir.exists() and not any(temp_dir.iterdir()):
                    temp_dir.rmdir()
        except Exception:
            pass  # Ignore cleanup errors


if __name__ == "__main__":
    main() 