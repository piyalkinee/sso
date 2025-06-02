from fastapi import Depends

from source.core.database.postgres import get_session

from .session import _session

session = Depends(_session)
database = Depends(get_session)
