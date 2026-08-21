"""用户仓储骨架。"""

from typing import Any


class UserRepository:
    def __init__(self, session: Any):
        """TODO：保存异步数据库会话。"""
        raise NotImplementedError("待实现：初始化用户仓储")

    async def get_by_email(self, email: str) -> Any | None:
        """TODO：按已规范化邮箱查询用户。"""
        raise NotImplementedError("待实现：按邮箱查询用户")

    async def get(self, user_id: Any) -> Any | None:
        """TODO：按主键查询用户。"""
        raise NotImplementedError("待实现：获取用户")

    def add(self, user: Any) -> None:
        """TODO：将新用户加入当前事务。"""
        raise NotImplementedError("待实现：新增用户")
