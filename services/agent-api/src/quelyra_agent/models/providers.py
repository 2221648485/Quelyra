"""OpenAI 兼容模型供应商的抽象；第一版只实现一个固定配置。"""


class ModelProvider:
    """将模型调用隔离在基础设施层，工作流不能直接依赖 SDK。"""

    async def generate_sql(self, *, question: str, context: dict) -> dict:
        """TODO：调用固定的 OpenAI 兼容接口，返回结构化 SQL 候选和推理摘要。"""
        raise NotImplementedError("待实现：生成 SQL")

    async def profile_datasource(self, *, physical_schema: dict) -> dict:
        """TODO：生成数据库画像草稿、置信度和需要管理员回答的问题。"""
        raise NotImplementedError("待实现：生成数据库语义画像")

    async def revise_profile(self, *, draft: dict, answer: str) -> dict:
        """TODO：把管理员答案合并到当前工作草稿，并可提出新的追问。"""
        raise NotImplementedError("待实现：修订数据库语义画像")
