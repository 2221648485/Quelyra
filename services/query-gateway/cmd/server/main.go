// 用途：组装依赖并启动 Go 查询网关进程。
package main

import (
	"context"
	"log/slog"
	"query-gateway/internal/api"
	"query-gateway/internal/config"
	"query-gateway/internal/telemetry"
)

func main() {
	cfg := config.Load()
	Init(cfg)
	app := api.NewRouter()
	if err := app.Run(":" + cfg.App.Port); err != nil {
		slog.Error("server stopped with error", "error", err)
	}
}

// 相关资源初始化
func Init(cfg config.Config) {
	telemetry.InitLogger(config.Env())

	slog.Info("配置文件加载成功...")
	resources := api.InitResources(context.Background(), cfg)
	defer resources.Close()
}
