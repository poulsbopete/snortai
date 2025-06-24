# Force redeploy
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.requests import Request
import asyncio
import json
import logging
from typing import List, Dict, Any
import os

from mangum import Mangum
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from snort.processor import SnortAlertProcessor
from elastic.client import ElasticsearchClient
from ai.analyzer import AlertAnalyzer
from models.snort import SnortAlert, AlertAnalysis
import openai
from elasticsearch import Elasticsearch

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
elastic_client = ElasticsearchClient()
alert_analyzer = AlertAnalyzer()

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
        # Analyze the alert
        analysis = await alert_analyzer.analyze_alert(alert)
        
        # Store in Elasticsearch
        await elastic_client.store_alert(analysis.dict())
        
        # Broadcast to WebSocket clients
        await manager.broadcast(json.dumps(analysis.dict()))

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

    return await elastic_client.search_alerts(query)

@app.get("/api/stats")
async def get_stats() -> Dict[str, Any]:
    """Get alert statistics from Elasticsearch"""
    return await elastic_client.get_alert_stats()

@app.post("/api/ai-assistant")
async def ai_assistant(request: Request):
    data = await request.json()
    question = data.get("question")
    logger.info(f"Received question: {question}")

    # Search Elasticsearch for relevant alerts
    es = Elasticsearch(settings.elasticsearch_url, api_key=settings.elasticsearch_api_key)
    es_query = {
        "query": {
            "multi_match": {
                "query": question,
                "fields": [
                    "alert_type", "classification", "message", "protocol", "raw_alert"
                ]
            }
        },
        "size": 3
    }
    try:
        es_results = es.search(index=settings.elasticsearch_index, body=es_query)
        hits = es_results["hits"]["hits"]
    except Exception as e:
        logger.error(f"Elasticsearch error: {e}")
        hits = []

    # Build context from hits
    context = ""
    for hit in hits:
        src = hit.get("_source", {})
        context += "\n".join(f"{k}: {v}" for k, v in src.items() if v) + "\n---\n"

    prompt = f"""
You are a senior solutions architect at a cloud company. Provide concise, step-by-step technical answers. Prioritize production-safe recommendations. If the answer isn't certain, say so and suggest next steps. Tone: professional, approachable, slightly nerdy.
Answer questions truthfully and factually using only the context presented.
If you don't know the answer, just say that you don't know, don't make up an answer.
Use markdown format for code examples.
Context:
{context}
"""

    # Call OpenAI
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": question}
            ]
        )
        answer = response.choices[0].message.content
    except Exception as e:
        logger.error(f"OpenAI error: {e}")
        answer = "Sorry, I couldn't get an answer from the AI."

    return {"answer": answer} 