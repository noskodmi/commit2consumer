from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/repo2chat"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Vector Database
    CHROMA_PATH: str = "./chroma_db"
    
    # GitHub
    GITHUB_TOKEN: str = ""
    
    # OpenAI
    OPENAI_API_KEY: str = ""
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Processing
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    MAX_REPO_SIZE: int = 500 * 1024 * 1024  # 500MB
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    # Rate Limits
    REQUESTS_PER_MINUTE: int = 100
    GITHUB_API_RATE_LIMIT: int = 5000
    
    class Config:
        env_file = ".env"

settings = Settings()
