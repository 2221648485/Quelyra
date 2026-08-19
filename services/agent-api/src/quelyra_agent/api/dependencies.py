# 用途：集中提供请求范围内的 FastAPI 依赖装配。
import uuid
from collections.abc import AsyncIterator
from dataclasses import dataclass

import jwt
from fastapi import Depends, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession

from quelyra_agent.api.errors import ApiError
from quelyra_agent.core.security import decode_access_token
from quelyra_agent.db.models import User

@dataclass
class CurrentUser:
    model: User

    @property
    def id(self) -> uuid.UUID:
        return self.model.id


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    with request.app.state.session_factory() as session:
        return session


async def get_current_user(
    request: Request,
    session: AsyncSession = Depends(get_session),
    authorization: str | None = Header(default=None),
) -> CurrentUser:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise ApiError(401, "AUTHENTICATION_REQUIRED", "A bearer access token is required")
    token = authorization.split(" ", 1)[1]
    try:
        claims = decode_access_token(token, request.app.state.settings)
        if claims.get("type") != "access":
            raise ValueError("wrong token type")
        user_id = uuid.UUID(claims["sub"])
    except (jwt.PyJWTError, KeyError, ValueError) as exc:
        raise ApiError(401, "INVALID_ACCESS_TOKEN", "Access token is invalid or expired") from exc
    user = await session.get(User, user_id)
    if not user or not user.is_active:
        raise ApiError(401, "INVALID_ACCESS_TOKEN", "Access token is invalid or expired")
    return CurrentUser(user)
