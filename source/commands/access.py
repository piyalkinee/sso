from datetime import datetime, timedelta

from loguru import logger
from databases.core import Connection

from ..model.queries import users as qusers, tokens as qtokens, projects as qprojects
from ..schemas import input as sinput, output as soutput, tokens as saccess, tokens as stokens, users as susers
from ..core import salt, access_tokens
from ..configuration import conf
from ..exceptions import auth, access


async def base(
        data: sinput.BaseInput,
        database: Connection
) -> soutput.AccessOutput:
    logger.debug("Get user data use email")
    user_data: soutput.UserFromEmailOutput = await qusers.get_by_email(
        database=database,
        email=data.email
    )
    logger.debug("Verify password")
    verify_result: bool = await salt.verify_password(
        input_password=data.password,
        password_hash=user_data.hash,
        password_salt=user_data.salt
    )
    if verify_result is False:
        raise access.InvalidPassword
    logger.debug("Get user")
    full_user_data: susers.User = await qusers.get_data_for_token(
        database=database,
        id=user_data.id
    )

    project_id_str = None
    if data.project_id:
        if await qprojects.exists(database=database, project_id=data.project_id):
            await qprojects.link_user(database=database, user_id=user_data.id, project_id=data.project_id)
            project_id_str = str(data.project_id)
        else:
            logger.warning(f"project_id={data.project_id} not found, skipping link")

    user_projects = await qprojects.get_user_project_names(database=database, user_id=user_data.id)

    logger.debug("Generate tokens")
    access_token: str = access_tokens.generate_token(
        type="access",
        data={**full_user_data.model_dump(), "project_id": project_id_str, "projects": user_projects},
        ttl=conf['access_security']['access_token_ttl']
    )
    refresh_token = access_tokens.generate_token(
        type="refresh",
        data={
            "id": user_data.id,
            "project_id": project_id_str,
        },
        ttl=conf['access_security']['refresh_token_ttl']
    )
    logger.debug("Save token in base")
    await qtokens.create(
        database=database,
        token=stokens.TokenCreate(
            access_token=access_token,
            refresh_token=refresh_token,
            valid_to=datetime.today() + timedelta(minutes=conf['access_security']['access_token_ttl']),
            user_id=user_data.id,
        ))
    return soutput.AccessOutput(
        tokens=soutput.TokensOutput(
            access=access_token,
            refresh=refresh_token
        )
    )


async def refresh(
        database: Connection = None,
        data: saccess.RefreshInput = None
) -> saccess.RefreshTokenOutput:
    logger.debug("In command [refresh]")

    try:
        decoded = access_tokens.decode_token(token=data.refresh_token)
    except Exception as e:
        raise auth.InvalidCredentialsError from e

    logger.debug("Get user")
    full_user_data: susers.User = await qusers.get_data_for_token(
        database=database,
        id=decoded["id"]
    )
    project_id_str = decoded.get("project_id")
    user_projects = await qprojects.get_user_project_names(database=database, user_id=decoded["id"])
    new_access_token = access_tokens.generate_token(
        type="access",
        data={**full_user_data.model_dump(), "project_id": project_id_str, "projects": user_projects},
        ttl=conf['access_security']['access_token_ttl']
    )

    try:
        await qtokens.create(
            database=database,
            token=stokens.TokenCreate(
                access_token=new_access_token,
                refresh_token=data.refresh_token,
                valid_to=datetime.today() + timedelta(minutes=conf['access_security']['access_token_ttl']),
                user_id=decoded["id"]
            )
        )
    except auth.TokenNotFound:
        raise

    return saccess.RefreshTokenOutput(access_token=new_access_token)


async def revoke(database: Connection = None, refresh_token: str = None) -> saccess.RevokeTokenOutput:
    logger.debug("In command [revoke]")
    try:
        return await qtokens.token_revoke(database=database, refresh_token=refresh_token)
    except auth.TokenNotFound as e:
        raise auth.InvalidCredentialsError from e
