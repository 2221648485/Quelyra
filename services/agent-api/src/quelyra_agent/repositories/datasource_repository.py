"""工作区隔离的数据源仓储骨架。"""

from typing import Any


class DataSourceRepository:
    def __init__(self, session: Any):
        """TODO：保存异步数据库会话。"""
        raise NotImplementedError("待实现：初始化数据源仓储")

    async def create(self, workspace_id: Any, values: dict[str, Any]) -> Any:
        """TODO：按 workspace_id 创建数据源并 flush。"""
        raise NotImplementedError("待实现：创建数据源")

    async def get(self, workspace_id: Any, datasource_id: Any) -> Any | None:
        """TODO：查询时必须同时过滤工作区和数据源 ID。"""
        raise NotImplementedError("待实现：获取数据源")

    async def get_by_id(self, datasource_id: Any) -> Any | None:
        """TODO：仅用于后续显式工作区鉴权的内部查询。"""
        raise NotImplementedError("待实现：按 ID 获取数据源")

    async def lock_for_update(self, workspace_id: Any, datasource_id: Any) -> Any | None:
        """TODO：对数据源行加锁，序列化 schema/画像版本变更。"""
        raise NotImplementedError("待实现：锁定数据源")

    async def list(self, workspace_id: Any) -> list[Any]:
        """TODO：只列出当前工作区的数据源。"""
        raise NotImplementedError("待实现：列出数据源")

    async def update(self, workspace_id: Any, datasource_id: Any, values: dict[str, Any]) -> Any | None:
        """TODO：更新前验证工作区归属，凭据由加密边界处理。"""
        raise NotImplementedError("待实现：更新数据源")

    async def delete(self, workspace_id: Any, datasource_id: Any) -> bool:
        """TODO：删除前检查关联任务、快照和审计保留策略。"""
        raise NotImplementedError("待实现：删除数据源")
