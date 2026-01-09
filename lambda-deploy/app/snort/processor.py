import re
from datetime import datetime
from typing import Optional, List
import logging
from app.models.snort import SnortAlert
from app.config import get_settings
import os

settings = get_settings()
logger = logging.getLogger(__name__)

# Change the alert file path to use a path in the user's home directory
alert_file = os.path.expanduser("~/snort_test/alert")

class SnortAlertProcessor:
    def __init__(self):
        self.alert_pattern = re.compile(
            r'\[(?P<timestamp>.*?)\] \[(?P<signature_id>.*?)\] (?P<message>.*?) \[Classification: (?P<classification>.*?)\] \[Priority: (?P<priority>\d+)\]'
        )
        self.packet_pattern = re.compile(
            r'(?P<protocol>TCP|UDP|ICMP) (?P<source_ip>[\d\.]+):(?P<source_port>\d+) -> (?P<destination_ip>[\d\.]+):(?P<destination_port>\d+)'
        )

    def parse_alert(self, alert_line: str) -> Optional[SnortAlert]:
        """Parse a single Snort alert line into a SnortAlert object"""
        try:
            # Extract alert information
            alert_match = self.alert_pattern.search(alert_line)
            if not alert_match:
                logger.warning(f"Could not parse alert line: {alert_line}")
                return None

            # Extract packet information
            packet_match = self.packet_pattern.search(alert_line)
            if not packet_match:
                logger.warning(f"Could not parse packet information: {alert_line}")
                return None

            # Parse timestamp
            timestamp_str = alert_match.group('timestamp')
            try:
                timestamp = datetime.strptime(timestamp_str, '%m/%d-%H:%M:%S.%f')
                # Add current year since Snort doesn't include it
                timestamp = timestamp.replace(year=datetime.now().year)
            except ValueError:
                logger.warning(f"Could not parse timestamp: {timestamp_str}")
                return None

            # Create SnortAlert object
            return SnortAlert(
                timestamp=timestamp,
                alert_type=alert_match.group('message').split(']')[0].strip(),
                priority=int(alert_match.group('priority')),
                protocol=packet_match.group('protocol'),
                source_ip=packet_match.group('source_ip'),
                source_port=int(packet_match.group('source_port')),
                destination_ip=packet_match.group('destination_ip'),
                destination_port=int(packet_match.group('destination_port')),
                message=alert_match.group('message'),
                classification=alert_match.group('classification'),
                signature_id=alert_match.group('signature_id'),
                raw_alert=alert_line
            )

        except Exception as e:
            logger.error(f"Error parsing alert: {str(e)}")
            return None

    async def process_alert_file(self, file_path: str = None) -> List[SnortAlert]:
        """Process a Snort alert file and return a list of parsed alerts"""
        if file_path is None:
            file_path = settings.snort_alert_file

        alerts = []
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    alert = self.parse_alert(line.strip())
                    if alert:
                        alerts.append(alert)
        except Exception as e:
            logger.error(f"Error processing alert file: {str(e)}")

        return alerts

    async def monitor_alert_file(self, callback):
        """Monitor the Snort alert file for new alerts and call the callback function"""
        import asyncio
        import time

        last_position = 0
        file_missing_warning_shown = False
        
        while True:
            try:
                # Check if file exists before trying to open it
                if not os.path.exists(settings.snort_alert_file):
                    if not file_missing_warning_shown:
                        logger.warning(f"Snort alert file not found: {settings.snort_alert_file}")
                        logger.info("Creating a test alert file for demonstration purposes...")
                        # Create a test alert file
                        os.makedirs(os.path.dirname(settings.snort_alert_file), exist_ok=True)
                        with open(settings.snort_alert_file, 'w') as test_file:
                            test_file.write("01/27-10:00:00.000000  [**] [1:1000001:1] Test alert [**] [Classification: Test] [Priority: 1] {TCP} 192.168.1.1:1234 -> 192.168.1.2:80\n")
                        logger.info(f"Created test alert file: {settings.snort_alert_file}")
                        file_missing_warning_shown = True
                    await asyncio.sleep(5)  # Wait longer when file is missing
                    continue
                
                with open(settings.snort_alert_file, 'r') as f:
                    f.seek(last_position)
                    new_alerts = []
                    for line in f:
                        alert = self.parse_alert(line.strip())
                        if alert:
                            new_alerts.append(alert)
                    last_position = f.tell()

                    if new_alerts:
                        await callback(new_alerts)

            except Exception as e:
                logger.error(f"Error monitoring alert file: {str(e)}")

            await asyncio.sleep(1)  # Check for new alerts every second 