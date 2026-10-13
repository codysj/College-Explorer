"""Fixed-window rate limiting and the internal-analytics gate.

Both exist because V3.3 puts this API on a public URL: every expensive endpoint accepts
an unauthenticated POST body, and the analytics dashboard reads aggregate product data.

ponytail: fixed window, not a sliding window or token bucket. A client can burst up to
2x the limit across a window boundary. That is fine for abuse control on a demo
deployment; move to a sliding window (or an edge rate limiter) if the limit ever needs to
be exact. Counters live in Redis, which is already a dependency, so the limit holds
across workers instead of being per-process.
"""

# No `from __future__ import annotations` here on purpose: FastAPI resolves a callable
# class dependency's annotations against `__globals__`, which an instance does not have,
# so stringized annotations make it treat `request: Request` as a query parameter and
# every call 422s. Python is pinned to >=3.12, so `X | None` works without the import.
import hashlib
import hmac
import json
import os
import time

from fastapi import Depends, Header, HTTPException, Request, status

from api.deps import get_cache_service
from core.config import Settings, get_settings
from core.logging import get_logger
from services.cache import CacheService

logger = get_logger(__name__)


def client_identifier(request: Request) -> str:
    """Client identity for bucketing, hashed to a fixed length for the Redis key.

    The left-most X-Forwarded-For hop is whatever the client typed, so keying on it would
    give an attacker a fresh bucket per request. On Lambda, prefer the source IP the platform
    observed: Lambda Web Adapter forwards the function URL request context, which carries
    it, and AWS appends the real client to X-Forwarded-For. Anywhere else no proxy rewrites
    those headers, so a client could forge them, and only the socket address is used.
    """
    if not os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
        return _digest(request.client.host if request.client else "unknown")
    context = request.headers.get("x-amzn-request-context")
    if context:
        try:
            source_ip = json.loads(context)["http"]["sourceIp"]
        except (ValueError, KeyError, TypeError):
            source_ip = None
        if isinstance(source_ip, str) and source_ip:
            return _digest(source_ip)
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        last_hop = forwarded.split(",")[-1].strip()
        if last_hop:
            return _digest(last_hop)
    return _digest(request.client.host if request.client else "unknown")


def _digest(identity: str) -> str:
    return hashlib.sha256(identity.encode("utf-8")).hexdigest()[:16]


class RateLimit:
    """Dependency that allows `limit` requests per `window_seconds` per client."""

    def __init__(self, bucket: str, limit: int | None = None, window_seconds: int | None = None) -> None:
        self.bucket = bucket
        self.limit = limit
        self.window_seconds = window_seconds

    def __call__(
        self,
        request: Request,
        settings: Settings = Depends(get_settings),
        cache: CacheService = Depends(get_cache_service),
    ) -> None:
        if not settings.rate_limit_enabled:
            return

        limit = self.limit or settings.rate_limit_requests
        window = self.window_seconds or settings.rate_limit_window_seconds
        client = client_identifier(request)
        window_start = int(time.time()) // window
        key = cache.rate_limit_key(self.bucket, client, window_start)

        count = cache.incr_counter(key, window)
        if count is None:
            # No counter backend. Fail open on purpose: refusing all traffic because
            # Redis blinked is a worse outcome than briefly not enforcing a demo limit.
            # The cache layer already logged why it was unavailable.
            return

        if count > limit:
            retry_after = window - (int(time.time()) % window)
            logger.warning(
                "rate_limit_exceeded",
                extra={"bucket": self.bucket, "limit": limit, "window_seconds": window, "count": count},
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit of {limit} requests per {window} seconds exceeded.",
                headers={"Retry-After": str(retry_after)},
            )


def require_analytics_token(
    settings: Settings = Depends(get_settings),
    x_analytics_token: str | None = Header(default=None),
) -> None:
    """Gate the internal analytics summary.

    The dashboard reports aggregate product behaviour, so it is operator-facing rather
    than public. When no token is configured the endpoint stays open in development
    only - a deployed environment with no token configured is refused rather than
    silently served, so forgetting to set it fails closed.
    """
    configured = settings.analytics_api_token.strip()
    if not configured:
        if settings.app_env.lower() in {"development", "dev", "local", "test"}:
            return
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Analytics summary is disabled because ANALYTICS_API_TOKEN is not configured.",
        )

    # Constant-time comparison: a token check should not leak its prefix via timing.
    if not x_analytics_token or not hmac.compare_digest(x_analytics_token, configured):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="A valid X-Analytics-Token header is required.",
        )
