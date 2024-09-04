from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from autostack.api.router import router
from autostack.args import get_command_line_args
from autostack.log import initialize_logger
from autostack.store.seed import setup_database, seed_initial_battles
from autostack.ui_router import ui_router

args = get_command_line_args()
initialize_logger()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    setup_database()
    if args.battles_parquet is not None:
        seed_initial_battles(args.battles_parquet)
    logger.info("AutoStack ready")
    yield


API_V1_STR = "/api/v1"
app = FastAPI(
    title="AutoStack",
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
