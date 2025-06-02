from sqlalchemy import Column, DateTime, func
from sqlalchemy.orm import declared_attr


class TimestampMixin:
    @declared_attr
    def created_at(cls):
        return Column(DateTime, nullable=False, default=func.now(), server_default=func.now())

    @declared_attr
    def updated_at(cls):
        return Column(DateTime)
