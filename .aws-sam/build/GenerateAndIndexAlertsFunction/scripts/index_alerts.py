import os
import click
from rich.console import Console
from rich.progress import Progress
from datetime import datetime
from elasticsearch import Elasticsearch
from models.snort import SnortAlert
from config import get_settings
from snort.parser import parse_alert_line

console = Console()
settings = get_settings()

def get_elasticsearch_client():
    """Create and return an Elasticsearch client."""
    return Elasticsearch(
        hosts=[settings.elasticsearch_url],
        api_key=settings.elasticsearch_api_key,
        verify_certs=True  # Enable SSL verification
    )

def index_alerts(alert_file: str, batch_size: int = 100):
    """Read alerts from file and index them in Elasticsearch."""
    es = get_elasticsearch_client()
    index_name = settings.elasticsearch_index
    
    # Create index if it doesn't exist
    if not es.indices.exists(index=index_name):
        es.indices.create(
            index=index_name,
            mappings={
                "properties": {
                    "timestamp": {"type": "date"},
                    "alert_type": {"type": "keyword"},
                    "priority": {"type": "integer"},
                    "message": {"type": "text"},
                    "source_ip": {"type": "ip"},
                    "source_port": {"type": "integer"},
                    "destination_ip": {"type": "ip"},
                    "destination_port": {"type": "integer"},
                    "protocol": {"type": "keyword"},
                    "classification": {"type": "keyword"},
                    "signature_id": {"type": "keyword"},
                    "raw_alert": {"type": "text"}
                }
            }
        )
    
    alerts = []
    total_indexed = 0
    
    try:
        with open(alert_file, 'r') as f:
            with Progress() as progress:
                task = progress.add_task("[cyan]Indexing alerts...", total=None)
                
                for line in f:
                    try:
                        alert = parse_alert_line(line)
                        if alert:
                            # Convert alert to dict for indexing
                            alert_dict = alert.dict()
                            alerts.append(alert_dict)
                            
                            # Index in batches
                            if len(alerts) >= batch_size:
                                # Prepare bulk request
                                bulk_data = []
                                for alert in alerts:
                                    bulk_data.append({"index": {"_index": index_name}})
                                    bulk_data.append(alert)
                                
                                # Send bulk request
                                response = es.bulk(operations=bulk_data)
                                if not response.get('errors'):
                                    total_indexed += len(alerts)
                                    progress.update(task, completed=total_indexed)
                                else:
                                    console.print(f"[red]Error in bulk indexing: {response}[/red]")
                                alerts = []
                    
                    except Exception as e:
                        console.print(f"[red]Error parsing alert: {str(e)}[/red]")
                        continue
                
                # Index any remaining alerts
                if alerts:
                    # Prepare bulk request
                    bulk_data = []
                    for alert in alerts:
                        bulk_data.append({"index": {"_index": index_name}})
                        bulk_data.append(alert)
                    
                    # Send bulk request
                    response = es.bulk(operations=bulk_data)
                    if not response.get('errors'):
                        total_indexed += len(alerts)
                        progress.update(task, completed=total_indexed)
                    else:
                        console.print(f"[red]Error in bulk indexing: {response}[/red]")
        
        console.print(f"\n[green]Successfully indexed {total_indexed} alerts in Elasticsearch[/green]")
        
    except Exception as e:
        console.print(f"[red]Error indexing alerts: {str(e)}[/red]")

@click.command()
@click.option('--alert-file', default='~/snort_test/alert', help='Path to Snort alert file')
@click.option('--batch-size', default=100, help='Number of alerts to index in each batch')
def main(alert_file: str, batch_size: int):
    """Index Snort alerts in Elasticsearch."""
    # Expand home directory in path
    alert_file = os.path.expanduser(alert_file)
    
    if not os.path.exists(alert_file):
        console.print(f"[red]Error: Alert file not found at {alert_file}[/red]")
        return
    
    console.print(f"[blue]Indexing alerts from {alert_file}...[/blue]")
    index_alerts(alert_file, batch_size)

if __name__ == '__main__':
    main() 