// 用途：组装依赖并启动 Go 查询网关进程。
package main

import "query-gateway/internal/api/router"

func main() {
	app := router.NewRouter()
	if err := app.Run(); err != nil {
		panic(err)
	}
}
