import os
from scripts.generate_test_alerts import generate_test_alerts
from scripts.index_alerts import index_alerts

def lambda_handler(event, context):
    # Generate test alerts
    output_file = os.path.expanduser('~/snort_test/alert')
    generate_test_alerts(num_alerts=10, output_file=output_file)
    # Index the alerts
    index_alerts(alert_file=output_file, batch_size=100)
    return {"status": "success"}