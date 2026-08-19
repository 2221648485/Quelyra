from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from quelyra_agent.db.models import DataSource


class DataSourceRepository:
    """All business-resource queries require the tenant workspace explicitly."""

    def __init__(self, session: AsyncSession):
        """初始化当前组件所需的依赖和配置。"""
        self.session = session

    async def create(self, workspace_id: uuid.UUID, values: dict[str, Any]) -> DataSource:
        """校验权限后创建资源并返回响应数据。"""
        datasource = DataSource(workspace_id=workspace_id, **values)
        self.session.add(datasource)
        await self.session.flush()
        return datasource

    async def get(self, workspace_id: uuid.UUID, datasource_id: uuid.UUID) -> DataSource | None:
        """查询指定资源并返回结果。"""
        return await self.session.scalar(
            select(DataSource).where(
                DataSource.workspace_id == workspace_id, DataSource.id == datasource_id
            )
        )

    async def get_by_id(self, datasource_id: uuid.UUID) -> DataSource | None:
        """查询指定资源并返回结果。"""
        return await self.session.get(DataSource, datasource_id)

    async def lock_for_update(self, workspace_id: uuid.UUID, datasource_id: uuid.UUID) -> DataSource | None:
        """构造或执行行级锁查询，保护并发更改。"""
        return await self.session.scalar(
            select(DataSource).where(
                DataSource.workspace_id == workspace_id, DataSource.id == datasource_id
            ).with_for_update()
        )

    async def list(self, workspace_id: uuid.UUID) -> list[DataSource]:
        """校验权限后列出相关资源。"""
        return list(
            (await self.session.scalars(select(DataSource).where(DataSource.workspace_id == workspace_id))).all()
        )

    async def update(self, workspace_id: uuid.UUID, datasource_id: uuid.UUID, values: dict[str, Any]) -> DataSource | None:
        """校验权限后更新目标资源。"""
        datasource = await self.get(workspace_id, datasource_id)
        if datasource:
            for key, value in values.items():
                setattr(datasource, key, value)
        return datasource

    async def delete(self, workspace_id: uuid.UUID, datasource_id: uuid.UUID) -> bool:
        """校验权限后删除或移除目标资源。"""
        datasource = await self.get(workspace_id, datasource_id)
        if not datasource:
            return False
        await self.session.delete(datasource)
        return True
