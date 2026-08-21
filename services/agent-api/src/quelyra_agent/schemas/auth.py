"""认证 API 的请求契约。"""


class RegisterRequest:
    """TODO：定义注册输入字段和密码策略。"""

    @classmethod
    def normalize_email(cls, value: str) -> str:
        """TODO：标准化邮箱并拒绝空值。"""
        raise NotImplementedError("待实现：标准化邮箱")

    @classmethod
    def clean_name(cls, value: str) -> str:
        """TODO：去除首尾空白并限制显示名长度。"""
        raise NotImplementedError("待实现：清理显示名")


class LoginRequest:
    """TODO：定义登录邮箱与密码字段。"""

    @classmethod
    def normalize_email(cls, value: str) -> str:
        """TODO：复用同一邮箱规范化规则。"""
        raise NotImplementedError("待实现：标准化登录邮箱")


class RefreshRequest:
    """TODO：定义刷新令牌输入，令牌只能通过安全 Cookie 或受控请求体传递。"""


class LogoutRequest(RefreshRequest):
    """TODO：定义登出时撤销指定会话族或全部会话的字段。"""
