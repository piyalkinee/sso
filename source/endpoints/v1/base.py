from fastapi import APIRouter
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from source.commands import access
from source.middleware import route
from source.middleware.dependencies import database, session
from source.schemas import input, middleware, output

router: APIRouter = APIRouter()
middleware_router = lambda method, path, **kwargs: route(router, method, path, **kwargs)


@middleware_router(
    method="post",
    path="/",
    summary=f"Get access and refresh tokens",
    response_model=output.AccessOutput,
    requires_auth=False,
    permissions=[],
)
async def base(
    data: input.BaseInput, ss: middleware.Session = session, db: AsyncSession = database
) -> output.AccessOutput | None:
    """Description"""
    logger.debug("In endpoint [base]")
    return await access.base(database=db, data=data)
