from fastapi import APIRouter

from quelyra_agent.api.v1.auth import router as auth_router
from quelyra_agent.api.v1.analysis import router as analysis_router
from quelyra_agent.api.v1.datasources import router as datasource_router
from quelyra_agent.api.v1.users import router as users_router
from quelyra_agent.api.v1.workspaces import router as workspaces_router

api_router = APIRouter()
api_router.include_router(analysis_router)
api_router.include_router(auth_router)
api_router.include_router(datasource_router)
api_router.include_router(users_router)
api_router.include_router(workspaces_router)
