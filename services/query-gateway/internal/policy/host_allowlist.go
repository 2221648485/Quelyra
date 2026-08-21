// Package policy 定义数据源网络访问策略。
package policy

// HostPolicy 保存允许连接的数据源 CIDR。
// 实现提示：生产环境应优先采用显式 allowlist；不能仅依靠“不是私网”的默认策略。
type HostPolicy struct{}

// NewHostPolicy 解析并验证管理员配置的 CIDR 列表。
func NewHostPolicy(cidrs []string) (*HostPolicy, error) {
	panic("待实现：创建数据源主机白名单")
}

// Allowed 判断解析后的 IP 是否可连接。
// 实现提示：拒绝 loopback、private、link-local、unspecified、multicast；还需防 DNS
// rebinding，实际连接应使用已校验的 IP 而不是再次解析 hostname。
func (p *HostPolicy) Allowed(ip any) bool { panic("待实现：校验数据源 IP") }
