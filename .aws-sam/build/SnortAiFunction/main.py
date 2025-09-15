# Force redeploy
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Body
from fastapi.requests import Request
import asyncio
import json
import logging
from typing import List, Dict, Any
import os
import requests

from mangum import Mangum
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from snort.processor import SnortAlertProcessor
from elastic.client import ElasticsearchClient
from models.snort import SnortAlert, AlertAnalysis
from elasticsearch import Elasticsearch
from services.onechat import onechat_service, ChatResponse
from services.ai_backend_manager import ai_backend_manager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="SnortAI")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

settings = get_settings()

handler = Mangum(app)

# Initialize components
snort_processor = SnortAlertProcessor()

# Initialize Elasticsearch client with error handling
try:
    elastic_client = ElasticsearchClient()
except Exception as e:
    logger.error(f"Failed to initialize Elasticsearch client: {e}")
    elastic_client = None

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle any incoming WebSocket messages if needed
    except WebSocketDisconnect:
        manager.disconnect(websocket)

async def process_new_alerts(alerts: List[SnortAlert]):
    """Process new alerts and broadcast them to connected clients"""
    for alert in alerts:
        # Store alert in Elasticsearch (without AI analysis for now)
        if elastic_client:
            try:
                await elastic_client.store_alert(alert.dict())
            except Exception as e:
                logger.error(f"Error storing alert: {e}")
        
        # Broadcast to WebSocket clients
        await manager.broadcast(json.dumps(alert.dict()))

@app.on_event("startup")
async def startup_event():
    """Start monitoring Snort alerts when the application starts"""
    if not os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
        # Only monitor the alert file when running locally
        asyncio.create_task(snort_processor.monitor_alert_file(process_new_alerts))

@app.get("/api/alerts")
async def get_alerts(
    start_time: str = None,
    end_time: str = None,
    alert_type: str = None,
    priority: int = None
) -> List[Dict[str, Any]]:
    """Get alerts from Elasticsearch with optional filters"""
    if not elastic_client:
        logger.error("Elasticsearch client not initialized")
        return []
    
    query = {
        "query": {
            "bool": {
                "must": []
            }
        },
        "sort": [{"timestamp": "desc"}]
    }

    if start_time:
        query["query"]["bool"]["must"].append({"range": {"timestamp": {"gte": start_time}}})
    if end_time:
        query["query"]["bool"]["must"].append({"range": {"timestamp": {"lte": end_time}}})
    if alert_type:
        query["query"]["bool"]["must"].append({"term": {"alert_type": alert_type}})
    if priority:
        query["query"]["bool"]["must"].append({"term": {"priority": priority}})

    try:
        return await elastic_client.search_alerts(query)
    except Exception as e:
        logger.error(f"Error searching alerts: {e}")
        return []

@app.get("/api/stats")
async def get_stats() -> Dict[str, Any]:
    """Get alert statistics from Elasticsearch"""
    if not elastic_client:
        logger.error("Elasticsearch client not initialized")
        return {}
    
    try:
        return await elastic_client.get_alert_stats()
    except Exception as e:
        logger.error(f"Error getting alert stats: {e}")
        return {}




@app.post("/api/ai-assistant")
async def ai_assistant(request: Request):
    """AI assistant endpoint with backend switching support"""
    data = await request.json()
    question = data.get("question")
    backend_override = data.get("backend")  # Optional backend override
    logger.info(f"Received question: {question}, backend override: {backend_override}")

    try:
        # Use backend manager for AI assistance
        if backend_override:
            # Temporarily switch backend for this request
            original_backend = ai_backend_manager.current_backend
            if ai_backend_manager.switch_backend(backend_override):
                try:
                    response = ai_backend_manager.chat(
                        input_text=question,
                        agent_id="snortai"
                    )
                finally:
                    # Restore original backend
                    ai_backend_manager.switch_backend(original_backend)
            else:
                # Fallback to current backend if override fails
                response = ai_backend_manager.chat(
                    input_text=question,
                    agent_id="snortai"
                )
        else:
            # Use current backend
            response = ai_backend_manager.chat(
                input_text=question,
                agent_id="snortai"
            )
        
        return {
            "answer": response.message,
            "citations": response.citations or [],
            "conversation_id": response.conversation_id,
            "backend_used": response.agent_id.split('_')[0] if response.agent_id else ai_backend_manager.current_backend
        }
        
    except Exception as e:
        logger.error(f"AI assistant error: {e}")
        return {
            "answer": "Sorry, I couldn't get an answer from the AI assistant.",
            "citations": [],
            "error": str(e),
            "backend_used": ai_backend_manager.current_backend
        }

