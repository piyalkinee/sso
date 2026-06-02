import jose
import jose.jwt
import datetime
import secrets

from loguru import logger

from ..configuration import conf
from ..exceptions import auth


def generate_token(data: dict, type: str, ttl: float = 10) -> str:
    logger.debug("In core [generate_token]")
    issued_at = datetime.datetime.utcnow()
    expiration_time = issued_at + datetime.timedelta(minutes=ttl)
    sub = str(data.get("sub") or data.get("id") or "")
    roles = data.get("roles")
    if roles is None:
        roles = [
            g["name"] if isinstance(g, dict) else g.name
            for g in data.get("groups", [])
            if (isinstance(g, dict) and g.get("name")) or (hasattr(g, "name") and g.name)
        ]
    token_payload = {
        **data,
        "sub": sub,
        "roles": roles,
        "type": type,
        "exp": int(expiration_time.timestamp()),
        "iat": int(issued_at.timestamp()),
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
            conf['access_security']['secret_key'],
            algorithm=conf['access_security']['algorithm'],
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
            conf['access_security']['secret_key'],
            algorithms=[conf['access_security']['algorithm']],
        )
        return dict(data)
    except jose.JWTError as e:
        raise auth.InvalidCredentialsError from e


def generate_salt():
    return "salt"
