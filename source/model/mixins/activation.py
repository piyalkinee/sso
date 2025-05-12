from sqlalchemy import Boolean, Column, DateTime, func, text
from sqlalchemy.orm import declared_attr


class ActivationMixin:
    @declared_attr
    def is_active(cls):
        return Column(
            Boolean, nullable=False, default=False, server_default=text("'false'")
        )

    @declared_attr
    def active_at(cls):
        return Column(
            DateTime, nullable=False, default=func.now(), server_default=func.now()
        )

    @declared_attr
    def inactive_at(cls):
        return Column(DateTime)
