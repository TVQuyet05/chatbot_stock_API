"""
SQLAlchemy ORM model for API clients.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.db.postgres import Base


class APIClient(Base):
    """Registered API client (OAuth2 consumer)."""

    __tablename__ = "api_clients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    client_id: Mapped[str] = mapped_column(
        String(64), unique=True, index=True,
        default=lambda: uuid.uuid4().hex,
    )
    client_secret_hash: Mapped[str] = mapped_column(String(128))
    name: Mapped[str] = mapped_column(String(100))
    tier: Mapped[str] = mapped_column(String(20), default="free")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    request_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
