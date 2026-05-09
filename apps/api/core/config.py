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
    cors_origins: list[str] = Field(default_factory=list)

    model_config = SettingsConfigDict(env_file=(".env", "../../.env"), env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
