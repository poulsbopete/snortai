from elasticsearch import Elasticsearch
from app.config import get_settings
from typing import List, Dict, Any
import logging

settings = get_settings()
logger = logging.getLogger(__name__)

class ElasticsearchClient:
    def __init__(self):
        self.client = Elasticsearch(
            settings.elasticsearch_url,
            api_key=settings.elasticsearch_api_key
        )
        self.index_name = "snort_alerts"
        self._ensure_index()

    def _ensure_index(self):
        """Ensure the index exists with proper mappings"""
        if not self.client.indices.exists(index=self.index_name):
            mapping = {
                "mappings": {
                    "properties": {
                        "timestamp": {"type": "date"},
                        "alert_type": {"type": "keyword"},
                        "priority": {"type": "integer"},
                        "protocol": {"type": "keyword"},
                        "source_ip": {"type": "ip"},
                        "source_port": {"type": "integer"},
                        "destination_ip": {"type": "ip"},
                        "destination_port": {"type": "integer"},
                        "message": {"type": "text"},
                        "classification": {"type": "keyword"},
                        "signature_id": {"type": "keyword"},
                        "raw_alert": {"type": "text"},
                        "analysis": {"type": "text"},
                        "recommendations": {"type": "text"},
                        "confidence_score": {"type": "float"}
                    }
                }
            }
            self.client.indices.create(index=self.index_name, body=mapping)

    async def store_alert(self, alert_data: Dict[str, Any]) -> bool:
        """Store a Snort alert in Elasticsearch"""
        try:
            response = self.client.index(
                index=self.index_name,
                document=alert_data
            )
            return response["result"] == "created"
        except Exception as e:
            logger.error(f"Error storing alert in Elasticsearch: {str(e)}")
            return False

    async def search_alerts(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search for alerts based on query"""
        try:
            response = self.client.search(
                index=self.index_name,
                body=query
            )
            return [hit["_source"] for hit in response["hits"]["hits"]]
        except Exception as e:
            logger.error(f"Error searching alerts in Elasticsearch: {str(e)}")
            return []

    async def get_alert_stats(self) -> Dict[str, Any]:
        """Get statistics about stored alerts"""
        try:
            response = self.client.search(
                index=self.index_name,
                body={
                    "size": 0,
                    "aggs": {
                        "alert_types": {"terms": {"field": "alert_type"}},
                        "priority_distribution": {"terms": {"field": "priority"}},
                        "protocols": {"terms": {"field": "protocol"}}
                    }
                }
            )
            return response["aggregations"]
        except Exception as e:
            logger.error(f"Error getting alert stats from Elasticsearch: {str(e)}")
            return {} 