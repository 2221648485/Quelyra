# 用途：编排工作区创建、成员管理和邀请用例。
from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from quelyra_agent.api.errors import ApiError
from quelyra_agent.db.models import User, Workspace, WorkspaceMember, WorkspaceRole
from quelyra_agent.repositories.membership_repository import MembershipRepository
from quelyra_agent.repositories.workspace_repository import WorkspaceRepository


class WorkspaceService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.workspaces = WorkspaceRepository(session)
        self.memberships = MembershipRepository(session)

    async def create(self, user_id: uuid.UUID, name: str) -> dict:
        workspace = Workspace(name=name.strip())
        self.workspaces.add(workspace)
        await self.session.flush()
        member = WorkspaceMember(workspace_id=workspace.id, user_id=user_id, role=WorkspaceRole.owner)
        self.memberships.add(member)
        await self.session.commit()
        return self._workspace_data(workspace, member)

    async def list(self, user_id: uuid.UUID) -> list[dict]:
        rows = await self.workspaces.list_for_user(user_id)
        return [self._workspace_data(workspace, member) for workspace, member in rows]

    async def require_membership(
        self, workspace_id: uuid.UUID, user_id: uuid.UUID, roles: set[WorkspaceRole] | None = None
    ) -> WorkspaceMember:
        membership = await self.memberships.get(workspace_id, user_id)
        if not membership:
            raise ApiError(403, "WORKSPACE_ACCESS_DENIED", "You do not have access to this workspace")
        if roles and membership.role not in roles:
            raise ApiError(403, "INSUFFICIENT_WORKSPACE_ROLE", "Your workspace role cannot perform this action")
        return membership

    async def list_members(self, workspace_id: uuid.UUID, user_id: uuid.UUID) -> list[dict]:
        await self.require_membership(workspace_id, user_id)
        return [self._member_data(member, user) for member, user in await self.memberships.list(workspace_id)]

    async def update_role(
        self, workspace_id: uuid.UUID, actor_id: uuid.UUID, member_id: uuid.UUID, role: WorkspaceRole
    ) -> dict:
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
        return {"id": str(workspace.id), "name": workspace.name, "role": member.role.value}

    @staticmethod
    def _member_data(member: WorkspaceMember, user: User) -> dict:
        return {
            "user_id": str(member.user_id), "email": user.email, "name": user.name,
            "role": member.role.value, "joined_at": member.created_at.isoformat(),
        }
