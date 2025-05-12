from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    headers = getattr(exc, "headers", None)
    if type(exc.detail) is dict:
        content = {
            "error": True,
            "class": exc.detail.get("name"),
            "doc": exc.detail.get("doc"),
            "code": exc.detail.get("x_code"),
            "message": exc.detail.get("message"),
        }
    else:
        content = {
            "error": True,
            "class": exc.__class__.__name__,
            "doc": exc.__doc__,
            "message": str(exc.detail),
        }
    if headers:
        return JSONResponse(content, status_code=exc.status_code, headers=headers)
    else:
        return JSONResponse(content, status_code=exc.status_code)


async def request_validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": True,
            "class": exc.__class__.__name__,
            "message": str(exc),
            "detail": jsonable_encoder(exc.errors()),
        },
    )


exception_handlers = {}
exception_handlers.setdefault(HTTPException, http_exception_handler)
exception_handlers.setdefault(
    RequestValidationError, request_validation_exception_handler
)
