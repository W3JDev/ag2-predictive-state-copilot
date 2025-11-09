# Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Vercel Frontend (Next.js)                    │
│                https://ag2-predictive-state-editor.vercel.app    │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTPS
                           │ CopilotKit Protocol
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Google Cloud Run (Backend)                     │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    FastAPI Application                      │ │
│  │  ┌──────────────────────────────────────────────────────┐  │ │
│  │  │ Endpoints:                                            │  │ │
│  │  │  • GET  /           (API info)                        │  │ │
│  │  │  • GET  /health     (Health check)                    │  │ │
│  │  │  • GET  /api/capabilities                             │  │ │
│  │  │  • POST /api/copilotkit                               │  │ │
│  │  │  • POST /api/copilotkit/stream (SSE)                  │  │ │
│  │  │  • POST /api/action/{action_name}                     │  │ │
│  │  └──────────────────────────────────────────────────────┘  │ │
│  │                                                              │ │
│  │  ┌──────────────────────────────────────────────────────┐  │ │
│  │  │        CopilotKit Integration Handler                 │  │ │
│  │  │  • Protocol handler                                   │  │ │
│  │  │  • Real-time streaming (SSE)                          │  │ │
│  │  │  • WebSocket message handling                         │  │ │
│  │  │  • Predictive state updates                           │  │ │
│  │  └──────────────────────────────────────────────────────┘  │ │
│  │                           │                                  │ │
│  │                           ▼                                  │ │
│  │  ┌──────────────────────────────────────────────────────┐  │ │
│  │  │         AG2 Document Editing Agent                    │  │ │
│  │  │  • Conversational interface                           │  │ │
│  │  │  • Multi-LLM support                                  │  │ │
│  │  │  • Tool orchestration                                 │  │ │
│  │  └──────────────────────────────────────────────────────┘  │ │
│  │                           │                                  │ │
│  │                           ▼                                  │ │
│  │  ┌──────────────────────────────────────────────────────┐  │ │
│  │  │          Text Transformation Tools                    │  │ │
│  │  │  • fix_grammar                                        │  │ │
│  │  │  • make_professional                                  │  │ │
│  │  │  • summarize_text                                     │  │ │
│  │  │  • add_section                                        │  │ │
│  │  │  • change_tone                                        │  │ │
│  │  └──────────────────────────────────────────────────────┘  │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                   │
└────────────┬──────────────────────────────┬─────────────────────┘
             │                              │
             ▼                              ▼
    ┌────────────────┐          ┌─────────────────────┐
    │  Google Gemini │          │  DeepSeek API       │
    │  (Primary LLM) │          │  (Fallback LLM)     │
    └────────────────┘          └─────────────────────┘
