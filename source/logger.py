import logging
import sys

import starlette.requests
from loguru import logger

from source.settings import settings


class AsyncLoguruLogger:
    def __init__(self, config):
        self.config = config
    async def info(self, message, *args, **kwargs):
        logger.info(message)

    async def warning(self, message, *args, **kwargs):
        logger.warning(message)

    async def error(self, message, *args, **kwargs):
        logger.error(message)

    async def critical(self, message, *args, **kwargs):
        logger.critical(message)

    async def debug(self, message, *args, **kwargs):
        logger.debug(message)

    async def access(self, scope, response, duration):
        logger.info(f"{scope['method']} {scope['path']} completed in {duration:.2f}s with status {response['status']}")


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


async def logging_dependency(request: starlette.requests.Request):
    params = [f"{name}: {value}" for name, value in request.path_params.items()]
    headers = [f"{name}: {value}" for name, value in request.headers.items()]
    logger.debug(f"{request.method} {request.url}")
    logger.debug(f"Params: {params}")
    logger.debug(f"Headers: {headers}")


def set_logging():  # sourcery skip: avoid-builtin-shadow
    intercept_handler = InterceptHandler()
    logging.root.setLevel(settings.log_level)
    seen = set()
    for name in [
        *logging.root.manager.loggerDict.keys(),
        "gunicorn",
        "gunicorn.access",
        "gunicorn.error",
        "uvicorn",
        "uvicorn.access",
        "uvicorn.error",
        "hypercorn",
        "hypercorn.access",
        "hypercorn.error",
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