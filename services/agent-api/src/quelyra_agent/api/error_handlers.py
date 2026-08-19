from __future__ import annotations

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from quelyra_agent.api.errors import ApiError


def request_id(request: Request) -> str:
    """读取请求上下文中的请求 ID。"""
    return getattr(request.state, "request_id", "unknown")


async def api_error_handler(request: Request, exc: ApiError) -> JSONResponse:
    """将 API 业务异常转换为统一错误响应。"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "request_id": request_id(request),
                "details": exc.details,
            }
        },
    )


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """将请求校验异常转换为统一错误响应。"""
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "request_id": request_id(request),
                "details": exc.errors(),
            }
        },
    )


async def http_error_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """将 HTTP 异常转换为统一错误响应。"""
    message = exc.detail if isinstance(exc.detail, str) else "HTTP request failed"
    details = None if isinstance(exc.detail, str) else exc.detail
    return JSONResponse(
        status_code=exc.status_code,
        headers=exc.headers,
        content={
            "error": {
                "code": f"HTTP_{exc.status_code}",
                "message": message,
                "request_id": request_id(request),
                "details": details,
            }
        },
    )


async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """将未捕获异常转换为统一的 500 错误响应。"""
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "request_id": request_id(request),
                "details": None,
            }
        },
    )
