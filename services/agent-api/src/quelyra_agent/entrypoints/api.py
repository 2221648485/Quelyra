from __future__ import annotations

import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from starlette.exceptions import HTTPException

from quelyra_agent.api.error_handlers import (
    api_error_handler,
    http_error_handler,
    unhandled_error_handler,
    validation_error_handler,
)
from quelyra_agent.api.errors import ApiError
from quelyra_agent.api.v1.router import api_router
from quelyra_agent.core.config import Settings, get_settings
from quelyra_agent.clients.query_gateway import QueryGatewayClient
from quelyra_agent.models.providers import build_model_provider
from quelyra_agent.db.session import build_engine, build_session_factory


def create_app(settings: Settings | None = None) -> FastAPI:
    """组装 FastAPI 应用、共享状态、中间件、路由和异常处理器。"""
    settings = settings or get_settings()
    engine = build_engine(settings)
    session_factory = build_session_factory(engine)

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        """在应用关闭时释放数据库引擎资源。"""
        yield
        await engine.dispose()

    app = FastAPI(title="Quelyra Agent API", version="0.1.0", lifespan=lifespan)
    app.state.settings = settings
    app.state.engine = engine
    app.state.session_factory = session_factory
    app.state.gateway_client = QueryGatewayClient(settings)
    app.state.model_provider = build_model_provider(settings)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def request_id_middleware(request: Request, call_next):
        """为每个请求绑定并回写请求 ID。"""
        incoming = request.headers.get("X-Request-ID")
        request.state.request_id = incoming[:128] if incoming else str(uuid.uuid4())
        response = await call_next(request)
        response.headers["X-Request-ID"] = request.state.request_id
        return response

    app.add_exception_handler(ApiError, api_error_handler)
    app.add_exception_handler(HTTPException, http_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(Exception, unhandled_error_handler)
    app.include_router(api_router, prefix="/api/v1")

    @app.get("/health/live")
    async def live(request: Request):
        """返回进程存活状态。"""
        return {"data": {"status": "ok"}, "meta": {"request_id": request.state.request_id}}

    @app.get("/health/ready")
    async def ready(request: Request):
        """检查数据库连通性并返回就绪状态。"""
        try:
            async with request.app.state.engine.connect() as connection:
                await connection.execute(text("SELECT 1"))
        except Exception as exc:
            raise ApiError(503, "NOT_READY", "Database is unavailable") from exc
        return {"data": {"status": "ready"}, "meta": {"request_id": request.state.request_id}}

    return app


app = create_app()
