from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from quelyra_agent.db.models import Workspace, WorkspaceMember


class WorkspaceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def add(self, workspace: Workspace) -> None:
        self.session.add(workspace)

    @staticmethod
    def workspace_for_update_statement(workspace_id: uuid.UUID):
        return select(Workspace).where(Workspace.id == workspace_id).with_for_update()

    async def lock_for_update(self, workspace_id: uuid.UUID) -> Workspace | None:
        return await self.session.scalar(self.workspace_for_update_statement(workspace_id))

    async def get_for_user(self, workspace_id: uuid.UUID, user_id: uuid.UUID) -> Workspace | None:
        statement = (
            select(Workspace)
            .join(WorkspaceMember, WorkspaceMember.workspace_id == Workspace.id)
            .where(Workspace.id == workspace_id, WorkspaceMember.user_id == user_id)
        )
        return await self.session.scalar(statement)

    async def list_for_user(self, user_id: uuid.UUID) -> list[tuple[Workspace, WorkspaceMember]]:
        statement = (
            select(Workspace, WorkspaceMember)
            .join(WorkspaceMember, WorkspaceMember.workspace_id == Workspace.id)
            .where(WorkspaceMember.user_id == user_id)
            .order_by(Workspace.created_at)
        )
        return list((await self.session.execute(statement)).all())
