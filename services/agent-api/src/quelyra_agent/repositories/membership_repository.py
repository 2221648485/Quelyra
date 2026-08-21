"""工作区成员关系仓储骨架。"""

from typing import Any


class MembershipRepository:
    def __init__(self, session: Any):
        """TODO：保存异步数据库会话。"""
        raise NotImplementedError("待实现：初始化成员仓储")

    def add(self, membership: Any) -> None:
        """TODO：加入成员关系到当前事务。"""
        raise NotImplementedError("待实现：新增成员")

    async def get(self, workspace_id: Any, user_id: Any) -> Any | None:
        """TODO：按工作区和用户获取成员关系。"""
        raise NotImplementedError("待实现：获取成员")

    async def list(self, workspace_id: Any) -> list[Any]:
        """TODO：列出成员及必要的公开用户信息。"""
        raise NotImplementedError("待实现：列出成员")

    async def owner_count(self, workspace_id: Any) -> int:
        """TODO：角色变更前统计 owner，防止移除最后一个 owner。"""
        raise NotImplementedError("待实现：统计 owner")

    async def delete(self, membership: Any) -> None:
        """TODO：删除已鉴权的成员关系。"""
        raise NotImplementedError("待实现：删除成员")
