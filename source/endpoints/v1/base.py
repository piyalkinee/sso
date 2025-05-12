from fastapi import APIRouter
from loguru import logger

from ...commands import access as caccess
from ...middleware import route
from ...middleware import session as mvsession
from ...schemas import input as sinput
from ...schemas import middleware as smiddleware
from ...schemas import output as soutput

router: APIRouter = APIRouter()
middleware_router = lambda method, path, **kwargs: route(router, method, path, **kwargs)


@middleware_router(
    method="post",
    path="/",
    summary=f"Get access and refresh tokens",
    response_model=soutput.AccessOutput,
    requires_auth=False,
    permissions=[],
)
async def base(
    data: sinput.BaseInput, session: smiddleware.Session = mvsession
) -> soutput.AccessOutput:
    """Description"""

    logger.debug("In endpoint [base]")
    return await caccess.base(database=session.db, data=data)
