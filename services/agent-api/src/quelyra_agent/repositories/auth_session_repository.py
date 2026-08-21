"""Refresh Token 会话族的持久化骨架。"""

from typing import Any


class AuthSessionRepository:
    def __init__(self, session: Any):
        """TODO：保存异步数据库会话。"""
        raise NotImplementedError("待实现：初始化认证会话仓储")

    def add(self, auth_session: Any) -> None:
        """TODO：将新会话加入当前事务。"""
        raise NotImplementedError("待实现：新增认证会话")

    def add_family(self, family: Any) -> None:
        """TODO：创建可整体撤销的会话族。"""
        raise NotImplementedError("待实现：新增会话族")

    async def get_by_token_hash(self, value: str) -> Any | None:
        """TODO：按哈希读取令牌，绝不查询或存储明文 refresh token。"""
        raise NotImplementedError("待实现：查询令牌")

    @staticmethod
    def token_for_update_statement(value: str) -> Any:
        """TODO：构造 token 行锁语句，解决刷新令牌并发复用。"""
        raise NotImplementedError("待实现：构造令牌锁")

    async def get_by_token_hash_for_update(self, value: str) -> Any | None:
        """TODO：在短事务内锁定令牌会话。"""
        raise NotImplementedError("待实现：锁定令牌")

    @staticmethod
    def family_for_update_statement(family_id: Any) -> Any:
        """TODO：构造会话族行锁语句。"""
        raise NotImplementedError("待实现：构造会话族锁")

    async def lock_family(self, family_id: Any) -> Any | None:
        """TODO：锁定会话族后再撤销。"""
        raise NotImplementedError("待实现：锁定会话族")

    async def revoke_family(self, family_id: Any) -> None:
        """TODO：原子撤销会话族及其全部令牌。"""
        raise NotImplementedError("待实现：撤销会话族")

    async def list_family_ids(self, user_id: Any) -> list[Any]:
        """TODO：读取用户的会话族 ID。"""
        raise NotImplementedError("待实现：列出会话族")

    async def revoke_all(self, user_id: Any) -> None:
        """TODO：逐个锁定并撤销该用户全部会话族。"""
        raise NotImplementedError("待实现：撤销全部会话")
