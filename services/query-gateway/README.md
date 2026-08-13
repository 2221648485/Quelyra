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

Handler 只处理 HTTP 映射，Policy 不依赖 Gin。所有 Explain、Execute 和 Cancel 操作都必须传播 `context.Context`。当前处于骨架与基础能力建设阶段，后续将按照上述边界逐步补充 Connector、策略校验与受控执行能力。

## Connector边界

Gateway从平台元数据库读取权威DataSource Engine，通过Connector Registry选择实现：MySQL使用`go-sql-driver/mysql`，PostgreSQL使用`pgx`。Connector不只封装`sql.Open`，还分别负责元数据扫描、EXPLAIN、只读事务、Timeout、Cancel、类型归一化和Driver错误分类。

请求中的Dialect必须与DataSource Engine映射一致；不一致返回`QUERY_DIALECT_MISMATCH`。完整SQL AST校验由Python SQLGlot完成，Gateway不重复实现一套多方言解析器，但仍通过只读账号、禁用多语句、Explain Token和资源限制形成独立执行防线。
