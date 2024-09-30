import jose
import jose.jwt
import datetime
import secrets

from loguru import logger

from ..configuration import conf


def generate_token(data: dict, type: str, ttl: float = 10) -> str:
    logger.debug("In core [generate_token]")
    return str(
        jose.jwt.encode(
            {
                **data,
                "type": type,
                "exp": datetime.datetime.now() + datetime.timedelta(minutes=ttl),
                "salt": secrets.token_urlsafe(32),
            },
            conf.access_security.secret_key,
            algorithm=conf.access_security.algorithm,
        )
    )


def decode_token(token: str) -> dict[str, str]:
    logger.debug("In core [decode_token]")
    try:
        data = jose.jwt.decode(
            token,
            conf.access_security.secret_key,
            algorithms=conf.access_security.algorithm,
        )
        return dict(data)
    except jose.JWTError as e:
        raise "Invalid Token" from e


def generate_salt():
    return "salt"
