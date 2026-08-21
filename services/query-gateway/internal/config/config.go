// Package config 负责读取网关运行配置。
package config

type Config struct {
	// TODO: 定义监听地址、数据库 DSN、JWT 公钥、加密密钥和资源上限。
}

func Load() (Config, error) {
	// TODO: 从环境变量读取配置，校验必填项，并拒绝不安全的默认值。
	panic("待实现：加载并校验网关配置")
}
