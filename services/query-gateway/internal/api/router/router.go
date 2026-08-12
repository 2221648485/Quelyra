package router

// 用途：注册版本化内部 HTTP 路由和中间件。

import (
	"query-gateway/internal/response"

	"github.com/gin-gonic/gin"
)

func NewRouter() *gin.Engine {
	router := gin.Default()
	RegisterRouter(router)
	return router
}

func RegisterRouter(router *gin.Engine) {
	router.GET("/healthz", func(c *gin.Context) {
		response.OK(c, gin.H{"status": "ok"})
	})
}
