# 架构文档

本目录保存系统上下文、容器、组件、身份认证、多租户授权、关键时序和部署架构等说明。身份架构必须区分浏览器 Access Token 与内部 Service Token，并明确 Agent API 和 Query Gateway 各自的授权边界。架构图应与实际实现保持同步，重要取舍应在 `docs/adr` 中记录原因。
