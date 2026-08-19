from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from quelyra_agent.db.models import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_email(self, email: str) -> User | None:
        return await self.session.scalar(select(User).where(User.email == email))

    async def get(self, user_id: uuid.UUID) -> User | None:
        return await self.session.get(User, user_id)

    def add(self, user: User) -> None:
        self.session.add(user)
