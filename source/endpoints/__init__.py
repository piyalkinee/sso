import fastapi

from .v1 import base as v1_base
from .v1 import oauth2 as v1_oauth2

router = fastapi.APIRouter()

router.include_router(v1_base.router, prefix="/v1/base", tags=["Base"])
router.include_router(v1_oauth2.router, prefix="/v1/oauth2", tags=["OAuth2"])
