from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings


def _key_func(request):
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return get_remote_address(request)


storage_uri = settings.REDIS_URL or None
limiter = Limiter(
    key_func=_key_func,
    default_limits=[settings.RATE_LIMIT_DEFAULT],
    storage_uri=storage_uri,
)
