from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import TypedDict

import httpx
from pydantic import BaseModel

from quelyra_agent.api.errors import ApiError
from quelyra_agent.core.config import Settings


class ModelGeneration(BaseModel):
    sql: str
    answer: str = ""


class RepairContext(TypedDict):
    previous_sql: str
    error: dict[str, str]


class ModelProvider(ABC):
    @abstractmethod
    async def generate_sql(self, question: str, schema: dict, dialect: str, repair_context: RepairContext | None = None) -> ModelGeneration:
        """根据自然语言问题和 schema 生成只读 SQL。"""
        raise NotImplementedError

    async def generate(self, question: str, schema: dict, dialect: str) -> ModelGeneration:
        """兼容旧调用路径，委托给 SQL 生成方法。"""
        return await self.generate_sql(question, schema, dialect)


class DemoProvider(ModelProvider):
    async def generate_sql(self, question: str, schema: dict, dialect: str, repair_context: RepairContext | None = None) -> ModelGeneration:
        """基于内置规则为演示问题生成 MySQL 查询。"""
        if repair_context:
            raise ApiError(422, "DEMO_REPAIR_UNAVAILABLE", "Demo provider cannot safely repair generated SQL")
        if dialect != "mysql":
            raise ApiError(422, "UNSUPPORTED_DIALECT", "Demo provider supports MySQL only")
        text = question.strip().lower()
        table_items = {item["name"]: item for item in schema.get("tables", [])}
        tables = set(table_items)
        columns = {
            name: {column["name"] for column in table.get("columns", [])}
            for name, table in table_items.items()
        }
        if ("总额" in text or "revenue" in text or "amount" in text) and "orders" in tables:
            if "total_amount" in columns.get("orders", set()):
                sql = "SELECT SUM(total_amount) AS order_total FROM orders"
            elif "order_items" in tables and {"quantity", "unit_price"} <= columns.get("order_items", set()):
                sql = "SELECT SUM(quantity * unit_price) AS order_total FROM order_items"
            else:
                raise ApiError(422, "DEMO_SCHEMA_UNSUPPORTED", "Demo schema does not expose order amount columns")
        elif ("订单" in text or "order" in text) and ("数量" in text or "count" in text) and "orders" in tables:
            sql = "SELECT COUNT(*) AS order_count FROM orders"
        elif ("客户" in text or "customer" in text) and ("数量" in text or "count" in text) and "customers" in tables:
            sql = "SELECT COUNT(*) AS customer_count FROM customers"
        elif ("销量" in text or "sales" in text) and {"products", "order_items"} <= tables:
            sql = (
                "SELECT p.id, p.name, SUM(oi.quantity) AS units_sold "
                "FROM products AS p JOIN order_items AS oi ON oi.product_id = p.id "
                "GROUP BY p.id, p.name ORDER BY units_sold DESC LIMIT 20"
            )
        elif ("类目" in text or "category" in text) and "products" in tables:
            sql = "SELECT category_id, COUNT(*) AS product_count FROM products GROUP BY category_id ORDER BY product_count DESC LIMIT 50"
        else:
            raise ApiError(422, "DEMO_UNSUPPORTED_QUESTION", "Demo provider cannot answer this question; please clarify it")
        return ModelGeneration(sql=sql, answer="Generated a read-only query from the available schema.")


class OpenAICompatibleProvider(ModelProvider):
    def __init__(self, settings: Settings, transport: httpx.AsyncBaseTransport | None = None):
        """初始化当前组件所需的依赖和配置。"""
        self.settings = settings
        self.transport = transport

    async def generate_sql(self, question: str, schema: dict, dialect: str, repair_context: RepairContext | None = None) -> ModelGeneration:
        """调用 OpenAI 兼容接口生成结构化 SQL 结果。"""
        if not self.settings.model_api_key:
            raise ApiError(503, "MODEL_NOT_CONFIGURED", "Model API key is not configured")
        prompt = (
            "Return JSON with string fields sql and answer. Generate exactly one read-only SELECT "
            f"for dialect {dialect}. Schema: {json.dumps(schema, ensure_ascii=False)}. Question: {question}"
        )
        if repair_context:
            prompt += (
                ". Repair the previous SQL without changing intent. "
                f"Previous SQL: {repair_context['previous_sql']}. "
                f"Validation or execution error: {json.dumps(repair_context['error'], ensure_ascii=False)}"
            )
        try:
            async with httpx.AsyncClient(
                base_url=self.settings.model_base_url,
                timeout=self.settings.model_timeout_seconds,
                transport=self.transport,
                headers={"Authorization": f"Bearer {self.settings.model_api_key}"},
            ) as client:
                response = await client.post(
                    "/chat/completions",
                    json={
                        "model": self.settings.model_name,
                        "messages": [{"role": "user", "content": prompt}],
                        "response_format": {"type": "json_object"},
                        "temperature": 0,
                    },
                )
                response.raise_for_status()
                content = response.json()["choices"][0]["message"]["content"]
                return ModelGeneration.model_validate_json(content)
        except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError) as exc:
            raise ApiError(502, "MODEL_PROVIDER_ERROR", "Model provider failed to generate a query") from exc


def build_model_provider(settings: Settings) -> ModelProvider:
    """根据配置选择演示提供者或 OpenAI 兼容提供者。"""
    if settings.model_provider.lower() == "demo" or not settings.model_api_key:
        return DemoProvider()
    return OpenAICompatibleProvider(settings)
