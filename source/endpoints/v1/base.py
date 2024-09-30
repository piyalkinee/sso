from loguru import logger
from fastapi import APIRouter

from ...commands import access as caccess
from ...schemas import input as sinput, output as soutput, middleware as smiddleware
from ...middleware import session as mvsession, route

router: APIRouter = APIRouter()
middleware_router = lambda method, path, **kwargs: route(router, method, path, **kwargs)


@middleware_router(
    method="post",
    path="/",
    summary=f"Get access and refresh tokens",
    response_model=soutput.AccessOutput,
    requires_auth=False,
    permissions=[]
)
async def base(
        data: sinput.BaseInput,
        session: smiddleware.Session = mvsession
) -> soutput.AccessOutput:
    """ Description """

    logger.debug("In endpoint [base]")
    return await caccess.base(
        database=session.db,
        data=data
    )
