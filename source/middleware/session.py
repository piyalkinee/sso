from fastapi import Request
from loguru import logger

from source.schemas import middleware


async def _session(request: Request = None) -> middleware.Session:
    logger.info(f"Setup session {request}")
    return middleware.Session(request=request)
