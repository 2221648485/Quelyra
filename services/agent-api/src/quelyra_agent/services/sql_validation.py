"""确定性 SQL 安全校验。"""


class SQLValidationService:
    """TODO：使用 SQLGlot 而不是字符串匹配执行 SQL 安全校验。"""

    def validate(self, sql: str, dialect: str, schema: dict) -> dict:
        """TODO：拒绝写操作、多语句、系统库、跨库访问、未知表列和超限 LIMIT。"""
        raise NotImplementedError
