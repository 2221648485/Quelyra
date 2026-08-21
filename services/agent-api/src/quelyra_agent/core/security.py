"""认证与服务间令牌工具。"""


def create_access_token(user_id: str, workspace_id: str) -> str:
    """TODO：签发短期 JWT，包含用户、工作区、issuer、audience 和过期时间。"""
    raise NotImplementedError


def verify_access_token(token: str) -> dict:
    """TODO：校验签名、过期时间、issuer、audience 后返回 claims。"""
    raise NotImplementedError
