from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from quelyra_agent.api.dependencies import CurrentUser, get_current_user, get_session
from quelyra_agent.api.v1.auth import envelope
from quelyra_agent.services.auth_service import user_data
from quelyra_agent.services.workspace_service import WorkspaceService

router = APIRouter(tags=["users"])


@router.get("/me")
async def me(
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """说明当前函数的主要职责和返回边界。"""
    workspaces = await WorkspaceService(session).list(current_user.id)
    return envelope(request, {"user": user_data(current_user.model), "workspaces": workspaces})
