import importlib.metadata
import os

import fastapi
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from setproctitle import setproctitle

from source.core.database.postgres import check_db_connection
from source.endpoints import router
from source.exceptions.api import exception_handlers
from source.logger import logging_dependency, set_logging
from source.settings import settings

_app = None

VERSION = importlib.metadata.version("source")


def create_app():
    global _app
    if _app is not None:
        return _app

    async def lifespan(app: fastapi.FastAPI):
        setproctitle("sso:master")
        logger.warning(f"process {os.getpid()}")
        set_logging()
        try:
            await check_db_connection()
            logger.info("Connection to the database is established")
            yield
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise e

    _app = fastapi.FastAPI(
        title="Single SignOn API",
        debug=settings.debug,
        version=VERSION,
        docs_url=f"{settings.http.path_prefix}/docs",
        redoc_url=f"{settings.http.path_prefix}/redoc",
        openapi_url=f"{settings.http.path_prefix}/openapi.json",
        exception_handlers=exception_handlers,
        lifespan=lifespan,
    )

    _app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    _app.include_router(
        router,
        prefix=settings.http.path_prefix,
        dependencies=[fastapi.Depends(logging_dependency)],
    )

    return _app
