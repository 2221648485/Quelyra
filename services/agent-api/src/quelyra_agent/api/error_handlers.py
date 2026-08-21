"""将框架异常映射为统一 API 错误响应。"""

from typing import Any


def request_id(request: Any) -> str:
    """TODO：从请求上下文读取 request ID，没有时生成安全的兜底值。"""
    raise NotImplementedError("待实现：读取 request ID")


async def api_error_handler(request: Any, exc: Exception) -> Any:
    """TODO：转换已知业务错误，返回统一错误信封。"""
    raise NotImplementedError("待实现：处理业务错误")


async def validation_error_handler(request: Any, exc: Exception) -> Any:
    """TODO：转换输入校验错误，不能回显敏感输入。"""
    raise NotImplementedError("待实现：处理校验错误")


async def http_error_handler(request: Any, exc: Exception) -> Any:
    """TODO：转换 HTTP 异常并保留安全的状态码。"""
    raise NotImplementedError("待实现：处理 HTTP 错误")


async def unhandled_error_handler(request: Any, exc: Exception) -> Any:
    """TODO：记录内部错误并返回不含内部细节的 500 响应。"""
    raise NotImplementedError("待实现：处理未捕获错误")
