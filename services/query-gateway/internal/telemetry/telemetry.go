// Package telemetry 负责日志、指标和链路追踪。
package telemetry

type Recorder interface {
	// TODO: 记录耗时、失败率、队列积压和模型/数据库调用指标，不记录 SQL 参数或凭据。
	Record(name string, value float64)
}
