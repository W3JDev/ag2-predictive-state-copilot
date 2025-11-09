# AG2 Predictive State Backend

Production-grade Python FastAPI backend for AG2 (AutoGen) agents featuring real-time collaborative document editing via CopilotKit.

## 🚀 Features

- **AG2 Conversational Agents**: Intelligent document editing with multi-agent orchestration
- **CopilotKit Integration**: Real-time streaming and WebSocket support for collaborative editing
- **Multi-LLM Support**: Google Gemini (primary) and DeepSeek (fallback) integration
- **Text Transformation Tools**:
  - Grammar correction and typo fixing
  - Professional tone transformation
  - Text summarization with bullet points
  - Section management
  - Tone adjustment (formal/casual/friendly/technical)
- **Predictive State Updates**: Real-time collaborative document editing
- **Production-Ready**: Robust error handling, logging, and monitoring
- **Containerized**: Docker multi-stage builds for optimization
- **CI/CD**: GitHub Actions for automatic deployment to Google Cloud Run

## 📋 Prerequisites

- Python 3.11+
- Docker (for containerization)
- Google Cloud account (for deployment)
- API Keys:
  - Google Gemini API key
  - DeepSeek API key (optional, for fallback)

## 🛠️ Local Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/W3JDev/ag2-predictive-state-copilot.git
cd ag2-predictive-state-copilot
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory:

```env
# API Keys
GEMINI_API_KEY=your_gemini_api_key_here
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# Application Configuration
FRONTEND_URL=https://ag2-predictive-state-editor.vercel.app
PORT=8080
ENVIRONMENT=development

# LLM Configuration
PRIMARY_LLM=gemini
MODEL_NAME=gemini-1.5-flash
TEMPERATURE=0.7
MAX_TOKENS=2000
```

### 5. Run the Application

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

# Or using Python
python -m app.main
```

The API will be available at `http://localhost:8080`

## 📚 API Endpoints

### Root Endpoint
```
GET /
```
Returns API information and available endpoints.

### Health Check
```
GET /health
```
Returns health status and LLM configuration.

### Capabilities
```
GET /api/capabilities
```
Returns agent capabilities and available tools.

### CopilotKit Integration
```
POST /api/copilotkit
```
Main CopilotKit integration endpoint for document editing operations.

**Request Body:**
```json
{
  "type": "action",
  "action": "fix_grammar",
  "params": {
    "text": "your text here"
  }
}
```

### Streaming Endpoint
```
POST /api/copilotkit/stream
```
Streaming endpoint for real-time updates via Server-Sent Events.

### Action Endpoints
```
POST /api/action/{action_name}
```

Available actions:
- `fix_grammar` - Fix grammar and typos
- `make_professional` - Transform to professional tone
- `summarize` - Create bullet-point summary
- `add_section` - Add new section to document
- `change_tone` - Adjust text tone

## 🐳 Docker Usage

### Build Image

```bash
docker build -t ag2-backend .
```

### Run Container

```bash
docker run -p 8080:8080 \
  -e GEMINI_API_KEY=your_key \
  -e DEEPSEEK_API_KEY=your_key \
  -e FRONTEND_URL=https://ag2-predictive-state-editor.vercel.app \
  ag2-backend
```

## ☁️ Google Cloud Run Deployment

### Prerequisites

1. **Install Google Cloud SDK**
   ```bash
   curl https://sdk.cloud.google.com | bash
   exec -l $SHELL
   gcloud init
   ```

2. **Enable Required APIs**
   ```bash
   gcloud services enable run.googleapis.com
   gcloud services enable artifactregistry.googleapis.com
   gcloud services enable cloudbuild.googleapis.com
   ```

3. **Create Artifact Registry**
   ```bash
   gcloud artifacts repositories create ag2-repo \
     --repository-format=docker \
     --location=us-central1
   ```

### Manual Deployment

```bash
# Build and push
gcloud builds submit --tag us-central1-docker.pkg.dev/PROJECT_ID/ag2-repo/ag2-backend

# Deploy
gcloud run deploy ag2-backend \
  --image us-central1-docker.pkg.dev/PROJECT_ID/ag2-repo/ag2-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="GEMINI_API_KEY=xxx,DEEPSEEK_API_KEY=xxx,FRONTEND_URL=https://ag2-predictive-state-editor.vercel.app"
```

### Automated CI/CD

The repository includes GitHub Actions workflow for automatic deployment:

1. **Configure GitHub Secrets**:
   - `GCP_PROJECT_ID`: Your Google Cloud project ID
   - `GCP_SA_KEY`: Service account key JSON
   - `GEMINI_API_KEY`: Gemini API key
   - `DEEPSEEK_API_KEY`: DeepSeek API key

2. **Push to Main Branch**:
   ```bash
   git push origin main
   ```

The workflow automatically builds, pushes, and deploys to Cloud Run.

## 🔒 Security

- API keys are managed via environment variables
- CORS configured for specific frontend origins
- No sensitive data in source code
- Multi-stage Docker builds minimize attack surface
- Production logging excludes sensitive information

## 🧪 Testing

### Manual Testing

```bash
# Health check
curl http://localhost:8080/health

# Get capabilities
curl http://localhost:8080/api/capabilities

# Fix grammar
curl -X POST http://localhost:8080/api/copilotkit \
  -H "Content-Type: application/json" \
  -d '{
    "type": "action",
    "action": "fix_grammar",
    "params": {"text": "this is a test"}
  }'
```

## 📊 Monitoring

The application includes:
- Structured logging with timestamps
- Error tracking and stack traces
- Health check endpoints
- Request/response logging

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Troubleshooting

### Common Issues

**Issue**: Module not found errors
- **Solution**: Ensure all dependencies are installed: `pip install -r requirements.txt`

**Issue**: LLM not responding
- **Solution**: Check API keys are correctly set in environment variables

**Issue**: CORS errors
- **Solution**: Verify `FRONTEND_URL` in environment variables matches your frontend domain

**Issue**: Docker build fails
- **Solution**: Ensure Docker has enough resources allocated (memory, CPU)

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Check existing issues for solutions
- Review the documentation

## 🗺️ Roadmap

- [ ] Add unit tests and integration tests
- [ ] Implement rate limiting
- [ ] Add authentication/authorization
- [ ] Enhance agent capabilities
- [ ] Add more LLM providers
- [ ] Implement caching for improved performance
- [ ] Add metrics and observability
