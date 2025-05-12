from sqlalchemy import Column, Integer, Text
from sqlalchemy.orm import declarative_mixin, declared_attr

from .activation import ActivationMixin
from .time_stamp import TimestampMixin


@declarative_mixin
class RightsBaseMixin(TimestampMixin, ActivationMixin):
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=False)

    @declared_attr
    def __table_args__(cls):
        return {"schema": "rights"}
