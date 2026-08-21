// Package connector 抽象不同数据库的统一访问能力。
package connector

type Connector interface {
	// TODO: 连接测试不得泄露凭据或完整连接串。
	TestConnection() error
	// TODO: 返回经过标准化的表、列、类型和关系元数据。
	Introspect() (any, error)
	// TODO: 只执行 EXPLAIN，不实际读取业务数据。
	Explain(sql string) (any, error)
	// TODO: 执行已通过网关策略校验的只读 SQL。
	ExecuteReadOnly(sql string, limit int) (any, error)
}
