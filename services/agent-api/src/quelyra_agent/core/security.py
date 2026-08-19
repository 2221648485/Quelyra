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
    """使用推荐算法生成密码哈希。"""
    return password_hash.hash(password)


def verify_password(password: str, encoded: str) -> bool:
    """校验明文密码是否匹配已保存的哈希。"""
    return password_hash.verify(password, encoded)


def token_hash(token: str) -> str:
    """生成令牌哈希，用于安全存储和查询。"""
    return hashlib.sha256(token.encode()).hexdigest()


def create_access_token(user_id: str, settings: Settings) -> tuple[str, int]:
    """为指定用户签发短期访问令牌并返回有效期。"""
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
    """校验并解码访问令牌声明。"""
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
    """为服务间调用签发包含租户上下文的短期令牌。"""
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
    """生成高熵刷新令牌。"""
    return secrets.token_urlsafe(48)
