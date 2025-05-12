# session.py

from functools import wraps

from fastapi import HTTPException, Request, status

from ..core.access_tokens import decode_token
from ..schemas import users as susers


def add_user_to_session(function):
    @wraps(function)
    async def wrapper(*args, **kwargs):
        request = None
        for arg in args:
            if isinstance(arg, Request):
                request = arg
                break
        if not request:
            request = kwargs.get("request")
        if not request:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Объект Request не найден",
            )
        token = request.headers.get("Authorization")
        if not token or not token.startswith("Bearer "):
            kwargs["session"] = {}
            return await function(*args, **kwargs)
        try:
            token = token[len("Bearer ") :]
            token_data = decode_token(token)
            user = susers.User(**token_data)
            session = kwargs.get("session", {})
            session["user"] = user
            kwargs["session"] = session
            return await function(*args, **kwargs)
        except Exception as e:
            kwargs["session"] = {}
            return await function(*args, **kwargs)

    return wrapper
