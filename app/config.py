from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="INV_", env_file=".env", extra="ignore")

    APP_VERSION: str = "1.0.0"
    ENV: str = "development"
    DATABASE_URL: str = Field(..., example="postgresql+asyncpg://postgres:postgres@localhost:5432/fb_inventory")
    HTTP_TIMEOUT: float = 5.0


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]


settings = get_settings()
