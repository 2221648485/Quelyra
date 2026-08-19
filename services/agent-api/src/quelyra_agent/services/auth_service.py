# 用途：编排注册、登录、令牌刷新和会话撤销用例。
from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from quelyra_agent.api.errors import ApiError
from quelyra_agent.core.config import Settings
from quelyra_agent.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    token_hash,
    verify_password,
)
from quelyra_agent.db.models import (
    AuthSession,
    AuthSessionFamily,
    User,
    Workspace,
    WorkspaceMember,
    WorkspaceRole,
)
from quelyra_agent.repositories.auth_session_repository import AuthSessionRepository
from quelyra_agent.repositories.user_repository import UserRepository
from quelyra_agent.repositories.workspace_repository import WorkspaceRepository


def user_data(user: User) -> dict:
    return {"id": str(user.id), "email": user.email, "name": user.name}


def workspace_data(workspace: Workspace, membership: WorkspaceMember) -> dict:
    return {"id": str(workspace.id), "name": workspace.name, "role": membership.role.value}


class AuthService:
    def __init__(self, session: AsyncSession, settings: Settings):
        self.session = session
        self.settings = settings
        self.users = UserRepository(session)
        self.sessions = AuthSessionRepository(session)
        self.workspaces = WorkspaceRepository(session)

    async def register(self, email: str, password: str, name: str) -> dict:
        email = email.strip().lower()
        if await self.users.get_by_email(email):
            raise ApiError(409, "EMAIL_ALREADY_EXISTS", "An account with this email already exists")
        try:
            user = User(email=email, name=name.strip(), password_hash=hash_password(password))
            workspace = Workspace(name=f"{name.strip()}'s Workspace")
            self.session.add_all([user, workspace])
            await self.session.flush()
            membership = WorkspaceMember(
                workspace_id=workspace.id, user_id=user.id, role=WorkspaceRole.owner
            )
            self.session.add(membership)
            await self.session.commit()
        except IntegrityError as exc:
            await self.session.rollback()
            raise ApiError(409, "EMAIL_ALREADY_EXISTS", "An account with this email already exists") from exc
        except Exception:
            await self.session.rollback()
            raise
        return {"user": user_data(user), "workspaces": [workspace_data(workspace, membership)]}

    async def login(self, email: str, password: str) -> dict:
        user = await self.users.get_by_email(email.strip().lower())
        if not user or not user.is_active or not verify_password(password, user.password_hash):
            raise ApiError(401, "INVALID_CREDENTIALS", "Email or password is incorrect")
        return await self._issue_tokens(user)

    async def _issue_tokens(self, user: User, family_id: uuid.UUID | None = None) -> dict:
        access_token, expires_in = create_access_token(str(user.id), self.settings)
        refresh_token = create_refresh_token()
        if family_id is None:
            family = AuthSessionFamily(user_id=user.id)
            self.sessions.add_family(family)
            await self.session.flush()
            family_id = family.id
        auth_session = AuthSession(
            user_id=user.id,
            family_id=family_id,
            refresh_token_hash=token_hash(refresh_token),
            expires_at=datetime.now(UTC) + timedelta(days=self.settings.refresh_token_ttl_days),
        )
        self.sessions.add(auth_session)
        workspaces = await self.workspaces.list_for_user(user.id)
        await self.session.commit()
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": expires_in,
            "user": user_data(user),
            "workspaces": [workspace_data(workspace, member) for workspace, member in workspaces],
        }

    async def refresh(self, refresh_token: str) -> dict:
        value_hash = token_hash(refresh_token)
        initial_record = await self.sessions.get_by_token_hash(value_hash)
        now = datetime.now(UTC)
        if not initial_record:
            raise ApiError(401, "INVALID_REFRESH_TOKEN", "Refresh token is invalid")
        family = await self.sessions.lock_family(initial_record.family_id)
        if not family:
            await self.session.rollback()
            raise ApiError(401, "INVALID_REFRESH_TOKEN", "Refresh token is invalid")
        if family.revoked_at is not None:
            await self.session.rollback()
            raise ApiError(401, "SESSION_REVOKED", "Authentication session has been revoked")
        record = await self.sessions.get_by_token_hash_for_update(value_hash)
        if not record:
            await self.session.rollback()
            raise ApiError(401, "INVALID_REFRESH_TOKEN", "Refresh token is invalid")
        if record.rotated_at is not None:
            await self.sessions.revoke_family(record.family_id)
            await self.session.commit()
            raise ApiError(401, "REFRESH_TOKEN_REUSED", "Refresh token reuse was detected")
        if record.revoked_at is not None:
            await self.session.rollback()
            raise ApiError(401, "SESSION_REVOKED", "Authentication session has been revoked")
        expires_at = record.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=UTC)
        if expires_at <= now:
            await self.session.rollback()
            raise ApiError(401, "REFRESH_TOKEN_EXPIRED", "Refresh token has expired")
        record.rotated_at = now
        user = await self.users.get(record.user_id)
        if not user or not user.is_active:
            raise ApiError(401, "SESSION_REVOKED", "Authentication session has been revoked")
        return await self._issue_tokens(user, record.family_id)

    async def logout(self, refresh_token: str) -> None:
        record = await self.sessions.get_by_token_hash(token_hash(refresh_token))
        if record:
            family = await self.sessions.lock_family(record.family_id)
            if not family:
                await self.session.rollback()
                return
            await self.sessions.revoke_family(record.family_id)
            await self.session.commit()

    async def logout_all(self, user_id: uuid.UUID) -> None:
        await self.sessions.revoke_all(user_id)
        await self.session.commit()
