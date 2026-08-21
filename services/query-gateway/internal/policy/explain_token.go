package policy

type ExplainTokenClaims struct {
	WorkspaceID  string
	DatasourceID string
	SQLHash      string
}

func SignExplainToken(claims ExplainTokenClaims) (string, error) {
	// TODO: 签发短期、绑定工作区/数据源/SQL 哈希的 explain 令牌。
	panic("待实现：签发 explain token")
}

func VerifyExplainToken(token string) (ExplainTokenClaims, error) {
	// TODO: 验证签名、有效期、工作区、数据源和 SQL 哈希，防止换 SQL 执行。
	panic("待实现：验证 explain token")
}
