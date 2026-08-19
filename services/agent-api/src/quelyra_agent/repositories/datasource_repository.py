from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from quelyra_agent.db.models import DataSource


class DataSourceRepository:
    """All business-resource queries require the tenant workspace explicitly."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, workspace_id: uuid.UUID, values: dict[str, Any]) -> DataSource:
        datasource = DataSource(workspace_id=workspace_id, **values)
        self.session.add(datasource)
        await self.session.flush()
        return datasource

    async def get(self, workspace_id: uuid.UUID, datasource_id: uuid.UUID) -> DataSource | None:
        return await self.session.scalar(
            select(DataSource).where(
                DataSource.workspace_id == workspace_id, DataSource.id == datasource_id
            )
        )

    async def get_by_id(self, datasource_id: uuid.UUID) -> DataSource | None:
        return await self.session.get(DataSource, datasource_id)

    async def lock_for_update(self, workspace_id: uuid.UUID, datasource_id: uuid.UUID) -> DataSource | None:
        return await self.session.scalar(
            select(DataSource).where(
                DataSource.workspace_id == workspace_id, DataSource.id == datasource_id
            ).with_for_update()
        )

    async def list(self, workspace_id: uuid.UUID) -> list[DataSource]:
        return list(
            (await self.session.scalars(select(DataSource).where(DataSource.workspace_id == workspace_id))).all()
        )

    async def update(self, workspace_id: uuid.UUID, datasource_id: uuid.UUID, values: dict[str, Any]) -> DataSource | None:
        datasource = await self.get(workspace_id, datasource_id)
        if datasource:
            for key, value in values.items():
                setattr(datasource, key, value)
        return datasource

    async def delete(self, workspace_id: uuid.UUID, datasource_id: uuid.UUID) -> bool:
        datasource = await self.get(workspace_id, datasource_id)
        if not datasource:
            return False
        await self.session.delete(datasource)
        return True
