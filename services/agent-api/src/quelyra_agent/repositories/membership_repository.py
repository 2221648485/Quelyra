from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from quelyra_agent.db.models import User, WorkspaceMember, WorkspaceRole


class MembershipRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def add(self, membership: WorkspaceMember) -> None:
        self.session.add(membership)

    async def get(self, workspace_id: uuid.UUID, user_id: uuid.UUID) -> WorkspaceMember | None:
        return await self.session.scalar(
            select(WorkspaceMember).where(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.user_id == user_id,
            )
        )

    async def list(self, workspace_id: uuid.UUID) -> list[tuple[WorkspaceMember, User]]:
        statement = (
            select(WorkspaceMember, User)
            .join(User, User.id == WorkspaceMember.user_id)
            .where(WorkspaceMember.workspace_id == workspace_id)
            .order_by(WorkspaceMember.created_at)
        )
        return list((await self.session.execute(statement)).all())

    async def owner_count(self, workspace_id: uuid.UUID) -> int:
        return int(
            await self.session.scalar(
                select(func.count()).select_from(WorkspaceMember).where(
                    WorkspaceMember.workspace_id == workspace_id,
                    WorkspaceMember.role == WorkspaceRole.owner,
                )
            )
            or 0
        )

    async def delete(self, membership: WorkspaceMember) -> None:
        await self.session.delete(membership)
