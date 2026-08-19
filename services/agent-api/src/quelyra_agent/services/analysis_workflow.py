from __future__ import annotations

import json
import uuid
from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from quelyra_agent.api.errors import ApiError
from quelyra_agent.clients.query_gateway import QueryGatewayClient
from quelyra_agent.db.models import AnalysisRun, Message, SchemaSnapshot
from quelyra_agent.models.providers import ModelProvider
from quelyra_agent.services.sql_validation import SQLValidationService


class AnalysisState(TypedDict, total=False):
    workspace_id: uuid.UUID
    actor_id: uuid.UUID
    datasource_id: uuid.UUID
    conversation_id: uuid.UUID
    run_id: uuid.UUID
    question: str
    normalized_question: str
    dialect: str
    target_database: str
    schema: dict[str, Any]
    generated_sql: str
    sql: str
    used_tables: list[str]
    explain_token: str
    explain: dict[str, Any]
    columns: list[Any]
    rows: list[Any]
    stats: dict[str, Any]
    answer: str
    trace: list[str]
    error: dict[str, Any]
    result: dict[str, Any]
    repair_attempts: int
    last_error: dict[str, Any]


class AnalysisWorkflow:
    def __init__(self, session: AsyncSession, provider: ModelProvider, gateway: QueryGatewayClient, max_rows: int, max_bytes: int, query_timeout_ms: int):
        """初始化分析工作流的依赖、限制参数和执行图。"""
        self.session = session
        self.provider = provider
        self.gateway = gateway
        self.max_rows = max_rows
        self.max_bytes = max_bytes
        self.query_timeout_ms = query_timeout_ms
        self.validator = SQLValidationService(max_rows)
        self.graph = self._build_graph()

    @staticmethod
    def _step(state: AnalysisState, name: str) -> list[str]:
        """向分析追踪链追加当前步骤名称。"""
        return [*state.get("trace", []), name]

    @staticmethod
    def _error(exc: Exception) -> dict[str, str]:
        """把异常转换为可写入分析结果的错误结构。"""
        if isinstance(exc, ApiError):
            return {"code": exc.code, "message": exc.message}
        return {"code": "ANALYSIS_FAILED", "message": "Analysis could not be completed"}

    async def normalize_question(self, state: AnalysisState) -> dict:
        """压缩问题空白并记录规范化步骤。"""
        return {"normalized_question": " ".join(state["question"].split()), "trace": self._step(state, "normalize")}

    async def retrieve_context(self, state: AnalysisState) -> dict:
        """读取最新 schema 快照作为 SQL 生成上下文。"""
        trace = self._step(state, "retrieve")
        try:
            snapshot = await self.session.scalar(
                select(SchemaSnapshot).where(
                    SchemaSnapshot.workspace_id == state["workspace_id"],
                    SchemaSnapshot.datasource_id == state["datasource_id"],
                ).order_by(SchemaSnapshot.version.desc()).limit(1)
            )
            if not snapshot:
                raise ApiError(409, "SCHEMA_SNAPSHOT_REQUIRED", "Introspect the datasource before analysis")
            return {"schema": snapshot.schema_data, "dialect": "mysql", "trace": trace}
        except Exception as exc:
            error = self._error(exc)
            return {"error": error, "last_error": error, "trace": trace}

    async def generate_sql(self, state: AnalysisState) -> dict:
        """调用模型提供者生成候选 SQL。"""
        trace = self._step(state, "generate")
        try:
            generation = await self.provider.generate_sql(state["normalized_question"], state["schema"], state["dialect"])
            return {"generated_sql": generation.sql, "answer": generation.answer, "trace": trace}
        except Exception as exc:
            error = self._error(exc)
            return {"error": error, "last_error": error, "trace": trace}

    async def validate_sql(self, state: AnalysisState) -> dict:
        """校验候选 SQL 的只读性、作用域和行数限制。"""
        trace = self._step(state, "validate")
        try:
            validated = self.validator.validate(
                state["generated_sql"], state["dialect"], state["schema"],
                target_database=state["target_database"],
            )
            return {"sql": validated.normalized_sql, "used_tables": validated.used_tables, "trace": trace}
        except Exception as exc:
            error = self._error(exc)
            return {"error": error, "last_error": error, "trace": trace}

    async def explain_query(self, state: AnalysisState) -> dict:
        """调用网关执行 explain 和策略检查。"""
        trace = self._step(state, "explain")
        try:
            result = await self.gateway.explain(
                state["datasource_id"], state["workspace_id"], state["actor_id"],
                state["sql"], state["dialect"], self.max_rows, self.query_timeout_ms,
            )
            if not result.allowed:
                raise ApiError(422, "QUERY_NOT_ALLOWED", "Gateway explain policy rejected the query")
            return {"explain_token": result.explain_token, "explain": {
                "estimated_rows": result.estimated_rows, "cost": result.cost,
            }, "trace": trace}
        except Exception as exc:
            error = self._error(exc)
            return {"error": error, "last_error": error, "trace": trace}

    async def execute_query(self, state: AnalysisState) -> dict:
        """执行查询并按行数和字节数裁剪返回结果。"""
        trace = self._step(state, "execute")
        try:
            execution_id = str(uuid.uuid4())
            result = await self.gateway.execute(
                state["datasource_id"], state["workspace_id"], state["actor_id"],
                state["sql"], state["dialect"], self.max_rows, self.query_timeout_ms, state["explain_token"],
                execution_id=execution_id,
            )
            rows = []
            encoded_size = 2
            for row in result.rows[: self.max_rows]:
                row_size = len(json.dumps(row, ensure_ascii=False, default=str).encode()) + 1
                if encoded_size + row_size > self.max_bytes:
                    break
                rows.append(row)
                encoded_size += row_size
            return {
                "columns": result.columns, "rows": rows,
                "stats": {"execution_id": result.execution_id, "row_count": result.row_count,
                          "truncated": result.truncated or len(rows) < result.row_count,
                          "duration_ms": result.duration_ms},
                "trace": trace,
            }
        except Exception as exc:
            error = self._error(exc)
            return {"error": error, "last_error": error, "trace": trace}

    async def generate_insight(self, state: AnalysisState) -> dict:
        """基于查询统计生成简短回答。"""
        answer = f"Query completed and returned {state['stats']['row_count']} row(s)."
        return {"answer": answer, "trace": self._step(state, "insight")}

    async def persist_and_finish(self, state: AnalysisState) -> dict:
        """持久化成功结果并写入助手消息。"""
        trace = self._step(state, "persist")
        result = {
            "sql": state["sql"], "used_tables": state["used_tables"], "columns": state["columns"],
            "rows": state["rows"], "stats": state["stats"], "answer": state["answer"],
            "explain": state["explain"], "trace": trace,
        }
        run = await self.session.get(AnalysisRun, state["run_id"])
        run.status, run.result = "succeeded", result
        self.session.add(Message(workspace_id=state["workspace_id"], conversation_id=state["conversation_id"], role="assistant", content=state["answer"]))
        await self.session.commit()
        return {"result": result, "trace": trace}

    async def persist_failure(self, state: AnalysisState) -> dict:
        """持久化失败结果并结束工作流。"""
        trace = self._step(state, "persist")
        result = {"error": state["error"], "trace": trace}
        run = await self.session.get(AnalysisRun, state["run_id"])
        run.status, run.result = "failed", result
        await self.session.commit()
        return {"result": result, "trace": trace}

    async def repair_sql(self, state: AnalysisState) -> dict:
        """在可修复错误后请求模型重新生成 SQL。"""
        trace = self._step(state, "repair")
        try:
            repair_context = {
                "previous_sql": state.get("sql") or state.get("generated_sql", ""),
                "error": state["last_error"],
            }
            generation = await self.provider.generate_sql(
                state["normalized_question"], state["schema"], state["dialect"],
                repair_context=repair_context,
            )
            return {"generated_sql": generation.sql, "answer": generation.answer,
                    "repair_attempts": state.get("repair_attempts", 0) + 1, "error": None, "trace": trace}
        except Exception as exc:
            return {"error": self._error(exc), "repair_attempts": state.get("repair_attempts", 0) + 1, "trace": trace}

    @staticmethod
    def route(state: AnalysisState) -> str:
        """根据当前状态选择工作流分支。"""
        return "failed" if state.get("error") else "continue"

    @staticmethod
    def route_repairable(state: AnalysisState) -> str:
        """根据当前状态选择工作流分支。"""
        if not state.get("error"):
            return "continue"
        non_repairable = {
            "SQL_READ_ONLY_REQUIRED", "SQL_MULTIPLE_STATEMENTS", "SQL_SYSTEM_SCHEMA_FORBIDDEN",
            "SQL_DIALECT_MISMATCH", "UNSUPPORTED_DIALECT", "QUERY_NOT_ALLOWED",
            "GATEWAY_UNAVAILABLE", "GATEWAY_TIMEOUT", "GATEWAY_INVALID_RESPONSE",
        }
        if state["error"]["code"] not in non_repairable and state.get("repair_attempts", 0) < 1:
            return "repair"
        return "failed"

    def _build_graph(self):
        """构建分析流程的 LangGraph 状态图。"""
        graph = StateGraph(AnalysisState)
        nodes = {
            "normalize": self.normalize_question, "retrieve": self.retrieve_context,
            "generate": self.generate_sql, "validate": self.validate_sql,
            "explain": self.explain_query, "execute": self.execute_query,
            "insight": self.generate_insight, "persist": self.persist_and_finish,
            "persist_failure": self.persist_failure, "repair": self.repair_sql,
        }
        for name, node in nodes.items():
            graph.add_node(name, node)
        graph.add_edge(START, "normalize")
        graph.add_edge("normalize", "retrieve")
        for current, following in (
            ("retrieve", "generate"), ("generate", "validate"),
        ):
            graph.add_conditional_edges(current, self.route, {"continue": following, "failed": "persist_failure"})
        graph.add_conditional_edges("validate", self.route_repairable, {"continue": "explain", "repair": "repair", "failed": "persist_failure"})
        graph.add_conditional_edges("explain", self.route_repairable, {"continue": "execute", "repair": "repair", "failed": "persist_failure"})
        graph.add_conditional_edges("execute", self.route_repairable, {"continue": "insight", "repair": "repair", "failed": "persist_failure"})
        graph.add_conditional_edges("repair", self.route, {"continue": "validate", "failed": "persist_failure"})
        graph.add_edge("insight", "persist")
        graph.add_edge("persist", END)
        graph.add_edge("persist_failure", END)
        return graph.compile()
