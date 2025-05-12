from sqlalchemy import *

from source.core.database.postgres import Base


class UsersPersonalInfo(Base):
    __tablename__ = "users_personal_info"
    __table_args__ = {"schema": "users"}

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer, ForeignKey("users.users_core.id", ondelete="CASCADE"), nullable=False
    )
    name = Column(Text, nullable=False)
    phone_number = Column(Text, unique=True, nullable=True)
    telegram_username = Column(Text, nullable=True)
    email = Column(Text, unique=True, nullable=False)
    language = Column(
        String(4), nullable=False, default=text("'en'"), server_default=text("'en'")
    )