@app.post("/api/semantic-search")
async def semantic_search(payload: dict = Body(...)):
    query = payload.get("query", "")
    if not query:
        return {"results": []}
    
    if not settings.elasticsearch_url or not settings.elasticsearch_api_key:
        logger.error("Elasticsearch configuration missing")
        return {"results": []}
    
    try:
        es = Elasticsearch(settings.elasticsearch_url, api_key=settings.elasticsearch_api_key)
        body = {
            "size": 5,
            "query": {
                "text_expansion": {
                    "message.elser_model": {
                        "model_id": ".elser_model_2_linux-x86_64",
                        "model_text": query
                    }
                }
            },
            "_source": ["alert_type", "message", "timestamp"]
        }
        response = es.search(index=settings.elasticsearch_index, body=body)
        results = [hit["_source"] for hit in response["hits"]["hits"]]
    except Exception as e:
        logger.error(f"ELSER search error: {e}")
        results = []
    return {"results": results}

# 1Chat API Endpoints
@app.get("/api/onechat/agents")
async def get_onechat_agents():
    """Get list of all 1Chat agents"""
    try:
        agents = onechat_service.get_agents()
        return {"agents": [{"id": agent.id, "name": agent.name, "description": agent.description} for agent in agents]}
    except Exception as e:
        logger.error(f"Failed to get 1Chat agents: {e}")
        return {"error": "Failed to get agents", "agents": []}

@app.get("/api/onechat/agents/{agent_id}")
async def get_onechat_agent(agent_id: str):
    """Get information about a specific 1Chat agent"""
    try:
        agent = onechat_service.get_agent(agent_id)
        if agent:
            return {"agent": {"id": agent.id, "name": agent.name, "description": agent.description, "configuration": agent.configuration}}
        else:
            return {"error": "Agent not found"}
    except Exception as e:
        logger.error(f"Failed to get 1Chat agent {agent_id}: {e}")
        return {"error": "Failed to get agent"}

@app.get("/api/onechat/cache/stats")
async def get_cache_stats():
    """Get cache statistics"""
    try:
        stats = onechat_service.get_cache_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        return {"error": str(e)}

@app.post("/api/onechat/cache/clear")
async def clear_cache():
    """Clear all cached responses"""
    try:
        onechat_service.clear_cache()
        return {"message": "Cache cleared successfully"}
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        return {"error": str(e)}

@app.post("/api/onechat/cache/clear-expired")
async def clear_expired_cache():
    """Clear only expired cache entries"""
    try:
        onechat_service.clear_expired_cache()
        return {"message": "Expired cache entries cleared successfully"}
    except Exception as e:
        logger.error(f"Error clearing expired cache: {e}")
        return {"error": str(e)}

# AI Backend Management Endpoints
@app.get("/api/ai/backend/status")
async def get_backend_status():
    """Get status of all AI backends"""
    try:
        status = ai_backend_manager.get_backend_status()
        return {
            "current_backend": ai_backend_manager.current_backend,
            "fallback_enabled": ai_backend_manager.fallback_enabled,
            "backends": {
                name: {
                    "name": backend.name,
                    "available": backend.available,
                    "error_message": backend.error_message,
                    "response_time_ms": backend.response_time_ms
                }
                for name, backend in status.items()
            }
        }
    except Exception as e:
        logger.error(f"Error getting backend status: {e}")
        return {"error": str(e)}

@app.post("/api/ai/backend/switch")
async def switch_backend(request: Request):
    """Switch AI backend"""
    try:
        body = await request.json()
        backend_name = body.get("backend")
        
        if not backend_name:
            return {"error": "Backend name is required"}
        
        success = ai_backend_manager.switch_backend(backend_name)
        if success:
            return {
                "message": f"Switched to {backend_name} backend",
                "current_backend": ai_backend_manager.current_backend
            }
        else:
            return {"error": f"Failed to switch to {backend_name} backend"}
            
    except Exception as e:
        logger.error(f"Error switching backend: {e}")
        return {"error": str(e)}

@app.get("/api/ai/backend/cache/stats")
async def get_all_cache_stats():
    """Get cache statistics from all backends"""
    try:
        stats = ai_backend_manager.get_cache_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        return {"error": str(e)}

