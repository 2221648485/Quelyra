# Go Query Gateway

该服务是 Quelyra 访问客户数据库时不可绕过的安全边界，集中负责凭据、连接、元数据发现、SQL 策略、Explain、受限执行、取消、脱敏、结果制品和审计。

## 目录职责

- `cmd/server/`：进程组装与启动入口。
- `internal/api/`：Gin 路由、中间件与 HTTP Handler。
- `internal/application/`：网关用例编排。
- `internal/domain/`：框架无关的网关领域模型。
- `internal/connector/`：数据库无关接口与 MySQL/PostgreSQL 实现。
- `internal/policy/`：只读、成本、资源、网络与脱敏策略。
- `internal/credential/`：凭据加解密和秘密存储边界。
- `internal/artifact/`：短期结果制品存储。
- `internal/audit/`：完整且脱敏的审计记录。

Handler 只处理 HTTP 映射，Policy 不依赖 Gin。所有 Explain、Execute 和 Cancel 操作都必须传播 `context.Context`。当前 Go 文件仅包含用途注释。
