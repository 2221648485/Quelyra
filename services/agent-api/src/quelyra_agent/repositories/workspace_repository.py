from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from quelyra_agent.db.models import Workspace, WorkspaceMember


class WorkspaceRepository:
    def __init__(self, session: AsyncSession):
        """初始化当前组件所需的依赖和配置。"""
        self.session = session

    def add(self, workspace: Workspace) -> None:
        """将模型对象加入当前数据库事务。"""
        self.session.add(workspace)

    @staticmethod
    def workspace_for_update_statement(workspace_id: uuid.UUID):
        """构造或执行行级锁查询，保护并发更改。"""
        return select(Workspace).where(Workspace.id == workspace_id).with_for_update()

    async def lock_for_update(self, workspace_id: uuid.UUID) -> Workspace | None:
        """构造或执行行级锁查询，保护并发更改。"""
        return await self.session.scalar(self.workspace_for_update_statement(workspace_id))

    async def get_for_user(self, workspace_id: uuid.UUID, user_id: uuid.UUID) -> Workspace | None:
        """查询指定资源并返回结果。"""
        statement = (
            select(Workspace)
            .join(WorkspaceMember, WorkspaceMember.workspace_id == Workspace.id)
            .where(Workspace.id == workspace_id, WorkspaceMember.user_id == user_id)
        )
        return await self.session.scalar(statement)

    async def list_for_user(self, user_id: uuid.UUID) -> list[tuple[Workspace, WorkspaceMember]]:
        """校验权限后列出相关资源。"""
        statement = (
            select(Workspace, WorkspaceMember)
            .join(WorkspaceMember, WorkspaceMember.workspace_id == Workspace.id)
            .where(WorkspaceMember.user_id == user_id)
            .order_by(Workspace.created_at)
        )
        return list((await self.session.execute(statement)).all())
