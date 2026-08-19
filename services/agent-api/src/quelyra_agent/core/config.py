# 用途：加载并校验以 QUELYRA_ 开头的 Python 服务运行配置。
from __future__ import annotations

import json
from functools import lru_cache
from typing import Annotated

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    environment: str
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/quelyra"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret: str
    jwt_issuer: str = "quelyra-agent-api"
    jwt_audience: str = "quelyra-web"
    service_jwt_audience: str = "quelyra-services"
    access_token_ttl_minutes: int = 15
    refresh_token_ttl_days: int = 30
    credential_encryption_key: str
    cors_origins: Annotated[list[str], NoDecode] = ["http://localhost:3000"]
    model_provider: str = "openai"
    gateway_base_url: str = "http://query-gateway:8080"
    gateway_timeout_seconds: float = 15.0
    gateway_max_response_bytes: int = 2_000_000
    query_timeout_ms: int = 15_000
    model_base_url: str = "https://api.openai.com/v1"
    model_api_key: str | None = None
    model_name: str = "gpt-4.1-mini"
    model_timeout_seconds: float = 30.0
    max_result_rows: int = 500
    max_result_bytes: int = 1_000_000

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value):
        if isinstance(value, str):
            if value.lstrip().startswith("["):
                return json.loads(value)
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @model_validator(mode="after")
    def validate_secrets(self) -> "Settings":
        if self.environment.lower() not in {"development", "dev", "test"}:
            weak = (
                len(self.jwt_secret) < 32
                or "development" in self.jwt_secret.lower()
                or len(self.credential_encryption_key) < 32
                or "development" in self.credential_encryption_key.lower()
            )
            if weak:
                raise ValueError("production secrets must be at least 32 characters and non-default")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
