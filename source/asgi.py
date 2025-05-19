import asyncio
import logging
import signal
import sys

import uvicorn.server
from loguru import logger

from hypercorn.asyncio import serve
from hypercorn.config import Config

from source import app

from . import settings


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


def setup_logging(level="DEBUG"):
    # Устанавливаем уровень root логгера
    logging.root.handlers = []
    logging.root.setLevel(level)

    intercept_handler = InterceptHandler()

    targets = [
        "uvicorn",
        "uvicorn.access",
        "uvicorn.error",
        "hypercorn",
        "hypercorn.access",
        "hypercorn.error",
        "asyncio",
    ]

    for name in targets:
        logging_logger = logging.getLogger(name)
        logging_logger.handlers = [intercept_handler]
        logging_logger.propagate = False  # чтобы не было дублей
        logging_logger.setLevel(level)

    logger.configure(
        handlers=[{
            "sink": sys.stdout,
            "format": (
                "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                "<level>{level: <8}</level> | {process} | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                "<level>{message}</level>"
            ),
            "level": level
        }]
    )



def run():
    setup_logging(settings.log_level.upper())

    config = Config()
    config.bind = [f"{settings.api.host}:{settings.api.port}"]
    config.workers = settings.workers
    config.loglevel = settings.log_level.lower()
    config.use_reloader = settings.debug
    config.errorlog = "-"
    config.accesslog = "-"

    # QUIC (если нужны HTTP/3)
    # if settings.tls_enabled:
    #     config.certfile = settings.certfile
    #     config.keyfile = settings.keyfile
    #     config.quic_bind = [f"{settings.api.host}:{settings.api.port}"]
    #     config.alpn_protocols = ["h3", "http/1.1"]

    logger.info("🚀 Starting Hypercorn server...")
    asyncio.run(serve(app, config))
