from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from quelyra_agent.api.errors import ApiError
from quelyra_agent.db.models import User, Workspace, WorkspaceMember, WorkspaceRole
from quelyra_agent.repositories.membership_repository import MembershipRepository
from quelyra_agent.repositories.workspace_repository import WorkspaceRepository


class WorkspaceService:
    def __init__(self, session: AsyncSession):
        """初始化当前组件所需的依赖和配置。"""
        self.session = session
        self.workspaces = WorkspaceRepository(session)
        self.memberships = MembershipRepository(session)

    async def create(self, user_id: uuid.UUID, name: str) -> dict:
        """校验权限后创建资源并返回响应数据。"""
        workspace = Workspace(name=name.strip())
        self.workspaces.add(workspace)
        await self.session.flush()
        member = WorkspaceMember(workspace_id=workspace.id, user_id=user_id, role=WorkspaceRole.owner)
        self.memberships.add(member)
        await self.session.commit()
        return self._workspace_data(workspace, member)

    async def list(self, user_id: uuid.UUID) -> list[dict]:
        """校验权限后列出相关资源。"""
        rows = await self.workspaces.list_for_user(user_id)
        return [self._workspace_data(workspace, member) for workspace, member in rows]

    async def require_membership(
        self, workspace_id: uuid.UUID, user_id: uuid.UUID, roles: set[WorkspaceRole] | None = None
    ) -> WorkspaceMember:
        """说明当前函数的主要职责和返回边界。"""
        membership = await self.memberships.get(workspace_id, user_id)
        if not membership:
            raise ApiError(403, "WORKSPACE_ACCESS_DENIED", "You do not have access to this workspace")
        if roles and membership.role not in roles:
            raise ApiError(403, "INSUFFICIENT_WORKSPACE_ROLE", "Your workspace role cannot perform this action")
        return membership

    async def list_members(self, workspace_id: uuid.UUID, user_id: uuid.UUID) -> list[dict]:
        """校验权限后列出相关资源。"""
        await self.require_membership(workspace_id, user_id)
        return [self._member_data(member, user) for member, user in await self.memberships.list(workspace_id)]

    async def update_role(
        self, workspace_id: uuid.UUID, actor_id: uuid.UUID, member_id: uuid.UUID, role: WorkspaceRole
    ) -> dict:
        """校验权限后更新目标资源。"""
        await self.workspaces.lock_for_update(workspace_id)
        await self.require_membership(workspace_id, actor_id, {WorkspaceRole.owner, WorkspaceRole.admin})
        target = await self.memberships.get(workspace_id, member_id)
        if not target:
            raise ApiError(404, "MEMBER_NOT_FOUND", "Workspace member was not found")
        if target.role == WorkspaceRole.owner and role != WorkspaceRole.owner:
            if await self.memberships.owner_count(workspace_id) == 1:
                raise ApiError(409, "LAST_OWNER_REQUIRED", "A workspace must retain at least one owner")
        target.role = role
        await self.session.commit()
        user = await self.session.get(User, member_id)
        return self._member_data(target, user)

    async def remove_member(
        self, workspace_id: uuid.UUID, actor_id: uuid.UUID, member_id: uuid.UUID
    ) -> None:
        """校验权限后删除或移除目标资源。"""
        await self.workspaces.lock_for_update(workspace_id)
        await self.require_membership(workspace_id, actor_id, {WorkspaceRole.owner, WorkspaceRole.admin})
        target = await self.memberships.get(workspace_id, member_id)
        if not target:
            raise ApiError(404, "MEMBER_NOT_FOUND", "Workspace member was not found")
        if target.role == WorkspaceRole.owner and await self.memberships.owner_count(workspace_id) == 1:
            raise ApiError(409, "LAST_OWNER_REQUIRED", "A workspace must retain at least one owner")
        await self.memberships.delete(target)
        await self.session.commit()

    @staticmethod
    def _workspace_data(workspace: Workspace, member: WorkspaceMember) -> dict:
        """将数据模型转换为接口响应字典。"""
        return {"id": str(workspace.id), "name": workspace.name, "role": member.role.value}

    @staticmethod
    def _member_data(member: WorkspaceMember, user: User) -> dict:
        """将数据模型转换为接口响应字典。"""
        return {
            "user_id": str(member.user_id), "email": user.email, "name": user.name,
            "role": member.role.value, "joined_at": member.created_at.isoformat(),
        }
