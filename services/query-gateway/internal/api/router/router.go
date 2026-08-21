// Package router 组装 Query Gateway 的 HTTP 路由和请求边界。
package router

// App 聚合路由所需依赖。
// 实现提示：放入 Config、Verifier、凭据仓储、授权仓储、Connector 注册表、策略、
// 执行注册表和审计器；handler 不应自行创建这些基础设施对象。
type App struct{}

// Repository 表示 Gateway 查询工作区和数据源授权所需的最小存储接口。
type Repository interface{}

type baseRequest struct{}
type queryRequest struct{}

// New 创建路由。
// 实现顺序：注册 health → 安装 request ID/recovery/logging → 安装服务 token 验证 →
// 注册连接测试、introspect、explain、execute 路由；所有业务路由必须经过 bound 校验。
func New(app *App) any { panic("待实现：构建 Gateway 路由") }

func authorize(app *App) any { panic("待实现：创建认证中间件") }
func requestID() any         { panic("待实现：创建请求 ID 中间件") }
func recovery() any          { panic("待实现：创建恢复中间件") }
func terminalAudit() any     { panic("待实现：创建审计中间件") }

// bind 只绑定并校验请求格式，不做授权。
func bind(context any, value any) bool { panic("待实现：绑定并校验请求") }

// bound 将请求体资源范围与服务 token claims 精确比较。
func bound(context any, request baseRequest) bool { panic("待实现：校验请求资源边界") }

// 以下 handler 实现提示：先 bind → bound → 加载已授权数据源 → 校验策略 → 调用 connector → 审计 → 输出脱敏响应。
func load(context any, app *App, request baseRequest) (any, any, string, bool) {
	panic("待实现：加载受控数据源")
}
func handleBase(context any, app *App, action string, handler any) {
	panic("待实现：处理基础数据源操作")
}
func validateQuery(context any, app *App, request queryRequest, datasource any) bool {
	panic("待实现：校验查询")
}
func binding(request queryRequest) any    { panic("待实现：构建 explain token 绑定") }
func handleExplain(context any, app *App) { panic("待实现：处理 explain") }
func handleExecute(context any, app *App) { panic("待实现：处理只读执行") }
func audit(context any, request baseRequest, action string, startedAt any, rows int, sqlHash string, err error) {
	panic("待实现：写入审计事件")
}
func newID() string { panic("待实现：生成执行 ID") }
