// Package response 统一网关对外返回格式。
package response

type ErrorBody struct {
	Code      string
	Message   string
	RequestID string
}

// TODO: 实现成功响应、业务错误和内部错误的序列化；禁止把驱动错误原样返回客户端。
