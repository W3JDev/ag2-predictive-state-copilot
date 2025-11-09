# Testing Guide

## Local Testing

### 1. Setup Test Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your API keys
```

### 2. Run the Application

```bash
# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

# Or
python -m app.main
```

### 3. Test Endpoints

#### Health Check
```bash
curl http://localhost:8080/health
```

Expected response:
```json
{
  "status": "healthy",
  "llm": "gemini",
  "environment": "development",
  "primary_llm": "gemini",
  "model": "gemini-1.5-flash",
  "features": {
    "gemini_configured": true,
    "deepseek_configured": false,
    "cors_enabled": true,
    "websocket_support": true
  }
}
```

#### Root Endpoint
```bash
curl http://localhost:8080/
```

#### Get Capabilities
```bash
curl http://localhost:8080/api/capabilities
```

#### Fix Grammar
```bash
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

Expected response:
```json
{
  "type": "action_response",
  "action": "fix_grammar",
  "result": {
    "success": true,
    "result": {
      "original": "this is a test i want to fix",
      "fixed": "This is a test I want to fix",
      "changes": ["Applied grammar corrections"],
      "tool": "fix_grammar"
    }
  },
  "success": true
}
```

#### Make Professional
```bash
curl -X POST http://localhost:8080/api/copilotkit \
  -H "Content-Type: application/json" \
  -d '{
    "type": "action",
    "action": "make_professional",
    "params": {
      "text": "yeah, this stuff is kinda cool guys"
    }
  }'
```

#### Summarize Text
```bash
curl -X POST http://localhost:8080/api/copilotkit \
  -H "Content-Type: application/json" \
  -d '{
    "type": "action",
    "action": "summarize",
    "params": {
      "text": "This is a long text. It has multiple sentences. We want to summarize it. The summary should be concise. It should capture key points.",
      "bullet_points": 3
    }
  }'
```

#### Add Section
```bash
curl -X POST http://localhost:8080/api/copilotkit \
  -H "Content-Type: application/json" \
  -d '{
    "type": "action",
    "action": "add_section",
    "params": {
      "text": "# Introduction\n\nThis is the introduction.",
      "topic": "Methodology",
      "position": "end"
    }
  }'
```

#### Change Tone
```bash
curl -X POST http://localhost:8080/api/copilotkit \
  -H "Content-Type: application/json" \
  -d '{
    "type": "action",
    "action": "change_tone",
    "params": {
      "text": "Hi, thanks for your help. Bye!",
      "target_tone": "formal"
    }
  }'
```

## Docker Testing

### Build and Run with Docker

```bash
# Build the image
docker build -t ag2-backend:test .

# Run the container
docker run -p 8080:8080 \
  -e GEMINI_API_KEY=your_key \
  -e DEEPSEEK_API_KEY=your_key \
  -e FRONTEND_URL=http://localhost:3000 \
  -e ENVIRONMENT=development \
  ag2-backend:test

# Test the health endpoint
curl http://localhost:8080/health
```

### Test Multi-stage Build

```bash
# Build with BuildKit
DOCKER_BUILDKIT=1 docker build -t ag2-backend:test .

# Check image size
docker images ag2-backend:test
```

## Integration Testing with Frontend

### 1. Setup Frontend

If you have the Vercel frontend locally:

```bash
# In your frontend directory
export NEXT_PUBLIC_COPILOTKIT_API_URL=http://localhost:8080/api/copilotkit
npm run dev
```

### 2. Test CORS

```bash
# Test CORS preflight
curl -X OPTIONS http://localhost:8080/api/copilotkit \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -v
```

Expected headers in response:
```
Access-Control-Allow-Origin: http://localhost:3000
Access-Control-Allow-Methods: *
Access-Control-Allow-Headers: *
```

## Performance Testing

### Load Testing with Apache Bench

```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Test health endpoint (100 requests, 10 concurrent)
ab -n 100 -c 10 http://localhost:8080/health

# Test with POST data
ab -n 50 -c 5 -p test_payload.json -T application/json \
  http://localhost:8080/api/copilotkit
```

### Memory and CPU Monitoring

```bash
# Monitor resources while running
docker stats

# Or if running directly
top -p $(pgrep -f "uvicorn app.main:app")
```

## Automated Testing

### Unit Tests (Future Enhancement)

Create `tests/test_tools.py`:
```python
import pytest
from app.agents.tools import DocumentTools

def test_fix_grammar():
    tools = DocumentTools()
    result = tools.fix_grammar("i want to test this")
    assert result["fixed"] == "I want to test this"
    assert result["tool"] == "fix_grammar"

def test_make_professional():
    tools = DocumentTools()
    result = tools.make_professional("yeah, that's kinda cool")
    assert "somewhat" in result["professional"]
    assert result["tool"] == "make_professional"
```

Run with:
```bash
pytest tests/ -v
```

## Cloud Run Testing

### Test Deployed Service

```bash
# Get service URL
export SERVICE_URL=$(gcloud run services describe ag2-backend \
  --region=us-central1 \
  --format='value(status.url)')

# Test health
curl $SERVICE_URL/health

# Test capabilities
curl $SERVICE_URL/api/capabilities

# Test action
curl -X POST $SERVICE_URL/api/copilotkit \
  -H "Content-Type: application/json" \
  -d '{
    "type": "action",
    "action": "fix_grammar",
    "params": {"text": "test text"}
  }'
```

### Monitor Logs

```bash
# View recent logs
gcloud run services logs read ag2-backend --region=us-central1 --limit=50

# Tail logs in real-time
gcloud run services logs tail ag2-backend --region=us-central1
```

## Troubleshooting Tests

### Issue: Connection refused
**Solution**: Ensure the server is running and listening on the correct port.

### Issue: Import errors
**Solution**: Ensure all dependencies are installed: `pip install -r requirements.txt`

### Issue: CORS errors in browser
**Solution**: Check that frontend URL is in the CORS allowed origins.

### Issue: LLM not responding
**Solution**: Verify API keys are set correctly in environment variables.

## Testing Checklist

- [ ] Health endpoint returns 200 OK
- [ ] Root endpoint returns API information
- [ ] Capabilities endpoint returns agent info
- [ ] Fix grammar action works correctly
- [ ] Make professional action works correctly
- [ ] Summarize action works correctly
- [ ] Add section action works correctly
- [ ] Change tone action works correctly
- [ ] CORS headers are correct
- [ ] Docker image builds successfully
- [ ] Container runs and serves requests
- [ ] Logging shows informative messages
- [ ] Error handling works (test with invalid requests)
- [ ] Cloud Run deployment succeeds
- [ ] Frontend can connect to backend

## Performance Benchmarks

Expected performance on Cloud Run (2 CPU, 2Gi RAM):
- Health check: < 100ms
- Text transformation: 200-500ms
- With LLM calls: 1-3 seconds
- Concurrent requests: 80+ requests/second

Monitor and optimize based on actual usage patterns.
