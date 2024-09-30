from sqlalchemy import *
from ....core.database.postgres import Base

class Claims(Base):
    __tablename__ = "claims"
    __table_args__ = {"schema": "rights"}

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    is_active = Column(Boolean, nullable=False, default=False, server_default=text("'false'"))
    created_at = Column(DateTime, nullable=False, default=func.now(), server_default=func.now())
    active_at = Column(DateTime, nullable=False, default=func.now(), server_default=func.now())
    updated_at = Column(DateTime)
    inactive_at = Column(DateTime)
