# session.py

from functools import wraps
from fastapi import Request, HTTPException, status

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
            request = kwargs.get('request')
            
        # Fallback: check if session object has request
        if not request:
            session = kwargs.get('session')
            if hasattr(session, 'request'):
                request = session.request

        if not request:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Объект Request не найден"
            )
        token = request.headers.get("Authorization")
        if not token or not token.startswith("Bearer "):
            kwargs['session'] = {}
            return await function(*args, **kwargs)
        try:
            token = token[len("Bearer "):]
            token_data = decode_token(token)
            user = susers.User(**token_data)
            session = kwargs.get('session', {})
            
            # Now that Session has user, we can set it confidently
            if isinstance(session, dict):
                session['user'] = user
            else:
                session.user = user
                
            kwargs['session'] = session
            return await function(*args, **kwargs)
        except Exception as e:
            # Helper to log errors safely
            from loguru import logger
            logger.warning(f"Failed to authenticate user from token: {e}")
            # If token is invalid, we don't set user
            return await function(*args, **kwargs)
    return wrapper