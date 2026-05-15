from collections.abc import Generator
from functools import lru_cache

from sqlalchemy.orm import Session

from core.config import get_settings
from db.session import SessionLocal
from services.cache import CacheService


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@lru_cache
def get_cache_service() -> CacheService:
    return CacheService.from_settings(get_settings())
