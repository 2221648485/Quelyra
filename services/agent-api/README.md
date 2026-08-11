# Python Agent API

该服务承载 Quelyra 的控制面和智能编排能力，主要包括 FastAPI 公共接口、LangGraph 分析与 Onboarding 工作流、持久化后台任务、语义上下文、模型适配和 Agent 评测。

## 目录职责

- `entrypoints/`：API 与 Worker 独立进程入口。
- `api/`：HTTP 路由、依赖和错误映射。
- `domain/`：不依赖 FastAPI、LangGraph 或 ORM 的领域模型。
- `graphs/`：状态、节点和条件路由组成的显式工作流。
- `services/`：被 API 和 Graph 调用的应用能力。
- `clients/`：Go Gateway 与模型提供商适配器。
- `repositories/`：平台元数据持久化接口与实现。
- `jobs/`：可租约、可恢复的后台任务。
- `prompts/`：版本化提示词模板。

Graph Node 不直接访问数据库或 HTTP；外部交互必须经由 Service、Client 或 Repository。当前文件仅用于固定结构，尚未加入实现代码。
