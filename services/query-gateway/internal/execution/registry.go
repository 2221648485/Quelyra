// Package execution 维护异步查询任务的状态。
package execution

type Registry interface {
	// TODO: 创建任务、写入状态、保存结果引用；大结果应只保存对象存储引用。
	Create(jobID string) error
	// TODO: 让前端安全地轮询自己的查询状态。
	Get(jobID string) (any, error)
}
