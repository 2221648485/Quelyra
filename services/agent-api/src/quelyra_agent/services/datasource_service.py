from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from quelyra_agent.api.errors import ApiError
from quelyra_agent.clients.query_gateway import QueryGatewayClient
from quelyra_agent.core.credentials import CredentialCipher
from quelyra_agent.db.models import DataSource, SchemaSnapshot, WorkspaceRole
from quelyra_agent.repositories.datasource_repository import DataSourceRepository
from quelyra_agent.schemas.datasource import DataSourceCreateRequest
from quelyra_agent.services.workspace_service import WorkspaceService


class DataSourceService:
    def __init__(self, session: AsyncSession, cipher: CredentialCipher, gateway: QueryGatewayClient):
        self.session = session
        self.cipher = cipher
        self.gateway = gateway
        self.datasources = DataSourceRepository(session)
        self.workspaces = WorkspaceService(session)

    async def create(self, workspace_id: uuid.UUID, actor_id: uuid.UUID, payload: DataSourceCreateRequest) -> dict:
        await self.workspaces.require_membership(workspace_id, actor_id, {WorkspaceRole.owner, WorkspaceRole.admin})
        if payload.engine.lower() != "mysql":
            raise ApiError(422, "UNSUPPORTED_DATASOURCE_ENGINE", "Only mysql datasources are supported")
        datasource = await self.datasources.create(
            workspace_id,
            {
                "name": payload.name.strip(), "engine": "mysql", "dialect": "mysql",
                "host": payload.host.strip(), "port": payload.port,
                "database_name": payload.database_name.strip(), "username": payload.username.strip(),
                "encrypted_password": self.cipher.encrypt(payload.password),
            },
        )
        await self.session.commit()
        return self.serialize(datasource)

    async def list(self, workspace_id: uuid.UUID, actor_id: uuid.UUID) -> list[dict]:
        await self.workspaces.require_membership(workspace_id, actor_id)
        return [self.serialize(item) for item in await self.datasources.list(workspace_id)]

    async def require_access(self, datasource_id: uuid.UUID, actor_id: uuid.UUID) -> DataSource:
        datasource = await self.datasources.get_by_id(datasource_id)
        if not datasource:
            raise ApiError(404, "DATASOURCE_NOT_FOUND", "Datasource was not found")
        try:
            await self.workspaces.require_membership(datasource.workspace_id, actor_id)
        except ApiError as exc:
            raise ApiError(403, "DATASOURCE_ACCESS_DENIED", "You do not have access to this datasource") from exc
        return datasource

    async def test_connection(self, datasource_id: uuid.UUID, actor_id: uuid.UUID) -> dict:
        datasource = await self.require_access(datasource_id, actor_id)
        await self.workspaces.require_membership(datasource.workspace_id, actor_id, {WorkspaceRole.owner, WorkspaceRole.admin})
        result = await self.gateway.test_connection(datasource.id, datasource.workspace_id, actor_id)
        datasource.status = "connected"
        datasource.engine_version = result.engine_version
        datasource.capabilities = result.capabilities
        await self.session.commit()
        return self.serialize(datasource)

    async def introspect(self, datasource_id: uuid.UUID, actor_id: uuid.UUID) -> dict:
        datasource = await self.require_access(datasource_id, actor_id)
        await self.workspaces.require_membership(datasource.workspace_id, actor_id, {WorkspaceRole.owner, WorkspaceRole.admin})
        result = await self.gateway.introspect(datasource.id, datasource.workspace_id, actor_id)
        datasource = await self.datasources.lock_for_update(datasource.workspace_id, datasource.id)
        version = int(await self.session.scalar(select(func.max(SchemaSnapshot.version)).where(
            SchemaSnapshot.workspace_id == datasource.workspace_id,
            SchemaSnapshot.datasource_id == datasource.id,
        )) or 0) + 1
        snapshot = SchemaSnapshot(
            workspace_id=datasource.workspace_id, datasource_id=datasource.id,
            schema_data=result.schema_data, version=version,
        )
        self.session.add(snapshot)
        datasource.status = "ready"
        datasource.engine_version = result.engine_version
        datasource.capabilities = result.capabilities
        await self.session.commit()
        return {"datasource": self.serialize(datasource), "snapshot": {
            "id": str(snapshot.id), "version": snapshot.version, "schema": snapshot.schema_data,
        }}

    @staticmethod
    def serialize(datasource: DataSource) -> dict:
        return {
            "id": str(datasource.id), "workspace_id": str(datasource.workspace_id),
            "name": datasource.name, "engine": datasource.engine, "dialect": datasource.dialect,
            "host": datasource.host, "port": datasource.port,
            "database_name": datasource.database_name, "username": datasource.username,
            "status": datasource.status, "engine_version": datasource.engine_version,
            "capabilities": datasource.capabilities,
        }
