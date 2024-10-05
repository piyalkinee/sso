from loguru import logger
from asyncpg import PostgresError

from databases.core import Connection
from ...exceptions.database import DatabaseError
from ...schemas import tokens as stokens
from ...exceptions.auth import TokenNotFound, TokenAlreadyStored


async def create(
        database: Connection = None,
        token: stokens.TokenCreate = None
) -> stokens.TokenGet:
    logger.debug("in model [token_create]")
    try:
        query = f"""
            INSERT INTO 
                access.tokens_info 
                (user_id, access_token, refresh_token)
            VALUES 
                (:user_id, :access_token, :refresh_token)
            RETURNING 
                *;
        """
        result = dict(await database.fetch_one(query,{
            "user_id": token.user_id,
            "access_token": token.access_token,
            "refresh_token": token.refresh_token
        }))
        return stokens.TokenGet(**result)
    except PostgresError as e:
        logger.debug(e)
        raise TokenAlreadyStored from e


async def revoke(
        database: Connection = None,
        refresh_token: str = None
) -> stokens.RevokeTokenOutput:
    logger.debug("In model [token_revoke]")
    try:
        logger.warning(refresh_token)
        query = """
            DELETE FROM 
                system.access_tokens
            WHERE 
                refresh_token = :refresh_token 
            AND 
                is_revoked = FALSE
            RETURNING 
                id;
        """
        revoked = await database.fetch_one(query, {
            'refresh_token': refresh_token
        })
        if revoked is None:
            raise TokenNotFound
        return stokens.RevokeTokenOutput()
    except PostgresError as e:
        logger.debug(e)
        raise DatabaseError from e


async def refresh(
        database: Connection = None,
        refresh_token: str = None,
        new_access_token: str = None
) -> stokens.TokenGet:
    logger.debug("In model [token_refresh]")
    try:
        query = """
            SELECT
                * 
            FROM
                system.access_tokens
            WHERE
                refresh_token = :refresh_token 
            AND
                is_revoked = FALSE;
        """
        refresh = await database.fetch_one(query, {
            "refresh_token": refresh_token
        })
        if refresh is None:
            raise TokenNotFound
        logger.debug(refresh)
        return await create(
            database=database,
            token=stokens.TokenCreate(
                access_token=new_access_token,
                refresh_token=refresh_token,
                valid_to=refresh["valid_to"],
                user_id=refresh["user_id"]
            )
        )
    except PostgresError as e:
        logger.debug(e)
        raise DatabaseError from e
