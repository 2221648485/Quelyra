// 用途：生成并传播请求标识和链路关联标识。

package middleware

import (
	"crypto/rand"
	"encoding/hex"
	"log/slog"
	"query-gateway/internal/auth"
	"query-gateway/internal/response"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
)

// RequestLog 记录简洁请求日志，主要用于观察调度器实际请求了哪些接口。
func RequestLog() gin.HandlerFunc {
	return func(c *gin.Context) {
		start := time.Now()
		c.Next()

		slog.Info("http request",
			"method", c.Request.Method,
			"path", c.FullPath(),
			"raw_path", c.Request.URL.Path,
			"query", c.Request.URL.RawQuery,
			"status", c.Writer.Status(),
			"latency_ms", time.Since(start).Milliseconds(),
			"client_ip", c.ClientIP(),
		)
	}
}

// 接口审计日志
func TerminalAudit() gin.HandlerFunc {
	return func(c *gin.Context) {
		start := time.Now()
		c.Next()
		attrs := []any{"request_id", response.RequestID(c), "action", c.FullPath(), "outcome", "success", "duration_ms", time.Since(start).Milliseconds()}
		if c.Writer.Status() >= 400 {
			attrs[5] = "failure"
			if code, ok := c.Get("error_code"); ok {
				attrs = append(attrs, "error_code", code)
			}
		}
		if cl, ok := auth.Get(c); ok {
			attrs = append(attrs, "actor_id", cl.ActorID, "workspace_id", cl.WorkspaceID, "datasource_id", cl.DatasourceID)
		}
		if hash, ok := c.Get("sql_hash"); ok {
			attrs = append(attrs, "sql_hash", hash)
		}
		slog.InfoContext(c.Request.Context(), "gateway request audit", attrs...)
	}
}

// 生成链路追踪ID
func RequestID() gin.HandlerFunc {
	return func(c *gin.Context) {
		id := strings.TrimSpace(c.GetHeader("X-Request-ID"))
		if id == "" || len(id) > 128 {
			b := make([]byte, 16)
			_, _ = rand.Read(b)
			id = hex.EncodeToString(b)
		}
		c.Set("request_id", id)
		c.Header("X-Request-ID", id)
		c.Next()
	}
}
