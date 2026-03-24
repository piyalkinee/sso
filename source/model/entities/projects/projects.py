from sqlalchemy import *
from sqlalchemy.dialects.postgresql import UUID
from ....core.database.postgres import Base


class Projects(Base):
    __tablename__ = "projects"
    __table_args__ = {"schema": "projects"}

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()'))
    name = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now(), server_default=func.now())
