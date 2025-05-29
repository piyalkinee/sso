import asyncio

from loguru import logger
from hypercorn.asyncio import serve
from hypercorn.config import Config

from source import app

from source import settings
from source.logger import AsyncLoguruLogger


def run():
    config = Config()
    config.bind = [f"{settings.api.host}:{settings.api.port}"]
    config.workers = settings.workers
    config.loglevel = settings.log_level.lower()
    config.use_reloader = settings.debug
    config.logger_class = AsyncLoguruLogger
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
