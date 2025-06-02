import datetime
import secrets

import jose
import jose.jwt
from loguru import logger

from source.settings import settings


def generate_token(data: dict, type: str, ttl: float = 10) -> str:
    logger.debug("In core [generate_token]")
    expiration_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=ttl)
    token_payload = {
        **data,
        "type": type,
        "exp": int(expiration_time.timestamp()),
        "salt": secrets.token_urlsafe(32),
    }

    logger.debug(f"Token payload before serialization: {token_payload}")

    def make_serializable(obj):
        if isinstance(obj, dict):
            return {k: make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [make_serializable(v) for v in obj]
        elif isinstance(obj, datetime.datetime):
            return obj.isoformat()
            # return int(obj.timestamp())
        elif isinstance(obj, datetime.date):
            return obj.isoformat()
        else:
            return obj

    serializable_payload = make_serializable(token_payload)
    logger.debug(f"Serializable payload: {serializable_payload}")

    try:
        token = jose.jwt.encode(
            serializable_payload,
            settings.access_security.secret_key,
            algorithm=settings.access_security.algorithm,
        )
        return str(token)
    except Exception as e:
        logger.error(f"Error generating token: {e}")
        raise


def decode_token(token: str) -> dict[str, str]:
    logger.debug("In core [decode_token]")
    try:
        data = jose.jwt.decode(
            token,
            settings.access_security.secret_key,
            algorithms=settings.access_security.algorithm,
        )
        return dict(data)
    except jose.JWTError as e:
        raise "Invalid Token" from e


def generate_salt():
    return "salt"
