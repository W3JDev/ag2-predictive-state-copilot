# API Documentation

## Base URL

- **Local Development**: `http://localhost:8080`
- **Production**: `https://your-service-url.run.app`

## Endpoints

### 1. Root Endpoint

**GET /**

Returns API information and available endpoints.

**Response:**
```json
{
  "service": "AG2 Predictive State Backend",
  "status": "running",
  "version": "1.0.0",
  "description": "FastAPI backend with AG2 agents and CopilotKit integration",
  "endpoints": {
    "root": "/",
    "health": "/health",
    "copilotkit": "/api/copilotkit",
    "capabilities": "/api/capabilities",
    "docs": "/docs",
    "redoc": "/redoc"
  },
  "features": [
    "AG2 conversational agents",
    "Real-time document editing",
    "CopilotKit protocol support",
    "Multi-LLM support (Gemini, DeepSeek)",
    "Text transformation tools",
    "WebSocket streaming",
    "Predictive state updates"
  ]
}
```

---

### 2. Health Check

**GET /health**

Returns the health status of the service and LLM configuration.

**Response:**
```json
{
  "status": "healthy",
  "llm": "gemini",
  "environment": "production",
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

**Status Codes:**
- `200 OK`: Service is healthy

---

### 3. Get Capabilities

**GET /api/capabilities**

Returns information about the agent's capabilities and available tools.

**Response:**
```json
{
  "success": true,
  "capabilities": {
    "agent_name": "DocumentEditor",
    "llm_backend": "gemini",
    "has_gemini": true,
    "has_deepseek": false,
    "capabilities": [
      "Grammar correction and typo fixing",
      "Professional tone transformation",
      "Text summarization with bullet points",
      "Section management and organization",
      "Tone adjustment (formal/casual/friendly/technical)",
      "Real-time collaborative editing",
      "Predictive state updates"
    ],
    "tools": [
      "fix_grammar",
      "make_professional",
      "summarize_text",
      "add_section",
      "change_tone"
    ]
  }
}
```

---

### 4. CopilotKit Integration

**POST /api/copilotkit**

Main endpoint for CopilotKit protocol integration. Handles document editing operations.

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

**Request Types:**
- `action`: Execute a document editing action
- `chat`: Conversational interaction with the agent
- `capabilities`: Get agent capabilities

---

#### 4.1 Fix Grammar Action

**Request:**
```json
{
  "type": "action",
  "action": "fix_grammar",
  "params": {
    "text": "this is a test i want to fix"
  }
}
```

**Response:**
```json
{
  "type": "action_response",
  "action": "fix_grammar",
  "result": {
    "success": true,
    "result": {
      "original": "this is a test i want to fix",
      "fixed": "This is a test I want to fix",
      "changes": ["Applied \\bi\\b", "Applied \\s+"],
      "tool": "fix_grammar"
    }
  },
  "success": true
}
```

---

#### 4.2 Make Professional Action

**Request:**
```json
{
  "type": "action",
  "action": "make_professional",
  "params": {
    "text": "yeah, this stuff is kinda cool guys"
  }
}
```

**Response:**
```json
{
  "type": "action_response",
  "action": "make_professional",
  "result": {
    "success": true,
    "result": {
      "original": "yeah, this stuff is kinda cool guys",
      "professional": "yes, these items are somewhat cool everyone",
      "changes": [
        "Replaced casual term with 'yes'",
        "Replaced casual term with 'items'",
        "Replaced casual term with 'somewhat'",
        "Replaced casual term with 'everyone'"
      ],
      "tool": "make_professional"
    }
  },
  "success": true
}
```

---

#### 4.3 Summarize Text Action

**Request:**
```json
{
  "type": "action",
  "action": "summarize",
  "params": {
    "text": "Long text with multiple sentences. Each sentence contains important information. We need to extract the key points. The summary should be concise and clear. It should help readers understand quickly.",
    "bullet_points": 3
  }
}
```

**Response:**
```json
{
  "type": "action_response",
  "action": "summarize",
  "result": {
    "success": true,
    "result": {
      "original": "Long text...",
      "summary": "• Long text with multiple sentences\n• Each sentence contains important information\n• We need to extract the key points",
      "bullet_points": 3,
      "word_count_original": 25,
      "word_count_summary": 18,
      "tool": "summarize_text"
    }
  },
  "success": true
}
```

---

#### 4.4 Add Section Action

**Request:**
```json
{
  "type": "action",
  "action": "add_section",
  "params": {
    "text": "# Introduction\n\nThis is the introduction section.",
    "topic": "Methodology",
    "position": "end"
  }
}
```

**Parameters:**
- `text`: Original document text
- `topic`: Topic for the new section
- `position`: Where to add (`start`, `middle`, `end`)

**Response:**
```json
{
  "type": "action_response",
  "action": "add_section",
  "result": {
    "success": true,
    "result": {
      "original": "# Introduction\n\nThis is the introduction section.",
      "updated": "# Introduction\n\nThis is the introduction section.\n\n## Methodology\n\n[Content about Methodology to be added here]\n\n",
      "section_added": "Methodology",
      "position": "end",
      "tool": "add_section"
    }
  },
  "success": true
}
```

---

#### 4.5 Change Tone Action

**Request:**
```json
{
  "type": "action",
  "action": "change_tone",
  "params": {
    "text": "Hi, thanks for your help. Bye!",
    "target_tone": "formal"
  }
}
```

**Supported Tones:**
- `formal`: Professional and formal language
- `casual`: Relaxed and friendly language
- `friendly`: Warm and approachable
- `technical`: Precise technical language

**Response:**
```json
{
  "type": "action_response",
  "action": "change_tone",
  "result": {
    "success": true,
    "result": {
      "original": "Hi, thanks for your help. Bye!",
      "transformed": "Hello, Thank you for your help. Goodbye!",
      "target_tone": "formal",
      "changes": [
        "Formalized: \\bhi\\b -> Hello",
        "Formalized: \\bthanks\\b -> Thank you",
        "Formalized: \\bbye\\b -> Goodbye"
      ],
      "tool": "change_tone"
    }
  },
  "success": true
}
```

---

### 5. Streaming Endpoint

**POST /api/copilotkit/stream**

Streaming endpoint for real-time updates via Server-Sent Events (SSE).

**Request:** Same as `/api/copilotkit`

**Response:** Server-Sent Events stream
```
data: {"type":"action_response",...}

data: {"type":"done"}
```

**Headers:**
- `Content-Type`: `text/event-stream`
- `Cache-Control`: `no-cache`
- `Connection`: `keep-alive`

---

### 6. Direct Action Endpoints

**POST /api/action/{action_name}**

Execute a specific action directly without the CopilotKit wrapper.

**Available Actions:**
- `/api/action/fix_grammar`
- `/api/action/make_professional`
- `/api/action/summarize`
- `/api/action/add_section`
- `/api/action/change_tone`

**Request:**
```json
{
  "text": "your text here",
  "bullet_points": 5
}
```

**Response:**
```json
{
  "success": true,
  "result": {
    "original": "...",
    "fixed": "...",
    "changes": [...],
    "tool": "fix_grammar"
  },
  "action": "fix_grammar"
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request format"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error",
  "detail": "Error message",
  "type": "ExceptionType"
}
```

---

## CORS

The API supports CORS for the following origins:
- `https://ag2-predictive-state-editor.vercel.app`
- `http://localhost:3000`
- `http://localhost:3001`

**Allowed Methods:** All (`*`)  
**Allowed Headers:** All (`*`)  
**Credentials:** Supported

---

## Rate Limiting

Currently no rate limiting is implemented. Consider implementing rate limiting for production use.

---

## Authentication

Currently the API is public (no authentication required). For production, consider implementing:
- API key authentication
- OAuth 2.0
- JWT tokens

---

## Interactive API Documentation

Access interactive API documentation at:
- **Swagger UI**: `/docs`
- **ReDoc**: `/redoc`

These endpoints provide interactive testing capabilities and detailed schema information.

---

## WebSocket Support

The backend supports WebSocket connections for real-time bidirectional communication. (Implementation pending in CopilotKit integration)

---

## Best Practices

1. **Error Handling**: Always check the `success` field in responses
2. **Retries**: Implement exponential backoff for retries
3. **Timeouts**: Set appropriate timeout values (recommended: 30s)
4. **Payload Size**: Keep text payloads under 10KB for optimal performance
5. **Caching**: Cache capabilities endpoint response

---

## Examples

### Python Example

```python
import requests

# Fix grammar
response = requests.post(
    "http://localhost:8080/api/copilotkit",
    json={
        "type": "action",
        "action": "fix_grammar",
        "params": {"text": "test text"}
    }
)
result = response.json()
print(result["result"]["result"]["fixed"])
```

### JavaScript Example

```javascript
// Make professional
const response = await fetch('http://localhost:8080/api/copilotkit', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    type: 'action',
    action: 'make_professional',
    params: {text: 'yeah this is cool'}
  })
});

const data = await response.json();
console.log(data.result.result.professional);
```

### cURL Example

```bash
curl -X POST http://localhost:8080/api/copilotkit \
  -H "Content-Type: application/json" \
  -d '{
    "type": "action",
    "action": "summarize",
    "params": {
      "text": "Long text to summarize",
      "bullet_points": 3
    }
  }'
```
