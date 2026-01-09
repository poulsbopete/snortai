"""
Streaming Chat Service for Elastic MCP Server
Provides real-time streaming responses to improve user experience
"""

import asyncio
import json
import logging
from typing import AsyncGenerator, Dict, Any, Optional
from services.onechat import OneChatService, ChatResponse

logger = logging.getLogger(__name__)

class StreamingChatService:
    """Service for streaming chat responses"""
    
    def __init__(self):
        self.onechat_service = OneChatService()
    
    async def stream_chat_response(self, input_text: str, conversation_id: Optional[str] = None, 
                                 agent_id: Optional[str] = None) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream chat response in real-time"""
        try:
            # Send initial request
            yield {
                "type": "status",
                "message": "Processing your request...",
                "conversation_id": conversation_id
            }
            
            # Get response from MCP server
            response = self.onechat_service.chat(
                input_text=input_text,
                conversation_id=conversation_id,
                agent_id=agent_id,
                timeout=60
            )
            
            # Stream the response
            yield {
                "type": "response",
                "message": response.message,
                "conversation_id": response.conversation_id,
                "citations": response.citations or []
            }
            
        except Exception as e:
            logger.error(f"Streaming chat failed: {e}")
            yield {
                "type": "error",
                "message": f"Error: {str(e)}",
                "conversation_id": conversation_id
            }
