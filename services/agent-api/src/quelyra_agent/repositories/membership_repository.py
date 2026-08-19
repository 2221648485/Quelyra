from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from quelyra_agent.db.models import User, WorkspaceMember, WorkspaceRole


class MembershipRepository:
    def __init__(self, session: AsyncSession):
        """初始化当前组件所需的依赖和配置。"""
        self.session = session

    def add(self, membership: WorkspaceMember) -> None:
        """将模型对象加入当前数据库事务。"""
        self.session.add(membership)

    async def get(self, workspace_id: uuid.UUID, user_id: uuid.UUID) -> WorkspaceMember | None:
        """查询指定资源并返回结果。"""
        return await self.session.scalar(
            select(WorkspaceMember).where(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.user_id == user_id,
            )
        )

    async def list(self, workspace_id: uuid.UUID) -> list[tuple[WorkspaceMember, User]]:
        """校验权限后列出相关资源。"""
        statement = (
            select(WorkspaceMember, User)
            .join(User, User.id == WorkspaceMember.user_id)
            .where(WorkspaceMember.workspace_id == workspace_id)
            .order_by(WorkspaceMember.created_at)
        )
        return list((await self.session.execute(statement)).all())

    async def owner_count(self, workspace_id: uuid.UUID) -> int:
        """说明当前函数的主要职责和返回边界。"""
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
        """校验权限后删除或移除目标资源。"""
        await self.session.delete(membership)
