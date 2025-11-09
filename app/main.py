"""FastAPI application for AG2 Predictive State Backend."""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from .config import settings
from .agents.document_agent import DocumentEditAgent
from .copilotkit_integration import CopilotKitHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    logger.info("Starting AG2 Predictive State Backend...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Primary LLM: {settings.PRIMARY_LLM}")
    logger.info(f"Frontend URL: {settings.FRONTEND_URL}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AG2 Predictive State Backend...")


# Initialize FastAPI app
app = FastAPI(
    title="AG2 Predictive State Backend",
    description="Backend for AG2 document editing agents with CopilotKit integration",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware configuration
allowed_origins = [
    settings.FRONTEND_URL,
    "http://localhost:3000",
    "http://localhost:3001"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Initialize agent and handler
document_agent = DocumentEditAgent()
copilotkit_handler = CopilotKitHandler(document_agent)


@app.get("/")
async def root() -> Dict[str, Any]:
    """
    Root endpoint with API information.
    
    Returns:
        API information and available endpoints
    """
    return {
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


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint.
    
    Returns:
        Health status and LLM configuration
    """
    llm_status = "not_configured"
    if settings.GEMINI_API_KEY:
        llm_status = "gemini"
    elif settings.DEEPSEEK_API_KEY:
        llm_status = "deepseek"
    
    return {
        "status": "healthy",
        "llm": llm_status,
        "environment": settings.ENVIRONMENT,
        "primary_llm": settings.PRIMARY_LLM,
        "model": settings.MODEL_NAME,
        "features": {
            "gemini_configured": bool(settings.GEMINI_API_KEY),
            "deepseek_configured": bool(settings.DEEPSEEK_API_KEY),
            "cors_enabled": True,
            "websocket_support": True
        }
    }


@app.get("/api/capabilities")
async def get_capabilities() -> Dict[str, Any]:
    """
    Get agent capabilities.
    
    Returns:
        Agent capabilities and available tools
    """
    capabilities = document_agent.get_capabilities()
    return {
        "success": True,
        "capabilities": capabilities
    }


@app.post("/api/copilotkit")
async def copilotkit_endpoint(request: Request) -> JSONResponse:
    """
    Main CopilotKit integration endpoint.
    
    Args:
        request: HTTP request
        
    Returns:
        JSON response with results
    """
    try:
        # Parse request body
        body = await request.json()
        logger.info(f"CopilotKit request received: {body.get('type', 'unknown')}")
        
        # Handle request
        response = await copilotkit_handler.handle_request(body)
        
        return JSONResponse(content=response)
        
    except Exception as e:
        logger.error(f"Error in copilotkit endpoint: {e}", exc_info=True)
        error_detail = str(e) if settings.ENVIRONMENT == "development" else "Internal server error"
        raise HTTPException(status_code=500, detail=error_detail)


@app.post("/api/copilotkit/stream")
async def copilotkit_stream_endpoint(request: Request) -> StreamingResponse:
    """
    Streaming CopilotKit endpoint for real-time updates.
    
    Args:
        request: HTTP request
        
    Returns:
        Streaming response
    """
    try:
        body = await request.json()
        logger.info(f"CopilotKit stream request: {body.get('type', 'unknown')}")
        
        async def generate():
            async for chunk in copilotkit_handler.stream_response(body):
                yield f"data: {chunk}\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
        
    except Exception as e:
        logger.error(f"Error in stream endpoint: {e}", exc_info=True)
        error_detail = str(e) if settings.ENVIRONMENT == "development" else "Internal server error"
        raise HTTPException(status_code=500, detail=error_detail)


@app.post("/api/action/{action_name}")
async def execute_action(action_name: str, request: Request) -> Dict[str, Any]:
    """
    Execute a specific document editing action.
    
    Args:
        action_name: Name of the action to execute
        request: HTTP request with parameters
        
    Returns:
        Action result
    """
    try:
        params = await request.json()
        logger.info(f"Executing action: {action_name}")
        
        result = document_agent.process_request({
            "action": action_name,
            "params": params
        })
        
        return result
        
    except Exception as e:
        logger.error(f"Error executing action {action_name}: {e}", exc_info=True)
        error_detail = str(e) if settings.ENVIRONMENT == "development" else "Internal server error"
        raise HTTPException(status_code=500, detail=error_detail)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler.
    
    Args:
        request: HTTP request
        exc: Exception that occurred
        
    Returns:
        Error response
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.ENVIRONMENT == "development" else "An error occurred",
            "type": type(exc).__name__
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development",
        log_level="info"
    )
