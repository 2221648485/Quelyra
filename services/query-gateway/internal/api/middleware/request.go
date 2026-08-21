// Package middleware 保存 Gateway 的 HTTP 横切中间件骨架。
package middleware

// RequestLog 创建请求日志中间件。
//
// 实现顺序：读取/生成 request ID → 记录方法、路径、状态码、耗时、workspace ID、
// datasource ID 和 SQL 哈希 → 禁止记录原始 SQL、查询参数、密码、token 或完整结果。
func RequestLog() any {
	panic("待实现：创建请求日志中间件")
}
