from loguru import logger
from fastapi import APIRouter

from ...commands import auth as cauth
from ...schemas import oauth2 as oauth2schema, output as soutput, middleware as smiddleware, users as susers
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


@middleware_router(
    method="post",
    path="/link",
    summary="Link OAuth2 Provider (Google/Apple) to current account",
    response_model=susers.UserOAuth,
    requires_auth=True,
    permissions=[]
)
async def oauth2_link(
        data: oauth2schema.OAuth2Input,
        session: smiddleware.Session = mvsession
) -> susers.UserOAuth:
    """ 
    Link Google/Apple identity to the currently logged in user.
    """

    logger.debug(f"In endpoint [oauth2_link] provider={data.provider}, user_id={session.user.id}")
    return await cauth.link_oauth2(
        database=session.db,
        user_id=session.user.id,
        data=data
    )
