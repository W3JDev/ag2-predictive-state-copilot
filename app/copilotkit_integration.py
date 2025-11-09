"""CopilotKit integration handler for real-time streaming and protocol support."""

import logging
from typing import Dict, Any, Optional, AsyncIterator
import json
from .agents.document_agent import DocumentEditAgent

logger = logging.getLogger(__name__)


class CopilotKitHandler:
    """
    Handler for CopilotKit protocol integration.
    Manages real-time streaming and WebSocket communication.
    """
    
    def __init__(self, agent: DocumentEditAgent):
        """
        Initialize the CopilotKit handler.
        
        Args:
            agent: DocumentEditAgent instance
        """
        self.agent = agent
        logger.info("CopilotKit handler initialized")
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle incoming CopilotKit requests.
        
        Args:
            request: Request payload from CopilotKit
            
        Returns:
            Response dictionary
        """
        try:
            request_type = request.get("type", "unknown")
            logger.info(f"Handling CopilotKit request: type={request_type}")
            
            if request_type == "action":
                return await self._handle_action(request)
            elif request_type == "chat":
                return await self._handle_chat(request)
            elif request_type == "capabilities":
                return await self._handle_capabilities()
            else:
                return {
                    "type": "error",
                    "error": f"Unknown request type: {request_type}",
                    "supported_types": ["action", "chat", "capabilities"]
                }
                
        except Exception as e:
            logger.error(f"Error handling CopilotKit request: {e}", exc_info=True)
            return {
                "type": "error",
                "error": str(e)
            }
    
    async def _handle_action(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle action requests (document editing operations).
        
        Args:
            request: Action request payload
            
        Returns:
            Action response
        """
        action = request.get("action")
        params = request.get("params", {})
        
        result = self.agent.process_request({
            "action": action,
            "params": params
        })
        
        return {
            "type": "action_response",
            "action": action,
            "result": result,
            "success": result.get("success", False)
        }
    
    async def _handle_chat(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle chat requests (conversational interaction).
        
        Args:
            request: Chat request payload
            
        Returns:
            Chat response
        """
        message = request.get("message", "")
        context = request.get("context", {})
        
        response = self.agent.chat(message, context)
        
        return {
            "type": "chat_response",
            "message": response,
            "context": context
        }
    
    async def _handle_capabilities(self) -> Dict[str, Any]:
        """
        Handle capabilities query.
        
        Returns:
            Capabilities information
        """
        capabilities = self.agent.get_capabilities()
        
        return {
            "type": "capabilities_response",
            "capabilities": capabilities
        }
    
    async def stream_response(self, request: Dict[str, Any]) -> AsyncIterator[str]:
        """
        Stream responses for real-time updates.
        
        Args:
            request: Request payload
            
        Yields:
            JSON-encoded response chunks
        """
        try:
            # Process request
            response = await self.handle_request(request)
            
            # For now, yield the complete response
            # In production, this could stream token-by-token from the LLM
            yield json.dumps(response)
            
            # Signal completion
            yield json.dumps({"type": "done"})
            
        except Exception as e:
            logger.error(f"Error streaming response: {e}", exc_info=True)
            yield json.dumps({
                "type": "error",
                "error": str(e)
            })
    
    def handle_websocket_message(self, message: str) -> Dict[str, Any]:
        """
        Handle WebSocket messages.
        
        Args:
            message: Raw WebSocket message
            
        Returns:
            Response dictionary
        """
        try:
            # Parse JSON message
            request = json.loads(message)
            logger.info(f"WebSocket message received: {request.get('type', 'unknown')}")
            
            # Handle based on message type
            msg_type = request.get("type")
            
            if msg_type == "ping":
                return {"type": "pong"}
            elif msg_type == "subscribe":
                return {
                    "type": "subscribed",
                    "channel": request.get("channel", "default")
                }
            else:
                # Process as regular request
                # Note: In async context, this should use handle_request
                return {
                    "type": "ack",
                    "message": "Request queued for processing"
                }
                
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in WebSocket message: {e}")
            return {
                "type": "error",
                "error": "Invalid JSON format"
            }
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}", exc_info=True)
            return {
                "type": "error",
                "error": str(e)
            }
    
    def create_predictive_state_update(
        self,
        document_id: str,
        changes: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a predictive state update for collaborative editing.
        
        Args:
            document_id: Document identifier
            changes: Changes to apply
            
        Returns:
            Predictive state update message
        """
        return {
            "type": "state_update",
            "document_id": document_id,
            "changes": changes,
            "timestamp": self._get_timestamp(),
            "source": "ag2_agent"
        }
    
    @staticmethod
    def _get_timestamp() -> str:
        """Get current timestamp."""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
