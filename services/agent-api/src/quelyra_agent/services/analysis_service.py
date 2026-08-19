from __future__ import annotations

import uuid
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from quelyra_agent.api.errors import ApiError
from quelyra_agent.clients.query_gateway import QueryGatewayClient
from quelyra_agent.core.config import Settings
from quelyra_agent.db.models import AnalysisRun, Conversation, Message
from quelyra_agent.models.providers import ModelProvider
from quelyra_agent.repositories.datasource_repository import DataSourceRepository
from quelyra_agent.services.analysis_workflow import AnalysisWorkflow
from quelyra_agent.services.workspace_service import WorkspaceService

logger = logging.getLogger(__name__)


class AnalysisService:
    def __init__(self, session: AsyncSession, settings: Settings, provider: ModelProvider, gateway: QueryGatewayClient):
        """初始化当前组件所需的依赖和配置。"""
        self.session, self.settings, self.provider, self.gateway = session, settings, provider, gateway
        self.workspaces = WorkspaceService(session)
        self.datasources = DataSourceRepository(session)

    async def create_conversation(self, workspace_id: uuid.UUID, actor_id: uuid.UUID, title: str) -> dict:
        """校验权限后创建资源并返回响应数据。"""
        await self.workspaces.require_membership(workspace_id, actor_id)
        conversation = Conversation(workspace_id=workspace_id, created_by=actor_id, title=title.strip())
        self.session.add(conversation)
        await self.session.commit()
        return self.serialize_conversation(conversation)

    async def submit(self, conversation_id: uuid.UUID, actor_id: uuid.UUID, datasource_id: uuid.UUID, question: str) -> dict:
        """说明当前函数的主要职责和返回边界。"""
        conversation = await self.session.get(Conversation, conversation_id)
        if not conversation:
            raise ApiError(404, "CONVERSATION_NOT_FOUND", "Conversation was not found")
        await self.workspaces.require_membership(conversation.workspace_id, actor_id)
        datasource = await self.datasources.get(conversation.workspace_id, datasource_id)
        if not datasource:
            raise ApiError(403, "DATASOURCE_ACCESS_DENIED", "Datasource is outside this workspace")
        message = Message(workspace_id=conversation.workspace_id, conversation_id=conversation.id, role="user", content=question.strip())
        run = AnalysisRun(workspace_id=conversation.workspace_id, conversation_id=conversation.id, datasource_id=datasource.id, status="running", question=question.strip())
        self.session.add_all([message, run])
        await self.session.commit()
        run_id = run.id
        workflow = AnalysisWorkflow(self.session, self.provider, self.gateway, self.settings.max_result_rows, self.settings.max_result_bytes, self.settings.query_timeout_ms)
        try:
            await workflow.graph.ainvoke({
                "workspace_id": conversation.workspace_id, "actor_id": actor_id,
                "datasource_id": datasource.id, "conversation_id": conversation.id,
                "run_id": run.id, "question": run.question, "trace": [], "repair_attempts": 0,
                "target_database": datasource.database_name,
            })
        except Exception:
            logger.error("Analysis graph failed", extra={"analysis_run_id": str(run_id)})
            await self.session.rollback()
            try:
                failed_run = await self.session.get(AnalysisRun, run_id)
                if not failed_run:
                    raise RuntimeError("analysis run disappeared")
                failed_run.status = "failed"
                failed_run.result = {
                    "error": {"code": "ANALYSIS_INTERNAL_ERROR", "message": "Analysis could not be completed"},
                    "trace": ["persist"],
                }
                await self.session.commit()
                run = failed_run
            except Exception as persist_exc:
                await self.session.rollback()
                logger.error("Failed to persist analysis failure", extra={"analysis_run_id": str(run_id)})
                raise ApiError(500, "ANALYSIS_INTERNAL_ERROR", "Analysis could not be completed") from persist_exc
        await self.session.refresh(run)
        return self.serialize_run(run)

    async def get_run(self, run_id: uuid.UUID, actor_id: uuid.UUID) -> dict:
        """查询指定资源并返回结果。"""
        run = await self.session.get(AnalysisRun, run_id)
        if not run:
            raise ApiError(404, "ANALYSIS_RUN_NOT_FOUND", "Analysis run was not found")
        await self.workspaces.require_membership(run.workspace_id, actor_id)
        return self.serialize_run(run)

    @staticmethod
    def serialize_conversation(item: Conversation) -> dict:
        """将数据模型转换为接口响应字典。"""
        return {"id": str(item.id), "workspace_id": str(item.workspace_id), "title": item.title, "created_at": item.created_at.isoformat()}

    @staticmethod
    def serialize_run(item: AnalysisRun) -> dict:
        """将数据模型转换为接口响应字典。"""
        return {"id": str(item.id), "workspace_id": str(item.workspace_id), "conversation_id": str(item.conversation_id), "datasource_id": str(item.datasource_id), "status": item.status, "question": item.question, "result": item.result}
