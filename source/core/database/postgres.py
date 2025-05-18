from typing import AsyncGenerator

import sqlalchemy
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.ext.declarative import declarative_base

from source.exceptions.database import SessionNotInitializedError
from source.settings import settings

metadata = sqlalchemy.MetaData()
Base = declarative_base(metadata=metadata)
s = settings.postgres
DATABASE_URL = f"postgresql+asyncpg://{s.user}:{s.password}@{s.host}:{s.port}/{s.database}"

engine = create_async_engine(DATABASE_URL, echo=False, future=True)
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    try:
        async with AsyncSessionLocal() as session:
            yield session
    except Exception as e:
        raise SessionNotInitializedError


async def check_db_connection():
    async with AsyncSessionLocal() as session:
        await session.execute(text("SELECT 1"))
