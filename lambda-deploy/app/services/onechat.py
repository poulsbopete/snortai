"""
Elastic 1Chat API Service
Provides integration with Elastic's 1Chat API for conversational AI
"""

import requests
import json
import logging
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from app.config import get_settings
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)
settings = get_settings()

@dataclass
class ChatMessage:
    """Represents a chat message in a conversation"""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: Optional[str] = None

@dataclass
class ChatResponse:
    """Response from 1Chat API"""
    message: str
    conversation_id: str
    agent_id: Optional[str] = None
    citations: Optional[List[Dict]] = None

@dataclass
class Agent:
    """Represents a 1Chat agent"""
    id: str
    name: str
    description: str
    configuration: Dict[str, Any]

class OneChatService:
    """Service for interacting with Elastic 1Chat API"""
    
    def __init__(self):
        # Convert Elasticsearch URL to Kibana URL for 1Chat API
        if '.es.' in settings.elasticsearch_url:
            self.base_url = settings.elasticsearch_url.replace('.es.', '.kb.')
        else:
            self.base_url = settings.elasticsearch_url
        self.api_key = settings.elasticsearch_api_key
        self.headers = {
            'Authorization': f'ApiKey {self.api_key}',
            'Content-Type': 'application/json',
            'kbn-xsrf': 'true'
        }
        
        # Create session with connection pooling and retry logic
        self.session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST"]
        )
        
        # Mount adapter with retry strategy
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=10, pool_maxsize=20)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Cache for agents and tools
        self._agents_cache = None
        self._tools_cache = None
        self._cache_timestamp = 0
        self._cache_ttl = 300  # 5 minutes
        
        # Response cache for chat responses
        self._response_cache = {}
        self._response_cache_ttl = 3600  # 1 hour for responses
        
        # Circuit breaker pattern
        self._failure_count = 0
        self._last_failure_time = 0
        self._circuit_breaker_threshold = 5
        self._circuit_breaker_timeout = 60  # 1 minute
    
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
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, timeout: int = 30) -> Dict[str, Any]:
        """Make a request to the 1Chat API with timeout and circuit breaker"""
        # Check circuit breaker
        if self._is_circuit_breaker_open():
            raise Exception("Service temporarily unavailable (circuit breaker open)")
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, headers=self.headers, timeout=timeout)
            elif method.upper() == 'POST':
                response = self.session.post(url, headers=self.headers, json=data, timeout=timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            self._reset_circuit_breaker()  # Reset on success
            return response.json()
            
        except requests.exceptions.Timeout:
            logger.error(f"1Chat API request timed out after {timeout} seconds")
            self._record_failure()
            raise Exception(f"Request timed out after {timeout} seconds")
        except requests.exceptions.RequestException as e:
            logger.error(f"1Chat API request failed: {e}")
            self._record_failure()
            raise Exception(f"Failed to communicate with 1Chat API: {str(e)}")
    
    def get_agents(self) -> List[Agent]:
        """Get list of all available agents with caching"""
        current_time = time.time()
        
        # Return cached data if still valid
        if (self._agents_cache is not None and 
            current_time - self._cache_timestamp < self._cache_ttl):
            return self._agents_cache
        
        try:
            # Use the working agent builder endpoint
            response = self._make_request('GET', '/api/agent_builder/agents', timeout=10)
            agents = []
            
            for agent_data in response.get('results', []):
                agents.append(Agent(
                    id=agent_data.get('id'),
                    name=agent_data.get('name'),
                    description=agent_data.get('description', ''),
                    configuration=agent_data.get('configuration', {})
                ))
            
            # Cache the results
            self._agents_cache = agents
            self._cache_timestamp = current_time
            
            return agents
            
        except Exception as e:
            logger.error(f"Failed to get agents: {e}")
            # Return cached data if available, even if expired
            return self._agents_cache or []
    
    def create_agent(self, agent_id: str, name: str, description: str, 
                    instructions: str, tools: Optional[List[Dict]] = None) -> bool:
        """Create a new agent"""
        try:
            agent_data = {
                "id": agent_id,
                "name": name,
                "description": description,
                "configuration": {
                    "instructions": instructions,
                    "tools": tools or []
                }
            }
            
            # Use the working agent builder agents endpoint
            self._make_request('POST', '/api/agent_builder/agents', agent_data)
            logger.info(f"Successfully created agent: {agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create agent {agent_id}: {e}")
            return False
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get information about a specific agent"""
        try:
            # Use the working agent builder agents endpoint
            response = self._make_request('GET', f'/api/agent_builder/agents/{agent_id}')
            
            return Agent(
                id=response.get('id'),
                name=response.get('name'),
                description=response.get('description', ''),
                configuration=response.get('configuration', {})
            )
            
        except Exception as e:
            logger.error(f"Failed to get agent {agent_id}: {e}")
            return None
    
    def _generate_cache_key(self, input_text: str, agent_id: Optional[str] = None) -> str:
        """Generate a cache key for the request"""
        import hashlib
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
        
        logger.info(f"Returning cached response for key: {cache_key[:8]}...")
        return cached_data['response']
    
    def _cache_response(self, cache_key: str, response: ChatResponse):
        """Cache the response"""
        self._response_cache[cache_key] = {
            'response': response,
            'timestamp': time.time()
        }
        logger.info(f"Cached response for key: {cache_key[:8]}...")
    
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
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")

    def chat(self, input_text: str, conversation_id: Optional[str] = None, 
             agent_id: Optional[str] = None, connector_id: Optional[str] = None, 
             timeout: int = 60, use_cache: bool = True) -> ChatResponse:
        """Send a message to 1Chat and get response with caching"""
        
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
            chat_data = {
                "input": input_text
            }
            
            if conversation_id:
                chat_data["conversation_id"] = conversation_id
            if agent_id:
                chat_data["agent_id"] = agent_id
            if connector_id:
                chat_data["connector_id"] = connector_id
            
            # Use the working agent builder converse endpoint
            response = self._make_request('POST', '/api/agent_builder/converse', chat_data, timeout=timeout)
            
            # Extract the response message
            message = ""
            citations = []
            
            # Check if there's a direct response message
            if 'response' in response and 'message' in response['response']:
                message = response['response']['message']
            else:
                # Fallback to parsing steps
                steps = response.get('steps', [])
                if steps:
                    # Get the last step which should contain the response
                    last_step = steps[-1]
                    if 'message' in last_step:
                        message = last_step['message']
                    elif 'content' in last_step:
                        message = last_step['content']
                    
                    # Extract citations if available
                    if 'citations' in last_step:
                        citations = last_step['citations']
            
            chat_response = ChatResponse(
                message=message,
                conversation_id=response.get('conversation_id', conversation_id or ''),
                agent_id=agent_id,
                citations=citations
            )
            
            # Cache the response (only for new conversations)
            if use_cache and not conversation_id:
                cache_key = self._generate_cache_key(input_text, agent_id)
                self._cache_response(cache_key, chat_response)
            
            return chat_response
            
        except Exception as e:
            logger.error(f"Failed to chat with 1Chat: {e}")
            # Return a fallback response instead of raising an exception
            return ChatResponse(
                message=f"I'm experiencing some technical difficulties with the AI service. Please try again in a moment. Error: {str(e)}",
                conversation_id=conversation_id or '',
                agent_id=agent_id,
                citations=[]
            )
    
    def get_conversations(self) -> List[Dict[str, Any]]:
        """Get list of conversation threads"""
        try:
            response = self._make_request('GET', '/api/chat/conversations')
            return response.get('results', [])
            
        except Exception as e:
            logger.error(f"Failed to get conversations: {e}")
            return []
    
    def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get full conversation using conversation_id"""
        try:
            response = self._make_request('GET', f'/api/chat/conversations/{conversation_id}')
            return response
            
        except Exception as e:
            logger.error(f"Failed to get conversation {conversation_id}: {e}")
            return None
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools"""
        try:
            # Use the working agent builder tools endpoint
            response = self._make_request('GET', '/api/agent_builder/tools')
            return response.get('results', [])
            
        except Exception as e:
            logger.error(f"Failed to get tools: {e}")
            return []
    
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
            'cache_ttl_hours': self._response_cache_ttl / 3600
        }
    
    def clear_cache(self):
        """Clear all cached responses"""
        cache_size = len(self._response_cache)
        self._response_cache.clear()
        logger.info(f"Cleared {cache_size} cached responses")
    
    def clear_expired_cache(self):
        """Clear only expired cache entries"""
        self._cleanup_expired_cache()

# Create a global instance only if credentials are available
try:
    onechat_service = OneChatService()
except ValueError as e:
    logger.warning(f"OneChat service not available: {e}")
    onechat_service = None
