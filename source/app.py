import importlib.metadata
import logging
import os
import sys

import fastapi
import starlette.requests
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from setproctitle import setproctitle

from source.core.database.postgres import check_db_connection
from source.settings import settings

from .endpoints import router
from .exceptions.api import exception_handlers

_app = None

VERSION = importlib.metadata.version("source")


async def logging_dependency(request: starlette.requests.Request):
    params = [f"{name}: {value}" for name, value in request.path_params.items()]
    headers = [f"{name}: {value}" for name, value in request.headers.items()]
    logger.debug(f"{request.method} {request.url}")
    logger.debug(f"Params: {params}")
    logger.debug(f"Headers: {headers}")


class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def set_logging():  # sourcery skip: avoid-builtin-shadow
    intercept_handler = InterceptHandler()
    logging.root.setLevel(settings.log_level)
    seen = set()
    for name in [
        *logging.root.manager.loggerDict.keys(),
        "gunicorn",
        "gunicorn.access",
        "gunicorn.error",
    ]:
        if name not in seen:
            seen.add(name.split(".")[0])
            logging.getLogger(name).handlers = [intercept_handler]

    _format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | {process} |"
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:"
        "<cyan>{line}</cyan> - <level>{message}</level>"
    )
    logger.configure(handlers=[{"sink": sys.stdout, "serialize": 0, "format": _format}])


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
