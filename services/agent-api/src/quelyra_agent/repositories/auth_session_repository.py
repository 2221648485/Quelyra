from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from quelyra_agent.db.models import AuthSession, AuthSessionFamily


class AuthSessionRepository:
    def __init__(self, session: AsyncSession):
        """初始化当前组件所需的依赖和配置。"""
        self.session = session

    def add(self, auth_session: AuthSession) -> None:
        """将模型对象加入当前数据库事务。"""
        self.session.add(auth_session)

    def add_family(self, family: AuthSessionFamily) -> None:
        """将模型对象加入当前数据库事务。"""
        self.session.add(family)

    async def get_by_token_hash(self, value: str) -> AuthSession | None:
        """查询指定资源并返回结果。"""
        return await self.session.scalar(
            select(AuthSession).where(AuthSession.refresh_token_hash == value)
        )

    @staticmethod
    def token_for_update_statement(value: str):
        """构造或执行行级锁查询，保护并发更改。"""
        return (
            select(AuthSession)
            .where(AuthSession.refresh_token_hash == value)
            .with_for_update()
        )

    async def get_by_token_hash_for_update(self, value: str) -> AuthSession | None:
        """查询指定资源并返回结果。"""
        statement = self.token_for_update_statement(value).execution_options(populate_existing=True)
        return await self.session.scalar(statement)

    @staticmethod
    def family_for_update_statement(family_id: uuid.UUID):
        """构造或执行行级锁查询，保护并发更改。"""
        return (
            select(AuthSessionFamily)
            .where(AuthSessionFamily.id == family_id)
            .with_for_update()
        )

    async def lock_family(self, family_id: uuid.UUID) -> AuthSessionFamily | None:
        """构造或执行行级锁查询，保护并发更改。"""
        statement = self.family_for_update_statement(family_id).execution_options(
            populate_existing=True
        )
        return await self.session.scalar(statement)

    async def revoke_family(self, family_id: uuid.UUID) -> None:
        """说明当前函数的主要职责和返回边界。"""
        now = datetime.now(UTC)
        await self.session.execute(
            update(AuthSessionFamily)
            .where(AuthSessionFamily.id == family_id, AuthSessionFamily.revoked_at.is_(None))
            .values(revoked_at=now)
        )
        await self.session.execute(
            update(AuthSession)
            .where(AuthSession.family_id == family_id, AuthSession.revoked_at.is_(None))
            .values(revoked_at=now)
        )

    async def list_family_ids(self, user_id: uuid.UUID) -> list[uuid.UUID]:
        """校验权限后列出相关资源。"""
        return list(
            (
                await self.session.scalars(
                    select(AuthSessionFamily.id)
                    .where(AuthSessionFamily.user_id == user_id)
                    .order_by(AuthSessionFamily.id)
                )
            ).all()
        )

    async def revoke_all(self, user_id: uuid.UUID) -> None:
        """说明当前函数的主要职责和返回边界。"""
        for family_id in await self.list_family_ids(user_id):
            await self.lock_family(family_id)
            await self.revoke_family(family_id)
