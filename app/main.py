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
from ai.analyzer import AlertAnalyzer
from models.snort import SnortAlert, AlertAnalysis
from elasticsearch import Elasticsearch
import openai

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

# Helper: fields to extract from ES hits
index_source_fields = {
    settings.elasticsearch_index: [
        "alert_type",
        "alert_type.keyword",
        "classification",
        "classification.keyword",
        "destination_ip",
        "destination_ip.keyword",
        "destination_port",
        "message",
        "message.keyword",
        "priority",
        "protocol",
        "protocol.keyword",
        "raw_alert",
        "raw_alert.keyword",
        "signature_id",
        "signature_id.keyword",
        "source_ip",
        "source_ip.keyword",
        "source_port",
        "timestamp"
    ]
}

def get_elasticsearch_results(query):
    es_query = {
        "query": {
            "multi_match": {
                "query": query,
                "fields": [
                    "alert_type",
                    "classification",
                    "message",
                    "protocol",
                    "raw_alert"
                ]
            }
        },
        "size": 3
    }
    es = Elasticsearch(settings.elasticsearch_url, api_key=settings.elasticsearch_api_key)
    result = es.search(index=settings.elasticsearch_index, body=es_query)
    return result["hits"]["hits"]

def create_openai_prompt(results):
    context = ""
    context_map = {}
    for idx, hit in enumerate(results, 1):
        context += f"[{idx}]\n"
        context_fields = index_source_fields.get(hit["_index"], index_source_fields[settings.elasticsearch_index])
        snippet = ""
        for source_field in context_fields:
            hit_context = hit["_source"].get(source_field)
            if hit_context:
                snippet += f"{source_field}: {hit_context}\n"
        context += snippet + "---\n"
        context_map[str(idx)] = snippet.strip()
    prompt = f"""
Instructions:
- You are a senior solutions architect at a cloud company. Provide concise, step-by-step technical answers. Prioritize production-safe recommendations. For YAML, JSON, or CLI, output only the relevant snippet. If the answer isn't certain, say so and suggest next steps. Tone: professional, approachable, slightly nerdy.
- Answer questions truthfully and factually using only the context presented.
- If you don't know the answer, just say that you don't know, don't make up an answer.
- You must always cite the document where the answer was extracted using inline academic citation style [n], using the position number from the context below.
- Use markdown format for code examples.
- You are correct, factual, precise, and reliable.

Context:
{context}
"""
    return prompt, context_map

def generate_openai_completion(user_prompt, question):
    openai.api_key = settings.openai_api_key
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": user_prompt},
            {"role": "user", "content": question},
        ]
    )
    return response.choices[0].message.content

@app.post("/api/ai-assistant")
async def ai_assistant(request: Request):
    data = await request.json()
    question = data.get("question")
    logger.info(f"Received question: {question}")

    try:
        elasticsearch_results = get_elasticsearch_results(question)
        context_prompt, context_map = create_openai_prompt(elasticsearch_results)
        openai_completion = generate_openai_completion(context_prompt, question)
        answer = openai_completion
    except Exception as e:
        logger.error(f"AI assistant error: {e}")
        answer = "Sorry, I couldn't get an answer from the AI assistant."
        context_map = {}

    return {"answer": answer, "citations": context_map}

@app.post("/api/semantic-search")
async def semantic_search(payload: dict = Body(...)):
    query = payload.get("query", "")
    if not query:
        return {"results": []}
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
    try:
        response = es.search(index=settings.elasticsearch_index, body=body)
        results = [hit["_source"] for hit in response["hits"]["hits"]]
    except Exception as e:
        logger.error(f"ELSER search error: {e}")
        results = []
    return {"results": results} 