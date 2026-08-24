"""Application configuration loaded from environment variables."""

from functools import lru_cache
from typing import Literal

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    environment: Literal["development", "staging", "production"] = "development"
    app_name: str = "AgentOps360"
    app_version: str = "1.0.0"

    openai_api_key: str = ""
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_database: str = "agentops360"
    mongodb_required: bool = False
    chroma_persist_dir: str = "./chroma_db"
    openai_model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"
    backend_port: int = 8000
    frontend_url: str = "http://localhost:3000"
    cors_origins: str = "http://localhost:3000"
    mock_mode: bool = True
    seed_demo_data: bool = True
    docs_enabled: bool = True
    log_level: str = "INFO"
    max_upload_size_mb: int = 10
    langsmith_api_key: str = ""
    redis_url: str = ""
    upload_dir: str = "./uploads"

    # ChromaDB — local PersistentClient or Chroma Cloud
    chroma_use_cloud: bool = False
    chroma_api_key: str = ""
    chroma_tenant: str = ""
    chroma_database: str = "AgentOps360"
    chroma_collection_name: str = "agentops360_knowledge"
    chroma_cloud_host: str = "api.trychroma.com"
    chroma_auto_create_database: bool = True
    chroma_fallback_to_local: bool = True
    embedding_dimension: int = 1536

    @field_validator("cors_origins")
    @classmethod
    def strip_cors(cls, v: str) -> str:
        return v.strip()

    @model_validator(mode="after")
    def validate_production(self) -> "Settings":
        if self.environment == "production":
            if self.mock_mode:
                raise ValueError("MOCK_MODE must be false when ENVIRONMENT=production")
            if not self.openai_api_key:
                raise ValueError("OPENAI_API_KEY is required when ENVIRONMENT=production")
            if self.mongodb_required and "localhost" in self.mongodb_uri:
                raise ValueError("Use a production MongoDB URI when ENVIRONMENT=production")
            if self.chroma_use_cloud and not self.chroma_api_key:
                raise ValueError("CHROMA_API_KEY is required when CHROMA_USE_CLOUD=true in production")
        if self.chroma_use_cloud and not self.chroma_api_key:
            raise ValueError("CHROMA_API_KEY is required when CHROMA_USE_CLOUD=true")
        if self.chroma_use_cloud and not self.chroma_tenant:
            raise ValueError("CHROMA_TENANT is required when CHROMA_USE_CLOUD=true")
        return self

    def cors_origin_list(self) -> list[str]:
        origins = [o.strip() for o in self.cors_origins.split(",") if o.strip()]
        if self.frontend_url and self.frontend_url not in origins:
            origins.append(self.frontend_url)
        return origins

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    return Settings()
