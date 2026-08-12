from fastapi import FastAPI

from quelyra_agent.api.v1.router import api_router


def create_app() -> FastAPI:
    app = FastAPI(
        title = "Quelyra-agent-api"
    )
    app.include_router(
        api_router,
        prefix="/api/v1",
    )
    return app

app = create_app()
@app.get("/")
def root():
    return {"message": "Hello Quelyra"}