```

## Component Responsibilities

### 1. FastAPI Application (`app/main.py`)
**Purpose**: Main application entry point and HTTP request handling

**Responsibilities**:
- Route management and endpoint definitions
- CORS middleware configuration
- Global exception handling
- Request/response logging
- Environment-based error sanitization
- Health monitoring

**Key Features**:
- Supports multiple content types (JSON, SSE)
- Interactive API documentation (Swagger/ReDoc)
- Graceful startup/shutdown
- Production-ready error handling

---

### 2. Configuration (`app/config.py`)
**Purpose**: Centralized configuration management

**Responsibilities**:
- Environment variable loading
- Settings validation with Pydantic
- Default value management
- Type safety enforcement

**Configuration Categories**:
- API keys (Gemini, DeepSeek)
- Application settings (PORT, FRONTEND_URL, ENVIRONMENT)
- LLM configuration (model names, temperature, max tokens)

---

### 3. CopilotKit Integration Handler (`app/copilotkit_integration.py`)
**Purpose**: Bridge between CopilotKit protocol and AG2 agents

**Responsibilities**:
- CopilotKit protocol implementation
- Request type routing (action, chat, capabilities)
- Real-time streaming via Server-Sent Events
- WebSocket message handling
- Predictive state update generation

**Supported Request Types**:
- `action`: Execute document editing operations
- `chat`: Conversational AI interactions
- `capabilities`: Query agent capabilities

---

### 4. AG2 Document Agent (`app/agents/document_agent.py`)
**Purpose**: Intelligent document editing orchestrator

**Responsibilities**:
- AG2 (AutoGen) agent initialization
- Multi-LLM configuration and fallback
- Tool invocation and coordination
- Conversational interface
- Request processing and routing

**LLM Support**:
- **Primary**: Google Gemini (gemini-1.5-flash)
- **Fallback**: DeepSeek (deepseek-chat)
- Automatic failover mechanism

---

### 5. Text Transformation Tools (`app/agents/tools.py`)
**Purpose**: Text manipulation utilities

**Tools Provided**:

#### `fix_grammar(text) -> Dict`
- Capitalizes 'I'
- Fixes multiple spaces
- Capitalizes after punctuation
- Returns original, fixed text, and changes

#### `make_professional(text) -> Dict`
- Replaces casual phrases
- Improves formal tone
- Returns transformation details

#### `summarize_text(text, bullet_points) -> Dict`
- Creates bullet-point summaries
- Configurable number of points
- Returns word count metrics

#### `add_section(text, topic, position) -> Dict`
- Adds new sections
- Supports start/middle/end positioning
- Returns updated document

#### `change_tone(text, target_tone) -> Dict`
- Adjusts text tone
- Supports formal/casual/friendly/technical
- Returns transformation details

---

## Data Flow

### Action Request Flow

```
1. Frontend → POST /api/copilotkit
   {
     "type": "action",
     "action": "fix_grammar",
     "params": {"text": "input text"}
   }

2. FastAPI → CopilotKitHandler.handle_request()
   - Routes based on request type
   - Validates payload

3. CopilotKitHandler → DocumentEditAgent.process_request()
   - Routes to appropriate tool
   - Manages execution

4. DocumentEditAgent → DocumentTools.fix_grammar()
   - Executes transformation
   - Returns results

5. Response ← FastAPI
   {
     "type": "action_response",
     "success": true,
     "result": {...}
   }
```

### Streaming Request Flow

```
1. Frontend → POST /api/copilotkit/stream
   - Opens SSE connection
   - Sends request payload

2. Backend → Processes request asynchronously
   - Generates response chunks
   - Streams via Server-Sent Events

3. Response Stream:
   data: {"type": "action_response", ...}
   
   data: {"type": "done"}

4. Connection closes after completion
```

---

## Security Architecture

### 1. Authentication & Authorization
- **Current**: Public API (no authentication)
- **Recommended for Production**:
  - API key authentication
  - OAuth 2.0 integration
  - JWT token validation
  - Rate limiting per client

### 2. Secret Management
- Environment variables for all secrets
- No hardcoded credentials
- GitHub Secrets for CI/CD
- Google Cloud Secret Manager (recommended)

### 3. CORS Policy
**Allowed Origins**:
- `https://ag2-predictive-state-editor.vercel.app`
- `http://localhost:3000`
- `http://localhost:3001`

**Configuration**:
- Credentials: Allowed
- Methods: All
- Headers: All

### 4. Error Handling
**Development Mode**:
- Detailed error messages
- Full stack traces
- Debug logging

**Production Mode**:
- Generic error messages
- No stack trace exposure
- Secure logging

### 5. Input Validation
- Pydantic models for type safety
- Request payload validation
- Environment variable validation
- Configuration schema enforcement

---

## Deployment Architecture

### CI/CD Pipeline (GitHub Actions)

```
┌──────────────┐
│  Git Push    │
│  to main     │
└──────┬───────┘
       │
       ▼
┌──────────────────────┐
│  GitHub Actions      │
│  Workflow Triggered  │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  1. Checkout Code    │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  2. Authenticate     │
│     with GCP         │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  3. Build Docker     │
│     Image            │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  4. Push to          │
│     Artifact Registry│
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  5. Deploy to        │
│     Cloud Run        │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  Service Available   │
│  at Cloud Run URL    │
└──────────────────────┘
```

