# 🏥 Multimodal Health Assistant

A comprehensive health assistant powered by Google's Gemini 2.0 API that can analyze text, images, and audio to provide health-related insights and recommendations.

## 🌟 Features

- **📝 Text Analysis**: Answer health questions and provide medical information
- **🖼️ Image Analysis**: Analyze health-related images (rashes, medications, medical devices)
- **🎵 Audio Analysis**: Process spoken health concerns and symptoms
- **🔍 Comprehensive Analysis**: Combine multiple input types for detailed insights
- **🌍 Multilingual Support**: Support for English, Hindi, Spanish, French, German, Japanese, Korean, and Chinese
- **📊 Analytics Dashboard**: Track usage patterns and generate insights
- **💡 Health Tips Database**: Curated health advice by category
- **🔄 Session Management**: Track interactions and export data
- **⚡ Rate Limiting**: Built-in API rate limiting and error handling

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Google Cloud Platform account with Vertex AI enabled
- Gemini 2.0 API access

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd multimodal-health-assistant
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up credentials**
   - Download your Google Cloud service account credentials JSON file
   - Place it in the project root as `cred.json`
   - Or specify a custom path using the `--credentials` flag

4. **Run the application**

   **Command Line Interface:**
   ```bash
   # Interactive mode
   python main.py --interactive
   
   # Text analysis
   python main.py --text "What causes headaches?"
   
   # Image analysis
   python main.py --image rash.jpg --description "Red rash on arm"
   
   # Audio analysis
   python main.py --audio symptoms.wav --language hi
   
   # Comprehensive analysis
   python main.py --comprehensive --text "I feel dizzy" --image medication.jpg
   ```

   **Web Interface:**
   ```bash
   streamlit run streamlit_app.py
   ```

   **Demo:**
   ```bash
   # Quick demo
   python examples/demo.py --quick
   
   # Full demo
   python examples/demo.py
   ```

## 📁 Project Structure

```
multimodal-health-assistant/
├── src/
│   ├── __init__.py
│   ├── config.py              # Configuration settings
│   ├── gemini_client.py       # Gemini API client
│   ├── health_assistant.py    # Main health assistant class
│   └── utils.py               # Utility functions
├── examples/
│   └── demo.py                # Demo script
├── main.py                    # Command-line interface
├── streamlit_app.py           # Web interface
├── requirements.txt           # Python dependencies
├── cred.json                  # Google Cloud credentials
└── README.md                  # This file
```

## 🔧 Configuration

### Credentials Setup

1. **Create a Google Cloud Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one

2. **Enable APIs**
   - Enable Vertex AI API
   - Enable Gemini API

3. **Create Service Account**
   - Go to IAM & Admin > Service Accounts
   - Create a new service account
   - Grant necessary permissions (Vertex AI User, etc.)

4. **Download Credentials**
   - Create and download a JSON key for the service account
   - Save as `cred.json` in the project root

### Environment Variables (Optional)

```bash
export GOOGLE_APPLICATION_CREDENTIALS="path/to/cred.json"
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_CLOUD_LOCATION="us-central1"
```

## 📖 Usage Examples

### Text Analysis

```python
from src.health_assistant import HealthAssistant

assistant = HealthAssistant(project_id="your-project-id")
result = assistant.analyze_text("What are the symptoms of dehydration?", "en")
print(result['response'])
```

### Image Analysis

```python
result = assistant.analyze_image("rash.jpg", "Red rash on the arm")
print(result['response'])
```

### Audio Analysis

```python
result = assistant.analyze_audio("symptoms.wav", "hi")  # Hindi audio
print(result['response'])
```

### Comprehensive Analysis

```python
result = assistant.comprehensive_analysis(
    text_input="I've been feeling dizzy",
    image_path="medication.jpg",
    audio_path="voice_symptoms.wav",
    language="en"
)
print(result['response'])
```

## 🌍 Multilingual Support

The assistant supports multiple languages:

| Language | Code | Example Query |
|----------|------|---------------|
| English | `en` | "What causes headaches?" |
| Hindi | `hi` | "मुझे सिरदर्द हो रहा है, क्या करूं?" |
| Spanish | `es` | "¿Qué debo hacer para un dolor de cabeza?" |
| French | `fr` | "Que dois-je faire pour un mal de tête?" |
| German | `de` | "Was soll ich bei Kopfschmerzen tun?" |
| Japanese | `ja` | "頭痛の原因は何ですか？" |
| Korean | `ko` | "두통의 원인은 무엇입니까?" |
| Chinese | `zh` | "头痛的原因是什么？" |

