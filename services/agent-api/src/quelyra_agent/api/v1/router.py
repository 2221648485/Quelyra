from fastapi import APIRouter

from quelyra_agent.api.v1 import auth
from quelyra_agent.api.v1 import workspaces

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(workspaces.router)