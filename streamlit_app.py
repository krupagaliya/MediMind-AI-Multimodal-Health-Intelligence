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
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 Text", "🖼️ Image", "🎵 Audio", "💡 Health Tips", "🚨 Emergency"])
    
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
    
    # Emergency Tab
    with tab5:
        st.header("🚨 Emergency")
        
        # Emergency numbers section
        st.subheader("📞 Emergency Numbers")
        
        # Create columns for emergency numbers
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div style="background-color: #dc3545; color: white; padding: 1rem; border-radius: 5px; text-align: center; margin-bottom: 1rem;">
                <h2 style="color: white; margin: 0;">📞 108</h2>
                <p style="margin: 0;">National Medical Emergency (India)</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown("""
            <div style="background-color: #fd7e14; color: white; padding: 1rem; border-radius: 5px; text-align: center; margin-bottom: 1rem;">
                <h2 style="color: white; margin: 0;">📞 102</h2>
                <p style="margin: 0;">Ambulance Service (India)</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Additional emergency numbers
        st.subheader("🌍 Other Emergency Numbers")
        emergency_numbers = {
            "911": "Emergency Services (USA)",
            "112": "Emergency Services (Europe)"
        }
        
        for number, description in emergency_numbers.items():
            st.write(f"📞 **{number}**: {description}")
        
        st.markdown("---")
        
        # Hospital finder section
        st.subheader("🏥 Find Nearby Hospitals")
        
        # Add Google API key input
        google_api_key = st.text_input(
            "Enter Google Maps API Key",
            type="password",
            help="Required for finding nearby hospitals. Get your API key from Google Cloud Console."
        )
        
        # Help section for getting API key
        with st.expander("🔑 How to get Google Maps API Key"):
            st.markdown("""
            **Step-by-step guide to get your Google Maps API key:**
            
            1. **Go to Google Cloud Console**
               - Visit [Google Cloud Console](https://console.cloud.google.com/)
               - Select or create a project
            
            2. **Enable Required APIs**
               - Navigate to "APIs & Services" > "Library"
               - Search for and enable:
                 - **Places API** (for finding hospitals)
            
            3. **Create API Key**
               - Go to "APIs & Services" > "Credentials"
               - Click "Create Credentials" > "API Key"
               - Copy the generated API key
            
            4. **Secure Your API Key (Optional)**
               - Click on your API key to edit it
               - Under "API restrictions", select "Restrict key"
               - Choose: Places API
               - Set application restrictions as needed
            
            5. **Use Your API Key**
               - Paste the API key in the field above
               - Keep it secure and don't share publicly
            
            **💡 Tip:** The API key is free for moderate usage. 
            """)
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            search_radius = st.selectbox(
                "Search Radius",
                options=[1000, 2000, 5000, 10000],
                format_func=lambda x: f"{x/1000:.0f} km",
                index=1,
                help="Select the search radius for finding hospitals"
            )
        
        with col2:
            manual_location = st.checkbox(
                "Use manual location",
                help="Check this to enter custom coordinates instead of auto-detecting"
            )
        
        # Manual location inputs
        if manual_location:
            col1, col2 = st.columns(2)
            with col1:
                latitude = st.number_input("Latitude", value=0.0, format="%.6f")
            with col2:
                longitude = st.number_input("Longitude", value=0.0, format="%.6f")
        else:
            latitude = longitude = None
        
        if st.button("🔍 Find Hospitals", type="primary"):
            if not google_api_key:
                st.error("❌ Please enter your Google Maps API key")
            else:
                try:
                    # Import and initialize the emergency hospital finder
                    from src.emergency_hospital import EmergencyHospitalFinder
                    
                    finder = EmergencyHospitalFinder(google_api_key)
                    
                    with st.spinner("Finding nearby hospitals..."):
                        emergency_info = finder.get_emergency_info(
                            lat=latitude if manual_location else None,
                            lon=longitude if manual_location else None,
                            radius=search_radius
                        )
                    
                    if emergency_info["success"]:
                        if emergency_info["location"]:
                            st.success(f"📍 Location: {emergency_info['location']}")
                        
                        hospitals = emergency_info["hospitals"]
                        
                        if hospitals:
                            st.success(f"✅ Found {len(hospitals)} hospitals nearby")
                            
                            for idx, hospital in enumerate(hospitals, 1):
                                with st.expander(f"{idx}. {hospital['name']} (⭐ {hospital['rating']})"):
                                    st.write(f"📍 **Address**: {hospital['address']}")
                                    st.write(f"📞 **Phone**: {hospital['phone']}")
                                    
                                    if hospital['website'] != "Website not available":
                                        st.write(f"🌐 **Website**: {hospital['website']}")
                                    
                                    # Phone number as a clickable link
                                    if hospital['phone'] != "Phone not available":
                                        st.markdown(f"📞 [Call {hospital['phone']}](tel:{hospital['phone'].replace(' ', '').replace('(', '').replace(')', '').replace('-', '')})")
                                    
                                    if hospital['opening_hours']:
                                        st.write("🕐 **Opening Hours**:")
                                        for hours in hospital['opening_hours'][:3]:  # Show first 3 days
                                            st.write(f"   • {hours}")
                        else:
                            st.warning("❌ No hospitals found in the specified radius")
                    else:
                        st.error(f"❌ Error: {emergency_info['error']}")
                        
                except ImportError:
                    st.error("❌ Emergency module not found. Please ensure src/emergency_hospital.py exists.")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        
        # Important disclaimer
        st.markdown("---")
        st.markdown("""
        <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; padding: 1rem; margin: 1rem 0;">
            <h4 style="color: #856404; margin-top: 0;">⚠️ Emergency Disclaimer</h4>
            <p style="color: #856404; margin-bottom: 0;">
                In case of a medical emergency, call emergency services immediately. 
                This tool is for informational purposes only and should not delay emergency care.
            </p>
        </div>
        """, unsafe_allow_html=True)

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