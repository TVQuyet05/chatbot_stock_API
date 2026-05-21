"""
In-memory token-bucket rate limiter (per client_id).
"""

import time
from collections import defaultdict
from dataclasses import dataclass, field
from threading import Lock

from src.core.config import get_settings


@dataclass
class _Bucket:
    tokens: float
    last_refill: float
    lock: Lock = field(default_factory=Lock)


class RateLimiter:
    """
    Token-bucket rate limiter.

    Each ``client_id`` gets its own bucket with ``max_tokens`` capacity
    that refills at a constant rate over ``window`` seconds.
    """

    def __init__(
        self,
        max_tokens: int | None = None,
        window: int | None = None,
    ) -> None:
        settings = get_settings()
        self.max_tokens = max_tokens or settings.RATE_LIMIT_REQUESTS
        self.window = window or settings.RATE_LIMIT_WINDOW
        self.refill_rate = self.max_tokens / self.window
        self._buckets: dict[str, _Bucket] = defaultdict(
            lambda: _Bucket(tokens=self.max_tokens, last_refill=time.monotonic())
        )

    def _refill(self, bucket: _Bucket) -> None:
        now = time.monotonic()
        elapsed = now - bucket.last_refill
        bucket.tokens = min(self.max_tokens, bucket.tokens + elapsed * self.refill_rate)
        bucket.last_refill = now

    def is_allowed(self, client_id: str) -> bool:
        """
        Check whether the client may proceed.

        Returns True if a token was consumed, False if rate-limited.
        """
        bucket = self._buckets[client_id]
        with bucket.lock:
            self._refill(bucket)
            if bucket.tokens >= 1:
                bucket.tokens -= 1
                return True
            return False

    def remaining(self, client_id: str) -> int:
        """Return the approximate number of remaining tokens."""
        bucket = self._buckets[client_id]
        with bucket.lock:
            self._refill(bucket)
            return int(bucket.tokens)


# Global singleton
_rate_limiter: RateLimiter | None = None


def get_rate_limiter() -> RateLimiter:
    """Return the global rate limiter instance."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter
