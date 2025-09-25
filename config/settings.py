"""
Configuration management for the Agentic POC
"""
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    
    # Qdrant Configuration
    qdrant_host: str = Field(default="localhost", env="QDRANT_HOST")
    qdrant_port: int = Field(default=6333, env="QDRANT_PORT")
    qdrant_collection_name: str = Field(default="business_rules", env="QDRANT_COLLECTION_NAME")
    
    # Ollama Configuration
    ollama_base_url: str = Field(default="http://localhost:11434", env="OLLAMA_BASE_URL")
    ollama_model: str = Field(default="llama3.2:1b", env="OLLAMA_MODEL")
    ollama_embedding_model: str = Field(default="nomic-embed-text", env="OLLAMA_EMBEDDING_MODEL")
    
    # API Configuration
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Vector DB Settings
    vector_dimension: int = Field(default=384, env="VECTOR_DIMENSION")
    top_k_results: int = Field(default=5, env="TOP_K_RESULTS")
    
    # Agent Configuration
    max_iterations: int = Field(default=10, env="MAX_ITERATIONS")
    confidence_threshold: float = Field(default=0.7, env="CONFIDENCE_THRESHOLD")
    
    # Project paths
    project_root: Path = Field(default_factory=lambda: Path(__file__).parent.parent)
    data_path: Path = Field(default_factory=lambda: Path(__file__).parent.parent / "data")
    business_rules_path: Path = Field(default_factory=lambda: Path(__file__).parent.parent / "data" / "business_rules")


# Global settings instance
settings = Settings()