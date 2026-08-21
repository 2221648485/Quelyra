"""FastAPI 依赖注入。"""


async def get_session():
    """TODO：为每个 HTTP 请求提供独立数据库 Session，并确保最终关闭。"""
    raise NotImplementedError


async def get_current_user():
    """TODO：从 Authorization Bearer Token 读取 claims，并加载当前用户。"""
    raise NotImplementedError
