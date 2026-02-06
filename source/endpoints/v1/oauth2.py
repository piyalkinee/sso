from loguru import logger
from fastapi import APIRouter

from ...commands import auth as cauth
from ...schemas import oauth2 as oauth2schema, output as soutput, middleware as smiddleware
from ...middleware import session as mvsession, route

router: APIRouter = APIRouter()
middleware_router = lambda method, path, **kwargs: route(router, method, path, **kwargs)


@middleware_router(
    method="post",
    path="/login",
    summary="Login with OAuth2 (Google/Apple)",
    response_model=soutput.AccessOutput,
    requires_auth=False,
    permissions=[]
)
async def oauth2_login(
        data: oauth2schema.OAuth2Input,
        session: smiddleware.Session = mvsession
) -> soutput.AccessOutput:
    """ 
    Exchange Google/Apple identity token for Application Access/Refresh Tokens.
    Creates user if email not found.
    """

    logger.debug(f"In endpoint [oauth2_login] provider={data.provider}")
    return await cauth.login_oauth2(
        database=session.db,
        data=data
    )
