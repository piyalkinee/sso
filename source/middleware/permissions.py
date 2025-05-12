from functools import wraps

from fastapi import HTTPException, status


def check_permissions(permissions_required: list[str]):
    def decorator(function):
        @wraps(function)
        async def wrapper(*args, **kwargs):
            session = kwargs.get("session", {})
            user = session.get("user")
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Пользователь не аутентифицирован",
                )

            user_permissions = getattr(user, "permissions", [])
            if not set(permissions_required).issubset(set(user_permissions)):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Недостаточно прав доступа",
                )

            return await function(*args, **kwargs)

        return wrapper

    return decorator
