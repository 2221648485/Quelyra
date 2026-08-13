package api

// 用途：注册版本化内部 HTTP 路由和中间件。

import (
	"query-gateway/internal/middleware"
	"query-gateway/internal/response"

	"github.com/gin-gonic/gin"
)

func NewRouter() *gin.Engine {
	router := gin.Default()
	router.Use(middleware.RequestLog(), middleware.RequestID(), middleware.TerminalAudit(), middleware.Recovery())
	ctx := NewAppContext()
	RegisterRouter(router, ctx)
	return router
}

func RegisterRouter(router *gin.Engine, ctx *AppContext) {
	r := router.Group("/internal/v1", middleware.Authorize(ctx.verifier))
	r.GET("/healthz", func(c *gin.Context) {
		response.OK(c, gin.H{"status": "ok1"})
	})
}
