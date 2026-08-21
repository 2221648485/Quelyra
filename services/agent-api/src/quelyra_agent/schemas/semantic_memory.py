"""语义画像 API 契约。"""


class SemanticModelDraftRequest:
    """TODO：定义 force_refresh 等创建画像参数。"""


class SemanticModelConfirmationRequest:
    """TODO：定义确认/拒绝语义模型的管理员操作。"""


class ClarificationAnswerRequest:
    """TODO：答案去除空白后必须非空，并限制长度、防止粘贴敏感数据。"""


class SemanticModelSummary:
    """TODO：定义返回给管理员的模型版本、状态、完整内容和治理摘要。"""
