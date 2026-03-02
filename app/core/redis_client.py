from typing import Optional
from app.core.config import settings

_redis = None

def get_redis_client():
    """Lazily create and return a Redis client based on `REDIS_URL`.
    Returns None if Redis is not configured or import/connection fails.
    """
    global _redis
    if _redis is not None:
        return _redis
    if not settings.REDIS_URL:
        return None
    try:
        import redis as _redis_lib
        _redis = _redis_lib.from_url(settings.REDIS_URL, decode_responses=True)
        return _redis
    except Exception:
        _redis = None
        return None


def ping_redis(timeout: float = 1.0) -> bool:
    """Return True if Redis responds to PING; False otherwise."""
    client = get_redis_client()
    if not client:
        return False
    try:
        return client.ping() is True
    except Exception:
        return False
