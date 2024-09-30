from pydantic import BaseModel


class HTTP400(BaseModel):
    status_code: int = 400
    error_message: str = "HTTPBadRequestError"


class HTTP401(BaseModel):
    status_code: int = 401
    error_message: str = "HTTPUnauthenticatedError"


class HTTP403(BaseModel):
    status_code: int = 403
    error_message: str = "HTTPForbiddenError"


class HTTP404(BaseModel):
    status_code: int = 404
    error_message: str = "HTTPNotFoundError"


class HTTP409(BaseModel):
    status_code: int = 409
    error_message: str = "HTTPConflictError"


class HTTP422(BaseModel):
    status_code: int = 422
    error_message: str = "HTTPValidationError"


class HTTP503(BaseModel):
    status_code: int = 503
    error_message: str = "HTTPUnavailableError"
