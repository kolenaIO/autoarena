from fastapi import FastAPI
from autostack.api.router import router

API_V1_STR = "/api/v1"
app = FastAPI(
    title="autostack",
    openapi_url=f"/{API_V1_STR}/openapi.json",
    docs_url=f"/{API_V1_STR}/docs",
)
app.include_router(router(), prefix=API_V1_STR)
