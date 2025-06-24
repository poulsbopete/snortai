# SnortAI - Snort Failure Analysis with AI

This application analyzes Snort alerts using AI to provide insights into why and where Snort is failing. It combines Snort alerts, Elasticsearch Serverless, and OpenAI to create a comprehensive analysis system.

## Features

- Real-time Snort alert capture and parsing
- Elasticsearch Serverless integration for alert storage
- OpenAI-powered analysis of alert patterns and failures
- Web interface for viewing insights and alerts
- Historical trend analysis
- Interactive CLI for discussing Snort issues with AI
- Test data generation with realistic failure scenarios

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with the following variables:
```
OPENAI_API_KEY=your_openai_api_key
ELASTICSEARCH_URL=your_elasticsearch_url
ELASTICSEARCH_API_KEY=your_elasticsearch_api_key
ELASTICSEARCH_INDEX=your_index_name
```

3. Configure Snort to output alerts in a format compatible with the application

4. Run the application:
```bash
uvicorn app.main:app --reload
```

## Fresh Start: Recreate Python Environment

If you want to start with a clean Python environment (recommended if you have dependency issues):

```bash
# Deactivate any active environment
deactivate

# Remove the old environment
rm -rf venv

# Create a new virtual environment
python3 -m venv venv

# Activate the new environment
source venv/bin/activate

# Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r app/requirements.txt
```

## Test Data Generation and Usage

The application includes a test data generator that creates realistic Snort alerts, including various failure scenarios. This is useful for testing and development without needing a live Snort installation.

### Generating Test Data

1. Generate test alerts:
```bash
python -m app.scripts.generate_test_alerts
```
This will create a file at `~/snort_test/alert` with sample alerts.

2. Index the alerts in Elasticsearch:
```bash
python -m app.scripts.index_alerts
```

### Sample Data Contents

The generator creates alerts with the following failure scenarios:

1. **Packet Processing Failures**:
   - Invalid packet length errors
   - Buffer overflow in preprocessor
   - Packet drops

2. **Stream Processing Issues**:
   - TCP packets out of state
   - Stream reassembly failures

3. **Fragment Reassembly Problems**:
   - Frag3 fragment reassembly failures
   - IP fragment handling issues

4. **Preprocessor Failures**:
   - HTTP Inspect preprocessor errors
   - Invalid protocol handling

### Analyzing Sample Data

After generating and indexing the test data, you can use the AI chat interface to analyze the failures:

```bash
python -m app.cli.ai_chat
```

Example questions you can ask:
1. "Why did Snort fail to process the packet with invalid length?"
2. "What does the Stream5 TCP packet out of state error mean?"
3. "How can I fix the Frag3 fragment reassembly failures?"
4. "What's causing the HTTP Inspect preprocessor to fail?"

The AI will analyze these alerts and provide insights into why Snort failed and how to address each issue.

## Project Structure

- `app/`
  - `main.py` - FastAPI application entry point
  - `snort/` - Snort alert processing modules
  - `elastic/` - Elasticsearch integration
  - `ai/` - OpenAI analysis modules
  - `web/` - Web interface templates and static files
  - `models/` - Data models and schemas
  - `config.py` - Configuration management
  - `scripts/` - Utility scripts for test data generation
  - `cli/` - Command-line interface tools

## License

MIT License 