// 用途：定义可信内部服务传递的用户与工作区授权上下文声明。
package auth

import "github.com/golang-jwt/jwt/v5"

type Claims struct {
	Type         string `json:"type"`
	ActorID      string `json:"actor_id"`
	WorkspaceID  string `json:"workspace_id"`
	DatasourceID string `json:"datasource_id"`
	jwt.RegisteredClaims
}
