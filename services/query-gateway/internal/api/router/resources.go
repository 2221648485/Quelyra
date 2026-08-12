package router

import (
	"context"
	"log/slog"
	"query-gateway/internal/config"
	"query-gateway/internal/connector/postgres"
	"query-gateway/internal/connector/redis"

	redisclient "github.com/redis/go-redis/v9"
	"gorm.io/gorm"
)

type Resources struct {
	DB    *gorm.DB
	Redis *redisclient.Client
}

// 初始化系统资源
func InitResources(ctx context.Context, cfg config.Config) Resources {
	// 初始化postgres
	resources := Resources{}
	DB, err := postgres.New(cfg.Database)
	if err != nil {
		slog.ErrorContext(ctx, "failed to connect database", "error", err)
	}
	resources.DB = DB
	// 初始化redis
	redisClient, err := redis.New(ctx, cfg.Redis)
	if err != nil {
		slog.ErrorContext(ctx, "failed to connect redis", "error", err)
	}
	resources.Redis = redisClient
	return resources
}

func (r *Resources) Close() {
	if err := postgres.Close(r.DB); err != nil {
		slog.Error("app resource postgres close failed", "error", err)
	}
	if err := redis.Close(r.Redis); err != nil {
		slog.Error("app resource redis close failed", "error", err)
	}
}
