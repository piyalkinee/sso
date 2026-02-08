from sqlalchemy import *
from ....core.database.postgres import Base

class UsersProviders(Base):
    __tablename__ = "users_oauth2_providers"
    __table_args__ = {"schema": "users"}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.users_core.id", ondelete="CASCADE"), nullable=False)
    provider = Column(String(20), nullable=False) # "google", "apple"
    provider_user_id = Column(Text, nullable=False) # email or sub
    created_at = Column(DateTime, nullable=False, default=func.now(), server_default=func.now())

    __table_args__ = (
        UniqueConstraint('provider', 'provider_user_id', name='uq_provider_user'),
        {"schema": "users"}
    )
