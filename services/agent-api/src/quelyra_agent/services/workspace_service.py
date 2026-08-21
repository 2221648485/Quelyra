"""工作区与成员管理的应用服务骨架。"""

from typing import Any


class WorkspaceService:
    def __init__(self, session: Any):
        """TODO：创建各仓储并保存数据库事务。"""
        raise NotImplementedError("待实现：初始化工作区服务")

    async def create(self, user_id: Any, name: str) -> dict:
        """TODO：创建工作区并把创建者作为 owner。"""
        raise NotImplementedError("待实现：创建工作区")

    async def list(self, user_id: Any) -> list[dict]:
        """TODO：列出该用户的工作区及角色。"""
        raise NotImplementedError("待实现：列出工作区")

    async def require_membership(self, workspace_id: Any, user_id: Any, allowed_roles: set[str] | None = None) -> Any:
        """TODO：读取成员关系并验证所需角色；失败时不泄露其他工作区信息。"""
        raise NotImplementedError("待实现：校验工作区成员")

    async def list_members(self, workspace_id: Any, user_id: Any) -> list[dict]:
        """TODO：成员可查看公开成员列表。"""
        raise NotImplementedError("待实现：列出工作区成员")

    async def update_role(self, workspace_id: Any, actor_id: Any, target_user_id: Any, role: str) -> dict:
        """TODO：锁定工作区并验证 owner/admin 权限、角色合法性及最后 owner 保护。"""
        raise NotImplementedError("待实现：更新成员角色")

    async def remove_member(self, workspace_id: Any, actor_id: Any, target_user_id: Any) -> None:
        """TODO：验证管理权限并保护最后一个 owner。"""
        raise NotImplementedError("待实现：移除工作区成员")

    @staticmethod
    def _workspace_data(workspace: Any, member: Any) -> dict:
        """TODO：构造安全的工作区响应。"""
        raise NotImplementedError("待实现：序列化工作区")

    @staticmethod
    def _member_data(member: Any, user: Any) -> dict:
        """TODO：构造不含认证字段的成员响应。"""
        raise NotImplementedError("待实现：序列化成员")
