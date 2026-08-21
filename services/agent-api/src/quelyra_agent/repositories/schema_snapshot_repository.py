"""物理 Schema 快照仓储骨架。"""

from typing import Any


class SchemaSnapshotRepository:
    def __init__(self, session: Any):
        """TODO：保存异步数据库会话。"""
        raise NotImplementedError("待实现：初始化 schema 快照仓储")

    async def get(self, workspace_id: Any, datasource_id: Any, snapshot_id: Any) -> Any | None:
        """TODO：按工作区、数据源和快照 ID 三重过滤。"""
        raise NotImplementedError("待实现：获取 schema 快照")

    async def get_latest(self, workspace_id: Any, datasource_id: Any) -> Any | None:
        """TODO：读取最新不可变物理 schema 版本。"""
        raise NotImplementedError("待实现：获取最新 schema")

    async def next_version(self, workspace_id: Any, datasource_id: Any) -> int:
        """TODO：在数据源锁保护下计算下一个版本，禁止 MAX(version)+1 竞态。"""
        raise NotImplementedError("待实现：生成 schema 版本")

    async def create(self, workspace_id: Any, datasource_id: Any, schema_data: dict[str, Any]) -> Any:
        """TODO：保存规范化 schema、哈希与版本。"""
        raise NotImplementedError("待实现：创建 schema 快照")
