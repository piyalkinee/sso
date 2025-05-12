from functools import wraps

from ..core.database import postgres


def add_database_to_session(function):
    @wraps(function)
    async def inner_wrapper(*args, **kwargs):
        async with postgres.get_session().connection() as connection:
            kwargs["session"].db = connection
            return await function(*args, **kwargs)

    return inner_wrapper
