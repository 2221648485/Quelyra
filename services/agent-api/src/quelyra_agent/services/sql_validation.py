from __future__ import annotations

from dataclasses import dataclass

import sqlglot
from sqlglot import exp
from sqlglot.errors import ParseError
from sqlglot.optimizer.scope import Scope, traverse_scope

from quelyra_agent.api.errors import ApiError


@dataclass(frozen=True)
class ValidatedSQL:
    normalized_sql: str
    used_tables: list[str]


class SQLValidationService:
    DANGEROUS_SCHEMAS = {"information_schema", "mysql", "performance_schema", "sys"}
    FORBIDDEN = (
        exp.Insert, exp.Update, exp.Delete, exp.Create, exp.Drop, exp.Alter,
        exp.Command, exp.Transaction, exp.Commit, exp.Rollback,
    )

    def __init__(self, max_rows: int):
        """初始化当前组件所需的依赖和配置。"""
        self.max_rows = max_rows

    def validate(self, sql: str, dialect: str, schema: dict, target_database: str | None = None) -> ValidatedSQL:
        """解析并校验 SQL，确保只读、同库且字段存在。"""
        if dialect.lower() != "mysql":
            raise ApiError(422, "UNSUPPORTED_DIALECT", "Target dialect must be mysql")
        try:
            statements = sqlglot.parse(sql, read=dialect)
        except (ParseError, ValueError) as exc:
            raise ApiError(422, "SQL_PARSE_ERROR", "SQL could not be parsed") from exc
        if len(statements) != 1 or statements[0] is None:
            raise ApiError(422, "SQL_MULTIPLE_STATEMENTS", "Exactly one SQL statement is required")
        expression = statements[0]
        if not isinstance(expression, (exp.Select, exp.Union, exp.Intersect, exp.Except)):
            raise ApiError(422, "SQL_READ_ONLY_REQUIRED", "Only SELECT queries are allowed")
        if any(expression.find(kind) is not None for kind in self.FORBIDDEN):
            raise ApiError(422, "SQL_READ_ONLY_REQUIRED", "Only read-only SQL is allowed")
        if any(select.args.get("locks") for select in expression.find_all(exp.Select)) or expression.args.get("locks"):
            raise ApiError(422, "SQL_READ_ONLY_REQUIRED", "Only read-only SQL is allowed")

        schema_tables = self._schema_tables(schema)
        cte_reference_ids = {
            id(node)
            for scope in traverse_scope(expression)
            for node, source in scope.selected_sources.values()
            if isinstance(node, exp.Table) and isinstance(source, Scope)
        }
        tables: list[str] = []
        aliases: dict[str, str] = {}
        for table in expression.find_all(exp.Table):
            name = table.name.lower()
            db = (table.db or "").lower()
            if db in self.DANGEROUS_SCHEMAS:
                raise ApiError(422, "SQL_SYSTEM_SCHEMA_FORBIDDEN", "System schemas are not queryable")
            if db and (not target_database or db != target_database.lower()):
                raise ApiError(422, "SQL_DATABASE_FORBIDDEN", "Cross-database queries are not allowed")
            if id(table) in cte_reference_ids:
                continue
            if name not in schema_tables:
                raise ApiError(422, "SQL_UNKNOWN_TABLE", f"Unknown table: {name}")
            if name not in tables:
                tables.append(name)
            aliases[(table.alias_or_name or name).lower()] = name
            aliases[name] = name

        self._validate_scopes(expression, schema_tables)

        limit = expression.args.get("limit")
        current = None
        if limit and isinstance(limit.expression, exp.Literal) and limit.expression.is_int:
            current = int(limit.expression.this)
        if current is None or current > self.max_rows:
            expression.set("limit", exp.Limit(expression=exp.Literal.number(self.max_rows)))
        return ValidatedSQL(expression.sql(dialect=dialect), tables)

    @staticmethod
    def _validate_scopes(expression: exp.Expression, schema_tables: dict[str, set[str]]) -> None:
        """按 sqlglot 作用域校验引用列是否来自可见数据源。"""
        for scope in traverse_scope(expression):
            output_aliases = {
                item.alias.lower() for item in scope.expression.expressions
                if isinstance(item, exp.Alias) and item.alias
            }
            for column in scope.columns:
                name = column.name.lower()
                if name == "*" or (not column.table and name in output_aliases):
                    continue
                if column.table:
                    candidates = SQLValidationService._source_columns(
                        scope.selected_sources.get(column.table.lower()), schema_tables
                    )
                else:
                    candidates = set()
                    for selected in scope.selected_sources.values():
                        candidates.update(SQLValidationService._source_columns(selected, schema_tables))
                if name not in candidates:
                    raise ApiError(422, "SQL_UNKNOWN_COLUMN", f"Unknown column: {column.name}")

    @staticmethod
    def _source_columns(selected, schema_tables: dict[str, set[str]]) -> set[str]:
        """解析作用域来源可提供的列集合。"""
        if not selected:
            return set()
        _node, source = selected
        if isinstance(source, Scope):
            return SQLValidationService._scope_output_columns(source, schema_tables)
        if isinstance(source, exp.Table):
            return schema_tables.get(source.name.lower(), set())
        return set()

    @staticmethod
    def _scope_output_columns(scope: Scope, schema_tables: dict[str, set[str]]) -> set[str]:
        """推导子查询或 CTE 作用域的输出列集合。"""
        if scope.outer_columns:
            return {name.lower() for name in scope.outer_columns}
        columns: set[str] = set()
        for projection in scope.expression.expressions:
            if isinstance(projection, exp.Star):
                for selected in scope.selected_sources.values():
                    columns.update(SQLValidationService._source_columns(selected, schema_tables))
            elif isinstance(projection, exp.Column) and projection.is_star:
                selected = scope.selected_sources.get((projection.table or "").lower())
                columns.update(SQLValidationService._source_columns(selected, schema_tables))
            elif projection.alias_or_name:
                columns.add(projection.alias_or_name.lower())
        return columns

    @staticmethod
    def _schema_tables(schema: dict) -> dict[str, set[str]]:
        """把 schema 快照转换为小写表名到列集合的映射。"""
        result: dict[str, set[str]] = {}
        raw_tables = schema.get("tables", [])
        if isinstance(raw_tables, dict):
            raw_tables = [{"name": name, "columns": columns} for name, columns in raw_tables.items()]
        for table in raw_tables:
            name = str(table.get("name", "")).lower()
            columns = table.get("columns", [])
            result[name] = {
                str(column.get("name") if isinstance(column, dict) else column).lower()
                for column in columns
            }
        return result
