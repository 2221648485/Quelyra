"""分析会话与异步任务的应用服务骨架。"""

from typing import Any


class AnalysisService:
    def __init__(self, session: Any, settings: Any, provider: Any, gateway: Any, task_queue: Any):
        """TODO：注入仓储、模型供应商、Gateway 客户端与任务队列。"""
        raise NotImplementedError("待实现：初始化分析服务")

    async def create_conversation(self, workspace_id: Any, actor_id: Any, title: str) -> dict:
        """TODO：验证成员身份后创建会话。"""
        raise NotImplementedError("待实现：创建分析会话")

    async def submit(self, conversation_id: Any, actor_id: Any, datasource_id: Any, question: str) -> dict:
        """TODO：鉴权、创建 run、保存问题、投递任务；API 不同步调用模型。"""
        raise NotImplementedError("待实现：提交分析问题")

    async def get_run(self, run_id: Any, actor_id: Any) -> dict:
        """TODO：仅向所属工作区成员返回任务状态与安全结果。"""
        raise NotImplementedError("待实现：获取分析任务")

    @staticmethod
    def serialize_conversation(item: Any) -> dict:
        """TODO：序列化会话并排除内部字段。"""
        raise NotImplementedError("待实现：序列化会话")

    @staticmethod
    def serialize_run(item: Any) -> dict:
        """TODO：序列化 run、SQL 摘要、状态和安全错误。"""
        raise NotImplementedError("待实现：序列化分析任务")
