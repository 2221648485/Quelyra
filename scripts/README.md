# 开发脚本

`build.ps1` 用于构建、启动、查看和停止 Quelyra 本地开发环境。

无参数运行时显示交互菜单：

```powershell
.\scripts\build.ps1
```

也可以直接指定组件：

```powershell
.\scripts\build.ps1 agent
.\scripts\build.ps1 gateway
.\scripts\build.ps1 web
.\scripts\build.ps1 backend
.\scripts\build.ps1 all
.\scripts\build.ps1 infra
.\scripts\build.ps1 status
.\scripts\build.ps1 down
```

`clean` 会清理容器和本地构建的 Quelyra 应用镜像，但不会删除 `D:\data\quelyra` 中的 PostgreSQL 与 Redis 数据，并且需要输入 `CLEAN` 二次确认。
