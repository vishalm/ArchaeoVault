# 🏺 ArchaeoVault - The Digital Archaeologist

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)
[![Claude AI](https://img.shields.io/badge/Claude-AI-FF6B35?style=for-the-badge)](https://anthropic.com/)
[![Agentic AI](https://img.shields.io/badge/Agentic-AI-9C27B0?style=for-the-badge)](https://en.wikipedia.org/wiki/Artificial_intelligence_agent)
[![12-Factor App](https://img.shields.io/badge/12--Factor-App-00D4AA?style=for-the-badge)](https://12factor.net/)

> **An agentic AI-powered archaeological research platform featuring multiple specialized AI agents that collaborate to analyze artifacts, research civilizations, reconstruct timelines, and generate excavation reports.**

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Anthropic API key (for Claude AI integration)

### Installation & Running

1. **Clone the repository**
   ```bash
   git clone https://github.com/vishalm/ArchaeoVault.git
   cd ArchaeoVault
   ```

2. **Run the application (automated setup)**
   ```bash
   chmod +x run.sh
   ./run.sh
   ```

   This will automatically:
   - Create a virtual environment
   - Install all dependencies
   - Start the application

3. **Set up environment variables**
   ```bash
   cp env.template .env
   # Edit .env and add your ANTHROPIC_API_KEY
   ```

4. **Access the application**
   Navigate to `http://localhost:8501`

### Alternative Installation Methods

#### Manual Setup
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

#### Using pip with pyproject.toml
```bash
pip install -e .
python run.py
```

---

## 🤖 AI Agent System

ArchaeoVault features a sophisticated **multi-agent AI system** with specialized agents:

- **🏺 Artifact Analysis Agent** - Comprehensive artifact analysis and identification
- **⏳ Carbon Dating Agent** - Scientific dating calculations and analysis  
- **🌍 Civilization Research Agent** - Deep research into ancient civilizations
- **⛏️ Excavation Planning Agent** - Intelligent excavation site planning
- **📝 Report Generation Agent** - Professional archaeological report creation
- **💬 Research Assistant Agent** - General archaeological research assistance

---

## 🌟 Core Features

- **Artifact Analysis & Dating** - AI-powered visual analysis and C-14 dating
- **Civilization Database Explorer** - Interactive research and mapping
- **Excavation Planner** - Intelligent site planning and resource management
- **Stratigraphy Layer Analyzer** - 3D layer modeling and analysis
- **Timeline Reconstruction** - Dynamic timeline creation and editing
- **Report Generator** - Professional archaeological documentation
- **3D Artifact Visualization** - Advanced 3D examination tools
- **Research Assistant** - Conversational AI for archaeological research

---

## ⚙️ Configuration

Create a `.env` file with:

```env
# Required
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Optional
APP_NAME=ArchaeoVault
DEBUG_MODE=False
LOG_LEVEL=INFO
DATABASE_URL=sqlite:///archaeo.db
MAPBOX_TOKEN=your_mapbox_token_here
```

### Getting API Keys

1. **Anthropic API Key** (Required)
   - Visit [Anthropic Console](https://console.anthropic.com/)
   - Create an account and generate an API key

2. **Mapbox Token** (Optional)
   - Visit [Mapbox](https://www.mapbox.com/)
   - Create a free account for enhanced mapping features

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test categories
pytest -m "unit"                    # Unit tests only
pytest -m "integration"             # Integration tests only
pytest -m "ai_agents"               # AI agent tests only
```

---

## 🚀 Deployment

### Streamlit Cloud (Recommended)
1. Fork this repository
2. Connect to [Streamlit Cloud](https://share.streamlit.io)
3. Add your `ANTHROPIC_API_KEY` in secrets
4. Deploy

### Docker
```bash
docker build -t archaeovault .
docker run -p 8501:8501 --env-file .env archaeovault
```

---

## 📚 Documentation

- **[Architecture Guide](docs/ARCHITECTURE.md)** - Complete system design, AI agent architecture, and technical details
- **[API Documentation](docs/API.md)** - Internal API reference
- **[User Guide](docs/USER_GUIDE.md)** - Feature walkthrough
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

---

## 🐛 Troubleshooting

### Common Issues

**Q: The app won't start**
- Check that all dependencies are installed: `pip install -r requirements.txt`
- Verify your `.env` file has the required variables
- Ensure Python 3.8+ is being used

**Q: AI analysis not working**
- Verify your `ANTHROPIC_API_KEY` is correct
- Check your internet connection
- Ensure you have sufficient API credits

**Q: Images not uploading**
- Check file size (max 10MB by default)
- Verify file format (PNG, JPG supported)

### Getting Help
- Check the [Issues](https://github.com/vishalm/ArchaeoVault/issues) page
- Create a new issue with detailed information

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Anthropic** for providing Claude AI capabilities
- **Streamlit** for the amazing web framework
- **Archaeological community** for inspiration and feedback

---

<div align="center">

**Built with ❤️ for the archaeological community**

[![Star](https://img.shields.io/github/stars/vishalm/ArchaeoVault?style=social)](https://github.com/vishalm/ArchaeoVault)
[![Fork](https://img.shields.io/github/forks/vishalm/ArchaeoVault?style=social)](https://github.com/vishalm/ArchaeoVault/fork)
[![Watch](https://img.shields.io/github/watchers/vishalm/ArchaeoVault?style=social)](https://github.com/vishalm/ArchaeoVault)

</div>