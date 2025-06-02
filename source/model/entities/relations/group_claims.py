from sqlalchemy import *

from source.core.database.postgres import Base
from source.model.mixins.time_stamp import TimestampMixin


class GroupClaims(Base, TimestampMixin):
    __tablename__ = "group_claims"
    __table_args__ = {"schema": "relations"}

    group_id = Column(Integer, ForeignKey("rights.groups.id", ondelete="CASCADE"), primary_key=True)
    claim_id = Column(Integer, ForeignKey("rights.claims.id", ondelete="CASCADE"), primary_key=True)
