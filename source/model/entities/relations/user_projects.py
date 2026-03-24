from sqlalchemy import *
from sqlalchemy.dialects.postgresql import UUID
from ....core.database.postgres import Base


class UserProjects(Base):
    __tablename__ = "user_projects"
    __table_args__ = {"schema": "relations"}

    user_id = Column(Integer, ForeignKey("users.users_core.id", ondelete="CASCADE"), primary_key=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.projects.id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(DateTime, nullable=False, default=func.now(), server_default=func.now())
