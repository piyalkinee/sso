from fastapi import Request, Depends
from loguru import logger

from ..schemas import middleware
from ..schemas import users as susers


async def _session(
        request: Request = None
) -> middleware.Session:
    logger.info(f"Setup session {request}")
    return middleware.Session(request=request)


session = Depends(_session)
