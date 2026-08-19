from __future__ import annotations

from pydantic import BaseModel, Field


class DataSourceCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    engine: str = "mysql"
    host: str = Field(min_length=1, max_length=255)
    port: int = Field(default=3306, ge=1, le=65535)
    database_name: str = Field(min_length=1, max_length=255)
    username: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=1, max_length=4096)


class CredentialUpdateRequest(BaseModel):
    username: str | None = Field(default=None, min_length=1, max_length=255)
    password: str = Field(min_length=1, max_length=4096)
