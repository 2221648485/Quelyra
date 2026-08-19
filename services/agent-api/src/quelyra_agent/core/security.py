# 用途：提供应用层身份认证、授权和安全基础能力。
from __future__ import annotations

import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import jwt
from pwdlib import PasswordHash

from quelyra_agent.core.config import Settings

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, encoded: str) -> bool:
    return password_hash.verify(password, encoded)


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def create_access_token(user_id: str, settings: Settings) -> tuple[str, int]:
    ttl = settings.access_token_ttl_minutes * 60
    now = datetime.now(UTC)
    payload = {
        "sub": user_id,
        "type": "access",
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
        "iat": now,
        "exp": now + timedelta(seconds=ttl),
        "jti": str(uuid4()),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256"), ttl


def decode_access_token(token: str, settings: Settings) -> dict:
    return jwt.decode(
        token,
        settings.jwt_secret,
        algorithms=["HS256"],
        audience=settings.jwt_audience,
        issuer=settings.jwt_issuer,
    )


def create_service_token(
    settings: Settings,
    *,
    actor_id: str,
    workspace_id: str,
    datasource_id: str,
) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": "agent-api",
        "type": "service",
        "iss": settings.jwt_issuer,
        "aud": settings.service_jwt_audience,
        "iat": now,
        "exp": now + timedelta(minutes=5),
        "jti": str(uuid4()),
        "actor_id": actor_id,
        "workspace_id": workspace_id,
        "datasource_id": datasource_id,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def create_refresh_token() -> str:
    return secrets.token_urlsafe(48)
