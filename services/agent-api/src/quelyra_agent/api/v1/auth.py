# 用途：提供身份认证和当前用户相关的 HTTP 接口。

from fastapi import FastAPI
app = FastAPI()

@app.get("/healthz")
def healthz():
    return {"status": "ok"}