// Package auth 定义 agent-api 调用 Gateway 时携带的服务身份声明。
package auth

// Claims 只保留 Gateway 做二次授权所需的最小身份范围。
//
// 实现提示：实际版本嵌入 JWT RegisteredClaims，并验证 token type、issuer、audience、
// subject、过期时间和以下三个资源绑定字段；不要相信请求体自己声称的工作区或用户。
type Claims struct {
	Type         string
	ActorID      string
	WorkspaceID  string
	DatasourceID string
}

// Bind 校验服务令牌是否与当前请求的资源范围一致。
//
// 实现顺序：检查 claims 非空 → 检查请求字段非空 → 精确比较 workspace、actor、
// datasource 三项 → 任一不一致返回通用授权错误。
func (c *Claims) Bind(workspace, actor, datasource string) error {
	panic("待实现：绑定并校验服务令牌资源范围")
}
