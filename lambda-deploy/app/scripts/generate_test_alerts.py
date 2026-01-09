import os
import click
from rich.console import Console
from datetime import datetime, timedelta
import random

console = Console()

def generate_test_alerts(num_alerts: int = 10, output_file: str = "~/snort_test/alert"):
    """Generate test Snort alerts with various failure scenarios and realistic attack patterns."""
    # Expand home directory in path
    output_file = os.path.expanduser(output_file)
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Define comprehensive alert types and their characteristics
    alert_types = [
        # Network Scanning & Reconnaissance
        {
            "type": "SCAN",
            "message": "ICMP PING NMAP",
            "classification": "Misc activity",
            "priority": 3,
            "protocol": "ICMP",
            "source_port": 0,
            "dest_port": 0
        },
        {
            "type": "SCAN",
            "message": "TCP SYN Scan",
            "classification": "Attempted Information Leak",
            "priority": 2,
            "protocol": "TCP",
            "source_port": random.randint(1024, 65535),
            "dest_port": random.choice([21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995])
        },
        {
            "type": "SCAN",
            "message": "UDP Port Scan",
            "classification": "Attempted Information Leak",
            "priority": 2,
            "protocol": "UDP",
            "source_port": random.randint(1024, 65535),
            "dest_port": random.choice([53, 67, 68, 69, 123, 135, 137, 138, 161, 162, 445])
        },
        {
            "type": "SCAN",
            "message": "FIN Scan",
            "classification": "Attempted Information Leak",
            "priority": 2,
            "protocol": "TCP",
            "source_port": random.randint(1024, 65535),
            "dest_port": random.choice([21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995])
        },
        {
            "type": "SCAN",
            "message": "XMAS Scan",
            "classification": "Attempted Information Leak",
            "priority": 2,
            "protocol": "TCP",
            "source_port": random.randint(1024, 65535),
            "dest_port": random.choice([21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995])
        },
        
        # Web Application Attacks
        {
            "type": "WEB-ATTACKS",
            "message": "SQL Injection Attack",
            "classification": "Attempted User Privilege Gain",
            "priority": 1,
            "protocol": "TCP",
            "source_port": random.randint(1024, 65535),
            "dest_port": 80
        },
        {
            "type": "WEB-ATTACKS",
            "message": "Cross-Site Scripting (XSS) Attempt",
            "classification": "Attempted User Privilege Gain",
            "priority": 1,
            "protocol": "TCP",
            "source_port": random.randint(1024, 65535),
            "dest_port": 80
        },
        {
            "type": "WEB-ATTACKS",
            "message": "Directory Traversal Attack",
            "classification": "Attempted Information Leak",
            "priority": 2,
            "protocol": "TCP",
            "source_port": random.randint(1024, 65535),
            "dest_port": 80
        },
        {
            "type": "WEB-ATTACKS",
            "message": "Command Injection Attempt",
            "classification": "Attempted User Privilege Gain",
            "priority": 1,
            "protocol": "TCP",
            "source_port": random.randint(1024, 65535),
            "dest_port": 80
        },
        {
            "type": "WEB-ATTACKS",
            "message": "File Upload Attack",
            "classification": "Attempted User Privilege Gain",
            "priority": 1,
            "protocol": "TCP",
            "source_port": random.randint(1024, 65535),
            "dest_port": 80
        },
        
        # Malware & Botnet Activity
        {
            "type": "MALWARE",
            "message": "Botnet C&C Communication",
            "classification": "Trojan Activity",
            "priority": 1,
            "protocol": "TCP",
            "source_port": random.randint(1024, 65535),
            "dest_port": random.choice([80, 443, 8080, 8443])
        },
        {
            "type": "MALWARE",
            "message": "Malware Download Attempt",
            "classification": "Malware",
            "priority": 1,
            "protocol": "TCP",
            "source_port": random.randint(1024, 65535),
            "dest_port": 80
        },
        {
            "type": "MALWARE",
            "message": "Ransomware Communication",
            "classification": "Malware",
            "priority": 1,
            "protocol": "TCP",
            "source_port": random.randint(1024, 65535),
            "dest_port": 443
        },
        {
            "type": "MALWARE",
            "message": "Cryptocurrency Mining Pool Connection",
            "classification": "Misc activity",
            "priority": 2,
            "protocol": "TCP",
            "source_port": random.randint(1024, 65535),
            "dest_port": random.choice([3333, 4444, 5555, 7777, 8888])
        },
        
        # Network Protocol Attacks
        {
            "type": "PROTOCOL",
            "message": "DNS Tunneling Attempt",
            "classification": "Attempted Information Leak",
            "priority": 2,
            "protocol": "UDP",
            "source_port": random.randint(1024, 65535),
            "dest_port": 53
        },
        {
            "type": "PROTOCOL",
            "message": "DHCP Exhaustion Attack",
            "classification": "Denial of Service",
            "priority": 2,
            "protocol": "UDP",
            "source_port": 68,
            "dest_port": 67
        },
        {
            "type": "PROTOCOL",
            "message": "ARP Spoofing Attempt",
            "classification": "Attempted Information Leak",
            "priority": 1,
            "protocol": "ARP",
            "source_port": 0,
            "dest_port": 0
        },
        {
            "type": "PROTOCOL",
            "message": "ICMP Redirect Attack",
            "classification": "Attempted Information Leak",
            "priority": 2,
            "protocol": "ICMP",
            "source_port": 0,
            "dest_port": 0
        },
        
        # Denial of Service Attacks
        {
            "type": "DOS",
            "message": "SYN Flood Attack",
            "classification": "Denial of Service",
            "priority": 1,
            "protocol": "TCP",
            "source_port": random.randint(1024, 65535),
            "dest_port": random.choice([80, 443, 22, 21, 25])
        },
        {
            "type": "DOS",
            "message": "UDP Flood Attack",
            "classification": "Denial of Service",
            "priority": 1,
            "protocol": "UDP",
            "source_port": random.randint(1024, 65535),
            "dest_port": random.choice([53, 123, 161, 500, 4500])
        },
        {
            "type": "DOS",
            "message": "ICMP Flood Attack",
            "classification": "Denial of Service",
            "priority": 1,
            "protocol": "ICMP",
            "source_port": 0,
            "dest_port": 0
        },
        {
            "type": "DOS",
            "message": "HTTP Slowloris Attack",
            "classification": "Denial of Service",
            "priority": 1,
            "protocol": "TCP",
            "source_port": random.randint(1024, 65535),
            "dest_port": 80
        },
        
        # Policy Violations
        {
            "type": "POLICY",
            "message": "P2P File Sharing Detected",
            "classification": "Policy Violation",
            "priority": 3,
            "protocol": "TCP",
            "source_port": random.randint(1024, 65535),
            "dest_port": random.choice([6881, 6882, 6883, 6884, 6885])
        },
        {
            "type": "POLICY",
            "message": "Unauthorized Remote Access Tool",
            "classification": "Policy Violation",
            "priority": 2,
            "protocol": "TCP",
            "source_port": random.randint(1024, 65535),
            "dest_port": random.choice([3389, 5900, 5901, 22, 23])
        },
        {
            "type": "POLICY",
            "message": "Tor Network Connection",
            "classification": "Policy Violation",
            "priority": 3,
            "protocol": "TCP",
            "source_port": random.randint(1024, 65535),
            "dest_port": random.choice([9001, 9030, 9050, 9051])
        },
        
        # Snort System Errors
        {
            "type": "FAILED",
            "message": "Failed to process packet: Invalid packet length",
            "classification": "Snort Error",
            "priority": 1,
            "protocol": "TCP",
            "source_port": random.randint(1024, 65535),
            "dest_port": random.choice([80, 443, 22, 21, 25])
        },
        {
            "type": "FAILED",
            "message": "Packet dropped: Buffer overflow in preprocessor",
            "classification": "Snort Error",
            "priority": 1,
            "protocol": "UDP",
            "source_port": random.randint(1024, 65535),
            "dest_port": 53
        },
        {
            "type": "FAILED",
            "message": "Stream5: TCP packet out of state",
            "classification": "Snort Error",
            "priority": 2,
            "protocol": "TCP",
            "source_port": random.choice([80, 443, 22, 21, 25]),
            "dest_port": random.randint(1024, 65535)
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
            "source_port": random.choice([80, 443]),
            "dest_port": random.randint(1024, 65535)
        },
        {
            "type": "FAILED",
            "message": "SSL/TLS: Certificate validation failed",
            "classification": "Snort Error",
            "priority": 2,
            "protocol": "TCP",
            "source_port": 443,
            "dest_port": random.randint(1024, 65535)
        },
        
        # Advanced Persistent Threats (APT)
        {
            "type": "APT",
            "message": "Lateral Movement Attempt",
            "classification": "Attempted User Privilege Gain",
            "priority": 1,
            "protocol": "TCP",
            "source_port": random.randint(1024, 65535),
            "dest_port": random.choice([135, 139, 445, 3389])
        },
        {
            "type": "APT",
            "message": "Credential Harvesting Attempt",
            "classification": "Attempted User Privilege Gain",
            "priority": 1,
            "protocol": "TCP",
            "source_port": random.randint(1024, 65535),
            "dest_port": 80
        },
        {
            "type": "APT",
            "message": "Data Exfiltration Attempt",
            "classification": "Attempted Information Leak",
            "priority": 1,
            "protocol": "TCP",
            "source_port": random.randint(1024, 65535),
            "dest_port": random.choice([80, 443, 21, 22])
        },
        
        # IoT and Embedded Device Attacks
        {
            "type": "IOT",
            "message": "IoT Device Exploit Attempt",
            "classification": "Attempted User Privilege Gain",
            "priority": 1,
            "protocol": "TCP",
            "source_port": random.randint(1024, 65535),
            "dest_port": random.choice([23, 80, 443, 8080, 8443])
        },
        {
            "type": "IOT",
            "message": "Default Credential Attack",
            "classification": "Attempted User Privilege Gain",
            "priority": 1,
            "protocol": "TCP",
            "source_port": random.randint(1024, 65535),
            "dest_port": random.choice([22, 23, 80, 443])
        },
        
        # Cloud and Container Attacks
        {
            "type": "CLOUD",
            "message": "Container Escape Attempt",
            "classification": "Attempted User Privilege Gain",
            "priority": 1,
            "protocol": "TCP",
            "source_port": random.randint(1024, 65535),
            "dest_port": random.choice([2375, 2376, 8080, 8443])
        },
        {
            "type": "CLOUD",
            "message": "Kubernetes API Exploit",
            "classification": "Attempted User Privilege Gain",
            "priority": 1,
            "protocol": "TCP",
            "source_port": random.randint(1024, 65535),
            "dest_port": 6443
        }
    ]
    
    # Generate alerts with more randomness and realistic patterns
    alerts = []
    base_time = datetime.now() - timedelta(hours=random.randint(1, 24))
    
    # Define realistic IP ranges for different scenarios
    internal_networks = [
        "192.168.1", "192.168.2", "192.168.10", "192.168.100",
        "10.0.0", "10.0.1", "10.1.0", "10.10.0",
        "172.16.0", "172.16.1", "172.17.0"
    ]
    
    external_networks = [
        "203.0.113", "198.51.100", "192.0.2", "8.8.8", "1.1.1",
        "45.33.32", "104.16.132", "151.101.1", "52.84.0", "13.107.42"
    ]
    
    # Generate alerts with burst patterns and realistic timing
    for i in range(num_alerts):
        # Select a random alert type with weighted probability
        # Higher priority alerts are less common
        weights = [1 if alert['priority'] == 1 else 2 if alert['priority'] == 2 else 3 for alert in alert_types]
        alert = random.choices(alert_types, weights=weights)[0]
        
        # Generate realistic IP addresses based on alert type
        if alert['type'] in ['SCAN', 'WEB-ATTACKS', 'MALWARE', 'APT', 'IOT', 'CLOUD']:
            # External attacks
            source_network = random.choice(external_networks)
            dest_network = random.choice(internal_networks)
        elif alert['type'] in ['POLICY', 'PROTOCOL']:
            # Internal policy violations
            source_network = random.choice(internal_networks)
            dest_network = random.choice(internal_networks)
        else:
            # Random for other types
            source_network = random.choice(internal_networks + external_networks)
            dest_network = random.choice(internal_networks + external_networks)
        
        source_ip = f"{source_network}.{random.randint(1, 254)}"
        dest_ip = f"{dest_network}.{random.randint(1, 254)}"
        
        # Generate realistic timestamps with burst patterns
        if random.random() < 0.3:  # 30% chance of burst activity
            # Burst pattern - multiple alerts in short time
            burst_duration = random.randint(1, 5)  # 1-5 minutes
            timestamp = base_time + timedelta(
                minutes=random.randint(0, 60),
                seconds=random.randint(0, 59),
                milliseconds=random.randint(0, 999)
            )
        else:
            # Normal pattern - spread out over time
            timestamp = base_time + timedelta(
                minutes=random.randint(0, 1440),  # Up to 24 hours
                seconds=random.randint(0, 59),
                milliseconds=random.randint(0, 999)
            )
        
        # Add some randomness to ports if they're not protocol-specific
        source_port = alert['source_port']
        dest_port = alert['dest_port']
        
        if source_port == 0 and alert['protocol'] not in ['ICMP', 'ARP']:
            source_port = random.randint(1024, 65535)
        elif isinstance(source_port, list):
            source_port = random.choice(source_port)
            
        if dest_port == 0 and alert['protocol'] not in ['ICMP', 'ARP']:
            dest_port = random.randint(1, 65535)
        elif isinstance(dest_port, list):
            dest_port = random.choice(dest_port)
        
        # Create alert line with signature ID
        signature_id = f"{random.randint(1, 9)}:{random.randint(1000000, 9999999)}:{random.randint(0, 9)}"
        
        alert_line = (
            f"[{timestamp.strftime('%m/%d-%H:%M:%S.%f')[:-3]}] "
            f"[**] [{signature_id}] {alert['message']} [**] "
            f"[Classification: {alert['classification']}] [Priority: {alert['priority']}] "
            f"{{{alert['protocol']}}} {source_ip}:{source_port} -> {dest_ip}:{dest_port}"
        )
        alerts.append(alert_line)
    
    # Sort alerts by timestamp for realistic ordering
    alerts.sort()
    
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