from pydantic_settings import BaseSettings
from typing import List, Dict
import json
from pydantic import field_validator

class Settings(BaseSettings):
    """
    Application settings with type validation using Pydantic.
    Values are defined in settings.py
    """
    # API settings
    API_V1_STR: str
    PROJECT_NAME: str
    VERSION: str
    
    # Database settings
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_DB: str
    DATABASE_URL: str

    @property
    def sync_database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # CORS settings
    BACKEND_CORS_ORIGINS: List[str]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def validate_cors_origins(cls, v):
        """Parse CORS origins from string or list"""
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [i.strip() for i in v.split(",")]
        return v
    
    # Gemini settings
    GEMINI_API_KEY: str
    GEMINI_MODEL: str
    EMBEDDING_MODEL: str
    EMBEDDING_DIMENSIONS: int
    
    # Rate limits
    MAX_RPM: int
    MAX_TPM: int
    MAX_CHUNK_TOKENS: int
    EMBEDDING_MAX_RPM: int
    
    # Document processing settings
    CHUNK_SIZE: int
    CHUNK_OVERLAP: int
    MAX_CHUNKS_PER_DOC: int
    SIMILARITY_TOP_K: int
    EMBEDDING_BATCH_SIZE: int
    MAX_FILE_SIZE: int
    
    # Chat configurations
    TEMPERATURE: float
    MAX_TOKENS: int
    SYSTEM_PROMPT: str
    SIMILARITY_THRESHOLD: float
    MAX_HISTORY: int
    
    # Supported file types
    SUPPORTED_FILE_TYPES: Dict[str, str]
    
    # Logging settings
    LOG_FORMAT: str
    LOG_LEVEL: str

    class Config:
        case_sensitive = True
        env_file = ".env"