from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from quelyra_agent.api.dependencies import CurrentUser, get_current_user, get_session
from quelyra_agent.schemas.auth import LoginRequest, LogoutRequest, RefreshRequest, RegisterRequest
from quelyra_agent.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


def envelope(request: Request, data):
    """使用统一的 data/meta 结构包装接口响应。"""
    return {"data": data, "meta": {"request_id": request.state.request_id}}


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, request: Request, session: AsyncSession = Depends(get_session)):
    """说明当前函数的主要职责和返回边界。"""
    result = await AuthService(session, request.app.state.settings).register(
        str(payload.email), payload.password, payload.name
    )
    return envelope(request, result)


@router.post("/login")
async def login(payload: LoginRequest, request: Request, session: AsyncSession = Depends(get_session)):
    """说明当前函数的主要职责和返回边界。"""
    result = await AuthService(session, request.app.state.settings).login(
        str(payload.email), payload.password
    )
    return envelope(request, result)


@router.post("/refresh")
async def refresh(payload: RefreshRequest, request: Request, session: AsyncSession = Depends(get_session)):
    """说明当前函数的主要职责和返回边界。"""
    result = await AuthService(session, request.app.state.settings).refresh(payload.refresh_token)
    return envelope(request, result)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(payload: LogoutRequest, request: Request, session: AsyncSession = Depends(get_session)):
    """说明当前函数的主要职责和返回边界。"""
    await AuthService(session, request.app.state.settings).logout(payload.refresh_token)
    return Response(status_code=204)


@router.post("/logout-all", status_code=status.HTTP_204_NO_CONTENT)
async def logout_all(
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """说明当前函数的主要职责和返回边界。"""
    await AuthService(session, request.app.state.settings).logout_all(current_user.id)
    return Response(status_code=204)
