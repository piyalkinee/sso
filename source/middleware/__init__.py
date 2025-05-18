from functools import wraps

from fastapi import APIRouter

from .dependencies import session
from .exceptions import exception_handler
from .jwt_user import add_user_to_session
from .permissions import check_permissions


def route(
    router: APIRouter,
    method: str,
    path: str,
    permissions: list[str],
    requires_auth: bool = True,
    **kwargs,
):
    router_type = getattr(router, method, "get")

    def inner(function):
        @wraps(function)
        async def f(*args, **kwargs):
            return await function(*args, **kwargs)

        if requires_auth:
            f = add_user_to_session(f)
            f = check_permissions(permissions)(f)
        f = exception_handler(f)
        f = router_type(path, **kwargs)(f)
        return f

    return inner
