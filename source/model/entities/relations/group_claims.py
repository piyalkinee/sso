from sqlalchemy import *
from ....core.database.postgres import Base

class GroupClaims(Base):
    __tablename__ = "group_claims"
    __table_args__ = {"schema": "relations"}

    group_id = Column(Integer, ForeignKey("rights.groups.id", ondelete="CASCADE"), primary_key=True)
    claim_id = Column(Integer, ForeignKey("rights.claims.id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(DateTime, nullable=False, default=func.now(), server_default=func.now())
