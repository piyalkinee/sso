from functools import wraps
from fastapi import APIRouter

from .database import add_database_to_session
from .exceptions import exception_handler
from .jwt_user import add_user_to_session
from .permissions import check_permissions
from .session import session


def route(
        router: APIRouter,
        method: str,
        path: str,
        permissions: list[str],
        requires_auth: bool = True,
        **kwargs,
):
    router_type = router.get
    if method == 'put':
        router_type = router.put
    if method == 'delete':
        router_type = router.delete
    if method == 'post':
        router_type = router.post

    def inner(function):
        @wraps(function)
        async def f(*args, **kwargs):
            return await function(*args, **kwargs)

        if requires_auth:
            f = check_permissions(permissions)(f)
            f = add_user_to_session(f)
        f = add_database_to_session(f)
        f = exception_handler(f)
        f = router_type(path, **kwargs)(f)
        return f

    return inner
