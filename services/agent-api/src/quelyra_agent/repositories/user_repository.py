from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from quelyra_agent.db.models import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        """初始化当前组件所需的依赖和配置。"""
        self.session = session

    async def get_by_email(self, email: str) -> User | None:
        """查询指定资源并返回结果。"""
        return await self.session.scalar(select(User).where(User.email == email))

    async def get(self, user_id: uuid.UUID) -> User | None:
        """查询指定资源并返回结果。"""
        return await self.session.get(User, user_id)

    def add(self, user: User) -> None:
        """将模型对象加入当前数据库事务。"""
        self.session.add(user)
