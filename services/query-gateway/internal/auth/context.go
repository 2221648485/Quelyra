// Package auth 提供认证中间件与后续 handler 之间的上下文传递。
package auth

const claimsKey = "service_claims"

// Set 将已验证的 claims 放入请求上下文。
// 实现提示：只能由认证中间件调用；不要将原始 token 放入 context 或日志。
func Set(context any, claims *Claims) {
	panic("待实现：写入已验证的服务声明")
}

// Get 读取认证中间件写入的 claims。
// 实现提示：类型断言失败与缺失都视为未认证，handler 不应继续执行。
func Get(context any) (*Claims, bool) {
	panic("待实现：读取已验证的服务声明")
}
