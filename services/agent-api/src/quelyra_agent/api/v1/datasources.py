from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from quelyra_agent.api.dependencies import CurrentUser, get_current_user, get_session
from quelyra_agent.api.v1.auth import envelope
from quelyra_agent.core.credentials import CredentialCipher
from quelyra_agent.schemas.datasource import DataSourceCreateRequest
from quelyra_agent.services.datasource_service import DataSourceService

router = APIRouter(tags=["datasources"])


def service(request: Request, session: AsyncSession) -> DataSourceService:
    """根据当前请求状态和数据库会话构造业务服务。"""
    return DataSourceService(
        session,
        CredentialCipher(request.app.state.settings.credential_encryption_key),
        request.app.state.gateway_client,
    )


@router.post("/workspaces/{workspace_id}/datasources", status_code=201)
async def create_datasource(workspace_id: uuid.UUID, payload: DataSourceCreateRequest, request: Request, current_user: CurrentUser = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    """校验权限后创建资源并返回响应数据。"""
    return envelope(request, await service(request, session).create(workspace_id, current_user.id, payload))


@router.get("/workspaces/{workspace_id}/datasources")
async def list_datasources(workspace_id: uuid.UUID, request: Request, current_user: CurrentUser = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    """校验权限后列出相关资源。"""
    return envelope(request, await service(request, session).list(workspace_id, current_user.id))


@router.post("/datasources/{datasource_id}/test-connection")
async def test_connection(datasource_id: uuid.UUID, request: Request, current_user: CurrentUser = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    """调用网关测试数据源连接并同步状态。"""
    return envelope(request, await service(request, session).test_connection(datasource_id, current_user.id))


@router.post("/datasources/{datasource_id}/introspect")
async def introspect(datasource_id: uuid.UUID, request: Request, current_user: CurrentUser = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    """调用网关读取数据源元数据并保存 schema 快照。"""
    return envelope(request, await service(request, session).introspect(datasource_id, current_user.id))
