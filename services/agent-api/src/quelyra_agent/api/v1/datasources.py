"""数据源 HTTP 端点。"""


async def create_datasource(workspace_id, payload, actor_id, session):
    """TODO：仅 Owner/Admin 可创建；密码加密后保存，不写入日志或响应。"""
    raise NotImplementedError


async def introspect_datasource(datasource_id, actor_id, session):
    """TODO：调用 Go Gateway 读取元数据，保存不可变 SchemaSnapshot，并启动语义画像。"""
    raise NotImplementedError
