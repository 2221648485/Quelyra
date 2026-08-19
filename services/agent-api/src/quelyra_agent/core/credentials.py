from __future__ import annotations

import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken


class CredentialCipher:
    def __init__(self, key: str):
        """初始化当前组件所需的依赖和配置。"""
        derived = base64.urlsafe_b64encode(hashlib.sha256(key.encode()).digest())
        self._fernet = Fernet(derived)

    def encrypt(self, plaintext: str) -> str:
        """说明当前函数的主要职责和返回边界。"""
        return self._fernet.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        """说明当前函数的主要职责和返回边界。"""
        try:
            return self._fernet.decrypt(ciphertext.encode()).decode()
        except InvalidToken as exc:
            raise ValueError("Stored credential cannot be decrypted") from exc
