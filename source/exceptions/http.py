import fastapi
import starlette.status


# noinspection PyUnusedClass
class HTTPBadRequestError(fastapi.HTTPException):
    def __init__(self, detail="Request is invalid"):
        super().__init__(
            status_code=starlette.status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )


class HTTPUnauthenticatedError(fastapi.HTTPException):
    def __init__(self, detail="Invalid credentials"):
        super().__init__(
            status_code=starlette.status.HTTP_401_UNAUTHORIZED,
            detail=detail,
        )


# noinspection PyUnusedClass
class HTTPForbiddenError(fastapi.HTTPException):
    def __init__(self, detail="You have no permission for this"):
        super().__init__(
            status_code=starlette.status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


class HTTPNotFoundError(fastapi.HTTPException):
    def __init__(self, detail="Requested item was not found"):
        super().__init__(
            status_code=starlette.status.HTTP_404_NOT_FOUND,
            detail=detail,
        )


class HTTPConflictError(fastapi.HTTPException):
    def __init__(self, detail="Resource already exists"):
        super().__init__(
            status_code=starlette.status.HTTP_409_CONFLICT,
            detail=detail,
        )


# noinspection PyUnusedClass
class HTTPValidationError(fastapi.HTTPException):
    def __init__(self, detail="Unprocessable Entity"):
        super().__init__(
            status_code=starlette.status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
        )


class HTTPInternalError(fastapi.HTTPException):
    def __init__(self, detail="Internal Server Error"):
        super().__init__(
            status_code=starlette.status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        )


class HTTPUnavailableError(fastapi.HTTPException):
    def __init__(self, detail="Server is temporary unavailable"):
        super().__init__(
            status_code=starlette.status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
        )
