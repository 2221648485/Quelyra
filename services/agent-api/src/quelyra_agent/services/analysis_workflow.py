"""SQL 分析 LangGraph 骨架。"""


class AnalysisWorkflow:
    """TODO：构建 START→normalize→retrieve→plan→generate→validate→explain→execute→persist 状态图。"""

    def build_graph(self):
        """TODO：使用 StateGraph 定义节点、条件边、失败分支和最多一次 SQL 修复。"""
        raise NotImplementedError

    async def retrieve_context(self, state: dict) -> dict:
        """TODO：读取最新 SchemaSnapshot 和唯一 active SemanticModelSnapshot。"""
        raise NotImplementedError

    async def validate_sql(self, state: dict) -> dict:
        """TODO：在调用 Gateway 前做 SQLGlot 只读、单语句、表列和 LIMIT 校验。"""
        raise NotImplementedError
