"""数据源语义画像 LangGraph 骨架。"""


class DatasourceUnderstandingWorkflow:
    """TODO：构建 load_schema→generate_draft→persist_draft 的可追踪语义图。"""

    def build_graph(self):
        """TODO：定义明确状态、节点和边；人工回答跨请求时由数据库快照状态恢复。"""
        raise NotImplementedError

    async def generate_draft(self, state: dict) -> dict:
        """TODO：调用 OpenAI 兼容模型生成 YAML、model_data 和澄清问题。"""
        raise NotImplementedError

    async def persist_draft(self, state: dict) -> dict:
        """TODO：事务内保存版本化快照和问题；不得把模型输出直接激活。"""
        raise NotImplementedError
