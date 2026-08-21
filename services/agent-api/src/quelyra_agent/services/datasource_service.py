"""数据源应用服务。

agent-api 管理工作区、权限、加密凭据引用和 Schema Snapshot；真实数据库连接、
元数据抓取与 SQL 执行必须交给 Go Query Gateway。
"""

from typing import Any


class DataSourceService:
    """数据源管理用例。

实现时注入 DataSourceRepository、MembershipRepository、SchemaSnapshotRepository、
CredentialCipher、QueryGatewayClient 与 SemanticMemoryService。
"""

    def __init__(self, session: Any, settings: Any, gateway: Any, semantic_memory: Any | None = None):
        """保存依赖，不建立真实数据库连接。

实现提示：Gateway 客户端应复用受控 HTTP 会话；凭据只在需要发给 Gateway 时短暂
解密，禁止放入日志、任务消息和异常文本。
"""
        raise NotImplementedError("待实现：初始化数据源服务")

    async def create(self, workspace_id: Any, actor_id: Any, payload: Any) -> dict:
        """创建工作区下的数据源。

实现顺序：验证 actor 是 owner/admin → 校验主机、端口、方言等输入 → 加密密码 →
创建 DataSource → flush → 返回 serialize 结果。不要让浏览器或 agent-api 直接
测试数据库连接；连接测试是独立的 Gateway 请求。
"""
        raise NotImplementedError("待实现：创建数据源")

    async def list(self, workspace_id: Any, actor_id: Any) -> list[dict]:
        """列出当前工作区的数据源。

实现提示：先验证成员关系，再通过 repository 的 workspace_id 条件查询。每项都用
serialize 输出，绝不返回 password_ciphertext、连接串或 Gateway 内部凭据 ID。
"""
        raise NotImplementedError("待实现：列出数据源")

    async def require_access(self, datasource_id: Any, actor_id: Any) -> Any:
        """验证用户对数据源的成员访问权。

实现顺序：查询数据源 → 根据其 workspace_id 查询成员关系 → 不存在和无权限采用
一致的安全错误策略。需要管理权限的操作再由调用方法检查角色。
"""
        raise NotImplementedError("待实现：校验数据源访问")

    async def test_connection(self, datasource_id: Any, actor_id: Any) -> dict:
        """通过 Gateway 测试连接。

实现顺序：require_access → 检查 owner/admin → 解密凭据 → 调用 Gateway → 映射为
安全错误和能力摘要。无论成功失败，都不能把底层数据库错误或密码返回给前端。
"""
        raise NotImplementedError("待实现：测试数据源连接")

    async def introspect(self, datasource_id: Any, actor_id: Any) -> dict:
        """抓取物理 Schema 并驱动画像更新。

实现顺序：管理员鉴权 → Gateway introspect → 规范化并哈希 schema → 与最新
SchemaSnapshot 比较 → 有变化则在数据源锁内创建新版本、标记旧语义模型 stale、
supersede 旧问题并启动新画像草稿。模型失败要记录可重试状态，不能静默吞掉。
"""
        raise NotImplementedError("待实现：抓取并保存 Schema")

    @staticmethod
    def serialize(datasource: Any) -> dict:
        """输出安全的数据源响应。

实现提示：包含名称、方言、状态、创建时间和最新 schema 版本；排除所有凭据、密文、
内部主机细节及供应商异常。
"""
        raise NotImplementedError("待实现：序列化数据源")
