package auth

// Verifier 保存验证服务令牌所需的密钥及签发范围。
// 实现提示：生产中密钥来自受控配置或密钥管理服务，禁止在源码或日志中出现。
type Verifier struct {
	secret   []byte
	issuer   string
	audience string
}

// NewVerifier 构造令牌验证器。
// 实现提示：启动时拒绝空密钥、空 issuer/audience 和不支持的签名算法。
func NewVerifier(secret []byte, issuer, audience string) *Verifier {
	panic("待实现：构造服务令牌验证器")
}

// Verify 验证并解析服务令牌。
// 实现顺序：去除空白 → 限制为预期签名算法 → 验签 → 校验 issuer/audience/exp →
// 校验 type=service 与资源 claims → 返回最小化 Claims。
func (v *Verifier) Verify(raw string) (*Claims, error) {
	panic("待实现：验证服务令牌")
}
