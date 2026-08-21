"""分析任务队列边界；API 投递任务，worker 领取执行。"""

from typing import Any, Protocol


class AnalysisTaskQueue(Protocol):
    async def enqueue_analysis(self, run_id: Any) -> None:
        """TODO：只投递 run ID，敏感上下文从数据库按权限加载。"""
        raise NotImplementedError("待实现：投递分析任务")


class InMemoryAnalysisTaskQueue:
    def __init__(self):
        """TODO：仅供单进程本地开发，生产环境不能使用。"""
        raise NotImplementedError("待实现：初始化内存队列")

    async def enqueue_analysis(self, run_id: Any) -> None:
        """TODO：把任务 ID 加入内存队列。"""
        raise NotImplementedError("待实现：投递内存任务")

    async def dequeue_analysis(self) -> Any:
        """TODO：worker 阻塞获取一个任务 ID。"""
        raise NotImplementedError("待实现：领取内存任务")


class RedisAnalysisTaskQueue:
    def __init__(self, redis_client: Any):
        """TODO：保存 Redis 客户端和受控队列名称。"""
        raise NotImplementedError("待实现：初始化 Redis 队列")

    @classmethod
    async def connect(cls, redis_url: str) -> "RedisAnalysisTaskQueue":
        """TODO：连接 Redis 并执行健康检查。"""
        raise NotImplementedError("待实现：连接 Redis")

    async def enqueue_analysis(self, run_id: Any) -> None:
        """TODO：投递幂等任务消息。"""
        raise NotImplementedError("待实现：投递 Redis 任务")

    async def dequeue_analysis(self, timeout_seconds: int = 5) -> Any | None:
        """TODO：带超时领取任务，避免 worker 无限阻塞。"""
        raise NotImplementedError("待实现：领取 Redis 任务")

    async def close(self) -> None:
        """TODO：关闭 Redis 连接。"""
        raise NotImplementedError("待实现：关闭 Redis")


async def build_analysis_task_queue(settings: Any) -> AnalysisTaskQueue:
    """TODO：根据配置选择队列实现；生产环境拒绝内存队列。"""
    raise NotImplementedError("待实现：构建分析任务队列")
