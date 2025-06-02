from source.core.database.postgres import Base
from source.model.mixins.rights import RightsBaseMixin


class Groups(Base, RightsBaseMixin):
    __tablename__ = "groups"
