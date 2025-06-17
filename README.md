# SnortAI - Snort Failure Analysis with AI

This application analyzes Snort alerts using AI to provide insights into why and where Snort is failing. It combines Snort alerts, Elasticsearch Serverless, and OpenAI to create a comprehensive analysis system.

## Features

- Real-time Snort alert capture and parsing
- Elasticsearch Serverless integration for alert storage
- OpenAI-powered analysis of alert patterns and failures
- Web interface for viewing insights and alerts
- Historical trend analysis

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
```

3. Configure Snort to output alerts in a format compatible with the application

4. Run the application:
```bash
uvicorn app.main:app --reload
```

## Project Structure

- `app/`
  - `main.py` - FastAPI application entry point
  - `snort/` - Snort alert processing modules
  - `elastic/` - Elasticsearch integration
  - `ai/` - OpenAI analysis modules
  - `web/` - Web interface templates and static files
  - `models/` - Data models and schemas
  - `config.py` - Configuration management

## License

MIT License 