// Package repository 定义网关访问的数据读取接口。
package repository

type Authorizer interface {
	// TODO: 判断用户是否仍是指定 workspace 的成员，以及是否拥有所需角色。
	Authorize(workspaceID string, userID string, action string) error
}
