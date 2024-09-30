import fastapi
import starlette.status


class InvalidPassword(fastapi.HTTPException):
    """This password is incorrect"""

    def __init__(self, detail="Password is incorrect."):
        super().__init__(
            status_code=starlette.status.HTTP_401_UNAUTHORIZED,
            detail=detail,
        )
