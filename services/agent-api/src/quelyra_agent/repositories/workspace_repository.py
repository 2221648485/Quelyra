"""工作区仓储骨架。"""

from typing import Any


class WorkspaceRepository:
    def __init__(self, session: Any):
        """TODO：保存异步数据库会话。"""
        raise NotImplementedError("待实现：初始化工作区仓储")

    def add(self, workspace: Any) -> None:
        """TODO：将新工作区加入当前事务。"""
        raise NotImplementedError("待实现：新增工作区")

    @staticmethod
    def workspace_for_update_statement(workspace_id: Any) -> Any:
        """TODO：构造工作区行锁语句。"""
        raise NotImplementedError("待实现：构造工作区锁")

    async def lock_for_update(self, workspace_id: Any) -> Any | None:
        """TODO：更新成员角色前锁定工作区。"""
        raise NotImplementedError("待实现：锁定工作区")

    async def get_for_user(self, workspace_id: Any, user_id: Any) -> Any | None:
        """TODO：只返回该用户可见的工作区。"""
        raise NotImplementedError("待实现：获取用户工作区")

    async def list_for_user(self, user_id: Any) -> list[Any]:
        """TODO：按创建时间列出用户工作区和成员角色。"""
        raise NotImplementedError("待实现：列出用户工作区")
