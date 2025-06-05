# app/core/config.py

import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    
    SECRET_KEY: str 
    
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
