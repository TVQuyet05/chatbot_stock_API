"""
JWT token creation and verification.
"""

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from src.core.config import get_settings


def create_access_token(client_id: str, extra_claims: dict | None = None) -> tuple[str, int]:
    """
    Create a signed JWT.

    Returns:
        Tuple of (token_string, expires_in_seconds).
    """
    settings = get_settings()
    expires_in = settings.JWT_EXPIRATION_MINUTES * 60
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)

    payload = {
        "sub": client_id,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    if extra_claims:
        payload.update(extra_claims)

    token = jwt.encode(payload, settings.OAUTH2_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token, expires_in


def verify_access_token(token: str) -> dict:
    """
    Decode and verify a JWT.

    Returns:
        Decoded payload dict.

    Raises:
        JWTError: If the token is invalid or expired.
    """
    settings = get_settings()
    return jwt.decode(token, settings.OAUTH2_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
