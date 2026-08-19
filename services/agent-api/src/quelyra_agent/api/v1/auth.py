# 用途：提供身份认证和当前用户相关的 HTTP 接口。
from fastapi import FastAPI, APIRouter,Request,status,Depends,Response
from sqlalchemy.ext.asyncio import AsyncSession

from quelyra_agent.api.dependencies import get_session, CurrentUser, get_current_user
from quelyra_agent.schemas.auth import RegisterRequest, LoginRequest, RefreshRequest, LogoutRequest
from quelyra_agent.services.auth_service import AuthService

app = FastAPI()

router = APIRouter(prefix="/auth", tags=["auth"])

# 统一包装返回
def envelope(request: Request, data):
    return {"data": data, "meta": {"request_id": request.state.request_id}}

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, request: Request, session: AsyncSession = Depends(get_session)):
    result = await AuthService(session, request.app.state.settings).register(
        str(payload.email), payload.password, payload.name
    )
    return envelope(request, result)

@router.post("/login")
async def login(payload: LoginRequest, request: Request, session: AsyncSession = Depends(get_session)):
    result = await AuthService(session, request.app.state.settings).login(
        str(payload.email), payload.password
    )
    return envelope(request, result)


@router.post("/refresh")
async def refresh(payload: RefreshRequest, request: Request, session: AsyncSession = Depends(get_session)):
    result = await AuthService(session, request.app.state.settings).refresh(payload.refresh_token)
    return envelope(request, result)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(payload: LogoutRequest, request: Request, session: AsyncSession = Depends(get_session)):
    await AuthService(session, request.app.state.settings).logout(payload.refresh_token)
    return Response(status_code=204)


@router.post("/logout-all", status_code=status.HTTP_204_NO_CONTENT)
async def logout_all(
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    await AuthService(session, request.app.state.settings).logout_all(current_user.id)
    return Response(status_code=204)