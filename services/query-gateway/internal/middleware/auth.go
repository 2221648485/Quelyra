// 用途：认证受信任的服务间请求。

package middleware

import (
	"query-gateway/internal/auth"
	"query-gateway/internal/response"
	"strings"

	"github.com/gin-gonic/gin"
)

func Authorize(v *auth.Verifier) gin.HandlerFunc {
	return func(c *gin.Context) {
		h := c.GetHeader("Authorization")
		if !strings.HasPrefix(h, "Bearer ") {
			response.Error(c, 401, "valid service token required")
			return
		}
		claims, err := v.Verify(strings.TrimSpace(strings.TrimPrefix(h, "Bearer ")))
		if err != nil {
			response.Error(c, 401, "valid service token required")
			return
		}
		auth.Set(c, claims)
		c.Next()
	}
}
