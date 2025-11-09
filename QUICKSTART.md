# Quick Start Guide

Get the AG2 Predictive State Backend up and running in minutes!

## Prerequisites

- Python 3.11 or higher
- Git
- pip (Python package manager)
- (Optional) Docker for containerized deployment

## 🚀 5-Minute Local Setup

### Step 1: Clone the Repository

```bash
git clone https://github.com/W3JDev/ag2-predictive-state-copilot.git
cd ag2-predictive-state-copilot
```

### Step 2: Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### Step 3: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your API keys
nano .env  # or use your favorite editor
```

Required environment variables:
```env
GEMINI_API_KEY=your_gemini_api_key_here
DEEPSEEK_API_KEY=your_deepseek_api_key_here  # Optional
ENVIRONMENT=development
```

### Step 4: Run the Server

```bash
# Start the development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

Server will be available at: `http://localhost:8080`

### Step 5: Test the API

Open a new terminal and test the endpoints:

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
    "params": {
      "text": "this is a test i want to fix"
    }
  }'
```

Success! 🎉 Your backend is running.

---

## 🐳 Docker Quick Start

### Build and Run with Docker

```bash
# Build the image
docker build -t ag2-backend .

# Run the container
docker run -p 8080:8080 \
  -e GEMINI_API_KEY=your_key \
  -e ENVIRONMENT=development \
  ag2-backend

# Test
curl http://localhost:8080/health
```

---

## ☁️ Cloud Run Quick Deploy

### Prerequisites
- Google Cloud account
- gcloud CLI installed and configured

### Deploy Steps

```bash
# Set project
gcloud config set project YOUR_PROJECT_ID

# Build and submit
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/ag2-backend

# Deploy
gcloud run deploy ag2-backend \
  --image gcr.io/YOUR_PROJECT_ID/ag2-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="GEMINI_API_KEY=xxx,ENVIRONMENT=production"

# Get URL
gcloud run services describe ag2-backend \
  --region us-central1 \
  --format='value(status.url)'
```

---

## 🧪 Quick API Tests

### Test All Features

```bash
# Base URL (change if deployed)
export API_URL="http://localhost:8080"

# 1. Fix Grammar
curl -X POST $API_URL/api/copilotkit \
  -H "Content-Type: application/json" \
  -d '{"type":"action","action":"fix_grammar","params":{"text":"i like this"}}'

# 2. Make Professional
curl -X POST $API_URL/api/copilotkit \
  -H "Content-Type: application/json" \
  -d '{"type":"action","action":"make_professional","params":{"text":"yeah this is cool"}}'

# 3. Summarize
curl -X POST $API_URL/api/copilotkit \
  -H "Content-Type: application/json" \
  -d '{"type":"action","action":"summarize","params":{"text":"First sentence. Second sentence. Third sentence.","bullet_points":2}}'

# 4. Change Tone
curl -X POST $API_URL/api/copilotkit \
  -H "Content-Type: application/json" \
  -d '{"type":"action","action":"change_tone","params":{"text":"Hi thanks bye","target_tone":"formal"}}'

# 5. Add Section
curl -X POST $API_URL/api/copilotkit \
  -H "Content-Type: application/json" \
  -d '{"type":"action","action":"add_section","params":{"text":"# Intro\n\nHello","topic":"Conclusion","position":"end"}}'
```

---

## 🌐 Connect to Frontend

### Local Development

1. Clone the frontend repository (if available)
2. Set environment variable:
   ```bash
   export NEXT_PUBLIC_COPILOTKIT_API_URL=http://localhost:8080/api/copilotkit
   ```
3. Start frontend:
   ```bash
   npm run dev
   ```

### Production

Update Vercel environment variable:
- **Name**: `NEXT_PUBLIC_COPILOTKIT_API_URL`
- **Value**: `https://your-backend-url.run.app/api/copilotkit`

---

## 📚 Interactive Documentation

Access interactive API docs at:
- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc

These provide:
- Complete API reference
- Interactive testing
- Schema definitions
- Examples and descriptions

---

## 🔧 Common Issues

### Issue: Module not found
```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

### Issue: Port already in use
```bash
# Solution: Use different port
uvicorn app.main:app --reload --port 8081
```

### Issue: GEMINI_API_KEY not set
```bash
# Solution: Set in .env file or export
export GEMINI_API_KEY=your_key_here
```

### Issue: CORS errors
```bash
# Solution: Check FRONTEND_URL in .env matches your frontend
FRONTEND_URL=http://localhost:3000
```

---

## 📖 Next Steps

1. **Read the Documentation**:
   - [README.md](README.md) - Complete project overview
   - [API.md](API.md) - API reference
   - [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment guide
   - [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture

2. **Customize the Agent**:
   - Edit `app/agents/tools.py` to add new tools
   - Modify `app/agents/document_agent.py` for different behaviors
   - Update `app/config.py` for new settings

3. **Add Tests**:
   - Create `tests/` directory
   - Write unit tests for tools
   - Add integration tests for endpoints

4. **Deploy to Production**:
   - Configure GitHub Secrets
   - Push to main branch
   - Monitor Cloud Run logs

5. **Monitor and Scale**:
   - Set up Cloud Monitoring
   - Configure alerts
   - Optimize resource allocation

---

## 💡 Pro Tips

1. **Development Mode**:
   - Use `--reload` flag for auto-restart on code changes
   - Set `ENVIRONMENT=development` for detailed errors
   - Check logs for debugging

2. **Performance**:
   - Use streaming endpoint for real-time updates
   - Cache capabilities response on frontend
   - Implement rate limiting for production

3. **Security**:
   - Never commit `.env` file
   - Use Secret Manager in production
   - Rotate API keys regularly
   - Enable authentication for production

4. **Debugging**:
   - Check `/health` endpoint first
   - Review application logs
   - Test with curl before frontend integration
   - Use interactive docs for testing

---

## 🤝 Get Help

- **Documentation**: Check [README.md](README.md) and other docs
- **Issues**: Open a GitHub issue
- **Logs**: Check application logs for errors
- **Community**: Reach out to maintainers

---

## ✅ Success Checklist

- [ ] Repository cloned
- [ ] Dependencies installed
- [ ] Environment variables configured
- [ ] Server running locally
- [ ] Health check passing
- [ ] API tests successful
- [ ] (Optional) Docker image built
- [ ] (Optional) Deployed to Cloud Run
- [ ] (Optional) Frontend connected

**You're ready to go! 🚀**
