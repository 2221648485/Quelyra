// Package policy 负责在真实数据库执行前强制安全规则。
package policy

type ValidationResult struct {
	NormalizedSQL string
}

func ValidateReadOnlySQL(sql string, limit int) (ValidationResult, error) {
	// TODO: 基于 SQL AST 拒绝写操作、多语句、跨数据源访问和超出限制的查询。
	// TODO: 后续在这里接入已确认语义模型中的敏感列/禁止列策略。
	panic("待实现：校验只读 SQL")
}
