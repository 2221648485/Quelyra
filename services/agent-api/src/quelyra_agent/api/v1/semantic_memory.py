"""语义画像 HTTP 端点。"""


async def answer_clarification(question_id, payload, actor_id, session):
    """TODO：仅 Owner/Admin 可回答；保存答案并恢复语义画像修订流程。"""
    raise NotImplementedError


async def confirm_semantic_model(datasource_id, snapshot_id, actor_id, session):
    """TODO：确认前检查所有开放问题已关闭，再原子激活唯一 active 版本。"""
    raise NotImplementedError
