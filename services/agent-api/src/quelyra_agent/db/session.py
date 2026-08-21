"""SQLAlchemy 异步数据库会话边界。"""


def build_session_factory(settings):
    """TODO：创建 async engine 和 async_sessionmaker；请求与 Worker 任务不得共享 Session。"""
    raise NotImplementedError
