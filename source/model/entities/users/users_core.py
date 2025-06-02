from sqlalchemy import *

from source.core.database.postgres import Base
from source.model.mixins.time_stamp import TimestampMixin


class UsersCore(Base, TimestampMixin):
    __tablename__ = "users_core"
    __table_args__ = {"schema": "users"}

    id = Column(Integer, primary_key=True)
