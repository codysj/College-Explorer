from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "College Exploration API"
    app_env: str = Field(default="development", validation_alias="APP_ENV")
    app_version: str = "0.3.0"
    debug: bool = False
    database_url: str = Field(
        default="postgresql+psycopg://college:college@localhost:5432/college_exploration",
        validation_alias="DATABASE_URL",
    )
    redis_url: str = Field(default="redis://localhost:6379/0", validation_alias="REDIS_URL")
    redis_enabled: bool = Field(default=True, validation_alias="REDIS_ENABLED")
    cache_key_version: str = Field(default="v1", validation_alias="CACHE_KEY_VERSION")
    cache_search_ttl_seconds: int = Field(default=300, validation_alias="CACHE_SEARCH_TTL_SECONDS")
    cache_profile_ttl_seconds: int = Field(default=3600, validation_alias="CACHE_PROFILE_TTL_SECONDS")
    cache_ranking_ttl_seconds: int = Field(default=300, validation_alias="CACHE_RANKING_TTL_SECONDS")
    cors_origins: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000",
        validation_alias="CORS_ORIGINS",
    )

    model_config = SettingsConfigDict(env_file=(".env", "../../.env"), env_file_encoding="utf-8", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
