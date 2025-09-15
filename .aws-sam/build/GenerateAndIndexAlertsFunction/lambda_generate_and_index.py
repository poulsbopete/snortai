import os
from scripts.generate_test_alerts import generate_test_alerts
from scripts.index_alerts import index_alerts

def lambda_handler(event, context):
    # Generate test alerts with more variety
    output_file = '/tmp/snort_alerts.txt'  # Use /tmp directory which is writable in Lambda
    # Generate 25-50 random alerts each time
    import random
    num_alerts = random.randint(25, 50)
    generate_test_alerts(num_alerts=num_alerts, output_file=output_file)
    # Index the alerts
    index_alerts(alert_file=output_file, batch_size=100)
    return {"status": "success", "alerts_generated": num_alerts}