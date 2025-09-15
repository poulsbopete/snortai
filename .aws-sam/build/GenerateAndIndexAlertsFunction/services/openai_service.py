import openai
import time
import hashlib
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import logging
from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

@dataclass
class ChatResponse:
    message: str
    conversation_id: Optional[str] = None
    agent_id: Optional[str] = None
    citations: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.citations is None:
            self.citations = []

class OpenAIService:
    """Service for interacting with OpenAI API"""
    
    def __init__(self):
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key must be configured")
        
        self.client = openai.OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        self.max_tokens = settings.openai_max_tokens
        self.temperature = settings.openai_temperature
        
        # Response cache for chat responses
        self._response_cache = {}
        self._response_cache_ttl = 3600  # 1 hour for responses
        
        # Circuit breaker pattern
        self._failure_count = 0
        self._last_failure_time = 0
        self._circuit_breaker_threshold = 5
        self._circuit_breaker_timeout = 60  # 1 minute
        
        logger.info(f"OpenAI service initialized with model: {self.model}")
    
    def _is_circuit_breaker_open(self) -> bool:
        """Check if circuit breaker is open"""
        current_time = time.time()
        if (self._failure_count >= self._circuit_breaker_threshold and 
            current_time - self._last_failure_time < self._circuit_breaker_timeout):
            return True
        return False
    
    def _reset_circuit_breaker(self):
        """Reset circuit breaker on successful request"""
        self._failure_count = 0
        self._last_failure_time = 0
    
    def _record_failure(self):
        """Record a failure for circuit breaker"""
        self._failure_count += 1
        self._last_failure_time = time.time()
    
    def _generate_cache_key(self, input_text: str, agent_id: Optional[str] = None) -> str:
        """Generate a cache key for the request"""
        # Normalize the input text for better cache hits
        normalized_input = input_text.strip().lower()
        cache_string = f"{normalized_input}:{agent_id or 'default'}"
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def _get_cached_response(self, cache_key: str) -> Optional[ChatResponse]:
        """Get cached response if available and not expired"""
        if cache_key not in self._response_cache:
            return None
        
        cached_data = self._response_cache[cache_key]
        current_time = time.time()
        
        # Check if cache is expired
        if current_time - cached_data['timestamp'] > self._response_cache_ttl:
            del self._response_cache[cache_key]
            return None
        
        logger.info(f"Returning cached OpenAI response for key: {cache_key[:8]}...")
        return cached_data['response']
    
    def _cache_response(self, cache_key: str, response: ChatResponse):
        """Cache the response"""
        self._response_cache[cache_key] = {
            'response': response,
            'timestamp': time.time()
        }
        logger.info(f"Cached OpenAI response for key: {cache_key[:8]}...")
    
    def _cleanup_expired_cache(self):
        """Remove expired entries from cache"""
        current_time = time.time()
        expired_keys = []
        
        for key, data in self._response_cache.items():
            if current_time - data['timestamp'] > self._response_cache_ttl:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self._response_cache[key]
        
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired OpenAI cache entries")
    
    def _get_system_prompt(self, agent_id: Optional[str] = None) -> str:
        """Get system prompt based on agent or default"""
        if agent_id == "security_analyst":
            return """You are a cybersecurity analyst specializing in Snort IDS alerts and network security. 
            Analyze security alerts, identify threats, and provide actionable insights. 
            Focus on high-priority alerts, attack patterns, and recommended responses."""
        
        return """You are an AI assistant helping with Snort IDS alert analysis and network security. 
        Provide clear, actionable insights about security alerts and network events. 
        Be concise but thorough in your analysis."""
    
    def chat(self, input_text: str, conversation_id: Optional[str] = None, 
             agent_id: Optional[str] = None, connector_id: Optional[str] = None, 
             timeout: int = 30, use_cache: bool = True) -> ChatResponse:
        """Send a message to OpenAI and get response with caching"""
        
        # Check circuit breaker
        if self._is_circuit_breaker_open():
            raise Exception("OpenAI service temporarily unavailable (circuit breaker open)")
        
        # Clean up expired cache entries periodically
        if len(self._response_cache) > 100:  # Cleanup when cache gets large
            self._cleanup_expired_cache()
        
        # Check cache first (only for new conversations, not continuing ones)
        if use_cache and not conversation_id:
            cache_key = self._generate_cache_key(input_text, agent_id)
            cached_response = self._get_cached_response(cache_key)
            if cached_response:
                # Update conversation_id if provided
                if conversation_id:
                    cached_response.conversation_id = conversation_id
                return cached_response
        
        try:
            system_prompt = self._get_system_prompt(agent_id)
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": input_text}
            ]
            
            # Add conversation history if conversation_id is provided
            if conversation_id:
                # For now, we'll keep it simple with just the current message
                # In a full implementation, you'd retrieve conversation history
                pass
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                timeout=timeout
            )
            
            message = response.choices[0].message.content
            conversation_id = conversation_id or f"openai_{int(time.time())}"
            
            chat_response = ChatResponse(
                message=message,
                conversation_id=conversation_id,
                agent_id=agent_id,
                citations=[]
            )
            
            # Cache the response (only for new conversations)
            if use_cache and not conversation_id:
                cache_key = self._generate_cache_key(input_text, agent_id)
                self._cache_response(cache_key, chat_response)
            
            self._reset_circuit_breaker()  # Reset on success
            return chat_response
            
        except Exception as e:
            logger.error(f"Failed to chat with OpenAI: {e}")
            self._record_failure()
            
            # Return a fallback response instead of raising an exception
            return ChatResponse(
                message=f"I'm experiencing some technical difficulties with the AI service. Please try again in a moment. Error: {str(e)}",
                conversation_id=conversation_id or '',
                agent_id=agent_id,
                citations=[]
            )
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        current_time = time.time()
        active_entries = 0
        expired_entries = 0
        
        for data in self._response_cache.values():
            if current_time - data['timestamp'] > self._response_cache_ttl:
                expired_entries += 1
            else:
                active_entries += 1
        
        return {
            'total_entries': len(self._response_cache),
            'active_entries': active_entries,
            'expired_entries': expired_entries,
            'cache_ttl_seconds': self._response_cache_ttl,
            'cache_ttl_hours': self._response_cache_ttl / 3600,
            'model': self.model,
            'circuit_breaker_open': self._is_circuit_breaker_open(),
            'failure_count': self._failure_count
        }
    
    def clear_cache(self):
        """Clear all cached responses"""
        cache_size = len(self._response_cache)
        self._response_cache.clear()
        logger.info(f"Cleared {cache_size} cached OpenAI responses")
    
    def clear_expired_cache(self):
        """Clear only expired cache entries"""
        self._cleanup_expired_cache()
    
    def get_models(self) -> List[str]:
        """Get available OpenAI models"""
        try:
            models = self.client.models.list()
            return [model.id for model in models.data if 'gpt' in model.id.lower()]
        except Exception as e:
            logger.error(f"Failed to get OpenAI models: {e}")
            return [self.model]  # Return current model as fallback

# Create a global instance only if API key is available
try:
    openai_service = OpenAIService()
except ValueError as e:
    logger.warning(f"OpenAI service not available: {e}")
    openai_service = None
