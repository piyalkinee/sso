import databases
import sqlalchemy

from sqlalchemy.ext.declarative import declarative_base

from ...configuration import conf
from ...exceptions.database import SessionNotInitializedError

metadata = sqlalchemy.MetaData()
Base = declarative_base(metadata=metadata)

_SESSION: databases.Database | None = None


async def get_connected_session() -> databases.Database:
    c = conf['postgres']
    connection_string = f"postgresql://{c['user']}:{c['password']}@{c['host']}:{c['port']}/{c['database']}"
    res = databases.Database(connection_string)
    await res.connect()
    return res


async def connect() -> databases.Database:
    global _SESSION
    if _SESSION is None:
        _SESSION = await get_connected_session()
    return _SESSION


def get_session() -> databases.Database:
    global _SESSION
    if not _SESSION:
        raise SessionNotInitializedError
    return _SESSION


async def disconnect() -> None:
    global _SESSION
    if _SESSION is not None and _SESSION.is_connected:
        await _SESSION.disconnect()
        _SESSION = None
        