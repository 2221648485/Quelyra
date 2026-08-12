// 用途：加载并校验以 QUELYRA_ 开头的网关运行配置。
package config

import (
	"errors"
	"fmt"
	"log/slog"
	"os"
	"strings"

	"github.com/spf13/viper"
)

const defaultEnv = "dev"

type Config struct {
	App      AppConfig      `mapstructure:"app"`
	Database DatabaseConfig `mapstructure:"postgres"`
	Redis    RedisConfig    `mapstructure:"redis"`
}

type RedisConfig struct {
	Addr     string `mapstructure:"addr"`
	Password string `mapstructure:"password"`
	DB       int    `mapstructure:"db"`
}

// HTTP配置
type AppConfig struct {
	Env  string `mapstructure:"env"`
	Port string `mapstructure:"port"`
}

// 数据库配置
type DatabaseConfig struct {
	DSN          string `mapstructure:"dsn"`
	MaxOpenConns int    `mapstructure:"max_open_conns"`
	MaxIdleConns int    `mapstructure:"max_idle_conns"`
}

// Load 根据 APP_ENV 或 GO_ENV 加载对应配置文件。
func Load() Config {
	path := FilePath(Env())
	cfg, err := LoadFromFile(path)
	if err != nil {
		slog.Error("failed to load config", "path", path, "error", err)
	}
	return cfg
}

// Env 返回当前运行环境，默认 dev。
func Env() string {
	env := strings.TrimSpace(os.Getenv("APP_ENV"))
	if env == "" {
		return defaultEnv
	}
	return strings.ToLower(env)
}

// FilePath 根据环境名生成配置文件路径。
func FilePath(env string) string {
	env = strings.TrimSpace(strings.ToLower(env))
	return fmt.Sprintf("configs/config.%s.yaml", env)
}

// LoadFromFile 从指定 yaml 文件加载配置。
func LoadFromFile(path string) (Config, error) {
	v := newViper()
	v.SetConfigFile(path)

	if err := v.ReadInConfig(); err != nil {
		var notFound viper.ConfigFileNotFoundError
		if !errors.As(err, &notFound) && !os.IsNotExist(err) {
			return Config{}, err
		}
	}

	var cfg Config
	if err := v.Unmarshal(&cfg); err != nil {
		return Config{}, err
	}
	return cfg, nil
}

func newViper() *viper.Viper {
	v := viper.New()
	v.SetConfigType("yaml")
	return v
}
