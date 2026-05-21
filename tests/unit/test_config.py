import pytest
from src.core.config import Settings

def test_settings_defaults():
    settings = Settings()
    assert settings.APP_NAME == "Stock Law Advisory API"
    assert settings.MILVUS_PORT == 19530
    assert settings.JWT_ALGORITHM == "HS256"

def test_database_url():
    settings = Settings(POSTGRES_USER="test", POSTGRES_PASSWORD="pwd", POSTGRES_HOST="localhost", POSTGRES_DB="db")
    assert "postgresql+asyncpg://test:pwd@localhost:5432/db" in settings.DATABASE_URL
