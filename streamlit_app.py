"""
Streamlit Web Application for Multimodal Health Assistant
A modern web interface for the health assistant using Streamlit.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import json
import time
from datetime import datetime
import base64

from src.health_assistant import HealthAssistant
from src.utils import (
    validate_file_path,
    format_response_for_display,
    create_visualization_summary,
    save_sample_data,
    create_health_tips_database
)
from src.config import (
    HEALTH_DISCLAIMER,
    SUPPORTED_LANGUAGES,
    HEALTH_CATEGORIES,
    SUPPORTED_IMAGE_FORMATS,
    SUPPORTED_AUDIO_FORMATS
)


def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="🏥 Multimodal Health Assistant",
        page_icon="🏥",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #2c3e50;
        margin-bottom: 1rem;
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
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<h1 class="main-header">🏥 Multimodal Health Assistant</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Powered by Google Gemini 2.0 API • Text • Image • Audio Analysis</p>', unsafe_allow_html=True)
    
    # Disclaimer
    st.markdown('<div class="disclaimer">⚠️ <strong>IMPORTANT DISCLAIMER:</strong> This health assistant is for educational and informational purposes only. It is not a substitute for professional medical advice, diagnosis, or treatment. Always consult with a qualified healthcare provider for medical concerns.</div>', unsafe_allow_html=True)
    
    # Initialize session state
    if 'assistant' not in st.session_state:
        st.session_state.assistant = None
    if 'session_history' not in st.session_state:
        st.session_state.session_history = []
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Credentials upload
        st.subheader("🔐 Authentication")
        credentials_file = st.file_uploader(
            "Upload credentials JSON file",
            type=['json'],
            help="Upload your Google Cloud service account credentials"
        )
        
        if credentials_file:
            # Save credentials temporarily
            creds_path = Path("temp_credentials.json")
            with open(creds_path, "wb") as f:
                f.write(credentials_file.getvalue())
            
            # Initialize assistant
            if st.session_state.assistant is None:
                try:
                    st.session_state.assistant = HealthAssistant(str(creds_path))
                    st.success("✅ Health Assistant initialized successfully!")
                except Exception as e:
                    st.error(f"❌ Failed to initialize: {str(e)}")
                    st.session_state.assistant = None
        
        # Language selection
        st.subheader("🌍 Language")
        selected_language = st.selectbox(
            "Select language",
            options=list(SUPPORTED_LANGUAGES.keys()),
            format_func=lambda x: f"{x} - {SUPPORTED_LANGUAGES[x]}",
            index=0
        )
        
        # Session info
        if st.session_state.assistant:
            st.subheader("📊 Session Info")
            summary = st.session_state.assistant.get_session_summary()
            st.metric("Total Interactions", summary['total_interactions'])
            st.metric("Session Duration", f"{summary['session_duration']:.1f}s")
            
            if st.button("🔄 Reset Session"):
                st.session_state.assistant.reset_session()
                st.session_state.session_history = []
                st.rerun()
    
    # Main content
    if st.session_state.assistant is None:
        st.warning("⚠️ Please upload your credentials file in the sidebar to start using the Health Assistant.")
        st.info("💡 Don't have credentials? Check the README for setup instructions.")
        return
    
    # Tab selection
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🔍 Analysis", "📊 Analytics", "💡 Health Tips", "📁 Sample Data", "ℹ️ Help"
    ])
    
    with tab1:
        st.header("🔍 Health Analysis")
        
        # Input type selection
        analysis_type = st.selectbox(
            "Choose analysis type",
            ["Text Analysis", "Image Analysis", "Audio Analysis", "Comprehensive Analysis"]
        )
        
        if analysis_type == "Text Analysis":
            text_analysis_tab()
        elif analysis_type == "Image Analysis":
            image_analysis_tab()
        elif analysis_type == "Audio Analysis":
            audio_analysis_tab()
        elif analysis_type == "Comprehensive Analysis":
            comprehensive_analysis_tab()
    
    with tab2:
        analytics_tab()
    
    with tab3:
        health_tips_tab()
    
    with tab4:
        sample_data_tab()
    
    with tab5:
        help_tab()


def text_analysis_tab():
    """Text analysis tab."""
    st.subheader("📝 Text Analysis")
    
    # Text input
    text_input = st.text_area(
        "Enter your health question",
        placeholder="e.g., What are the symptoms of dehydration?",
        height=100
    )
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if st.button("🔍 Analyze Text", type="primary"):
            if text_input.strip():
                with st.spinner("Processing text analysis..."):
                    result = st.session_state.assistant.analyze_text(
                        text_input, 
                        st.session_state.get('selected_language', 'en')
                    )
                    display_result(result)
            else:
                st.error("Please enter a health question.")


def image_analysis_tab():
    """Image analysis tab."""
    st.subheader("🖼️ Image Analysis")
    
    # Image upload
    uploaded_image = st.file_uploader(
        "Upload an image",
        type=SUPPORTED_IMAGE_FORMATS,
        help=f"Supported formats: {', '.join(SUPPORTED_IMAGE_FORMATS)}"
    )
    
    # Image description
    description = st.text_input(
        "Image description (optional)",
        placeholder="e.g., Red rash on the arm"
    )
    
    if uploaded_image:
        # Display image
        st.image(uploaded_image, caption="Uploaded Image", use_column_width=True)
        
        # Save image temporarily
        temp_image_path = Path(f"temp_image_{int(time.time())}.{uploaded_image.name.split('.')[-1]}")
        with open(temp_image_path, "wb") as f:
            f.write(uploaded_image.getvalue())
        
        if st.button("🔍 Analyze Image", type="primary"):
            with st.spinner("Processing image analysis..."):
                result = st.session_state.assistant.analyze_image(str(temp_image_path), description)
                display_result(result)
                
                # Clean up temp file
                temp_image_path.unlink(missing_ok=True)


def audio_analysis_tab():
    """Audio analysis tab."""
    st.subheader("🎵 Audio Analysis")
    
    # Audio upload
    uploaded_audio = st.file_uploader(
        "Upload an audio file",
        type=SUPPORTED_AUDIO_FORMATS,
        help=f"Supported formats: {', '.join(SUPPORTED_AUDIO_FORMATS)}"
    )
    
    if uploaded_audio:
        # Display audio player
        st.audio(uploaded_audio)
        
        # Save audio temporarily
        temp_audio_path = Path(f"temp_audio_{int(time.time())}.{uploaded_audio.name.split('.')[-1]}")
        with open(temp_audio_path, "wb") as f:
            f.write(uploaded_audio.getvalue())
        
        if st.button("🔍 Analyze Audio", type="primary"):
            with st.spinner("Processing audio analysis..."):
                result = st.session_state.assistant.analyze_audio(
                    str(temp_audio_path), 
                    st.session_state.get('selected_language', 'en')
                )
                display_result(result)
                
                # Clean up temp file
                temp_audio_path.unlink(missing_ok=True)


def comprehensive_analysis_tab():
    """Comprehensive analysis tab."""
    st.subheader("🔍 Comprehensive Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        text_input = st.text_area(
            "Text query (optional)",
            placeholder="e.g., I've been feeling dizzy",
            height=100
        )
        
        uploaded_image = st.file_uploader(
            "Upload image (optional)",
            type=SUPPORTED_IMAGE_FORMATS,
            key="comp_image"
        )
    
    with col2:
        uploaded_audio = st.file_uploader(
            "Upload audio (optional)",
            type=SUPPORTED_AUDIO_FORMATS,
            key="comp_audio"
        )
        
        description = st.text_input(
            "Image description (optional)",
            placeholder="e.g., Medication bottle"
        )
    
    # Display uploaded files
    if uploaded_image:
        st.image(uploaded_image, caption="Uploaded Image", width=200)
    
    if uploaded_audio:
        st.audio(uploaded_audio)
    
    if st.button("🔍 Perform Comprehensive Analysis", type="primary"):
        if not any([text_input.strip(), uploaded_image, uploaded_audio]):
            st.error("Please provide at least one input (text, image, or audio).")
            return
        
        with st.spinner("Processing comprehensive analysis..."):
            # Save files temporarily
            temp_files = []
            
            image_path = None
            if uploaded_image:
                temp_image_path = Path(f"temp_comp_image_{int(time.time())}.{uploaded_image.name.split('.')[-1]}")
                with open(temp_image_path, "wb") as f:
                    f.write(uploaded_image.getvalue())
                image_path = str(temp_image_path)
                temp_files.append(temp_image_path)
            
            audio_path = None
            if uploaded_audio:
                temp_audio_path = Path(f"temp_comp_audio_{int(time.time())}.{uploaded_audio.name.split('.')[-1]}")
                with open(temp_audio_path, "wb") as f:
                    f.write(uploaded_audio.getvalue())
                audio_path = str(temp_audio_path)
                temp_files.append(temp_audio_path)
            
            # Perform analysis
            result = st.session_state.assistant.comprehensive_analysis(
                text_input=text_input.strip() if text_input.strip() else None,
                image_path=image_path,
                audio_path=audio_path,
                language=st.session_state.get('selected_language', 'en')
            )
            
            display_result(result)
            
            # Clean up temp files
            for temp_file in temp_files:
                temp_file.unlink(missing_ok=True)


def display_result(result):
    """Display analysis result."""
    formatted_result = format_response_for_display(result)
    
    if formatted_result['status'] == 'error':
        st.error(f"❌ Error: {formatted_result['message']}")
        return
    
    # Success message
    st.success("✅ Analysis completed successfully!")
    
    # Result details
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Input Type", formatted_result['input_type'].title())
    
    with col2:
        st.metric("Word Count", formatted_result['word_count'])
    
    with col3:
        st.metric("Character Count", formatted_result['character_count'])
    
    # Response
    st.subheader("📋 Analysis Result")
    st.markdown(formatted_result['response'])
    
    # Add to session history
    st.session_state.session_history.append({
        'timestamp': datetime.now(),
        'input_type': formatted_result['input_type'],
        'response': formatted_result['response'],
        'word_count': formatted_result['word_count']
    })


def analytics_tab():
    """Analytics tab."""
    st.header("📊 Analytics Dashboard")
    
    if not st.session_state.session_history:
        st.info("No session data available. Start analyzing to see analytics.")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(st.session_state.session_history)
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Interactions", len(df))
    
    with col2:
        st.metric("Average Word Count", f"{df['word_count'].mean():.1f}")
    
    with col3:
        st.metric("Total Words", df['word_count'].sum())
    
    with col4:
        st.metric("Session Duration", f"{(df['timestamp'].max() - df['timestamp'].min()).total_seconds():.1f}s")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Input type distribution
        input_type_counts = df['input_type'].value_counts()
        fig1 = px.pie(
            values=input_type_counts.values,
            names=input_type_counts.index,
            title="Input Type Distribution"
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Word count over time
        fig2 = px.line(
            df,
            x='timestamp',
            y='word_count',
            title="Response Length Over Time"
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    # Recent interactions table
    st.subheader("Recent Interactions")
    recent_df = df.tail(10)[['timestamp', 'input_type', 'word_count']].copy()
    recent_df['timestamp'] = recent_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    st.dataframe(recent_df, use_container_width=True)


def health_tips_tab():
    """Health tips tab."""
    st.header("💡 Health Tips")
    
    tips = create_health_tips_database()
    
    # Category selection
    selected_category = st.selectbox(
        "Select category",
        options=list(tips.keys())
    )
    
    # Display tips
    st.subheader(f"🏷️ {selected_category}")
    
    for i, tip in enumerate(tips[selected_category], 1):
        st.markdown(f"**{i}.** {tip}")
    
    # All tips expander
    with st.expander("📚 View All Health Tips"):
        for category, tip_list in tips.items():
            st.markdown(f"### {category}")
            for i, tip in enumerate(tip_list, 1):
                st.markdown(f"**{i}.** {tip}")
            st.markdown("---")


def sample_data_tab():
    """Sample data tab."""
    st.header("📁 Sample Data")
    
    if st.button("📄 Generate Sample Data"):
        with st.spinner("Generating sample data..."):
            output_path = save_sample_data()
            st.success(f"✅ Sample data saved to: {output_path}")
    
    # Display sample queries
    sample_data = {
        'text_queries': [
            "What are the common symptoms of dehydration?",
            "How can I improve my sleep quality?",
            "What should I do for a mild headache?",
            "What are the benefits of regular exercise?",
            "How can I manage stress and anxiety?"
        ],
        'multilingual_queries': {
            'hi': ["मुझे सिरदर्द हो रहा है, क्या करूं?", "थकान के लक्षण क्या हैं?"],
            'es': ["¿Qué debo hacer para un dolor de cabeza?", "¿Cuáles son los síntomas de la deshidratación?"],
            'fr': ["Que dois-je faire pour un mal de tête?", "Quels sont les symptômes de la déshydratation?"]
        }
    }
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📝 Sample Text Queries")
        for i, query in enumerate(sample_data['text_queries'], 1):
            st.markdown(f"**{i}.** {query}")
    
    with col2:
        st.subheader("🌍 Multilingual Queries")
        for lang_code, queries in sample_data['multilingual_queries'].items():
            lang_name = SUPPORTED_LANGUAGES.get(lang_code, lang_code)
            st.markdown(f"**{lang_name}:**")
            for query in queries:
                st.markdown(f"• {query}")


def help_tab():
    """Help tab."""
    st.header("ℹ️ Help & Documentation")
    
    st.subheader("🚀 Getting Started")
    st.markdown("""
    1. **Upload Credentials**: In the sidebar, upload your Google Cloud service account credentials JSON file
    2. **Choose Analysis Type**: Select the type of analysis you want to perform
    3. **Provide Input**: Enter text, upload images, or upload audio files
    4. **Get Results**: View the AI-generated health insights and recommendations
    """)
    
    st.subheader("📋 Supported Features")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Text Analysis:**
        - Health questions and queries
        - Symptom descriptions
        - General health advice
        
        **Image Analysis:**
        - Skin conditions and rashes
        - Medication labels
        - Medical devices
        - Wounds and injuries
        """)
    
    with col2:
        st.markdown("""
        **Audio Analysis:**
        - Spoken symptom descriptions
        - Voice recordings of health concerns
        - Multilingual audio support
        
        **Comprehensive Analysis:**
        - Combine multiple input types
        - Integrated health insights
        - Cross-modal analysis
        """)
    
    st.subheader("🌍 Supported Languages")
    lang_text = ", ".join([f"{code} ({name})" for code, name in SUPPORTED_LANGUAGES.items()])
    st.markdown(f"**Languages:** {lang_text}")
    
    st.subheader("📁 Supported File Formats")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"**Images:** {', '.join(SUPPORTED_IMAGE_FORMATS)}")
    
    with col2:
        st.markdown(f"**Audio:** {', '.join(SUPPORTED_AUDIO_FORMATS)}")
    
    st.subheader("⚠️ Important Notes")
    st.markdown("""
    - This assistant is for **educational purposes only**
    - **Not a substitute** for professional medical advice
    - Always consult healthcare professionals for medical concerns
    - Results are AI-generated and should be used with caution
    - Keep your credentials secure and never share them
    """)


if __name__ == "__main__":
    main() 