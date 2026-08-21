"""配置读取边界。"""


class Settings:
    """TODO：使用 pydantic-settings 从环境变量读取数据库、Redis、JWT、模型配置。"""


def get_settings() -> Settings:
    """TODO：返回缓存后的 Settings；不得在日志中输出密钥。"""
    raise NotImplementedError
