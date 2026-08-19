import uuid

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from quelyra_agent.api.dependencies import CurrentUser, get_current_user, get_session
from quelyra_agent.api.v1.auth import envelope
from quelyra_agent.schemas.workspace import RoleUpdateRequest, WorkspaceCreateRequest
from quelyra_agent.services.workspace_service import WorkspaceService

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.post("", status_code=201)
async def create_workspace(
    payload: WorkspaceCreateRequest,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """校验权限后创建资源并返回响应数据。"""
    return envelope(request, await WorkspaceService(session).create(current_user.id, payload.name))


@router.get("")
async def list_workspaces(
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """校验权限后列出相关资源。"""
    return envelope(request, await WorkspaceService(session).list(current_user.id))


@router.get("/{workspace_id}/members")
async def list_members(
    workspace_id: uuid.UUID,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """校验权限后列出相关资源。"""
    return envelope(
        request, await WorkspaceService(session).list_members(workspace_id, current_user.id)
    )


@router.patch("/{workspace_id}/members/{member_id}")
async def update_member_role(
    workspace_id: uuid.UUID,
    member_id: uuid.UUID,
    payload: RoleUpdateRequest,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """校验权限后更新目标资源。"""
    result = await WorkspaceService(session).update_role(
        workspace_id, current_user.id, member_id, payload.role
    )
    return envelope(request, result)


@router.delete("/{workspace_id}/members/{member_id}", status_code=204)
async def delete_member(
    workspace_id: uuid.UUID,
    member_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """校验权限后删除或移除目标资源。"""
    await WorkspaceService(session).remove_member(workspace_id, current_user.id, member_id)
    return Response(status_code=204)
