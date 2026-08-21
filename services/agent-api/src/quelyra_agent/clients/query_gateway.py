"""到 Go Query Gateway 的内部客户端。"""


class QueryGatewayClient:
    """TODO：只通过服务 JWT 调用 connection、introspect、explain、execute、cancel。"""

    async def execute(self, request: dict) -> dict:
        """TODO：传递 execution_id 和 explain_token，映射稳定错误码，限制响应字节数。"""
        raise NotImplementedError
