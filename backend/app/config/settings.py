import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    DATABASE_URL: str
    GEE_PROJECT_ID: Optional[str] = None
    GEE_SERVICE_ACCOUNT_JSON: Optional[str] = None
    
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), ".env"),
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()
