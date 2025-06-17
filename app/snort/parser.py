import re
from datetime import datetime
from typing import Optional
from app.models.snort import SnortAlert

def parse_alert_line(line: str) -> Optional[SnortAlert]:
    """
    Parse a line from a Snort alert file into a SnortAlert object.
    
    Example alert line format:
    [03/20-10:00:00.123] [**] [FAILED] Failed to process packet: Invalid packet length [**] [Classification: Snort Error] [Priority: 1] TCP 192.168.1.1:54321 -> 10.0.0.1:443
    
    Args:
        line: A line from the Snort alert file
        
    Returns:
        SnortAlert object if parsing successful, None otherwise
    """
    try:
        # Skip empty lines
        if not line.strip():
            return None
            
        # Extract timestamp
        timestamp_match = re.search(r'\[(\d{2}/\d{2}-\d{2}:\d{2}:\d{2}\.\d{3})\]', line)
        if not timestamp_match:
            return None
            
        # Parse timestamp
        timestamp_str = timestamp_match.group(1)
        timestamp = datetime.strptime(timestamp_str, '%m/%d-%H:%M:%S.%f')
        
        # Extract alert type and message
        alert_match = re.search(r'\[\*\*\] \[([^\]]+)\] (.+?) \[\*\*\]', line)
        if not alert_match:
            return None
            
        alert_type = alert_match.group(1)
        message = alert_match.group(2).strip()
        
        # Extract classification and priority
        class_match = re.search(r'\[Classification: (.+?)\]', line)
        priority_match = re.search(r'\[Priority: (\d+)\]', line)
        
        classification = class_match.group(1) if class_match else "Unknown"
        priority = int(priority_match.group(1)) if priority_match else 0
        
        # Extract protocol and IP addresses
        ip_match = re.search(r'(\w+) (\d+\.\d+\.\d+\.\d+):(\d+) -> (\d+\.\d+\.\d+\.\d+):(\d+)', line)
        if not ip_match:
            return None
            
        protocol = ip_match.group(1)
        source_ip = ip_match.group(2)
        source_port = int(ip_match.group(3))
        destination_ip = ip_match.group(4)
        destination_port = int(ip_match.group(5))
        
        # Generate signature ID for failed alerts
        signature_id = f"0:0:0" if alert_type == "FAILED" else alert_type
        
        return SnortAlert(
            timestamp=timestamp.isoformat(),
            alert_type=alert_type,
            priority=priority,
            message=message,
            source_ip=source_ip,
            source_port=source_port,
            destination_ip=destination_ip,
            destination_port=destination_port,
            protocol=protocol,
            classification=classification,
            signature_id=signature_id,
            raw_alert=line.strip()
        )
        
    except Exception as e:
        print(f"Error parsing alert line: {str(e)}")
        return None 