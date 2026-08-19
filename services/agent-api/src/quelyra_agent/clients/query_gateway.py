# 用途：通过版本化内部契约调用 Go Query Gateway。
from __future__ import annotations

import uuid
import json
from typing import Any

import httpx
from pydantic import AliasChoices, BaseModel, Field, model_validator
from pydantic import ValidationError

from quelyra_agent.api.errors import ApiError
from quelyra_agent.core.config import Settings
from quelyra_agent.core.security import create_service_token


class ConnectionTestResult(BaseModel):
    engine_version: str | None = None
    capabilities: dict[str, Any] = Field(default_factory=dict)


class IntrospectionResult(ConnectionTestResult):
    schema_data: dict[str, Any] = Field(default_factory=dict)
    tables: list[dict[str, Any]] = Field(default_factory=list)

    @model_validator(mode="after")
    def normalize_schema(self):
        if not self.schema_data and self.tables:
            self.schema_data = {"tables": self.tables}
        elif not self.tables and isinstance(self.schema_data.get("tables"), list):
            self.tables = self.schema_data["tables"]
        return self


class ExplainResult(BaseModel):
    explain_token: str
    estimated_rows: int | None = None
    cost: float | None = Field(default=None, validation_alias=AliasChoices("cost", "estimated_cost"))
    allowed: bool = True


class ExecuteResult(BaseModel):
    execution_id: str
    columns: list[Any] = Field(max_length=1000)
    rows: list[Any] = Field(max_length=10000)
    row_count: int
    truncated: bool = False
    duration_ms: int | float | None = None


class QueryGatewayClient:
    def __init__(self, settings: Settings, transport: httpx.AsyncBaseTransport | None = None):
        self.settings = settings
        self._transport = transport

    async def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        context = {key: payload.get(key) for key in ("actor_id", "workspace_id", "datasource_id")}
        if not all(isinstance(value, str) and value for value in context.values()):
            raise ApiError(500, "GATEWAY_CONTEXT_REQUIRED", "Gateway authorization context is incomplete")
        headers = {"Authorization": f"Bearer {create_service_token(self.settings, **context)}"}
        try:
            async with httpx.AsyncClient(
                base_url=self.settings.gateway_base_url,
                timeout=self.settings.gateway_timeout_seconds,
                transport=self._transport,
                headers=headers,
            ) as client:
                request = client.build_request("POST", path, json=payload)
                response = await client.send(request, stream=True)
                content = bytearray()
                try:
                    async for chunk in response.aiter_bytes():
                        content.extend(chunk)
                        if len(content) > self.settings.gateway_max_response_bytes:
                            raise ApiError(502, "GATEWAY_RESPONSE_TOO_LARGE", "Query Gateway response exceeded the configured limit")
                finally:
                    await response.aclose()
        except httpx.TimeoutException as exc:
            raise ApiError(504, "GATEWAY_TIMEOUT", "Query Gateway timed out") from exc
        except httpx.HTTPError as exc:
            raise ApiError(503, "GATEWAY_UNAVAILABLE", "Query Gateway is unavailable") from exc
        if response.status_code >= 500:
            raise ApiError(503, "GATEWAY_UNAVAILABLE", "Query Gateway is unavailable")
        if response.status_code >= 400:
            code, message = "GATEWAY_REJECTED", "Query Gateway rejected the request"
            try:
                body = json.loads(content)
                error = body.get("error") if isinstance(body, dict) else None
                if isinstance(error, dict) and isinstance(error.get("code"), str):
                    code = error["code"]
            except (ValueError, TypeError):
                pass
            raise ApiError(422, code, message)
        try:
            raw = json.loads(content)
            if not isinstance(raw, dict):
                raise ValueError("response is not an object")
            data = raw.get("data", raw)
            if not isinstance(data, dict):
                raise ValueError("data is not an object")
            return data
        except (ValueError, TypeError) as exc:
            raise ApiError(502, "GATEWAY_INVALID_RESPONSE", "Query Gateway returned invalid JSON") from exc

    async def _validated(self, path: str, payload: dict[str, Any], model):
        try:
            return model.model_validate(await self._post(path, payload))
        except ValidationError as exc:
            raise ApiError(502, "GATEWAY_INVALID_RESPONSE", "Query Gateway returned an invalid response") from exc

    @staticmethod
    def _context(datasource_id: uuid.UUID, workspace_id: uuid.UUID, actor_id: uuid.UUID) -> dict[str, str]:
        return {"datasource_id": str(datasource_id), "workspace_id": str(workspace_id), "actor_id": str(actor_id)}

    async def test_connection(self, datasource_id: uuid.UUID, workspace_id: uuid.UUID, actor_id: uuid.UUID) -> ConnectionTestResult:
        return await self._validated("/internal/v1/connections/test", self._context(datasource_id, workspace_id, actor_id), ConnectionTestResult)

    async def introspect(self, datasource_id: uuid.UUID, workspace_id: uuid.UUID, actor_id: uuid.UUID) -> IntrospectionResult:
        return await self._validated("/internal/v1/metadata/introspect", self._context(datasource_id, workspace_id, actor_id), IntrospectionResult)

    async def explain(self, datasource_id: uuid.UUID, workspace_id: uuid.UUID, actor_id: uuid.UUID, sql: str, dialect: str, max_rows: int, timeout_ms: int) -> ExplainResult:
        payload = self._context(datasource_id, workspace_id, actor_id) | {"sql": sql, "dialect": dialect, "max_rows": max_rows, "timeout_ms": timeout_ms}
        return await self._validated("/internal/v1/queries/explain", payload, ExplainResult)

    async def execute(self, datasource_id: uuid.UUID, workspace_id: uuid.UUID, actor_id: uuid.UUID, sql: str, dialect: str, max_rows: int, timeout_ms: int, explain_token: str, execution_id: str | None = None) -> ExecuteResult:
        payload = self._context(datasource_id, workspace_id, actor_id) | {"sql": sql, "dialect": dialect, "max_rows": max_rows, "timeout_ms": timeout_ms, "explain_token": explain_token}
        if execution_id:
            payload["execution_id"] = execution_id
        return await self._validated("/internal/v1/queries/execute", payload, ExecuteResult)

    async def cancel(self, datasource_id: uuid.UUID, workspace_id: uuid.UUID, actor_id: uuid.UUID, execution_id: str) -> bool:
        data = await self._post(
            f"/internal/v1/queries/{execution_id}/cancel",
            self._context(datasource_id, workspace_id, actor_id),
        )
        return bool(data.get("canceled"))
