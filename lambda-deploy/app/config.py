from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from dotenv import load_dotenv

# Add for AWS Secrets Manager
import boto3
import json

def get_secret(secret_name, region_name="us-east-1"):
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name=region_name)
    get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    secret = get_secret_value_response['SecretString']
    return json.loads(secret)

load_dotenv()

# Try to load secrets from AWS Secrets Manager if running in Lambda
if os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
    # Default secret name and region for us-east-1 and account 461485115270
    # Example ARN: arn:aws:secretsmanager:us-east-1:461485115270:secret:snortai/prod/api-keys-xxxxxx
    secret_name = os.environ.get("SNORTAI_SECRET_NAME", "snortai/prod/api-keys")
    region_name = os.environ.get("AWS_REGION", "us-east-1")
    try:
        secrets = get_secret(secret_name, region_name)
        os.environ["ELASTICSEARCH_URL"] = secrets.get("ELASTICSEARCH_URL", "")
        os.environ["ELASTICSEARCH_API_KEY"] = secrets.get("ELASTICSEARCH_API_KEY", "")
        os.environ["OPENAI_API_KEY"] = secrets.get("OPENAI_API_KEY", "")
    except Exception as e:
        print(f"Could not load secrets from AWS Secrets Manager: {e}")

class Settings(BaseSettings):
    # Elasticsearch Configuration
    elasticsearch_url: str = os.getenv("ELASTICSEARCH_URL", "")
    elasticsearch_api_key: str = os.getenv("ELASTICSEARCH_API_KEY", "")
    elasticsearch_index: str = os.getenv("ELASTICSEARCH_INDEX", "snort-alerts")
    
    # OpenAI Configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    openai_max_tokens: int = int(os.getenv("OPENAI_MAX_TOKENS", "2000"))
    openai_temperature: float = float(os.getenv("OPENAI_TEMPERATURE", "0.1"))
    
    # AI Backend Configuration
    ai_backend: str = os.getenv("AI_BACKEND", "openai")  # "openai" or "onechat"
    ai_backend_fallback: bool = os.getenv("AI_BACKEND_FALLBACK", "true").lower() == "true"
    
    # Snort Configuration
    snort_alert_file: str = os.getenv("SNORT_ALERT_FILE", "/var/log/snort/alert")
    
    # Application Configuration
    app_name: str = "SnortAI"
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings() 