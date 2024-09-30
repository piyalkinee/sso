from sqlalchemy import *
from ....core.database.postgres import Base

class TokensInfo(Base):
    __tablename__ = "tokens_info"
    __table_args__ = {"schema": "access"}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.users_core.id", ondelete="CASCADE"), nullable=False)
    is_revoked = Column(Boolean, nullable=False, default=False, server_default="false")
    valid_to = Column(
        DateTime,
        nullable=False,
        default=lambda: func.now() + text("INTERVAL '1 day'"),
        server_default=text("NOW() + INTERVAL '1 day'")
    )
    access_token = Column(String(256), nullable=False)
    refresh_token = Column(String(256), nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now(), server_default=func.now())
