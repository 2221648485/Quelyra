from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from quelyra_agent.core.config import Settings


def build_engine(settings: Settings):
    """根据配置创建异步 SQLAlchemy 引擎。"""
    return create_async_engine(settings.database_url, pool_pre_ping=True)


def build_session_factory(engine) -> async_sessionmaker[AsyncSession]:
    """创建请求级异步数据库会话工厂。"""
    return async_sessionmaker(engine, expire_on_commit=False)
