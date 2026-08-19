from __future__ import annotations

from typing import Any


class ApiError(Exception):
    def __init__(self, status_code: int, code: str, message: str, details: Any = None):
        """保存 API 错误的状态码、业务码、消息和详情。"""
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details
        super().__init__(message)
