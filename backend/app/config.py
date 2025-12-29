"""Application configuration using Pydantic Settings."""

from typing import Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    DATABASE_URL: str = Field(..., description="PostgreSQL database URL")
    REDIS_URL: str = Field(
        default="redis://localhost:6379", description="Redis connection URL"
    )
    QDRANT_URL: str = Field(
        default="http://localhost:6333", description="Qdrant vector database URL"
    )

    OPENROUTER_API_KEY: str = Field(
        ..., description="OpenRouter API key for LLM access"
    )
    OPENROUTER_BASE_URL: str = Field(
        default="https://openrouter.ai/api/v1", description="OpenRouter API base URL"
    )
    OPENAI_API_KEY: Optional[str] = Field(
        default=None, description="OpenAI API key (optional)"
    )

    SECRET_KEY: str = Field(..., min_length=32, description="JWT secret key")

    ENVIRONMENT: str = Field(
        default="development", description="Environment (development/production)"
    )

    PDPA_DATA_RETENTION_DAYS: int = Field(
        default=30, description="PDPA data retention period in days"
    )
    PDPA_SESSION_TTL_MINUTES: int = Field(
        default=30, description="Session TTL in minutes"
    )

    EMBEDDING_MODEL: str = Field(
        default="text-embedding-3-small", description="Embedding model name"
    )
    EMBEDDING_DIMENSION: int = Field(
        default=1536, description="Embedding vector dimension"
    )
    RERANKER_MODEL: str = Field(
        default="BAAI/bge-reranker-v2-m3", description="Reranker model name"
    )

    CHUNK_SIZE: int = Field(default=512, description="Chunk size in tokens")
    CHUNK_OVERLAP: int = Field(default=50, description="Chunk overlap in tokens")
    CHUNK_SIMILARITY_THRESHOLD: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Similarity threshold for semantic chunking",
    )

    RETRIEVAL_TOP_K: int = Field(
        default=50, description="Top K documents for retrieval"
    )
    RERANK_TOP_N: int = Field(default=5, description="Top N documents after reranking")
    CONTEXT_TOKEN_BUDGET: int = Field(
        default=4000, description="Maximum tokens for context"
    )

    LLM_MODEL_PRIMARY: str = Field(
        default="openai/gpt-4o-mini", description="Primary LLM model"
    )
    LLM_MODEL_FALLBACK: str = Field(
        default="openai/gpt-4o", description="Fallback LLM model"
    )
    LLM_TEMPERATURE: float = Field(
        default=0.7, ge=0.0, le=2.0, description="LLM temperature"
    )

    BUSINESS_HOURS_START: str = Field(
        default="09:00", description="Business hours start (HH:MM)"
    )
    BUSINESS_HOURS_END: str = Field(
        default="18:00", description="Business hours end (HH:MM)"
    )
    TIMEZONE: str = Field(default="Asia/Singapore", description="Timezone")

    MAX_CONCURRENT_REQUESTS: int = Field(
        default=100, description="Maximum concurrent requests"
    )
    REQUEST_TIMEOUT: int = Field(default=30, description="Request timeout in seconds")

    DEBUG: bool = Field(default=False, description="Debug mode")
    ENABLE_RAGAS_EVALUATION: bool = Field(
        default=False, description="Enable RAGAS evaluation"
    )
    ENABLE_SENTIMENT_ANALYSIS: bool = Field(
        default=True, description="Enable sentiment analysis"
    )

    @field_validator("OPENROUTER_BASE_URL")
    @classmethod
    def normalize_openrouter_url(cls, v: str) -> str:
        """Ensure OpenRouter base URL ends with /v1."""
        if not v.endswith("/v1"):
            v = f"{v.rstrip('/')}/v1"
        return v

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.ENVIRONMENT == "development"


settings = Settings()
