"""认证 HTTP 端点。"""


async def register_user(payload, session):
    """TODO：校验邮箱和密码，创建用户与默认工作区，绝不返回密码哈希。"""
    raise NotImplementedError


async def login(payload, session):
    """TODO：校验密码，轮换 refresh token，返回 access/refresh token。"""
    raise NotImplementedError
