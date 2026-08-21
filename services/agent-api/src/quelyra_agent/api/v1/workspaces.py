"""工作区 HTTP 端点。"""


async def create_workspace(payload, actor_id, session):
    """TODO：创建工作区，并将创建者写为 owner。"""
    raise NotImplementedError


async def list_members(workspace_id, actor_id, session):
    """TODO：先校验成员关系，再返回该工作区成员。"""
    raise NotImplementedError
