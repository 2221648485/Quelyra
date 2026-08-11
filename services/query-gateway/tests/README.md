# Go Query Gateway 测试

- `integration/`：使用真实数据库验证连接器、超时、取消、限制和脱敏。
- `contract/`：验证 Python Agent 与 Gateway 的内部 OpenAPI 兼容性。

Go 包级单元测试与被测源码放在同一目录，本目录不重复收纳包内测试。
