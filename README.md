# 🏺 ArchaeoVault - The Digital Archaeologist

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)
[![Claude AI](https://img.shields.io/badge/Claude-AI-FF6B35?style=for-the-badge)](https://anthropic.com/)
[![12-Factor App](https://img.shields.io/badge/12--Factor-App-00D4AA?style=for-the-badge)](https://12factor.net/)

> **An AI-powered archaeological research and analysis platform that helps archaeologists, historians, and enthusiasts analyze artifacts, research civilizations, reconstruct timelines, and generate excavation reports.**

---

## 🌟 Features

### 🏺 **Artifact Analysis & Dating**
- Upload artifact images for AI-powered visual analysis
- Material identification and dating recommendations
- Historical significance assessment
- Preservation guidelines

### ⏳ **Carbon Dating Calculator**
- Scientific C-14 dating calculations
- Interactive decay curve visualization
- Calibrated date range estimation
- Comparison with other dating methods

### 🌍 **Civilization Database Explorer**
- Searchable database of ancient civilizations
- Interactive maps showing geographic extent
- Cultural achievements and notable artifacts
- AI-powered civilization research chat

### ⛏️ **Excavation Planner**
- Grid-based site planning tools
- AI-generated excavation strategies
- Resource and timeline estimation
- Professional excavation reports

### 📊 **Stratigraphy Layer Analyzer**
- Visual layer-by-layer soil profile builder
- AI interpretation of stratigraphic sequences
- 3D visualization of archaeological layers
- Timeline reconstruction from layers

### 📅 **Timeline Reconstruction Tool**
- Interactive timeline builder
- AI suggestions for related events
- Confidence level assessment
- Export as professional infographics

### 📝 **Archaeological Report Generator**
- Professional report templates
- AI writing assistant
- Citation management
- Export as PDF/DOCX

### 🔮 **3D Artifact Visualization**
- Interactive 3D artifact viewer
- Measurement and annotation tools
- Virtual restoration preview
- Side-by-side artifact comparison

### 💬 **Research Assistant**
- AI-powered archaeological research chat
- Literature review assistance
- Hypothesis generation
- Statistical analysis recommendations

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Anthropic API key (for Claude AI integration)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/vishalm/ArchaeoVault.git
   cd ArchaeoVault
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your ANTHROPIC_API_KEY
   ```

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

6. **Open your browser**
   Navigate to `http://localhost:8501`

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Required
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Optional
APP_NAME=ArchaeoVault
DEBUG_MODE=False
LOG_LEVEL=INFO
DATABASE_URL=sqlite:///archaeo.db
MAPBOX_TOKEN=your_mapbox_token_here

# Feature Flags
ENABLE_AI_ANALYSIS=True
ENABLE_3D_VIEWER=True

# Limits
MAX_UPLOAD_SIZE_MB=10
MAX_REPORT_LENGTH=5000
```

### Getting API Keys

1. **Anthropic API Key** (Required)
   - Visit [Anthropic Console](https://console.anthropic.com/)
   - Create an account and generate an API key
   - Add to your `.env` file

2. **Mapbox Token** (Optional)
   - Visit [Mapbox](https://www.mapbox.com/)
   - Create a free account and get your token
   - Enables enhanced mapping features

---

## 🏗️ Architecture

### 12-Factor App Compliance

ArchaeoVault follows the [12-Factor App methodology](https://12factor.net/) for building modern, scalable applications:

1. **Codebase** - Single codebase with clear structure
2. **Dependencies** - Explicit dependency declaration
3. **Config** - Environment-based configuration
4. **Backing Services** - Treat external services as attached resources
5. **Build, Release, Run** - Strict separation of build and run stages
6. **Processes** - Stateless, share-nothing processes
7. **Port Binding** - Self-contained web service
8. **Concurrency** - Scale via process model
9. **Disposability** - Fast startup and graceful shutdown
10. **Dev/Prod Parity** - Keep environments similar
11. **Logs** - Treat logs as event streams
12. **Admin Processes** - Run admin tasks as one-off processes

### Project Structure

```
ArchaeoVault/
├── app/
│   ├── pages/              # Streamlit page modules
│   │   ├── home.py
│   │   ├── artifact_analyzer.py
│   │   ├── carbon_dating.py
│   │   ├── civilizations.py
│   │   ├── excavation_planner.py
│   │   ├── stratigraphy.py
│   │   ├── timeline.py
│   │   ├── reports.py
│   │   ├── viewer_3d.py
│   │   └── research_chat.py
│   ├── components/         # Reusable UI components
│   │   ├── artifact_card.py
│   │   ├── civilization_badge.py
│   │   └── timeline_widget.py
│   ├── services/           # Business logic
│   │   ├── ai_analyzer.py
│   │   ├── external.py
│   │   └── storage.py
│   ├── models/             # Data models
│   │   ├── artifact.py
│   │   ├── civilization.py
│   │   └── excavation.py
│   ├── utils/              # Helper functions
│   │   ├── helpers.py
│   │   └── validators.py
│   └── app.py              # Main application entry point
├── tests/                  # Test suite
│   ├── test_ai_analyzer.py
│   ├── test_models.py
│   └── test_utils.py
├── docs/                   # Documentation
│   ├── ARCHITECTURE.md
│   ├── API.md
│   └── USER_GUIDE.md
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── .gitignore
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## 🎨 UI/UX Design

### Color Palette
- **Primary**: Saddle Brown (#8B4513)
- **Secondary**: Chocolate (#D2691E)
- **Background**: Antique White (#F5E6D3)
- **Text**: Dark Brown (#3E2723)

### Design Principles
- Earth tones inspired by archaeological sites
- Ancient-inspired typography and textures
- Responsive design for all devices
- Smooth animations and transitions
- Intuitive navigation with clear visual hierarchy

---

## 🔧 Development

### Local Development

1. **Install development dependencies**
   ```bash
   pip install -r requirements-dev.txt
   ```

2. **Run tests**
   ```bash
   pytest tests/
   ```

3. **Run with hot reload**
   ```bash
   streamlit run app.py --server.runOnSave true
   ```

4. **Code formatting**
   ```bash
   black app/
   isort app/
   ```

### Docker Development

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

2. **Access the application**
   Navigate to `http://localhost:8501`

---

## 🚀 Deployment

### Streamlit Cloud (Recommended)

1. **Fork this repository**
2. **Connect to Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub account
   - Select this repository
3. **Add secrets**
   - Add `ANTHROPIC_API_KEY` in the secrets section
   - Add other environment variables as needed
4. **Deploy**
   - Click "Deploy" and wait for deployment

### Docker Deployment

1. **Build the image**
   ```bash
   docker build -t archaeovault .
   ```

2. **Run the container**
   ```bash
   docker run -p 8501:8501 --env-file .env archaeovault
   ```

### Heroku Deployment

1. **Install Heroku CLI**
2. **Create Heroku app**
   ```bash
   heroku create your-archaeovault-app
   ```

3. **Set environment variables**
   ```bash
   heroku config:set ANTHROPIC_API_KEY=your_key_here
   ```

4. **Deploy**
   ```bash
   git push heroku main
   ```

### AWS/GCP/Azure

For production deployments on cloud platforms, refer to the [Deployment Guide](docs/DEPLOYMENT.md).

---

## 📊 Performance

### Caching Strategy
- **Data caching**: `@st.cache_data` for expensive computations
- **Session caching**: Store user data in `st.session_state`
- **External caching**: Redis for production deployments

### Optimization
- Lazy loading of heavy libraries
- Image optimization and compression
- Efficient data structures and algorithms
- Horizontal scaling via process model

---

## 🧪 Testing

### Test Coverage
- Unit tests for all business logic
- Integration tests for AI services
- UI tests for critical user flows
- Performance tests for heavy operations

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_ai_analyzer.py
```

---

## 📚 Documentation

- **[Architecture Guide](docs/ARCHITECTURE.md)** - System design and patterns
- **[API Documentation](docs/API.md)** - Internal API reference
- **[User Guide](docs/USER_GUIDE.md)** - Feature walkthrough
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute
- **[Deployment Guide](docs/DEPLOYMENT.md)** - Production deployment

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

### Code Style
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Write comprehensive docstrings
- Include unit tests for new features

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
- Ensure sufficient disk space

**Q: Performance issues**
- Clear browser cache
- Restart the application
- Check system resources

### Getting Help

- Check the [Issues](https://github.com/vishalm/ArchaeoVault/issues) page
- Create a new issue with detailed information
- Join our community discussions

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Anthropic** for providing Claude AI capabilities
- **Streamlit** for the amazing web framework
- **Archaeological community** for inspiration and feedback
- **Open source contributors** who made this possible

---

## 📞 Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/vishalm/ArchaeoVault/issues)
- **Discussions**: [GitHub Discussions](https://github.com/vishalm/ArchaeoVault/discussions)
- **Email**: support@archaeovault.com

---

## 🔮 Roadmap

### Version 2.0
- [ ] Mobile app (React Native)
- [ ] Advanced 3D modeling
- [ ] Collaborative excavation planning
- [ ] Machine learning artifact classification
- [ ] Integration with museum databases

### Version 2.1
- [ ] Multi-language support
- [ ] Advanced statistical analysis
- [ ] VR/AR visualization
- [ ] Blockchain artifact provenance
- [ ] Advanced AI research assistant

---

<div align="center">

**Built with ❤️ for the archaeological community**

[![Star](https://img.shields.io/github/stars/vishalm/ArchaeoVault?style=social)](https://github.com/vishalm/ArchaeoVault)
[![Fork](https://img.shields.io/github/forks/vishalm/ArchaeoVault?style=social)](https://github.com/vishalm/ArchaeoVault/fork)
[![Watch](https://img.shields.io/github/watchers/vishalm/ArchaeoVault?style=social)](https://github.com/vishalm/ArchaeoVault)

</div>
