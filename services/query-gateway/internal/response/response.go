package response

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

type Body struct {
	Code    int         `json:"code"`
	Message string      `json:"message"`
	Data    interface{} `json:"data,omitempty"`
}

func RequestID(c *gin.Context) string {
	v, _ := c.Get("request_id")
	s, _ := v.(string)
	return s
}

func OK(c *gin.Context, data interface{}) {
	c.JSON(http.StatusOK, Body{
		Code:    0,
		Message: "success",
		Data:    data,
	})
}

func Error(c *gin.Context, code int, message string) {
	c.Set("error_code", code)
	c.AbortWithStatusJSON(code, Body{
		Code:    code,
		Message: message,
		Data:    "RequestID:" + RequestID(c),
	})
}
