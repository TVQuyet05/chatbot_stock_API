"""
Application configuration using Pydantic BaseSettings.

All settings are loaded from environment variables with sensible defaults.
"""

import os
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Central application settings."""

    # ── App ──────────────────────────────────────────────
    APP_NAME: str = "Stock Law Advisory API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # ── Milvus ───────────────────────────────────────────
    MILVUS_HOST: str = "localhost"
    MILVUS_PORT: int = 19530
    MILVUS_COLLECTION: str = "vietnam_securities_law"

    @property
    def MILVUS_URI(self) -> str:
        return f"http://{self.MILVUS_HOST}:{self.MILVUS_PORT}"

    # ── Embedding ────────────────────────────────────────
    EMBEDDING_MODEL: str = "bkai-foundation-models/vietnamese-bi-encoder"
    EMBEDDING_DIMENSION: int = 768

    # ── Chunking ─────────────────────────────────────────
    MAX_CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 100

    # ── Data ─────────────────────────────────────────────
    KNOWLEDGE_DIR: str = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "datasets", "ViSecQA", "knowledge",
    )

    # ── Retrieval ────────────────────────────────────────
    TOP_K: int = 5
    SCORE_THRESHOLD: float = 0.5

    # ── Gemini LLM ───────────────────────────────────────
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash"

    # ── PostgreSQL ───────────────────────────────────────
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "stocklaw"
    POSTGRES_PASSWORD: str = "stocklaw_secret"
    POSTGRES_DB: str = "stocklaw_auth"

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # ── OAuth2 / JWT ─────────────────────────────────────
    OAUTH2_SECRET_KEY: str = "change-me-in-production-use-openssl-rand-hex-32"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60

    # ── Rate Limiting ────────────────────────────────────
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 3600  # seconds (1 hour)

    # ── Admin ────────────────────────────────────────────
    ADMIN_API_KEY: str = "admin-change-me-in-production"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


@lru_cache
def get_settings() -> Settings:
    """Return cached settings singleton."""
    return Settings()
