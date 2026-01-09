import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from app.config import get_settings
from app.services.openai_service import OpenAIService, ChatResponse
from app.services.onechat import OneChatService

logger = logging.getLogger(__name__)
settings = get_settings()

@dataclass
class BackendStatus:
    name: str
    available: bool
    error_message: Optional[str] = None
    response_time_ms: Optional[float] = None

class AIBackendManager:
    """Manages switching between different AI backends"""
    
    def __init__(self):
        self.current_backend = settings.ai_backend
        self.fallback_enabled = settings.ai_backend_fallback
        
        # Initialize services
        self.openai_service = None
        self.onechat_service = None
        
        # Initialize available backends
        self._initialize_services()
        
        logger.info(f"AI Backend Manager initialized with primary backend: {self.current_backend}")
    
    def _initialize_services(self):
        """Initialize available AI services"""
        # Use the global instances that handle missing credentials gracefully
        from app.services.openai_service import openai_service
        from app.services.onechat import onechat_service
        
        self.openai_service = openai_service
        self.onechat_service = onechat_service
        
        if self.openai_service:
            logger.info("OpenAI service available")
        else:
            logger.warning("OpenAI service not available")
            
        if self.onechat_service:
            logger.info("MCP server service available")
        else:
            logger.warning("MCP server service not available")
    
    def _get_primary_service(self):
        """Get the primary AI service based on current backend setting"""
        if self.current_backend == "openai" and self.openai_service:
            return self.openai_service
        elif self.current_backend == "onechat" and self.onechat_service:
            return self.onechat_service
        return None
    
    def _get_fallback_service(self):
        """Get the fallback AI service"""
        if self.current_backend == "openai" and self.onechat_service:
            return self.onechat_service
        elif self.current_backend == "onechat" and self.openai_service:
            return self.openai_service
        return None
    
    def get_backend_status(self) -> Dict[str, BackendStatus]:
        """Get status of all available backends"""
        status = {}
        
        # Check OpenAI status
        if self.openai_service:
            try:
                # Quick test to see if service is responsive
                import time
                start_time = time.time()
                # Just check if we can access the service (don't make actual API call)
                status["openai"] = BackendStatus(
                    name="OpenAI",
                    available=True,
                    response_time_ms=None
                )
            except Exception as e:
                status["openai"] = BackendStatus(
                    name="OpenAI",
                    available=False,
                    error_message=str(e)
                )
        else:
            status["openai"] = BackendStatus(
                name="OpenAI",
                available=False,
                error_message="Service not initialized"
            )
        
        # Check MCP server status
        if self.onechat_service:
            try:
                # Quick test to see if service is responsive
                import time
                start_time = time.time()
                # Just check if we can access the service (don't make actual API call)
                status["onechat"] = BackendStatus(
                    name="MCP Server",
                    available=True,
                    response_time_ms=None
                )
            except Exception as e:
                status["onechat"] = BackendStatus(
                    name="MCP Server",
                    available=False,
                    error_message=str(e)
                )
        else:
            status["onechat"] = BackendStatus(
                name="MCP Server",
                available=False,
                error_message="Service not initialized"
            )
        
        return status
    
    def switch_backend(self, backend_name: str) -> bool:
        """Switch to a different AI backend"""
        if backend_name not in ["openai", "onechat"]:
            logger.error(f"Invalid backend name: {backend_name}")
            return False
        
        if backend_name == "openai" and not self.openai_service:
            logger.error("OpenAI service not available")
            return False
        
        if backend_name == "onechat" and not self.onechat_service:
            logger.error("MCP server service not available")
            return False
        
        self.current_backend = backend_name
        logger.info(f"Switched AI backend to: {backend_name}")
        return True
    
    def chat(self, input_text: str, conversation_id: Optional[str] = None, 
             agent_id: Optional[str] = None, connector_id: Optional[str] = None, 
             timeout: int = 60, use_cache: bool = True) -> ChatResponse:
        """Send a message using the current AI backend with fallback support"""
        
        # Try primary backend first
        primary_service = self._get_primary_service()
        if primary_service:
            try:
                logger.info(f"Using primary backend: {self.current_backend}")
                response = primary_service.chat(
                    input_text=input_text,
                    conversation_id=conversation_id,
                    agent_id=agent_id,
                    connector_id=connector_id,
                    timeout=timeout,
                    use_cache=use_cache
                )
                
                # Add backend info to response
                response.agent_id = f"{self.current_backend}_{agent_id}" if agent_id else self.current_backend
                return response
                
            except Exception as e:
                logger.error(f"Primary backend {self.current_backend} failed: {e}")
                
                # Try fallback if enabled
                if self.fallback_enabled:
                    fallback_service = self._get_fallback_service()
                    if fallback_service:
                        try:
                            fallback_backend = "onechat" if self.current_backend == "openai" else "openai"
                            logger.info(f"Trying fallback backend: {fallback_backend}")
                            
                            response = fallback_service.chat(
                                input_text=input_text,
                                conversation_id=conversation_id,
                                agent_id=agent_id,
                                connector_id=connector_id,
                                timeout=timeout,
                                use_cache=use_cache
                            )
                            
                            # Add fallback info to response
                            response.agent_id = f"{fallback_backend}_{agent_id}" if agent_id else f"{fallback_backend}_fallback"
                            return response
                            
                        except Exception as fallback_error:
                            logger.error(f"Fallback backend {fallback_backend} also failed: {fallback_error}")
        
        # If both backends fail, return error response
        logger.error("All AI backends failed")
        return ChatResponse(
            message="I'm experiencing technical difficulties with all AI services. Please try again later.",
            conversation_id=conversation_id or '',
            agent_id="error",
            citations=[]
        )
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics from all backends"""
        stats = {
            "current_backend": self.current_backend,
            "fallback_enabled": self.fallback_enabled,
            "backends": {}
        }
        
        if self.openai_service:
            try:
                stats["backends"]["openai"] = self.openai_service.get_cache_stats()
            except Exception as e:
                stats["backends"]["openai"] = {"error": str(e)}
        
        if self.onechat_service:
            try:
                stats["backends"]["onechat"] = self.onechat_service.get_cache_stats()
            except Exception as e:
                stats["backends"]["onechat"] = {"error": str(e)}
        
        return stats
    
    def clear_all_caches(self):
        """Clear caches from all backends"""
        if self.openai_service:
            try:
                self.openai_service.clear_cache()
            except Exception as e:
                logger.error(f"Failed to clear OpenAI cache: {e}")
        
        if self.onechat_service:
            try:
                self.onechat_service.clear_cache()
            except Exception as e:
                logger.error(f"Failed to clear MCP server cache: {e}")
    
    def clear_expired_caches(self):
        """Clear expired caches from all backends"""
        if self.openai_service:
            try:
                self.openai_service.clear_expired_cache()
            except Exception as e:
                logger.error(f"Failed to clear expired OpenAI cache: {e}")
        
        if self.onechat_service:
            try:
                self.onechat_service.clear_expired_cache()
            except Exception as e:
                logger.error(f"Failed to clear expired MCP server cache: {e}")

# Create a global instance
ai_backend_manager = AIBackendManager()
