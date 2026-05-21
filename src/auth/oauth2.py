"""
OAuth2 client credentials — registration, authentication, lookup.
"""

import logging
import secrets
import uuid

from passlib.context import CryptContext
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import APIClient
from src.db.postgres import get_session_factory

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _hash_secret(secret: str) -> str:
    return pwd_context.hash(secret)


def _verify_secret(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


async def register_client(name: str) -> dict:
    """
    Register a new API client.

    Returns dict with ``client_id`` and ``client_secret`` (plaintext, shown once).
    """
    client_id = uuid.uuid4().hex
    client_secret = secrets.token_urlsafe(32)

    client = APIClient(
        client_id=client_id,
        client_secret_hash=_hash_secret(client_secret),
        name=name,
    )

    factory = get_session_factory()
    async with factory() as session:
        session.add(client)
        await session.commit()

    logger.info("Registered client: %s (%s)", name, client_id)
    return {"client_id": client_id, "client_secret": client_secret, "name": name}


async def authenticate_client(client_id: str, client_secret: str) -> APIClient | None:
    """
    Verify client credentials.

    Returns the ``APIClient`` row if valid, ``None`` otherwise.
    """
    factory = get_session_factory()
    async with factory() as session:
        stmt = select(APIClient).where(
            APIClient.client_id == client_id,
            APIClient.is_active.is_(True),
        )
        result = await session.execute(stmt)
        client = result.scalar_one_or_none()

    if client is None:
        return None

    if not _verify_secret(client_secret, client.client_secret_hash):
        return None

    return client


async def get_client_by_id(client_id: str) -> APIClient | None:
    """Look up a client by ``client_id``."""
    factory = get_session_factory()
    async with factory() as session:
        stmt = select(APIClient).where(APIClient.client_id == client_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()


async def list_clients() -> list[APIClient]:
    """Return all registered clients."""
    factory = get_session_factory()
    async with factory() as session:
        result = await session.execute(select(APIClient).order_by(APIClient.created_at.desc()))
        return list(result.scalars().all())


async def delete_client(client_id: str) -> bool:
    """Deactivate (soft-delete) a client. Returns True if found."""
    factory = get_session_factory()
    async with factory() as session:
        stmt = (
            update(APIClient)
            .where(APIClient.client_id == client_id)
            .values(is_active=False)
        )
        result = await session.execute(stmt)
        await session.commit()
        return result.rowcount > 0


async def reset_client_secret(client_id: str) -> str | None:
    """
    Generate a new secret for the client.

    Returns the new plaintext secret, or None if client not found.
    """
    new_secret = secrets.token_urlsafe(32)
    factory = get_session_factory()
    async with factory() as session:
        stmt = (
            update(APIClient)
            .where(APIClient.client_id == client_id, APIClient.is_active.is_(True))
            .values(client_secret_hash=_hash_secret(new_secret))
        )
        result = await session.execute(stmt)
        await session.commit()
        if result.rowcount == 0:
            return None
    return new_secret


async def increment_request_count(client_id: str) -> None:
    """Increment the request counter for a client."""
    factory = get_session_factory()
    async with factory() as session:
        stmt = (
            update(APIClient)
            .where(APIClient.client_id == client_id)
            .values(request_count=APIClient.request_count + 1)
        )
        await session.execute(stmt)
        await session.commit()
