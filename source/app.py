import os
import sys
import logging

import fastapi
import starlette.requests

from loguru import logger
from setproctitle import setproctitle
from fastapi.middleware.cors import CORSMiddleware

from . import configuration
from .endpoints import router
from .core.database import postgres
from .exceptions.api import exception_handlers

_app = None

current_directory = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_directory, '..'))
os.environ['PATH'] += os.pathsep + project_root

ROOT_DIR: str = os.environ['PATH'].split(":")[-1] + "/"

with open(ROOT_DIR + "VERSION_SSO") as f:
    VERSION = f.readlines()[0]


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
    logging.root.setLevel(configuration.conf['log_level'])
    seen = set()
    for name in [
        *logging.root.manager.loggerDict.keys(),
        "gunicorn",
        "gunicorn.access",
        "gunicorn.error"
    ]:
        if name not in seen:
            seen.add(name.split(".")[0])
            logging.getLogger(name).handlers = [intercept_handler]

    _format = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | " \
              "<level>{level: <8}</level> | {process} |" \
              "<cyan>{name}</cyan>:<cyan>{function}</cyan>:" \
              "<cyan>{line}</cyan> - <level>{message}</level>"
    logger.configure(handlers=[{"sink": sys.stdout, "serialize": 0, "format": _format}])


def create_app():
    global _app
    if _app is not None:
        return _app

    async def lifespan(app: fastapi.FastAPI):
        # Startup
        setproctitle("sso:master")
        logger.warning(f"process {os.getpid()}")
        set_logging()
        await postgres.connect()

        yield

        # Shutdown
        await postgres.disconnect()

    _app = fastapi.FastAPI(
        title="Single SignOn API",
        debug=configuration.conf['debug'],
        version=VERSION,
        docs_url=f"{configuration.conf['http']['path_prefix']}/docs",
        redoc_url=f"{configuration.conf['http']['path_prefix']}/redoc",
        openapi_url=f"{configuration.conf['http']['path_prefix']}/openapi.json",
        exception_handlers=exception_handlers,
        lifespan=lifespan
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
        prefix=configuration.conf['http']['path_prefix'],
        dependencies=[fastapi.Depends(logging_dependency)],
    )

    return _app
