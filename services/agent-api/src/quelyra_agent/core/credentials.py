"""数据源凭据的加密边界。"""


class CredentialCipher:
    def __init__(self, key: str):
        """TODO：验证密钥来源；生产环境应采用 KMS 或信封加密。"""
        raise NotImplementedError("待实现：初始化凭据加密器")

    def encrypt(self, plaintext: str) -> str:
        """TODO：加密凭据后才能持久化，日志中不得出现 plaintext。"""
        raise NotImplementedError("待实现：加密凭据")

    def decrypt(self, ciphertext: str) -> str:
        """TODO：仅在调用 Gateway 前短暂解密，失败时返回通用错误。"""
        raise NotImplementedError("待实现：解密凭据")
