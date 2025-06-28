# 🏥 MediMind AI - Multimodal Health Assistant

A sophisticated health assistant powered by Google's Gemini 2.0 API that can analyze text, images, and audio to provide health-related insights and recommendations.

## 🌟 Features

- **📝 Text Analysis**: Answer health questions and provide medical information
- **🖼️ Image Analysis**: Analyze health-related images (rashes, medications, medical devices)
- **🎵 Audio Analysis**: Process spoken health concerns and symptoms
- **🌍 Multilingual Support**: Support for English, Hindi, and Spanish
- **📊 Session Management**: Track interactions and export data
- **💡 Health Tips Database**: Curated health advice by category
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
   cd medi-mind-ai
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
medi-mind-ai/
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
result = assistant.process_query(
    text_input="What are the symptoms of dehydration?", 
    language="en"
)
print(result['response'])
```

### Image Analysis

```python
result = assistant.process_query(
    image_path="rash.jpg", 
    description="Red rash on the arm"
)
print(result['response'])
```

### Audio Analysis

```python
result = assistant.process_query(
    audio_path="symptoms.wav", 
    language="hi"  # Hindi audio
)
print(result['response'])
```

## 🌍 Multilingual Support

The assistant supports three languages:

| Language | Code | Example Query |
|----------|------|---------------|
| English | `en` | "What causes headaches?" |
| Hindi | `hi` | "मुझे सिरदर्द हो रहा है, क्या करूं?" |
| Spanish | `es` | "¿Qué debo hacer para un dolor de cabeza?" |

## 📊 Session Management

The assistant provides session tracking and data export:

- **Session tracking**: Monitor interactions and usage patterns
- **Data export**: Export session data to JSON format
- **Health tips**: Access curated health advice by category

```python
# Get session summary
summary = assistant.get_session_summary()
print(f"Total queries: {summary['total_queries']}")

# Save session data
result = assistant.save_session_to_file("session_data.json")
print(f"Session saved to: {result['filepath']}")
```

## 🛡️ Safety and Disclaimers

⚠️ **IMPORTANT DISCLAIMER**

This health assistant is for **educational and informational purposes only**. It is **NOT** a substitute for professional medical advice, diagnosis, or treatment.

**Key Points:**
- ❌ **NOT** for medical diagnosis or treatment
- ❌ **NOT** for emergency situations
- ❌ **NOT** a replacement for healthcare professionals
- ✅ **FOR** learning and information
- ✅ **FOR** general health awareness
- ✅ **FOR** educational purposes

**Always consult qualified healthcare professionals for medical concerns.**

## 🔒 Privacy & Security

- No data is stored permanently
- All processing happens through Google's secure APIs
- Credentials are handled locally
- Session data can be exported/deleted

## 🛠️ Development

### Running Tests
```bash
python -m pytest tests/
```

### Code Style
```bash
black src/ main.py streamlit_app.py
flake8 src/ main.py streamlit_app.py
```

### Adding New Features
1. Update the appropriate module in `src/`
2. Add tests in `tests/`
3. Update documentation
4. Test thoroughly

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Google Gemini 2.0 API
- Streamlit for the web interface
- The open-source community

## 📞 Support

For issues and questions:
1. Check the documentation
2. Review existing issues
3. Create a new issue with details

---

**Remember**: This is an educational tool. Always consult healthcare professionals for medical advice. 