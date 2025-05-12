import fastapi
import starlette.status


class ExecutorNotInitializedError(fastapi.HTTPException):
    """Raised on attempt to utilize unavailable executor."""


class InvalidToken(fastapi.HTTPException):
    """Invalid token provided"""

    def __init__(
        self, detail="Please ensure the access token is correct and try again."
    ):
        super().__init__(
            status_code=starlette.status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )


class InvalidCredentialsError(fastapi.HTTPException):
    """Invalid credentials provided."""

    def __init__(
        self,
        detail="Please ensure the token is correct or token is not revoked and try again later.",
    ):
        super().__init__(
            status_code=starlette.status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )


class AuthServerUnavailable(fastapi.HTTPException):
    """Raise an attempt to unavailable server response."""

    def __init__(
        self, detail="Sorry but service is unavailable at the moment. Try again later."
    ):
        super().__init__(
            status_code=starlette.status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
        )


class TokenNotFound(fastapi.HTTPException):
    """Raised on attempt to revoke nonexistent or refresh revoked token."""

    def __init__(self, detail="Please ensure the data is correct or try again later."):
        super().__init__(
            status_code=starlette.status.HTTP_404_NOT_FOUND,
            detail=detail,
        )


class TokenAlreadyStored(fastapi.HTTPException):
    """Raised on attempt to store an already present token."""

    def __init__(self, detail="Please ensure the data is correct or try again later."):
        super().__init__(
            status_code=starlette.status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )
