from pydantic import BaseModel, Field

from quelyra_agent.db.models import WorkspaceRole


class WorkspaceCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)


class RoleUpdateRequest(BaseModel):
    role: WorkspaceRole
