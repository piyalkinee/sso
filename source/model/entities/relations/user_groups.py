from sqlalchemy import *

from source.core.database.postgres import Base
from source.model.mixins.time_stamp import TimestampMixin


class UserGroups(Base, TimestampMixin):
    __tablename__ = "user_groups"
    __table_args__ = {"schema": "relations"}

    user_id = Column(Integer, ForeignKey("users.users_core.id", ondelete="CASCADE"), primary_key=True)
    group_id = Column(Integer, ForeignKey("rights.groups.id", ondelete="CASCADE"), primary_key=True)
