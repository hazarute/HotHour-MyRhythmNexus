"""Refresh-token revocation store.

This module uses Redis for cross-process revocation when a `REDIS_URL`
is configured in settings. If Redis is not configured/available it
falls back to a process-local in-memory set (not durable, not shared
across workers). The functions below provide a minimal API used by
the auth endpoints: `revoke_refresh_token` and
`is_refresh_token_revoked`.
"""
from typing import Optional, Set

from app.core.config import settings
from app.core.redis_client import get_redis_client

_revoked_tokens: Set[str] = set()

_redis_client = get_redis_client()


def _redis_key(token: str) -> str:
    return f"{settings.REDIS_REVOKED_KEY_PREFIX}{token}"


def revoke_refresh_token(token: str) -> None:
    if not token:
        return
    # If redis is configured use it with TTL equal to refresh token lifetime
    if _redis_client:
        try:
            ttl = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
            _redis_client.set(_redis_key(token), "1", ex=ttl)
            return
        except Exception:
            # if redis fails, fall back to in-memory
            pass
    _revoked_tokens.add(token)


def is_refresh_token_revoked(token: str) -> bool:
    if not token:
        return False
    if _redis_client:
        try:
            return _redis_client.exists(_redis_key(token)) == 1
        except Exception:
            # fall back to in-memory check on redis error
            pass
    return token in _revoked_tokens
