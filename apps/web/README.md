# Quelyra Web

该应用是基于 Vue 3、Vite 和 TypeScript 的数据分析工作台，负责数据源接入、语义模型审核、多轮分析、结果图表和审计记录展示。

## 目录职责

- `api/`：类型化 HTTP 客户端。
- `components/`：跨业务功能复用的展示组件。
- `features/`：Onboarding、对话、查询结果、语义模型和治理等完整业务能力。
- `views/`：路由级页面组合。
- `stores/`：跨页面共享的 Pinia 状态。
- `types/`：生成类型的出口与前端专用契约。
- `styles/`：设计令牌和全局基础样式。

`package.json` 与 `tsconfig` 当前保留合法空对象，用于固定文件位置；开始实现时再由 Vue 官方工具链写入真实配置。
