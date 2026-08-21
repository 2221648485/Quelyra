"""用户自身信息路由。"""

from typing import Any


async def me(request: Any, current_user: Any, session: Any) -> dict:
    """TODO：读取当前用户和其可见工作区，脱敏后包装为 API 响应。"""
    raise NotImplementedError("待实现：获取当前用户")
