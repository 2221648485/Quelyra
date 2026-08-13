// 用途：捕获服务异常，避免泄露凭据或查询数据。

package middleware

import (
	"query-gateway/internal/response"

	"github.com/gin-gonic/gin"
)

// 异常处理
func Recovery() gin.HandlerFunc {
	return gin.CustomRecovery(func(c *gin.Context, _ any) {
		response.Error(c, 500, "internal server error")
	})
}
