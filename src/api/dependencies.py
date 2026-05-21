"""
FastAPI dependency injection for RAG, Auth, and Rate Limiting.
"""

import logging
from typing import Annotated

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.jwt_handler import verify_access_token
from src.auth.oauth2 import get_client_by_id, increment_request_count
from src.auth.rate_limiter import get_rate_limiter
from src.core.config import get_settings
from src.db.milvus_store import create_milvus_store
from src.db.postgres import get_session_factory
from src.rag.chain import create_rag_chain
from src.rag.embedding import get_embedding_model

logger = logging.getLogger(__name__)

# Security schemes
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token", auto_error=False)
admin_key_header = APIKeyHeader(name="X-Admin-Key", auto_error=False)


async def get_db():
    """Dependency to get an async PostgreSQL session."""
    factory = get_session_factory()
    async with factory() as session:
        yield session


def get_vector_store():
    """Dependency to get the Milvus vector store."""
    embeddings = get_embedding_model()
    return create_milvus_store(embeddings=embeddings)


def get_rag_chain(vector_store=Depends(get_vector_store)):
    """Dependency to get the RAG chain."""
    return create_rag_chain(vector_store)


async def get_current_client(
    token: Annotated[str | None, Depends(oauth2_scheme)]
):
    """
    Validate the JWT token and return the client_id.
    Also handles rate limiting and request counting.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = verify_access_token(token)
        client_id: str = payload.get("sub")
        if client_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing subject",
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 1. Check if client exists and is active
    client = await get_client_by_id(client_id)
    if not client or not client.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Client inactive or not found",
        )

    # 2. Rate limiting
    limiter = get_rate_limiter()
    if not limiter.is_allowed(client_id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Try again later.",
        )

    # 3. Analytics (async increment)
    await increment_request_count(client_id)

    return client


def verify_admin(
    admin_key: Annotated[str | None, Depends(admin_key_header)]
):
    """Simple admin key verification for sensitive endpoints."""
    settings = get_settings()
    if not admin_key or admin_key != settings.ADMIN_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing Admin Key",
        )
    return True
