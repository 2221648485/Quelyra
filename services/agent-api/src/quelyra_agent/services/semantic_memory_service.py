"""数据库语义画像的应用服务骨架。"""

from typing import Any


class SemanticMemoryService:
    def __init__(self, session: Any, settings: Any, provider: Any, gateway: Any):
        """TODO：注入事务、模型、Gateway 和仓储依赖。"""
        raise NotImplementedError("待实现：初始化语义画像服务")

    async def start_draft(self, datasource_id: Any, actor_id: Any, force_refresh: bool = False) -> dict:
        """TODO：管理员鉴权后加载最新 schema；刷新时先 supersede 旧未决问题。"""
        raise NotImplementedError("待实现：启动画像草稿")

    async def get_current_model(self, datasource_id: Any, actor_id: Any) -> dict:
        """TODO：成员可读当前模型；返回可审阅的结构化内容和版本信息。"""
        raise NotImplementedError("待实现：获取当前画像")

    async def list_open_questions(self, datasource_id: Any, actor_id: Any) -> list[dict]:
        """TODO：只返回最新工作版本的 open 问题。"""
        raise NotImplementedError("待实现：列出澄清问题")

    async def answer_question(self, datasource_id: Any, question_id: Any, actor_id: Any, answer_text: str) -> dict:
        """TODO：基于最新 working snapshot 合并答案；不得回退到初始 draft。"""
        raise NotImplementedError("待实现：回答澄清问题")

    async def confirm_model(self, datasource_id: Any, snapshot_id: Any, actor_id: Any, approved: bool) -> dict:
        """TODO：仅当没有 open 问题且校验通过时确认；事务内原子替换 active 版本。"""
        raise NotImplementedError("待实现：确认语义画像")

    async def require_datasource_member(self, datasource_id: Any, actor_id: Any) -> Any:
        """TODO：验证数据源所在工作区成员身份。"""
        raise NotImplementedError("待实现：校验数据源成员")

    async def require_datasource_admin(self, datasource_id: Any, actor_id: Any) -> Any:
        """TODO：验证 owner/admin 身份。"""
        raise NotImplementedError("待实现：校验数据源管理员")

    def workflow(self) -> Any:
        """TODO：创建并返回数据库画像 LangGraph 工作流。"""
        raise NotImplementedError("待实现：构建画像工作流")

    @staticmethod
    def serialize_model(model: Any) -> dict:
        """TODO：向管理员展示 YAML、结构化模型、治理规则和 diff。"""
        raise NotImplementedError("待实现：序列化语义模型")

    @staticmethod
    def serialize_question(question: Any) -> dict:
        """TODO：序列化问题状态、来源版本和文本。"""
        raise NotImplementedError("待实现：序列化澄清问题")

    @staticmethod
    def serialize_answer(answer: Any) -> dict:
        """TODO：按隐私策略序列化或脱敏管理员回答。"""
        raise NotImplementedError("待实现：序列化澄清答案")
