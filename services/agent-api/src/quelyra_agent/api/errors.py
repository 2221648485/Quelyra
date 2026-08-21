"""API 业务错误的统一表达。"""

from typing import Any


class ApiError(Exception):
    def __init__(self, status_code: int, code: str, message: str, details: Any = None):
        """TODO：保存可公开的错误信息；禁止把异常堆栈、凭据或 SQL 原样放入 details。"""
        raise NotImplementedError("待实现：构造 API 错误")