@app.post("/api/ai/backend/cache/clear")
async def clear_all_caches():
    """Clear all cached responses from all backends"""
    try:
        ai_backend_manager.clear_all_caches()
        return {"message": "All caches cleared successfully"}
    except Exception as e:
        logger.error(f"Error clearing all caches: {e}")
        return {"error": str(e)}

@app.post("/api/ai/backend/cache/clear-expired")
async def clear_all_expired_caches():
    """Clear only expired cache entries from all backends"""
    try:
        ai_backend_manager.clear_expired_caches()
        return {"message": "All expired cache entries cleared successfully"}
    except Exception as e:
        logger.error(f"Error clearing expired caches: {e}")
        return {"error": str(e)}

@app.post("/api/onechat/agents")
async def create_onechat_agent(request: Request):
    """Create a new 1Chat agent"""
    try:
        data = await request.json()
        success = onechat_service.create_agent(
            agent_id=data.get("id"),
            name=data.get("name"),
            description=data.get("description"),
            instructions=data.get("instructions", ""),
            tools=data.get("tools", [])
        )
        if success:
            return {"message": "Agent created successfully"}
        else:
            return {"error": "Failed to create agent"}
    except Exception as e:
        logger.error(f"Failed to create 1Chat agent: {e}")
        return {"error": "Failed to create agent"}

@app.post("/api/onechat/converse")
async def converse_with_onechat(request: Request):
    """Send a message to 1Chat and get response"""
    try:
        data = await request.json()
        input_text = data.get("input", "")
        conversation_id = data.get("conversation_id")
        agent_id = data.get("agent_id")
        connector_id = data.get("connector_id")
        
        if not input_text:
            return {"error": "Input text is required"}
        
        response = onechat_service.chat(
            input_text=input_text,
            conversation_id=conversation_id,
            agent_id=agent_id,
            connector_id=connector_id
        )
        
        return {
            "message": response.message,
            "conversation_id": response.conversation_id,
            "agent_id": response.agent_id,
            "citations": response.citations or []
        }
        
    except Exception as e:
        logger.error(f"Failed to converse with 1Chat: {e}")
        return {"error": "Failed to get response from 1Chat"}

@app.get("/api/onechat/conversations")
async def get_onechat_conversations():
    """Get list of conversation threads"""
    try:
        conversations = onechat_service.get_conversations()
        return {"conversations": conversations}
    except Exception as e:
        logger.error(f"Failed to get 1Chat conversations: {e}")
        return {"error": "Failed to get conversations", "conversations": []}

@app.get("/api/onechat/conversations/{conversation_id}")
async def get_onechat_conversation(conversation_id: str):
    """Get full conversation using conversation_id"""
    try:
        conversation = onechat_service.get_conversation(conversation_id)
        if conversation:
            return {"conversation": conversation}
        else:
            return {"error": "Conversation not found"}
    except Exception as e:
        logger.error(f"Failed to get 1Chat conversation {conversation_id}: {e}")
        return {"error": "Failed to get conversation"}

@app.get("/api/onechat/tools")
async def get_onechat_tools():
    """Get list of available 1Chat tools"""
    try:
        tools = onechat_service.get_tools()
        return {"tools": tools}
    except Exception as e:
        logger.error(f"Failed to get 1Chat tools: {e}")
        return {"error": "Failed to get tools", "tools": []}

@app.get("/api/onechat/status")
async def get_onechat_status():
    """Get 1Chat service status and health information"""
    try:
        # Test basic connectivity
        agents = onechat_service.get_agents()
        tools = onechat_service.get_tools()
        
        # Test a simple chat to verify full functionality
        test_response = onechat_service.chat(
            input_text="Hello, are you working?",
            agent_id="default"
        )
        
        status_info = {
            "status": "healthy",
            "agents_count": len(agents),
            "tools_count": len(tools),
            "available_agents": [{"id": agent.id, "name": agent.name} for agent in agents],
            "test_chat_successful": bool(test_response.message),
            "last_test_conversation_id": test_response.conversation_id,
            "timestamp": "2025-01-27T10:00:00Z"
        }
        
        return status_info
        
    except Exception as e:
        logger.error(f"1Chat status check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "agents_count": 0,
            "tools_count": 0,
            "available_agents": [],
            "test_chat_successful": False,
            "timestamp": "2025-01-27T10:00:00Z"
        } 