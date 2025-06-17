from pydantic import BaseSettings
from functools import lru_cache
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # OpenAI Configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    
    # Elasticsearch Configuration
    elasticsearch_url: str = os.getenv("ELASTICSEARCH_URL", "")
    elasticsearch_api_key: str = os.getenv("ELASTICSEARCH_API_KEY", "")
    
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