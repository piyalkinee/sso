from ..schemas.errors import *

ERRORS_SCHEMAS = {
    "400": {"model": HTTP400},
    "401": {"model": HTTP401},
    "403": {"model": HTTP403},
    "404": {"model": HTTP404},
    "409": {"model": HTTP409},
    "422": {"model": HTTP422},
    "503": {"model": HTTP503},
}
