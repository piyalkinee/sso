from sqlalchemy import *
from ....core.database.postgres import Base

class UserGroups(Base):
    __tablename__ = "user_groups"
    __table_args__ = {"schema": "relations"}

    user_id = Column(Integer, ForeignKey("users.users_core.id", ondelete="CASCADE"), primary_key=True)
    group_id = Column(Integer, ForeignKey("rights.groups.id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(DateTime, nullable=False, default=func.now(), server_default=func.now())
