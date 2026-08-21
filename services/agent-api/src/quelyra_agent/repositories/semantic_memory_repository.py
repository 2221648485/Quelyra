"""语义画像仓储的学习骨架。"""


class SemanticMemoryRepository:
    async def lock_datasource(self, *, workspace_id: str, datasource_id: str) -> None:
        """TODO：在短事务内锁定数据源，序列化版本递增、刷新和确认操作。"""
        raise NotImplementedError("待实现：锁定数据源")

    async def list_open_questions(self, *, workspace_id: str, datasource_id: str) -> list[dict]:
        """TODO：只返回当前工作版本的未决问题，过滤 superseded 问题。"""
        raise NotImplementedError("待实现：查询未决问题")
