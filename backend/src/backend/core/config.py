from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    redis_url: str = "redis://localhost:6379"
    jira_base_url: str = ""
    jira_email: str = ""
    jira_project_key: str = ""
    jira_api_token: str = ""
    jira_timeout_seconds: float = 15.0
    langsmith_api_key: str = ""
    langsmith_tracing: bool = False
    langsmith_project: str = ""
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    max_upload_bytes: int = 10_485_760
    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    ollama_base_url: str = "http://localhost:11434"
    ollama_llm_model: str = "gemma3:4b"
    ollama_embedding_model: str = "bge-m3"
    ollama_timeout_seconds: float = 60.0
    document_storage_dir: str = "uploads/documents"
    rag_chunk_size: int = 1200
    rag_chunk_overlap: int = 200
    rag_top_k: int = 5
    celery_broker_url: str | None = None
    celery_result_backend: str | None = None

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[3] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
