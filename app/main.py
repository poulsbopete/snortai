from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.requests import Request
import asyncio
import json
import logging
from typing import List, Dict, Any

from app.config import get_settings
from app.snort.processor import SnortAlertProcessor
from app.elastic.client import ElasticsearchClient
from app.ai.analyzer import AlertAnalyzer
from app.models.snort import SnortAlert, AlertAnalysis

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="SnortAI")
settings = get_settings()

# Initialize components
snort_processor = SnortAlertProcessor()
elastic_client = ElasticsearchClient()
alert_analyzer = AlertAnalyzer()

# Mount static files and templates
app.mount("/static", StaticFiles(directory="app/web/static"), name="static")
templates = Jinja2Templates(directory="app/web/templates")

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

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 