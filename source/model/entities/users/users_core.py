from sqlalchemy import *
from ....core.database.postgres import Base

class UsersCore(Base):
    __tablename__ = "users_core"
    __table_args__ = {"schema": "users"}

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=False, default=func.now(), server_default=func.now())
    updated_at = Column(DateTime)
