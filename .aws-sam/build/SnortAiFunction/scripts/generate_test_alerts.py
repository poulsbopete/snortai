import os
import click
from rich.console import Console
from datetime import datetime, timedelta
import random

console = Console()

def generate_test_alerts(num_alerts: int = 10, output_file: str = "~/snort_test/alert"):
    """Generate test Snort alerts with various failure scenarios."""
    # Expand home directory in path
    output_file = os.path.expanduser(output_file)
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Define alert types and their characteristics
    alert_types = [
        # Normal alerts
        {
            "type": "ICMP",
            "message": "ICMP PING NMAP",
            "classification": "Misc activity",
            "priority": 3,
            "protocol": "ICMP",
            "source_port": 0,
            "dest_port": 0
        },
        {
            "type": "TCP",
            "message": "TCP SYN Scan",
            "classification": "Attempted Information Leak",
            "priority": 2,
            "protocol": "TCP",
            "source_port": 12345,
            "dest_port": 80
        },
        # Failure scenarios
        {
            "type": "FAILED",
            "message": "Failed to process packet: Invalid packet length",
            "classification": "Snort Error",
            "priority": 1,
            "protocol": "TCP",
            "source_port": 54321,
            "dest_port": 443
        },
        {
            "type": "FAILED",
            "message": "Packet dropped: Buffer overflow in preprocessor",
            "classification": "Snort Error",
            "priority": 1,
            "protocol": "UDP",
            "source_port": 12345,
            "dest_port": 53
        },
        {
            "type": "FAILED",
            "message": "Stream5: TCP packet out of state",
            "classification": "Snort Error",
            "priority": 2,
            "protocol": "TCP",
            "source_port": 80,
            "dest_port": 12345
        },
        {
            "type": "FAILED",
            "message": "Frag3: Fragment reassembly failed",
            "classification": "Snort Error",
            "priority": 1,
            "protocol": "IP",
            "source_port": 0,
            "dest_port": 0
        },
        {
            "type": "FAILED",
            "message": "HTTP Inspect: Invalid HTTP request",
            "classification": "Snort Error",
            "priority": 2,
            "protocol": "TCP",
            "source_port": 80,
            "dest_port": 12345
        }
    ]
    
    # Generate alerts
    alerts = []
    base_time = datetime.now() - timedelta(hours=1)
    
    for i in range(num_alerts):
        # Select a random alert type
        alert = random.choice(alert_types)
        
        # Generate random IPs
        source_ip = f"192.168.{random.randint(1, 254)}.{random.randint(1, 254)}"
        dest_ip = f"10.0.{random.randint(1, 254)}.{random.randint(1, 254)}"
        
        # Generate timestamp
        timestamp = base_time + timedelta(minutes=i*5)
        
        # Create alert line
        alert_line = (
            f"[{timestamp.strftime('%m/%d-%H:%M:%S.%f')[:-3]}] "
            f"[**] [{alert['type']}] {alert['message']} [**] "
            f"[Classification: {alert['classification']}] [Priority: {alert['priority']}] "
            f"{alert['protocol']} {source_ip}:{alert['source_port']} -> {dest_ip}:{alert['dest_port']}"
        )
        alerts.append(alert_line)
    
    # Write alerts to file
    try:
        with open(output_file, 'w') as f:
            f.write('\n'.join(alerts))
        console.print(f"[green]Successfully generated {num_alerts} test alerts[/green]")
        console.print(f"[blue]Output file: {output_file}[/blue]")
    except Exception as e:
        console.print(f"[red]Error writing alerts to file: {str(e)}[/red]")

@click.command()
@click.option('--num-alerts', default=10, help='Number of test alerts to generate')
@click.option('--output-file', default='~/snort_test/alert', help='Path to output file')
def main(num_alerts: int, output_file: str):
    """Generate test Snort alerts."""
    generate_test_alerts(num_alerts, output_file)

if __name__ == '__main__':
    main() 