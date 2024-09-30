import fastapi

from .v1 import base as v1_base

router = fastapi.APIRouter()

router.include_router(v1_base.router, prefix="/v1/base", tags=["Base"])