### Container Architecture

**Multi-Stage Build**:
1. **Builder Stage**:
   - Base: `python:3.11-slim`
   - Installs system dependencies
   - Installs Python packages
   - Optimizes for size

2. **Runtime Stage**:
   - Base: `python:3.11-slim`
   - Copies Python dependencies
   - Copies application code
   - Minimal attack surface

**Resource Configuration**:
- Memory: 2Gi
- CPU: 2
- Timeout: 300s
- Concurrency: 80
- Auto-scaling: 0-10 instances

---

## Scalability Considerations

### Horizontal Scaling
- Cloud Run auto-scales based on load
- Stateless design enables easy scaling
- Each instance handles 80 concurrent requests

### Performance Optimization
- Multi-stage Docker builds reduce image size
- Efficient dependency management
- Async request handling
- Streaming for long-running operations

### Cost Optimization
- Scale to zero when idle
- Pay-per-use pricing model
- Optimized resource allocation
- Efficient container images

---

## Monitoring & Observability

### Logging
- Structured JSON logging
- Request/response logging
- Error tracking with stack traces
- Environment-based log levels

### Health Checks
- `/health` endpoint
- LLM configuration status
- Feature availability checks
- Kubernetes-compatible

### Metrics (Recommended)
- Request latency
- Error rates
- LLM response times
- Resource utilization
- Concurrent connections

---

## Technology Stack

### Core Framework
- **FastAPI** 0.109.0: Modern async web framework
- **Uvicorn** 0.27.0: ASGI server with WebSocket support
- **Pydantic** 2.5.0+: Data validation and settings

### AI/ML
- **PyAutoGen** 0.2.18: Multi-agent orchestration
- **Google Generative AI** 0.3.2: Gemini integration
- **DeepSeek API**: Fallback LLM (OpenAI-compatible)

### Infrastructure
- **Docker**: Containerization
- **Google Cloud Run**: Serverless container platform
- **Google Artifact Registry**: Container image storage
- **GitHub Actions**: CI/CD automation

### Development
- **Python** 3.11+: Programming language
- **python-dotenv**: Environment management
- **httpx**: Async HTTP client
- **websockets**: WebSocket support

---

## Future Enhancements

### Short Term
- [ ] Unit and integration tests
- [ ] Rate limiting implementation
- [ ] API key authentication
- [ ] Caching layer for responses

### Medium Term
- [ ] WebSocket bidirectional communication
- [ ] Real-time collaboration features
- [ ] Enhanced LLM capabilities
- [ ] Metrics and monitoring dashboard

### Long Term
- [ ] Multi-region deployment
- [ ] Advanced agent capabilities
- [ ] Plugin system for custom tools
- [ ] GraphQL API support
- [ ] Real-time collaborative editing with OT/CRDT

---

## Design Decisions

### Why FastAPI?
- Modern, fast, and async-first
- Automatic API documentation
- Built-in validation with Pydantic
- WebSocket support
- Large ecosystem and community

### Why AG2 (AutoGen)?
- Multi-agent orchestration
- Easy tool integration
- Conversational AI capabilities
- Flexible LLM backends
- Active development

### Why Multi-Stage Docker?
- Smaller final image size
- Faster deployments
- Reduced attack surface
- Better caching
- Production-optimized

### Why Google Cloud Run?
- Serverless simplicity
- Auto-scaling
- Pay-per-use pricing
- Easy deployment
- Integrated with GCP ecosystem

---

## Contributing

When contributing to the architecture:

1. **Maintain Separation of Concerns**: Keep components focused and decoupled
2. **Follow Type Safety**: Use Pydantic for all data models
3. **Document Changes**: Update architecture docs for significant changes
4. **Security First**: Never compromise security for convenience
5. **Test Thoroughly**: Ensure changes work in all environments
