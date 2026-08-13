// 用途：在请求上下文中安全传递已验证的内部授权信息。
package auth

import "github.com/gin-gonic/gin"

const claimsKey = "service_claims"

func Get(c *gin.Context) (*Claims, bool) {
	claims, ok := c.Get(claimsKey)
	if !ok {
		return nil, false
	}
	return claims.(*Claims), true
}

func Set(c *gin.Context, claims *Claims) {
	c.Set(claimsKey, claims)
}
