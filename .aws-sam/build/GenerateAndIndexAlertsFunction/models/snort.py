from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict

class SnortAlert(BaseModel):
    timestamp: datetime
    alert_type: str
    priority: int
    protocol: str
    source_ip: str
    source_port: int
    destination_ip: str
    destination_port: int
    message: str
    classification: Optional[str] = None
    signature_id: Optional[str] = None
    raw_alert: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2024-03-20T10:00:00",
                "alert_type": "Potential Exploit",
                "priority": 1,
                "protocol": "TCP",
                "source_ip": "192.168.1.100",
                "source_port": 12345,
                "destination_ip": "10.0.0.1",
                "destination_port": 80,
                "message": "Potential SQL Injection Attempt",
                "classification": "Exploit",
                "signature_id": "1:1234:1",
                "raw_alert": "[**] [1:1234:1] Potential SQL Injection Attempt [**]"
            }
        }

class AlertAnalysis(BaseModel):
    alert: SnortAlert
    analysis: str
    recommendations: List[str]
    confidence_score: float = Field(ge=0.0, le=1.0)
    related_alerts: Optional[List[str]] = None
    context: Optional[Dict] = None 