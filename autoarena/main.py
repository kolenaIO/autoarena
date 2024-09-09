from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from autoarena.api.router import router
from autoarena.log import initialize_logger
from autoarena.store.seed import setup_database
from autoarena.ui_router import ui_router

API_V1_STR = "/api/v1"


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    setup_database()
    logger.info("AutoArena ready")
    yield


def main() -> FastAPI:
    initialize_logger()

    app = FastAPI(
        title="AutoArena",
        lifespan=lifespan,
        openapi_url=f"/{API_V1_STR}/openapi.json",
        docs_url=f"/{API_V1_STR}/docs",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router(), prefix=API_V1_STR)
    app.include_router(ui_router())
    return app
