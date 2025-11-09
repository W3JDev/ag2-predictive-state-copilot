"""AG2 Document Editing Agent with multi-LLM support."""

import logging
from typing import Dict, Any, Optional, List
import autogen
from ..config import settings
from .tools import DocumentTools

logger = logging.getLogger(__name__)


class DocumentEditAgent:
    """
    AG2-based conversational agent for collaborative document editing.
    Supports Google Gemini (primary) and DeepSeek (fallback) LLMs.
    """
    
    def __init__(self):
        """Initialize the document editing agent with LLM configuration."""
        self.tools = DocumentTools()
        self.config = self._setup_llm_config()
        self.agent = self._create_agent()
        
    def _setup_llm_config(self) -> List[Dict[str, Any]]:
        """
        Set up LLM configuration with primary (Gemini) and fallback (DeepSeek).
        
        Returns:
            List of LLM configurations
        """
        llm_configs = []
        
        # Primary: Google Gemini
        if settings.GEMINI_API_KEY:
            gemini_config = {
                "model": settings.MODEL_NAME,
                "api_key": settings.GEMINI_API_KEY,
                "api_type": "google",
                "temperature": settings.TEMPERATURE,
                "max_tokens": settings.MAX_TOKENS,
            }
            llm_configs.append(gemini_config)
            logger.info("Configured Gemini as primary LLM")
        
        # Fallback: DeepSeek
        if settings.DEEPSEEK_API_KEY:
            deepseek_config = {
                "model": settings.DEEPSEEK_MODEL,
                "api_key": settings.DEEPSEEK_API_KEY,
                "base_url": settings.DEEPSEEK_BASE_URL,
                "api_type": "openai",  # DeepSeek uses OpenAI-compatible API
                "temperature": settings.TEMPERATURE,
                "max_tokens": settings.MAX_TOKENS,
            }
            llm_configs.append(deepseek_config)
            logger.info("Configured DeepSeek as fallback LLM")
        
        if not llm_configs:
            logger.warning("No LLM configured. Agent will have limited functionality.")
            # Provide a default configuration for testing
            llm_configs.append({
                "model": "gpt-3.5-turbo",
                "api_key": "dummy",
                "temperature": settings.TEMPERATURE,
            })
        
        return llm_configs
    
    def _create_agent(self) -> autogen.AssistantAgent:
        """
        Create an AG2 AssistantAgent with document editing capabilities.
        
        Returns:
            Configured AssistantAgent instance
        """
        system_message = """You are an expert document editing assistant with the following capabilities:

1. **Grammar Correction**: Fix grammar, spelling, and punctuation errors
2. **Professional Tone**: Transform text to sound more professional and polished
3. **Summarization**: Create concise bullet-point summaries
4. **Section Management**: Add new sections on specific topics
5. **Tone Adjustment**: Change text tone (formal, casual, friendly, technical)

When editing documents:
- Be precise and maintain the original meaning
- Explain changes when significant
- Ask for clarification if needed
- Provide predictive suggestions for improvements
- Work collaboratively with the user

Available tools:
- fix_grammar(text): Fix grammar and typos
- make_professional(text): Make text more professional
- summarize_text(text, bullet_points): Create bullet-point summary
- add_section(text, topic, position): Add new section
- change_tone(text, target_tone): Adjust text tone
"""
        
        agent = autogen.AssistantAgent(
            name="DocumentEditor",
            system_message=system_message,
            llm_config={
                "config_list": self.config,
                "timeout": 120,
            },
        )
        
        return agent
    
    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a document editing request.
        
        Args:
            request: Request dictionary with action and parameters
            
        Returns:
            Response dictionary with results
        """
        try:
            action = request.get("action")
            params = request.get("params", {})
            
            logger.info(f"Processing request: action={action}")
            
            # Route to appropriate tool
            if action == "fix_grammar":
                result = self.tools.fix_grammar(params.get("text", ""))
            elif action == "make_professional":
                result = self.tools.make_professional(params.get("text", ""))
            elif action == "summarize":
                result = self.tools.summarize_text(
                    params.get("text", ""),
                    params.get("bullet_points", 5)
                )
            elif action == "add_section":
                result = self.tools.add_section(
                    params.get("text", ""),
                    params.get("topic", "New Section"),
                    params.get("position", "end")
                )
            elif action == "change_tone":
                result = self.tools.change_tone(
                    params.get("text", ""),
                    params.get("target_tone", "formal")
                )
            else:
                result = {
                    "error": f"Unknown action: {action}",
                    "available_actions": [
                        "fix_grammar",
                        "make_professional",
                        "summarize",
                        "add_section",
                        "change_tone"
                    ]
                }
            
            return {
                "success": "error" not in result,
                "result": result,
                "action": action
            }
            
        except Exception as e:
            logger.error(f"Error processing request: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "action": request.get("action")
            }
    
    def chat(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Have a conversational interaction with the agent.
        
        Args:
            message: User message
            context: Optional context dictionary
            
        Returns:
            Agent's response
        """
        try:
            # Create a user proxy for conversation
            user_proxy = autogen.UserProxyAgent(
                name="User",
                human_input_mode="NEVER",
                max_consecutive_auto_reply=0,
            )
            
            # Initiate chat
            user_proxy.initiate_chat(
                self.agent,
                message=message,
            )
            
            # Get the last message from the agent
            if hasattr(user_proxy, 'last_message'):
                response = user_proxy.last_message()
                return response.get("content", "No response generated")
            
            return "Agent processed the request"
            
        except Exception as e:
            logger.error(f"Error in chat: {e}", exc_info=True)
            return f"Error: {str(e)}"
    
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Get information about the agent's capabilities.
        
        Returns:
            Dictionary describing capabilities
        """
        return {
            "agent_name": "DocumentEditor",
            "llm_backend": settings.PRIMARY_LLM,
            "has_gemini": bool(settings.GEMINI_API_KEY),
            "has_deepseek": bool(settings.DEEPSEEK_API_KEY),
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
