from __future__ import annotations

import hashlib
import json
from typing import Any, Protocol, TypeVar

from pydantic import BaseModel

from core.config import Settings
from core.logging import get_logger

try:
    from redis import Redis
    from redis.exceptions import RedisError
except ImportError:  # pragma: no cover - exercised only when dependencies are not installed.
    Redis = None  # type: ignore[assignment]

    class RedisError(Exception):
        pass


logger = get_logger(__name__)
ModelT = TypeVar("ModelT", bound=BaseModel)


class CacheBackend(Protocol):
    def get(self, key: str) -> str | None:
        ...

    def set(self, key: str, value: str, ttl_seconds: int) -> None:
        ...

    def delete(self, key: str) -> int:
        ...

    def delete_prefix(self, prefix: str) -> int:
        ...


class NullCacheBackend:
    def get(self, key: str) -> str | None:
        return None

    def set(self, key: str, value: str, ttl_seconds: int) -> None:
        return None

    def delete(self, key: str) -> int:
        return 0

    def delete_prefix(self, prefix: str) -> int:
        return 0


class RedisCacheBackend:
    def __init__(self, redis_url: str) -> None:
        if Redis is None:
            raise RuntimeError("redis package is not installed")
        self.client: Redis = Redis.from_url(
            redis_url,
            decode_responses=True,
            socket_connect_timeout=0.2,
            socket_timeout=0.2,
        )
        self.available = True

    def get(self, key: str) -> str | None:
        try:
            value = self.client.get(key)
            self.available = True
            return str(value) if value is not None else None
        except (OSError, RedisError) as exc:
            self._mark_unavailable("cache_redis_unavailable", key, exc)
            return None

    def set(self, key: str, value: str, ttl_seconds: int) -> None:
        try:
            self.client.setex(key, ttl_seconds, value)
            self.available = True
        except (OSError, RedisError) as exc:
            self._mark_unavailable("cache_write_failure", key, exc)

    def delete(self, key: str) -> int:
        try:
            deleted = self.client.delete(key)
            self.available = True
            return int(deleted)
        except (OSError, RedisError) as exc:
            self._mark_unavailable("cache_invalidation_failure", key, exc)
            return 0

    def delete_prefix(self, prefix: str) -> int:
        deleted = 0
        try:
            for key in self.client.scan_iter(match=f"{prefix}*"):
                deleted += int(self.client.delete(key))
            self.available = True
        except (OSError, RedisError) as exc:
            self._mark_unavailable("cache_invalidation_failure", prefix, exc)
        return deleted

    def _mark_unavailable(self, message: str, key: str, exc: Exception) -> None:
        if self.available or message != "cache_redis_unavailable":
            logger.warning(
                message,
                extra={"cache_key": key, "fallback": "database", "error": str(exc)},
            )
        self.available = False


class CacheService:
    def __init__(
        self,
        backend: CacheBackend,
        key_version: str,
        search_ttl_seconds: int,
        profile_ttl_seconds: int,
        ranking_ttl_seconds: int,
    ) -> None:
        self.backend = backend
        self.key_version = key_version
        self.search_ttl_seconds = search_ttl_seconds
        self.profile_ttl_seconds = profile_ttl_seconds
        self.ranking_ttl_seconds = ranking_ttl_seconds
        self.namespace = "college-exploration:cache"

    @classmethod
    def from_settings(cls, settings: Settings) -> "CacheService":
        backend: CacheBackend
        if settings.redis_enabled:
            try:
                backend = RedisCacheBackend(settings.redis_url)
            except (RuntimeError, ValueError) as exc:
                logger.warning(
                    "cache_redis_unavailable",
                    extra={"fallback": "database", "error": str(exc)},
                )
                backend = NullCacheBackend()
        else:
            backend = NullCacheBackend()
            logger.info("cache_disabled", extra={"fallback": "database"})

        return cls(
            backend=backend,
            key_version=settings.cache_key_version,
            search_ttl_seconds=settings.cache_search_ttl_seconds,
            profile_ttl_seconds=settings.cache_profile_ttl_seconds,
            ranking_ttl_seconds=settings.cache_ranking_ttl_seconds,
        )

    def make_key(self, resource: str, payload: dict[str, Any], version: str | None = None) -> str:
        key_payload = {"resource": resource, "version": version, "params": payload}
        digest = hashlib.sha256(self._canonical_json(key_payload).encode("utf-8")).hexdigest()[:24]
        return f"{self.namespace}:{self.key_version}:{resource}:{digest}"

    def search_key(self, filters: BaseModel) -> str:
        return self.make_key("search", filters.model_dump(mode="json"))

    def profile_key(self, school_id: int) -> str:
        return self.make_key("school-profile", {"school_id": school_id})

    def ranking_key(self, request: BaseModel, ranking_version: str) -> str:
        return self.make_key("ranking", request.model_dump(mode="json"), version=ranking_version)

    def get_model(self, key: str, model_type: type[ModelT]) -> ModelT | None:
        raw = self.backend.get(key)
        if raw is None:
            logger.info("cache_miss", extra={"cache_key": key, "db_call_required": True})
            return None
        try:
            value = model_type.model_validate_json(raw)
        except ValueError as exc:
            logger.warning("cache_deserialize_failure", extra={"cache_key": key, "error": str(exc)})
            return None
        logger.info("cache_hit", extra={"cache_key": key, "db_call_avoided": True})
        return value

    def set_model(self, key: str, value: BaseModel, ttl_seconds: int) -> None:
        self.backend.set(key, value.model_dump_json(), ttl_seconds)

    def invalidate_key(self, key: str) -> int:
        return self.backend.delete(key)

    def invalidate_resource(self, resource: str) -> int:
        return self.backend.delete_prefix(f"{self.namespace}:{self.key_version}:{resource}:")

    def _canonical_json(self, payload: dict[str, Any]) -> str:
        return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
