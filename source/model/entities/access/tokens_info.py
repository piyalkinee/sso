from sqlalchemy import *

from source.core.database.postgres import Base
from source.model.mixins.time_stamp import TimestampMixin


class TokensInfo(Base, TimestampMixin):
    __tablename__ = "tokens_info"
    __table_args__ = {"schema": "access"}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.users_core.id", ondelete="CASCADE"), nullable=False)
    is_revoked = Column(Boolean, nullable=False, default=False, server_default="false")
    valid_to = Column(
        DateTime,
        nullable=False,
        default=lambda: func.now() + text("INTERVAL '1 day'"),
        server_default=text("NOW() + INTERVAL '1 day'"),
    )
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=False)
