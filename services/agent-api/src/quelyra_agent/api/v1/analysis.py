"""分析任务 HTTP 端点。"""


async def submit_question(conversation_id, payload, actor_id, session):
    """TODO：创建 queued AnalysisRun，只把 run_id 投递到 Redis，返回 202。"""
    raise NotImplementedError


async def get_analysis_run(run_id, actor_id, session):
    """TODO：按 workspace 校验后返回运行状态、结果和可展示 trace。"""
    raise NotImplementedError
