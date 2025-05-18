from sqlalchemy import *

from source.core.database.postgres import Base


class UsersSecurity(Base):
    __tablename__ = "users_security"
    __table_args__ = {"schema": "users"}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.users_core.id", ondelete="CASCADE"), nullable=False)
    password_hash = Column(Text)
    password_salt = Column(Text)
    ban_message = Column(Text)
    is_banned = Column(Boolean, nullable=False, default=text("'false'"), server_default=text("'false'"))
    login_ip = Column(String(15))
    login_count = Column(Integer, nullable=False, default=text("0"), server_default=text("0"))
    login_at = Column(DateTime)
    banned_at = Column(DateTime)
