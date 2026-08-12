package redis

import (
	"context"
	"query-gateway/internal/config"

	"github.com/redis/go-redis/v9"
)

// New 创建 Redis 客户端，并通过 Ping 确认 Redis 当前可用。
func New(ctx context.Context, cfg config.RedisConfig) (*redis.Client, error) {
	client := redis.NewClient(&redis.Options{
		Addr:     cfg.Addr,
		Password: cfg.Password,
		DB:       cfg.DB,
	})
	if err := client.Ping(ctx).Err(); err != nil {
		_ = client.Close()
		return nil, err
	}
	return client, nil
}

// Close 关闭 Redis 客户端。
func Close(client *redis.Client) error {
	if client == nil {
		return nil
	}
	return client.Close()
}
