"""Configuration settings for the Snowflake AI Agent."""

import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class SnowflakeSettings(BaseSettings):
    """Snowflake connection settings."""
    
    account: str
    user: str
    password: Optional[str] = None
    warehouse: Optional[str] = None
    database: Optional[str] = None
    schema: Optional[str] = None
    role: Optional[str] = None
    
    # Secure authentication options
    authenticator: Optional[str] = None
    private_key_path: Optional[str] = None
    private_key_passphrase: Optional[str] = None
    oauth_token: Optional[str] = None
    
    model_config = {
        "env_file": ".env", 
        "env_prefix": "SNOWFLAKE_",
        "extra": "ignore"  # Ignore extra fields
    }


class AISettings(BaseSettings):
    """AI model settings."""
    
    openai_api_key: str = "your_openai_api_key"
    model: str = "gpt-3.5-turbo"
    temperature: float = 0.1
    max_tokens: int = 2000
    
    model_config = {
        "env_file": ".env", 
        "extra": "ignore"
    }


class AppSettings(BaseSettings):
    """Application settings."""
    
    log_level: str = "INFO"
    max_query_results: int = 100
    query_timeout: int = 30
    
    model_config = {
        "env_file": ".env", 
        "extra": "ignore"
    }


# Global settings instances
try:
    snowflake_settings = SnowflakeSettings()
    ai_settings = AISettings()
    app_settings = AppSettings()
except Exception as e:
    print(f"Error loading settings: {e}")
    print("Please check your .env file configuration")
    raise