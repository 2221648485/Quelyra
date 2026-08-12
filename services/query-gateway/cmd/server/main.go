// 用途：组装依赖并启动 Go 查询网关进程。
package main

import (
	"context"
	"log/slog"
	"query-gateway/internal/api/router"
	"query-gateway/internal/config"
	"query-gateway/internal/telemetry"
)

func main() {
	Init()
	app := router.NewRouter()
	if err := app.Run(); err != nil {
		slog.Error("server stopped with error", "error", err)
	}
}

// 相关资源初始化
func Init() {
	telemetry.InitLogger(config.Env())
	cfg := config.Load()
	slog.Info("%s", cfg)
	resources := router.InitResources(context.Background(), cfg)
	defer resources.Close()
}