## 📊 Analytics and Data Export

The assistant provides comprehensive analytics:

- **Session tracking**: Monitor interactions and usage patterns
- **Data export**: Export session data to JSON and CSV formats
- **Visualizations**: Generate charts and graphs for analysis
- **Health tips**: Access curated health advice by category

```python
# Get session summary
summary = assistant.get_session_summary()
print(f"Total interactions: {summary['total_interactions']}")

# Export session data
output_path = assistant.export_session_data()
print(f"Data exported to: {output_path}")
```

## 🛡️ Safety and Disclaimers

⚠️ **IMPORTANT DISCLAIMER**

This health assistant is for **educational and informational purposes only**. It is **not a substitute** for professional medical advice, diagnosis, or treatment. 

- Always consult with qualified healthcare providers for medical concerns
- Never disregard professional medical advice based on AI-generated responses
- The assistant provides general information and should not be used for emergency situations
- Results are AI-generated and may not be accurate or complete

## 🔒 Privacy and Security

- **Local Processing**: All processing is done locally or through secure API calls
- **No Data Storage**: Personal health information is not stored permanently
- **Secure Credentials**: Keep your API credentials secure and never share them
- **Rate Limiting**: Built-in rate limiting to prevent API abuse

## 🚀 Advanced Features

### Custom Health Categories

The assistant organizes health information into categories:

- General Health
- Symptoms
- Medications
- First Aid
- Nutrition
- Exercise
- Mental Health
- Emergency

### File Format Support

**Images**: JPG, JPEG, PNG, BMP, TIFF, WebP
**Audio**: WAV, MP3, M4A, FLAC, OGG

### Rate Limiting

- Maximum 60 requests per minute
- Automatic request spacing
- Error handling for rate limit exceeded

### Technical Implementation

The project uses the latest `google-genai` library with Vertex AI integration:

```python
from google import genai

# Set environment variables
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'path/to/cred.json'
os.environ['GOOGLE_CLOUD_PROJECT'] = 'your-project-id'

# Create client for Vertex AI API
client = genai.Client(
    vertexai=True, 
    project='your-project-id', 
    location='us-central1'
)

# Generate content
response = client.models.generate_content(
    model='gemini-2.0-flash-001',
    contents='Your prompt here'
)
```

## 🐛 Troubleshooting

### Common Issues

1. **Authentication Error**
   ```
   ❌ Failed to initialize Health Assistant: Authentication failed
   ```
   - Check your credentials file path
   - Ensure service account has proper permissions
   - Verify API is enabled in Google Cloud Console

2. **File Not Found**
   ```
   ❌ File not found: image.jpg
   ```
   - Check file path is correct
   - Ensure file exists and is accessible
   - Verify file format is supported

3. **Unsupported Language**
   ```
   ❌ Unsupported language: xx
   ```
   - Use one of the supported language codes
   - Check language code spelling

4. **Rate Limit Exceeded**
   ```
   Rate limit reached. Waiting X seconds...
   ```
   - Wait for rate limit to reset
   - Reduce request frequency
   - Consider upgrading API quota

### Debug Mode

Enable debug logging by setting environment variable:
```bash
export DEBUG=1
```

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Development Setup

```bash
# Clone repository
git clone <repository-url>
cd multimodal-health-assistant

# Install development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If available

# Run tests
python -m pytest tests/

# Run linting
flake8 src/
black src/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Google Gemini 2.0 API for multimodal AI capabilities
- Streamlit for the web interface
- Open source community for various libraries and tools

## 📞 Support

For support and questions:

- Create an issue on GitHub
- Check the troubleshooting section
- Review the documentation

## 🔄 Changelog

### Version 1.0.0
- Initial release
- Text, image, and audio analysis
- Multilingual support
- Web interface
- Command-line interface
- Session management
- Analytics dashboard
- Updated to use google-genai with Vertex AI

---

**Remember**: This assistant is for educational purposes only. Always consult healthcare professionals for medical advice. 