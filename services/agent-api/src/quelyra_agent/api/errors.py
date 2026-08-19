# 用途：将应用异常映射为稳定且统一的 HTTP 错误响应。
from __future__ import annotations

from typing import Any


class ApiError(Exception):
    def __init__(self, status_code: int, code: str, message: str, details: Any = None):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details
        super().__init__(message)
