from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from quelyra_agent.api.dependencies import CurrentUser, get_current_user, get_session
from quelyra_agent.api.v1.auth import envelope
from quelyra_agent.schemas.analysis import ConversationCreateRequest, QuestionRequest
from quelyra_agent.services.analysis_service import AnalysisService

router = APIRouter(tags=["analysis"])


def service(request: Request, session: AsyncSession) -> AnalysisService:
    """根据当前请求状态和数据库会话构造业务服务。"""
    return AnalysisService(session, request.app.state.settings, request.app.state.model_provider, request.app.state.gateway_client)


@router.post("/workspaces/{workspace_id}/conversations", status_code=201)
async def create_conversation(workspace_id: uuid.UUID, payload: ConversationCreateRequest, request: Request, current_user: CurrentUser = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    """校验权限后创建资源并返回响应数据。"""
    return envelope(request, await service(request, session).create_conversation(workspace_id, current_user.id, payload.title))


@router.post("/conversations/{conversation_id}/questions", status_code=201)
@router.post("/conversations/{conversation_id}/messages", status_code=201)
async def submit_question(conversation_id: uuid.UUID, payload: QuestionRequest, request: Request, current_user: CurrentUser = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    """说明当前函数的主要职责和返回边界。"""
    return envelope(request, await service(request, session).submit(conversation_id, current_user.id, payload.datasource_id, payload.question))


@router.get("/analysis-runs/{run_id}")
async def get_analysis_run(run_id: uuid.UUID, request: Request, current_user: CurrentUser = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    """查询指定资源并返回结果。"""
    return envelope(request, await service(request, session).get_run(run_id, current_user.id))
