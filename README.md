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

## Test Data Generation

The application includes a test data generator that creates realistic Snort alerts, including various failure scenarios. To generate test data:

```bash
python -m app.scripts.generate_test_alerts
```

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

## Interactive AI Chat

Use the interactive CLI to discuss Snort issues with the AI:

```bash
python -m app.cli.ai_chat
```

Example questions you can ask:
1. "Why did Snort fail to process the packet with invalid length?"
2. "What does the Stream5 TCP packet out of state error mean?"
3. "How can I fix the Frag3 fragment reassembly failures?"
4. "What's causing the HTTP Inspect preprocessor to fail?"

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